import ast
import asyncio
import difflib
import json
import re
import logging
from pathlib import Path
from typing import Optional

from config import (
    MAX_FILE_ATTEMPTS, MAX_TEST_ATTEMPTS, MAX_CONTEXT_CHARS, MIN_COVERAGE,
    FACTORY_DIR, LOGS_DIR, SRC_DIR, RUN_TIMEOUT, MAX_SPEC_REVISIONS,
    MAX_A5_PATCHES_PER_FILE, SELF_REFLECT_RETRIES, TRUNCATE_FEEDBACK,
    TRUNCATE_CODE, TRUNCATE_LOG, TRUNCATE_ERROR_MSG,
)

MAX_CUMULATIVE = MAX_FILE_ATTEMPTS * 3  # После 15 суммарных попыток — принудительный APPROVE
from exceptions import LLMError
from llm import ask_agent
from stats import ModelStats
from json_utils import to_str, safe_contract
from lang_utils import LANG_DISPLAY, LANG_EXT, get_execution_command, get_test_command, get_docker_image
from log_utils import get_model, log_runtime_error
from code_context import get_global_context, get_full_context, build_dependency_order, find_failing_file, validate_imports, validate_cross_file_names
from state import push_feedback, get_feedback_ctx, update_dependencies, update_dockerfile, update_requirements
from artifacts import update_artifact_a9, save_artifact
from infra import run_in_docker, build_docker_image
from contract import refresh_api_contract, phase_review_api_contract, patch_contract_for_file
from cache import ThreadSafeCache

# Детекция замаскированных ошибок (rc=0 но traceback в stdout)
_EXCEPTION_LINE_RE = re.compile(
    r"^\s*(?:(?:\w+\.)*\w+)?(?:Error|Exception):(?:\s+|\s*$)", re.MULTILINE
)


def _sanitize_llm_code(code: str) -> str:
    """Очищает код от артефактов LLM: markdown fences, garbage tokens."""
    # 1. Убираем markdown code fences (```python ... ```)
    code = re.sub(r"^```[\w]*\s*\n?", "", code, flags=re.MULTILINE)
    code = re.sub(r"^```\s*$", "", code, flags=re.MULTILINE)
    # 2. Убираем garbage tokens deepseek-coder (begin_of_sentence и т.п.)
    # Сначала дедупликация: img<token>img_bytes → img_bytes (модель перезапускает генерацию)
    _GARBAGE_TOKEN = r"<[｜|][\w▁]+[｜|]>"
    code = re.sub(r"(\w+)" + _GARBAGE_TOKEN + r"\1", r"\1", code)
    # Затем убираем оставшиеся токены (gcv<token>_image → gcv_image)
    code = re.sub(_GARBAGE_TOKEN, "", code)
    # 3. Убираем JSON-wrapper поля, которые LLM встраивает в код
    # (imports_from_project = [...], external_dependencies = [...])
    code = re.sub(
        r"\n\s*(?:imports_from_project|external_dependencies|called_by)\s*=\s*\[.*?\]\s*$",
        "", code, flags=re.MULTILINE,
    )
    return code.strip()


def _ensure_a5_imports(code: str, global_imports: list[str]) -> str:
    """Гарантирует что все A5 global_imports присутствуют в коде.

    Developer часто забывает импорты (import numpy as np, from typing import List и т.д.)
    хотя A5 контракт их требует. Вместо REJECT → авто-добавляем.
    """
    if not global_imports or not code.strip():
        return code
    # Парсим существующие import-строки из кода
    existing_imports: set[str] = set()
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            # Нормализуем пробелы для сравнения
            existing_imports.add(re.sub(r"\s+", " ", stripped))

    missing: list[str] = []
    for imp_line in global_imports:
        if not isinstance(imp_line, str):
            continue
        normalized = re.sub(r"\s+", " ", imp_line.strip())
        if not normalized:
            continue
        # Проверяем точное совпадение или что базовый модуль уже импортирован
        if normalized in existing_imports:
            continue
        # "from typing import List" vs "from typing import List, Dict" → проверяем базу
        m = re.match(r"from\s+(\S+)\s+import\s+(.+)", normalized)
        if m:
            source = m.group(1)
            names = {n.strip().split()[0] for n in m.group(2).split(",") if n.strip()}
            # Ищем существующий import из того же source
            found_source = False
            for ex in existing_imports:
                ex_m = re.match(r"from\s+(\S+)\s+import\s+(.+)", ex)
                if ex_m and ex_m.group(1) == source:
                    found_source = True
                    ex_names = {n.strip().split()[0] for n in ex_m.group(2).split(",") if n.strip()}
                    # Есть ли недостающие имена?
                    missing_names = names - ex_names
                    if missing_names:
                        # Объединяем в один import
                        all_names = sorted(ex_names | names)
                        new_line = f"from {source} import {', '.join(all_names)}"
                        # Заменяем в коде (ищем оригинальную строку с любым whitespace)
                        code = re.sub(
                            rf"^\s*from\s+{re.escape(source)}\s+import\s+.+$",
                            new_line, code, count=1, flags=re.MULTILINE,
                        )
                        existing_imports.discard(ex)
                        existing_imports.add(re.sub(r"\s+", " ", new_line))
                    break
            if not found_source:
                missing.append(normalized)
        else:
            # "import X as Y" — проверяем по alias
            m2 = re.match(r"import\s+(\S+)(?:\s+as\s+(\w+))?", normalized)
            if m2:
                module = m2.group(1)
                alias = m2.group(2) or module.split(".")[0]
                # Если alias уже используется как import
                already = any(
                    re.match(rf"import\s+{re.escape(module)}\b", ex)
                    for ex in existing_imports
                )
                if not already:
                    missing.append(normalized)
            else:
                missing.append(normalized)

    if missing:
        # Добавляем пропущенные imports в начало файла (после docstring/comments если есть)
        lines = code.split("\n")
        insert_pos = 0
        # Пропускаем начальные комментарии, docstrings, shebang
        in_docstring = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Обработка многострочных docstrings
            if in_docstring:
                insert_pos = i + 1
                if '"""' in stripped or "'''" in stripped:
                    in_docstring = False
                continue
            if (stripped.startswith('"""') or stripped.startswith("'''")):
                insert_pos = i + 1
                # Однострочный docstring (открытие и закрытие на одной строке)
                quote = '"""' if stripped.startswith('"""') else "'''"
                if stripped.count(quote) < 2:
                    in_docstring = True
                continue
            if stripped.startswith("#") or not stripped:
                insert_pos = i + 1
            elif stripped.startswith("import ") or stripped.startswith("from "):
                insert_pos = i  # Вставляем перед первым import
                break
            else:
                break
        for imp in reversed(missing):
            lines.insert(insert_pos, imp)
        code = "\n".join(lines)

    return code


def _check_class_duplication(code: str, global_context: str, file_contract: list | None = None) -> list[str]:
    """Детерминистская проверка: не определяет ли код классы, которые уже есть в других файлах.
    file_contract — A5 контракт текущего файла; классы, ожидаемые по контракту, не считаются дублями.
    Возвращает список предупреждений (пустой если дублирования нет)."""
    if not global_context:
        return []
    # Классы, определённые в новом коде (только публичные)
    classes_in_code = {n for n in re.findall(r'^class\s+(\w+)', code, re.MULTILINE)
                       if not n.startswith('_')}
    if not classes_in_code:
        return []
    # Классы, ожидаемые по A5 контракту для этого файла — их определять МОЖНО
    expected_classes: set[str] = set()
    if file_contract:
        for item in file_contract:
            if isinstance(item, dict):
                name = item.get("class") or item.get("name") or item.get("function", "")
                if name:
                    expected_classes.add(name)
    # Маппинг класс → файл-источник из global_context
    name_to_file: dict[str, str] = {}
    current_file = None
    for line in global_context.splitlines():
        m = re.match(r'^--- (\S+) PUBLIC API ---$', line)
        if m:
            current_file = m.group(1)
            continue
        if current_file:
            for name in re.findall(r'class\s+(\w+)', line):
                if not name.startswith('_'):
                    name_to_file[name] = current_file
    duplicates = classes_in_code & set(name_to_file.keys()) - expected_classes
    if not duplicates:
        return []
    return [
        f"{name} уже определён в {name_to_file[name]} — "
        f"используй импорт из {name_to_file[name]} вместо переопределения"
        for name in sorted(duplicates)
    ]


def _check_import_shadowing(code: str) -> list[str]:
    """Детерминистская проверка: не определяет ли файл top-level функцию/класс
    с тем же именем, что импортируется через from X import Y.
    Пример ошибки: from video_processing import process_frame + def process_frame(...)
    Возвращает список предупреждений."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    # Собираем имена, импортированные через from X import Y
    imported_names: dict[str, str] = {}  # name → "from X import name"
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in (node.names or []):
                real_name = alias.asname or alias.name
                if real_name != "*":
                    imported_names[real_name] = f"from {node.module} import {alias.name}"
    if not imported_names:
        return []
    # Собираем top-level определения (def / class) — только прямые потомки модуля
    defined_names: set[str] = set()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined_names.add(node.name)
    # Пересечение = shadowing
    shadowed = defined_names & set(imported_names.keys())
    if not shadowed:
        return []
    return [
        f"'{name}' импортирован ({imported_names[name]}) И определён "
        f"в этом файле — убери локальное определение или импорт"
        for name in sorted(shadowed)
    ]


def _check_data_only_violations(
    code: str,
    current_file: str,
    project_files: list[str],
) -> list[str]:
    """Детерминистская проверка: если файл — data-only (models.py / data_models.py),
    запрещает:
    1. Импорты из других файлов проекта (создают циклические зависимости)
    2. Top-level функции с бизнес-логикой (только dunder-методы внутри классов)

    Возвращает список предупреждений (пустой если всё ОК или файл не data-only).
    """
    stem = Path(current_file).stem
    if stem not in ("models", "data_models"):
        return []

    warnings: list[str] = []
    project_stems = {Path(f).stem for f in project_files if Path(f).stem != stem}

    # 1. Проверяем project-file imports
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            base = node.module.split(".")[0]
            if base in project_stems:
                names = ", ".join(a.name for a in (node.names or []))
                warnings.append(
                    f"ЗАПРЕЩЕНО: 'from {node.module} import {names}' — "
                    f"{current_file} это data-only файл, он НЕ ДОЛЖЕН импортировать "
                    f"из других файлов проекта. Определи все классы ЗДЕСЬ, "
                    f"а другие файлы будут импортировать ИЗ {current_file}"
                )
        elif isinstance(node, ast.Import):
            for alias in (node.names or []):
                base = alias.name.split(".")[0]
                if base in project_stems:
                    warnings.append(
                        f"ЗАПРЕЩЕНО: 'import {alias.name}' — "
                        f"{current_file} это data-only файл, он НЕ ДОЛЖЕН импортировать "
                        f"из других файлов проекта"
                    )

    # 2. Проверяем top-level функции (не внутри классов)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                warnings.append(
                    f"ЗАПРЕЩЕНО: top-level функция '{node.name}()' в {current_file} — "
                    f"этот файл содержит ТОЛЬКО data classes (dataclass/class определения). "
                    f"Бизнес-логику вынеси в соответствующий модуль"
                )

    return warnings


def _check_stub_functions(code: str) -> list[str]:
    """Детерминистская проверка: содержит ли код функции-заглушки.

    Ловит: pass / ... / raise NotImplementedError как единственное тело функции,
    а также pass внутри единственного try-блока.
    Возвращает список предупреждений (пустой если заглушек нет).
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    warnings: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        fname = node.name
        body = node.body
        # Пропускаем docstring если есть (только строковые литералы, не Ellipsis)
        effective = body
        if (effective and isinstance(effective[0], ast.Expr)
                and isinstance(effective[0].value, ast.Constant)
                and isinstance(getattr(effective[0].value, "value", None), str)):
            effective = effective[1:]
        if not effective:
            warnings.append(f"функция '{fname}' пустая (только docstring)")
            continue
        # Проверяем паттерны заглушек
        if _is_stub_body(effective):
            warnings.append(
                f"функция '{fname}' — заглушка (pass / ... / NotImplementedError). "
                f"Напиши полную реализацию с бизнес-логикой"
            )
            continue
        # Проверяем фиктивную реализацию (hardcoded return без использования параметров)
        if _is_hardcoded_return_stub(node):
            warnings.append(
                f"функция '{fname}' — фиктивная реализация (возвращает захардкоженный литерал, "
                f"не используя параметры). Напиши реальную логику, использующую входные данные"
            )
    return warnings


def _is_trivial_stmt(node: ast.AST) -> bool:
    """Проверяет, является ли statement тривиальным (pass, docstring, print)."""
    if isinstance(node, ast.Pass):
        return True
    if isinstance(node, ast.Expr):
        # Строковые литералы (docstrings)
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return True
        # print(...) вызовы
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            if node.value.func.id == "print":
                return True
    return False


def _is_stub_body(stmts: list) -> bool:
    """Проверяет что список statements — это заглушка."""
    if len(stmts) == 1:
        s = stmts[0]
        # pass
        if isinstance(s, ast.Pass):
            return True
        # ... (Ellipsis)
        if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and s.value.value is ...:
            return True
        # raise NotImplementedError(...)
        if isinstance(s, ast.Raise) and s.exc:
            if isinstance(s.exc, ast.Call) and isinstance(s.exc.func, ast.Name):
                if s.exc.func.id == "NotImplementedError":
                    return True
            if isinstance(s.exc, ast.Name) and s.exc.id == "NotImplementedError":
                return True
        # try: pass/print except: pass/print (заглушка обёрнутая в try)
        if isinstance(s, ast.Try):
            try_effective = [st for st in s.body if not _is_trivial_stmt(st)]
            if not try_effective:
                return True
    return False


def _is_hardcoded_return_stub(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Проверяет: функция с параметрами возвращает захардкоженный литерал,
    не используя ни один параметр в теле. Это фиктивная реализация.

    Пример: def recognize_plate(image: bytes) -> str: return 'ABC123'
    НЕ флагует: def get_version() -> str: return "1.0" (нет параметров)
    НЕ флагует: def process(x): return x.upper() (параметр используется)
    """
    # Собираем имена параметров (кроме self/cls)
    param_names: set[str] = set()
    for arg in func_node.args.args + func_node.args.posonlyargs + func_node.args.kwonlyargs:
        if arg.arg not in ("self", "cls"):
            param_names.add(arg.arg)
    if func_node.args.vararg:
        param_names.add(func_node.args.vararg.arg)
    if func_node.args.kwarg:
        param_names.add(func_node.args.kwarg.arg)

    # Нет параметров (кроме self/cls) → getter/константа → не флагуем
    if not param_names:
        return False

    # Пропускаем docstring
    body = func_node.body
    if (body and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)):
        body = body[1:]

    if not body:
        return False

    def _is_empty_literal(val: ast.AST) -> bool:
        """Проверяет что AST-узел — пустой/захардкоженный литерал."""
        if isinstance(val, ast.Constant):
            return True
        if isinstance(val, (ast.List, ast.Dict, ast.Tuple)):
            elts = getattr(val, "elts", None) or []
            keys = getattr(val, "keys", None) or []
            if not elts and not keys:
                return True  # [], {}, ()
            if isinstance(val, (ast.List, ast.Tuple)) and all(isinstance(e, ast.Constant) for e in elts):
                return True  # ['ABC123'], [0, 0, 0]
        return False

    # Паттерн 1: ровно один statement — return <literal>
    if len(body) == 1:
        stmt = body[0]
        if isinstance(stmt, ast.Return) and stmt.value is not None and _is_empty_literal(stmt.value):
            for node in ast.walk(func_node):
                if isinstance(node, ast.Name) and node.id in param_names:
                    return False
            return True

    # Паттерн 2: var = <empty_literal>; return var (без использования параметров)
    # Ловит: vehicles = []; return vehicles
    if 1 < len(body) <= 3:
        last = body[-1]
        if isinstance(last, ast.Return) and isinstance(last.value, ast.Name):
            ret_var = last.value.id
            # Проверяем что переменная инициализирована пустым литералом
            for stmt in body[:-1]:
                if (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                        and isinstance(stmt.targets[0], ast.Name)
                        and stmt.targets[0].id == ret_var
                        and _is_empty_literal(stmt.value)):
                    # Переменная = пустой литерал, return переменная
                    for node in ast.walk(func_node):
                        if isinstance(node, ast.Name) and node.id in param_names:
                            return False
                    return True

    return False


def _check_function_preservation(
    new_code: str, old_code: str, feedback: str,
    file_contract: list | None = None,
) -> list[str]:
    """Детерминистская проверка: не потерял ли новый код функции/классы из предыдущей версии.

    Сравнивает top-level function/class names между old и new.
    Если имя исчезло и НЕ упомянуто в feedback → авто-REJECT.
    Приватные имена (_prefix) игнорируются.
    Функции, которых нет в текущем A5 контракте, тоже игнорируются
    (A5 мог измениться после revise_spec).
    Возвращает список предупреждений (пустой если всё ОК).
    """
    if not old_code:
        return []

    def _extract_top_names(code: str) -> set[str]:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            names = set(re.findall(r'^class\s+(\w+)', code, re.MULTILINE))
            names.update(re.findall(r'^(?:async\s+)?def\s+(\w+)', code, re.MULTILINE))
            return names
        names: set[str] = set()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names.add(node.name)
            elif isinstance(node, ast.ClassDef):
                names.add(node.name)
        return names

    old_names = _extract_top_names(old_code)
    new_names = _extract_top_names(new_code)
    disappeared = old_names - new_names
    if not disappeared:
        return []

    # Имена, ожидаемые текущим A5 контрактом (может быть под ключами name/class/function)
    contract_names: set[str] = set()
    if file_contract:
        for item in file_contract:
            if isinstance(item, dict):
                for key in ("name", "class", "function"):
                    n = item.get(key, "")
                    if n:
                        contract_names.add(n)

    # Фильтруем: имена упомянутые в feedback + приватные + не в текущем A5
    feedback_lower = feedback.lower() if feedback else ""
    warnings: list[str] = []
    for name in sorted(disappeared):
        if name.startswith("_"):
            continue
        if feedback_lower and re.search(rf'\b{re.escape(name.lower())}\b', feedback_lower):
            continue
        # Если функции нет в текущем A5 — значит A5 изменился, удаление допустимо
        if contract_names and name not in contract_names:
            continue
        warnings.append(
            f"функция/класс '{name}' из предыдущей версии УДАЛЕНА, "
            f"но НЕ упоминается в фидбэке. Верни её обратно."
        )
    return warnings


def _check_contract_compliance(code: str, file_contract: list) -> list[str]:
    """Детерминистская проверка: содержит ли код ВСЕ required функции/классы из A5 контракта.
    Возвращает список отсутствующих элементов с сигнатурой для подсказки модели.
    При fuzzy-match показывает: "Ты определил X, но ожидается Y — ПЕРЕИМЕНУЙ"."""
    if not file_contract:
        return []
    # Извлекаем все определённые в коде имена функций и классов
    code_func_names: list[str] = re.findall(r'^\s*(?:async\s+)?def\s+(\w+)\s*\(', code, re.MULTILINE)
    code_class_names: list[str] = re.findall(r'^\s*class\s+(\w+)\b', code, re.MULTILINE)
    all_code_names = code_func_names + code_class_names

    missing = []
    for item in file_contract:
        if not item.get("required", False):
            continue
        sig = item.get("signature", "")
        name = item.get("name", "")
        if sig.startswith("class "):
            class_name = sig.split("class ", 1)[1].split("(")[0].split(":")[0].strip()
            if not re.search(rf'^class\s+{re.escape(class_name)}\b', code, re.MULTILINE):
                hint = _fuzzy_name_hint(class_name, all_code_names)
                missing.append(f"ОТСУТСТВУЕТ: {sig} — добавь определение класса {class_name}{hint}")
        elif sig.startswith("def ") or sig.startswith("async def "):
            func_name = name or sig.split("def ", 1)[1].split("(")[0].strip()
            # Ищем как top-level функцию (^def) так и метод класса (с отступом)
            if not re.search(rf'^\s*(?:async\s+)?def\s+{re.escape(func_name)}\s*\(', code, re.MULTILINE):
                hint = _fuzzy_name_hint(func_name, all_code_names)
                missing.append(f"ОТСУТСТВУЕТ: {sig} — добавь эту функцию ИМЕННО с таким именем{hint}")
    return missing


def _fuzzy_name_hint(expected: str, code_names: list[str]) -> str:
    """Если в коде есть похожее имя — вернуть подсказку для переименования."""
    if not code_names:
        return ""
    matches = difflib.get_close_matches(expected, code_names, n=1, cutoff=0.5)
    if matches and matches[0] != expected:
        return (
            f"\n    ⚠️ ПОХОЖЕЕ ИМЯ В КОДЕ: '{matches[0]}' — но ожидается '{expected}'. "
            f"ПЕРЕИМЕНУЙ '{matches[0]}' → '{expected}'"
        )
    return ""


async def _review_file(
    logger: logging.Logger,
    cache: ThreadSafeCache,
    current_file: str,
    code: str,
    attempt: int,
    stats: ModelStats,
    randomize: bool = False,
    language: str = "python",
    file_contract: list | None = None,
    global_imports: list | None = None,
) -> tuple[str, str, bool]:
    """Возвращает (status, feedback, needs_spec_revision)."""
    rev_model = get_model("reviewer", attempt, randomize=randomize)
    logger.info(f"👀 [{rev_model}] Reviewer проверяет {current_file} ...")
    try:
        rev_ctx = ""
        if file_contract:
            rev_ctx += f"API КОНТРАКТ (A5) для {current_file}:\n{json.dumps(file_contract, ensure_ascii=False, indent=2)}\n\n"
        if global_imports:
            rev_ctx += f"ОЖИДАЕМЫЕ ИМПОРТЫ (A5):\n{json.dumps(global_imports, ensure_ascii=False, indent=2)}\n\n"
        rev_ctx += f"Файл: {current_file}\nКод:\n{code}"
        result   = await ask_agent(logger, "reviewer", rev_ctx,
                                   cache, attempt, randomize, language)
        status   = result.get("status", "REJECT")
        feedback = to_str(result.get("feedback", ""))
        needs_spec = bool(result.get("needs_spec_revision", False))
        stats.record("reviewer", rev_model, status == "APPROVE")
        if needs_spec:
            logger.warning(f"  📋 Reviewer: проблема уровня спецификации для {current_file}")
        return status, feedback, needs_spec
    except (LLMError, ValueError) as e:
        logger.exception(f"Reviewer упал: {e}")
        stats.record("reviewer", rev_model, False)
        return "REJECT", f"Reviewer упал: {e}", False


async def do_self_reflect(
    logger: logging.Logger,
    cache: ThreadSafeCache,
    src_path: Path,
    current_file: str,
    code: str,
    state: dict,
    stats: ModelStats,
    randomize: bool = False,
) -> tuple[str, str]:
    """Self-Reflect проверяет соответствие A2 и A5."""
    language  = state.get("language", "python")
    sr_model  = get_model("self_reflect", 0, randomize=randomize)
    logger.info(f"🤔 [{sr_model}] Self-Reflect проверяет {current_file} ...")

    # Контракт для текущего файла из A5
    file_contract  = safe_contract(state).get("file_contracts", {}).get(current_file, [])
    global_imports = safe_contract(state).get("global_imports", {}).get(current_file, [])

    try:
        ctx = (
            f"Файл: {current_file}\nКод:\n{code}\n\n"
            f"Спецификации (A2):\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
            f"МИНИМАЛЬНЫЙ API контракт A5 (все эти функции ДОЛЖНЫ быть реализованы):\n"
            f"{json.dumps(file_contract, ensure_ascii=False, indent=2)}\n\n"
            f"Ключевые внешние импорты из A5 (могут быть расширены разработчиком — это нормально):\n"
            f"{json.dumps(global_imports, ensure_ascii=False, indent=2)}"
        )
        result   = await ask_agent(logger, "self_reflect", ctx, cache, 0, randomize, language, max_retries=SELF_REFLECT_RETRIES)
        status   = result.get("status", "OK")
        feedback = to_str(result.get("feedback", ""))
        improved = _sanitize_llm_code(to_str(result.get("improved_code", "")))

        if status == "NEEDS_IMPROVEMENT" and improved:
            (src_path / current_file).write_text(improved, encoding="utf-8")
            logger.info(f"  → Self-Reflect улучшил код: {feedback[:TRUNCATE_FEEDBACK]}")

        stats.record("self_reflect", sr_model, status == "OK")
        return status, feedback
    except (LLMError, ValueError) as e:
        logger.exception(f"Self-Reflect упал: {e}")
        stats.record("self_reflect", sr_model, False)
        return "OK", ""


async def phase_validate_architecture(
    logger: logging.Logger,
    project_path: Path,
    state: Optional[dict],
    cache: ThreadSafeCache,
    stats: ModelStats,
    arch_resp: dict,
    sa_resp: dict,
    task: str,
    language: str = "python",
    randomize: bool = False,
) -> bool:
    arch_text = json.dumps(arch_resp, ensure_ascii=False, indent=2)
    sa_text   = json.dumps(sa_resp,   ensure_ascii=False, indent=2)

    validation_map = [
        ("Системный аналитик", "system_analyst",
         "Проверь соответствие архитектуры бизнес-требованиям и спецификации."),
        ("Architect Validator", "arch_validator",
         "Проверь реализуемость, production-readiness и корректность для языка."),
        ("DevOps-инженер",     "devops_runtime",
         "Проверь Docker-совместимость, корректность зависимостей и базового образа."),
    ]

    rejections = 0
    for label, agent_key, instruction in validation_map:
        logger.info(f"🔍 Валидация архитектуры — {label} ...")
        val_ctx = (
            f"Запрос: {task}\n\n"
            f"Спецификация (SA): {sa_text}\n\n"
            f"Предложенная архитектура: {arch_text}\n\n"
            f"Язык: {LANG_DISPLAY.get(language, language)}\n\n"
            f"Задача проверки: {instruction}"
        )
        try:
            val_resp = await ask_agent(logger, agent_key, val_ctx, cache, 0, randomize, language)
            if val_resp.get("status") in ("REJECT", "CANNOT_FIX"):
                fb = to_str(val_resp.get("feedback", val_resp.get("explanation", "")))
                logger.warning(f"  ❌ {label} отклонил: {fb[:TRUNCATE_FEEDBACK]}")
                rejections += 1
                stats.record(agent_key, get_model(agent_key), False)
            else:
                logger.info(f"  ✅ {label} одобрил.")
                stats.record(agent_key, get_model(agent_key), True)
        except (LLMError, ValueError) as e:
            logger.exception(f"{label} упал: {e}")
            rejections += 1

        if rejections > 1:
            return False

    logger.info("✅ Архитектура прошла многоуровневую валидацию!")
    return True

async def phase_a5_compliance_review(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    randomize: bool = False,
) -> bool:
    logger.info("\n🔍 A5 Compliance Review (BA + Architect + Contract) ...")
    language = state.get("language", "python")
    src_path = project_path / SRC_DIR

    all_code = get_full_context(src_path, state["files"])
    a5_contract = safe_contract(state)

    agents = [
        ("a5_business_reviewer", "Business Analyst"),
        ("a5_architect_reviewer", "Architect"),
        ("a5_contract_reviewer", "Contract Compliance"),
    ]

    gather_results = await asyncio.gather(
        *[ask_agent(logger, ak, 
                    f"A5 Contract:\n{json.dumps(a5_contract, ensure_ascii=False, indent=2)}\n\n"
                    f"Код проекта:\n{all_code}\n\n"
                    f"A1/A2:\n{json.dumps(state.get('business_requirements', {}), ensure_ascii=False, indent=2)}\n"
                    f"A3/A4:\n{state.get('architecture', '')}",
                    cache, 0, randomize, language) 
          for ak, _ in agents],
        return_exceptions=True,
    )

    rejections = []
    for (agent_key, label), result in zip(agents, gather_results):
        if isinstance(result, Exception):
            logger.exception(f"{label} упал")
            rejections.append((agent_key, "CRITICAL", str(result)))
            continue

        status = result.get("status", "REJECT")
        feedback = to_str(result.get("feedback", ""))
        if status == "REJECT":
            rejections.append((agent_key, label, feedback))
            stats.record(agent_key, get_model(agent_key), False)
        else:
            stats.record(agent_key, get_model(agent_key), True)

    if rejections:
        logger.warning(f"❌ A5 Compliance отклонён ({len(rejections)} ревьюеров)")
        combined_fb = "\n\n".join([f"[{label}] {fb}" for _, label, fb in rejections])
        for f in state["files"]:
            state["feedbacks"][f] = f"A5 COMPLIANCE REJECT:\n{combined_fb}"
            if f in state.get("approved_files", []):
                state["approved_files"].remove(f)
        save_artifact(project_path, "A5.1", {"status": "REJECT", "rejections": rejections})
        return False

    logger.info("✅ A5 полностью соответствует всем артефактам!")
    state["a5_compliance_passed"] = True
    save_artifact(project_path, "A5.1", {"status": "APPROVE_ALL"})
    return True

async def phase_develop(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    randomize: bool = False,
) -> tuple[list[str], list[str]]:
    """Возвращает (exhausted_files, spec_blocked_files)."""
    language  = state.get("language", "python")
    src_path  = project_path / SRC_DIR
    order     = build_dependency_order(state["files"], src_path)
    file_attempts: dict[str, int] = state.setdefault("file_attempts", {})
    exhausted_files: list[str] = []
    spec_blocked_files: list[str] = []
    # Суммарные попытки (не сбрасываются при revise_spec) — для предохранителя
    if not isinstance(state.get("cumulative_file_attempts"), dict):
        state["cumulative_file_attempts"] = {}
    cumulative_attempts: dict[str, int] = state["cumulative_file_attempts"]

    for current_file in order:
        if current_file in state.get("approved_files", []):
            logger.info(f"⏭️  {current_file} уже одобрен.")
            continue

        attempt = file_attempts.get(current_file, 0)
        total_attempts = cumulative_attempts.get(current_file, 0)

        # Предохранитель: файл не проходит ревью после множества попыток → принудительный approve
        force_approve_mode = total_attempts >= MAX_CUMULATIVE
        if force_approve_mode:
            file_path = src_path / current_file
            if file_path.exists() and file_path.read_text(encoding="utf-8").strip():
                # Перед force-approve: инжектируем A5 imports в код на диске
                gi = safe_contract(state).get("global_imports", {}).get(current_file, [])
                if gi:
                    existing = file_path.read_text(encoding="utf-8")
                    patched = _ensure_a5_imports(existing, gi)
                    if patched != existing:
                        file_path.write_text(patched, encoding="utf-8")
                        logger.info(f"  📎 {current_file}: A5 imports авто-инжектированы при force-approve")
                logger.warning(
                    f"⚠️  {current_file} не прошёл ревью за {total_attempts} суммарных попыток "
                    f"→ принудительный APPROVE (код есть, проверим при интеграции)."
                )
                approved = state.setdefault("approved_files", [])
                if current_file not in approved:
                    approved.append(current_file)
                state["feedbacks"][current_file] = ""
                file_attempts[current_file] = 0
                continue
            else:
                # Файл не на диске — даём developer ещё попытку, approve после записи
                logger.warning(
                    f"⚠️  {current_file}: cumulative={total_attempts} но файла нет на диске "
                    f"→ пишем код без проверок."
                )
                file_attempts[current_file] = 0
                attempt = 0

        if attempt >= MAX_FILE_ATTEMPTS:
            logger.warning(
                f"⚠️  {current_file} исчерпал {MAX_FILE_ATTEMPTS} попыток → эскалация в spec_reviewer."
            )
            state["feedbacks"][current_file] = (
                f"Файл не удалось написать за {MAX_FILE_ATTEMPTS} попыток. "
                "Возможно, спецификация противоречива. Требуется revise_spec."
            )
            exhausted_files.append(current_file)
            continue

        file_path = src_path / current_file
        # Проверяем, что файл не выходит за пределы src_path (защита от ../атак)
        try:
            file_path.resolve().relative_to(src_path.resolve())
        except ValueError:
            logger.warning(f"Небезопасный путь файла: {current_file} — пропускаю.")
            continue
        file_path.parent.mkdir(parents=True, exist_ok=True)

        existing_code  = file_path.read_text(encoding="utf-8").strip() if file_path.exists() else ""
        global_context = get_global_context(src_path, state["files"], exclude=current_file)

        # A5: контракт для текущего файла
        file_contract  = safe_contract(state).get("file_contracts", {}).get(current_file, [])
        global_imports = safe_contract(state).get("global_imports", {}).get(current_file, [])

        # Патч A5 после 3+ неудачных попыток — контракт может не соответствовать реальности
        # Лимит: не более 2 патч-ресетов на файл (чтобы не откладывать force-approve бесконечно)
        a5_patch_counts: dict = state.setdefault("_a5_patch_counts", {})
        patches_done = a5_patch_counts.get(current_file, 0)
        if attempt >= 3 and file_contract and existing_code and patches_done < MAX_A5_PATCHES_PER_FILE:
            last_feedback = state.get("feedbacks", {}).get(current_file, "")
            if last_feedback:
                patched = await patch_contract_for_file(
                    logger, project_path, state, cache, stats,
                    current_file, existing_code, last_feedback, randomize,
                )
                if patched:
                    a5_patch_counts[current_file] = patches_done + 1
                    file_contract  = safe_contract(state).get("file_contracts", {}).get(current_file, [])
                    global_imports = safe_contract(state).get("global_imports", {}).get(current_file, [])
                    # Сброс попыток после патча A5 — дать developer шанс с новым контрактом
                    file_attempts[current_file] = 0
                    attempt = 0
                    logger.info(f"🔄 A5 для {current_file} обновлён (патч {patches_done + 1}/{MAX_A5_PATCHES_PER_FILE}) → счётчик попыток сброшен.")

        dev_ctx = (
            f"Задача:\n{state['task']}\n\n"
            f"СИСТЕМНЫЕ СПЕЦИФИКАЦИИ (A2):\n"
            f"{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
            f"Файл для написания: `{current_file}`.\n\n"
        )

        # Специальная инструкция для entry point — не раздувать бизнес-логикой
        if current_file == state.get("entry_point"):
            dev_ctx += (
                "⚠️ ЭТОТ ФАЙЛ — ТОЧКА ВХОДА ПРИЛОЖЕНИЯ.\n"
                "НЕ определяй здесь бизнес-классы — они в других файлах, ИМПОРТИРУЙ их.\n"
                "Содержимое: импорты + инициализация + запуск (идиоматичная точка входа для целевого языка).\n\n"
            )

        # Специальная инструкция для data-only файлов (models.py, data_models.py)
        if Path(current_file).stem in ("models", "data_models"):
            dev_ctx += (
                "⚠️ ЭТОТ ФАЙЛ — ХРАНИЛИЩЕ DATA STRUCTURES (data-only).\n"
                "ОБЯЗАТЕЛЬНО:\n"
                "  - Определи ЗДЕСЬ ВСЕ классы/структуры из контракта ниже\n"
                "  - Используй идиоматичные структуры данных для целевого языка\n"
                "КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО:\n"
                "  - Импортировать из ДРУГИХ ФАЙЛОВ ПРОЕКТА\n"
                "  - Определять PUBLIC top-level функции\n"
                "  - Допускаются ТОЛЬКО: stdlib импорты\n"
                "  - Приватные хелперы допустимы\n"
                "Другие модули будут импортировать структуры ОТСЮДА.\n\n"
            )

        # Добавляем A5 если он есть
        if file_contract:
            dev_ctx += (
                f"API КОНТРАКТ (A5) — реализуй ИМЕННО эти функции/классы:\n"
                f"{json.dumps(file_contract, ensure_ascii=False, indent=2)}\n\n"
            )
        if global_imports:
            dev_ctx += (
                f"ОЖИДАЕМЫЕ ИМПОРТЫ (A5):\n"
                f"{json.dumps(global_imports, ensure_ascii=False, indent=2)}\n\n"
            )
        req_path = src_path / "requirements.txt"
        if req_path.exists():
            req_content = req_path.read_text(encoding="utf-8").strip()
            if req_content:
                dev_ctx += (
                    f"ДОСТУПНЫЕ PIP-ПАКЕТЫ (requirements.txt):\n{req_content}\n"
                    f"⛔ Импорт пакетов НЕ из этого списка будет отклонён.\n\n"
                )
        if global_context:
            dev_ctx += f"ГЛОБАЛЬНЫЙ КОНТЕКСТ (public API других файлов):\n{global_context}\n\n"
            # Извлекаем имена классов/функций из других файлов + файл-источник
            _import_hints: list[str] = []
            _cur_file = ""
            for _gc_line in global_context.splitlines():
                if _gc_line.startswith("--- ") and _gc_line.endswith(" PUBLIC API ---"):
                    _cur_file = _gc_line.split("---")[1].strip().replace(" PUBLIC API ", "")
                elif _cur_file:
                    _m = re.match(r"(?:class|def|async def)\s+(\w+)", _gc_line.strip())
                    if _m:
                        _name = _m.group(1)
                        _stem = Path(_cur_file).stem
                        _import_hints.append(f"from {_stem} import {_name}")
            if _import_hints:
                dev_ctx += (
                    f"⛔ ЗАПРЕЩЕНО ПЕРЕОПРЕДЕЛЯТЬ эти классы/функции — они УЖЕ СУЩЕСТВУЮТ.\n"
                    f"ИСПОЛЬЗУЙ ИМПОРТ:\n"
                    + "\n".join(f"  {h}" for h in _import_hints)
                    + "\n\n"
                )
        if existing_code:
            max_code_chars = MAX_CONTEXT_CHARS // 2
            if len(existing_code) > max_code_chars:
                existing_code = existing_code[:max_code_chars] + "\n# [... код обрезан ...]"
            dev_ctx += f"ТЕКУЩИЙ КОД `{current_file}`:\n{existing_code}\n\n"
        feedback_ctx = get_feedback_ctx(state, current_file)
        if feedback_ctx:
            max_feedback_chars = MAX_CONTEXT_CHARS // 3
            if len(feedback_ctx) > max_feedback_chars:
                feedback_ctx = feedback_ctx[:max_feedback_chars] + "\n[... обрезано ...]"
            # Если есть и код и фидбэк — явная инструкция на точечное исправление
            if existing_code:
                dev_ctx += (
                    "⚠️ ПРАВЬ ТОЧЕЧНО: текущий код уже предоставлен выше. "
                    "Исправь ТОЛЬКО проблемы из фидбэка ниже, сохрани работающую структуру.\n\n"
                )
            dev_ctx += feedback_ctx

        dev_model = get_model("developer", attempt, randomize=randomize)
        logger.info(
            f"💻 [{dev_model}] Разработчик пишет {current_file} (попытка {attempt + 1}/{MAX_FILE_ATTEMPTS}) ..."
        )

        try:
            dev_resp = await ask_agent(logger, "developer", dev_ctx, cache, attempt, randomize, language)
            code     = _sanitize_llm_code(dev_resp.get("code", ""))
        except (LLMError, ValueError) as e:
            logger.exception(f"Developer упал: {e}")
            stats.record("developer", dev_model, False)
            state["feedbacks"][current_file] = f"Агент не вернул код: {e}"
            file_attempts[current_file] = attempt + 1
            cumulative_attempts[current_file] = total_attempts + 1
            continue

        if not code:
            stats.record("developer", dev_model, False)
            state["feedbacks"][current_file] = "Агент вернул пустой код."
            file_attempts[current_file] = attempt + 1
            cumulative_attempts[current_file] = total_attempts + 1
            continue

        # Проверка: если код — только imports + пустые строки (модель не написала тело функций),
        # генерируем скелет из A5 контракта и повторяем запрос с ним как "existing_code"
        code_lines = [ln for ln in code.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        non_import_lines = [ln for ln in code_lines
                            if not ln.strip().startswith(("import ", "from "))
                            and not ln.strip().startswith(("class ", "def "))]
        has_functions = any(ln.strip().startswith(("def ", "class ", "async def ")) for ln in code_lines)
        if not has_functions and file_contract and attempt < MAX_FILE_ATTEMPTS - 1:
            logger.warning(
                f"  ⚠️  {current_file}: developer вернул код без функций/классов — генерирую скелет из A5"
            )
            skeleton_parts = []
            if global_imports:
                for imp in global_imports:
                    if isinstance(imp, str):
                        skeleton_parts.append(imp)
                skeleton_parts.append("")
            for item in file_contract:
                if not isinstance(item, dict):
                    continue
                sig = item.get("signature", "")
                hints = item.get("implementation_hints", "")
                desc = item.get("description", "")
                if sig.strip().startswith("class "):
                    skeleton_parts.append(f"{sig}:")
                    skeleton_parts.append(f"    \"\"\"{desc}\"\"\"")
                    skeleton_parts.append(f"    # TODO: {hints}")
                    skeleton_parts.append(f"    pass")
                    skeleton_parts.append("")
                elif sig.strip().startswith(("def ", "async def ")):
                    skeleton_parts.append(f"{sig}:")
                    skeleton_parts.append(f"    \"\"\"{desc}\"\"\"")
                    skeleton_parts.append(f"    # Алгоритм: {hints}")
                    skeleton_parts.append(f"    pass")
                    skeleton_parts.append("")
            skeleton_code = "\n".join(skeleton_parts)
            state["feedbacks"][current_file] = (
                f"Ты вернул код БЕЗ функций/классов — только импорты.\n"
                f"НИЖЕ — СКЕЛЕТ из A5 контракта. Заполни ВСЕ функции/классы реальным кодом.\n"
                f"Убери pass и TODO, напиши ПОЛНУЮ рабочую реализацию по алгоритму в комментариях.\n"
            )
            # Записываем скелет как existing_code для следующей попытки
            file_path.write_text(skeleton_code, encoding="utf-8")
            file_attempts[current_file] = attempt + 1
            cumulative_attempts[current_file] = total_attempts + 1
            stats.record("developer", dev_model, False)
            continue

        # Авто-инъекция A5 импортов — developer часто забывает import numpy, from typing и т.д.
        if global_imports:
            code = _ensure_a5_imports(code, global_imports)

        # Force-approve mode: файл не на диске после MAX_CUMULATIVE попыток →
        # записываем что есть и approve без проверок
        if force_approve_mode:
            file_path.write_text(code, encoding="utf-8")
            logger.warning(
                f"⚠️  {current_file}: force-approve mode → код записан и одобрен без проверок."
            )
            stats.record("developer", dev_model, True)
            approved = state.setdefault("approved_files", [])
            if current_file not in approved:
                approved.append(current_file)
            state["feedbacks"][current_file] = ""
            file_attempts[current_file] = 0
            continue

        # Детерминистская проверка: не потерял ли developer функции из предыдущей версии
        if existing_code:
            last_fb = state.get("feedbacks", {}).get(current_file, "")
            pres_warnings = _check_function_preservation(code, existing_code, last_fb, file_contract)
            if pres_warnings:
                pres_feedback = (
                    "АВТОМАТИЧЕСКИЙ REJECT — потеря функций из предыдущей версии:\n"
                    + "\n".join(f"  - {w}" for w in pres_warnings)
                    + "\n\n⚠️ НЕ ПЕРЕПИСЫВАЙ файл с нуля. Исправь ТОЛЬКО то, что указано "
                    "в фидбэке. Сохрани ВСЮ существующую структуру."
                )
                logger.warning(f"⛔ {current_file}: {len(pres_warnings)} функций потеряно → авто-REJECT")
                stats.record("developer", dev_model, False)
                push_feedback(state, current_file, pres_feedback)
                file_attempts[current_file] = attempt + 1
                cumulative_attempts[current_file] = total_attempts + 1
                continue

        # Детерминистская проверка: не дублирует ли код классы из других файлов
        dup_warnings = _check_class_duplication(code, global_context, file_contract)
        if dup_warnings:
            dup_feedback = (
                "АВТОМАТИЧЕСКИЙ REJECT — дублирование классов из других файлов проекта:\n"
                + "\n".join(f"  - {w}" for w in dup_warnings)
                + "\n\nНЕ ОПРЕДЕЛЯЙ эти классы заново. Используй import."
            )
            logger.warning(f"⛔ {current_file}: дублирование {len(dup_warnings)} классов → автоматический REJECT")
            stats.record("developer", dev_model, False)
            push_feedback(state, current_file, dup_feedback)
            file_attempts[current_file] = attempt + 1
            cumulative_attempts[current_file] = total_attempts + 1
            continue

        # Детерминистская проверка: import shadowing (from X import Y + def Y)
        shadow_warnings = _check_import_shadowing(code)
        if shadow_warnings:
            shadow_feedback = (
                "АВТОМАТИЧЕСКИЙ REJECT — конфликт имён (import + определение):\n"
                + "\n".join(f"  - {w}" for w in shadow_warnings)
                + "\n\nЕсли имя импортировано из другого файла — НЕ определяй его заново."
            )
            logger.warning(f"⛔ {current_file}: {len(shadow_warnings)} конфликтов имён → авто-REJECT")
            stats.record("developer", dev_model, False)
            push_feedback(state, current_file, shadow_feedback)
            file_attempts[current_file] = attempt + 1
            cumulative_attempts[current_file] = total_attempts + 1
            continue

        # Детерминистская проверка: data-only файл (models.py) не должен импортировать из проекта
        data_only_warnings = _check_data_only_violations(code, current_file, state["files"])
        if data_only_warnings:
            data_only_feedback = (
                "АВТОМАТИЧЕСКИЙ REJECT — нарушение правил data-only файла:\n"
                + "\n".join(f"  - {w}" for w in data_only_warnings)
                + f"\n\n{current_file} — это файл для ХРАНЕНИЯ data structures.\n"
                "Он НЕ ДОЛЖЕН импортировать из других файлов проекта.\n"
                "Он НЕ ДОЛЖЕН содержать бизнес-логику (функции).\n"
                "Другие файлы импортируют ОТСЮДА, а не наоборот."
            )
            logger.warning(f"⛔ {current_file}: data-only нарушения → авто-REJECT")
            stats.record("developer", dev_model, False)
            push_feedback(state, current_file, data_only_feedback)
            file_attempts[current_file] = attempt + 1
            cumulative_attempts[current_file] = total_attempts + 1
            continue

        # Детерминистская проверка: валидность импортов (stdlib / pip / проект)
        req_path = src_path / "requirements.txt"
        import_warnings = validate_imports(
            code, current_file, state["files"],
            req_path if req_path.exists() else None, language, src_path,
        )
        if import_warnings:
            # Подсказка: показать ожидаемые импорты из A5
            expected_hint = ""
            if global_imports:
                expected_hint = (
                    "\n\nОЖИДАЕМЫЕ ИМПОРТЫ из A5 контракта для этого файла:\n"
                    + "\n".join(f"  {imp}" for imp in global_imports)
                )
            req_content_hint = ""
            if req_path.exists():
                rc = req_path.read_text(encoding="utf-8").strip()
                if rc:
                    req_content_hint = f"\n\nСодержимое requirements.txt (доступные пакеты):\n{rc}"
            import_feedback = (
                "АВТОМАТИЧЕСКИЙ REJECT — невалидные импорты:\n"
                + "\n".join(f"  - {w}" for w in import_warnings)
                + "\n\nИсправь: используй только stdlib, pip-пакеты из requirements.txt "
                "или модули проекта: " + ", ".join(state["files"])
                + expected_hint
                + req_content_hint
            )
            logger.warning(f"⛔ {current_file}: {len(import_warnings)} ошибок импорта → авто-REJECT")
            stats.record("developer", dev_model, False)
            push_feedback(state, current_file, import_feedback)
            file_attempts[current_file] = attempt + 1
            cumulative_attempts[current_file] = total_attempts + 1
            continue

        # Детерминистская проверка: кросс-файловые имена (from X import Y → Y существует в X)
        if language == "python":
            xfile_warnings = validate_cross_file_names(
                code, current_file, state["files"], src_path,
            )
            if xfile_warnings:
                xfile_feedback = (
                    "АВТОМАТИЧЕСКИЙ REJECT — ошибки кросс-файловых имён:\n"
                    + "\n".join(f"  - {w}" for w in xfile_warnings)
                    + "\n\nПроверь что все импортируемые имена определены в целевых файлах."
                )
                logger.warning(f"⛔ {current_file}: {len(xfile_warnings)} ошибок имён → авто-REJECT")
                stats.record("developer", dev_model, False)
                push_feedback(state, current_file, xfile_feedback)
                file_attempts[current_file] = attempt + 1
                cumulative_attempts[current_file] = total_attempts + 1
                continue

        # Детерминистская проверка: нет ли функций-заглушек (pass, ..., NotImplementedError)
        stub_warnings = _check_stub_functions(code)
        if stub_warnings:
            stub_feedback = (
                "АВТОМАТИЧЕСКИЙ REJECT — функции-заглушки:\n"
                + "\n".join(f"  - {w}" for w in stub_warnings)
                + "\n\nВесь код должен быть полностью рабочим. Заглушки (pass, ..., "
                "raise NotImplementedError) и фиктивные реализации "
                "(захардкоженные return без использования параметров) ЗАПРЕЩЕНЫ."
            )
            logger.warning(f"⛔ {current_file}: {len(stub_warnings)} заглушек → авто-REJECT")
            stats.record("developer", dev_model, False)
            push_feedback(state, current_file, stub_feedback)
            file_attempts[current_file] = attempt + 1
            cumulative_attempts[current_file] = total_attempts + 1
            continue

        # Детерминистская проверка: все required функции/классы из A5 контракта присутствуют
        contract_missing = _check_contract_compliance(code, file_contract)
        if contract_missing:
            contract_feedback = (
                "АВТОМАТИЧЕСКИЙ REJECT — отсутствуют required элементы из A5 контракта:\n"
                + "\n".join(f"  - {m}" for m in contract_missing)
                + "\n\nРеализуй ВСЕ функции/классы, указанные в API контракте A5."
            )
            logger.warning(f"⛔ {current_file}: отсутствуют {len(contract_missing)} элементов A5 → авто-REJECT")
            stats.record("developer", dev_model, False)
            push_feedback(state, current_file, contract_feedback)
            file_attempts[current_file] = attempt + 1
            cumulative_attempts[current_file] = total_attempts + 1
            continue

        file_path.write_text(code, encoding="utf-8")

        # Self-Reflect с проверкой A5
        sr_status, sr_feedback = await do_self_reflect(
            logger, cache, src_path, current_file, code, state, stats, randomize
        )
        if sr_status == "NEEDS_IMPROVEMENT":
            # Перечитываем файл — self-reflect мог записать улучшенный код
            new_code = file_path.read_text(encoding="utf-8")
            # Повторяем ключевые проверки на улучшенном коде
            _sr_ok = True
            for _sr_check_name, _sr_warnings in [
                ("function_preservation", _check_function_preservation(code, new_code, "", file_contract)),
                ("class_duplication", _check_class_duplication(new_code, current_file, state, src_path)),
                ("import_shadowing", _check_import_shadowing(new_code)),
                ("data_only", _check_data_only_violations(new_code, current_file, state["files"])),
                ("imports", validate_imports(new_code, current_file, state["files"],
                                            req_path if req_path.exists() else None, language, src_path)),
                ("cross_file_names", validate_cross_file_names(
                    new_code, current_file, state["files"], src_path) if language == "python" else []),
                ("stubs", _check_stub_functions(new_code)),
                ("contract", _check_contract_compliance(new_code, file_contract)),
            ]:
                if _sr_warnings:
                    logger.warning(f"  ⚠️  Self-reflect ввёл ошибки ({_sr_check_name}) → откат")
                    file_path.write_text(code, encoding="utf-8")  # откат к оригиналу
                    _sr_ok = False
                    break
            if _sr_ok:
                code = new_code

        # Внешний ревью
        rev_status, rev_feedback, needs_spec = await _review_file(
            logger, cache, current_file, code, attempt, stats, randomize, language,
            file_contract=file_contract, global_imports=global_imports,
        )

        if rev_status == "APPROVE":
            stats.record("developer", dev_model, True)
            logger.info(f"✅ {current_file} одобрен.")
            approved = state.setdefault("approved_files", [])
            if current_file not in approved:
                approved.append(current_file)
            state["feedbacks"][current_file] = ""
            state.setdefault("feedback_history", {})[current_file] = []
            file_attempts[current_file] = 0
            # Обновляем A9 (Implementation Logs)
            update_artifact_a9(project_path, current_file, f"Одобрен на попытке {attempt + 1}. Модель: {dev_model}.")
        else:
            stats.record("developer", dev_model, False)
            combined = "\n".join(filter(None, [to_str(sr_feedback), to_str(rev_feedback)]))
            # Защита от пустого feedback при REJECT
            if not combined:
                combined = (
                    f"Reviewer отклонил {current_file} без конкретных замечаний. "
                    "Проверь: корректность импортов из других файлов проекта, "
                    "соответствие API контракту A5, полноту реализации всех функций, "
                    "типы данных параметров и возвращаемых значений."
                )
            # Уведомление: spec зафиксирована
            if needs_spec and len(state.get("spec_history", [])) >= 3:
                combined += (
                    "\n\nСПЕЦИФИКАЦИЯ ЗАФИКСИРОВАНА (лимит ревизий исчерпан). "
                    "НЕ жди изменений спецификации — реши проблему В РАМКАХ текущего API контракта. "
                    "Адаптируй код под текущие интерфейсы файлов проекта."
                )
            logger.warning(f"❌ {current_file} отклонён: {combined[:TRUNCATE_FEEDBACK]}")
            push_feedback(state, current_file, combined)
            file_attempts[current_file] = attempt + 1
            cumulative_attempts[current_file] = total_attempts + 1
            # Эскалация на spec только после 3+ неудачных попыток
            # (до этого patch_contract_for_file попробует починить A5)
            if needs_spec and attempt + 1 >= MAX_FILE_ATTEMPTS and current_file not in spec_blocked_files:
                spec_blocked_files.append(current_file)

    return exhausted_files, spec_blocked_files


async def phase_e2e_review(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    attempt: int = 0,
    randomize: bool = False,
) -> bool:
    logger.info("\n🧐 Parallel E2E-ревью (Architect + QA) ...")
    language = state.get("language", "python")
    src_path = project_path / SRC_DIR
    all_code = get_full_context(src_path, state["files"])
    # Добавляем информацию о файлах проекта, чтобы ревьюер не галлюцинировал
    file_list_info = (
        f"\n\nПРОЕКТ СОСТОИТ РОВНО ИЗ ЭТИХ ФАЙЛОВ (других файлов НЕТ, не требуй создания новых): "
        f"{', '.join(state['files'])}\n"
    )
    all_code = file_list_info + all_code

    agents = [("e2e_architect", "Architect"), ("e2e_qa", "QA Lead")]
    result_ok = True
    rejections: list[tuple[str, str, str]] = []  # (agent_key, target, feedback)

    # Параллельный запуск через asyncio.gather вместо ThreadPoolExecutor
    gather_results = await asyncio.gather(
        *[ask_agent(logger, ak, all_code, cache, attempt, randomize, language) for ak, _ in agents],
        return_exceptions=True,
    )

    for (agent_key, label), result in zip(agents, gather_results):
        model = get_model(agent_key, attempt, randomize)
        if isinstance(result, Exception):
            logger.exception(f"[{label}] future error: {result}")
            stats.record(agent_key, model, False)
            result_ok = False
            continue

        resp = result
        if resp.get("status") == "REJECT":
            # Парсим structured issues (новый формат) с fallback на старый
            issues = resp.get("issues", [])
            if issues and isinstance(issues, list):
                for issue in issues:
                    if not isinstance(issue, dict):
                        continue
                    target = issue.get("file", "").strip()
                    if target not in state["files"]:
                        target = state["files"][0]
                    element  = issue.get("element", "")
                    severity = issue.get("severity", "MAJOR")
                    problem  = issue.get("problem", "")
                    fix_text = issue.get("fix", "")
                    structured_fb = f"[{severity}] {element}: {problem}\n  FIX: {fix_text}"
                    rejections.append((agent_key, target, structured_fb))
                logger.warning(f"❌ E2E [{label}] REJECT: {len(issues)} issues")
            else:
                # Fallback: старый формат target_file + feedback
                target   = resp.get("target_file", "").strip() or state["files"][0]
                feedback = to_str(resp.get("feedback", ""))
                logger.warning(f"❌ E2E [{label}] REJECT на {target}: {feedback[:TRUNCATE_FEEDBACK]}")
                rejections.append((agent_key, target, feedback))
            stats.record(agent_key, model, False)
            result_ok = False
        else:
            stats.record(agent_key, model, True)

    # E2E — селективный сброс с per-file targeted feedback.
    if rejections:
        agents_map = dict(agents)
        # Группируем feedback по файлам
        file_feedbacks: dict[str, list[str]] = {}
        for ak, target, fb in rejections:
            file_feedbacks.setdefault(target, []).append(
                f"[{agents_map.get(ak, ak)}]:\n{fb}"
            )
        target_files = list(file_feedbacks.keys())

        # Если targets пуст или покрывает > 50% файлов — полный сброс
        if not target_files or len(target_files) > len(state["files"]) * 0.5:
            combined_fb = "\n\n".join(
                f"[{agents_map.get(ak, ak)}] → {t}:\n{fb}"
                for ak, t, fb in rejections
            )
            logger.warning(f"❌ E2E REJECT — сброс ВСЕХ файлов (затронуто >{50 if target_files else 0}%).")
            state["approved_files"] = []
            for f in state["files"]:
                state["feedbacks"][f] = f"E2E REJECT (кросс-файловая проблема):\n{combined_fb}"
            files_to_reset = set(state["files"])
        else:
            # Находим зависимые файлы (импортирующие target_files)
            gi = safe_contract(state).get("global_imports", {})
            target_stems = {Path(t).stem for t in target_files}
            dependent_files = set()
            for f in state["files"]:
                if f in target_files:
                    continue
                file_imports = gi.get(f, [])
                imports_str = " ".join(file_imports) if isinstance(file_imports, list) else str(file_imports)
                if any(stem in imports_str for stem in target_stems):
                    dependent_files.add(f)
            files_to_reset = set(target_files) | dependent_files
            logger.warning(
                f"❌ E2E REJECT — селективный сброс: {', '.join(sorted(files_to_reset))} "
                f"(targets: {', '.join(target_files)}, зависимые: {', '.join(sorted(dependent_files)) or 'нет'})"
            )
            state["approved_files"] = [f for f in state.get("approved_files", []) if f not in files_to_reset]
            for f in files_to_reset:
                if f in file_feedbacks:
                    state["feedbacks"][f] = (
                        "E2E REJECT — проблемы в ЭТОМ файле:\n"
                        + "\n\n".join(file_feedbacks[f])
                    )
                else:
                    related = [t for t in target_files if t != f]
                    state["feedbacks"][f] = (
                        f"E2E REJECT (зависимый файл, затронут изменениями в: "
                        f"{', '.join(related) if related else 'проект'})"
                    )

        # Сброс счётчиков: первый E2E-сброс → частичный reset (дать 5 попыток),
        # повторные → не сбрасывать (developer уже пробовал с E2E фидбэком).
        # Без этого: E2E reject → cumulative=0 → 15 итераций develop → force-approve
        # → E2E reject → cumulative=0 → ещё 15 итераций → ... (бесконечный цикл).
        e2e_resets = state.setdefault("e2e_cumulative_resets", {})
        cumulative = state.setdefault("cumulative_file_attempts", {})
        for f in files_to_reset:
            old_cum = cumulative.get(f, 0)
            resets_done = e2e_resets.get(f, 0)
            state["file_attempts"][f] = 0
            if resets_done < 1 and old_cum > 0:
                # Первый E2E-сброс: дать developer MAX_FILE_ATTEMPTS попыток
                new_cum = max(0, old_cum - MAX_FILE_ATTEMPTS)
                cumulative[f] = new_cum
                e2e_resets[f] = resets_done + 1
                logger.info(f"  🔄 {f}: cumulative {old_cum} → {new_cum} "
                            f"(E2E reset #{resets_done + 1}, дано {old_cum - new_cum} попыток)")
            elif old_cum > 0:
                # Повторный E2E-сброс: developer уже пробовал → не сбрасываем cumulative
                # → force-approve сработает мгновенно → E2E safety valve наберётся быстро
                logger.info(f"  🔒 {f}: cumulative={old_cum}, E2E уже сбрасывал → "
                            f"оставляем (force-approve мгновенно)")

    if result_ok:
        logger.info("✅ Parallel E2E-ревью пройдено!")
    return result_ok


def phase_cross_file_check(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
) -> bool:
    """Детерминистская кросс-файловая проверка всего проекта перед E2E.

    Если проблемы: снимает APPROVE с проблемных файлов, ставит feedback.
    Возвращает True если всё ОК, False если есть проблемы.
    """
    language = state.get("language", "python")
    if language != "python":
        return True

    src_path = project_path / SRC_DIR
    from code_context import validate_project_consistency
    issues = validate_project_consistency(src_path, state["files"])

    if not issues:
        logger.info("✅ Кросс-файловая проверка проекта пройдена.")
        return True

    total_issues = sum(len(w) for w in issues.values())
    logger.warning(f"⛔ Кросс-файловая проверка: {total_issues} проблем в {len(issues)} файлах")

    cumulative = state.setdefault("cumulative_file_attempts", {})
    has_actionable = False
    for filename, warnings in issues.items():
        # Не снимать approve с файлов, исчерпавших cumulative лимит
        # (иначе бесконечный цикл: принудительный approve → cross-file снимает → опять approve)
        if cumulative.get(filename, 0) >= MAX_CUMULATIVE:
            logger.warning(f"  ⚠️  {filename}: {len(warnings)} кросс-файловых проблем, "
                           f"но cumulative={cumulative[filename]} → оставляем APPROVE")
            continue
        feedback = (
            "АВТОМАТИЧЕСКИЙ REJECT — кросс-файловые ошибки (до E2E):\n"
            + "\n".join(f"  - {w}" for w in warnings)
        )
        state["feedbacks"][filename] = feedback
        approved = state.get("approved_files", [])
        if filename in approved:
            approved.remove(filename)
            logger.warning(f"  ⛔ {filename}: {len(warnings)} проблем → снят APPROVE")
        # Инкремент cumulative: без этого цикл develop→cross_file→develop
        # не приближает файл к force-approve лимиту (cumulative не растёт при APPROVE в develop).
        # Шаг 2 (не MAX_FILE_ATTEMPTS) — чтобы не съедать бюджет develop-попыток слишком быстро.
        cumulative[filename] = cumulative.get(filename, 0) + 2
        has_actionable = True

    if not has_actionable:
        logger.warning("⚠️  Кросс-файловые проблемы есть, но все файлы на cumulative лимите → пропускаем к E2E.")
        return True
    return False


def _fix_docker_requirements(src_path: Path, logger: logging.Logger) -> None:
    """Автоматическая замена пакетов, несовместимых с headless Docker-окружением."""
    req_path = src_path / "requirements.txt"
    if not req_path.exists():
        return
    HEADLESS_SUBSTITUTIONS = {
        "opencv-python": "opencv-python-headless",
        "opencv-contrib-python": "opencv-contrib-python-headless",
    }
    lines = req_path.read_text(encoding="utf-8").splitlines()
    changed = False
    new_lines = []
    for line in lines:
        pkg_base = re.split(r'[=<>~!\[]', line.strip())[0].strip().lower()
        if pkg_base in HEADLESS_SUBSTITUTIONS:
            replacement = HEADLESS_SUBSTITUTIONS[pkg_base]
            # Сохраняем версию если была
            suffix = line.strip()[len(pkg_base):]
            new_line = replacement + suffix
            logger.info(f"  🔧 {line.strip()} → {new_line} (headless для Docker)")
            new_lines.append(new_line)
            changed = True
        else:
            new_lines.append(line)
    if changed:
        req_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


async def phase_integration_test(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    randomize: bool = False,
) -> bool:
    language    = state.get("language", "python")
    entry_point = state.get("entry_point", "main.py")
    src_path    = project_path / SRC_DIR
    dockerfile  = src_path / "Dockerfile"    # Dockerfile теперь в src/
    use_custom  = dockerfile.exists()
    image_tag   = f"{project_path.name}:latest" if use_custom else get_docker_image(language)

    # Превентивная замена пакетов, несовместимых с Docker (opencv → headless)
    if language == "python":
        _fix_docker_requirements(src_path, logger)

    # ── Сборка образа ────────────────────────────────────────────────────────
    build_success = False
    for build_attempt in range(1, 4):
        if use_custom:
            logger.info(f"\n🏗️ Сборка Docker-образа (попытка {build_attempt}/3) ...")
            build_success, _, build_err = build_docker_image(src_path, image_tag)
            if build_success:
                logger.info("✅ Образ собран.")
                break
            logger.error(f"❌ Ошибка сборки:\n{build_err[:TRUNCATE_ERROR_MSG]}")
            try:
                devops_ctx  = (
                    f"Ошибка сборки Docker:\n{build_err}\n\n"
                    f"Текущий Dockerfile:\n{dockerfile.read_text(encoding='utf-8')}"
                )
                devops_resp = await ask_agent(
                    logger, "devops_runtime", devops_ctx, cache, 0, randomize, language
                )
                stats.record("devops_runtime", get_model("devops_runtime"), True)
                patch = devops_resp.get("dockerfile_patch", "")
                if devops_resp.get("status") == "FIX_PROPOSED" and isinstance(patch, str) and patch.strip():
                    update_dockerfile(src_path, patch)
                    logger.info("  → Dockerfile обновлён, пересобираю.")
            except (LLMError, ValueError) as e:
                logger.exception(f"DevOps (build) упал: {e}")
                stats.record("devops_runtime", get_model("devops_runtime"), False)
        else:
            build_success = True
            break

    if not build_success:
        state["feedbacks"][state["files"][0]] = "Не удалось собрать Docker-образ."
        return False

    # ── Запуск приложения ────────────────────────────────────────────────────
    for run_attempt in range(1, 6):
        logger.info(f"\n🚀 Запуск в Docker (попытка {run_attempt}/5) ...")
        cmd = get_execution_command(language, entry_point)

        env_fixes = state.get("env_fixes", {})
        if env_fixes.get("system_packages"):
            cmd = "apt-get update -q && apt-get install -y " + " ".join(env_fixes["system_packages"]) + " && " + cmd
        if language == "python":
            for orig, alt in (env_fixes.get("package_alternatives") or env_fixes.get("pip_alternatives") or {}).items():
                update_requirements(src_path, orig, alt)

        rc, stdout, stderr = run_in_docker(src_path, cmd, RUN_TIMEOUT, language)

        # Логи рантайма — в .factory/logs/
        logs_dir = project_path / FACTORY_DIR / LOGS_DIR
        logs_dir.mkdir(parents=True, exist_ok=True)
        (logs_dir / "test.log").write_text(
            f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}", encoding="utf-8"
        )
        logger.info(f"\n--- STDOUT ---\n{stdout[:TRUNCATE_LOG]}")
        logger.info(f"\n--- STDERR ---\n{stderr[:TRUNCATE_LOG]}")

        if rc == 0:
            # Проверяем: rc=0 но в stdout/stderr есть traceback → программа
            # поймала exception через try/except и вышла с кодом 0, маскируя ошибку
            combined_output = stdout + "\n" + stderr
            has_traceback = "Traceback (most recent call last)" in combined_output
            has_exception_line = bool(_EXCEPTION_LINE_RE.search(combined_output))
            if has_traceback and has_exception_line:
                logger.warning(
                    "⚠️  rc=0 но обнаружен traceback в выводе! "
                    "Программа поймала исключение через try/except. Считаем как провал."
                )
                log_runtime_error(project_path, combined_output)
                failing_file = find_failing_file(stderr, stdout, state["files"])
                state["feedbacks"][failing_file] = (
                    "ПРОГРАММА ЗАМАСКИРОВАЛА ОШИБКУ (rc=0, но traceback в выводе):\n"
                    f"{combined_output[-TRUNCATE_LOG:]}\n\n"
                    "Исправь причину exception — не ловить его через try/except, а устранить."
                )
                if failing_file in state.get("approved_files", []):
                    state["approved_files"].remove(failing_file)
                cum = state.setdefault("cumulative_file_attempts", {})
                cum[failing_file] = cum.get(failing_file, 0) + 3
                return False

            logger.info("\n✅ Приложение завершилось успешно!")
            state["env_fixes"] = {}
            return True

        logger.error("\n💥 Ошибка выполнения!")
        log_runtime_error(project_path, stderr)

        # Ошибка pip install/build — проблема зависимостей, не кода
        if language == "python" and any(kw in stderr for kw in [
            "pip subprocess to install build dependencies did not run successfully",
            "Failed building wheel",
            "No matching distribution found",
            "Could not find a version that satisfies",
            "error: subprocess-exited-with-error",
        ]):
            logger.info("🔧 Ошибка pip install — исправляю requirements.txt ...")
            req_path = src_path / "requirements.txt"
            if req_path.exists():
                from code_context import WRONG_PIP_PACKAGES
                lines = req_path.read_text(encoding="utf-8").splitlines()
                new_lines = []
                fixed_wrong = False
                for line in lines:
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        new_lines.append(line)
                        continue
                    # Исправляем невалидные pip-пакеты (opencv → opencv-python-headless)
                    pkg_base = re.split(r'[=<>~!]', stripped)[0].strip()
                    if pkg_base in WRONG_PIP_PACKAGES:
                        correct_pip, _ = WRONG_PIP_PACKAGES[pkg_base]
                        logger.info(f"  → {pkg_base} → {correct_pip} (невалидный pip-пакет)")
                        new_lines.append(correct_pip)
                        fixed_wrong = True
                        continue
                    # Убираем жёсткие версии (==x.y.z) → пусть pip найдёт совместимую
                    if pkg_base.lower() != stripped.lower():
                        logger.info(f"  → {stripped} → {pkg_base} (убрана версия)")
                        new_lines.append(pkg_base)
                    else:
                        new_lines.append(line)
                req_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
                if fixed_wrong:
                    logger.info("  ✅ requirements.txt: невалидные пакеты исправлены.")
                else:
                    logger.info("  ✅ requirements.txt обновлён (убраны версии).")
            continue  # Повторяем попытку с обновлёнными зависимостями

        failing_file = find_failing_file(stderr, stdout, state["files"])

        if any(kw in stderr.lower() for kw in ["lib", ".so", "cannot open shared object", "no such file"]):
            logger.info("🛠️  DevOps анализирует ошибку окружения ...")
            try:
                devops_ctx  = (
                    f"Traceback:\n{stderr}\n\n"
                    f"Dockerfile: {dockerfile.read_text(encoding='utf-8') if dockerfile.exists() else 'Нет'}"
                )
                devops_resp = await ask_agent(
                    logger, "devops_runtime", devops_ctx, cache, 0, randomize, language
                )
                stats.record("devops_runtime", get_model("devops_runtime"), True)
                if devops_resp.get("status") == "FIX_PROPOSED":
                    if devops_resp.get("dockerfile_patch"):
                        update_dockerfile(src_path, devops_resp["dockerfile_patch"])
                        logger.info("  → Dockerfile обновлён, требуется пересборка.")
                        return False
                    state["env_fixes"] = devops_resp
                    continue
            except (LLMError, ValueError) as e:
                logger.exception(f"DevOps (runtime) упал: {e}")
                stats.record("devops_runtime", get_model("devops_runtime"), False)

        qa_model = get_model("qa_runtime", run_attempt - 1, randomize)
        fix         = "Смотри traceback."
        missing_pkg = ""
        try:
            qa_resp     = await ask_agent(
                logger, "qa_runtime",
                f"Traceback:\n{stderr}\n\nФайл с ошибкой: {failing_file}",
                cache, run_attempt - 1, randomize, language,
            )
            fix         = qa_resp.get("fix", "Смотри traceback.")
            missing_pkg = qa_resp.get("missing_package", "").strip()
            agent_file  = qa_resp.get("file", "").strip()
            if agent_file and agent_file in state["files"]:
                failing_file = agent_file
            stats.record("qa_runtime", qa_model, True)
        except (LLMError, ValueError) as e:
            logger.exception(f"QA Runtime упал: {e}")
            stats.record("qa_runtime", qa_model, False)

        if missing_pkg:
            if language == "python":
                req_path = src_path / "requirements.txt"
                current_reqs = req_path.read_text(encoding="utf-8") if req_path.exists() else ""
                pkg_clean    = re.split(r'[=<>~]', missing_pkg)[0].strip().lower()
                existing     = [re.split(r'[=<>~]', l)[0].strip().lower()
                                for l in current_reqs.splitlines() if l.strip() and not l.startswith("#")]
                if pkg_clean in existing:
                    logger.warning(
                        f"⚠️  '{pkg_clean}' уже в requirements, но всё равно падает → возврат разработчику."
                    )
                    state["feedbacks"][failing_file] = (
                        f"ПРОГРАММА УПАЛА. Пакет '{pkg_clean}' установлен, но код падает. "
                        f"Проблема в логике или импортах.\nTraceback:\n{stderr}"
                    )
                    if failing_file in state.get("approved_files", []):
                        state["approved_files"].remove(failing_file)
                    cum = state.setdefault("cumulative_file_attempts", {})
                    cum[failing_file] = cum.get(failing_file, 0) + 3
                    return False
                else:
                    logger.info(f"🔧 Добавляю пакет: {missing_pkg}")
                    update_dependencies(src_path, language, missing_pkg)
                    continue
            elif language == "typescript":
                logger.info(f"🔧 Добавляю пакет в package.json: {missing_pkg}")
                update_dependencies(src_path, language, missing_pkg)
                continue

        if failing_file in state.get("approved_files", []):
            state["approved_files"].remove(failing_file)
        cum = state.setdefault("cumulative_file_attempts", {})
        cum[failing_file] = cum.get(failing_file, 0) + 3
        state["feedbacks"][failing_file] = f"ПРОГРАММА УПАЛА.\nTRACEBACK:\n{stderr}\nQA:\n{fix}"
        logger.info("🔄 Возврат к разработчику.")
        return False

    return False


def _classify_test_error(
    stderr: str, stdout: str, project_files: list[str],
) -> tuple[str, str]:
    """Классифицирует ошибку unit-тестов: 'test_bug' или 'app_bug'.

    test_bug — проблема в самих тестах (неправильный mock, import, assert).
    app_bug — проблема в коде приложения (функция возвращает не то, отсутствует метод).

    Возвращает (classification, failing_app_file_or_empty).
    """
    combined = stderr + "\n" + stdout

    # Все файлы из traceback (в порядке появления)
    all_traceback_files = re.findall(
        r'File "[^"]*[/\\]([^"]+\.py)", line \d+', combined
    )
    test_file_errors = [f for f in all_traceback_files if f.startswith("test_")]
    app_file_errors = [f for f in all_traceback_files
                       if f in project_files and not f.startswith("test_")]

    # Типичные ошибки тестов (проблема в тест-коде, не в приложении)
    test_bug_indicators = [
        "ModuleNotFoundError",
        "ImportError: cannot import name",
        "does not have the attribute",
        "fixture",
        "assert_called",
        "TypeError: test_",
    ]

    test_bug_score = 0
    app_bug_score = 0

    if test_file_errors:
        test_bug_score += len(test_file_errors) * 2
    if app_file_errors:
        app_bug_score += len(app_file_errors) * 2

    for indicator in test_bug_indicators:
        if indicator in combined:
            test_bug_score += 3

    # AssertionError: если traceback в app файлах → app_bug, иначе → test_bug
    if "AssertionError" in combined:
        if app_file_errors:
            app_bug_score += 2
        else:
            test_bug_score += 1

    # Ключевая эвристика: ПОСЛЕДНИЙ файл в traceback — причина ошибки.
    # Если это app файл → app_bug (ошибка упала ВНУТРИ кода приложения).
    if all_traceback_files:
        last_file = all_traceback_files[-1]
        if last_file in project_files and not last_file.startswith("test_"):
            app_bug_score += 5  # Сильный сигнал: exception возник в коде приложения

    failing_app_file = app_file_errors[-1] if app_file_errors else ""

    if test_bug_score >= app_bug_score:
        return "test_bug", ""
    return "app_bug", failing_app_file


async def phase_unit_tests(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    randomize: bool = False,
) -> bool:
    logger.info("\n🧪 Генерация unit-тестов ...")
    language = state.get("language", "python")
    src_path = project_path / SRC_DIR

    # Превентивная замена пакетов, несовместимых с Docker (opencv → headless)
    if language == "python":
        _fix_docker_requirements(src_path, logger)

    all_code = get_global_context(src_path, state["files"])

    # Передаём A7 (Test Plan) если есть
    test_plan = state.get("test_plan", {})

    # Контекст для генерации (неизменная часть)
    base_context = (
        f"Спецификации (A2):\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}"
        f"\n\nAPI Контракт (A5):\n{json.dumps(safe_contract(state), ensure_ascii=False, indent=2)}"
        f"\n\nТест-план (A7):\n{json.dumps(test_plan, ensure_ascii=False, indent=2)}"
        f"\n\nКод проекта:\n{all_code}"
    )

    prev_test_code: dict[str, str] = {}  # filename → code (для feedback-а)
    prev_error: str = ""
    last_stderr: str = ""
    last_stdout: str = ""

    for test_attempt in range(MAX_TEST_ATTEMPTS):
        tg_model = get_model("test_generator", test_attempt, randomize)
        logger.info(
            f"🧪 [{tg_model}] Генерация тестов "
            f"(попытка {test_attempt + 1}/{MAX_TEST_ATTEMPTS}) ..."
        )

        # Формируем контекст: базовый + feedback от предыдущей попытки
        gen_context = base_context
        if prev_test_code and prev_error:
            prev_tests_str = "\n\n".join(
                f"=== {fname} ===\n{code}" for fname, code in prev_test_code.items()
            )
            gen_context += (
                f"\n\n⚠️ ПРЕДЫДУЩИЕ ТЕСТЫ УПАЛИ. Исправь ТОЧЕЧНО — НЕ переписывай с нуля.\n"
                f"\nПРЕДЫДУЩИЙ КОД ТЕСТОВ:\n{prev_tests_str}"
                f"\n\nОШИБКА:\n{prev_error[-TRUNCATE_LOG:]}"
                f"\n\nИСПРАВЬ ТОЛЬКО упавшие тесты. Сохрани работающие."
            )

        try:
            test_resp = await ask_agent(
                logger, "test_generator", gen_context,
                cache, test_attempt, randomize, language,
            )
            test_files = test_resp.get("test_files", [])
            stats.record("test_generator", tg_model, True)
        except (LLMError, ValueError) as e:
            logger.warning(f"⚠️  Не удалось сгенерировать тесты: {e}.")
            stats.record("test_generator", tg_model, False)
            if test_attempt == MAX_TEST_ATTEMPTS - 1:
                return True  # Исчерпали попытки генерации → пропускаем тесты
            continue

        if not test_files:
            return True

        tests_dir = src_path / "tests"
        tests_dir.mkdir(exist_ok=True)
        if language == "python":
            (tests_dir / "__init__.py").write_text("", encoding="utf-8")

        # Сохраняем тесты и запоминаем код для feedback-а
        current_test_code: dict[str, str] = {}
        for tf in test_files:
            if code := _sanitize_llm_code(tf.get("code", "")):
                fname = tf.get("filename", f"test_generated.{LANG_EXT.get(language, 'py')}")
                # Защита от path traversal (../../malicious.py)
                resolved = (tests_dir / fname).resolve()
                if not resolved.is_relative_to(tests_dir.resolve()):
                    logger.warning(f"⚠️  Небезопасное имя теста: {fname} — пропускаю")
                    continue
                resolved.write_text(code, encoding="utf-8")
                current_test_code[fname] = code

        logger.info("🚀 Запуск тестов в Docker ...")
        cmd = get_test_command(language)
        rc, stdout, stderr = run_in_docker(src_path, cmd, RUN_TIMEOUT * 2, language)
        last_stderr = stderr
        last_stdout = stdout

        # Логи покрытия — в .factory/logs/
        logs_dir = project_path / FACTORY_DIR / LOGS_DIR
        (logs_dir / "coverage.log").write_text(
            f"ATTEMPT {test_attempt + 1}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}",
            encoding="utf-8",
        )

        if rc == 0:
            # Тесты прошли — проверяем покрытие
            m = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", stdout)
            coverage = int(m.group(1)) if m else 100

            if coverage < MIN_COVERAGE:
                logger.warning(f"❌ Покрытие {coverage}% < {MIN_COVERAGE}%")
                entry = state.get("entry_point", "main.py")
                state["feedbacks"][entry] = (
                    f"Покрытие {coverage}% < порога {MIN_COVERAGE}%. "
                    "Добавь публичные функции с понятными сигнатурами."
                )
                if entry in state.get("approved_files", []):
                    state["approved_files"].remove(entry)
                cum = state.setdefault("cumulative_file_attempts", {})
                cum[entry] = cum.get(entry, 0) + 3
                return False

            logger.info(f"✅ Тесты пройдены! Покрытие: {coverage}%")
            return True

        # ── Тесты упали ──
        logger.warning(
            f"❌ Тесты провалены (попытка {test_attempt + 1}/{MAX_TEST_ATTEMPTS})"
        )

        # Ошибка окружения Docker — не вина кода и не вина тестов
        if language == "python" and any(kw in stderr for kw in [
            "cannot open shared object file",
            "ImportError: lib",
            "pip subprocess to install build dependencies",
            "Failed building wheel",
            "No matching distribution found",
        ]):
            logger.warning("  ⚠️  Ошибка окружения Docker, не кода. Файлы не сбрасываем.")
            state["feedbacks"][state.get("entry_point", "main.py")] = (
                f"ОШИБКА ОКРУЖЕНИЯ DOCKER (не кода):\n{stderr[-TRUNCATE_LOG // 2:]}"
            )
            return False

        # Классифицируем: ошибка теста или ошибка приложения?
        classification, failing_app_file = _classify_test_error(
            stderr, stdout, state["files"]
        )

        if classification == "app_bug" and failing_app_file:
            # Ошибка в коде приложения → де-аппрувим файл, возвращаем в develop
            logger.warning(
                f"  🐛 Ошибка в коде приложения ({failing_app_file}), не в тестах."
            )
            state["feedbacks"][failing_app_file] = (
                f"UNIT-ТЕСТЫ ОБНАРУЖИЛИ БАГ В КОДЕ:\n{stderr[-TRUNCATE_LOG:]}"
                f"\n\nВывод:\n{stdout[-TRUNCATE_LOG // 2:]}"
            )
            if failing_app_file in state.get("approved_files", []):
                state["approved_files"].remove(failing_app_file)
            cum = state.setdefault("cumulative_file_attempts", {})
            cum[failing_app_file] = cum.get(failing_app_file, 0) + 3
            return False

        # classification == "test_bug" → ошибка в самих тестах → повтор генерации
        logger.info(
            f"  🔧 Ошибка в тестах (не в приложении) → повтор генерации "
            f"({test_attempt + 1}/{MAX_TEST_ATTEMPTS})"
        )
        prev_test_code = current_test_code
        prev_error = f"STDERR:\n{stderr[-1500:]}\nSTDOUT:\n{stdout[-500:]}"
        # Продолжаем цикл

    # Исчерпали все попытки генерации тестов
    logger.warning(
        f"⚠️  Тесты не прошли за {MAX_TEST_ATTEMPTS} попыток генерации. "
        "Де-аппрувим по _find_failing_file."
    )
    failing_file = find_failing_file(last_stderr, last_stdout, state["files"])
    state["feedbacks"][failing_file] = (
        f"UNIT-ТЕСТЫ НЕ ПРОЙДЕНЫ ПОСЛЕ {MAX_TEST_ATTEMPTS} ПОПЫТОК ГЕНЕРАЦИИ:\n"
        f"{last_stderr[-TRUNCATE_LOG:]}\n\nВывод:\n{last_stdout[-TRUNCATE_LOG // 2:]}"
    )
    if failing_file in state.get("approved_files", []):
        state["approved_files"].remove(failing_file)
    cum = state.setdefault("cumulative_file_attempts", {})
    cum[failing_file] = cum.get(failing_file, 0) + 3
    return False


async def phase_document(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    randomize: bool = False,
) -> None:
    logger.info("📝 Генерация README.md (A10) ...")
    language = state.get("language", "python")
    try:
        resp = await ask_agent(
            logger, "documenter",
            (
                f"Задача: {state['task']}\n"
                f"Бизнес-требования (A1): {json.dumps(state.get('business_requirements', {}), ensure_ascii=False)}\n"
                f"Архитектура: {state['architecture']}\n"
                f"Язык: {LANG_DISPLAY.get(language, language)}"
            ),
            cache, 0, randomize, language,
        )
        readme_text = resp.get("readme", "").strip()
        # README.md — в корне src/ (виден пользователю)
        (project_path / SRC_DIR / "README.md").write_text(readme_text, encoding="utf-8")
        # Также сохраняем как артефакт A10
        save_artifact(project_path, "A10", readme_text)
        logger.info("✅ README.md сгенерирован (A10 сохранён).")
    except (LLMError, ValueError) as e:
        logger.warning(f"⚠️  Documenter не справился: {e}")


async def revise_spec(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    problem: str,
    randomize: bool = False,
    stats: Optional[ModelStats] = None,
) -> None:
    """
    v15.0: Каскадный пересмотр спецификации.
    A2 обновляется → автоматически пересчитывается A5 →
    сбрасываются только файлы, затронутые изменённым контрактом.
    """
    # Ограничение: не более 3 пересмотров спецификации за проект
    # (было 10, но приводило к scope creep — supervisor/e2e/develop
    # вызывали revise_spec напрямую, раздувая спецификацию)
    spec_count = len(state.get("spec_history", []))
    if spec_count >= MAX_SPEC_REVISIONS:
        logger.warning(
            f"⚠️  Лимит пересмотров спецификации ({MAX_SPEC_REVISIONS}) исчерпан. "
            "Продолжаем с текущей спецификацией."
        )
        # Сбрасываем только revise_spec счётчик (другие фазы сохраняют свою информацию)
        state.setdefault("phase_fail_counts", {}).pop("revise_spec", None)
        return

    logger.info("\n🔁 Пересмотр спецификации (каскад A2 → A5) ...")
    language = state.get("language", "python")
    ctx = (
        f"Запрос заказчика:\n{state['task']}\n\n"
        f"Текущая спецификация (A2):\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
        f"Проблема:\n{problem}"
    )
    try:
        new_specs      = await ask_agent(logger, "spec_reviewer", ctx, cache, 0, randomize, language)
        change_summary = new_specs.get("change_summary", "нет описания")
        # Извлекаем только ожидаемые ключи спецификации
        state["system_specs"] = {
            "data_models":     new_specs.get("data_models", state.get("system_specs", {}).get("data_models", [])),
            "components":      new_specs.get("components", state.get("system_specs", {}).get("components", [])),
            "business_rules":  new_specs.get("business_rules", state.get("system_specs", {}).get("business_rules", [])),
            "external_systems": new_specs.get("external_systems", state.get("system_specs", {}).get("external_systems", [])),
        }

        # Сохраняем обновлённый A2
        save_artifact(project_path, "A2", state["system_specs"])

        # Каскад: пересчитываем A5
        _stats = stats or ModelStats(project_path)
        await refresh_api_contract(logger, project_path, state, cache,
                                    _stats, randomize)

        # Ревью обновлённого A5
        a5_ok = await phase_review_api_contract(
            logger, project_path, state, cache, _stats,
            state.get("api_contract", {}),
            {"architecture": state.get("architecture", ""), "files": state.get("files", [])},
            state.get("system_specs", {}),
            randomize,
        )
        if not a5_ok:
            logger.warning("⚠️  Обновлённый A5 не прошёл ревью. Продолжаем с текущим.")

        # Определяем, какие файлы затронуты новым контрактом
        new_contracts     = safe_contract(state).get("file_contracts", {})
        previously_approved = list(state.get("approved_files", []))
        affected_files = []
        for fname in previously_approved:
            # Если контракт файла изменился — сбрасываем его
            old_contract = state.get("_prev_file_contracts", {}).get(fname)
            new_contract = new_contracts.get(fname)
            if old_contract != new_contract:
                affected_files.append(fname)

        # Если нет информации о предыдущем контракте — сбрасываем всё (безопасно)
        if not state.get("_prev_file_contracts"):
            affected_files = previously_approved

        for fname in affected_files:
            if fname in state.get("approved_files", []):
                state["approved_files"].remove(fname)
            state["feedbacks"][fname] = "Спецификация обновлена, требуется переписать файл."
            state["file_attempts"][fname] = 0

        # Сброс file_attempts для ВСЕХ файлов проекта (не только affected)
        # Иначе файлы, которые были exhausted до revise_spec, останутся на MAX попыток
        for fname in state.get("files", []):
            state["file_attempts"][fname] = 0

        # Сброс E2E reset-счётчика: спека изменилась → E2E проблемы могут быть другими
        state["e2e_cumulative_resets"] = {}

        # Запоминаем текущий контракт для следующего сравнения
        state["_prev_file_contracts"] = new_contracts

        state["env_fixes"]          = {}
        state["phase_fail_counts"]  = {}
        # Не сбрасываем *_passed для фаз, уже превысивших порог safety-valve
        # (иначе бесполезный цикл: сброс → safety-valve → approve → повтор)
        pt = state.get("phase_total_fails", {})
        if pt.get("e2e_review", 0) < 6:
            state["e2e_passed"] = False
        if pt.get("integration_test", 0) < 8:
            state["integration_passed"] = False
        if pt.get("unit_tests", 0) < 6:
            state["tests_passed"] = False
        state["document_generated"] = False

        logger.info(f"✅ Спецификация обновлена (A2): {change_summary}")
        if affected_files:
            logger.info(f"ℹ️  Сброшены затронутые файлы: {', '.join(affected_files)}")
        unchanged = [f for f in previously_approved if f not in affected_files]
        if unchanged:
            logger.info(f"✅ Незатронутые файлы сохранены: {', '.join(unchanged)}")

        state.setdefault("spec_history", []).append({
            "iteration":      state["iteration"],
            "problem":        problem,
            "change":         change_summary,
            "reset_files":    affected_files,
            "kept_files":     unchanged,
        })

        # Обновляем ARCHITECTURE.md (в корне — видно в Git)
        arch_path = project_path / "ARCHITECTURE.md"
        arch_md   = arch_path.read_text(encoding="utf-8") if arch_path.exists() else ""
        arch_md  += (
            f"\n\n## Обновление спецификации (итерация {state['iteration']})\n"
            f"**Причина:** {problem}\n**Изменение:** {change_summary}\n"
            f"**Сброшены файлы:** {', '.join(affected_files) or 'нет'}\n\n"
            f"```json\n{json.dumps(state['system_specs'], ensure_ascii=False, indent=2)}\n```"
        )
        arch_path.write_text(arch_md, encoding="utf-8")

    except (LLMError, ValueError) as e:
        logger.warning(f"⚠️  Не удалось обновить спецификацию: {e}")

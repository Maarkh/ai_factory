import ast
import difflib
import re
from pathlib import Path


def sanitize_llm_code(code: str) -> str:
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
        r"^\s*(?:imports_from_project|external_dependencies|called_by)\s*=\s*\[.*?\]\s*$",
        "", code, flags=re.MULTILINE,
    )
    return code.strip()


def check_truncated_code(code: str) -> str:
    """Проверяет код на признаки усечения (LLM исчерпал max_tokens).

    Возвращает сообщение об ошибке или пустую строку если всё ок.
    """
    if not code or not code.strip():
        return ""
    lines = code.rstrip().splitlines()
    if not lines:
        return ""
    # Признак 1: последняя строка — незакрытый комментарий-заглушка (# ...)
    last = lines[-1].strip()
    if last in ("# ...", "# …", "...", "…"):
        return (
            "Код обрезан — последняя строка '# ...' указывает на незавершённый код. "
            "Сократи реализацию или разбей на части."
        )
    # Признак 2: SyntaxError на последних строках — вероятно обрезка
    try:
        ast.parse(code)
    except SyntaxError as e:
        if e.lineno and len(lines) > 3 and e.lineno >= len(lines) - 2:
            return (
                f"Код обрезан на строке {e.lineno}: {e.msg}. "
                f"Вероятно исчерпан лимит токенов. Сократи реализацию."
            )
    return ""


def apply_search_replace(code: str, changes: list[dict]) -> str | None:
    """Применяет search/replace патчи к коду.

    Каждый элемент changes: {"search": "...", "replace": "..."}.
    Возвращает пропатченный код или None если хотя бы один search не найден.
    """
    if not changes:
        return None
    for change in changes:
        if not isinstance(change, dict):
            return None
        search = change.get("search", "")
        replace = change.get("replace", "")
        if not isinstance(search, str) or not search.strip():
            return None
        if not isinstance(replace, str):
            return None
        # Точный поиск
        if search in code:
            code = code.replace(search, replace, 1)
            continue
        # Нормализация пробелов: strip каждой строки search и ищем по нормализованным строкам
        search_lines = [ln.rstrip() for ln in search.splitlines()]
        code_lines = code.splitlines()
        found = False
        for i in range(len(code_lines) - len(search_lines) + 1):
            if all(
                code_lines[i + j].rstrip() == search_lines[j]
                for j in range(len(search_lines))
            ):
                replace_lines = replace.splitlines() if replace else [""]
                code_lines[i:i + len(search_lines)] = replace_lines
                code = "\n".join(code_lines)
                found = True
                break
        if not found:
            # Нормализация внутренних пробелов (multiple → single, сохраняя leading whitespace)
            def _norm_inner(s: str) -> str:
                stripped = s.lstrip()
                leading = s[:len(s) - len(stripped)]
                return leading + re.sub(r" {2,}", " ", stripped)

            norm_search = [_norm_inner(ln.rstrip()) for ln in search.splitlines()]
            for i in range(len(code_lines) - len(norm_search) + 1):
                if all(
                    _norm_inner(code_lines[i + j].rstrip()) == norm_search[j]
                    for j in range(len(norm_search))
                ):
                    replace_lines = replace.splitlines() if replace else [""]
                    code_lines[i:i + len(norm_search)] = replace_lines
                    code = "\n".join(code_lines)
                    found = True
                    break
            # Fuzzy fallback: ищем блок с наибольшим сходством (>= 0.7)
            if not found and len(search_lines) >= 1:
                search_text = "\n".join(search_lines)
                best_ratio, best_i = 0.0, -1
                window = len(search_lines)
                for i in range(len(code_lines) - window + 1):
                    candidate = "\n".join(code_lines[i:i + window])
                    ratio = difflib.SequenceMatcher(None, search_text, candidate).ratio()
                    if ratio > best_ratio:
                        best_ratio, best_i = ratio, i
                if best_ratio >= 0.7 and best_i >= 0:
                    replace_lines = replace.splitlines() if replace else [""]
                    code_lines[best_i:best_i + window] = replace_lines
                    code = "\n".join(code_lines)
                    found = True
            if not found:
                return None
    return code


def ensure_a5_imports(code: str, global_imports: list[str]) -> str:
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
                        # Ищем конкретную строку в коде, которая нормализуется в ex
                        lines = code.split("\n")
                        for li, line in enumerate(lines):
                            if re.sub(r"\s+", " ", line.strip()) == ex:
                                lines[li] = new_line
                                break
                        code = "\n".join(lines)
                        existing_imports.discard(ex)
                        existing_imports.add(re.sub(r"\s+", " ", new_line))
                    break
            if not found_source:
                missing.append(normalized)
        else:
            # "import X as Y" — проверяем по полному совпадению (включая alias)
            m2 = re.match(r"import\s+(\S+)(?:\s+as\s+(\w+))?", normalized)
            if m2:
                module = m2.group(1)
                alias = m2.group(2)
                # Проверяем: есть ли уже точно такой же import (с тем же alias)?
                already = any(
                    re.match(rf"import\s+{re.escape(module)}\s+as\s+{re.escape(alias)}\b", ex)
                    for ex in existing_imports
                ) if alias else any(
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


def strip_non_a5_cross_imports(
    code: str,
    global_imports: list[str],
    project_files: list[str],
    global_context: str = "",
) -> str:
    """Удаляет из кода cross-file project imports несуществующих имён.

    Оставляет импорт если:
      1) имя есть в A5 global_imports, ИЛИ
      2) имя реально существует в public API целевого файла (global_context).
    Удаляет только импорты имён, которых нигде нет (LLM выдумал).
    Не трогает stdlib, pip-пакеты — только import из файлов проекта.
    """
    if not project_files or not code.strip():
        return code

    project_stems = {Path(f).stem for f in project_files}

    # Нормализованные A5 imports: stem → set(imported names)
    a5_sources: dict[str, set[str]] = {}
    a5_bare: set[str] = set()  # import module (без from)
    for imp in (global_imports or []):
        if not isinstance(imp, str):
            continue
        m = re.match(r"from\s+([\w.]+)\s+import\s+(.+)", imp.strip())
        if m:
            stem = m.group(1).split(".")[0]
            if stem in project_stems:
                names = {n.strip().split()[0] for n in m.group(2).split(",") if n.strip()}
                a5_sources.setdefault(stem, set()).update(names)
        else:
            m2 = re.match(r"import\s+([\w.]+)", imp.strip())
            if m2 and m2.group(1).split(".")[0] in project_stems:
                a5_bare.add(m2.group(1).split(".")[0])

    # Реально существующие имена из public API: stem → set(names)
    real_names: dict[str, set[str]] = {}
    if global_context:
        _cur_stem = ""
        for gc_line in global_context.splitlines():
            if gc_line.startswith("--- ") and gc_line.endswith(" PUBLIC API ---"):
                fname = gc_line.split("---")[1].strip().replace(" PUBLIC API", "").strip()
                _cur_stem = Path(fname).stem
            elif _cur_stem:
                gm = re.match(r"(?:class|def|async def)\s+(\w+)", gc_line.strip())
                if gm:
                    real_names.setdefault(_cur_stem, set()).add(gm.group(1))
                # Top-level assignments: NAME = ...
                am = re.match(r"(\w+)\s*=", gc_line.strip())
                if am and not gc_line.strip().startswith(("_", "#")):
                    real_names.setdefault(_cur_stem, set()).add(am.group(1))

    def _is_allowed(stem: str, name: str) -> bool:
        """Имя разрешено если есть в A5 ИЛИ реально существует в файле."""
        if stem in a5_sources and name in a5_sources[stem]:
            return True
        if stem in real_names and name in real_names[stem]:
            return True
        return False

    lines = code.split("\n")
    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()
        m = re.match(r"from\s+([\w.]+)\s+import\s+(.+)", stripped)
        if m:
            stem = m.group(1).split(".")[0]
            if stem in project_stems:
                names = [n.strip() for n in m.group(2).split(",") if n.strip()]
                allowed = [n for n in names if _is_allowed(stem, n.split()[0])]
                if not allowed:
                    continue  # Все имена — выдуманные
                if len(allowed) < len(names):
                    cleaned.append(f"from {m.group(1)} import {', '.join(allowed)}")
                    continue
        else:
            m2 = re.match(r"import\s+([\w.]+)", stripped)
            if m2:
                stem = m2.group(1).split(".")[0]
                if stem in project_stems and stem not in a5_bare and stem not in a5_sources and stem not in real_names:
                    continue
        cleaned.append(line)
    return "\n".join(cleaned)


def check_class_duplication(code: str, global_context: str, file_contract: list | None = None) -> list[str]:
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


def check_import_shadowing(code: str) -> list[str]:
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


def check_data_only_violations(
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


def check_stub_functions(code: str) -> list[str]:
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
            vals = getattr(val, "values", None) or []
            if not elts and not keys:
                return True  # [], {}, ()
            if isinstance(val, (ast.List, ast.Tuple)) and all(isinstance(e, ast.Constant) for e in elts):
                return True  # ['ABC123'], [0, 0, 0]
            if isinstance(val, ast.Dict) and keys and all(isinstance(k, ast.Constant) for k in keys) and all(isinstance(v, ast.Constant) for v in vals):
                return True  # {"plate": "ABC123", "confidence": 0.99}
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


def check_function_preservation(
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


def check_contract_compliance(code: str, file_contract: list) -> list[str]:
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
        if not isinstance(item, dict):
            continue
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


def classify_test_error(
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


def diagnose_runtime_error(
    stderr: str, stdout: str, project_files: list[str], src_path: Path,
) -> dict | None:
    """Детерминистская диагностика runtime-ошибок БЕЗ вызова LLM.

    Парсит traceback, определяет тип ошибки и генерирует конкретный фидбэк.
    Возвращает {"file": str, "fix": str, "missing_package": str} или None
    если ошибка не распознана (нужен LLM).
    """
    combined = stderr + "\n" + stdout

    # Извлекаем последнюю строку exception
    exc_match = re.search(
        r"^(\w+(?:\.\w+)*(?:Error|Exception|Warning)):\s*(.+)$",
        combined, re.MULTILINE,
    )
    if not exc_match:
        return None

    exc_type = exc_match.group(1)
    exc_msg = exc_match.group(2).strip()

    # Файл из traceback (последний файл проекта)
    from code_context import find_failing_file
    failing_file = find_failing_file(stderr, stdout, project_files)

    result: dict = {"file": failing_file, "fix": "", "missing_package": ""}

    # ── ModuleNotFoundError / ImportError (отсутствующий пакет) ──
    if exc_type in ("ModuleNotFoundError", "ImportError"):
        mod_match = re.search(r"No module named ['\"]?(\w+)", exc_msg)
        if mod_match:
            missing_mod = mod_match.group(1)
            # Маппинг import-имя → pip-пакет
            from code_context import PIP_TO_IMPORT
            import_to_pip = {v: k for k, v in PIP_TO_IMPORT.items()}
            pip_pkg = import_to_pip.get(missing_mod, missing_mod)
            result["missing_package"] = pip_pkg
            result["fix"] = (
                f"Отсутствует модуль '{missing_mod}'. "
                f"Добавь '{pip_pkg}' в requirements.txt."
            )
            return result

        # ImportError: cannot import name 'X' from 'Y'
        name_match = re.search(
            r"cannot import name ['\"](\w+)['\"] from ['\"](\w+)['\"]", exc_msg
        )
        if name_match:
            import_name = name_match.group(1)
            module_name = name_match.group(2)
            target_file = module_name + ".py"
            if target_file in project_files:
                # Проверяем что реально определено в целевом файле
                target_path = src_path / target_file
                available = ""
                if target_path.exists():
                    try:
                        from code_context import get_top_level_names
                        names = get_top_level_names(
                            target_path.read_text(encoding="utf-8")
                        )
                        available = ", ".join(sorted(names - {"__all__"})[:10])
                    except (OSError, UnicodeDecodeError):
                        pass
                result["file"] = failing_file
                result["fix"] = (
                    f"ImportError: '{import_name}' не определён в {target_file}. "
                    f"Доступные имена: {available or '(не удалось прочитать)'}. "
                    f"Исправь import или добавь '{import_name}' в {target_file}."
                )
                return result

    # ── NameError: name 'X' is not defined ──
    if exc_type == "NameError":
        name_match = re.search(r"name ['\"](\w+)['\"] is not defined", exc_msg)
        if name_match:
            undefined_name = name_match.group(1)
            result["fix"] = (
                f"NameError: '{undefined_name}' не определён. "
                f"Добавь import или определи '{undefined_name}' перед использованием."
            )
            return result

    # ── AttributeError: module/object has no attribute 'X' ──
    if exc_type == "AttributeError":
        attr_match = re.search(
            r"(?:module |type object )?['\"]?(\w+)['\"]? has no attribute ['\"](\w+)['\"]",
            exc_msg,
        )
        if attr_match:
            obj_name = attr_match.group(1)
            attr_name = attr_match.group(2)
            # Если obj — файл проекта
            target_file = obj_name + ".py"
            if target_file in project_files:
                result["fix"] = (
                    f"AttributeError: модуль '{obj_name}' не имеет атрибута '{attr_name}'. "
                    f"Добавь '{attr_name}' в {target_file} или исправь имя."
                )
            else:
                result["fix"] = (
                    f"AttributeError: '{obj_name}' не имеет атрибута '{attr_name}'. "
                    f"Проверь имя метода/атрибута и совместимость API."
                )
            return result

    # ── TypeError: missing required argument / got unexpected keyword ──
    if exc_type == "TypeError":
        if "missing" in exc_msg and "argument" in exc_msg:
            result["fix"] = (
                f"TypeError: {exc_msg}. "
                f"Проверь сигнатуру вызываемой функции и передай все обязательные аргументы."
            )
            return result
        if "unexpected keyword argument" in exc_msg:
            result["fix"] = (
                f"TypeError: {exc_msg}. "
                f"Убери лишний именованный аргумент или обнови сигнатуру функции."
            )
            return result

    # ── SyntaxError ──
    if exc_type == "SyntaxError":
        result["fix"] = (
            f"SyntaxError: {exc_msg}. "
            f"Проверь синтаксис Python в {failing_file} — скобки, двоеточия, отступы."
        )
        return result

    return None


def check_runtime_imports(
    src_path: Path,
    project_files: list[str],
) -> dict[str, str]:
    """Лёгкая runtime-проверка: пытается импортировать каждый файл проекта.

    Запускает `python -c "import module"` в subprocess для каждого файла.
    Ловит ImportError, NameError, AttributeError без Docker.

    Возвращает {filename: error_message} для файлов с ошибками. Пустой dict = OK.
    """
    import subprocess

    issues: dict[str, str] = {}
    project_stems = {Path(f).stem for f in project_files}
    # Добавляем package dirs
    for f in project_files:
        parts = Path(f).parts
        if len(parts) > 1:
            project_stems.add(parts[0])

    for fname in project_files:
        if not fname.endswith(".py"):
            continue
        stem = Path(fname).stem
        if "/" in fname:
            stem = fname.replace("/", ".").removesuffix(".py")
        try:
            result = subprocess.run(
                ["python", "-c", f"import {stem}"],
                capture_output=True, text=True, timeout=10,
                cwd=str(src_path),
            )
            if result.returncode != 0:
                stderr = result.stderr.strip()
                last_line = stderr.splitlines()[-1] if stderr else "Unknown error"
                # Пропускаем ModuleNotFoundError для внешних пакетов (cv2, torch)
                if "ModuleNotFoundError" in last_line:
                    m = re.search(r"No module named '([\w.]+)'", last_line)
                    if m:
                        import_name = m.group(1).split(".")[0]
                        if import_name not in project_stems:
                            continue  # Внешний пакет — не баг кода
                issues[fname] = last_line
        except (subprocess.TimeoutExpired, Exception):
            continue

    return issues

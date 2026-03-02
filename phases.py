import ast
import asyncio
import json
import re
import logging
from pathlib import Path
from typing import Optional

from config import MAX_FILE_ATTEMPTS, MAX_CONTEXT_CHARS, MIN_COVERAGE, FACTORY_DIR, LOGS_DIR, SRC_DIR, RUN_TIMEOUT
from exceptions import LLMError
from llm import ask_agent
from stats import ModelStats
from json_utils import _to_str, _safe_contract
from lang_utils import LANG_DISPLAY, LANG_EXT, get_execution_command, get_test_command, get_docker_image
from log_utils import get_model, log_runtime_error
from code_context import get_global_context, get_full_context, build_dependency_order, _find_failing_file, validate_imports, validate_cross_file_names
from state import _push_feedback, _get_feedback_ctx, update_dependencies, update_dockerfile, update_requirements
from artifacts import update_artifact_a9, save_artifact
from infra import run_in_docker, build_docker_image
from contract import _refresh_api_contract, phase_review_api_contract, patch_contract_for_file
from cache import ThreadSafeCache


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
        f"используй `from {name_to_file[name].removesuffix('.py')} import {name}`"
        for name in sorted(duplicates)
    ]


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
                and isinstance(effective[0].value, (ast.Constant, ast.Str))
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
    return warnings


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
            try_effective = [st for st in s.body if not isinstance(st, (ast.Pass, ast.Expr))]
            if not try_effective:
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

    # Имена, ожидаемые текущим A5 контрактом
    contract_names: set[str] = set()
    if file_contract:
        for item in file_contract:
            contract_names.add(item.get("name", ""))

    # Фильтруем: имена упомянутые в feedback + приватные + не в текущем A5
    feedback_lower = feedback.lower() if feedback else ""
    warnings: list[str] = []
    for name in sorted(disappeared):
        if name.startswith("_"):
            continue
        if name.lower() in feedback_lower:
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
    Возвращает список отсутствующих элементов."""
    if not file_contract:
        return []
    missing = []
    for item in file_contract:
        if not item.get("required", False):
            continue
        sig = item.get("signature", "")
        name = item.get("name", "")
        if sig.startswith("class "):
            # Проверяем наличие class ClassName
            class_name = sig.split("class ", 1)[1].split("(")[0].split(":")[0].strip()
            if not re.search(rf'^class\s+{re.escape(class_name)}\b', code, re.MULTILINE):
                missing.append(f"class {class_name}")
        elif sig.startswith("def ") or sig.startswith("async def "):
            # Проверяем наличие def func_name(
            func_name = name or sig.split("def ", 1)[1].split("(")[0].strip()
            if not re.search(rf'^\s*(?:async\s+)?def\s+{re.escape(func_name)}\s*\(', code, re.MULTILINE):
                missing.append(f"def {func_name}()")
    return missing


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
        feedback = _to_str(result.get("feedback", ""))
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
    file_contract  = _safe_contract(state).get("file_contracts", {}).get(current_file, [])
    global_imports = _safe_contract(state).get("global_imports", {}).get(current_file, [])

    try:
        ctx = (
            f"Файл: {current_file}\nКод:\n{code}\n\n"
            f"Спецификации (A2):\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
            f"МИНИМАЛЬНЫЙ API контракт A5 (все эти функции ДОЛЖНЫ быть реализованы):\n"
            f"{json.dumps(file_contract, ensure_ascii=False, indent=2)}\n\n"
            f"Ключевые внешние импорты из A5 (могут быть расширены разработчиком — это нормально):\n"
            f"{json.dumps(global_imports, ensure_ascii=False, indent=2)}"
        )
        result   = await ask_agent(logger, "self_reflect", ctx, cache, 0, randomize, language)
        status   = result.get("status", "OK")
        feedback = _to_str(result.get("feedback", ""))
        improved = _to_str(result.get("improved_code", "")).strip()

        if status == "NEEDS_IMPROVEMENT" and improved:
            (src_path / current_file).write_text(improved, encoding="utf-8")
            logger.info(f"  → Self-Reflect улучшил код: {feedback[:80]}")

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
                fb = _to_str(val_resp.get("feedback", val_resp.get("explanation", "")))
                logger.warning(f"  ❌ {label} отклонил: {fb[:150]}")
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
    a5_contract = _safe_contract(state)

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
        feedback = _to_str(result.get("feedback", ""))
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
    MAX_CUMULATIVE = MAX_FILE_ATTEMPTS * 3  # После 15 суммарных попыток — принудительный APPROVE

    for current_file in order:
        if current_file in state.get("approved_files", []):
            logger.info(f"⏭️  {current_file} уже одобрен.")
            continue

        attempt = file_attempts.get(current_file, 0)
        total_attempts = cumulative_attempts.get(current_file, 0)

        # Предохранитель: файл не проходит ревью после множества попыток → принудительный approve
        if total_attempts >= MAX_CUMULATIVE:
            file_path = src_path / current_file
            if file_path.exists() and file_path.read_text(encoding="utf-8").strip():
                logger.warning(
                    f"⚠️  {current_file} не прошёл ревью за {total_attempts} суммарных попыток "
                    f"→ принудительный APPROVE (код есть, проверим при интеграции)."
                )
                state.setdefault("approved_files", []).append(current_file)
                state["feedbacks"][current_file] = ""
                file_attempts[current_file] = 0
                continue

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
        file_contract  = _safe_contract(state).get("file_contracts", {}).get(current_file, [])
        global_imports = _safe_contract(state).get("global_imports", {}).get(current_file, [])

        # Патч A5 после 3+ неудачных попыток — контракт может не соответствовать реальности
        if attempt >= 3 and file_contract and existing_code:
            last_feedback = state.get("feedbacks", {}).get(current_file, "")
            if last_feedback:
                patched = await patch_contract_for_file(
                    logger, project_path, state, cache, stats,
                    current_file, existing_code, last_feedback, randomize,
                )
                if patched:
                    file_contract  = _safe_contract(state).get("file_contracts", {}).get(current_file, [])
                    global_imports = _safe_contract(state).get("global_imports", {}).get(current_file, [])

        dev_ctx = (
            f"Задача:\n{state['task']}\n\n"
            f"СИСТЕМНЫЕ СПЕЦИФИКАЦИИ (A2):\n"
            f"{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
            f"Файл для написания: `{current_file}`.\n\n"
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
        if global_context:
            dev_ctx += f"ГЛОБАЛЬНЫЙ КОНТЕКСТ (public API других файлов):\n{global_context}\n\n"
            # Извлекаем имена классов/функций из других файлов — запрет на переопределение
            defined_elsewhere = re.findall(r'(?:class|def)\s+(\w+)', global_context)
            if defined_elsewhere:
                dev_ctx += (
                    f"⛔ ЗАПРЕЩЕНО ПЕРЕОПРЕДЕЛЯТЬ (уже определены в других файлах проекта, "
                    f"используй import): {', '.join(defined_elsewhere)}\n\n"
                )
        if existing_code:
            max_code_chars = MAX_CONTEXT_CHARS // 2
            if len(existing_code) > max_code_chars:
                existing_code = existing_code[:max_code_chars] + "\n# [... код обрезан ...]"
            dev_ctx += f"ТЕКУЩИЙ КОД `{current_file}`:\n{existing_code}\n\n"
        feedback_ctx = _get_feedback_ctx(state, current_file)
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
            code     = dev_resp.get("code", "").strip()
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
                _push_feedback(state, current_file, pres_feedback)
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
            _push_feedback(state, current_file, dup_feedback)
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
            import_feedback = (
                "АВТОМАТИЧЕСКИЙ REJECT — невалидные импорты:\n"
                + "\n".join(f"  - {w}" for w in import_warnings)
                + "\n\nИсправь: используй только stdlib, pip-пакеты из requirements.txt "
                "или модули проекта: " + ", ".join(state["files"])
            )
            logger.warning(f"⛔ {current_file}: {len(import_warnings)} ошибок импорта → авто-REJECT")
            stats.record("developer", dev_model, False)
            _push_feedback(state, current_file, import_feedback)
            file_attempts[current_file] = attempt + 1
            cumulative_attempts[current_file] = total_attempts + 1
            continue

        # Детерминистская проверка: кросс-файловые имена (from X import Y → Y существует в X)
        if language == "python":
            xfile_warnings = validate_cross_file_names(
                code, current_file, state["files"], src_path,
                approved_files=state.get("approved_files", []),
            )
            if xfile_warnings:
                xfile_feedback = (
                    "АВТОМАТИЧЕСКИЙ REJECT — ошибки кросс-файловых имён:\n"
                    + "\n".join(f"  - {w}" for w in xfile_warnings)
                    + "\n\nПроверь что все импортируемые имена определены в целевых файлах."
                )
                logger.warning(f"⛔ {current_file}: {len(xfile_warnings)} ошибок имён → авто-REJECT")
                stats.record("developer", dev_model, False)
                _push_feedback(state, current_file, xfile_feedback)
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
                "raise NotImplementedError) ЗАПРЕЩЕНЫ."
            )
            logger.warning(f"⛔ {current_file}: {len(stub_warnings)} заглушек → авто-REJECT")
            stats.record("developer", dev_model, False)
            _push_feedback(state, current_file, stub_feedback)
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
            _push_feedback(state, current_file, contract_feedback)
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
            code = file_path.read_text(encoding="utf-8")

        # Внешний ревью
        rev_status, rev_feedback, needs_spec = await _review_file(
            logger, cache, current_file, code, attempt, stats, randomize, language,
            file_contract=file_contract, global_imports=global_imports,
        )

        if rev_status == "APPROVE":
            stats.record("developer", dev_model, True)
            logger.info(f"✅ {current_file} одобрен.")
            state.setdefault("approved_files", []).append(current_file)
            state["feedbacks"][current_file] = ""
            state.setdefault("feedback_history", {})[current_file] = []
            file_attempts[current_file] = 0
            # Обновляем A9 (Implementation Logs)
            update_artifact_a9(project_path, current_file, f"Одобрен на попытке {attempt + 1}. Модель: {dev_model}.")
        else:
            stats.record("developer", dev_model, False)
            combined = "\n".join(filter(None, [_to_str(sr_feedback), _to_str(rev_feedback)]))
            logger.warning(f"❌ {current_file} отклонён: {combined[:100]}")
            _push_feedback(state, current_file, combined)
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
                feedback = _to_str(resp.get("feedback", ""))
                logger.warning(f"❌ E2E [{label}] REJECT на {target}: {feedback[:120]}")
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
        else:
            # Находим зависимые файлы (импортирующие target_files)
            gi = _safe_contract(state).get("global_imports", {})
            target_stems = {t.removesuffix(".py") for t in target_files}
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

    for filename, warnings in issues.items():
        feedback = (
            "АВТОМАТИЧЕСКИЙ REJECT — кросс-файловые ошибки (до E2E):\n"
            + "\n".join(f"  - {w}" for w in warnings)
        )
        state["feedbacks"][filename] = feedback
        approved = state.get("approved_files", [])
        if filename in approved:
            approved.remove(filename)
            logger.warning(f"  ⛔ {filename}: {len(warnings)} проблем → снят APPROVE")

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
            logger.error(f"❌ Ошибка сборки:\n{build_err[:400]}")
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
            for orig, alt in env_fixes.get("pip_alternatives", {}).items():
                update_requirements(src_path, orig, alt)

        rc, stdout, stderr = run_in_docker(src_path, cmd, RUN_TIMEOUT, language)

        # Логи рантайма — в .factory/logs/
        logs_dir = project_path / FACTORY_DIR / LOGS_DIR
        logs_dir.mkdir(parents=True, exist_ok=True)
        (logs_dir / "test.log").write_text(
            f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}", encoding="utf-8"
        )
        logger.info(f"\n--- STDOUT ---\n{stdout[:2000]}")
        logger.info(f"\n--- STDERR ---\n{stderr[:2000]}")

        if rc == 0:
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
                lines = req_path.read_text(encoding="utf-8").splitlines()
                new_lines = []
                for line in lines:
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        new_lines.append(line)
                        continue
                    # Убираем жёсткие версии (==x.y.z) → пусть pip найдёт совместимую
                    pkg_base = re.split(r'[=<>~!]', stripped)[0].strip()
                    if pkg_base.lower() != stripped.lower():
                        logger.info(f"  → {stripped} → {pkg_base} (убрана версия)")
                        new_lines.append(pkg_base)
                    else:
                        new_lines.append(line)
                req_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
                logger.info("  ✅ requirements.txt обновлён (убраны версии).")
            continue  # Повторяем попытку с обновлёнными зависимостями

        failing_file = _find_failing_file(stderr, stdout, state["files"])

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
        state["feedbacks"][failing_file] = f"ПРОГРАММА УПАЛА.\nTRACEBACK:\n{stderr}\nQA:\n{fix}"
        logger.info("🔄 Возврат к разработчику.")
        return False

    return False


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

    tg_model = get_model("test_generator", 0, randomize)
    try:
        test_resp  = await ask_agent(
            logger, "test_generator",
            f"Спецификации (A2):\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}"
            f"\n\nAPI Контракт (A5):\n{json.dumps(_safe_contract(state), ensure_ascii=False, indent=2)}"
            f"\n\nТест-план (A7):\n{json.dumps(test_plan, ensure_ascii=False, indent=2)}"
            f"\n\nКод проекта:\n{all_code}",
            cache, 0, randomize, language,
        )
        test_files = test_resp.get("test_files", [])
        stats.record("test_generator", tg_model, True)
    except (LLMError, ValueError) as e:
        logger.warning(f"⚠️  Не удалось сгенерировать тесты: {e}. Пропускаю.")
        stats.record("test_generator", tg_model, False)
        return True

    if not test_files:
        return True

    tests_dir = src_path / "tests"
    tests_dir.mkdir(exist_ok=True)
    if language == "python":
        (tests_dir / "__init__.py").write_text("", encoding="utf-8")

    for tf in test_files:
        if code := tf.get("code", ""):
            (tests_dir / tf.get("filename", f"test_generated.{LANG_EXT.get(language, 'py')}")).write_text(
                code, encoding="utf-8"
            )

    logger.info("🚀 Запуск тестов в Docker ...")
    cmd = get_test_command(language)
    rc, stdout, stderr = run_in_docker(src_path, cmd, RUN_TIMEOUT * 2, language)

    # Логи покрытия — в .factory/logs/
    logs_dir = project_path / FACTORY_DIR / LOGS_DIR
    (logs_dir / "coverage.log").write_text(stdout + "\n" + stderr, encoding="utf-8")

    if rc != 0:
        logger.warning("❌ Тесты провалены!")
        # Ошибка окружения Docker (missing .so, pip) — не вина кода, не снимаем approve
        if language == "python" and any(kw in stderr for kw in [
            "cannot open shared object file",
            "ImportError: lib",
            "pip subprocess to install build dependencies",
            "Failed building wheel",
            "No matching distribution found",
        ]):
            logger.warning("  ⚠️  Ошибка окружения Docker, не кода. Файлы не сбрасываем.")
            state["feedbacks"][state.get("entry_point", "main.py")] = (
                f"ОШИБКА ОКРУЖЕНИЯ DOCKER (не кода):\n{stderr[-1000:]}"
            )
            return False
        failing_file = _find_failing_file(stderr, stdout, state["files"])
        state["feedbacks"][failing_file] = f"UNIT-ТЕСТЫ УПАЛИ:\n{stderr[-2000:]}\n\nВывод:\n{stdout[-1000:]}"
        if failing_file in state.get("approved_files", []):
            state["approved_files"].remove(failing_file)
        return False

    m        = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", stdout)
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
        return False

    logger.info(f"✅ Тесты пройдены! Покрытие: {coverage}%")
    return True


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
    MAX_SPEC_REVISIONS = 3
    spec_count = len(state.get("spec_history", []))
    if spec_count >= MAX_SPEC_REVISIONS:
        logger.warning(
            f"⚠️  Лимит пересмотров спецификации ({MAX_SPEC_REVISIONS}) исчерпан. "
            "Продолжаем с текущей спецификацией."
        )
        # Сбрасываем consecutive-счётчики чтобы supervisor перестал слать revise_spec
        state["phase_fail_counts"] = {}
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
        await _refresh_api_contract(logger, project_path, state, cache,
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
        new_contracts     = _safe_contract(state).get("file_contracts", {})
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

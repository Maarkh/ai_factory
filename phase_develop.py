import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Optional

from config import (
    MAX_FILE_ATTEMPTS, MAX_CUMULATIVE, MAX_CONTEXT_CHARS, SRC_DIR,
    MAX_A5_PATCHES_PER_FILE, SELF_REFLECT_RETRIES, TRUNCATE_FEEDBACK,
)

from exceptions import LLMError
from llm import ask_agent
from stats import ModelStats
from json_utils import to_str, safe_contract
from lang_utils import LANG_DISPLAY
from log_utils import get_model
from code_context import (
    get_global_context, get_full_context, build_dependency_order,
    validate_imports, validate_cross_file_names, get_a5_deps,
)
from state import push_feedback, get_feedback_ctx
from artifacts import update_artifact_a9, save_artifact
from contract import patch_contract_for_file
from cache import ThreadSafeCache
from checks import (
    sanitize_llm_code, check_truncated_code, ensure_a5_imports,
    strip_non_a5_cross_imports, apply_search_replace,
    check_function_preservation, check_class_duplication,
    check_import_shadowing, check_data_only_violations,
    check_stub_functions, check_contract_compliance,
)
from experience import record_experience, search_experience, format_experience_context


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
        improved = sanitize_llm_code(to_str(result.get("improved_code", "")))

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

def _reject_file(
    state: dict,
    file_attempts: dict,
    cumulative_attempts: dict,
    current_file: str,
    attempt: int,
    total_attempts: int,
    feedback: str,
    stats: ModelStats,
    dev_model: str,
    logger: logging.Logger,
) -> None:
    """Записывает REJECT файла: статистика, feedback, инкремент счётчиков."""
    stats.record("developer", dev_model, False)
    push_feedback(state, current_file, feedback)
    file_attempts[current_file] = attempt + 1
    cumulative_attempts[current_file] = total_attempts + 1


def _run_checks(
    code: str,
    existing_code: str,
    current_file: str,
    state: dict,
    file_contract: list,
    global_context: str,
    global_imports: list,
    language: str,
    src_path: Path,
) -> tuple[str, str] | None:
    """Запускает 9 детерминистских проверок на код.

    Возвращает (check_name, feedback) при первом провале, или None если все проверки пройдены.
    """
    req_path = src_path / "requirements.txt"

    # 0. Синтаксическая валидность (ast.parse) — код с SyntaxError пройдёт ВСЕ
    # остальные проверки молча (они ловят SyntaxError и возвращают [])
    if language == "python":
        try:
            import ast as _ast
            _ast.parse(code)
        except SyntaxError as e:
            line_info = f" (строка {e.lineno})" if e.lineno else ""
            return "syntax", (
                f"АВТОМАТИЧЕСКИЙ REJECT — SyntaxError{line_info}: {e.msg}\n\n"
                f"Код содержит синтаксическую ошибку и не может быть выполнен.\n"
                f"Исправь синтаксис и верни ПОЛНЫЙ рабочий файл."
            )

    # 1. Потеря функций из предыдущей версии
    if existing_code:
        last_fb = state.get("feedbacks", {}).get(current_file, "")
        pres_warnings = check_function_preservation(code, existing_code, last_fb, file_contract)
        if pres_warnings:
            return "function_preservation", (
                "АВТОМАТИЧЕСКИЙ REJECT — потеря функций из предыдущей версии:\n"
                + "\n".join(f"  - {w}" for w in pres_warnings)
                + "\n\n⚠️ НЕ ПЕРЕПИСЫВАЙ файл с нуля. Исправь ТОЛЬКО то, что указано "
                "в фидбэке. Сохрани ВСЮ существующую структуру."
            )

    # 2. Дублирование классов из других файлов
    dup_warnings = check_class_duplication(code, global_context, file_contract)
    if dup_warnings:
        return "class_duplication", (
            "АВТОМАТИЧЕСКИЙ REJECT — дублирование классов из других файлов проекта:\n"
            + "\n".join(f"  - {w}" for w in dup_warnings)
            + "\n\nНЕ ОПРЕДЕЛЯЙ эти классы заново. Используй import."
        )

    # 3. Import shadowing (from X import Y + def Y)
    shadow_warnings = check_import_shadowing(code)
    if shadow_warnings:
        return "import_shadowing", (
            "АВТОМАТИЧЕСКИЙ REJECT — конфликт имён (import + определение):\n"
            + "\n".join(f"  - {w}" for w in shadow_warnings)
            + "\n\nЕсли имя импортировано из другого файла — НЕ определяй его заново."
        )

    # 4. Data-only файл не должен импортировать из проекта
    data_only_warnings = check_data_only_violations(code, current_file, state["files"])
    if data_only_warnings:
        return "data_only", (
            "АВТОМАТИЧЕСКИЙ REJECT — нарушение правил data-only файла:\n"
            + "\n".join(f"  - {w}" for w in data_only_warnings)
            + f"\n\n{current_file} — это файл для ХРАНЕНИЯ data structures.\n"
            "Он НЕ ДОЛЖЕН импортировать из других файлов проекта.\n"
            "Он НЕ ДОЛЖЕН содержать бизнес-логику (функции).\n"
            "Другие файлы импортируют ОТСЮДА, а не наоборот."
        )

    # 5. Валидность импортов (stdlib / pip / проект)
    import_warnings = validate_imports(
        code, current_file, state["files"],
        req_path if req_path.exists() else None, language, src_path,
    )
    if import_warnings:
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
        return "imports", (
            "АВТОМАТИЧЕСКИЙ REJECT — невалидные импорты:\n"
            + "\n".join(f"  - {w}" for w in import_warnings)
            + "\n\nИсправь: используй только stdlib, pip-пакеты из requirements.txt "
            "или модули проекта: " + ", ".join(state["files"])
            + expected_hint
            + req_content_hint
        )

    # 6. Кросс-файловые имена (from X import Y → Y существует в X)
    if language == "python":
        xfile_warnings = validate_cross_file_names(code, current_file, state["files"], src_path)
        if xfile_warnings:
            return "cross_file_names", (
                "АВТОМАТИЧЕСКИЙ REJECT — ошибки кросс-файловых имён:\n"
                + "\n".join(f"  - {w}" for w in xfile_warnings)
                + "\n\nПроверь что все импортируемые имена определены в целевых файлах."
            )

    # 7. Функции-заглушки (pass, ..., NotImplementedError)
    stub_warnings = check_stub_functions(code)
    if stub_warnings:
        return "stubs", (
            "АВТОМАТИЧЕСКИЙ REJECT — функции-заглушки:\n"
            + "\n".join(f"  - {w}" for w in stub_warnings)
            + "\n\nВесь код должен быть полностью рабочим. Заглушки (pass, ..., "
            "raise NotImplementedError) и фиктивные реализации "
            "(захардкоженные return без использования параметров) ЗАПРЕЩЕНЫ."
        )

    # 8. Все required функции/классы из A5 контракта присутствуют
    contract_missing = check_contract_compliance(code, file_contract)
    if contract_missing:
        return "contract_compliance", (
            "АВТОМАТИЧЕСКИЙ REJECT — отсутствуют required элементы из A5 контракта:\n"
            + "\n".join(f"  - {m}" for m in contract_missing)
            + "\n\nРеализуй ВСЕ функции/классы, указанные в API контракте A5."
        )

    return None


def _build_dev_context(
    state: dict,
    current_file: str,
    existing_code: str,
    file_contract: list,
    global_imports: list,
    global_context: str,
    src_path: Path,
) -> str:
    """Собирает контекст для агента-разработчика."""
    dev_ctx = (
        f"Задача:\n{state['task']}\n\n"
        f"СИСТЕМНЫЕ СПЕЦИФИКАЦИИ (A2):\n"
        f"{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
        f"Файл для написания: `{current_file}`.\n\n"
    )

    # Специальная инструкция для entry point
    if current_file == state.get("entry_point"):
        dev_ctx += (
            "⚠️ ЭТОТ ФАЙЛ — ТОЧКА ВХОДА ПРИЛОЖЕНИЯ.\n"
            "НЕ определяй здесь бизнес-классы — они в других файлах, ИМПОРТИРУЙ их.\n"
            "Содержимое: импорты + инициализация + запуск (идиоматичная точка входа для целевого языка).\n\n"
        )

    # Специальная инструкция для data-only файлов
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

    # A5 контракт
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

    # Список файлов проекта (для ясности, что можно импортировать)
    project_files = state.get("files", [])
    other_files = [f for f in project_files if f != current_file]
    if other_files:
        dev_ctx += (
            f"ФАЙЛЫ ПРОЕКТА (можно импортировать ТОЛЬКО из них):\n"
            + ", ".join(other_files) + "\n"
            "⛔ Импорт из несуществующих модулей проекта будет отклонён.\n\n"
        )

    # requirements.txt
    req_path = src_path / "requirements.txt"
    if req_path.exists():
        req_content = req_path.read_text(encoding="utf-8").strip()
        if req_content:
            dev_ctx += (
                f"ДОСТУПНЫЕ PIP-ПАКЕТЫ (requirements.txt):\n{req_content}\n"
                f"⛔ Импорт пакетов НЕ из этого списка будет отклонён.\n\n"
            )

    # Глобальный контекст
    if global_context:
        dev_ctx += f"ГЛОБАЛЬНЫЙ КОНТЕКСТ (public API других файлов):\n{global_context}\n\n"
        _import_hints: list[str] = []
        _cur_file = ""
        for _gc_line in global_context.splitlines():
            if _gc_line.startswith("--- ") and _gc_line.endswith(" PUBLIC API ---"):
                _cur_file = _gc_line.split("---")[1].strip().replace(" PUBLIC API", "").strip()
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

    # Опыт прошлых проектов (если есть feedback — ищем релевантный опыт)
    last_fb = state.get("feedbacks", {}).get(current_file, "")
    if last_fb:
        experiences = search_experience(last_fb, category="develop")
        exp_ctx = format_experience_context(experiences)
        if exp_ctx:
            dev_ctx += exp_ctx

    # Существующий код
    if existing_code:
        max_code_chars = MAX_CONTEXT_CHARS // 2
        trimmed = existing_code[:max_code_chars] + "\n# [... код обрезан ...]" if len(existing_code) > max_code_chars else existing_code
        dev_ctx += f"ТЕКУЩИЙ КОД `{current_file}`:\n{trimmed}\n\n"

    # Feedback
    feedback_ctx = get_feedback_ctx(state, current_file)
    if feedback_ctx:
        max_feedback_chars = MAX_CONTEXT_CHARS // 3
        if len(feedback_ctx) > max_feedback_chars:
            feedback_ctx = feedback_ctx[:max_feedback_chars] + "\n[... обрезано ...]"
        if existing_code:
            dev_ctx += (
                "⚠️ ПРАВЬ ТОЧЕЧНО: текущий код уже предоставлен выше. "
                "Исправь ТОЛЬКО проблемы из фидбэка ниже, сохрани работающую структуру.\n\n"
            )
        dev_ctx += feedback_ctx

    return dev_ctx


def _try_force_approve(
    logger: logging.Logger,
    state: dict,
    src_path: Path,
    current_file: str,
    total_attempts: int,
    file_attempts: dict[str, int],
) -> str:
    """Проверяет force-approve mode. Возвращает: 'approved', 'write_without_checks', 'normal'."""
    if total_attempts < MAX_CUMULATIVE:
        return "normal"

    file_path = src_path / current_file
    if file_path.exists() and file_path.read_text(encoding="utf-8").strip():
        gi = safe_contract(state).get("global_imports", {}).get(current_file, [])
        if gi:
            existing = file_path.read_text(encoding="utf-8")
            patched = ensure_a5_imports(existing, gi)
            patched = strip_non_a5_cross_imports(patched, gi, state.get("files", []))
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
        return "approved"
    else:
        logger.warning(
            f"⚠️  {current_file}: cumulative={total_attempts} но файла нет на диске "
            f"→ пишем код без проверок."
        )
        file_attempts[current_file] = 0
        return "write_without_checks"


def _generate_skeleton(
    logger: logging.Logger,
    file_contract: list,
    global_imports: list,
    file_path: Path,
    current_file: str,
) -> str:
    """Генерирует скелет из A5 контракта. Возвращает код скелета."""
    logger.warning(f"  ⚠️  {current_file}: developer вернул код без функций/классов — генерирую скелет из A5")
    skeleton_parts: list[str] = []
    if global_imports:
        for imp in global_imports:
            if isinstance(imp, str):
                skeleton_parts.append(imp)
        skeleton_parts.append("")
    in_class = False  # Трекаем: следующие методы (self/cls) — внутри класса
    for item in file_contract:
        if not isinstance(item, dict):
            continue
        sig = item.get("signature", "").strip()
        hints = item.get("implementation_hints", "")
        desc = item.get("description", "")
        if sig.startswith("class "):
            # Чистим остатки "class X: ..." → "class X"
            clean_sig = re.sub(r"\s*:\s*\.{3,}\s*$", "", sig)
            clean_sig = re.sub(r"\s*\.{3,}\s*$", "", clean_sig).rstrip(": ")
            in_class = True
            skeleton_parts.append(f"{clean_sig}:")
            skeleton_parts.append(f"    \"\"\"{desc}\"\"\"")
            if hints:
                skeleton_parts.append(f"    # TODO: {hints}")
            skeleton_parts.append(f"    pass")
            skeleton_parts.append("")
        elif sig.startswith(("def ", "async def ")):
            # Определяем: это метод класса (self/cls) или модульная функция?
            is_method = in_class and re.search(r"\(\s*(?:self|cls)\b", sig)
            indent = "    " if is_method else ""
            skeleton_parts.append(f"{indent}{sig}:")
            skeleton_parts.append(f"{indent}    \"\"\"{desc}\"\"\"")
            if hints:
                skeleton_parts.append(f"{indent}    # Алгоритм: {hints}")
            skeleton_parts.append(f"{indent}    pass")
            skeleton_parts.append("")
            if not is_method:
                in_class = False  # Модульная функция — выходим из контекста класса
    skeleton_code = "\n".join(skeleton_parts)
    file_path.write_text(skeleton_code, encoding="utf-8")
    return skeleton_code


async def _self_reflect_with_rollback(
    logger: logging.Logger,
    cache: ThreadSafeCache,
    src_path: Path,
    current_file: str,
    code: str,
    state: dict,
    stats: ModelStats,
    randomize: bool,
    file_path: Path,
    file_contract: list,
    global_context: str,
    global_imports: list,
    language: str,
) -> tuple[str, str]:
    """Self-Reflect с откатом при ошибках. Возвращает (итоговый_код, sr_feedback)."""
    sr_status, sr_feedback = await do_self_reflect(
        logger, cache, src_path, current_file, code, state, stats, randomize
    )
    if sr_status == "NEEDS_IMPROVEMENT":
        new_code = file_path.read_text(encoding="utf-8")
        sr_check = _run_checks(
            new_code, code, current_file, state, file_contract,
            global_context, global_imports, language, src_path,
        )
        if sr_check:
            logger.warning(f"  ⚠️  Self-reflect ввёл ошибки ({sr_check[0]}) → откат")
            file_path.write_text(code, encoding="utf-8")
        else:
            code = new_code
    return code, sr_feedback


def _approve_file(
    logger: logging.Logger,
    state: dict,
    project_path: Path,
    current_file: str,
    attempt: int,
    dev_model: str,
    stats: ModelStats,
    file_attempts: dict[str, int],
) -> None:
    """Одобряет файл: обновляет статистику, state, записывает опыт."""
    stats.record("developer", dev_model, True)
    logger.info(f"✅ {current_file} одобрен.")
    prev_feedback = state.get("feedbacks", {}).get(current_file, "")
    if prev_feedback and attempt > 0:
        record_experience(
            error_pattern=prev_feedback[:500],
            fix_description=f"Файл {current_file} исправлен на попытке {attempt + 1}",
            category="develop",
            file=current_file,
        )
    approved = state.setdefault("approved_files", [])
    if current_file not in approved:
        approved.append(current_file)
    state["feedbacks"][current_file] = ""
    state.setdefault("feedback_history", {})[current_file] = []
    file_attempts[current_file] = 0
    update_artifact_a9(project_path, current_file, f"Одобрен на попытке {attempt + 1}. Модель: {dev_model}.")


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
    file_attempts: dict[str, int] = state.setdefault("file_attempts", {})
    order     = build_dependency_order(state["files"], src_path, file_attempts)
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
        fa_result = _try_force_approve(logger, state, src_path, current_file, total_attempts, file_attempts)
        force_approve_mode = fa_result != "normal"
        if fa_result == "approved":
            continue
        if fa_result == "write_without_checks":
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

        # A5: контракт для текущего файла
        file_contract  = safe_contract(state).get("file_contracts", {}).get(current_file, [])
        global_imports = safe_contract(state).get("global_imports", {}).get(current_file, [])

        # Контекст: сначала A5-зависимости, потом остальные (фильтрация по dependency graph)
        dep_ordered = get_a5_deps(current_file, global_imports, state["files"])
        global_context = get_global_context(src_path, dep_ordered)

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

        dev_ctx = _build_dev_context(
            state, current_file, existing_code, file_contract, global_imports, global_context, src_path,
        )

        # Patch mode: если есть existing_code + feedback + attempt >= 1, пробуем search/replace
        last_feedback = state.get("feedbacks", {}).get(current_file, "")
        use_patch = bool(existing_code and last_feedback and attempt >= 1)
        code = ""
        dev_model = get_model("developer", attempt, randomize=randomize)

        if use_patch:
            patch_model = get_model("developer_patch", attempt, randomize=randomize)
            logger.info(
                f"🩹 [{patch_model}] Patch mode: {current_file} (попытка {attempt + 1}/{MAX_FILE_ATTEMPTS}) ..."
            )
            patch_ctx = (
                f"Файл: `{current_file}`\n\n"
                f"ТЕКУЩИЙ КОД:\n{existing_code}\n\n"
            )
            if file_contract:
                patch_ctx += f"API КОНТРАКТ (A5):\n{json.dumps(file_contract, ensure_ascii=False, indent=2)}\n\n"
            patch_ctx += f"ЗАМЕЧАНИЯ (исправь ТОЛЬКО эти проблемы):\n{last_feedback}\n"
            try:
                patch_resp = await ask_agent(logger, "developer_patch", patch_ctx, cache, attempt, randomize, language)
                changes = patch_resp.get("changes", [])
                if isinstance(changes, list) and changes:
                    patched = apply_search_replace(existing_code, changes)
                    if patched is not None:
                        code = sanitize_llm_code(patched)
                        stats.record("developer_patch", patch_model, True)
                        logger.info(f"  ✅ Patch applied: {len(changes)} change(s)")
                    else:
                        stats.record("developer_patch", patch_model, False)
                        logger.info(f"  ⚠️  Patch не применился (search не найден) → fallback на full regen")
                else:
                    stats.record("developer_patch", patch_model, False)
                    logger.info(f"  ⚠️  Patch пустой → fallback на full regen")
            except (LLMError, ValueError) as e:
                stats.record("developer_patch", patch_model, False)
                logger.info(f"  ⚠️  Patch agent упал: {e} → fallback на full regen")

        if not code:
            dev_model = get_model("developer", attempt, randomize=randomize)
            # Если patch не сработал — усилить инструкцию не терять функции
            if use_patch and existing_code:
                dev_ctx += (
                    "\n\n⛔ ВНИМАНИЕ: patch-режим не сработал, ты пишешь ПОЛНЫЙ файл.\n"
                    "ОБЯЗАТЕЛЬНО сохрани ВСЕ существующие функции и классы из ТЕКУЩЕГО КОДА.\n"
                    "Удаление функций = автоматический REJECT.\n"
                )
            logger.info(
                f"💻 [{dev_model}] Разработчик пишет {current_file} (попытка {attempt + 1}/{MAX_FILE_ATTEMPTS}) ..."
            )
            try:
                dev_resp = await ask_agent(logger, "developer", dev_ctx, cache, attempt, randomize, language)
                code     = sanitize_llm_code(dev_resp.get("code", ""))
            except (LLMError, ValueError) as e:
                logger.exception(f"Developer упал: {e}")
                stats.record("developer", dev_model, False)
                state["feedbacks"][current_file] = f"Агент не вернул код: {e}"
                file_attempts[current_file] = attempt + 1
                cumulative_attempts[current_file] = total_attempts + 1
                continue

        if not code:
            stats.record("developer", get_model("developer", attempt, randomize=randomize), False)
            state["feedbacks"][current_file] = "Агент вернул пустой код."
            file_attempts[current_file] = attempt + 1
            cumulative_attempts[current_file] = total_attempts + 1
            continue

        # Проверка усечения: LLM мог исчерпать max_tokens и обрезать код
        truncation_msg = check_truncated_code(code)
        if truncation_msg:
            logger.warning(f"  ⚠️  {current_file}: {truncation_msg}")
            _reject_file(state, file_attempts, cumulative_attempts, current_file,
                         attempt, total_attempts, truncation_msg, stats, dev_model, logger)
            continue

        # Проверка: если код — только imports + пустые строки (модель не написала тело функций),
        # генерируем скелет из A5 контракта и повторяем запрос с ним как "existing_code"
        code_lines = [ln for ln in code.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        has_functions = any(ln.strip().startswith(("def ", "class ", "async def ")) for ln in code_lines)
        if not has_functions and file_contract and attempt < MAX_FILE_ATTEMPTS - 1:
            _generate_skeleton(logger, file_contract, global_imports, file_path, current_file)
            state["feedbacks"][current_file] = (
                f"Ты вернул код БЕЗ функций/классов — только импорты.\n"
                f"НИЖЕ — СКЕЛЕТ из A5 контракта. Заполни ВСЕ функции/классы реальным кодом.\n"
                f"Убери pass и TODO, напиши ПОЛНУЮ рабочую реализацию по алгоритму в комментариях.\n"
            )
            file_attempts[current_file] = attempt + 1
            cumulative_attempts[current_file] = total_attempts + 1
            stats.record("developer", dev_model, False)
            continue

        # Авто-инъекция A5 импортов — developer часто забывает import numpy, from typing и т.д.
        if global_imports:
            code = ensure_a5_imports(code, global_imports)

        # Удаление cross-file project imports несуществующих имён
        # (LLM часто выдумывает импорты; оставляем если имя есть в A5 или реально в файле)
        project_files = state.get("files", [])
        if project_files:
            code = strip_non_a5_cross_imports(code, global_imports, project_files, global_context)

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

        # Детерминистские проверки (9 штук)
        check_result = _run_checks(
            code, existing_code, current_file, state, file_contract,
            global_context, global_imports, language, src_path,
        )
        if check_result:
            check_name, check_feedback = check_result
            logger.warning(f"⛔ {current_file}: {check_name} → авто-REJECT")
            _reject_file(state, file_attempts, cumulative_attempts, current_file,
                         attempt, total_attempts, check_feedback, stats, dev_model, logger)
            continue

        file_path.write_text(code, encoding="utf-8")

        # Self-Reflect с откатом при ошибках
        code, sr_feedback = await _self_reflect_with_rollback(
            logger, cache, src_path, current_file, code, state, stats, randomize,
            file_path, file_contract, global_context, global_imports, language,
        )

        # Детекция зацикливания reviewer: если все последние feedback одинаковы — auto-approve
        fb_history = state.get("feedback_history", {}).get(current_file, [])
        reviewer_looping = (
            len(fb_history) >= MAX_FEEDBACK_HISTORY
            and len(set(fb_history[-MAX_FEEDBACK_HISTORY:])) == 1
        )
        if reviewer_looping:
            logger.warning(
                f"⚠️  {current_file}: reviewer зациклился (одинаковый feedback {MAX_FEEDBACK_HISTORY} раз) → auto-approve"
            )
            _approve_file(logger, state, project_path, current_file, attempt, dev_model, stats, file_attempts)
            continue

        # Внешний ревью
        rev_status, rev_feedback, needs_spec = await _review_file(
            logger, cache, current_file, code, attempt, stats, randomize, language,
            file_contract=file_contract, global_imports=global_imports,
        )

        if rev_status == "APPROVE":
            _approve_file(logger, state, project_path, current_file, attempt, dev_model, stats, file_attempts)
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

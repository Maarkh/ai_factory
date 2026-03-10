import json
import logging
from pathlib import Path

from config import TRUNCATE_CODE
from exceptions import LLMError
from llm import ask_agent
from json_utils import parse_if_str
from artifacts import save_artifact
from lang_utils import LANG_DISPLAY
from log_utils import get_model
from cache import ThreadSafeCache
from stats import ModelStats

from contract_validation import (
    _normalize_file_contracts,
    _remove_non_ascii_entries,
    _inject_missing_data_models,
    _validate_global_imports,
    _inject_signature_type_imports,
    _sanitize_implementation_hints,
    _inject_requirements_imports,
    _inject_cross_file_imports,
    _dedup_cross_file_classes,
    _validate_signature_types,
    _validate_import_consistency,
    _detect_and_fix_circular_imports,
)

# Re-exports: other modules import these from contract
from contract_validation import (  # noqa: F401
    validate_requirements_txt,
    _parse_import_line,
    _validate_data_model_coverage,
)


async def _validate_and_patch_contract(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    contract: dict,
    files: list[str],
    randomize: bool = False,
) -> dict:
    """
    Проверяет что все файлы из списка присутствуют в контракте.
    Для отсутствующих файлов запрашивает контракт отдельно.
    Защита от неполной генерации contract_analyst.
    """
    language = state.get("language", "python")
    contract = _normalize_file_contracts(contract)
    fc = contract.setdefault("file_contracts", {})
    gi = contract.setdefault("global_imports", {})

    missing = [f for f in files if f not in fc or not fc[f]]
    if not missing:
        return contract

    logger.warning(f"⚠️  A5 неполный — отсутствуют контракты для: {', '.join(missing)}")

    req_path = project_path / "src" / "requirements.txt"
    req_content = req_path.read_text(encoding="utf-8").strip() if req_path.exists() else "# пусто"

    for fname in missing:
        logger.info(f"   🔧 Запрашиваю контракт для {fname} ...")
        # Контекст: задача + архитектура + уже известные контракты других файлов
        existing_contracts = {k: v for k, v in fc.items() if k != fname}
        ctx = (
            f"Запрос: {state['task']}\n\n"
            f"Системная спецификация (A2):\n"
            f"{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
            f"Архитектура:\n{json.dumps(state.get('architecture', {}), ensure_ascii=False, indent=2)}\n\n"
            f"Язык: {LANG_DISPLAY.get(language, language)}\n\n"
            f"Доступные pip-пакеты (requirements.txt):\n{req_content}\n\n"
            f"Уже сгенерированные контракты других файлов:\n"
            f"{json.dumps(existing_contracts, ensure_ascii=False, indent=2)}\n\n"
            f"ЗАДАЧА: Сгенерируй API контракт ТОЛЬКО для файла `{fname}`.\n"
            f"Верни JSON с ключами file_contracts и global_imports только для этого файла."
        )
        try:
            patch = await ask_agent(logger, "contract_analyst", ctx, cache, 0, randomize, language)
            patch_fc = parse_if_str(patch.get("file_contracts", {}), dict, {})
            patch_gi = parse_if_str(patch.get("global_imports", {}), dict, {})

            # Берём контракт для нашего файла — или весь ответ если ключ не совпал
            file_contract = patch_fc.get(fname)
            if file_contract is None:
                file_contract = next(iter(patch_fc.values()), [])
            file_imports = patch_gi.get(fname)
            if file_imports is None:
                file_imports = next(iter(patch_gi.values()), [])

            if file_contract:
                fc[fname] = parse_if_str(file_contract, list, [])
                gi[fname] = parse_if_str(file_imports,  list, [])
                logger.info(f"   ✅ Контракт для {fname} получен ({len(fc[fname])} функций).")
                stats.record("contract_analyst", get_model("contract_analyst"), True)
            else:
                logger.warning(f"   ⚠️  Контракт для {fname} пустой — разработчик будет работать без него.")
                stats.record("contract_analyst", get_model("contract_analyst"), False)
        except (LLMError, ValueError) as e:
            logger.exception(f"Патч контракта для {fname} упал: {e}")
            stats.record("contract_analyst", get_model("contract_analyst"), False)

    contract["file_contracts"] = fc
    contract["global_imports"]  = gi
    # Post-validation: полный набор валидаций
    contract = _validate_global_imports(
        contract, state.get("architecture", {}), files, logger,
        requirements_path=req_path if req_path.exists() else None,
    )
    contract = _inject_signature_type_imports(contract, logger)
    contract = _sanitize_implementation_hints(contract, logger)
    contract = _inject_requirements_imports(contract, req_path if req_path.exists() else None, logger)
    contract = _inject_cross_file_imports(contract, logger)
    contract = _dedup_cross_file_classes(contract, logger)
    contract = _validate_signature_types(contract, files, logger)
    contract = _validate_import_consistency(contract, logger)
    contract = _detect_and_fix_circular_imports(contract, files, logger)
    contract = _remove_non_ascii_entries(contract)
    return contract


async def patch_contract_for_file(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    filename: str,
    developer_code: str,
    feedback: str,
    randomize: bool = False,
) -> bool:
    """
    Патчит A5 контракт для одного файла на основе фидбэка ревьюера.
    Вызывается когда файл не проходит ревью N раз подряд —
    значит контракт не соответствует реальности и нужно его починить.
    Возвращает True если контракт обновлён.
    """
    language = state.get("language", "python")
    contract = state.get("api_contract", {})
    fc = contract.get("file_contracts", {})
    gi = contract.get("global_imports", {})
    current = fc.get(filename, [])

    logger.info(f"🔧 Патч A5 для {filename} на основе фидбэка ревьюера ...")

    req_path = project_path / "src" / "requirements.txt"
    req_content = req_path.read_text(encoding="utf-8").strip() if req_path.exists() else "# пусто"

    ctx = (
        f"Текущий API контракт (A5) для файла `{filename}`:\n"
        f"{json.dumps(current, ensure_ascii=False, indent=2)}\n\n"
        f"Код разработчика (НЕ прошёл ревью):\n{developer_code[:TRUNCATE_CODE]}\n\n"
        f"Замечания ревьюера (код отклонён из-за этих проблем):\n{feedback[:TRUNCATE_CODE // 2]}\n\n"
        f"Контракты ДРУГИХ файлов проекта (для called_by ссылок):\n"
        f"{json.dumps({k: v for k, v in fc.items() if k != filename}, ensure_ascii=False, indent=2)}\n\n"
        f"Язык: {LANG_DISPLAY.get(language, language)}\n\n"
        f"Доступные pip-пакеты (requirements.txt):\n{req_content}\n\n"
        f"ЗАДАЧА: Исправь контракт A5 ТОЛЬКО для файла `{filename}`.\n"
        f"Проанализируй замечания ревьюера и код разработчика.\n"
        f"Если функция требует дополнительных параметров — добавь их в сигнатуру.\n"
        f"Если нужны дополнительные функции/классы — добавь их.\n"
        f"Если сигнатура неидиоматична — исправь.\n"
        f"Верни JSON с ключами file_contracts и global_imports только для этого файла."
    )

    try:
        patch = await ask_agent(logger, "contract_analyst", ctx, cache, 0, randomize, language)
        patch = _normalize_file_contracts(patch) if isinstance(patch, dict) else {}
        patch_fc = parse_if_str(patch.get("file_contracts", {}), dict, {})
        patch_gi = parse_if_str(patch.get("global_imports", {}), dict, {})

        file_contract = patch_fc.get(filename)
        if file_contract is None:
            file_contract = next(iter(patch_fc.values()), [])
        file_imports = patch_gi.get(filename)
        if file_imports is None:
            file_imports = next(iter(patch_gi.values()), [])

        if file_contract:
            fc[filename] = parse_if_str(file_contract, list, [])
            gi[filename] = parse_if_str(file_imports, list, [])
            contract["file_contracts"] = fc
            contract["global_imports"] = gi
            # Post-validation: полный набор валидаций как в phase_generate_api_contract
            files_list = state.get("files", [])
            contract = _validate_global_imports(
                contract, state.get("architecture", {}),
                files_list, logger,
                requirements_path=req_path if req_path.exists() else None,
            )
            contract = _inject_signature_type_imports(contract, logger)
            contract = _sanitize_implementation_hints(contract, logger)
            contract = _inject_requirements_imports(contract, req_path if req_path.exists() else None, logger)
            contract = _inject_cross_file_imports(contract, logger)
            contract = _dedup_cross_file_classes(contract, logger)
            contract = _validate_signature_types(contract, files_list, logger)
            contract = _validate_import_consistency(contract, logger)
            contract = _detect_and_fix_circular_imports(contract, files_list, logger)
            contract = _remove_non_ascii_entries(contract)
            state["api_contract"] = contract
            save_artifact(project_path, "A5", contract)
            stats.record("contract_analyst", get_model("contract_analyst"), True)
            logger.info(f"   ✅ A5 для {filename} обновлён ({len(fc[filename])} функций).")
            return True
        else:
            logger.warning(f"   ⚠️  Патч A5 для {filename} пустой.")
            stats.record("contract_analyst", get_model("contract_analyst"), False)
            return False
    except (LLMError, ValueError) as e:
        logger.exception(f"Патч A5 для {filename} упал: {e}")
        stats.record("contract_analyst", get_model("contract_analyst"), False)
        return False


async def phase_review_api_contract(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    contract: dict,
    arch_resp: dict,
    sa_resp: dict,
    randomize: bool = False,
) -> bool:
    """
    Ревью A5 (API Contract) на согласованность с A2/A3.
    Возвращает True если контракт одобрен, False если отклонён.
    При исключении возвращает True (не блокируем пайплайн).
    """
    language = state.get("language", "python")
    logger.info("🔍 Ревью A5 (API Contract) ...")

    files_list = [f.get("path", f) if isinstance(f, dict) else f
                  for f in arch_resp.get("files", state.get("files", []))]

    ctx = (
        f"API контракт (A5):\n{json.dumps(contract, ensure_ascii=False, indent=2)}\n\n"
        f"Системная спецификация (A2):\n{json.dumps(sa_resp, ensure_ascii=False, indent=2)}\n\n"
        f"Архитектура (A3/A4):\n{json.dumps(arch_resp, ensure_ascii=False, indent=2)}\n\n"
        f"Файлы проекта: {files_list}\n\n"
        f"Язык: {language}"
    )

    try:
        result = await ask_agent(logger, "a5_validator", ctx, cache, 0, randomize, language)
        status = result.get("status", "REJECT")
        feedback = result.get("feedback", "")
        model = get_model("a5_validator")

        if status == "APPROVE":
            logger.info("✅ A5 прошёл ревью.")
            stats.record("a5_validator", model, True)
            save_artifact(project_path, "A5.1", result)
            return True
        else:
            logger.warning(f"❌ A5 отклонён: {feedback}")
            stats.record("a5_validator", model, False)
            return False
    except (LLMError, ValueError) as e:
        logger.warning(f"⚠️  A5 Validator упал: {e}. Пропускаем ревью.")
        return True


async def phase_generate_api_contract(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    arch_resp: dict,
    sa_resp: dict,
    randomize: bool = False,
) -> dict:
    """
    Генерирует A5 (API & Contract Spec).
    Developer получает явный контракт функций вместо «угадывания».
    """
    language = state.get("language", "python")
    logger.info("📋 Contract Analyst генерирует A5 (API контракт) ...")

    req_path = project_path / "src" / "requirements.txt"
    req_content = req_path.read_text(encoding="utf-8").strip() if req_path.exists() else "# пусто"

    ctx = (
        f"Запрос: {state['task']}\n\n"
        f"Системная спецификация (A2):\n{json.dumps(sa_resp, ensure_ascii=False, indent=2)}\n\n"
        f"Архитектура (A3/A4):\n{json.dumps(arch_resp, ensure_ascii=False, indent=2)}\n\n"
        f"Язык: {LANG_DISPLAY.get(language, language)}\n\n"
        f"Файлы: {arch_resp.get('files', [])}\n\n"
        f"Доступные pip-пакеты (requirements.txt):\n{req_content}"
    )

    try:
        contract = await ask_agent(logger, "contract_analyst", ctx, cache, 0, randomize, language)
        # Гарантируем, что контракт — это dict с нужными ключами
        if not isinstance(contract, dict):
            contract = {}
        # Нормализация: модель может вернуть file_contracts как list вместо dict
        contract = _normalize_file_contracts(contract)
        contract.setdefault("file_contracts", {})
        contract.setdefault("global_imports", {})
        stats.record("contract_analyst", get_model("contract_analyst"), True)
        # Валидация: все файлы должны иметь контракт
        files_list = [f.get("path", f) if isinstance(f, dict) else f
                      for f in arch_resp.get("files", state.get("files", []))]
        contract = await _validate_and_patch_contract(
            logger, project_path, state, cache, stats, contract, files_list, randomize
        )
        # Детерминистская валидация: data models из A2 покрыты классами в A5
        contract = _inject_missing_data_models(contract, sa_resp, files_list, logger)
        # Детерминистская валидация: global_imports ссылаются на реальные пакеты
        req_path = project_path / "src" / "requirements.txt"
        contract = _validate_global_imports(
            contract, arch_resp, files_list, logger,
            requirements_path=req_path if req_path.exists() else None,
        )
        contract = _inject_signature_type_imports(contract, logger)
        # Санитизация: implementation_hints не ссылаются на несуществующие имена
        contract = _sanitize_implementation_hints(contract, logger)
        # Авто-инжект imports из requirements.txt на основе hints
        contract = _inject_requirements_imports(contract, req_path if req_path.exists() else None, logger)
        # Детерминистская инъекция: межфайловые импорты (data models и т.п.)
        contract = _inject_cross_file_imports(contract, logger)
        # Дедупликация: один класс — один файл
        contract = _dedup_cross_file_classes(contract, logger)
        # Проверка: все типы из сигнатур определены (иначе → models.py)
        contract = _validate_signature_types(contract, files_list, logger)
        # Детерминистская валидация: cross-file imports ссылаются на реальные имена
        # (ПОСЛЕ inject, чтобы проверить и свежедобавленные импорты)
        contract = _validate_import_consistency(contract, logger)
        # Детерминистская проверка: циклические зависимости → вынос в models.py
        contract = _detect_and_fix_circular_imports(contract, files_list, logger)
        # Финальная очистка: убираем не-ASCII имена, которые могли появиться на любом этапе
        contract = _remove_non_ascii_entries(contract)
        save_artifact(project_path, "A5", contract)
        logger.info("✅ A5 (API контракт) готов.")
        return contract
    except (LLMError, ValueError) as e:
        logger.exception(f"Contract Analyst упал: {e}")
        stats.record("contract_analyst", get_model("contract_analyst"), False)
        logger.warning(f"⚠️  Contract Analyst не справился: {e}. Контракт будет пустым.")
        return {"file_contracts": {}, "global_imports": {}}


async def refresh_api_contract(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    randomize: bool = False,
) -> None:
    """
    Каскад: после обновления A2 пересчитывает A5.
    Вызывается из revise_spec().
    """
    language = state.get("language", "python")
    logger.info("🔄 Каскадное обновление A5 после изменения A2 ...")
    req_path = project_path / "src" / "requirements.txt"
    req_content = req_path.read_text(encoding="utf-8").strip() if req_path.exists() else "# пусто"

    ctx = (
        f"Запрос: {state['task']}\n\n"
        f"Обновлённая спецификация (A2):\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
        f"Файлы: {state.get('files', [])}\n\n"
        f"Язык: {LANG_DISPLAY.get(language, language)}\n\n"
        f"Доступные pip-пакеты (requirements.txt):\n{req_content}"
    )
    try:
        new_contract = await ask_agent(logger, "contract_analyst", ctx, cache, 0, randomize, language)
        if not isinstance(new_contract, dict):
            new_contract = {}
        new_contract = _normalize_file_contracts(new_contract)
        new_contract.setdefault("file_contracts", {})
        new_contract.setdefault("global_imports", {})
        # Валидация: все файлы должны иметь контракт
        files_list = state.get("files", [])
        new_contract = await _validate_and_patch_contract(
            logger, project_path, state, cache, stats,
            new_contract, files_list, randomize
        )
        # Детерминистские валидации (аналогично phase_generate_api_contract)
        new_contract = _inject_missing_data_models(
            new_contract, state.get("system_specs", {}), files_list, logger
        )
        req_path = project_path / "src" / "requirements.txt"
        new_contract = _validate_global_imports(
            new_contract, state.get("architecture", {}),
            files_list, logger,
            requirements_path=req_path if req_path.exists() else None,
        )
        new_contract = _inject_signature_type_imports(new_contract, logger)
        new_contract = _sanitize_implementation_hints(new_contract, logger)
        new_contract = _inject_requirements_imports(new_contract, req_path if req_path.exists() else None, logger)
        new_contract = _inject_cross_file_imports(new_contract, logger)
        new_contract = _dedup_cross_file_classes(new_contract, logger)
        new_contract = _validate_signature_types(new_contract, files_list, logger)
        new_contract = _validate_import_consistency(new_contract, logger)
        new_contract = _detect_and_fix_circular_imports(new_contract, files_list, logger)
        new_contract = _remove_non_ascii_entries(new_contract)
        # Восстановление: если новый A5 потерял валидные импорты из старого A5,
        # сохраняем их (LLM при cascade refresh часто возвращает мусор вместо imports)
        old_gi = state.get("api_contract", {}).get("global_imports", {})
        new_gi = new_contract.setdefault("global_imports", {})
        for fname in files_list:
            old_imports = old_gi.get(fname, [])
            new_imports = new_gi.get(fname, [])
            if isinstance(old_imports, list) and isinstance(new_imports, list):
                if len(new_imports) < len(old_imports):
                    # Новый A5 потерял импорты — восстанавливаем из старого
                    new_set = set(new_imports)
                    for imp in old_imports:
                        if imp not in new_set:
                            new_imports.append(imp)
                            logger.info(f"  📎 Восстановлен import из старого A5: '{imp}' для {fname}")
                    new_gi[fname] = new_imports
        # Sync: добавляем новые файлы, удаляем призраки
        a5_files = set(new_contract.get("file_contracts", {}).keys())
        for f in a5_files:
            if f not in files_list:
                files_list.append(f)
            state.setdefault("feedbacks", {}).setdefault(f, "")
        for f in list(files_list):
            if f not in a5_files:
                logger.info(f"  🗑️  Удалён файл-призрак: {f} (нет в новом A5)")
                files_list.remove(f)
                state.get("feedbacks", {}).pop(f, None)
                if f in state.get("approved_files", []):
                    state["approved_files"].remove(f)
                state.get("file_attempts", {}).pop(f, None)
                state.get("cumulative_file_attempts", {}).pop(f, None)
        state["api_contract"] = new_contract
        save_artifact(project_path, "A5", new_contract)
        logger.info("✅ A5 обновлён каскадно.")
    except (LLMError, ValueError) as e:
        logger.exception(f"Каскадное обновление A5 упало: {e}")
        logger.warning(f"⚠️  Не удалось обновить A5: {e}")

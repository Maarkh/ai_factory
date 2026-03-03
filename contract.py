import json
import logging
import re
import sys
from pathlib import Path

from exceptions import LLMError
from llm import ask_agent
from json_utils import _parse_if_str
from artifacts import save_artifact
from lang_utils import LANG_DISPLAY
from log_utils import get_model
from cache import ThreadSafeCache
from stats import ModelStats


# ─────────────────────────────────────────────
# Детерминистские валидации A5 контракта
# ─────────────────────────────────────────────


def _normalize_file_contracts(contract: dict) -> dict:
    """Нормализация: модель может вернуть file_contracts как list вместо dict."""
    raw_fc = contract.get("file_contracts", {})
    if isinstance(raw_fc, list):
        normalized: dict = {}
        for item in raw_fc:
            if isinstance(item, dict):
                fname = item.get("file") or item.get("path") or item.get("name", "")
                funcs = item.get("functions") or item.get("contracts") or item.get("items") or []
                if fname:
                    normalized[fname] = funcs
        contract["file_contracts"] = normalized
    raw_gi = contract.get("global_imports", {})
    if isinstance(raw_gi, list):
        contract["global_imports"] = {}
    return contract


def _validate_data_model_coverage(
    contract: dict,
    system_specs: dict,
    logger: logging.Logger,
) -> list[str]:
    """Проверяет что каждая data_model из A2 определена как класс хотя бы в одном файле A5.

    Возвращает список имён моделей, не покрытых контрактом.
    """
    data_models = system_specs.get("data_models", [])
    if not data_models:
        return []
    # Имена моделей из A2
    model_names: set[str] = set()
    for dm in data_models:
        name = dm.get("name", "") if isinstance(dm, dict) else ""
        if name:
            model_names.add(name)
    if not model_names:
        return []
    # Ищем покрытие в file_contracts A5
    defined_names: set[str] = set()
    for fname, items in contract.get("file_contracts", {}).items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            item_name = item.get("name", "")
            sig = item.get("signature", "")
            # Совпадение по name или по "class ModelName" в signature
            if item_name in model_names:
                defined_names.add(item_name)
            for mn in model_names:
                if f"class {mn}" in sig:
                    defined_names.add(mn)
    missing = sorted(model_names - defined_names)
    if missing:
        logger.warning(f"⚠️  A5: data models из A2 не покрыты контрактом: {', '.join(missing)}")
    return missing


def _inject_missing_data_models(
    contract: dict,
    system_specs: dict,
    files: list[str],
    logger: logging.Logger,
) -> dict:
    """Добавляет в A5 контракт класс для каждой data_model из A2, которая не покрыта.

    Выбирает файл: первый файл != main.py (или main.py если он единственный).
    """
    missing = _validate_data_model_coverage(contract, system_specs, logger)
    if not missing:
        return contract

    fc = contract.setdefault("file_contracts", {})

    # Выбираем целевой файл для data models
    target_file = files[0]  # fallback
    for f in files:
        if f != "main.py" and not f.startswith("test_"):
            target_file = f
            break

    data_models = {
        dm.get("name", ""): dm
        for dm in system_specs.get("data_models", [])
        if isinstance(dm, dict) and dm.get("name")
    }

    for model_name in missing:
        dm = data_models.get(model_name, {})
        fields = dm.get("fields", [])
        # Формируем описание полей для description
        field_desc = ""
        if fields:
            field_names = []
            for f in fields:
                if isinstance(f, dict):
                    field_names.extend(f.keys())
                elif isinstance(f, str):
                    field_names.append(f.split(":")[0].strip())
            if field_names:
                field_desc = f" Поля: {', '.join(field_names)}."

        entry = {
            "name": model_name,
            "signature": f"class {model_name}",
            "description": f"Data model из A2.{field_desc}",
            "required": True,
            "called_by": [],
        }
        fc.setdefault(target_file, []).append(entry)
        logger.info(f"  📋 A5: добавлен класс {model_name} в контракт файла {target_file} (из data_models A2)")

    return contract


def _validate_global_imports(
    contract: dict,
    arch_resp: dict,
    project_files: list[str],
    logger: logging.Logger,
    requirements_path: Path | None = None,
) -> dict:
    """Удаляет из global_imports A5 импорты несуществующих пакетов.

    Проверяет: stdlib, файлы проекта, dependencies из архитектуры,
    а также requirements.txt (если передан).
    """
    gi = contract.get("global_imports", {})
    if not gi:
        return contract

    # Допустимые имена: stdlib
    stdlib = sys.stdlib_module_names if hasattr(sys, "stdlib_module_names") else set()
    # Модули проекта (без расширения)
    project_modules = {Path(f).stem for f in project_files}
    # pip-пакеты из dependencies архитектуры
    deps = arch_resp.get("dependencies", []) if isinstance(arch_resp, dict) else []
    pip_names: set[str] = set()
    for dep in deps:
        if isinstance(dep, str):
            pkg = re.split(r"[=<>~!\[]", dep)[0].strip().lower()
            pip_names.add(pkg)
            pip_names.add(pkg.replace("-", "_"))
    # Дополнительно: pip-пакеты из requirements.txt (всегда актуальный источник)
    if requirements_path and requirements_path.exists():
        from code_context import _parse_requirements
        pip_names.update(_parse_requirements(requirements_path))

    cleaned_gi: dict[str, list[str]] = {}
    for fname, imports in gi.items():
        if not isinstance(imports, list):
            cleaned_gi[fname] = imports
            continue
        valid_imports: list[str] = []
        for imp_line in imports:
            if not isinstance(imp_line, str):
                valid_imports.append(imp_line)
                continue
            # Извлекаем базовый модуль: from X import Y → X; import X → X
            m = re.match(r"(?:from\s+(\S+)\s+import|import\s+(\S+))", imp_line.strip())
            if not m:
                valid_imports.append(imp_line)
                continue
            base_module = (m.group(1) or m.group(2)).split(".")[0]
            base_lower = base_module.lower()
            base_normalized = base_lower.replace("-", "_")

            # Проверяем допустимость
            if base_module in stdlib:
                valid_imports.append(imp_line)  # stdlib — оставляем (не критично)
                continue
            if base_module in project_modules:
                valid_imports.append(imp_line)
                continue
            if base_lower in pip_names or base_normalized in pip_names:
                valid_imports.append(imp_line)
                continue
            # Невалидный import — удаляем
            logger.warning(
                f"  ⚠️  A5 global_imports: удалён '{imp_line}' для {fname} "
                f"('{base_module}' не найден в stdlib, dependencies или файлах проекта)"
            )
        cleaned_gi[fname] = valid_imports

    contract["global_imports"] = cleaned_gi
    return contract


def _inject_cross_file_imports(
    contract: dict,
    logger: logging.Logger,
) -> dict:
    """Детерминистски добавляет в global_imports межфайловые импорты.

    Если класс определён в файле A (signature='class X'), а используется
    в сигнатуре функции файла B (параметр/return type содержит 'X'),
    то в global_imports файла B добавляется 'from A_stem import X'.
    """
    fc = contract.get("file_contracts", {})
    gi = contract.setdefault("global_imports", {})

    # 1. Собираем маппинг class_name → source_file (stem)
    class_to_file: dict[str, str] = {}
    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            sig = item.get("signature", "")
            if sig.strip().startswith("class "):
                class_name = item.get("name", "")
                if class_name:
                    class_to_file[class_name] = fname

    if not class_to_file:
        return contract

    # 2. Для каждого файла проверяем сигнатуры на ссылки к классам из других файлов
    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        needed_imports: dict[str, str] = {}  # class_name → source_file
        for item in items:
            if not isinstance(item, dict):
                continue
            sig = item.get("signature", "")
            desc = item.get("description", "")
            # Не проверяем сигнатуры class (они определяют, а не используют)
            if sig.strip().startswith("class "):
                continue
            # Ищем ссылки на известные классы в сигнатуре
            for class_name, source_file in class_to_file.items():
                if source_file == fname:
                    continue  # Класс определён в этом же файле
                if class_name in sig:
                    needed_imports[class_name] = source_file

        if not needed_imports:
            continue

        # 3. Проверяем что import ещё не добавлен в global_imports
        existing = gi.get(fname, [])
        if not isinstance(existing, list):
            existing = []
        existing_str = " ".join(existing)

        for class_name, source_file in needed_imports.items():
            source_stem = Path(source_file).stem
            import_line = f"from {source_stem} import {class_name}"
            if class_name not in existing_str:
                existing.append(import_line)
                logger.info(f"  📋 A5 global_imports: добавлен '{import_line}' для {fname}")

        gi[fname] = existing

    return contract


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
            f"Уже сгенерированные контракты других файлов:\n"
            f"{json.dumps(existing_contracts, ensure_ascii=False, indent=2)}\n\n"
            f"ЗАДАЧА: Сгенерируй API контракт ТОЛЬКО для файла `{fname}`.\n"
            f"Верни JSON с ключами file_contracts и global_imports только для этого файла."
        )
        try:
            patch = await ask_agent(logger, "contract_analyst", ctx, cache, 0, randomize, language)
            patch_fc = _parse_if_str(patch.get("file_contracts", {}), dict, {})
            patch_gi = _parse_if_str(patch.get("global_imports", {}), dict, {})

            # Берём контракт для нашего файла — или весь ответ если ключ не совпал
            file_contract = patch_fc.get(fname) or next(iter(patch_fc.values()), [])
            file_imports  = patch_gi.get(fname)  or next(iter(patch_gi.values()),  [])

            if file_contract:
                fc[fname] = _parse_if_str(file_contract, list, [])
                gi[fname] = _parse_if_str(file_imports,  list, [])
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

    ctx = (
        f"Текущий API контракт (A5) для файла `{filename}`:\n"
        f"{json.dumps(current, ensure_ascii=False, indent=2)}\n\n"
        f"Код разработчика (НЕ прошёл ревью):\n{developer_code[:3000]}\n\n"
        f"Замечания ревьюера (код отклонён из-за этих проблем):\n{feedback[:1500]}\n\n"
        f"Контракты ДРУГИХ файлов проекта (для called_by ссылок):\n"
        f"{json.dumps({k: v for k, v in fc.items() if k != filename}, ensure_ascii=False, indent=2)}\n\n"
        f"Язык: {LANG_DISPLAY.get(language, language)}\n\n"
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
        patch_fc = _parse_if_str(patch.get("file_contracts", {}), dict, {})
        patch_gi = _parse_if_str(patch.get("global_imports", {}), dict, {})

        file_contract = patch_fc.get(filename) or next(iter(patch_fc.values()), [])
        file_imports  = patch_gi.get(filename) or next(iter(patch_gi.values()), [])

        if file_contract:
            fc[filename] = _parse_if_str(file_contract, list, [])
            gi[filename] = _parse_if_str(file_imports, list, [])
            contract["file_contracts"] = fc
            contract["global_imports"] = gi
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
    Новая фаза v15.0: генерирует A5 (API & Contract Spec).
    Developer получает явный контракт функций вместо «угадывания».
    """
    language = state.get("language", "python")
    logger.info("📋 Contract Analyst генерирует A5 (API контракт) ...")

    ctx = (
        f"Запрос: {state['task']}\n\n"
        f"Системная спецификация (A2):\n{json.dumps(sa_resp, ensure_ascii=False, indent=2)}\n\n"
        f"Архитектура (A3/A4):\n{json.dumps(arch_resp, ensure_ascii=False, indent=2)}\n\n"
        f"Язык: {LANG_DISPLAY.get(language, language)}\n\n"
        f"Файлы: {arch_resp.get('files', [])}"
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
        # Детерминистская инъекция: межфайловые импорты (data models и т.п.)
        contract = _inject_cross_file_imports(contract, logger)
        save_artifact(project_path, "A5", contract)
        logger.info("✅ A5 (API контракт) готов.")
        return contract
    except (LLMError, ValueError) as e:
        logger.exception(f"Contract Analyst упал: {e}")
        stats.record("contract_analyst", get_model("contract_analyst"), False)
        logger.warning(f"⚠️  Contract Analyst не справился: {e}. Контракт будет пустым.")
        return {"file_contracts": {}, "global_imports": {}}


async def _refresh_api_contract(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    randomize: bool = False,
) -> None:
    """
    Каскад v15.0: после обновления A2 пересчитывает A5.
    Вызывается из revise_spec().
    """
    language = state.get("language", "python")
    logger.info("🔄 Каскадное обновление A5 после изменения A2 ...")
    ctx = (
        f"Запрос: {state['task']}\n\n"
        f"Обновлённая спецификация (A2):\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
        f"Файлы: {state.get('files', [])}\n\n"
        f"Язык: {LANG_DISPLAY.get(language, language)}"
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
            new_contract, {},  # arch_resp недоступен после каскада
            files_list, logger,
            requirements_path=req_path if req_path.exists() else None,
        )
        new_contract = _inject_cross_file_imports(new_contract, logger)
        state["api_contract"] = new_contract
        save_artifact(project_path, "A5", new_contract)
        logger.info("✅ A5 обновлён каскадно.")
    except (LLMError, ValueError) as e:
        logger.exception(f"Каскадное обновление A5 упало: {e}")
        logger.warning(f"⚠️  Не удалось обновить A5: {e}")

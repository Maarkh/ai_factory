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


def _parse_import_line(imp_line: str) -> tuple[str, list[str]] | None:
    """Парсит строку импорта. Возвращает (source_stem, [imported_names]) или None.

    Поддерживает: 'from X import A', 'from X import A, B', 'from X import A as Z'.
    """
    if not isinstance(imp_line, str):
        return None
    m = re.match(r"from\s+(\w+)\s+import\s+(.+)", imp_line.strip())
    if not m:
        return None
    source = m.group(1)
    raw_names = m.group(2)
    names = []
    for part in raw_names.split(","):
        part = part.strip()
        if not part:
            continue
        # 'A as Z' → берём 'A' (оригинальное имя)
        name = part.split()[0].strip()
        if name.isidentifier():
            names.append(name)
    return (source, names) if names else None


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
        import logging as _log
        _log.getLogger(__name__).warning(
            f"⚠️  A5 global_imports вернулся как list (ожидался dict) — сброс в {{}}")
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

    Создаёт models.py для shared data models (предотвращает циклические зависимости).
    """
    missing = _validate_data_model_coverage(contract, system_specs, logger)
    if not missing:
        return contract

    fc = contract.setdefault("file_contracts", {})
    gi = contract.setdefault("global_imports", {})

    # Ищем существующий файл моделей или создаём новый
    target_file = None
    for f in files:
        if Path(f).stem in ("models", "data_models"):
            target_file = f
            break
    if target_file is None:
        ext = Path(files[0]).suffix if files else ".py"
        target_file = f"models{ext}"
        if target_file not in files:
            files.append(target_file)
        fc.setdefault(target_file, [])
        gi.setdefault(target_file, [])
        logger.info(f"  📋 A5: создан файл {target_file} для shared data models")

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

            # Проверка: base_module должен быть валидным Python-идентификатором
            # (ловит "from opencv-python import cv2" — дефис невалиден)
            if not base_module.isidentifier():
                from code_context import _PIP_TO_IMPORT
                correct = _PIP_TO_IMPORT.get(base_module.lower())
                if correct:
                    corrected = f"import {correct}"
                    logger.warning(
                        f"  ⚠️  A5 global_imports: '{imp_line}' для {fname} — "
                        f"'{base_module}' невалидный идентификатор → '{corrected}'"
                    )
                    valid_imports.append(corrected)
                else:
                    logger.warning(
                        f"  ⚠️  A5 global_imports: удалён '{imp_line}' для {fname} — "
                        f"'{base_module}' невалидный Python-идентификатор"
                    )
                continue

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


def _validate_import_consistency(
    contract: dict,
    logger: logging.Logger,
) -> dict:
    """Проверяет что cross-file imports в global_imports ссылаются на имена из file_contracts.

    Для каждого `from project_file import Name`:
    - Если Name не найдено в file_contracts целевого файла → удалить import.
    - Если у целевого файла нет контрактов вовсе → оставить (неполный A5).
    """
    fc = contract.get("file_contracts", {})
    gi = contract.get("global_imports", {})
    if not fc or not gi:
        return contract

    # stem → filename маппинг
    file_stems: dict[str, str] = {Path(f).stem: f for f in fc}
    # stem → set(defined names) из file_contracts
    defined_names: dict[str, set[str]] = {}
    for fname, items in fc.items():
        stem = Path(fname).stem
        names: set[str] = set()
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    n = item.get("name", "")
                    if n:
                        names.add(n)
        defined_names[stem] = names

    cleaned_gi: dict[str, list[str]] = {}
    for fname, imports in gi.items():
        if not isinstance(imports, list):
            cleaned_gi[fname] = imports
            continue
        valid: list[str] = []
        for imp_line in imports:
            parsed = _parse_import_line(imp_line)
            if parsed is None:
                valid.append(imp_line)
                continue
            source_stem, imported_names = parsed
            # Только cross-file project imports
            if source_stem not in file_stems:
                valid.append(imp_line)
                continue
            # Если у целевого файла нет контрактов — оставляем (неполный A5)
            if not defined_names.get(source_stem):
                valid.append(imp_line)
                continue
            # Проверяем наличие каждого имени
            valid_names = [n for n in imported_names if n in defined_names[source_stem]]
            invalid_names = [n for n in imported_names if n not in defined_names[source_stem]]
            if invalid_names:
                for inv_name in invalid_names:
                    logger.warning(
                        f"  ⚠️  A5 global_imports: удалён '{inv_name}' из '{imp_line}' для {fname} — "
                        f"не определён в file_contracts {file_stems[source_stem]} "
                        f"(доступны: {', '.join(sorted(defined_names[source_stem]))})"
                    )
            if valid_names:
                valid.append(f"from {source_stem} import {', '.join(valid_names)}")
            # Если все имена невалидны — строка не добавляется
        cleaned_gi[fname] = valid

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
                if re.search(rf'\b{re.escape(class_name)}\b', sig):
                    needed_imports[class_name] = source_file

        if not needed_imports:
            continue

        # 3. Проверяем что import ещё не добавлен в global_imports
        existing = gi.get(fname, [])
        if not isinstance(existing, list):
            existing = []

        # Извлекаем уже импортированные имена из строк import
        imported_names = set()
        for imp in existing:
            parsed = _parse_import_line(imp)
            if parsed:
                imported_names.update(parsed[1])
            else:
                # Fallback для 'import X'
                m = re.search(r'import\s+(\w+)', imp)
                if m:
                    imported_names.add(m.group(1))

        for class_name, source_file in needed_imports.items():
            source_stem = Path(source_file).stem
            import_line = f"from {source_stem} import {class_name}"
            if class_name not in imported_names:
                existing.append(import_line)
                imported_names.add(class_name)
                logger.info(f"  📋 A5 global_imports: добавлен '{import_line}' для {fname}")

        gi[fname] = existing

    return contract


def _detect_and_fix_circular_imports(
    contract: dict,
    files: list[str],
    logger: logging.Logger,
) -> dict:
    """Детерминистская проверка циклических зависимостей в A5 global_imports.

    Строит граф из cross-file imports, находит циклы, переносит shared classes
    в models.py для разрыва циклов.
    """
    fc = contract.get("file_contracts", {})
    gi = contract.get("global_imports", {})
    if not fc or not gi:
        return contract

    project_stems = {Path(f).stem for f in files}

    # 1. Строим граф: stem → set(dependency stems)
    graph: dict[str, set[str]] = {Path(f).stem: set() for f in files}
    # (source_stem, imported_name) для каждого файла
    import_details: dict[str, list[tuple[str, str]]] = {}

    for fname, imports in gi.items():
        if not isinstance(imports, list):
            continue
        stem = Path(fname).stem
        graph.setdefault(stem, set())
        import_details.setdefault(stem, [])
        for imp_line in imports:
            parsed = _parse_import_line(imp_line)
            if not parsed:
                continue
            src_stem, names = parsed
            if src_stem in project_stems and src_stem != stem:
                graph[stem].add(src_stem)
                for name in names:
                    import_details[stem].append((src_stem, name))

    # 2. Поиск циклов через DFS (color-based)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {v: WHITE for v in graph}
    cycles: list[list[str]] = []

    def _dfs(u: str, path: list[str]) -> None:
        color[u] = GRAY
        for v in graph.get(u, set()):
            if v not in color:
                continue
            if color[v] == GRAY:
                idx = path.index(v) if v in path else -1
                if idx >= 0:
                    cycles.append(path[idx:] + [v])
            elif color[v] == WHITE:
                _dfs(v, path + [v])
        color[u] = BLACK

    for v in graph:
        if color[v] == WHITE:
            _dfs(v, [v])

    if not cycles:
        return contract

    # 3. Собираем все stems участвующие в циклах
    cycle_stems: set[str] = set()
    for cycle in cycles:
        cycle_stems.update(cycle)

    logger.warning(
        f"  ⚠️  A5: обнаружены циклические зависимости: "
        f"{'; '.join(' → '.join(c) for c in cycles)}"
    )

    # 4. Находим classes, которые импортируются другим файлом цикла
    classes_to_move: dict[str, str] = {}  # class_name → source_stem
    for stem in cycle_stems:
        fname = next((f for f in files if Path(f).stem == stem), None)
        if not fname or fname not in fc:
            continue
        for other_stem in cycle_stems:
            if other_stem == stem:
                continue
            for src_stem, name in import_details.get(other_stem, []):
                if src_stem != stem:
                    continue
                # Проверяем что name — класс в file_contracts
                for item in fc.get(fname, []):
                    if isinstance(item, dict) and item.get("name") == name:
                        sig = item.get("signature", "")
                        if sig.strip().startswith("class "):
                            classes_to_move[name] = stem

    if not classes_to_move:
        logger.info("  ℹ️  Циклы найдены, но нет переносимых классов (циклы через функции).")
        return contract

    # 5. Определяем/создаём models файл
    ext = Path(files[0]).suffix if files else ".py"
    models_file = f"models{ext}"
    models_stem = "models"
    for f in files:
        if Path(f).stem in ("models", "data_models"):
            models_file = f
            models_stem = Path(f).stem
            break
    if models_file not in files:
        files.append(models_file)
    fc.setdefault(models_file, [])
    gi.setdefault(models_file, [])

    # 6. Переносим классы
    moved = 0
    for class_name, source_stem in classes_to_move.items():
        source_file = next((f for f in files if Path(f).stem == source_stem), None)
        if not source_file:
            continue
        # Перемещаем контракт класса
        source_items = fc.get(source_file, [])
        for i, item in enumerate(source_items):
            if isinstance(item, dict) and item.get("name") == class_name:
                fc[models_file].append(source_items.pop(i))
                moved += 1
                break
        # Обновляем global_imports: from source_stem import Class → from models import Class
        new_import = f"from {models_stem} import {class_name}"
        for fkey, imp_list in gi.items():
            if not isinstance(imp_list, list):
                continue
            for idx, imp_line in enumerate(imp_list):
                parsed = _parse_import_line(imp_line)
                if not parsed:
                    continue
                imp_src, imp_names = parsed
                if imp_src != source_stem or class_name not in imp_names:
                    continue
                # Убираем class_name из текущей строки
                remaining = [n for n in imp_names if n != class_name]
                if remaining:
                    gi[fkey][idx] = f"from {imp_src} import {', '.join(remaining)}"
                else:
                    gi[fkey][idx] = ""  # Пометка для удаления
                # Добавляем новый import из models
                if new_import not in gi[fkey]:
                    gi[fkey].append(new_import)
                break
            # Чистим пустые строки
            gi[fkey] = [imp for imp in gi[fkey] if imp]

    # 7. models.py — data-only: удаляем только PROJECT-file imports (не stdlib/pip)
    models_imports = gi.get(models_file, [])
    if isinstance(models_imports, list):
        # stems без самого models
        other_project_stems = project_stems - {models_stem}
        clean = []
        for imp in models_imports:
            parsed = _parse_import_line(imp)
            if parsed and parsed[0] in other_project_stems:
                logger.info(f"  🗑️  Удалён project import из {models_file}: {imp}")
                continue
            clean.append(imp)
        gi[models_file] = clean

    logger.info(
        f"  📋 A5: перенесено {moved} классов в {models_file} для разрыва циклов: "
        f"{', '.join(classes_to_move.keys())}"
    )

    contract["file_contracts"] = fc
    contract["global_imports"] = gi
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
            patch_fc = _parse_if_str(patch.get("file_contracts", {}), dict, {})
            patch_gi = _parse_if_str(patch.get("global_imports", {}), dict, {})

            # Берём контракт для нашего файла — или весь ответ если ключ не совпал
            file_contract = patch_fc.get(fname)
            if file_contract is None:
                file_contract = next(iter(patch_fc.values()), [])
            file_imports = patch_gi.get(fname)
            if file_imports is None:
                file_imports = next(iter(patch_gi.values()), [])

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
    # Post-validation: полный набор валидаций
    contract = _validate_global_imports(
        contract, state.get("architecture", {}), files, logger,
        requirements_path=req_path if req_path.exists() else None,
    )
    contract = _validate_import_consistency(contract, logger)
    contract = _inject_cross_file_imports(contract, logger)
    contract = _detect_and_fix_circular_imports(contract, files, logger)
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
        f"Код разработчика (НЕ прошёл ревью):\n{developer_code[:3000]}\n\n"
        f"Замечания ревьюера (код отклонён из-за этих проблем):\n{feedback[:1500]}\n\n"
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
        patch_fc = _parse_if_str(patch.get("file_contracts", {}), dict, {})
        patch_gi = _parse_if_str(patch.get("global_imports", {}), dict, {})

        file_contract = patch_fc.get(filename) or next(iter(patch_fc.values()), [])
        file_imports  = patch_gi.get(filename) or next(iter(patch_gi.values()), [])

        if file_contract:
            fc[filename] = _parse_if_str(file_contract, list, [])
            gi[filename] = _parse_if_str(file_imports, list, [])
            contract["file_contracts"] = fc
            contract["global_imports"] = gi
            # Post-validation: полный набор валидаций как в phase_generate_api_contract
            files_list = state.get("files", [])
            contract = _validate_global_imports(
                contract, state.get("architecture", {}),
                files_list, logger,
                requirements_path=req_path if req_path.exists() else None,
            )
            contract = _validate_import_consistency(contract, logger)
            contract = _inject_cross_file_imports(contract, logger)
            contract = _detect_and_fix_circular_imports(contract, files_list, logger)
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
        # Детерминистская валидация: cross-file imports ссылаются на реальные имена
        contract = _validate_import_consistency(contract, logger)
        # Детерминистская инъекция: межфайловые импорты (data models и т.п.)
        contract = _inject_cross_file_imports(contract, logger)
        # Детерминистская проверка: циклические зависимости → вынос в models.py
        contract = _detect_and_fix_circular_imports(contract, files_list, logger)
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
        new_contract = _validate_import_consistency(new_contract, logger)
        new_contract = _inject_cross_file_imports(new_contract, logger)
        new_contract = _detect_and_fix_circular_imports(new_contract, files_list, logger)
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

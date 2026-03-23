import logging
import re
import sys
from pathlib import Path


# ─────────────────────────────────────────────
# Детерминистские валидации A5 контракта
# ─────────────────────────────────────────────


def _auto_add_requirement(
    requirements_path: Path, package_name: str, logger: logging.Logger,
    project_stems: set[str] | None = None,
) -> None:
    """Авто-добавляет пакет в requirements.txt если его ещё нет."""
    if not requirements_path or not requirements_path.exists():
        return
    # Не добавляем файлы проекта как pip-пакеты (models, config, utils и т.д.)
    if project_stems and package_name.lower().replace("-", "_") in project_stems:
        return
    # Исправляем невалидные pip-имена (LLM часто пишет import-имя вместо pip-имени)
    from code_context import WRONG_PIP_PACKAGES
    if package_name in WRONG_PIP_PACKAGES:
        correct_pip, _ = WRONG_PIP_PACKAGES[package_name]
        logger.warning(
            f"  ⚠️  _auto_add_requirement: '{package_name}' → '{correct_pip}' "
            f"(невалидный pip-пакет)"
        )
        package_name = correct_pip
    try:
        content = requirements_path.read_text(encoding="utf-8")
    except OSError:
        return
    # Проверяем, не добавлен ли уже (с учётом семейств пакетов типа opencv)
    pkg_lower = package_name.lower()
    pkg_norm = pkg_lower.replace("-", "_")
    # Семейства пакетов, которые конфликтуют друг с другом
    _PKG_FAMILIES: list[set[str]] = [
        {"opencv_python", "opencv_python_headless",
         "opencv_contrib_python", "opencv_contrib_python_headless"},
    ]
    pkg_family = {pkg_norm}
    for family in _PKG_FAMILIES:
        if pkg_norm in family:
            pkg_family = family
            break
    for line in content.splitlines():
        line_pkg = re.split(r"[=<>~!\[;]", line.strip())[0].strip().lower()
        line_norm = line_pkg.replace("-", "_")
        if line_norm == pkg_norm or line_norm in pkg_family:
            return  # Уже есть (или есть вариант из того же семейства)
    # Добавляем
    if not content.endswith("\n"):
        content += "\n"
    requirements_path.write_text(content + package_name + "\n", encoding="utf-8")
    logger.info(f"  📦  Авто-добавлен '{package_name}' в requirements.txt")


def validate_requirements_txt(requirements_path: Path, logger: logging.Logger) -> None:
    """Проверяет requirements.txt на невалидные pip-пакеты и исправляет их."""
    if not requirements_path or not requirements_path.exists():
        return
    from code_context import WRONG_PIP_PACKAGES
    try:
        content = requirements_path.read_text(encoding="utf-8")
    except OSError:
        return
    lines = content.splitlines()
    changed = False
    new_lines: list[str] = []
    seen_normalized: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue
        pkg = re.split(r"[=<>~!\[;]", stripped)[0].strip()
        if pkg in WRONG_PIP_PACKAGES:
            correct_pip, _ = WRONG_PIP_PACKAGES[pkg]
            logger.warning(
                f"  ⚠️  requirements.txt: '{pkg}' → '{correct_pip}' (невалидный pip-пакет)"
            )
            # Заменяем на правильный, если его ещё нет
            norm = correct_pip.lower().replace("-", "_")
            if norm not in seen_normalized:
                new_lines.append(correct_pip)
                seen_normalized.add(norm)
            changed = True
            continue
        norm = pkg.lower().replace("-", "_")
        if norm in seen_normalized:
            changed = True
            continue  # Дубликат
        seen_normalized.add(norm)
        new_lines.append(line)
    if changed:
        requirements_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        logger.info("  ✅ requirements.txt: невалидные пакеты исправлены")


def _parse_import_line(imp_line: str) -> tuple[str, list[str]] | None:
    """Парсит строку импорта. Возвращает (source_stem, [imported_names]) или None.

    Поддерживает: 'from X import A', 'from X import A, B', 'from X import A as Z'.
    """
    if not isinstance(imp_line, str):
        return None
    m = re.match(r"from\s+([\w.]+)\s+import\s+(.+)", imp_line.strip())
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
    # Нормализация name: "ClassName.method_name" → "method_name"
    # (LLM часто возвращает полные пути, но checks ищет только имя метода)
    for fname, items in contract.get("file_contracts", {}).items():
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and "name" in item:
                name = item["name"]
                if "." in name and not name.startswith("__"):
                    item["name"] = name.rsplit(".", 1)[1]

    # Удаляем записи с не-ASCII именами (LLM может вернуть русские имена из A2)
    contract = _remove_non_ascii_entries(contract)
    # Удаляем невалидные ключи (директории без расширения: "models/", "data/")
    _VALID_FILE_RE = re.compile(r'^[\w/\-\.]+\.\w+$')
    fc_raw = contract.get("file_contracts", {})
    if isinstance(fc_raw, dict):
        invalid_keys = [k for k in fc_raw if not _VALID_FILE_RE.match(k) or ".." in k]
        for k in invalid_keys:
            del fc_raw[k]
    gi_raw = contract.get("global_imports", {})
    if isinstance(gi_raw, dict):
        invalid_gi = [k for k in gi_raw if not _VALID_FILE_RE.match(k) or ".." in k]
        for k in invalid_gi:
            del gi_raw[k]
    # Удаляем конфликты module vs package: X.py не может существовать рядом с X/
    fc_clean = contract.get("file_contracts", {})
    if isinstance(fc_clean, dict):
        # Собираем все пакеты (каталоги из путей вида "X/file.py")
        package_dirs: set[str] = set()
        for k in fc_clean:
            parts = k.split("/")
            if len(parts) > 1:
                package_dirs.add(parts[0])
        # Удаляем X.py если X/ — пакет
        conflict_keys = [
            k for k in fc_clean
            if "/" not in k and k.endswith(".py") and k[:-3] in package_dirs
        ]
        for k in conflict_keys:
            import logging as _clog
            _clog.getLogger(__name__).warning(
                f"  ⚠️  A5: удалён '{k}' — конфликт с пакетом '{k[:-3]}/' (module vs package)"
            )
            del fc_clean[k]
            gi_clean = contract.get("global_imports", {})
            if isinstance(gi_clean, dict):
                gi_clean.pop(k, None)
    # Чистим остаточные garbage tokens из сигнатур (если LLM-level strip не применён)
    _GRB_RE = re.compile(r"<[｜|][\w▁]+[｜|]>")
    fc = contract.get("file_contracts", {})
    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            for key in ("signature", "name", "description", "implementation_hints"):
                val = item.get(key, "")
                if isinstance(val, str) and _GRB_RE.search(val):
                    val = re.sub(r"(\w+)" + r"<[｜|][\w▁]+[｜|]>" + r"\1", r"\1", val)
                    val = _GRB_RE.sub("", val)
                    # Исправляем сломанные аннотации: ") - str" → ") -> str"
                    val = re.sub(r"\)\s*-\s+(\w)", r") -> \1", val)
                    item[key] = val
            # Нормализуем class-сигнатуры: "class X: ... " → "class X"
            # LLM пишет "class X: ..." чтобы показать "тут будут методы", но это
            # ломает скелет-генерацию и ast.parse
            sig = item.get("signature", "")
            if isinstance(sig, str) and sig.strip().startswith("class "):
                sig = re.sub(r"\s*:\s*\.{3,}\s*$", "", sig)   # "class X: ..." → "class X"
                sig = re.sub(r"\s*\.{3,}\s*$", "", sig)        # "class X ..." → "class X"
                sig = sig.rstrip(": ")                          # "class X:" → "class X"
                item["signature"] = sig
    return contract


def _remove_non_ascii_entries(contract: dict) -> dict:
    """Удаляет из file_contracts записи с не-ASCII именами (например 'class Видео')."""
    import logging as _log
    _logger = _log.getLogger(__name__)
    fc = contract.get("file_contracts", {})
    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        cleaned = []
        for item in items:
            if not isinstance(item, dict):
                cleaned.append(item)
                continue
            name = item.get("name", "")
            if name and not name.isascii():
                _logger.warning(f"  A5: удалена запись с не-ASCII именем '{name}' из {fname}")
                continue
            cleaned.append(item)
        fc[fname] = cleaned
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
    # CamelCase-версии имён моделей для нечувствительного к регистру сравнения
    camel_to_original: dict[str, str] = {}
    for mn in model_names:
        camel = "".join(part.capitalize() for part in mn.split("_"))
        camel_to_original[camel.lower()] = mn  # Camera→camera, Vehicle→vehicle

    defined_names: set[str] = set()
    for fname, items in contract.get("file_contracts", {}).items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            item_name = item.get("name", "")
            sig = item.get("signature", "")
            # Совпадение по name (точное ИЛИ CamelCase) или по "class ..." в signature
            if item_name in model_names:
                defined_names.add(item_name)
            elif item_name.lower() in camel_to_original:
                defined_names.add(camel_to_original[item_name.lower()])
            for mn in model_names:
                camel = "".join(part.capitalize() for part in mn.split("_"))
                if f"class {mn}" in sig or f"class {camel}" in sig:
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
        and dm["name"].isidentifier() and dm["name"].isascii()
    }

    for model_name in missing:
        # Пропускаем не-ASCII имена (русские из A2) и невалидные идентификаторы
        if not model_name.isascii() or not model_name.replace("_", "a").isidentifier():
            logger.info(f"  📋 A5: пропущена не-ASCII data model '{model_name}' из A2")
            continue
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

        # CamelCase для имён классов: camera → Camera, license_plate → LicensePlate
        # Если имя уже CamelCase (без подчёркиваний, с заглавной) — оставить как есть
        if "_" not in model_name and model_name[0].isupper():
            class_name = model_name
        else:
            class_name = "".join(part.capitalize() for part in model_name.split("_"))
        entry = {
            "name": class_name,
            "signature": f"class {class_name}",
            "description": f"Data model из A2.{field_desc}",
            "required": True,
            "called_by": [],
        }
        fc.setdefault(target_file, []).append(entry)
        logger.info(f"  📋 A5: добавлен класс {class_name} в контракт файла {target_file} (из data_models A2: '{model_name}')")

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
    # Модули проекта (без расширения) + корневые package-директории
    project_modules = {Path(f).stem for f in project_files}
    for f in project_files:
        parts = Path(f).parts
        if len(parts) > 1:
            project_modules.add(parts[0])  # models/ → "models"
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
        from code_context import parse_requirements
        pip_names.update(parse_requirements(requirements_path))

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
                # Bare name без import/from — мусор от LLM, удаляем
                logger.warning(
                    f"  ⚠️  A5 global_imports: удалён '{imp_line}' для {fname} "
                    f"(не является валидным import-выражением)"
                )
                continue
            base_module = (m.group(1) or m.group(2)).split(".")[0]

            # Проверка: base_module должен быть валидным Python-идентификатором
            # (ловит "from opencv-python import cv2" — дефис невалиден)
            if not base_module.isidentifier():
                from code_context import PIP_TO_IMPORT
                correct = PIP_TO_IMPORT.get(base_module.lower())
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

            # Проверка: невалидный pip-пакет как import-имя
            # (ловит "import opencv", "from opencv import ..." — opencv не Python-модуль)
            from code_context import WRONG_PIP_PACKAGES
            if base_module in WRONG_PIP_PACKAGES:
                correct_pip, correct_import = WRONG_PIP_PACKAGES[base_module]
                if base_module != correct_import:
                    corrected = imp_line.replace(base_module, correct_import, 1)
                    logger.warning(
                        f"  ⚠️  A5 global_imports: '{imp_line}' для {fname} → "
                        f"'{corrected}' ('{base_module}' невалидный модуль)"
                    )
                    valid_imports.append(corrected)
                else:
                    valid_imports.append(imp_line)
                if requirements_path:
                    _auto_add_requirement(requirements_path, correct_pip, logger)
                continue

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
            # Пакет не найден — определяем: это pip-пакет или фантомный project import?
            # Признаки project import (а не pip): snake_case, нет дефисов,
            # выглядит как "from some_module import ClassName"
            looks_like_project = (
                base_module.isidentifier()
                and "_" in base_module
                and base_module == base_module.lower()
                and not any(c.isdigit() for c in base_module[:3])
            )
            if looks_like_project:
                # Фантомный project import — файла нет в проекте → удаляем
                logger.warning(
                    f"  ⚠️  A5 global_imports: удалён '{imp_line}' для {fname} "
                    f"('{base_module}' выглядит как модуль проекта, но файла нет)"
                )
                continue
            # pip-пакет → авто-добавляем в requirements.txt
            # НЕ добавляем если имя совпадает с файлом проекта (project_modules уже проверены выше)
            if (requirements_path and base_module.isidentifier()
                    and base_lower not in {pm.lower() for pm in project_modules}):
                _auto_add_requirement(requirements_path, base_module, logger)
                pip_names.add(base_lower)
                pip_names.add(base_normalized)
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
    src_path: Path | None = None,
) -> dict:
    """Проверяет что cross-file imports в global_imports ссылаются на имена из file_contracts.

    Для каждого `from project_file import Name`:
    - Если Name не найдено в file_contracts целевого файла → удалить import.
    - Если у целевого файла нет контрактов вовсе → оставить (неполный A5).

    Дополнительно: если src_path доступен, извлекает реальные top-level имена из исходников
    (class/def), чтобы не удалять импорты, которые есть в коде но отсутствуют в контракте.
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

    # Дополняем реальными top-level именами из исходников (class/def)
    if src_path:
        import ast as _ast
        for fname in fc:
            fpath = src_path / fname
            if not fpath.exists():
                continue
            stem = Path(fname).stem
            try:
                tree = _ast.parse(fpath.read_text(encoding="utf-8"))
                for node in _ast.iter_child_nodes(tree):
                    if isinstance(node, (_ast.ClassDef, _ast.FunctionDef, _ast.AsyncFunctionDef)):
                        defined_names.setdefault(stem, set()).add(node.name)
            except (SyntaxError, OSError, UnicodeDecodeError):
                pass

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
            # Проверяем наличие каждого имени, сохраняя оригинальные части (с as-алиасами)
            m_imp = re.match(r"from\s+[\w.]+\s+import\s+(.+)", imp_line.strip())
            raw_parts = [p.strip() for p in m_imp.group(1).split(",")] if m_imp else []
            valid_parts = []
            for part in raw_parts:
                if not part.strip():
                    continue
                name = part.split()[0].strip()
                if name in defined_names[source_stem]:
                    valid_parts.append(part)
                else:
                    logger.warning(
                        f"  ⚠️  A5 global_imports: удалён '{name}' из '{imp_line}' для {fname} — "
                        f"не определён в file_contracts {file_stems[source_stem]} "
                        f"(доступны: {', '.join(sorted(defined_names[source_stem]))})"
                    )
            if valid_parts:
                valid.append(f"from {source_stem} import {', '.join(valid_parts)}")
            # Если все имена невалидны — строка не добавляется
        cleaned_gi[fname] = valid

    contract["global_imports"] = cleaned_gi
    return contract


def _sanitize_implementation_hints(
    contract: dict,
    logger: logging.Logger,
) -> dict:
    """Убирает из implementation_hints ссылки на несуществующие имена.

    Если hints файла A ссылаются на 'VideoStreamProcessor' но в file_contracts
    файла video_stream_processor.py определён только 'process_frame' → заменяет
    'VideoStreamProcessor' на 'process_frame' (или убирает если нет однозначной замены).
    """
    fc = contract.get("file_contracts", {})
    if not fc:
        return contract

    # stem → set(defined names) из ВСЕХ file_contracts
    all_defined: dict[str, set[str]] = {}
    for fname, items in fc.items():
        stem = Path(fname).stem
        names: set[str] = set()
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    n = item.get("name", "")
                    if n:
                        names.add(n)
        all_defined[stem] = names

    # Все определённые имена (flat set)
    all_names_flat: set[str] = set()
    for names in all_defined.values():
        all_names_flat.update(names)

    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            hints = item.get("implementation_hints", "")
            if not hints:
                continue
            # Ищем CamelCase имена в hints, которые похожи на имена из file_contracts
            # но не существуют ни в одном file_contract
            for word in re.findall(r"\b([A-Z][a-zA-Z0-9]+)\b", hints):
                if word in all_names_flat:
                    continue  # Это имя реально существует
                # Проверяем: это имя похоже на stem файла?
                # VideoStreamProcessor → video_stream_processor
                snake = re.sub(r"(?<!^)(?=[A-Z])", "_", word).lower()
                if snake in all_defined and all_defined[snake]:
                    # Имя совпадает с файлом, но класс не определён
                    available = sorted(all_defined[snake])
                    old_hints = hints
                    hints = re.sub(rf"\b{re.escape(word)}\b", available[0], hints)
                    if hints != old_hints:
                        logger.info(
                            f"  🔧 A5 hints: заменено '{word}' → '{available[0]}' в {fname} "
                            f"('{word}' не определён, доступно: {', '.join(available)})"
                        )
            item["implementation_hints"] = hints

    return contract


# Типы из typing → import line
_TYPING_TYPES = {
    "List": "List", "Dict": "Dict", "Tuple": "Tuple", "Set": "Set",
    "Optional": "Optional", "Union": "Union", "Any": "Any",
    "Callable": "Callable", "Iterator": "Iterator", "Generator": "Generator",
    "Sequence": "Sequence", "Mapping": "Mapping", "Iterable": "Iterable",
}
# Prefix → import line (для np.ndarray, pd.DataFrame и т.д.)
_PREFIX_IMPORTS = {
    "np": "import numpy as np",
    "pd": "import pandas as pd",
    "tf": "import tensorflow as tf",
    "plt": "import matplotlib.pyplot as plt",
    "cv2": "import cv2",
}


def _inject_signature_type_imports(
    contract: dict,
    logger: logging.Logger,
) -> dict:
    """Авто-инжектирует import-строки для типов, используемых в сигнатурах A5.

    Если сигнатура содержит 'np.ndarray' → добавляет 'import numpy as np'.
    Если содержит 'List[...]' → добавляет 'from typing import List'.
    """
    fc = contract.get("file_contracts", {})
    gi = contract.setdefault("global_imports", {})

    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        file_imports = gi.setdefault(fname, [])
        existing_text = " ".join(file_imports)
        needed_typing: set[str] = set()

        for item in items:
            if not isinstance(item, dict):
                continue
            sig = item.get("signature", "")
            if not sig:
                continue

            # Проверяем typing types
            for type_name in _TYPING_TYPES:
                if re.search(rf"\b{type_name}\b", sig):
                    needed_typing.add(type_name)

            # Проверяем prefix-based imports (np.X, pd.X и т.д.)
            for prefix, imp_line in _PREFIX_IMPORTS.items():
                if f"{prefix}." in sig and imp_line not in existing_text:
                    if imp_line not in file_imports:
                        file_imports.append(imp_line)
                        logger.info(f"  📎 A5: авто-добавлен '{imp_line}' для {fname} (из сигнатуры)")

        # Собираем typing imports
        if needed_typing:
            # Проверяем что уже есть
            existing_typing: set[str] = set()
            for imp in file_imports:
                m = re.match(r"from\s+typing\s+import\s+(.+)", imp)
                if m:
                    existing_typing.update(n.strip().split()[0] for n in m.group(1).split(","))
            new_typing = needed_typing - existing_typing
            if new_typing:
                # Удаляем старую typing строку и создаём новую объединённую
                all_typing = sorted(existing_typing | new_typing)
                new_line = f"from typing import {', '.join(all_typing)}"
                file_imports[:] = [
                    imp for imp in file_imports
                    if not re.match(r"from\s+typing\s+import", imp)
                ]
                file_imports.insert(0, new_line)
                logger.info(f"  📎 A5: обновлён typing import для {fname}: {', '.join(new_typing)}")

    return contract


def _inject_requirements_imports(
    contract: dict,
    requirements_path: Path | None,
    logger: logging.Logger,
) -> dict:
    """Инжектирует imports пакетов из requirements.txt если они упоминаются в hints/description.

    Если implementation_hints или description содержат имя пакета (cv2, numpy, requests и т.п.),
    а global_imports не содержит соответствующий import — добавляет его.
    """
    if not requirements_path or not requirements_path.exists():
        return contract
    from code_context import PIP_TO_IMPORT
    fc = contract.get("file_contracts", {})
    gi = contract.setdefault("global_imports", {})

    # Собираем pip → import mapping из requirements.txt
    pkg_to_import: dict[str, str] = {}  # import_name → import_line
    try:
        for line in requirements_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            pkg = re.split(r"[=<>~!\[]", line)[0].strip().lower()
            pkg_norm = pkg.replace("-", "_")
            # Ищем правильное имя импорта
            import_name = PIP_TO_IMPORT.get(pkg, PIP_TO_IMPORT.get(pkg_norm, pkg_norm))
            if import_name and import_name.isidentifier():
                pkg_to_import[import_name] = f"import {import_name}"
    except Exception as exc:
        logger.warning(f"⚠️  Ошибка чтения requirements.txt для inject_requirements_imports: {exc}")
        return contract

    if not pkg_to_import:
        return contract

    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        # Собираем текст hints + description для поиска
        search_parts: list[str] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            sig = item.get("signature", "")
            if sig.strip().startswith("class "):
                continue
            search_parts.append(item.get("implementation_hints", ""))
            search_parts.append(item.get("description", ""))
            search_parts.append(sig)
        if not search_parts:
            continue
        search_text = " ".join(search_parts).lower()

        existing = gi.setdefault(fname, [])

        for import_name, import_line in pkg_to_import.items():
            # Проверяем упоминание пакета в hints/description (word boundary, не substring)
            if (len(import_name) >= 3
                    and re.search(rf'\b{re.escape(import_name.lower())}\b', search_text)
                    and import_line not in existing):
                existing.append(import_line)
                logger.info(f"  📎 A5 global_imports: авто-добавлен '{import_line}' для {fname} (из requirements + hints)")

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

    # Слова из docstring и Python builtins — НЕ являются именами классов
    _DOCSTRING_NOISE = {
        "Args", "Returns", "Raises", "Yields", "Note", "Notes", "Example",
        "Examples", "Attributes", "References", "See", "Also", "Warnings",
        "Todo", "Param", "Params", "Return", "Keyword",
    }
    _PYTHON_KEYWORDS = {
        "True", "False", "None", "and", "or", "not", "is", "in", "if", "else",
        "elif", "for", "while", "break", "continue", "pass", "def", "class",
        "return", "yield", "import", "from", "as", "with", "try", "except",
        "finally", "raise", "del", "global", "nonlocal", "assert", "lambda",
    }

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
                if class_name and class_name not in _DOCSTRING_NOISE and class_name not in _PYTHON_KEYWORDS:
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
            # Очищаем сигнатуру от docstring — оставляем только первую строку (def ...)
            sig_first_line = sig.split("\n")[0] if "\n" in sig else sig
            # Ищем ссылки на известные классы в сигнатуре, описании и hints
            hints = item.get("implementation_hints", "")
            search_text = f"{sig_first_line} {desc} {hints}"
            for class_name, source_file in class_to_file.items():
                if source_file == fname:
                    continue  # Класс определён в этом же файле
                # Пропускаем короткие/общие имена — слишком много false positives
                if len(class_name) < 4 or class_name in {
                    "Error", "Data", "Config", "Image", "Result", "Response",
                    "Request", "Event", "Model", "Base", "Item", "Type", "Node",
                    "Info", "State", "Action", "Status", "Value", "Entry", "Record",
                    "Task", "Message", "Handler", "Manager", "Service", "Client",
                    "Server", "Worker", "Logger", "Filter", "Parser", "Builder",
                }:
                    # Для общих имён — проверяем только сигнатуру (без desc/hints)
                    if not re.search(rf'\b{re.escape(class_name)}\b', sig_first_line):
                        continue
                if re.search(rf'\b{re.escape(class_name)}\b', search_text):
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


# Встроенные типы Python + частые неклассовые имена — не нужно определять
_BUILTIN_TYPES = {
    "int", "float", "str", "bool", "bytes", "None", "object", "type",
    "list", "dict", "set", "tuple", "frozenset", "complex", "bytearray",
    "memoryview", "range", "slice", "property", "classmethod", "staticmethod",
    "Exception", "ValueError", "TypeError", "KeyError", "IndexError",
    "RuntimeError", "IOError", "OSError", "FileNotFoundError",
    "AttributeError", "ImportError", "StopIteration", "NotImplementedError",
}


def _validate_signature_types(
    contract: dict,
    files: list[str],
    logger: logging.Logger,
) -> dict:
    """Проверяет что все типы (CamelCase) в сигнатурах A5 определены в file_contracts.

    Если тип не определён нигде → создаёт запись class в models.py.
    Также очищает called_by от ссылок на несуществующие классы.
    """
    fc = contract.get("file_contracts", {})
    gi = contract.setdefault("global_imports", {})

    # 1. Собираем все определённые классы: name → file
    defined_classes: dict[str, str] = {}
    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            sig = item.get("signature", "")
            if sig.strip().startswith("class "):
                defined_classes[item.get("name", "")] = fname

    # 2. Сканируем все сигнатуры на CamelCase типы
    undefined_types: dict[str, set[str]] = {}  # type_name → set of files that use it
    _skip = set(_TYPING_TYPES) | _BUILTIN_TYPES | set(defined_classes)
    _skip |= set(_PREFIX_IMPORTS)  # np, pd, tf и т.д. — не типы

    # Слова из docstring-стиля — не являются типами
    _docstring_noise = {
        "Args", "Returns", "Raises", "Yields", "Note", "Notes", "Example",
        "Examples", "Attributes", "References", "Warnings", "Todo",
        "Param", "Params", "Return", "Keyword", "True", "False",
    }
    _skip |= _docstring_noise

    # Типы, импортированные из pip-пакетов (не project files) — не нужно определять
    project_stems = {Path(f).stem for f in files}
    for _fname_gi, _imports_gi in gi.items():
        if not isinstance(_imports_gi, list):
            continue
        for _imp in _imports_gi:
            if not isinstance(_imp, str):
                continue
            parsed = _parse_import_line(_imp)
            if parsed:
                src_stem, names = parsed
                if src_stem not in project_stems:
                    _skip.update(names)  # e.g. Flask, Api, Resource from flask
            else:
                m = re.match(r"import\s+(\w+)(?:\s+as\s+(\w+))?", _imp)
                if m:
                    _skip.add(m.group(2) or m.group(1))

    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            sig = item.get("signature", "")
            if sig.strip().startswith("class "):
                continue
            # Используем только первую строку сигнатуры (def ...), не docstring
            sig_line = sig.split("\n")[0] if "\n" in sig else sig
            # Извлекаем CamelCase слова (начинаются с заглавной, ≥2 символа)
            for m in re.finditer(r'\b([A-Z][a-zA-Z0-9]+)\b', sig_line):
                type_name = m.group(1)
                if type_name not in _skip:
                    undefined_types.setdefault(type_name, set()).add(fname)

    if not undefined_types:
        return contract

    # 3. Создаём undefined типы в models.py
    ext = Path(files[0]).suffix if files else ".py"
    models_file = None
    for f in files:
        if Path(f).stem in ("models", "data_models"):
            models_file = f
            break
    if models_file is None:
        models_file = f"models{ext}"
        if models_file not in files:
            files.append(models_file)
        fc.setdefault(models_file, [])
        gi.setdefault(models_file, [])
        logger.info(f"  📋 A5: создан файл {models_file} для undefined типов из сигнатур")

    existing_names = {
        item.get("name", "")
        for item in fc.get(models_file, [])
        if isinstance(item, dict)
    }

    for type_name, used_in_files in undefined_types.items():
        if type_name in existing_names:
            continue
        entry = {
            "name": type_name,
            "signature": f"class {type_name}",
            "description": f"Data class для типа {type_name} (авто-создан — тип используется в сигнатурах, но не определён)",
            "required": True,
            "called_by": [],
        }
        fc.setdefault(models_file, []).append(entry)
        existing_names.add(type_name)
        logger.warning(
            f"  ⚠️  A5: тип '{type_name}' используется в сигнатурах ({', '.join(sorted(used_in_files))}), "
            f"но не определён → добавлен как класс в {models_file}"
        )

    # 4. Очищаем called_by от ссылок на несуществующие классы
    all_names = set()
    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict):
                all_names.add(item.get("name", ""))
    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            called_by = item.get("called_by", [])
            if not isinstance(called_by, list):
                continue
            cleaned = []
            for ref in called_by:
                if not isinstance(ref, str):
                    cleaned.append(ref)
                    continue
                # "ClassName.method" → проверяем ClassName
                parts = ref.split(".")
                if len(parts) >= 2 and parts[0] not in all_names:
                    logger.warning(
                        f"  ⚠️  A5: called_by '{ref}' для {item.get('name', '?')} в {fname} — "
                        f"класс '{parts[0]}' не определён в контракте → удалён"
                    )
                    continue
                cleaned.append(ref)
            item["called_by"] = cleaned

    return contract


def _dedup_global_imports(
    contract: dict,
    logger: logging.Logger,
) -> dict:
    """Дедупликация global_imports: удаляет семантически одинаковые импорты.

    Правила:
    - Точные дубликаты удаляются.
    - 'from X import Y' + 'import X' → оставляем 'from X import Y' (более специфичный).
    - 'from X import Y' + 'from X import Z' → оставляем оба (разные имена).
    """
    gi = contract.get("global_imports", {})
    if not gi:
        return contract
    for fname, imports in gi.items():
        if not isinstance(imports, list):
            continue
        seen: set[str] = set()
        # Собираем базовые модули из 'from X import Y' (если есть — 'import X' избыточен)
        from_modules: set[str] = set()
        for imp in imports:
            if isinstance(imp, str):
                m = re.match(r"from\s+(\S+)\s+import", imp.strip())
                if m:
                    from_modules.add(m.group(1))
        deduped: list[str] = []
        for imp in imports:
            if not isinstance(imp, str):
                deduped.append(imp)
                continue
            stripped = imp.strip()
            if stripped in seen:
                continue
            # 'import X' избыточен если уже есть 'from X import ...'
            m_bare = re.match(r"import\s+(\S+)$", stripped)
            if m_bare and m_bare.group(1) in from_modules:
                logger.debug(f"  A5 dedup: '{stripped}' для {fname} — есть from-импорт")
                continue
            seen.add(stripped)
            deduped.append(imp)
        if len(deduped) < len(imports):
            logger.info(
                f"  A5 dedup imports: {fname}: {len(imports)} → {len(deduped)}"
            )
        gi[fname] = deduped
    return contract


def _dedup_cross_file_classes(
    contract: dict,
    logger: logging.Logger,
) -> dict:
    """Удаляет дублированные классы из file_contracts.

    Если один класс (по name) определён в нескольких файлах,
    оставляем его в файле с наилучшим соответствием (по stem name),
    или в файле с наибольшим количеством полей/методов.
    Пример: Camera в camera.py и models.py → оставляем в camera.py.
    """
    fc = contract.get("file_contracts", {})
    # Маппинг class_name → [(fname, item, field_count)]
    class_locations: dict[str, list[tuple[str, dict, int]]] = {}
    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            sig = item.get("signature", "")
            if sig.strip().startswith("class "):
                name = item.get("name", "")
                if name:
                    # Считаем "richness" — длина сигнатуры как прокси
                    richness = len(sig)
                    class_locations.setdefault(name, []).append((fname, item, richness))

    for class_name, locations in class_locations.items():
        if len(locations) <= 1:
            continue
        # Выбираем лучший файл: сначала по stem match, затем по richness
        best_fname = locations[0][0]
        best_score = -1
        for fname, item, richness in locations:
            stem = Path(fname).stem.lower()
            score = richness
            # Бонус если stem совпадает с именем класса (camera.py для Camera)
            if stem == class_name.lower():
                score += 10000
            # Бонус если это не models.py (предпочитаем бизнес-файл)
            if stem != "models":
                score += 100
            if score > best_score:
                best_score = score
                best_fname = fname
        # Удаляем дубли из других файлов
        for fname, item, _ in locations:
            if fname != best_fname:
                fc[fname] = [i for i in fc[fname] if i is not item]
                logger.info(
                    f"  📋 A5 dedup: удалён дубль класса '{class_name}' из {fname} "
                    f"(оставлен в {best_fname})"
                )

    return contract


def _build_import_graph(
    gi: dict[str, list[str]],
    files: list[str],
    project_stems: set[str],
) -> tuple[dict[str, set[str]], dict[str, list[tuple[str, str]]]]:
    """Строит граф зависимостей из global_imports A5. Возвращает (graph, import_details)."""
    graph: dict[str, set[str]] = {Path(f).stem: set() for f in files}
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
    return graph, import_details


def _find_graph_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """DFS-поиск циклов в графе зависимостей (color-based)."""
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
    return cycles


def _move_classes_to_models(
    classes_to_move: dict[str, str],
    fc: dict, gi: dict,
    files: list[str],
    project_stems: set[str],
    models_file: str, models_stem: str,
    logger: logging.Logger,
) -> int:
    """Переносит классы из file_contracts в models.py, обновляет global_imports. Возвращает кол-во перемещённых."""
    moved = 0
    for class_name, source_stem in classes_to_move.items():
        source_file = next((f for f in files if Path(f).stem == source_stem), None)
        if not source_file:
            continue
        if source_file == models_file:
            continue  # Уже в models — не перемещаем сами в себя
        if source_file not in fc:
            continue
        source_items = fc[source_file]
        for i, item in enumerate(source_items):
            if isinstance(item, dict) and item.get("name") == class_name:
                fc[models_file].append(source_items.pop(i))
                moved += 1
                break
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
                remaining = [n for n in imp_names if n != class_name]
                if remaining:
                    gi[fkey][idx] = f"from {imp_src} import {', '.join(remaining)}"
                else:
                    gi[fkey][idx] = ""
                if new_import not in gi[fkey]:
                    gi[fkey].append(new_import)
                break
            gi[fkey] = [imp for imp in gi[fkey] if imp]
    return moved


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
    graph, import_details = _build_import_graph(gi, files, project_stems)
    cycles = _find_graph_cycles(graph)
    if not cycles:
        return contract

    cycle_stems: set[str] = set()
    for cycle in cycles:
        cycle_stems.update(cycle)

    logger.warning(
        f"  ⚠️  A5: обнаружены циклические зависимости: "
        f"{'; '.join(' → '.join(c) for c in cycles)}"
    )

    # Находим classes/functions, которые импортируются другим файлом цикла
    classes_to_move: dict[str, str] = {}
    funcs_in_cycle: list[tuple[str, str, str]] = []
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
                for item in fc.get(fname, []):
                    if isinstance(item, dict) and item.get("name") == name:
                        sig = item.get("signature", "")
                        if sig.strip().startswith("class "):
                            classes_to_move[name] = stem
                        else:
                            funcs_in_cycle.append((name, stem, other_stem))

    if not classes_to_move:
        if funcs_in_cycle:
            logger.warning(
                f"  ⚠️  Циклические imports через функции: "
                + ", ".join(f"{n} ({s}→{d})" for n, s, d in funcs_in_cycle)
                + " — удаляю кросс-импорт из одного направления"
            )
            for name, from_stem, to_stem in funcs_in_cycle:
                # to_stem импортирует name из from_stem — удаляем этот import
                importer_file = next((f for f in files if Path(f).stem == to_stem), None)
                if importer_file and importer_file in gi:
                    cleaned = []
                    for imp in gi[importer_file]:
                        parsed = _parse_import_line(imp)
                        if parsed and parsed[0] == from_stem and name in parsed[1]:
                            remaining = [n for n in parsed[1] if n != name]
                            if remaining:
                                cleaned.append(f"from {parsed[0]} import {', '.join(remaining)}")
                            logger.info(f"    → Удалён import '{name}' из {importer_file}")
                            continue
                        cleaned.append(imp)
                    gi[importer_file] = cleaned
            contract["global_imports"] = gi
            return contract
        logger.info("  ℹ️  Циклы найдены, но нет переносимых элементов.")
        return contract

    # Определяем/создаём models файл
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

    moved = _move_classes_to_models(classes_to_move, fc, gi, files, project_stems,
                                     models_file, models_stem, logger)

    # models.py — data-only: удаляем только PROJECT-file imports (не stdlib/pip)
    models_imports = gi.get(models_file, [])
    if isinstance(models_imports, list):
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


# ─────────────────────────────────────────────
# Проверки полноты A5 контракта
# ─────────────────────────────────────────────


def _validate_class_methods(contract: dict, logger: logging.Logger) -> dict:
    """Проверяет что классы в A5 имеют публичные методы (не только __init__).

    Если класс содержит только __init__ — логирует WARNING.
    Не блокирует (auto-fix невозможен), но информирует.
    """
    fc = contract.get("file_contracts", {})
    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        # Собираем классы и их методы
        classes: dict[str, list[str]] = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            sig = item.get("signature", "")
            name = item.get("name", "")
            if sig.startswith("class "):
                classes.setdefault(name, [])
            elif "(self" in sig or "(cls" in sig:
                # Метод класса — находим к какому классу относится
                for cls_name in classes:
                    if name.startswith(cls_name + ".") or any(
                        name == m for m in [name]
                    ):
                        classes[cls_name].append(name)
                        break
                else:
                    # Метод без привязки к классу — привяжем к последнему
                    if classes:
                        last_cls = list(classes.keys())[-1]
                        classes[last_cls].append(name)
        # Проверяем: есть ли классы без методов
        for cls_name, methods in classes.items():
            non_init = [m for m in methods if m != "__init__"]
            if not non_init:
                logger.warning(
                    f"  ⚠️  A5: класс '{cls_name}' в {fname} не имеет публичных методов "
                    f"(только __init__). Другие файлы не смогут вызвать его методы."
                )
    return contract


def _validate_cross_file_calls(contract: dict, logger: logging.Logger) -> dict:
    """Проверяет консистентность вызовов между файлами в implementation_hints.

    Если hints файла A упоминают функцию/метод из файла B —
    проверяет что это имя реально есть в контракте B.
    """
    fc = contract.get("file_contracts", {})
    gi = contract.get("global_imports", {})

    # Собираем все имена из каждого файла
    file_names: dict[str, set[str]] = {}
    for fname, items in fc.items():
        names: set[str] = set()
        for item in items:
            if isinstance(item, dict):
                n = item.get("name", "")
                if n:
                    names.add(n)
                # Из сигнатуры: def method_name(...)
                sig = item.get("signature", "")
                m = re.match(r"(?:class|def|async def)\s+(\w+)", sig.strip())
                if m:
                    names.add(m.group(1))
        file_names[fname] = names

    # Для каждого файла проверяем: импортируемые имена из проекта есть в целевом файле?
    project_stems = {Path(f).stem for f in fc}
    for fname in fc:
        imports = gi.get(fname, [])
        for imp in imports:
            if not isinstance(imp, str):
                continue
            m = re.match(r"from\s+([\w.]+)\s+import\s+(.+)", imp)
            if not m:
                continue
            stem = m.group(1).split(".")[0]
            if stem not in project_stems:
                continue
            target_file = None
            for f in fc:
                if Path(f).stem == stem:
                    target_file = f
                    break
            if not target_file:
                continue
            imported_names = [n.strip().split()[0] for n in m.group(2).split(",")]
            for iname in imported_names:
                if iname and iname not in file_names.get(target_file, set()):
                    logger.warning(
                        f"  ⚠️  A5: {fname} импортирует '{iname}' из {target_file}, "
                        f"но '{iname}' не определён в контракте {target_file}"
                    )
    return contract


def run_a5_validation_pipeline(
    contract: dict,
    arch_resp: dict,
    files: list[str],
    logger: logging.Logger,
    requirements_path: Path | None = None,
    src_path: Path | None = None,
) -> dict:
    """Полный конвейер детерминистских валидаций A5. Вызывается из 4 мест в contract.py."""
    contract = _validate_global_imports(
        contract, arch_resp, files, logger,
        requirements_path=requirements_path,
    )
    contract = _inject_signature_type_imports(contract, logger)
    contract = _sanitize_implementation_hints(contract, logger)
    contract = _inject_requirements_imports(contract, requirements_path, logger)
    contract = _inject_cross_file_imports(contract, logger)
    contract = _dedup_cross_file_classes(contract, logger)
    contract = _dedup_global_imports(contract, logger)
    contract = _validate_signature_types(contract, files, logger)
    contract = _validate_import_consistency(contract, logger, src_path=src_path)
    contract = _detect_and_fix_circular_imports(contract, files, logger)
    contract = _remove_non_ascii_entries(contract)
    # Проверки полноты (warnings, не блокируют)
    contract = _validate_class_methods(contract, logger)
    contract = _validate_cross_file_calls(contract, logger)
    return contract

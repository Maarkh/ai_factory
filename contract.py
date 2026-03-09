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


def _auto_add_requirement(requirements_path: Path, package_name: str, logger: logging.Logger) -> None:
    """Авто-добавляет пакет в requirements.txt если его ещё нет."""
    if not requirements_path or not requirements_path.exists():
        return
    try:
        content = requirements_path.read_text(encoding="utf-8")
    except OSError:
        return
    # Проверяем, не добавлен ли уже
    pkg_lower = package_name.lower()
    for line in content.splitlines():
        line_pkg = re.split(r"[=<>~!\[;]", line.strip())[0].strip().lower()
        if line_pkg.replace("-", "_") == pkg_lower.replace("-", "_"):
            return  # Уже есть
    # Добавляем
    if not content.endswith("\n"):
        content += "\n"
    requirements_path.write_text(content + package_name + "\n", encoding="utf-8")
    logger.info(f"  📦  Авто-добавлен '{package_name}' в requirements.txt")


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
    # Удаляем записи с не-ASCII именами (LLM может вернуть русские имена из A2)
    contract = _remove_non_ascii_entries(contract)
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
                    hints = hints.replace(word, available[0])
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
    from code_context import _PIP_TO_IMPORT
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
            import_name = _PIP_TO_IMPORT.get(pkg, _PIP_TO_IMPORT.get(pkg_norm, pkg_norm))
            if import_name and import_name.isidentifier():
                pkg_to_import[import_name] = f"import {import_name}"
    except Exception:
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
        existing_text = " ".join(existing).lower()

        for import_name, import_line in pkg_to_import.items():
            # Проверяем упоминание пакета в hints/description
            if import_name.lower() in search_text and import_name.lower() not in existing_text:
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
            contract = _inject_signature_type_imports(contract, logger)
            contract = _validate_import_consistency(contract, logger)
            contract = _sanitize_implementation_hints(contract, logger)
            contract = _inject_requirements_imports(contract, req_path if req_path.exists() else None, logger)
            contract = _inject_cross_file_imports(contract, logger)
            contract = _dedup_cross_file_classes(contract, logger)
            contract = _validate_signature_types(contract, files_list, logger)
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


async def _refresh_api_contract(
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

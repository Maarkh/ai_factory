import json
import logging
import os
import re
from pathlib import Path
from typing import Optional

from config import FACTORY_DIR, MAX_FEEDBACK_HISTORY
from exceptions import StateError
from artifacts import save_artifact
from json_utils import safe_contract
from lang_utils import get_docker_image, get_execution_command, LANG_DISPLAY

logger = logging.getLogger(__name__)


def save_state(project_path: Path, state: dict) -> None:
    """Состояние хранится в .factory/state.json.

    Поля с _ не сериализуются в основной файл, но _prev_file_contracts
    сохраняется отдельно для корректной работы каскадного revise_spec.
    """
    factory_dir = project_path / FACTORY_DIR
    factory_dir.mkdir(parents=True, exist_ok=True)
    clean = {k: v for k, v in state.items() if not k.startswith("_")}
    try:
        (factory_dir / "state.json").write_text(
            json.dumps(clean, indent=4, ensure_ascii=False), encoding="utf-8"
        )
        # Сохраняем _prev_file_contracts отдельно для корректного каскада
        prev = state.get("_prev_file_contracts")
        if prev is not None:
            (factory_dir / "prev_contracts.json").write_text(
                json.dumps(prev, indent=2, ensure_ascii=False), encoding="utf-8"
            )
    except OSError as e:
        raise StateError(f"Не удалось сохранить state.json: {e}") from e


def load_state(project_path: Path) -> Optional[dict]:
    p = project_path / FACTORY_DIR / "state.json"
    if not p.exists():
        return None
    try:
        state = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise StateError(f"Не удалось загрузить state.json: {e}") from e
    # Восстанавливаем _prev_file_contracts
    prev_path = project_path / FACTORY_DIR / "prev_contracts.json"
    if prev_path.exists():
        try:
            state["_prev_file_contracts"] = json.loads(prev_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            logger.warning("⚠️  Повреждён prev_contracts.json — пропускаю.")
    return state


def push_feedback(state: dict, filename: str, feedback: str) -> None:
    """Добавляет замечание в историю файла. Хранит только последние MAX_FEEDBACK_HISTORY."""
    if not feedback:
        return
    history = state.setdefault("feedback_history", {}).setdefault(filename, [])
    history.append(feedback)
    if len(history) > MAX_FEEDBACK_HISTORY:
        state["feedback_history"][filename] = history[-MAX_FEEDBACK_HISTORY:]
    state.setdefault("feedbacks", {})[filename] = feedback


def get_feedback_ctx(state: dict, filename: str) -> str:
    """Формирует блок замечаний для контекста разработчика."""
    history = state.get("feedback_history", {}).get(filename, [])
    if not history:
        return state.get("feedbacks", {}).get(filename, "")
    if len(history) == 1:
        return f"ЗАМЕЧАНИЕ (исправь это):\n{history[-1]}"
    # Детекция зацикливания: все замечания одинаковые
    unique = set(history)
    if len(unique) == 1 and len(history) >= MAX_FEEDBACK_HISTORY:
        return (
            "КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ: одно и то же замечание повторяется "
            f"{len(history)} раз подряд. Твой предыдущий подход НЕ РАБОТАЕТ.\n"
            "Попробуй ПРИНЦИПИАЛЬНО ДРУГУЮ структуру кода. "
            "НЕ используй ту же архитектуру классов/функций.\n\n"
            f"ЗАМЕЧАНИЕ:\n{history[-1]}"
        )
    parts = ["ИСТОРИЯ ЗАМЕЧАНИЙ (не повторяй одни и те же ошибки):"]
    for i, fb in enumerate(history, 1):
        parts.append(f"--- Попытка {i} ---\n{fb}")
    return "\n".join(parts)


def _is_valid_filename(f: str) -> bool:
    """Проверяет что строка — валидное имя файла (не директория, имеет расширение)."""
    return bool(re.match(r'^[\w/\-\.]+\.\w+$', f) and ".." not in f and not f.startswith("/"))


def sync_files_with_a5(state: dict, a5_files: set[str], logger: logging.Logger) -> None:
    """Синхронизирует state['files'] с файлами из A5 контракта.

    Добавляет новые файлы из A5, удаляет файлы-призраки (есть в state но нет в A5).
    Фильтрует невалидные имена (директории без расширения, пустые строки).
    """
    files_list = state.setdefault("files", [])
    # Добавляем новые файлы из A5
    for f in a5_files:
        if not _is_valid_filename(f):
            logger.warning(f"  ⚠️  A5 содержит невалидное имя файла: '{f}' — пропущено")
            continue
        if f not in files_list:
            files_list.append(f)
        state.setdefault("feedbacks", {}).setdefault(f, "")
    # Удаляем файлы-призраки и невалидные имена (но НЕ одобренные валидные файлы)
    approved = set(state.get("approved_files", []))
    for f in list(files_list):
        if not _is_valid_filename(f):
            # Невалидные имена удаляем всегда (даже если approved — такого быть не должно)
            logger.info(f"  🗑️  Удалён невалидный файл: {f}")
            files_list.remove(f)
            state.setdefault("feedbacks", {}).pop(f, None)
            if f in state.get("approved_files", []):
                state["approved_files"].remove(f)
            state.setdefault("file_attempts", {}).pop(f, None)
            state.setdefault("cumulative_file_attempts", {}).pop(f, None)
        elif f not in a5_files:
            if f in approved:
                logger.warning(f"  🛡️  {f} нет в новом A5, но уже одобрен — оставляю.")
                continue
            logger.info(f"  🗑️  Удалён файл-призрак: {f} (нет в A5)")
            files_list.remove(f)
            state.setdefault("feedbacks", {}).pop(f, None)
            state.setdefault("file_attempts", {}).pop(f, None)
            state.setdefault("cumulative_file_attempts", {}).pop(f, None)


def ensure_feedback_keys(state: dict) -> None:
    state.setdefault("feedbacks", {})
    for f in state.get("files", []):
        state["feedbacks"].setdefault(f, "")
    state.setdefault("feedback_history", {})
    safe_contract(state)


def generate_summary(project_path: Path, state: dict) -> None:
    """SUMMARY.md — в корне проекта (видно в Git)."""
    language   = state.get("language", "python")
    entry      = state.get("entry_point", "main.py")
    docker_img = get_docker_image(language)
    run_cmd    = get_execution_command(language, entry)
    text = (
        f"# Проект: {project_path.name}\n\n"
        f"## Задача\n{state.get('task', 'N/A')}\n\n"
        f"## Язык\n{LANG_DISPLAY.get(language, language.upper())}\n\n"
        f"## Архитектура\n{state.get('architecture', 'N/A')}\n\n"
        "## Файлы\n" + "\n".join(f"- {f}" for f in state.get("files", []))
        + f"\n\n## Итераций: {state.get('iteration', 1) - 1}\n\n"
        f"## Запуск\n```bash\n"
        f"docker run --rm -v $(pwd)/src:/app -w /app {docker_img} bash -c '{run_cmd}'\n```\n"
    )
    (project_path / "SUMMARY.md").write_text(text, encoding="utf-8")
    logger.info("📄 Сгенерирован SUMMARY.md")


def update_requirements(src_path: Path, orig: str, alt: str) -> None:
    """requirements.txt — в src/. Совпадение по базовому имени пакета (до ==, >=, etc.)."""
    req_path = src_path / "requirements.txt"
    if not req_path.exists():
        return
    orig_base = re.split(r"[=<>!~\[]", orig.strip())[0].strip().lower()
    lines = req_path.read_text(encoding="utf-8").splitlines()
    new_lines = []
    for line in lines:
        line_base = re.split(r"[=<>!~\[]", line.strip())[0].strip().lower()
        new_lines.append(alt if line_base == orig_base else line)
    req_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def sanitize_package_name(pkg: str) -> str:
    """Санитизация имени пакета: разрешены только безопасные символы."""
    # Разрешены буквы, цифры, дефис, подчёркивание, точка, ==, >=, <=, ~=, [extras]
    clean = re.sub(r"[^\w\-\.\[\]=<>~,!]", "", pkg)
    return clean.strip()


def update_dependencies(src_path: Path, language: str, pkg: str) -> None:
    """Зависимости добавляются в src/."""
    pkg = sanitize_package_name(pkg)
    if not pkg:
        logger.warning("⚠️  Пустое или небезопасное имя пакета — пропускаю.")
        return
    if language == "python":
        req_path = src_path / "requirements.txt"
        current_reqs = req_path.read_text(encoding="utf-8") if req_path.exists() else ""
        pkg_base = re.split(r'[=<>~\[!]', pkg)[0].strip().lower()
        existing = [
            re.split(r'[=<>~\[!]', line)[0].strip().lower()
            for line in current_reqs.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        if pkg_base in existing:
            logger.info(f"  ℹ️  '{pkg_base}' уже в requirements.txt — пропускаю.")
            return
        with open(req_path, "a", encoding="utf-8") as f:
            f.write(f"\n{pkg}\n")
            f.flush()
            os.fsync(f.fileno())

    elif language == "typescript":
        pkg_json_path = src_path / "package.json"
        if pkg_json_path.exists():
            try:
                raw_text = pkg_json_path.read_text(encoding="utf-8")
                pkg_data = json.loads(raw_text)  # гарантируем валидный JSON перед редактированием
                if not isinstance(pkg_data, dict):
                    raise ValueError("package.json должен быть объектом, а не массивом/строкой")
                pkg_data.setdefault("dependencies", {})[pkg] = "latest"
                new_text = json.dumps(pkg_data, indent=2, ensure_ascii=False)
                json.loads(new_text)  # двойная проверка перед записью
                pkg_json_path.write_text(new_text, encoding="utf-8")
                logger.info(f"  → Добавлен {pkg} в package.json")
            except (json.JSONDecodeError, ValueError, OSError) as e:
                logger.warning(f"  ⚠️  Не удалось обновить package.json: {e}")

    else:
        logger.warning(f"⚠️  Добавление пакета для {language} требует ручного вмешательства: {pkg}")


def update_dockerfile(src_path: Path, patch: str) -> None:
    """Dockerfile — в src/."""
    dockerfile = src_path / "Dockerfile"
    if not dockerfile.exists():
        return
    content = dockerfile.read_text(encoding="utf-8").rstrip()
    if patch.strip() not in content:
        if not patch.strip().upper().startswith("RUN"):
            patch = f"RUN {patch}"
        content += f"\n\n# DevOps fix\n{patch}\n"
    dockerfile.write_text(content + "\n", encoding="utf-8")


def generate_tor_md(project_path: Path, ba_resp: dict) -> None:
    """A1 сохраняется как артефакт."""
    tor_text = (
        "# A1: Business Requirements (TOR)\n\n"
        f"## Цель проекта\n{ba_resp.get('project_goal', '')}\n\n"
        "## User Stories\n"
        + "\n".join(f"- {s}" for s in ba_resp.get("user_stories", []))
        + "\n\n## Критерии приёмки\n"
        + "\n".join(f"- {c}" for c in ba_resp.get("acceptance_criteria", []))
    )
    save_artifact(project_path, "A1", tor_text)
    logger.info("📄 Артефакт A1 (Business Requirements) сохранён.")

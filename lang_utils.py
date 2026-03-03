import re
from typing import Any

from prompts import PROMPTS

LANG_DISPLAY = {"python": "Python", "typescript": "TypeScript", "rust": "Rust"}
LANG_EXT     = {"python": "py",     "typescript": "ts",         "rust": "rs"}

DOCKER_IMAGES = {
    "python":     "python:3.12-slim",
    "typescript": "node:20-slim",
    "rust":       "rust:1.75-slim",
}


def get_docker_image(language: str) -> str:
    return DOCKER_IMAGES.get(language, "python:3.12-slim")


def get_execution_command(language: str, entry_point: str) -> str:
    """TypeScript: явная установка ts-node и typescript."""
    if language == "python":
        return f"pip install -r requirements.txt -q && python {entry_point}"
    elif language == "typescript":
        return (
            "npm install -q && "
            "npm install -g ts-node typescript --quiet && "
            f"npx ts-node {entry_point}"
        )
    elif language == "rust":
        return "cargo run --quiet"
    return f"python {entry_point}"


def get_test_command(language: str) -> str:
    if language == "python":
        return (
            "pip install pytest pytest-cov -q && "
            "pip install -r requirements.txt -q && "
            "pytest tests/ --cov=. --cov-report=term-missing -q"
        )
    elif language == "typescript":
        return "npm install -q && npm install -g ts-jest --quiet && npx jest --coverage"
    elif language == "rust":
        return "cargo test"
    return "pytest tests/ -q"


def get_system_prompt(agent: str, language: str = "python") -> str:
    """Подставляет {lang} и {ext} в промпты."""
    if agent not in PROMPTS:
        raise ValueError(f"Неизвестный агент: '{agent}'. Доступны: {', '.join(sorted(PROMPTS))}")
    base = PROMPTS[agent]
    lang_name = LANG_DISPLAY.get(language, "Python")
    ext       = LANG_EXT.get(language, "py")
    return base.replace("{lang}", lang_name).replace("{ext}", ext)


def sanitize_files_list(files_raw: list[Any], language: str = "python") -> list[str]:
    """Санитизация: только безопасные относительные пути."""
    safe: list[str] = []
    for f in files_raw:
        if isinstance(f, dict):
            f = f.get("path", "")
        if not isinstance(f, str):
            continue
        if re.match(r'^[\w/\-\.]+\.\w+$', f) and ".." not in f and not f.startswith("/"):
            safe.append(f)
    if safe:
        return safe
    fallback = {
        "python": "main.py",
        "typescript": "main.ts",
        "rust": "src/main.rs",
    }
    return [fallback.get(language, "main.py")]

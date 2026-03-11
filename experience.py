"""
Experience Memory — накопление инженерного опыта между проектами.

Сохраняет пары (error_pattern → fix) из успешных исправлений.
При генерации кода подгружает релевантный опыт в контекст LLM.

Хранилище: BASE_DIR/.factory_experience.json (общее для всех проектов).
"""

import json
import logging
import re
from pathlib import Path
from typing import Any

from config import BASE_DIR

_EXPERIENCE_PATH = BASE_DIR / ".factory_experience.json"
_MAX_EXPERIENCES = 500
_MAX_QUERY_RESULTS = 5

logger = logging.getLogger(__name__)


def _load() -> list[dict]:
    if _EXPERIENCE_PATH.exists():
        try:
            data = json.loads(_EXPERIENCE_PATH.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save(data: list[dict]) -> None:
    _EXPERIENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _EXPERIENCE_PATH.write_text(
        json.dumps(data[-_MAX_EXPERIENCES:], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _normalize(text: str) -> str:
    """Нормализация для поиска: lowercase, без лишних пробелов."""
    return re.sub(r"\s+", " ", text.lower().strip())


def record_experience(
    error_pattern: str,
    fix_description: str,
    category: str = "develop",
    file: str = "",
) -> None:
    """Сохраняет опыт успешного исправления ошибки."""
    if not error_pattern.strip() or not fix_description.strip():
        return

    exp = {
        "category": category,
        "error": error_pattern.strip()[:500],
        "fix": fix_description.strip()[:500],
        "file": file,
    }

    data = _load()

    # Дедупликация: если такой же error+fix уже есть, обновляем
    norm_err = _normalize(exp["error"])
    for existing in data:
        if _normalize(existing.get("error", "")) == norm_err:
            existing["fix"] = exp["fix"]
            existing["category"] = exp["category"]
            _save(data)
            return

    data.append(exp)
    _save(data)
    logger.debug(f"[experience] Saved: {category} | {error_pattern[:80]}...")


def search_experience(query: str, category: str = "") -> list[dict]:
    """Ищет релевантный опыт по substring match в error pattern.

    Возвращает до _MAX_QUERY_RESULTS результатов, отсортированных по релевантности.
    """
    if not query.strip():
        return []

    data = _load()
    if not data:
        return []

    norm_query = _normalize(query)
    # Извлекаем ключевые слова (>3 символов) для scoring
    keywords = [w for w in norm_query.split() if len(w) > 3]
    if not keywords:
        return []

    scored: list[tuple[int, dict]] = []
    for exp in data:
        if category and exp.get("category") != category:
            continue
        norm_err = _normalize(exp.get("error", ""))
        norm_fix = _normalize(exp.get("fix", ""))
        # Подсчёт совпадений ключевых слов
        score = sum(2 for kw in keywords if kw in norm_err)
        score += sum(1 for kw in keywords if kw in norm_fix)
        if score > 0:
            scored.append((score, exp))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [exp for _, exp in scored[:_MAX_QUERY_RESULTS]]


def format_experience_context(experiences: list[dict]) -> str:
    """Форматирует опыт для вставки в промпт разработчика."""
    if not experiences:
        return ""
    parts = ["ОПЫТ ПРОШЛЫХ ПРОЕКТОВ (учти при написании кода):"]
    for i, exp in enumerate(experiences, 1):
        parts.append(f"  {i}. Ошибка: {exp['error']}")
        parts.append(f"     Решение: {exp['fix']}")
    return "\n".join(parts) + "\n\n"

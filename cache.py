import copy
import json
import hashlib
import threading
from pathlib import Path
from typing import Any

from config import FACTORY_DIR


class ThreadSafeCache:
    """Потокобезопасная обёртка над словарём кэша."""

    def __init__(self, data: dict) -> None:
        self._data = data
        self._lock = threading.RLock()

    _MISSING = object()

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            val = self._data.get(key, self._MISSING)
            if val is self._MISSING:
                return default
            return copy.deepcopy(val)

    def __contains__(self, key: str) -> bool:
        with self._lock:
            return key in self._data

    def __setitem__(self, key: str, value: Any) -> None:
        with self._lock:
            self._data[key] = copy.deepcopy(value)

    def __getitem__(self, key: str) -> Any:
        with self._lock:
            return copy.deepcopy(self._data[key])

    def to_dict(self) -> dict:
        with self._lock:
            return copy.deepcopy(self._data)


def cache_key(agent: str, model: str, user_text: str, language: str) -> str:
    return hashlib.sha256(f"{agent}:{model}:{language}:{user_text}".encode()).hexdigest()


def load_cache(project_path: Path) -> ThreadSafeCache:
    """Кэш хранится в .factory/cache.json."""
    p = project_path / FACTORY_DIR / "cache.json"
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                data = {}
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            import logging
            logging.getLogger(__name__).warning(f"⚠️  Повреждённый кэш {p}, начинаю с пустого.")
            data = {}
    else:
        data = {}
    return ThreadSafeCache(data)


def save_cache(project_path: Path, cache: ThreadSafeCache) -> None:
    factory_dir = project_path / FACTORY_DIR
    factory_dir.mkdir(parents=True, exist_ok=True)
    (factory_dir / "cache.json").write_text(
        json.dumps(cache.to_dict(), indent=4, ensure_ascii=False), encoding="utf-8"
    )

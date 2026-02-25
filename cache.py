import copy
import json
import hashlib
import threading
from pathlib import Path

from config import FACTORY_DIR


class ThreadSafeCache:
    """Потокобезопасная обёртка над словарём кэша."""

    def __init__(self, data: dict) -> None:
        self._data = data
        self._lock = threading.RLock()

    def get(self, key: str, default=None):
        with self._lock:
            return self._data.get(key, default)

    def __contains__(self, key: str) -> bool:
        with self._lock:
            return key in self._data

    def __setitem__(self, key: str, value) -> None:
        with self._lock:
            self._data[key] = value

    def __getitem__(self, key: str):
        with self._lock:
            return self._data[key]

    def to_dict(self) -> dict:
        with self._lock:
            return copy.deepcopy(self._data)


def _cache_key(agent: str, model: str, user_text: str, language: str) -> str:
    return hashlib.sha256(f"{agent}:{model}:{language}:{user_text}".encode()).hexdigest()


def load_cache(project_path: Path) -> ThreadSafeCache:
    """Кэш хранится в .factory/cache.json."""
    p = project_path / FACTORY_DIR / "cache.json"
    data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    return ThreadSafeCache(data)


def save_cache(project_path: Path, cache: ThreadSafeCache) -> None:
    factory_dir = project_path / FACTORY_DIR
    factory_dir.mkdir(parents=True, exist_ok=True)
    (factory_dir / "cache.json").write_text(
        json.dumps(cache.to_dict(), indent=4, ensure_ascii=False), encoding="utf-8"
    )

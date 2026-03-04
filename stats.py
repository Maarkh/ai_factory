import json
import os
import tempfile
from pathlib import Path

from config import FACTORY_DIR, FLUSH_EVERY
from lang_utils import LANG_DISPLAY


class ModelStats:
    """Статистика использования моделей."""

    FLUSH_EVERY = FLUSH_EVERY

    def __init__(self, path: Path) -> None:
        # Статистика — в .factory/
        stats_dir = path / FACTORY_DIR
        stats_dir.mkdir(parents=True, exist_ok=True)
        self.path = stats_dir / "model_stats.json"
        self.data: dict = self._load()
        self._dirty: int = 0

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _flush(self) -> None:
        # Атомарная запись: tmp → rename
        content = json.dumps(self.data, indent=2, ensure_ascii=False)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
        try:
            os.write(fd, content.encode("utf-8"))
            os.fsync(fd)
            os.close(fd)
            os.replace(tmp, self.path)
        except OSError:
            os.close(fd)
            os.unlink(tmp)
            raise
        self._dirty = 0

    def record(self, agent: str, model: str, success: bool) -> None:
        key   = f"{agent}:{model}"
        entry = self.data.setdefault(key, {"success": 0, "fail": 0})
        if success:
            entry["success"] += 1
        else:
            entry["fail"] += 1
        self._dirty += 1
        if self._dirty >= self.FLUSH_EVERY:
            self._flush()

    def flush(self) -> None:
        """Принудительный сброс на диск (вызывать в конце итерации / при завершении)."""
        if self._dirty > 0:
            self._flush()

    def print_report(self) -> None:
        """Выводит статистику в консоль (UI — print сохранён намеренно)."""
        self.flush()
        print("\n📊 Статистика моделей:")
        if not self.data:
            print("  Нет данных.")
            return
        for key, d in sorted(self.data.items()):
            total = d["success"] + d["fail"]
            rate  = d["success"] / total * 100 if total else 0
            print(f"  {key}: {d['success']}/{total} ({rate:.0f}%)")


def print_iteration_table(state: dict) -> None:
    """Выводит таблицу итерации в консоль (UI — print сохранён намеренно)."""
    language = state.get("language", "python")
    approved = len(state.get("approved_files", []))
    total    = len(state.get("files", []))
    status   = "✅ ПОЛНЫЙ УСПЕХ" if approved == total else "⏳ В ПРОЦЕССЕ"
    itr      = state.get("iteration", 0)
    phase    = state.get("last_phase", "—")

    w = 78
    def row(left: str, right: str) -> None:
        content = f"  {left:<20}: {right}"
        print(f"║{content:<{w}}║")

    print("╔" + "═" * w + "╗")
    title = f"ИТЕРАЦИЯ {itr:2d} — {status}"
    print(f"║{title:^{w}}║")
    print("╠" + "═" * w + "╣")
    row("Язык",           LANG_DISPLAY.get(language, language.upper()))
    row("Одобрено файлов", f"{approved}/{total} {'✅' if approved == total else '🔄'}")
    row("Последняя фаза",  phase)
    print("╚" + "═" * w + "╝")

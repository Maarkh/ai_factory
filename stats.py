import json
from pathlib import Path

from config import FACTORY_DIR
from lang_utils import LANG_DISPLAY


class ModelStats:
    FLUSH_EVERY = 20  # сбрасывать на диск каждые N записей

    def __init__(self, path: Path) -> None:
        # Статистика — в .factory/
        stats_dir = path / FACTORY_DIR
        stats_dir.mkdir(parents=True, exist_ok=True)
        self.path = stats_dir / "model_stats.json"
        self.data: dict = self._load()
        self._dirty: int = 0

    def _load(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {}

    def _flush(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
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

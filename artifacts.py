import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
from config import FACTORY_DIR, ARTIFACTS_DIR, ARTIFACT_LABELS


def save_artifact(
    project_path: Path,
    artifact_id: str,
    content: Union[str, dict],
    extra_label: str = "",
) -> None:
    """Сохраняет артефакт в .factory/artifacts/AX_label.md.

    content может быть строкой (markdown) или dict (будет завёрнут в JSON-блок).
    """
    art_dir = project_path / FACTORY_DIR / ARTIFACTS_DIR
    art_dir.mkdir(parents=True, exist_ok=True)

    label = ARTIFACT_LABELS.get(artifact_id, extra_label or artifact_id.lower())
    fname = f"{artifact_id}_{label}.md"

    if isinstance(content, dict):
        text = (
            f"# {artifact_id}: {label.replace('_', ' ').title()}\n\n"
            f"```json\n{json.dumps(content, ensure_ascii=False, indent=2)}\n```\n"
        )
    else:
        text = content

    (art_dir / fname).write_text(text, encoding="utf-8")


def load_artifact(project_path: Path, artifact_id: str, extra_label: str = "") -> Optional[str]:
    """Загружает артефакт по ID. Возвращает текст или None."""
    art_dir = project_path / FACTORY_DIR / ARTIFACTS_DIR
    label = ARTIFACT_LABELS.get(artifact_id, extra_label or artifact_id.lower())
    fname = f"{artifact_id}_{label}.md"
    p = art_dir / fname
    return p.read_text(encoding="utf-8") if p.exists() else None


def update_artifact_a9(project_path: Path, filename: str, description: str) -> None:
    """Добавляет запись в A9 (Implementation Logs)."""
    art_dir = project_path / FACTORY_DIR / ARTIFACTS_DIR
    art_dir.mkdir(parents=True, exist_ok=True)
    a9_path = art_dir / "A9_implementation_logs.md"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n### [{ts}] {filename}\n{description}\n"
    with open(a9_path, "a", encoding="utf-8") as f:
        f.write(entry)

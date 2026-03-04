import json
import logging
import sys
from pathlib import Path
from typing import Optional

from cache import ThreadSafeCache
from exceptions import LLMError, StateError
from llm import ask_agent
from state import save_state
from config import MAX_SPEC_REVISIONS
from log_utils import get_model

logger = logging.getLogger(__name__)

_shutdown_requested = False


class PipelineContext:
    """Хранит пути к обеим директориям проекта."""

    def __init__(self) -> None:
        self.state: Optional[dict] = None
        self.project_path: Optional[Path] = None
        self.src_path: Optional[Path] = None
        self.factory_path: Optional[Path] = None

    def bind(self, project_path: Path, state: dict) -> None:
        from config import SRC_DIR, FACTORY_DIR
        self.project_path = project_path
        self.src_path = project_path / SRC_DIR
        self.factory_path = project_path / FACTORY_DIR
        self.state = state

    def save_if_bound(self) -> None:
        if self.state is not None and self.project_path is not None:
            try:
                save_state(self.project_path, self.state)
                logger.info("✅ Состояние сохранено.")
            except (StateError, OSError) as e:
                logger.warning(f"⚠️  Не удалось сохранить состояние: {e}")


_ctx = PipelineContext()


def signal_handler(sig, frame) -> None:
    global _shutdown_requested
    _shutdown_requested = True
    print("\n⌛ Ctrl+C — сохраняем состояние...")
    _ctx.save_if_bound()
    sys.exit(0)


def is_shutdown_requested() -> bool:
    return _shutdown_requested


def _fallback_phase(state: dict, reason: str) -> dict:
    """Детерминистский выбор следующей фазы по текущему состоянию."""
    approved = len(state.get("approved_files", []))
    total = len(state.get("files", []))
    if approved < total:
        return {"next_phase": "develop",          "reason": reason}
    if not state.get("e2e_passed"):
        return {"next_phase": "e2e_review",       "reason": reason}
    if not state.get("integration_passed"):
        return {"next_phase": "integration_test", "reason": reason}
    if not state.get("tests_passed"):
        return {"next_phase": "unit_tests",       "reason": reason}
    if not state.get("document_generated"):
        return {"next_phase": "document",         "reason": reason}
    return {"next_phase": "success",              "reason": reason}


async def ask_supervisor(
    logger: logging.Logger,
    state: dict,
    cache: ThreadSafeCache,
    randomize: bool,
    language: str,
) -> dict:
    approved = len(state.get("approved_files", []))
    total    = len(state.get("files", []))
    phase_fails = state.get("phase_fail_counts", {})

    summary = {
        "iteration":            state.get("iteration", 1),
        "language":             language,
        "approved_files":       approved,
        "total_files":          total,
        "all_files_approved":   approved == total,
        "e2e_passed":           state.get("e2e_passed", False),
        "integration_passed":   state.get("integration_passed", False),
        "tests_passed":         state.get("tests_passed", False),
        "document_generated":   state.get("document_generated", False),
        "has_pending_feedback": any(v for v in state.get("feedbacks", {}).values()),
        "last_phase":           state.get("last_phase", "initial"),
        "phase_fail_counts":    phase_fails,
        "phase_total_fails":    state.get("phase_total_fails", {}),
        "spec_revisions_count": len(state.get("spec_history", [])),
    }

    ctx = (
        f"Текущее состояние проекта:\n"
        f"{json.dumps(summary, ensure_ascii=False, indent=2)}\n\n"
        "Реши следующую фазу строго по правилам из промпта."
    )
    try:
        result = await ask_agent(logger, "supervisor", ctx, cache, 0, randomize, language)

        # Детерминистская защита от scope creep: максимум 3 revise_spec
        next_phase = result.get("next_phase", "")
        spec_count = len(state.get("spec_history", []))
        if next_phase == "revise_spec" and spec_count >= MAX_SPEC_REVISIONS:
            logger.warning(
                f"⚠️  Supervisor предложил revise_spec, но лимит ({spec_count}/{MAX_SPEC_REVISIONS}) исчерпан. "
                "Принудительно продолжаем без ревизии."
            )
            # Сбрасываем только revise_spec счётчик (другие фазы сохраняют информацию)
            state.setdefault("phase_fail_counts", {}).pop("revise_spec", None)
            result = _fallback_phase(state, "fallback: revise_spec лимит исчерпан")

        return result
    except (LLMError, ValueError) as e:
        logger.exception(f"Supervisor упал: {e}")
        return _fallback_phase(state, f"fallback: supervisor exception: {e}")


def _bump_phase_fail(state: dict, phase: str) -> int:
    counts = state.setdefault("phase_fail_counts", {})
    counts[phase] = counts.get(phase, 0) + 1
    # Общий счётчик фейлов за весь проект (не сбрасывается)
    total_counts = state.setdefault("phase_total_fails", {})
    total_counts[phase] = total_counts.get(phase, 0) + 1
    return counts[phase]


def _reset_phase_fail(state: dict, phase: str) -> None:
    state.setdefault("phase_fail_counts", {})[phase] = 0

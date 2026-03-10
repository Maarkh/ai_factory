import json
import logging
from pathlib import Path
from typing import Optional

from config import MAX_SPEC_REVISIONS, SRC_DIR, TRUNCATE_FEEDBACK
from exceptions import LLMError
from llm import ask_agent
from stats import ModelStats
from json_utils import safe_contract
from lang_utils import LANG_DISPLAY
from log_utils import get_model
from artifacts import save_artifact
from contract import refresh_api_contract, phase_review_api_contract
from cache import ThreadSafeCache

# Re-exports: ai_factory.py imports these from phases
from phase_develop import (  # noqa: F401
    phase_validate_architecture,
    phase_a5_compliance_review,
    phase_develop,
    do_self_reflect,
)
from phase_test import (  # noqa: F401
    phase_e2e_review,
    phase_cross_file_check,
    phase_integration_test,
    phase_unit_tests,
)


async def phase_document(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    randomize: bool = False,
) -> None:
    logger.info("📝 Генерация README.md (A10) ...")
    language = state.get("language", "python")
    try:
        resp = await ask_agent(
            logger, "documenter",
            (
                f"Задача: {state['task']}\n"
                f"Бизнес-требования (A1): {json.dumps(state.get('business_requirements', {}), ensure_ascii=False)}\n"
                f"Архитектура: {state['architecture']}\n"
                f"Язык: {LANG_DISPLAY.get(language, language)}"
            ),
            cache, 0, randomize, language,
        )
        readme_text = resp.get("readme", "").strip()
        # README.md — в корне src/ (виден пользователю)
        (project_path / SRC_DIR / "README.md").write_text(readme_text, encoding="utf-8")
        # Также сохраняем как артефакт A10
        save_artifact(project_path, "A10", readme_text)
        logger.info("✅ README.md сгенерирован (A10 сохранён).")
    except (LLMError, ValueError) as e:
        logger.warning(f"⚠️  Documenter не справился: {e}")


async def revise_spec(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    problem: str,
    randomize: bool = False,
    stats: Optional[ModelStats] = None,
) -> None:
    """
    v15.0: Каскадный пересмотр спецификации.
    A2 обновляется → автоматически пересчитывается A5 →
    сбрасываются только файлы, затронутые изменённым контрактом.
    """
    spec_count = len(state.get("spec_history", []))
    if spec_count >= MAX_SPEC_REVISIONS:
        logger.warning(
            f"⚠️  Лимит пересмотров спецификации ({MAX_SPEC_REVISIONS}) исчерпан. "
            "Продолжаем с текущей спецификацией."
        )
        state.setdefault("phase_fail_counts", {}).pop("revise_spec", None)
        return

    logger.info("\n🔁 Пересмотр спецификации (каскад A2 → A5) ...")
    language = state.get("language", "python")
    ctx = (
        f"Запрос заказчика:\n{state['task']}\n\n"
        f"Текущая спецификация (A2):\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
        f"Проблема:\n{problem}"
    )
    try:
        new_specs      = await ask_agent(logger, "spec_reviewer", ctx, cache, 0, randomize, language)
        change_summary = new_specs.get("change_summary", "нет описания")
        state["system_specs"] = {
            "data_models":     new_specs.get("data_models", state.get("system_specs", {}).get("data_models", [])),
            "components":      new_specs.get("components", state.get("system_specs", {}).get("components", [])),
            "business_rules":  new_specs.get("business_rules", state.get("system_specs", {}).get("business_rules", [])),
            "external_systems": new_specs.get("external_systems", state.get("system_specs", {}).get("external_systems", [])),
        }

        save_artifact(project_path, "A2", state["system_specs"])

        _stats = stats or ModelStats(project_path)
        await refresh_api_contract(logger, project_path, state, cache,
                                    _stats, randomize)

        a5_ok = await phase_review_api_contract(
            logger, project_path, state, cache, _stats,
            state.get("api_contract", {}),
            {"architecture": state.get("architecture", ""), "files": state.get("files", [])},
            state.get("system_specs", {}),
            randomize,
        )
        if not a5_ok:
            logger.warning("⚠️  Обновлённый A5 не прошёл ревью. Продолжаем с текущим.")

        new_contracts     = safe_contract(state).get("file_contracts", {})
        previously_approved = list(state.get("approved_files", []))
        affected_files = []
        for fname in previously_approved:
            old_contract = state.get("_prev_file_contracts", {}).get(fname)
            new_contract = new_contracts.get(fname)
            if old_contract != new_contract:
                affected_files.append(fname)

        if not state.get("_prev_file_contracts"):
            affected_files = previously_approved

        for fname in affected_files:
            if fname in state.get("approved_files", []):
                state["approved_files"].remove(fname)
            state["feedbacks"][fname] = "Спецификация обновлена, требуется переписать файл."
            state["file_attempts"][fname] = 0

        for fname in state.get("files", []):
            state["file_attempts"][fname] = 0

        state["e2e_cumulative_resets"] = {}

        state["_prev_file_contracts"] = new_contracts

        state["env_fixes"]          = {}
        state["phase_fail_counts"]  = {}
        pt = state.get("phase_total_fails", {})
        if pt.get("e2e_review", 0) < 6:
            state["e2e_passed"] = False
        if pt.get("integration_test", 0) < 8:
            state["integration_passed"] = False
        if pt.get("unit_tests", 0) < 6:
            state["tests_passed"] = False
        state["document_generated"] = False

        logger.info(f"✅ Спецификация обновлена (A2): {change_summary}")
        if affected_files:
            logger.info(f"ℹ️  Сброшены затронутые файлы: {', '.join(affected_files)}")
        unchanged = [f for f in previously_approved if f not in affected_files]
        if unchanged:
            logger.info(f"✅ Незатронутые файлы сохранены: {', '.join(unchanged)}")

        state.setdefault("spec_history", []).append({
            "iteration":      state["iteration"],
            "problem":        problem,
            "change":         change_summary,
            "reset_files":    affected_files,
            "kept_files":     unchanged,
        })

        arch_path = project_path / "ARCHITECTURE.md"
        arch_md   = arch_path.read_text(encoding="utf-8") if arch_path.exists() else ""
        arch_md  += (
            f"\n\n## Обновление спецификации (итерация {state['iteration']})\n"
            f"**Причина:** {problem}\n**Изменение:** {change_summary}\n"
            f"**Сброшены файлы:** {', '.join(affected_files) or 'нет'}\n\n"
            f"```json\n{json.dumps(state['system_specs'], ensure_ascii=False, indent=2)}\n```"
        )
        arch_path.write_text(arch_md, encoding="utf-8")

    except (LLMError, ValueError) as e:
        logger.warning(f"⚠️  Не удалось обновить спецификацию: {e}")

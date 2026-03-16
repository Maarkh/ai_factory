import json
import logging
from pathlib import Path
from typing import Optional

from config import MAX_SPEC_REVISIONS, SRC_DIR, E2E_TOTAL_SKIP, INTEGRATION_TOTAL_SKIP, UNIT_TEST_TOTAL_SKIP
from exceptions import LLMError
from llm import ask_agent
from stats import ModelStats
from json_utils import safe_contract
from lang_utils import LANG_DISPLAY
from artifacts import save_artifact
from contract import refresh_api_contract, phase_review_api_contract
from cache import ThreadSafeCache
from generate_docs import generate_docs_markdown

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
    src_path = project_path / SRC_DIR
    language = state.get("language", "python")

    # 1) LLM-генерированный README (описание, архитектура, примеры)
    logger.info("📝 Генерация README.md (A10) ...")
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
        (src_path / "README.md").write_text(readme_text, encoding="utf-8")
        save_artifact(project_path, "A10", readme_text)
        logger.info("✅ README.md сгенерирован (A10 сохранён).")
    except (LLMError, ValueError) as e:
        logger.warning(f"⚠️  Documenter не справился: {e}")

    # 2) Детерминистический справочник — дерево + все исходники
    logger.info("📝 Генерация PROJECT_DOCS.md (полный код) ...")
    try:
        project_name = state.get("project_name", project_path.name)
        docs_md = generate_docs_markdown(
            src_path, description=state.get("task", ""), name=project_name,
        )
        (src_path / "PROJECT_DOCS.md").write_text(docs_md, encoding="utf-8")
        logger.info("✅ PROJECT_DOCS.md сгенерирован.")
    except Exception as e:
        logger.warning(f"⚠️  generate_docs не справился: {e}")


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

    # История предыдущих ревизий — чтобы не повторять неудачные изменения
    spec_history = state.get("spec_history", [])
    if spec_history:
        history_lines = []
        for i, entry in enumerate(spec_history, 1):
            history_lines.append(
                f"  Ревизия {i} (итерация {entry.get('iteration', '?')}): "
                f"проблема: {entry.get('problem', '?')[:200]} → "
                f"изменение: {entry.get('change', '?')[:200]}"
            )
        ctx += (
            f"\n\n⚠️ ИСТОРИЯ РЕВИЗИЙ (НЕ повторяй те же изменения):\n"
            + "\n".join(history_lines)
        )

    # Статус разработки — какие файлы работают, какие зациклились
    approved = state.get("approved_files", [])
    all_files = state.get("files", [])
    stuck_files = []
    for f in all_files:
        if f not in approved:
            fb = state.get("feedbacks", {}).get(f, "")
            cum = state.get("cumulative_file_attempts", {}).get(f, 0)
            if cum >= 3 and fb:
                stuck_files.append(f"{f} ({cum} попыток): {fb[:150]}")
    if approved or stuck_files:
        ctx += f"\n\nСТАТУС РАЗРАБОТКИ: одобрено {len(approved)}/{len(all_files)} файлов."
        if stuck_files:
            ctx += "\nЗАСТРЯВШИЕ ФАЙЛЫ (учти при ревизии):\n" + "\n".join(f"  - {s}" for s in stuck_files)
    try:
        new_specs      = await ask_agent(logger, "spec_reviewer", ctx, cache, 0, randomize, language)
        change_summary = new_specs.get("change_summary", "нет описания")

        # Детерминистская защита от scope creep: LLM не должен добавлять
        # новые компоненты/data_models/business_rules, которых не было в спецификации.
        old_specs = state.get("system_specs", {})
        old_component_names = {c["name"] for c in old_specs.get("components", []) if isinstance(c, dict) and "name" in c}
        old_model_names     = {m["name"] for m in old_specs.get("data_models", []) if isinstance(m, dict) and "name" in m}

        new_components = new_specs.get("components", old_specs.get("components", []))
        new_models     = new_specs.get("data_models", old_specs.get("data_models", []))
        new_rules      = new_specs.get("business_rules", old_specs.get("business_rules", []))

        if old_component_names:
            filtered_components = [c for c in new_components if not isinstance(c, dict) or c.get("name") in old_component_names]
            if len(filtered_components) < len(new_components):
                stripped = [c.get("name", "?") for c in new_components if isinstance(c, dict) and c.get("name") not in old_component_names]
                logger.warning(f"⚠️  spec_reviewer добавил лишние компоненты: {stripped} — отброшены (scope creep)")
                new_components = filtered_components

        if old_model_names:
            filtered_models = [m for m in new_models if not isinstance(m, dict) or m.get("name") in old_model_names]
            if len(filtered_models) < len(new_models):
                stripped = [m.get("name", "?") for m in new_models if isinstance(m, dict) and m.get("name") not in old_model_names]
                logger.warning(f"⚠️  spec_reviewer добавил лишние модели: {stripped} — отброшены (scope creep)")
                new_models = filtered_models

        old_rules_count = len(old_specs.get("business_rules", []))
        if len(new_rules) > old_rules_count and old_rules_count > 0:
            logger.warning(f"⚠️  spec_reviewer добавил лишние бизнес-правила ({len(new_rules)} > {old_rules_count}) — обрезаны до исходного количества")
            new_rules = new_rules[:old_rules_count]

        state["system_specs"] = {
            "data_models":      new_models,
            "components":       new_components,
            "business_rules":   new_rules,
            "external_systems": new_specs.get("external_systems", old_specs.get("external_systems", [])),
        }

        save_artifact(project_path, "A2", state["system_specs"])

        _stats = stats or ModelStats(project_path)

        # Обновляем архитектуру (A3) под изменённую A2
        language = state.get("language", "python")
        try:
            logger.info("🏗️  Обновляю архитектуру (A3) под новую спецификацию ...")
            arch_ctx = (
                f"Запрос:\n{state['task']}\n\n"
                f"Обновлённая спецификация (A2):\n{json.dumps(state['system_specs'], ensure_ascii=False, indent=2)}\n\n"
                f"Текущая архитектура:\n{state.get('architecture', '')}\n\n"
                f"Текущие файлы проекта: {state.get('files', [])}\n\n"
                f"Целевой язык: {LANG_DISPLAY.get(language, language)}\n\n"
                f"ВАЖНО: адаптируй архитектуру под изменения в A2. "
                f"Сохрани существующие файлы и модули. Меняй только то, что затронуто."
            )
            arch_resp = await ask_agent(logger, "architect", arch_ctx, cache, 0, randomize, language)
            state["architecture"] = arch_resp.get("architecture", state.get("architecture", ""))
            state["arch_resp"] = arch_resp
            save_artifact(project_path, "A3", arch_resp)
            # Обновляем requirements.txt из новых dependencies
            new_deps = arch_resp.get("dependencies", [])
            if new_deps:
                req_path = project_path / SRC_DIR / "requirements.txt"
                existing = set()
                if req_path.exists():
                    existing = {line.strip().lower().split("==")[0].split(">=")[0]
                                for line in req_path.read_text().splitlines() if line.strip() and not line.startswith("#")}
                added = []
                for dep in new_deps:
                    dep_name = dep.strip().lower().split("==")[0].split(">=")[0]
                    if dep_name and dep_name not in existing:
                        added.append(dep.strip())
                if added:
                    with open(req_path, "a", encoding="utf-8") as f:
                        f.write("\n" + "\n".join(added) + "\n")
                    logger.info(f"📦 requirements.txt: добавлены {added}")
            logger.info(f"✅ Архитектура обновлена.")
        except (LLMError, ValueError) as e:
            logger.warning(f"⚠️  Не удалось обновить архитектуру: {e}. Продолжаем со старой.")

        await refresh_api_contract(logger, project_path, state, cache,
                                    _stats, randomize)

        a5_ok = await phase_review_api_contract(
            logger, project_path, state, cache, _stats,
            state.get("api_contract", {}),
            state.get("arch_resp", {"architecture": state.get("architecture", ""), "files": state.get("files", [])}),
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
        if pt.get("e2e_review", 0) < E2E_TOTAL_SKIP:
            state["e2e_passed"] = False
        if pt.get("integration_test", 0) < INTEGRATION_TOTAL_SKIP:
            state["integration_passed"] = False
        if pt.get("unit_tests", 0) < UNIT_TEST_TOTAL_SKIP:
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

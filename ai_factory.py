"""
Мультифайловая Фабрика Агентов v15.0
=====================================

"""

import asyncio
import json
import re
import signal
from pathlib import Path

from config import (
    BASE_DIR,
    WAIT_TIMEOUT,
    MAX_ABSOLUTE_ITERS,
    MAX_FILE_ATTEMPTS,
    MAX_PHASE_TOTAL_FAILS,
    MAX_ITERS_DEFAULT,
    MAX_ITERS_INCREMENT,
    TRUNCATE_FEEDBACK,
    MIN_COVERAGE,
    FACTORY_DIR,
    SRC_DIR,
    ARTIFACTS_DIR,
    LOGS_DIR,
    MAX_ARCH_ATTEMPTS,
    MAX_A5_REVIEW_ATTEMPTS,
    DEVELOP_STALL_THRESHOLD,
    E2E_TOTAL_SKIP,
    E2E_CONSECUTIVE_REVISE,
    INTEGRATION_TOTAL_SKIP,
    UNIT_TEST_TOTAL_SKIP,
    ITERS_BUMP_REVISE,
    ITERS_BUMP_SMALL,
)
from cache import load_cache, save_cache
from log_utils import setup_logger, input_with_timeout
from llm import ask_agent
from stats import ModelStats, print_iteration_table
from artifacts import save_artifact
from infra import check_docker_installed, git_init, git_commit
from state import (
    save_state, load_state, ensure_feedback_keys,
    generate_summary, generate_tor_md, sync_files_with_a5,
)
from lang_utils import LANG_DISPLAY, DOCKER_IMAGES, sanitize_files_list, get_execution_command, get_docker_image
from contract import phase_generate_api_contract, phase_review_api_contract
from phases import (
    phase_validate_architecture,
    phase_develop,
    phase_e2e_review,
    phase_cross_file_check,
    phase_integration_test,
    phase_unit_tests,
    phase_document,
    revise_spec,
)
from supervisor import (
    ctx, signal_handler,
    ask_supervisor, bump_phase_fail, reset_phase_fail,
)


def _force_approve_files(state: dict, project_path: Path, files: list[str], reason: str, logger) -> None:
    """Принудительно одобряет файлы с непустым кодом на диске."""
    src_path = project_path / SRC_DIR
    approved = state.setdefault("approved_files", [])
    for f in files:
        fpath = src_path / f
        if fpath.exists() and fpath.read_text(encoding="utf-8").strip():
            logger.warning(f"⚠️  {f}: {reason} → принудительный APPROVE")
            if f not in approved:
                approved.append(f)
            state["feedbacks"][f] = ""
            state["file_attempts"][f] = 0


def _can_revise_spec(state: dict, logger, phase: str = "") -> bool:
    """Проверяет, не исчерпан ли лимит revise_spec (MAX_SPEC_REVISIONS за проект).

    phase — имя фазы-инициатора. При отказе сбрасывается ТОЛЬКО её consecutive-счётчик,
    а не все фазы (иначе supervisor теряет информацию о проблемах в других фазах).
    """
    from config import MAX_SPEC_REVISIONS
    count = len(state.get("spec_history", []))
    if count >= MAX_SPEC_REVISIONS:
        logger.warning(
            f"⚠️  revise_spec пропущен: лимит {count}/{MAX_SPEC_REVISIONS} исчерпан. "
            "Продолжаем с текущей спецификацией."
        )
        counts = state.setdefault("phase_fail_counts", {})
        if phase:
            counts.pop(phase, None)
        else:
            counts.clear()
        return False
    return True


def _init_project_files(
    project_path: Path,
    project_name: str,
    language: str,
    deps: list[str],
    files_list: list[str],
    arch_resp: dict,
    ba_resp: dict,
    sa_resp: dict,
    task: str,
) -> tuple[list[str], str]:
    """
    v15.0: Все исходники создаются в src/.
    .factory/ создаётся отдельно.
    """
    src_path = project_path / SRC_DIR
    src_path.mkdir(parents=True, exist_ok=True)

    # Создаём директории для .factory
    (project_path / FACTORY_DIR / ARTIFACTS_DIR).mkdir(parents=True, exist_ok=True)
    (project_path / FACTORY_DIR / LOGS_DIR).mkdir(parents=True, exist_ok=True)

    if language == "python":
        entry_point = "main.py"
        if "main.py" not in files_list:
            files_list.append("main.py")
        req_path = src_path / "requirements.txt"
        req_path.write_text(
            "\n".join(deps) if deps else "# No external dependencies\n", encoding="utf-8"
        )
        # Исправляем невалидные pip-пакеты от LLM (opencv → opencv-python-headless)
        from contract import validate_requirements_txt
        import logging as _logging
        validate_requirements_txt(req_path, _logging.getLogger("ai_factory"))

    elif language == "typescript":
        entry_point = "main.ts"
        if "main.ts" not in files_list:
            files_list.append("main.ts")
        pkg_data = {
            "name":         project_name.lower(),
            "version":      "1.0.0",
            "dependencies": {d: "latest" for d in deps},
        }
        (src_path / "package.json").write_text(json.dumps(pkg_data, indent=2), encoding="utf-8")

    elif language == "rust":
        entry_point = "src/main.rs"
        if "src/main.rs" not in files_list:
            files_list.append("src/main.rs")
        (src_path / "src").mkdir(exist_ok=True)
        cargo_deps = "\n".join(f'{d} = "*"' for d in deps)
        cargo_toml = (
            f'[package]\nname = "{project_name.lower()}"\n'
            f'version = "0.1.0"\nedition = "2021"\n\n[dependencies]\n{cargo_deps}\n'
        )
        (src_path / "Cargo.toml").write_text(cargo_toml, encoding="utf-8")
    else:
        entry_point = "main.py"

    # ARCHITECTURE.md — в корне проекта (виден в Git)
    (project_path / "ARCHITECTURE.md").write_text(
        f"# {project_name}\n\n"
        f"## Задача\n{task}\n\n"
        f"## Бизнес-требования (A1)\n```json\n{json.dumps(ba_resp, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## Системная спецификация (A2)\n```json\n{json.dumps(sa_resp, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## Архитектура (A3)\n{arch_resp.get('architecture', '')}",
        encoding="utf-8",
    )

    # Сохраняем A0 (User Intent) — неизменяемый базис
    save_artifact(project_path, "A0", f"# A0: User Intent\n\n{task}\n")

    # Сохраняем A2 (System Specification) как артефакт
    save_artifact(project_path, "A2", sa_resp)

    # Сохраняем A3/A4 (Architecture)
    arch_text = (
        f"# A3/A4: Architecture Map & File Structure\n\n"
        f"## Architecture\n{arch_resp.get('architecture', '')}\n\n"
        f"## Files\n" + "\n".join(f"- `{f}`" for f in files_list)
    )
    save_artifact(project_path, "A3", arch_text)

    return files_list, entry_point


async def _run_initial_pipeline(
    logger, project_path: Path, project_name: str,
    language: str, cache, stats: ModelStats, randomize_models: bool,
) -> dict | None:
    """Запускает начальный пайплайн BA→SA→Arch→A5. Возвращает state или None при ошибке."""
    task = input("Опишите задачу: ").strip()
    if not task:
        print("❌ Задача не может быть пустой.")
        return None

    git_init(project_path)

    print("\n📊 Business Analyst (→ A1) ...")
    try:
        ba_resp = await ask_agent(logger, "business_analyst", f"Запрос:\n{task}", cache, language=language)
        generate_tor_md(project_path, ba_resp)
    except Exception as e:
        print(f"❌ Business Analyst упал: {e}")
        return None

    print("⚙️  System Analyst (→ A2) ...")
    try:
        sa_resp = await ask_agent(
            logger, "system_analyst",
            f"Запрос:\n{task}\n\nТЗ от БА (A1):\n{json.dumps(ba_resp, ensure_ascii=False, indent=2)}",
            cache, language=language,
        )
    except Exception as e:
        print(f"❌ System Analyst упал: {e}")
        return None

    print("🏗️  Architect (→ A3/A4) ...")
    arch_resp: dict = {}
    arch_attempt = 0
    while arch_attempt < MAX_ARCH_ATTEMPTS:
        if arch_attempt > 0:
            delay = 2 ** arch_attempt
            print(f"  ⏳ Пауза {delay}с перед попыткой {arch_attempt + 1}/5 ...")
            await asyncio.sleep(delay)
        try:
            arch_resp = await ask_agent(
                logger, "architect",
                (
                    f"Запрос:\n{task}\n\n"
                    f"Спецификация от SA (A2):\n{json.dumps(sa_resp, ensure_ascii=False, indent=2)}\n\n"
                    f"Целевой язык: {LANG_DISPLAY.get(language, language)}"
                ),
                cache, arch_attempt, randomize_models, language,
            )
            if await phase_validate_architecture(
                logger, project_path, None, cache, stats,
                arch_resp, sa_resp, task, language, randomize_models,
            ):
                break
            arch_attempt += 1
            print(f"🔄 Перегенерация архитектуры (попытка {arch_attempt}/{MAX_ARCH_ATTEMPTS}) ...")
        except Exception as e:
            print(f"❌ Architect упал: {e}")
            arch_attempt += 1

    if arch_attempt >= MAX_ARCH_ATTEMPTS:
        print(f"❌ Не удалось валидировать архитектуру за {MAX_ARCH_ATTEMPTS} попыток.")
        return None

    deps       = arch_resp.get("dependencies", [])
    files_raw  = arch_resp.get("files", [])
    files_list = sanitize_files_list(files_raw, language)

    files_list, entry_point = _init_project_files(
        project_path, project_name, language,
        deps, files_list, arch_resp, ba_resp, sa_resp, task,
    )

    state = {
        "task":                 task,
        "business_requirements": ba_resp,
        "system_specs":         sa_resp,
        "architecture":         arch_resp.get("architecture", ""),
        "api_contract":         {},
        "test_plan":            {},
        "files":                files_list,
        "approved_files":       [],
        "feedbacks":            {f: "" for f in files_list},
        "file_attempts":        {},
        "spec_history":         [],
        "env_fixes":            {},
        "phase_fail_counts":    {},
        "iteration":            1,
        "max_iters":            MAX_ITERS_DEFAULT,
        "language":             language,
        "entry_point":          entry_point,
        "last_phase":           "initial",
        "e2e_passed":           False,
        "integration_passed":   False,
        "tests_passed":         False,
        "document_generated":   False,
    }

    for a5_attempt in range(MAX_A5_REVIEW_ATTEMPTS):
        api_contract = await phase_generate_api_contract(
            logger, project_path, state, cache, stats,
            arch_resp, sa_resp, randomize_models,
        )
        state["api_contract"] = api_contract
        a5_files = set(api_contract.get("file_contracts", {}).keys())
        sync_files_with_a5(state, a5_files, logger)
        state["_prev_file_contracts"] = api_contract.get("file_contracts", {})
        if await phase_review_api_contract(
            logger, project_path, state, cache, stats,
            api_contract, arch_resp, sa_resp, randomize_models,
        ):
            break
        logger.warning(f"🔄 A5 отклонён, перегенерация (попытка {a5_attempt + 2}/{MAX_A5_REVIEW_ATTEMPTS}) ...")
    else:
        logger.warning(f"⚠️  A5 не прошёл ревью за {MAX_A5_REVIEW_ATTEMPTS} попыток, продолжаем с текущим.")

    save_state(project_path, state)
    save_cache(project_path, cache)
    git_commit(project_path, "Initial architecture + artifacts A0-A5")

    return state


def _print_success_summary(state: dict, project_path: Path, language: str) -> list[str]:
    """Печатает итоговую сводку проекта. Возвращает список пропущенных фаз."""
    src_path = project_path / SRC_DIR
    skipped = []
    if state.get("e2e_skipped"):
        skipped.append("E2E")
    if state.get("integration_skipped"):
        skipped.append("Integration")
    if state.get("tests_skipped"):
        skipped.append("Unit tests")
    all_skipped = len(skipped) >= 3
    print("\n" + "═" * 80)
    if all_skipped:
        print(f"{'⚠️  ЧАСТИЧНЫЙ УСПЕХ — ВСЕ ТЕСТЫ ПРОПУЩЕНЫ ⚠️':^80}")
    elif skipped:
        print(f"{'⚠️  УСПЕХ С ОГОВОРКАМИ ⚠️':^80}")
    else:
        print(f"{'🎉 УСПЕХ! Проект готов 🎉':^80}")
    print("═" * 80)
    print(f"📂 Папка проекта : {project_path}")
    print(f"📦 Исходный код  : {src_path}")
    print(f"🗄️  Метаданные    : {project_path / FACTORY_DIR}")
    print(f"🌍 Язык          : {LANG_DISPLAY.get(language, language)}")
    print(f"🔢 Итераций      : {state['iteration']}")
    print(f"📄 Файлов        : {len(state['files'])}")
    if skipped:
        print(f"⚠️  ПРОПУЩЕНО    : {', '.join(skipped)}")
    else:
        print(f"🧪 Unit-тесты + покрытие ≥ {MIN_COVERAGE}%")
    print(f"🚀 Docker-ready")
    print("\n📋 Артефакты проекта:")
    art_dir = project_path / FACTORY_DIR / ARTIFACTS_DIR
    if art_dir.exists():
        for art in sorted(art_dir.iterdir()):
            print(f"   {art.name}")
    print("\n📋 Запуск:")
    run_cmd = get_execution_command(language, state.get("entry_point", "main.py"))
    print(f"   docker run --rm -v $(pwd)/src:/app -w /app {get_docker_image(language)} bash -c '{run_cmd}'")
    print("═" * 80)
    return skipped


async def main() -> None:
    if not check_docker_installed():
        return

    signal.signal(signal.SIGINT, signal_handler)

    print("🚀 Мультифайловая Фабрика Агентов v15.0")
    print("   (Supervisor · Self-Reflect · Parallel E2E · Multi-Language · Artifacts A0-A10)\n")

    if input("Подтвердите запуск (yes/no): ").strip().lower() != "yes":
        print("Отменено.")
        return

    randomize_models = input("Случайная ротация моделей? (y/n) [n]: ").strip().lower() == "y"
    if randomize_models:
        print("🎲 Режим случайной ротации включён.")

    project_name = input("Имя проекта (латиницей): ").strip()
    if not re.match(r"^[A-Za-z0-9_\-]+$", project_name):
        print("❌ Недопустимое имя проекта.")
        return

    language_input = input("Язык (python / typescript / rust) [python]: ").strip().lower()
    language = language_input if language_input in DOCKER_IMAGES else "python"
    print(f"🌍 Выбран язык: {LANG_DISPLAY.get(language, language)}")

    project_path = BASE_DIR / project_name
    project_path.mkdir(parents=True, exist_ok=True)

    logger = setup_logger(project_path)
    cache  = load_cache(project_path)
    stats  = ModelStats(project_path)

    # ── Загрузка или создание состояния ──────────────────────────────────────
    state = load_state(project_path)
    if state:
        if "language" not in state:
            state["language"] = "python"
        language = state["language"]
        if input_with_timeout(
            f"📁 Найден прогресс (итерация {state.get('iteration', 1)}). Продолжить? (y/n): ",
            WAIT_TIMEOUT, "y"
        ).lower() != "y":
            state = None

    if state:
        ensure_feedback_keys(state)
    else:
        state = await _run_initial_pipeline(
            logger, project_path, project_name, language,
            cache, stats, randomize_models,
        )
        if state is None:
            return

    # Привязываем контекст для signal handler
    ctx.bind(project_path, state)

    # ── Главный цикл ─────────────────────────────────────────────────────────
    state.setdefault("e2e_attempt", 0)

    while True:
        if state["iteration"] > MAX_ABSOLUTE_ITERS:
            print(f"\n🛑 Достигнут абсолютный потолок {MAX_ABSOLUTE_ITERS} итераций. Завершение.")
            stats.print_report()
            return

        if state["iteration"] > state["max_iters"]:
            if input_with_timeout(
                f"⚠️  Лимит {state['max_iters']} итераций. Дать ещё {MAX_ITERS_INCREMENT}? (y/n): ",
                WAIT_TIMEOUT, "y"
            ).lower() == "y":
                state["max_iters"] += MAX_ITERS_INCREMENT
                save_state(project_path, state)
            else:
                stats.print_report()
                return

        decision   = await ask_supervisor(logger, state, cache, randomize_models, language)
        next_phase = decision.get("next_phase", "develop")
        confidence = decision.get("confidence", 0)
        reason     = decision.get("reason", "")

        # Проверка абсолютного лимита фейлов одной фазы (но не чаще 1 раза)
        total_fails = state.get("phase_total_fails", {}).get(next_phase, 0)
        if not isinstance(state.get("spec_escalated_phases"), list):
            state["spec_escalated_phases"] = []
        spec_escalated_phases = state["spec_escalated_phases"]
        if total_fails >= MAX_PHASE_TOTAL_FAILS and next_phase not in spec_escalated_phases:
            spec_escalated_phases.append(next_phase)
            if _can_revise_spec(state, logger, next_phase):
                print(f"\n🛑 Фаза '{next_phase}' провалилась {total_fails} раз за проект. "
                      f"Принудительный revise_spec.")
                problem = (
                    f"Фаза '{next_phase}' провалилась {total_fails} раз. "
                    "Вероятно, фундаментальная проблема в спецификации."
                )
                await revise_spec(logger, project_path, state, cache, problem, randomize_models, stats)
                state["max_iters"] += ITERS_BUMP_REVISE
            save_state(project_path, state)
            save_cache(project_path, cache)
            stats.flush()
            state["iteration"] += 1
            continue

        print(f"\n{'─' * 50}")
        print(f"🧭 SUPERVISOR → {next_phase.upper()} (уверенность: {confidence}%) | {reason}")
        state["last_phase"] = next_phase
        save_state(project_path, state)

        # ── Диспетчер фаз ────────────────────────────────────────────────────
        try:
            if next_phase == "develop":
                approved_before = set(state.get("approved_files", []))
                exhausted, spec_blocked = await phase_develop(logger, project_path, state, cache, stats, randomize=randomize_models)
                approved_after = set(state.get("approved_files", []))
                made_progress = len(approved_after) > len(approved_before)

                if made_progress:
                    reset_phase_fail(state, "develop")

                # Немедленная эскалация: reviewer сказал что проблема в спецификации
                if spec_blocked:
                    problem = (
                        f"Reviewer определил проблемы уровня СПЕЦИФИКАЦИИ в файлах: {', '.join(spec_blocked)}. "
                        "Разработчик НЕ может исправить это без изменения A2/A3/A5. "
                        "Последние замечания: "
                        + "; ".join(
                            f"{f}: {state['feedbacks'].get(f, '')[:TRUNCATE_FEEDBACK]}"
                            for f in spec_blocked
                        )
                    )
                    if _can_revise_spec(state, logger, "develop"):
                        print(f"📋 Проблема спецификации: {', '.join(spec_blocked)} → revise_spec")
                        await revise_spec(logger, project_path, state, cache, problem, randomize_models, stats)
                        state["max_iters"] += ITERS_BUMP_REVISE
                        for f in spec_blocked:
                            state["file_attempts"][f] = 0
                    else:
                        _force_approve_files(state, project_path, spec_blocked, "spec исчерпана + spec_blocked", logger)
                elif exhausted:
                    problem = (
                        f"Файлы не удалось написать за {MAX_FILE_ATTEMPTS} попыток: {', '.join(exhausted)}. "
                        "Последние замечания: "
                        + "; ".join(
                            f"{f}: {state['feedbacks'].get(f, '')[:TRUNCATE_FEEDBACK]}"
                            for f in exhausted
                        )
                    )
                    if _can_revise_spec(state, logger, "develop"):
                        print(f"🔁 Автоэскалация: {', '.join(exhausted)} → revise_spec")
                        await revise_spec(logger, project_path, state, cache, problem, randomize_models, stats)
                        state["max_iters"] += ITERS_BUMP_REVISE
                        for f in exhausted:
                            state["file_attempts"][f] = 0
                    else:
                        _force_approve_files(state, project_path, exhausted, "spec исчерпана + exhausted", logger)
                elif not made_progress:
                    fails = bump_phase_fail(state, "develop")
                    if fails >= DEVELOP_STALL_THRESHOLD:
                        unapproved = [f for f in state["files"]
                                      if f not in state.get("approved_files", [])]
                        problem = (
                            f"Разработка застопорилась на {fails} итераций подряд. "
                            f"Файлы без прогресса: {', '.join(unapproved)}. "
                            "Последние замечания: "
                            + "; ".join(
                                f"{f}: {state['feedbacks'].get(f, '')[:TRUNCATE_FEEDBACK]}"
                                for f in unapproved
                            )
                        )
                        if _can_revise_spec(state, logger, "develop"):
                            print(f"⚠️  Разработка не продвигается {fails} итераций → revise_spec ({', '.join(unapproved)})")
                            await revise_spec(logger, project_path, state, cache, problem, randomize_models, stats)
                            state["max_iters"] += ITERS_BUMP_REVISE
                            for f in unapproved:
                                state["file_attempts"][f] = 0
                        else:
                            _force_approve_files(state, project_path, unapproved, "spec исчерпана + stalled", logger)

            elif next_phase == "e2e_review":
                total_e2e_fails = state.get("phase_total_fails", {}).get("e2e_review", 0)
                # Предохранитель: после 6+ суммарных E2E отказов — пропускаем к integration_test
                if total_e2e_fails >= E2E_TOTAL_SKIP:
                    logger.warning(f"⚠️  E2E падал {E2E_TOTAL_SKIP}+ раз суммарно → ПРОПУСК (e2e_skipped=true), переход к integration_test.")
                    state["e2e_passed"] = True
                    state["e2e_skipped"] = True
                    state["e2e_attempt"] = 0
                    reset_phase_fail(state, "e2e_review")
                elif not phase_cross_file_check(logger, project_path, state):
                    bump_phase_fail(state, "cross_file_check")
                    save_state(project_path, state)
                    state["iteration"] += 1
                    continue
                elif not await phase_e2e_review(logger, project_path, state, cache, stats, state["e2e_attempt"], randomize=randomize_models):
                    fails = bump_phase_fail(state, "e2e_review")
                    state["e2e_attempt"] += 1
                    if fails >= E2E_CONSECUTIVE_REVISE and _can_revise_spec(state, logger, "e2e_review"):
                        print(f"⚠️  E2E падает {E2E_CONSECUTIVE_REVISE} раз подряд → принудительный revise_spec.")
                        feedbacks = [
                            f"  {f}: {state['feedbacks'].get(f, '')[:TRUNCATE_FEEDBACK]}"
                            for f in state["files"] if state["feedbacks"].get(f, "")
                        ]
                        problem = (
                            f"E2E Review отклоняет проект {fails} раз подряд.\n"
                            "Конкретные замечания ревьюеров:\n" + "\n".join(feedbacks)
                        )
                        await revise_spec(logger, project_path, state, cache, problem, randomize_models, stats)
                        state["max_iters"] += ITERS_BUMP_SMALL
                else:
                    state["e2e_passed"] = True
                    state["e2e_attempt"] = 0
                    reset_phase_fail(state, "e2e_review")

            elif next_phase == "integration_test":
                total_int_fails = state.get("phase_total_fails", {}).get("integration_test", 0)
                if total_int_fails >= INTEGRATION_TOTAL_SKIP:
                    logger.warning(f"⚠️  Integration test падал {INTEGRATION_TOTAL_SKIP}+ раз суммарно → ПРОПУСК, переход к unit_tests.")
                    state["integration_passed"] = True
                    state["integration_skipped"] = True
                    reset_phase_fail(state, "integration_test")
                elif not await phase_integration_test(logger, project_path, state, cache, stats, randomize=randomize_models):
                    bump_phase_fail(state, "integration_test")
                else:
                    state["integration_passed"] = True
                    reset_phase_fail(state, "integration_test")

            elif next_phase == "unit_tests":
                total_ut_fails = state.get("phase_total_fails", {}).get("unit_tests", 0)
                if total_ut_fails >= UNIT_TEST_TOTAL_SKIP:
                    logger.warning(f"⚠️  Unit tests падал {UNIT_TEST_TOTAL_SKIP}+ раз суммарно → ПРОПУСК, переход к document.")
                    state["tests_passed"] = True
                    state["tests_skipped"] = True
                    reset_phase_fail(state, "unit_tests")
                elif not await phase_unit_tests(logger, project_path, state, cache, stats, randomize=randomize_models):
                    bump_phase_fail(state, "unit_tests")
                else:
                    state["tests_passed"] = True
                    reset_phase_fail(state, "unit_tests")

            elif next_phase == "document":
                await phase_document(logger, project_path, state, cache, randomize=randomize_models)
                state["document_generated"] = True

            elif next_phase == "revise_spec":
                if _can_revise_spec(state, logger, "revise_spec"):
                    problem = input_with_timeout(
                        "Опишите противоречие (или Enter для авто): ", 10,
                        "Авто-эскалация от Supervisor"
                    ).strip() or "Авто-эскалация от Supervisor"
                    await revise_spec(logger, project_path, state, cache, problem, randomize_models, stats)
                    state["max_iters"] += ITERS_BUMP_REVISE

            elif next_phase == "success":
                git_commit(project_path, f"Successful build: iteration {state['iteration']}")
                print_iteration_table(state)
                generate_summary(project_path, state)
                skipped = _print_success_summary(state, project_path, language)
                stats.print_report()

                act = input_with_timeout(
                    f"\nЧто дальше?\n  Enter — принять\n  r — доработать файл\n  spec — пересмотреть спецификацию\n"
                    f"👉 [авто через {WAIT_TIMEOUT}с]: ",
                    WAIT_TIMEOUT, ""
                ).lower()

                if act == "r":
                    target   = input("Файл (main.py): ").strip() or state.get("entry_point", "main.py")
                    feedback = input(f"Правки для {target}: ").strip()
                    if not feedback:
                        print("Пустые правки — пропускаю.")
                    else:
                        if target not in state["files"]:
                            state["files"].append(target)
                            state["feedbacks"][target] = ""
                        if target in state.get("approved_files", []):
                            state["approved_files"].remove(target)
                        state["feedbacks"][target] = f"Требование заказчика: {feedback}"
                        state["file_attempts"][target] = 0
                        state["e2e_passed"] = state["integration_passed"] = \
                            state["tests_passed"] = state["document_generated"] = False
                        # Сброс phase counters чтобы safety valves не блокировали re-test
                        state["phase_total_fails"] = {}
                        state["phase_fail_counts"] = {}
                        state["max_iters"] += ITERS_BUMP_SMALL
                        save_state(project_path, state)
                elif act == "spec":
                    if _can_revise_spec(state, logger, "success"):
                        problem = input("Опишите противоречие: ").strip() or "Запрос заказчика"
                        await revise_spec(logger, project_path, state, cache, problem, randomize_models, stats)
                        state["e2e_passed"] = state["integration_passed"] = \
                            state["tests_passed"] = state["document_generated"] = False
                        state["max_iters"] += ITERS_BUMP_REVISE
                        save_state(project_path, state)
                    else:
                        print("⚠️  Лимит ревизий спецификации исчерпан (3/3).")
                else:
                    print("✅ Готово. Можно пить кофе ☕")
                    return

            else:
                logger.warning(f"Неизвестная фаза от Supervisor: '{next_phase}'. Fallback → develop.")
                exhausted, spec_blocked = await phase_develop(logger, project_path, state, cache, stats, randomize=randomize_models)
                if spec_blocked or exhausted:
                    _force_approve_files(state, project_path, spec_blocked + exhausted, "unknown phase fallback", logger)
        except Exception as _phase_exc:
            logger.exception(f"💥 Необработанная ошибка в фазе '{next_phase}': {_phase_exc}")
            save_state(project_path, state)

        save_cache(project_path, cache)
        state["iteration"] += 1
        save_state(project_path, state)
        stats.flush()
        print_iteration_table(state)


if __name__ == "__main__":
    asyncio.run(main())

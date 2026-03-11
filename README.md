# 📄 Проект "Ситуационный центр"

## 📝 Описание

Это проект автоматизации полного цикла разработки на нескольких языках программирования.

## 🛠️ Установка

1. Клонируйте репозиторий.
2. Создайте виртуальное окружение: `python -m venv .venv`
3. Активируйте виртуальное окружение:
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`
4. Установите зависимости: `pip install -r requirements.txt`


## ▶️ Запуск

Описан в файле RUN.md

## 📁 Структура проекта

├── ai_factory/
│   ├────── README.md
│   ├────── ai_factory.py
│   ├────── artifacts.py
│   ├────── cache.py
│   ├────── checks.py
│   ├────── code_context.py
│   ├────── config.py
│   ├────── contract.py
│   ├────── contract_validation.py
│   ├────── exceptions.py
│   ├────── generate_docs.py
│   ├────── infra.py
│   ├────── json_utils.py
│   ├────── lang_utils.py
│   ├────── llm.py
│   ├────── log_utils.py
│   ├────── models_pool.py
│   ├────── phase_develop.py
│   ├────── phase_test.py
│   ├────── phases.py
│   ├────── prompts.py
│   ├────── requirements.txt
│   ├────── state.py
│   ├────── stats.py
│   ├────── supervisor.py
│   ├────── test_task.md
│   ├── .venv_factory/
│   ├── __pycache__/
│   ├── .claude/
│   ├── tests/
│   │   ├────── __init__.py
│   │   ├────── test_business_logic.py
│   │   ├────── test_modules.py
│   │   ├── __pycache__/
│   ├── .pytest_cache/
│   ├── documents/
│   ├── .git/
│   │   ├── info/
│   │   ├── refs/
│   │   │   ├── remotes/
│   │   │   │   ├── origin/
│   │   │   ├── tags/
│   │   │   ├── heads/
│   │   ├── objects/
│   │   │   ├── 14/
│   │   │   ├── 5e/
│   │   │   ├── e1/
│   │   │   ├── 60/
│   │   │   ├── d6/
│   │   │   ├── 16/
│   │   │   ├── 6a/
│   │   │   ├── a6/
│   │   │   ├── info/
│   │   │   ├── fc/
│   │   │   ├── ac/
│   │   │   ├── 44/
│   │   │   ├── 42/
│   │   │   ├── 2a/
│   │   │   ├── 21/
│   │   │   ├── ff/
│   │   │   ├── 3f/
│   │   │   ├── 4d/
│   │   │   ├── 7e/
│   │   │   ├── 4f/
│   │   │   ├── cb/
│   │   │   ├── 8e/
│   │   │   ├── 82/
│   │   │   ├── f9/
│   │   │   ├── 37/
│   │   │   ├── b9/
│   │   │   ├── 56/
│   │   │   ├── 95/
│   │   │   ├── aa/
│   │   │   ├── da/
│   │   │   ├── 78/
│   │   │   ├── 50/
│   │   │   ├── 36/
│   │   │   ├── 1d/
│   │   │   ├── 7c/
│   │   │   ├── 38/
│   │   │   ├── 2f/
│   │   │   ├── 1e/
│   │   │   ├── 6b/
│   │   │   ├── a1/
│   │   │   ├── 0f/
│   │   │   ├── 7a/
│   │   │   ├── 6d/
│   │   │   ├── de/
│   │   │   ├── 46/
│   │   │   ├── a8/
│   │   │   ├── d4/
│   │   │   ├── 5f/
│   │   │   ├── c8/
│   │   │   ├── 7f/
│   │   │   ├── 32/
│   │   │   ├── e5/
│   │   │   ├── 1a/
│   │   │   ├── 73/
│   │   │   ├── 40/
│   │   │   ├── df/
│   │   │   ├── d9/
│   │   │   ├── 81/
│   │   │   ├── 58/
│   │   │   ├── cf/
│   │   │   ├── 92/
│   │   │   ├── c6/
│   │   │   ├── b6/
│   │   │   ├── 00/
│   │   │   ├── e6/
│   │   │   ├── 70/
│   │   │   ├── 9b/
│   │   │   ├── 72/
│   │   │   ├── 06/
│   │   │   ├── e0/
│   │   │   ├── af/
│   │   │   ├── b7/
│   │   │   ├── e8/
│   │   │   ├── 09/
│   │   │   ├── e4/
│   │   │   ├── db/
│   │   │   ├── 2c/
│   │   │   ├── 9c/
│   │   │   ├── f5/
│   │   │   ├── 6e/
│   │   │   ├── 96/
│   │   │   ├── 87/
│   │   │   ├── b4/
│   │   │   ├── 48/
│   │   │   ├── 4e/
│   │   │   ├── a9/
│   │   │   ├── ba/
│   │   │   ├── f0/
│   │   │   ├── 30/
│   │   │   ├── 35/
│   │   │   ├── 83/
│   │   │   ├── d8/
│   │   │   ├── 04/
│   │   │   ├── ec/
│   │   │   ├── 8b/
│   │   │   ├── 4b/
│   │   │   ├── ee/
│   │   │   ├── f8/
│   │   │   ├── 10/
│   │   │   ├── 3c/
│   │   │   ├── ef/
│   │   │   ├── 34/
│   │   │   ├── 53/
│   │   │   ├── 23/
│   │   │   ├── 07/
│   │   │   ├── 01/
│   │   │   ├── ea/
│   │   │   ├── 59/
│   │   │   ├── eb/
│   │   │   ├── 0e/
│   │   │   ├── 66/
│   │   │   ├── 18/
│   │   │   ├── 4a/
│   │   │   ├── 8d/
│   │   │   ├── 97/
│   │   │   ├── 0c/
│   │   │   ├── 3a/
│   │   │   ├── 80/
│   │   │   ├── 45/
│   │   │   ├── d3/
│   │   │   ├── 3d/
│   │   │   ├── a7/
│   │   │   ├── 8f/
│   │   │   ├── fd/
│   │   │   ├── 0b/
│   │   │   ├── 43/
│   │   │   ├── b8/
│   │   │   ├── 0a/
│   │   │   ├── 5c/
│   │   │   ├── e9/
│   │   │   ├── bd/
│   │   │   ├── 12/
│   │   │   ├── 64/
│   │   │   ├── f3/
│   │   │   ├── 8c/
│   │   │   ├── 51/
│   │   │   ├── 68/
│   │   │   ├── 27/
│   │   │   ├── 57/
│   │   │   ├── 98/
│   │   │   ├── ca/
│   │   │   ├── 39/
│   │   │   ├── 86/
│   │   │   ├── a3/
│   │   │   ├── 9a/
│   │   │   ├── 55/
│   │   │   ├── 11/
│   │   │   ├── 22/
│   │   │   ├── 31/
│   │   │   ├── 13/
│   │   │   ├── 9f/
│   │   │   ├── 7d/
│   │   │   ├── ad/
│   │   │   ├── 05/
│   │   │   ├── b0/
│   │   │   ├── 74/
│   │   │   ├── c2/
│   │   │   ├── 9d/
│   │   │   ├── ce/
│   │   │   ├── 29/
│   │   │   ├── 2e/
│   │   │   ├── bc/
│   │   │   ├── 2d/
│   │   │   ├── 5a/
│   │   │   ├── 52/
│   │   │   ├── d1/
│   │   │   ├── dd/
│   │   │   ├── f7/
│   │   │   ├── fa/
│   │   │   ├── 67/
│   │   │   ├── 17/
│   │   │   ├── 6c/
│   │   │   ├── pack/
│   │   │   ├── ab/
│   │   │   ├── b1/
│   │   │   ├── e2/
│   │   │   ├── 93/
│   │   │   ├── 69/
│   │   │   ├── d7/
│   │   │   ├── bb/
│   │   │   ├── d5/
│   │   │   ├── 6f/
│   │   │   ├── 89/
│   │   │   ├── c5/
│   │   │   ├── 2b/
│   │   │   ├── c4/
│   │   │   ├── 65/
│   │   │   ├── a2/
│   │   │   ├── f1/
│   │   │   ├── 26/
│   │   │   ├── 88/
│   │   │   ├── c0/
│   │   │   ├── f4/
│   │   ├── logs/
│   │   │   ├── refs/
│   │   │   │   ├── remotes/
│   │   │   │   │   ├── origin/
│   │   │   │   ├── heads/
│   │   ├── hooks/
## 💻 Коды основных модулей
### 📄 `ai_factory.py`

```python
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
                    save_cache(project_path, cache)
                    stats.flush()
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
                        # Сброс skip-флагов чтобы повторные тесты реально запустились
                        for _sk in ("e2e_skipped", "integration_skipped", "tests_skipped"):
                            state.pop(_sk, None)
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
                        for _sk in ("e2e_skipped", "integration_skipped", "tests_skipped"):
                            state.pop(_sk, None)
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

```
### 📄 `artifacts.py`

```python
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

```
### 📄 `cache.py`

```python
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

```
### 📄 `checks.py`

```python
import ast
import difflib
import re
from pathlib import Path


def sanitize_llm_code(code: str) -> str:
    """Очищает код от артефактов LLM: markdown fences, garbage tokens."""
    # 1. Убираем markdown code fences (```python ... ```)
    code = re.sub(r"^```[\w]*\s*\n?", "", code, flags=re.MULTILINE)
    code = re.sub(r"^```\s*$", "", code, flags=re.MULTILINE)
    # 2. Убираем garbage tokens deepseek-coder (begin_of_sentence и т.п.)
    # Сначала дедупликация: img<token>img_bytes → img_bytes (модель перезапускает генерацию)
    _GARBAGE_TOKEN = r"<[｜|][\w▁]+[｜|]>"
    code = re.sub(r"(\w+)" + _GARBAGE_TOKEN + r"\1", r"\1", code)
    # Затем убираем оставшиеся токены (gcv<token>_image → gcv_image)
    code = re.sub(_GARBAGE_TOKEN, "", code)
    # 3. Убираем JSON-wrapper поля, которые LLM встраивает в код
    # (imports_from_project = [...], external_dependencies = [...])
    code = re.sub(
        r"^\s*(?:imports_from_project|external_dependencies|called_by)\s*=\s*\[.*?\]\s*$",
        "", code, flags=re.MULTILINE,
    )
    return code.strip()


def ensure_a5_imports(code: str, global_imports: list[str]) -> str:
    """Гарантирует что все A5 global_imports присутствуют в коде.

    Developer часто забывает импорты (import numpy as np, from typing import List и т.д.)
    хотя A5 контракт их требует. Вместо REJECT → авто-добавляем.
    """
    if not global_imports or not code.strip():
        return code
    # Парсим существующие import-строки из кода
    existing_imports: set[str] = set()
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            # Нормализуем пробелы для сравнения
            existing_imports.add(re.sub(r"\s+", " ", stripped))

    missing: list[str] = []
    for imp_line in global_imports:
        if not isinstance(imp_line, str):
            continue
        normalized = re.sub(r"\s+", " ", imp_line.strip())
        if not normalized:
            continue
        # Проверяем точное совпадение или что базовый модуль уже импортирован
        if normalized in existing_imports:
            continue
        # "from typing import List" vs "from typing import List, Dict" → проверяем базу
        m = re.match(r"from\s+(\S+)\s+import\s+(.+)", normalized)
        if m:
            source = m.group(1)
            names = {n.strip().split()[0] for n in m.group(2).split(",") if n.strip()}
            # Ищем существующий import из того же source
            found_source = False
            for ex in existing_imports:
                ex_m = re.match(r"from\s+(\S+)\s+import\s+(.+)", ex)
                if ex_m and ex_m.group(1) == source:
                    found_source = True
                    ex_names = {n.strip().split()[0] for n in ex_m.group(2).split(",") if n.strip()}
                    # Есть ли недостающие имена?
                    missing_names = names - ex_names
                    if missing_names:
                        # Объединяем в один import
                        all_names = sorted(ex_names | names)
                        new_line = f"from {source} import {', '.join(all_names)}"
                        # Ищем конкретную строку в коде, которая нормализуется в ex
                        lines = code.split("\n")
                        for li, line in enumerate(lines):
                            if re.sub(r"\s+", " ", line.strip()) == ex:
                                lines[li] = new_line
                                break
                        code = "\n".join(lines)
                        existing_imports.discard(ex)
                        existing_imports.add(re.sub(r"\s+", " ", new_line))
                    break
            if not found_source:
                missing.append(normalized)
        else:
            # "import X as Y" — проверяем по полному совпадению (включая alias)
            m2 = re.match(r"import\s+(\S+)(?:\s+as\s+(\w+))?", normalized)
            if m2:
                module = m2.group(1)
                alias = m2.group(2)
                # Проверяем: есть ли уже точно такой же import (с тем же alias)?
                already = any(
                    re.match(rf"import\s+{re.escape(module)}\s+as\s+{re.escape(alias)}\b", ex)
                    for ex in existing_imports
                ) if alias else any(
                    re.match(rf"import\s+{re.escape(module)}\b", ex)
                    for ex in existing_imports
                )
                if not already:
                    missing.append(normalized)
            else:
                missing.append(normalized)

    if missing:
        # Добавляем пропущенные imports в начало файла (после docstring/comments если есть)
        lines = code.split("\n")
        insert_pos = 0
        # Пропускаем начальные комментарии, docstrings, shebang
        in_docstring = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Обработка многострочных docstrings
            if in_docstring:
                insert_pos = i + 1
                if '"""' in stripped or "'''" in stripped:
                    in_docstring = False
                continue
            if (stripped.startswith('"""') or stripped.startswith("'''")):
                insert_pos = i + 1
                # Однострочный docstring (открытие и закрытие на одной строке)
                quote = '"""' if stripped.startswith('"""') else "'''"
                if stripped.count(quote) < 2:
                    in_docstring = True
                continue
            if stripped.startswith("#") or not stripped:
                insert_pos = i + 1
            elif stripped.startswith("import ") or stripped.startswith("from "):
                insert_pos = i  # Вставляем перед первым import
                break
            else:
                break
        for imp in reversed(missing):
            lines.insert(insert_pos, imp)
        code = "\n".join(lines)

    return code


def check_class_duplication(code: str, global_context: str, file_contract: list | None = None) -> list[str]:
    """Детерминистская проверка: не определяет ли код классы, которые уже есть в других файлах.
    file_contract — A5 контракт текущего файла; классы, ожидаемые по контракту, не считаются дублями.
    Возвращает список предупреждений (пустой если дублирования нет)."""
    if not global_context:
        return []
    # Классы, определённые в новом коде (только публичные)
    classes_in_code = {n for n in re.findall(r'^class\s+(\w+)', code, re.MULTILINE)
                       if not n.startswith('_')}
    if not classes_in_code:
        return []
    # Классы, ожидаемые по A5 контракту для этого файла — их определять МОЖНО
    expected_classes: set[str] = set()
    if file_contract:
        for item in file_contract:
            if isinstance(item, dict):
                name = item.get("class") or item.get("name") or item.get("function", "")
                if name:
                    expected_classes.add(name)
    # Маппинг класс → файл-источник из global_context
    name_to_file: dict[str, str] = {}
    current_file = None
    for line in global_context.splitlines():
        m = re.match(r'^--- (\S+) PUBLIC API ---$', line)
        if m:
            current_file = m.group(1)
            continue
        if current_file:
            for name in re.findall(r'class\s+(\w+)', line):
                if not name.startswith('_'):
                    name_to_file[name] = current_file
    duplicates = classes_in_code & set(name_to_file.keys()) - expected_classes
    if not duplicates:
        return []
    return [
        f"{name} уже определён в {name_to_file[name]} — "
        f"используй импорт из {name_to_file[name]} вместо переопределения"
        for name in sorted(duplicates)
    ]


def check_import_shadowing(code: str) -> list[str]:
    """Детерминистская проверка: не определяет ли файл top-level функцию/класс
    с тем же именем, что импортируется через from X import Y.
    Пример ошибки: from video_processing import process_frame + def process_frame(...)
    Возвращает список предупреждений."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    # Собираем имена, импортированные через from X import Y
    imported_names: dict[str, str] = {}  # name → "from X import name"
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in (node.names or []):
                real_name = alias.asname or alias.name
                if real_name != "*":
                    imported_names[real_name] = f"from {node.module} import {alias.name}"
    if not imported_names:
        return []
    # Собираем top-level определения (def / class) — только прямые потомки модуля
    defined_names: set[str] = set()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined_names.add(node.name)
    # Пересечение = shadowing
    shadowed = defined_names & set(imported_names.keys())
    if not shadowed:
        return []
    return [
        f"'{name}' импортирован ({imported_names[name]}) И определён "
        f"в этом файле — убери локальное определение или импорт"
        for name in sorted(shadowed)
    ]


def check_data_only_violations(
    code: str,
    current_file: str,
    project_files: list[str],
) -> list[str]:
    """Детерминистская проверка: если файл — data-only (models.py / data_models.py),
    запрещает:
    1. Импорты из других файлов проекта (создают циклические зависимости)
    2. Top-level функции с бизнес-логикой (только dunder-методы внутри классов)

    Возвращает список предупреждений (пустой если всё ОК или файл не data-only).
    """
    stem = Path(current_file).stem
    if stem not in ("models", "data_models"):
        return []

    warnings: list[str] = []
    project_stems = {Path(f).stem for f in project_files if Path(f).stem != stem}

    # 1. Проверяем project-file imports
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            base = node.module.split(".")[0]
            if base in project_stems:
                names = ", ".join(a.name for a in (node.names or []))
                warnings.append(
                    f"ЗАПРЕЩЕНО: 'from {node.module} import {names}' — "
                    f"{current_file} это data-only файл, он НЕ ДОЛЖЕН импортировать "
                    f"из других файлов проекта. Определи все классы ЗДЕСЬ, "
                    f"а другие файлы будут импортировать ИЗ {current_file}"
                )
        elif isinstance(node, ast.Import):
            for alias in (node.names or []):
                base = alias.name.split(".")[0]
                if base in project_stems:
                    warnings.append(
                        f"ЗАПРЕЩЕНО: 'import {alias.name}' — "
                        f"{current_file} это data-only файл, он НЕ ДОЛЖЕН импортировать "
                        f"из других файлов проекта"
                    )

    # 2. Проверяем top-level функции (не внутри классов)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                warnings.append(
                    f"ЗАПРЕЩЕНО: top-level функция '{node.name}()' в {current_file} — "
                    f"этот файл содержит ТОЛЬКО data classes (dataclass/class определения). "
                    f"Бизнес-логику вынеси в соответствующий модуль"
                )

    return warnings


def check_stub_functions(code: str) -> list[str]:
    """Детерминистская проверка: содержит ли код функции-заглушки.

    Ловит: pass / ... / raise NotImplementedError как единственное тело функции,
    а также pass внутри единственного try-блока.
    Возвращает список предупреждений (пустой если заглушек нет).
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    warnings: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        fname = node.name
        body = node.body
        # Пропускаем docstring если есть (только строковые литералы, не Ellipsis)
        effective = body
        if (effective and isinstance(effective[0], ast.Expr)
                and isinstance(effective[0].value, ast.Constant)
                and isinstance(getattr(effective[0].value, "value", None), str)):
            effective = effective[1:]
        if not effective:
            warnings.append(f"функция '{fname}' пустая (только docstring)")
            continue
        # Проверяем паттерны заглушек
        if _is_stub_body(effective):
            warnings.append(
                f"функция '{fname}' — заглушка (pass / ... / NotImplementedError). "
                f"Напиши полную реализацию с бизнес-логикой"
            )
            continue
        # Проверяем фиктивную реализацию (hardcoded return без использования параметров)
        if _is_hardcoded_return_stub(node):
            warnings.append(
                f"функция '{fname}' — фиктивная реализация (возвращает захардкоженный литерал, "
                f"не используя параметры). Напиши реальную логику, использующую входные данные"
            )
    return warnings


def _is_trivial_stmt(node: ast.AST) -> bool:
    """Проверяет, является ли statement тривиальным (pass, docstring, print)."""
    if isinstance(node, ast.Pass):
        return True
    if isinstance(node, ast.Expr):
        # Строковые литералы (docstrings)
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return True
        # print(...) вызовы
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            if node.value.func.id == "print":
                return True
    return False


def _is_stub_body(stmts: list) -> bool:
    """Проверяет что список statements — это заглушка."""
    if len(stmts) == 1:
        s = stmts[0]
        # pass
        if isinstance(s, ast.Pass):
            return True
        # ... (Ellipsis)
        if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and s.value.value is ...:
            return True
        # raise NotImplementedError(...)
        if isinstance(s, ast.Raise) and s.exc:
            if isinstance(s.exc, ast.Call) and isinstance(s.exc.func, ast.Name):
                if s.exc.func.id == "NotImplementedError":
                    return True
            if isinstance(s.exc, ast.Name) and s.exc.id == "NotImplementedError":
                return True
        # try: pass/print except: pass/print (заглушка обёрнутая в try)
        if isinstance(s, ast.Try):
            try_effective = [st for st in s.body if not _is_trivial_stmt(st)]
            if not try_effective:
                return True
    return False


def _is_hardcoded_return_stub(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Проверяет: функция с параметрами возвращает захардкоженный литерал,
    не используя ни один параметр в теле. Это фиктивная реализация.

    Пример: def recognize_plate(image: bytes) -> str: return 'ABC123'
    НЕ флагует: def get_version() -> str: return "1.0" (нет параметров)
    НЕ флагует: def process(x): return x.upper() (параметр используется)
    """
    # Собираем имена параметров (кроме self/cls)
    param_names: set[str] = set()
    for arg in func_node.args.args + func_node.args.posonlyargs + func_node.args.kwonlyargs:
        if arg.arg not in ("self", "cls"):
            param_names.add(arg.arg)
    if func_node.args.vararg:
        param_names.add(func_node.args.vararg.arg)
    if func_node.args.kwarg:
        param_names.add(func_node.args.kwarg.arg)

    # Нет параметров (кроме self/cls) → getter/константа → не флагуем
    if not param_names:
        return False

    # Пропускаем docstring
    body = func_node.body
    if (body and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)):
        body = body[1:]

    if not body:
        return False

    def _is_empty_literal(val: ast.AST) -> bool:
        """Проверяет что AST-узел — пустой/захардкоженный литерал."""
        if isinstance(val, ast.Constant):
            return True
        if isinstance(val, (ast.List, ast.Dict, ast.Tuple)):
            elts = getattr(val, "elts", None) or []
            keys = getattr(val, "keys", None) or []
            vals = getattr(val, "values", None) or []
            if not elts and not keys:
                return True  # [], {}, ()
            if isinstance(val, (ast.List, ast.Tuple)) and all(isinstance(e, ast.Constant) for e in elts):
                return True  # ['ABC123'], [0, 0, 0]
            if isinstance(val, ast.Dict) and keys and all(isinstance(k, ast.Constant) for k in keys) and all(isinstance(v, ast.Constant) for v in vals):
                return True  # {"plate": "ABC123", "confidence": 0.99}
        return False

    # Паттерн 1: ровно один statement — return <literal>
    if len(body) == 1:
        stmt = body[0]
        if isinstance(stmt, ast.Return) and stmt.value is not None and _is_empty_literal(stmt.value):
            for node in ast.walk(func_node):
                if isinstance(node, ast.Name) and node.id in param_names:
                    return False
            return True

    # Паттерн 2: var = <empty_literal>; return var (без использования параметров)
    # Ловит: vehicles = []; return vehicles
    if 1 < len(body) <= 3:
        last = body[-1]
        if isinstance(last, ast.Return) and isinstance(last.value, ast.Name):
            ret_var = last.value.id
            # Проверяем что переменная инициализирована пустым литералом
            for stmt in body[:-1]:
                if (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                        and isinstance(stmt.targets[0], ast.Name)
                        and stmt.targets[0].id == ret_var
                        and _is_empty_literal(stmt.value)):
                    # Переменная = пустой литерал, return переменная
                    for node in ast.walk(func_node):
                        if isinstance(node, ast.Name) and node.id in param_names:
                            return False
                    return True

    return False


def check_function_preservation(
    new_code: str, old_code: str, feedback: str,
    file_contract: list | None = None,
) -> list[str]:
    """Детерминистская проверка: не потерял ли новый код функции/классы из предыдущей версии.

    Сравнивает top-level function/class names между old и new.
    Если имя исчезло и НЕ упомянуто в feedback → авто-REJECT.
    Приватные имена (_prefix) игнорируются.
    Функции, которых нет в текущем A5 контракте, тоже игнорируются
    (A5 мог измениться после revise_spec).
    Возвращает список предупреждений (пустой если всё ОК).
    """
    if not old_code:
        return []

    def _extract_top_names(code: str) -> set[str]:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            names = set(re.findall(r'^class\s+(\w+)', code, re.MULTILINE))
            names.update(re.findall(r'^(?:async\s+)?def\s+(\w+)', code, re.MULTILINE))
            return names
        names: set[str] = set()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names.add(node.name)
            elif isinstance(node, ast.ClassDef):
                names.add(node.name)
        return names

    old_names = _extract_top_names(old_code)
    new_names = _extract_top_names(new_code)
    disappeared = old_names - new_names
    if not disappeared:
        return []

    # Имена, ожидаемые текущим A5 контрактом (может быть под ключами name/class/function)
    contract_names: set[str] = set()
    if file_contract:
        for item in file_contract:
            if isinstance(item, dict):
                for key in ("name", "class", "function"):
                    n = item.get(key, "")
                    if n:
                        contract_names.add(n)

    # Фильтруем: имена упомянутые в feedback + приватные + не в текущем A5
    feedback_lower = feedback.lower() if feedback else ""
    warnings: list[str] = []
    for name in sorted(disappeared):
        if name.startswith("_"):
            continue
        if feedback_lower and re.search(rf'\b{re.escape(name.lower())}\b', feedback_lower):
            continue
        # Если функции нет в текущем A5 — значит A5 изменился, удаление допустимо
        if contract_names and name not in contract_names:
            continue
        warnings.append(
            f"функция/класс '{name}' из предыдущей версии УДАЛЕНА, "
            f"но НЕ упоминается в фидбэке. Верни её обратно."
        )
    return warnings


def check_contract_compliance(code: str, file_contract: list) -> list[str]:
    """Детерминистская проверка: содержит ли код ВСЕ required функции/классы из A5 контракта.
    Возвращает список отсутствующих элементов с сигнатурой для подсказки модели.
    При fuzzy-match показывает: "Ты определил X, но ожидается Y — ПЕРЕИМЕНУЙ"."""
    if not file_contract:
        return []
    # Извлекаем все определённые в коде имена функций и классов
    code_func_names: list[str] = re.findall(r'^\s*(?:async\s+)?def\s+(\w+)\s*\(', code, re.MULTILINE)
    code_class_names: list[str] = re.findall(r'^\s*class\s+(\w+)\b', code, re.MULTILINE)
    all_code_names = code_func_names + code_class_names

    missing = []
    for item in file_contract:
        if not item.get("required", False):
            continue
        sig = item.get("signature", "")
        name = item.get("name", "")
        if sig.startswith("class "):
            class_name = sig.split("class ", 1)[1].split("(")[0].split(":")[0].strip()
            if not re.search(rf'^class\s+{re.escape(class_name)}\b', code, re.MULTILINE):
                hint = _fuzzy_name_hint(class_name, all_code_names)
                missing.append(f"ОТСУТСТВУЕТ: {sig} — добавь определение класса {class_name}{hint}")
        elif sig.startswith("def ") or sig.startswith("async def "):
            func_name = name or sig.split("def ", 1)[1].split("(")[0].strip()
            # Ищем как top-level функцию (^def) так и метод класса (с отступом)
            if not re.search(rf'^\s*(?:async\s+)?def\s+{re.escape(func_name)}\s*\(', code, re.MULTILINE):
                hint = _fuzzy_name_hint(func_name, all_code_names)
                missing.append(f"ОТСУТСТВУЕТ: {sig} — добавь эту функцию ИМЕННО с таким именем{hint}")
    return missing


def _fuzzy_name_hint(expected: str, code_names: list[str]) -> str:
    """Если в коде есть похожее имя — вернуть подсказку для переименования."""
    if not code_names:
        return ""
    matches = difflib.get_close_matches(expected, code_names, n=1, cutoff=0.5)
    if matches and matches[0] != expected:
        return (
            f"\n    ⚠️ ПОХОЖЕЕ ИМЯ В КОДЕ: '{matches[0]}' — но ожидается '{expected}'. "
            f"ПЕРЕИМЕНУЙ '{matches[0]}' → '{expected}'"
        )
    return ""


def classify_test_error(
    stderr: str, stdout: str, project_files: list[str],
) -> tuple[str, str]:
    """Классифицирует ошибку unit-тестов: 'test_bug' или 'app_bug'.

    test_bug — проблема в самих тестах (неправильный mock, import, assert).
    app_bug — проблема в коде приложения (функция возвращает не то, отсутствует метод).

    Возвращает (classification, failing_app_file_or_empty).
    """
    combined = stderr + "\n" + stdout

    # Все файлы из traceback (в порядке появления)
    all_traceback_files = re.findall(
        r'File "[^"]*[/\\]([^"]+\.py)", line \d+', combined
    )
    test_file_errors = [f for f in all_traceback_files if f.startswith("test_")]
    app_file_errors = [f for f in all_traceback_files
                       if f in project_files and not f.startswith("test_")]

    # Типичные ошибки тестов (проблема в тест-коде, не в приложении)
    test_bug_indicators = [
        "ModuleNotFoundError",
        "ImportError: cannot import name",
        "does not have the attribute",
        "fixture",
        "assert_called",
        "TypeError: test_",
    ]

    test_bug_score = 0
    app_bug_score = 0

    if test_file_errors:
        test_bug_score += len(test_file_errors) * 2
    if app_file_errors:
        app_bug_score += len(app_file_errors) * 2

    for indicator in test_bug_indicators:
        if indicator in combined:
            test_bug_score += 3

    # AssertionError: если traceback в app файлах → app_bug, иначе → test_bug
    if "AssertionError" in combined:
        if app_file_errors:
            app_bug_score += 2
        else:
            test_bug_score += 1

    # Ключевая эвристика: ПОСЛЕДНИЙ файл в traceback — причина ошибки.
    # Если это app файл → app_bug (ошибка упала ВНУТРИ кода приложения).
    if all_traceback_files:
        last_file = all_traceback_files[-1]
        if last_file in project_files and not last_file.startswith("test_"):
            app_bug_score += 5  # Сильный сигнал: exception возник в коде приложения

    failing_app_file = app_file_errors[-1] if app_file_errors else ""

    if test_bug_score >= app_bug_score:
        return "test_bug", ""
    return "app_bug", failing_app_file

```
### 📄 `code_context.py`

```python
import ast
import os
import re
import sys
from collections import defaultdict, deque
from pathlib import Path

from config import MAX_CONTEXT_CHARS


def _levenshtein_close(a: str, b: str) -> bool:
    """Проверка: compound-имена похожи (общие сегменты по '_').

    vehicle_processing vs video_processing → True (общий сегмент 'processing')
    numpy vs video_processing → False
    """
    parts_a = set(a.split("_"))
    parts_b = set(b.split("_"))
    common = parts_a & parts_b
    # Считаем похожим если есть хотя бы 1 общий значимый сегмент (>2 символов)
    return any(len(p) > 2 for p in common)


def extract_public_api(code: str) -> str:
    """Извлекает публичный API файла: импорты, классы, функции, публичные переменные."""
    api_lines: list[str] = []
    total = 0
    PUBLIC_PREFIXES = (
        "import ", "from ", "class ", "def ",
        "fn ", "pub fn ", "pub struct ", "pub enum ",
        "export ", "const ", "let ", "function ",
    )
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith(PUBLIC_PREFIXES):
            api_lines.append(line)
            total += len(line)
        elif (
            not line.startswith((" ", "\t"))
            and "=" in stripped
            and not stripped.startswith(("_", "#", "//"))
        ):
            api_lines.append(line)
            total += len(line)
        if total >= MAX_CONTEXT_CHARS:
            api_lines.append("# [... обрезано ...]")
            break
    return "\n".join(api_lines)


def get_global_context(
    src_path: Path,
    files: list[str],
    exclude: str | None = None,
) -> str:
    """Читает файлы из src_path и возвращает их публичный API в виде строки."""
    parts: list[str] = []
    total = 0
    for fname in files:
        if exclude is not None and fname == exclude:
            continue
        fpath = src_path / fname
        if not fpath.exists():
            continue
        try:
            api = extract_public_api(fpath.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        chunk = f"\n--- {fname} PUBLIC API ---\n{api}\n"
        if total + len(chunk) > MAX_CONTEXT_CHARS:
            remaining = MAX_CONTEXT_CHARS - total
            if remaining > 200:
                parts.append(chunk[:remaining] + "\n[... обрезано ...]")
            break
        parts.append(chunk)
        total += len(chunk)
    return "".join(parts)


def get_full_context(
    src_path: Path,
    files: list[str],
) -> str:
    """Читает ПОЛНЫЙ код файлов для E2E ревью (не только API)."""
    parts: list[str] = []
    total = 0
    for fname in files:
        fpath = src_path / fname
        if not fpath.exists():
            continue
        try:
            code = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        chunk = f"\n--- {fname} ---\n{code}\n"
        if total + len(chunk) > MAX_CONTEXT_CHARS:
            remaining = MAX_CONTEXT_CHARS - total
            if remaining > 200:
                parts.append(chunk[:remaining] + "\n[... обрезано ...]")
            break
        parts.append(chunk)
        total += len(chunk)
    return "".join(parts)


def build_dependency_order(files: list[str], src_path: Path) -> list[str]:
    """Возвращает файлы в порядке топологической сортировки по импортам."""
    graph: dict[str, list[str]]  = defaultdict(list)
    indegree: dict[str, int]     = {f: 0 for f in files}
    file_set = set(files)

    for f in files:
        fpath = src_path / f
        if not fpath.exists():
            continue
        try:
            code = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        imports = (
            re.findall(r"from\s+(\S+)\s+import", code)
            + re.findall(r"^import\s+([\w.]+)", code, re.MULTILINE)
            + re.findall(r"require\(['\"]([^'\"]+)['\"]", code)
            + re.findall(r"\buse\s+([\w:]+)", code)
        )
        ext = Path(f).suffix
        for imp in imports:
            dep = imp.split(".")[0] + ext
            if dep in file_set and dep != f:
                graph[dep].append(f)
                indegree[f] += 1

    q: deque[str] = deque(f for f in files if indegree[f] == 0)
    order: list[str] = []
    while q:
        curr = q.popleft()
        order.append(curr)
        for dep in graph[curr]:
            indegree[dep] -= 1
            if indegree[dep] == 0:
                q.append(dep)

    if len(order) < len(files):
        order.extend(f for f in files if f not in order)
    return order


def find_failing_file(stderr: str, stdout: str, files: list[str]) -> str:
    """Определяет файл с ошибкой по traceback. Возвращает имя файла или files[0]."""
    combined = stderr + "\n" + stdout
    # Python: File "path/file.py", line N
    for match in re.findall(r'File "([^"]+)", line \d+', combined):
        candidate = os.path.basename(match)
        if candidate in files:
            return candidate
    # TypeScript/Node: at ... (file.ts:10:5) or at ... file.js:10:5
    for match in re.findall(r'[( ]([\w/\-\.]+\.(?:ts|js|tsx|jsx)):\d+:\d+', combined):
        candidate = os.path.basename(match)
        if candidate in files:
            return candidate
    # Rust: --> src/file.rs:10:5 or src/file.rs:10
    for match in re.findall(r'(?:-->|error\[).*?([\w/\-\.]+\.rs):\d+', combined):
        candidate = match  # Rust paths are often relative like src/main.rs
        if candidate in files:
            return candidate
        candidate = os.path.basename(match)
        if candidate in files:
            return candidate
    # Generic: FAILED/ERROR pattern
    for match in re.findall(r'(?:FAILED|ERROR)\s+([\w/]+\.\w+)', combined):
        src = os.path.basename(match).replace("test_", "")
        if src in files:
            return src
    return files[0] if files else "main.py"


# ─────────────────────────────────────────────
# Детерминистская валидация импортов
# ─────────────────────────────────────────────

# Маппинг pip-пакет → import-имя (для пакетов, где они различаются)
PIP_TO_IMPORT: dict[str, str] = {
    "opencv-python":            "cv2",
    "opencv-python-headless":   "cv2",
    "opencv-contrib-python":    "cv2",
    "opencv-contrib-python-headless": "cv2",
    "pillow":                   "PIL",
    "scikit-learn":             "sklearn",
    "scikit-image":             "skimage",
    "python-dateutil":          "dateutil",
    "pyyaml":                   "yaml",
    "beautifulsoup4":           "bs4",
    "python-dotenv":            "dotenv",
    "attrs":                    "attr",
    "python-jose":              "jose",
    "python-multipart":         "multipart",
    "msgpack-python":           "msgpack",
    "ruamel.yaml":              "ruamel",
    "pyjwt":                    "jwt",
    "python-telegram-bot":      "telegram",
    "psycopg2-binary":          "psycopg2",
    "google-api-python-client": "googleapiclient",
    "python-magic":             "magic",
    "python-pptx":              "pptx",
    "python-docx":              "docx",
    "websocket-client":         "websocket",
    "pyserial":                 "serial",
    "python-rapidjson":         "rapidjson",
    "python-snappy":            "snappy",
    "python-ldap":              "ldap",
    "python-Levenshtein":       "Levenshtein",
    "mysql-connector-python":   "mysql",
    "mysqlclient":              "MySQLdb",
    "cx-Oracle":                "cx_Oracle",
    "grpcio":                   "grpc",
    "grpcio-tools":             "grpc_tools",
    "Twisted":                  "twisted",
    "twisted":                  "twisted",
    "Pygments":                 "pygments",
    "pygments":                 "pygments",
    "Faker":                    "faker",
    "faker":                    "faker",
    "Cython":                   "cython",
    "cython":                   "cython",
    "PyJWT":                    "jwt",
}

# Невалидные pip-пакеты, которые LLM часто галлюцинирует.
# wrong_pip_name → (correct_pip_name, correct_import_name)
WRONG_PIP_PACKAGES: dict[str, tuple[str, str]] = {
    "opencv":                    ("opencv-python-headless", "cv2"),
    "cv2":                       ("opencv-python-headless", "cv2"),
    "tensorflow-gpu":            ("tensorflow",             "tensorflow"),
    "sklearn":                   ("scikit-learn",           "sklearn"),
    "bs4":                       ("beautifulsoup4",         "bs4"),
    "yaml":                      ("pyyaml",                 "yaml"),
    "attr":                      ("attrs",                  "attr"),
    "dotenv":                    ("python-dotenv",          "dotenv"),
    "jwt":                       ("pyjwt",                  "jwt"),
    "serial":                    ("pyserial",               "serial"),
    "PIL":                       ("pillow",                 "PIL"),
    "dateutil":                  ("python-dateutil",        "dateutil"),
}

# Известные транзитивные зависимости: пакет из requirements.txt → {import-имена}
# Если tensorflow в requirements.txt → numpy, keras, h5py тоже валидные импорты
_KNOWN_TRANSITIVE_DEPS: dict[str, set[str]] = {
    "tensorflow":              {"numpy", "keras", "h5py", "absl", "google"},
    "tensorflow_gpu":          {"numpy", "keras", "h5py", "absl", "google"},
    "opencv_python":           {"numpy"},
    "opencv_python_headless":  {"numpy"},
    "opencv_contrib_python":   {"numpy"},
    "opencv_contrib_python_headless": {"numpy"},
    "scipy":                   {"numpy"},
    "pandas":                  {"numpy"},
    "scikit_learn":            {"numpy", "scipy", "joblib"},
    "torch":                   {"numpy"},
    "torchvision":             {"numpy", "torch"},
    "matplotlib":              {"numpy"},
    "seaborn":                 {"numpy", "matplotlib"},
    "jax":                     {"numpy", "jaxlib"},
    "xgboost":                 {"numpy", "scipy"},
}


def parse_requirements(path: Path) -> set[str]:
    """Парсит requirements.txt и возвращает множество допустимых import-имён."""
    if not path.exists():
        return set()
    result: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Убираем маркеры окружения: requests ; python_version >= "3.6"
        line = line.split(";")[0].strip()
        # Извлекаем имя пакета (до ==, >=, <=, ~=, !=, [extras])
        pkg = re.split(r"[=<>~!\[]", line)[0].strip()
        if not pkg:
            continue
        pkg_lower = pkg.lower()
        # Пропускаем невалидные pip-пакеты (LLM-галлюцинации)
        if pkg in WRONG_PIP_PACKAGES:
            correct_pip, correct_import = WRONG_PIP_PACKAGES[pkg]
            result.add(correct_import.lower())
            result.add(correct_pip.lower().replace("-", "_"))
            continue
        # Нормализация: pip нормализует дефисы в подчёркивания
        pkg_normalized = pkg_lower.replace("-", "_")
        result.add(pkg_normalized)
        # Маппинг pip→import для известных расхождений
        # PIP_TO_IMPORT keys могут быть в любом регистре (Twisted, Pygments...)
        _pip_import = PIP_TO_IMPORT.get(pkg_lower) or PIP_TO_IMPORT.get(pkg)
        if _pip_import:
            result.add(_pip_import.lower())
        # Также добавляем оригинальное имя (без нормализации)
        result.add(pkg_lower)
        # Транзитивные зависимости (numpy для tensorflow/opencv и т.д.)
        if pkg_normalized in _KNOWN_TRANSITIVE_DEPS:
            result.update(_KNOWN_TRANSITIVE_DEPS[pkg_normalized])
    return result


def _get_stdlib_modules() -> frozenset[str]:
    """Возвращает множество имён стандартной библиотеки Python."""
    if hasattr(sys, "stdlib_module_names"):
        return sys.stdlib_module_names  # Python 3.10+
    # Fallback для Python < 3.10 — основные модули
    return frozenset({
        "abc", "argparse", "ast", "asyncio", "atexit", "base64", "bisect",
        "builtins", "calendar", "cmath", "codecs", "collections", "concurrent",
        "configparser", "contextlib", "copy", "csv", "ctypes", "dataclasses",
        "datetime", "decimal", "difflib", "dis", "email", "encodings", "enum",
        "errno", "faulthandler", "fcntl", "filecmp", "fileinput", "fnmatch",
        "fractions", "ftplib", "functools", "gc", "getpass", "gettext", "glob",
        "gzip", "hashlib", "heapq", "hmac", "html", "http", "idlelib",
        "importlib", "inspect", "io", "ipaddress", "itertools", "json",
        "keyword", "lib2to3", "linecache", "locale", "logging", "lzma",
        "mailbox", "math", "mimetypes", "mmap", "multiprocessing", "netrc",
        "numbers", "operator", "os", "pathlib", "pdb", "pickle", "pkgutil",
        "platform", "plistlib", "poplib", "posixpath", "pprint", "profile",
        "pstats", "py_compile", "pyclbr", "pydoc", "queue", "quopri",
        "random", "re", "readline", "reprlib", "resource", "rlcompleter",
        "runpy", "sched", "secrets", "select", "selectors", "shelve",
        "shlex", "shutil", "signal", "site", "smtplib", "sndhdr", "socket",
        "socketserver", "sqlite3", "ssl", "stat", "statistics", "string",
        "struct", "subprocess", "sunau", "symtable", "sys", "sysconfig",
        "syslog", "tabnanny", "tarfile", "tempfile", "termios", "test",
        "textwrap", "threading", "time", "timeit", "tkinter", "token",
        "tokenize", "tomllib", "trace", "traceback", "tracemalloc", "tty",
        "turtle", "turtledemo", "types", "typing", "unicodedata", "unittest",
        "urllib", "uuid", "venv", "warnings", "wave", "weakref", "webbrowser",
        "wsgiref", "xml", "xmlrpc", "zipapp", "zipfile", "zipimport", "zlib",
        "_thread",
    })


def find_name_in_classes(code: str, name: str) -> str | None:
    """Ищет имя как метод/атрибут класса в коде. Возвращает имя класса или None.

    Используется для улучшения фидбэка: если `from X import Y` невалиден,
    но Y — метод класса Z в X, подсказываем `from X import Z`.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if item.name == name:
                    return node.name
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == name:
                        return node.name
            elif isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name) and item.target.id == name:
                    return node.name
    return None


def get_top_level_names(code: str) -> set[str]:
    """Извлекает только TOP-LEVEL определения из Python-кода через AST.

    Обходит ТОЛЬКО tree.body (не вложенные узлы).
    Собирает: FunctionDef.name, ClassDef.name, Assign targets, Import/ImportFrom aliases.
    При SyntaxError — fallback на regex.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        names = set(re.findall(r"^class\s+(\w+)", code, re.MULTILINE))
        names.update(re.findall(r"^def\s+(\w+)", code, re.MULTILINE))
        names.update(re.findall(r"^async\s+def\s+(\w+)", code, re.MULTILINE))
        names.update(re.findall(r"^(\w+)\s*=", code, re.MULTILINE))
        return names

    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, ast.ClassDef):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
                elif isinstance(target, (ast.Tuple, ast.List)):
                    for elt in ast.walk(target):
                        if isinstance(elt, ast.Name):
                            names.add(elt.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    names.add(alias.asname or alias.name)
        # Python 3.12+: type X = ... (TypeAlias)
        elif hasattr(ast, "TypeAlias") and isinstance(node, ast.TypeAlias):
            names.add(node.name.id if isinstance(node.name, ast.Name) else str(node.name))
    return names


def _get_all_bound_names(code: str) -> set[str]:
    """Извлекает ВСЕ связанные имена из Python-кода через AST.

    Покрывает: присвоения (на любом уровне вложенности), параметры функций,
    имена классов/функций, for-loop переменные, with-as, except-as, import aliases.
    При SyntaxError — fallback на regex.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        # Fallback: regex с захватом indented assignments
        names = set(re.findall(r"^(?:class|def)\s+(\w+)", code, re.MULTILINE))
        names.update(re.findall(r"^\s*(\w+)\s*=", code, re.MULTILINE))
        return names

    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
            for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
                names.add(arg.arg)
            if node.args.vararg:
                names.add(node.args.vararg.arg)
            if node.args.kwarg:
                names.add(node.args.kwarg.arg)
        elif isinstance(node, ast.ClassDef):
            names.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.asname or alias.name)
        # except SomeError as e → e
        elif isinstance(node, ast.ExceptHandler) and node.name:
            names.add(node.name)
    return names


def _check_circular_imports(
    code: str,
    filename: str,
    project_files: list[str],
    project_modules: set[str],
    src_path: Path,
) -> list[str]:
    """DFS-поиск циклических импортов через граф проектных файлов."""
    current_stem = Path(filename).stem
    stem_to_file = {Path(f).stem: f for f in project_files}

    def _get_project_imports(file_stem: str, override_code: str | None = None) -> set[str]:
        if override_code is not None:
            fc = override_code
        else:
            target_fname = stem_to_file.get(file_stem)
            if not target_fname:
                return set()
            fp = src_path / target_fname
            if not fp.exists():
                return set()
            try:
                fc = fp.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                return set()
        fi = re.findall(r"^\s*from\s+(\S+)\s+import", fc, re.MULTILINE)
        di = re.findall(r"^\s*import\s+([\w.]+)", fc, re.MULTILINE)
        bases: set[str] = set()
        for imp in fi + di:
            b = imp.split(".")[0]
            if b == "":
                rel = imp.lstrip(".").split(".")[0]
                if rel:
                    bases.add(rel)
            else:
                bases.add(b)
        return (bases & project_modules) - {file_stem}

    my_deps = _get_project_imports(current_stem, override_code=code)
    visited: set[str] = set()
    stack = [(dep, [current_stem, dep]) for dep in my_deps]
    while stack:
        node, path = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        node_deps = _get_project_imports(node)
        if current_stem in node_deps:
            cycle_path = " → ".join(path + [current_stem])
            return [
                f"циклический импорт: {cycle_path} "
                f"(файлы импортируют друг друга по кругу)"
            ]
        for nd in node_deps:
            if nd not in visited:
                stack.append((nd, path + [nd]))
    return []


def _check_undefined_refs(
    code: str,
    filename: str,
    direct_imports: list[str],
    stdlib: set[str],
    pip_packages: set[str],
) -> list[str]:
    """Проверяет undefined module references: name.attr где name не импортирован."""
    imported_names: set[str] = set()
    # Только "import X" делает X доступным как namespace
    # "from X import Y" НЕ делает X доступным
    for imp in direct_imports:
        base = imp.split(".")[0]
        if base:
            imported_names.add(base)
    imported_names.update({"self", "cls", "super", "type", "print", "len", "range",
                           "str", "int", "float", "bool", "list", "dict", "set",
                           "tuple", "None", "True", "False", "Exception"})
    imported_names.update(_get_all_bound_names(code))

    warnings: list[str] = []
    seen_refs: set[str] = set()
    try:
        attr_tree = ast.parse(code)
        for node in ast.walk(attr_tree):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                ref_name = node.value.id
                if ref_name in imported_names or ref_name in seen_refs:
                    continue
                if ref_name in stdlib or ref_name in pip_packages:
                    continue
                seen_refs.add(ref_name)
                warnings.append(
                    f"undefined reference '{ref_name}' в {filename}: "
                    f"используется как '{ref_name}.…' но не импортирован "
                    f"(добавь import или from ... import)"
                )
    except SyntaxError:
        pass
    return warnings


def validate_imports(
    code: str,
    filename: str,
    project_files: list[str],
    requirements_path: Path | None = None,
    language: str = "python",
    src_path: Path | None = None,
) -> list[str]:
    """Детерминистская проверка импортов в сгенерированном коде.

    Проверяет что каждый импортируемый модуль — это:
    - файл проекта (project_files)
    - модуль stdlib
    - пакет из requirements.txt

    Также проверяет циклические импорты (если src_path задан).

    Возвращает список предупреждений (пустой если всё OK).
    """
    if language != "python":
        return []  # Пока только Python

    warnings: list[str] = []
    stdlib = _get_stdlib_modules()
    pip_packages = parse_requirements(requirements_path) if requirements_path else set()

    # Множество имён проектных модулей (без расширения)
    project_modules = {Path(f).stem for f in project_files}

    # Парсим импорты из кода
    from_imports = re.findall(r"^\s*from\s+(\S+)\s+import", code, re.MULTILINE)
    # Ловим все модули из "import X" и "import X, Y, Z"
    direct_imports = []
    for imp_line in re.findall(r"^\s*import\s+(.+)$", code, re.MULTILINE):
        for part in imp_line.split(","):
            mod = part.strip().split()[0].split(".")[0] if part.strip() else ""
            if mod:
                direct_imports.append(mod)

    seen: set[str] = set()
    for imp in from_imports + direct_imports:
        # Базовый модуль (до первой точки): from os.path → os
        base = imp.split(".")[0]

        # Relative imports: from .data_models → base="", imp=".data_models"
        # Извлекаем реальное имя модуля
        if base == "":
            # from . import X → пропускаем (текущий пакет)
            rel_module = imp.lstrip(".")
            if not rel_module:
                continue
            # from .data_models import Y → rel_module = "data_models"
            rel_base = rel_module.split(".")[0]
            if rel_base in seen:
                continue
            seen.add(rel_base)
            # Relative import ОБЯЗАН ссылаться на файл проекта
            if rel_base not in project_modules:
                warnings.append(
                    f"relative import 'from {imp} import ...' в {filename}: "
                    f"модуль '{rel_base}' не найден в файлах проекта ({', '.join(project_files)}). "
                    f"Используй абсолютный import или определи класс/функцию в одном из существующих файлов"
                )
            continue

        if base in seen:
            continue
        seen.add(base)

        # 1. Файл проекта?
        if base in project_modules:
            continue

        # 2. Stdlib?
        if base in stdlib:
            continue

        # 3. pip-пакет из requirements.txt?
        base_lower = base.lower()
        base_normalized = base_lower.replace("-", "_")
        if base_lower in pip_packages or base_normalized in pip_packages:
            continue

        # 4. Общеизвестные встроенные модули с подчёркиванием
        if base in {"_thread", "_io", "_collections", "_abc", "_decimal",
                     "typing_extensions", "_operator", "_functools", "_heapq",
                     "_contextvars", "_signal", "_csv", "_json", "_datetime"}:
            continue

        # Подсказка: если phantom-имя похоже на один из файлов проекта
        hint = ""
        base_lower_nrm = base.lower().replace("-", "_")
        for pm in project_modules:
            # Точное совпадение с учётом типичных ошибок 7B-моделей
            if (base_lower_nrm in pm or pm in base_lower_nrm
                    or _levenshtein_close(base_lower_nrm, pm)):
                hint = f". Возможно, вы имели в виду: from {pm} import ..."
                break
        warnings.append(
            f"import '{base}' в {filename}: не найден в stdlib, "
            f"requirements.txt и файлах проекта ({', '.join(project_files)})"
            f"{hint}"
        )

    # Проверка циклических импортов
    if src_path:
        warnings.extend(_check_circular_imports(code, filename, project_files, project_modules, src_path))

    # Проверка self-referencing assignments: func = func
    self_refs = re.findall(r"^(\w+)\s*=\s*(\w+)\s*(?:#.*)?$", code, re.MULTILINE)
    for lhs, rhs in self_refs:
        if lhs == rhs:
            warnings.append(
                f"бессмысленное присвоение '{lhs} = {lhs}' в {filename}: "
                f"переменная ссылается на саму себя (возможно, пропущен import)"
            )

    # Проверка undefined module references
    warnings.extend(_check_undefined_refs(code, filename, direct_imports, stdlib, pip_packages))

    return warnings


def _collect_class_members(target_code: str) -> dict[str, set[str]]:
    """Собирает {class_name: {methods, attributes}} из кода файла с учётом наследования."""
    try:
        target_tree = ast.parse(target_code)
    except SyntaxError:
        return {}
    file_classes: dict[str, set[str]] = {}
    file_bases: dict[str, list[str]] = {}
    for tnode in target_tree.body:
        if isinstance(tnode, ast.ClassDef):
            members: set[str] = set()
            for item in tnode.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    members.add(item.name)
                elif isinstance(item, ast.Assign):
                    for t in item.targets:
                        if isinstance(t, ast.Name):
                            members.add(t.id)
                elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    members.add(item.target.id)
            file_classes[tnode.name] = members
            file_bases[tnode.name] = [b.id for b in tnode.bases if isinstance(b, ast.Name)]
    # Наследование: добавляем members из базовых классов того же файла
    for cls_name, bases in file_bases.items():
        for base_name in bases:
            if base_name in file_classes:
                file_classes[cls_name] |= file_classes[base_name]
    return file_classes


def _collect_imported_classes(
    tree: ast.Module,
    project_stems: dict[str, str],
    get_file_cached,
) -> dict[str, tuple[str, set[str]]]:
    """Собирает информацию об импортированных классах из проектных файлов.

    Возвращает {local_alias: (source_stem, class_methods)}.
    """
    imported: dict[str, tuple[str, set[str]]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        module_stem = node.module.split(".")[0]
        if module_stem not in project_stems:
            continue
        cached = get_file_cached(module_stem)
        if cached is None:
            continue
        _, target_code = cached
        file_classes = _collect_class_members(target_code)
        for cls_name, cls_methods in file_classes.items():
            for alias in node.names:
                if alias.name == cls_name:
                    local_name = alias.asname or alias.name
                    imported[local_name] = (module_stem, cls_methods)
    return imported


def _validate_method_calls(
    tree: ast.Module,
    imported_classes: dict[str, tuple[str, set[str]]],
    project_stems: dict[str, str],
) -> list[str]:
    """Проверяет что instance.method() вызовы используют существующие методы."""
    if not imported_classes:
        return []

    # variable = ClassName(...) → variable type is ClassName
    instance_types: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Name) and node.value.func.id in imported_classes:
                    instance_types[target.id] = node.value.func.id
            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                if target.value.id == "self" and isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name) and node.value.func.id in imported_classes:
                        instance_types[f"self.{target.attr}"] = node.value.func.id

    warnings: list[str] = []
    seen: set[str] = set()
    for node in ast.walk(tree):
        # var.method()
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            var_name = node.value.id
            method_name = node.attr
            class_name = instance_types.get(var_name)
            if not class_name or method_name.startswith("_"):
                continue
            source_stem, cls_methods = imported_classes[class_name]
            wkey = f"{var_name}.{method_name}"
            if method_name not in cls_methods and wkey not in seen:
                seen.add(wkey)
                public = sorted(m for m in cls_methods if not m.startswith("_") and m != "__init__")
                warnings.append(
                    f"{var_name}.{method_name}(): метод '{method_name}' не найден "
                    f"в классе {class_name} из {project_stems[source_stem]}. "
                    f"Доступные методы: {', '.join(public) if public else '(нет)'}"
                )
        # self.x.method()
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Attribute):
            if isinstance(node.value.value, ast.Name) and node.value.value.id == "self":
                key = f"self.{node.value.attr}"
                class_name = instance_types.get(key)
                if not class_name or node.attr.startswith("_"):
                    continue
                source_stem, cls_methods = imported_classes[class_name]
                wkey = f"{key}.{node.attr}"
                if node.attr not in cls_methods and wkey not in seen:
                    seen.add(wkey)
                    public = sorted(m for m in cls_methods if not m.startswith("_") and m != "__init__")
                    warnings.append(
                        f"self.{node.value.attr}.{node.attr}(): метод '{node.attr}' не найден "
                        f"в классе {class_name} из {project_stems[source_stem]}. "
                        f"Доступные методы: {', '.join(public) if public else '(нет)'}"
                    )
    return warnings


def validate_cross_file_names(
    code: str,
    filename: str,
    project_files: list[str],
    src_path: Path,
) -> list[str]:
    """Детерминистская проверка: для каждого `from X import Y` где X — файл проекта,
    проверяет что Y действительно определён на top-level в X.

    Пропускает файлы, которые ещё не существуют на диске.
    Возвращает список предупреждений (пустой если всё ОК).
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    project_stems = {Path(f).stem: f for f in project_files}
    warnings: list[str] = []
    # Кэш прочитанных файлов: stem → (top_level_names, code) | None
    _cache: dict[str, tuple[set[str], str] | None] = {}

    def _get_for(stem: str) -> tuple[set[str], str] | None:
        if stem in _cache:
            return _cache[stem]
        target_file = project_stems.get(stem)
        if not target_file:
            _cache[stem] = None
            return None
        target_path = src_path / target_file
        if not target_path.exists():
            _cache[stem] = None
            return None
        try:
            target_code = target_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            _cache[stem] = None
            return None
        names = get_top_level_names(target_code)
        _cache[stem] = (names, target_code)
        return (names, target_code)

    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        module_stem = node.module.split(".")[0]
        if module_stem not in project_stems:
            continue
        # Не проверяем свой же файл
        if project_stems[module_stem] == filename:
            continue
        target_fname = project_stems[module_stem]
        cached = _get_for(module_stem)
        if cached is None:
            continue  # Файл ещё не написан — пропускаем
        target_names, target_code = cached
        for alias in node.names:
            if alias.name == "*":
                continue
            if alias.name not in target_names:
                # Проверяем: может это метод класса в целевом файле?
                owner_class = find_name_in_classes(target_code, alias.name)
                if owner_class:
                    warnings.append(
                        f"from {module_stem} import {alias.name}: "
                        f"'{alias.name}' — это МЕТОД класса {owner_class} в "
                        f"{project_stems[module_stem]}, а не top-level функция. "
                        f"ИСПРАВЬ: `from {module_stem} import {owner_class}`, "
                        f"затем вызывай `{owner_class}().{alias.name}(...)` или "
                        f"через экземпляр"
                    )
                else:
                    suggestions = sorted(target_names - {"__all__"})[:8]
                    warnings.append(
                        f"from {module_stem} import {alias.name}: "
                        f"'{alias.name}' не определён в {project_stems[module_stem]}. "
                        f"Доступные имена: {', '.join(suggestions) if suggestions else '(пусто)'}"
                    )

    # Проверяем что вызываемые методы на импортированных классах существуют
    imported_classes = _collect_imported_classes(tree, project_stems, _get_for)
    warnings.extend(_validate_method_calls(tree, imported_classes, project_stems))

    return warnings


# ── Builtins для фильтрации ────────────────────────────────────────────────────

_PYTHON_BUILTINS = {
    "True", "False", "None",
    "int", "float", "str", "bool", "bytes", "bytearray",
    "list", "dict", "set", "tuple", "frozenset",
    "type", "object", "super", "property", "classmethod", "staticmethod",
    "print", "len", "range", "enumerate", "zip", "map", "filter", "sorted",
    "min", "max", "sum", "abs", "round", "pow", "divmod",
    "isinstance", "issubclass", "hasattr", "getattr", "setattr", "delattr",
    "id", "hash", "repr", "format", "chr", "ord",
    "open", "input", "iter", "next", "reversed", "slice",
    "any", "all", "callable", "dir", "vars", "globals", "locals",
    "Exception", "BaseException", "ValueError", "TypeError", "KeyError",
    "IndexError", "AttributeError", "ImportError", "ModuleNotFoundError",
    "RuntimeError", "StopIteration", "FileNotFoundError", "IOError",
    "OSError", "NotImplementedError", "NameError", "ZeroDivisionError",
    "ConnectionError", "TimeoutError", "PermissionError", "UnicodeDecodeError",
    "SystemExit", "KeyboardInterrupt", "GeneratorExit",
}


def validate_project_consistency(
    src_path: Path,
    project_files: list[str],
) -> dict[str, list[str]]:
    """Детерминистская кросс-файловая проверка всего проекта.

    Строит таблицу символов проекта, затем для каждого файла:
    1. `from X import Y` → Y определён на top-level в X
    2. Type annotations ссылаются на импортированные/определённые/builtin имена

    Возвращает dict[filename → list[warnings]]. Пустой dict = всё ОК.
    """
    # 1. Строим таблицу символов проекта
    project_stems = {Path(f).stem: f for f in project_files}
    symbol_table: dict[str, set[str]] = {}  # stem → top-level names
    file_codes: dict[str, str] = {}  # filename → code

    for fname in project_files:
        fpath = src_path / fname
        if not fpath.exists():
            continue
        try:
            code = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        file_codes[fname] = code
        stem = Path(fname).stem
        symbol_table[stem] = get_top_level_names(code)

    issues: dict[str, list[str]] = {}

    # 2. Проверяем каждый файл
    for fname, code in file_codes.items():
        try:
            tree = ast.parse(code)
        except SyntaxError:
            continue

        file_warnings: list[str] = []
        file_stem = Path(fname).stem

        # 2a. Проверяем from X import Y
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or not node.module:
                continue
            module_stem = node.module.split(".")[0]
            if module_stem not in project_stems or module_stem == file_stem:
                continue
            if module_stem not in symbol_table:
                continue  # Файл не существует
            target_names = symbol_table[module_stem]
            target_fname = project_stems[module_stem]
            for alias in node.names:
                if alias.name == "*":
                    continue
                if alias.name not in target_names:
                    # Проверяем: может это метод класса?
                    target_code = file_codes.get(target_fname, "")
                    owner_class = find_name_in_classes(target_code, alias.name) if target_code else None
                    if owner_class:
                        file_warnings.append(
                            f"from {module_stem} import {alias.name}: "
                            f"'{alias.name}' — метод класса {owner_class} в "
                            f"{target_fname}. ИСПРАВЬ: from {module_stem} import {owner_class}"
                        )
                    else:
                        file_warnings.append(
                            f"from {module_stem} import {alias.name}: "
                            f"'{alias.name}' не определён в {target_fname}"
                        )

        # 2b. Проверяем type annotations на неимпортированные имена
        imported_names = _get_all_bound_names(code)
        annotation_names: set[str] = set()

        def _collect_annotation_names(ann_node):
            """Рекурсивно собирает все ast.Name из аннотации (включая list[X], Optional[X], X|Y)."""
            if ann_node is None:
                return
            for child in ast.walk(ann_node):
                if isinstance(child, ast.Name):
                    annotation_names.add(child.id)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
                    _collect_annotation_names(arg.annotation)
                _collect_annotation_names(node.returns)
            elif isinstance(node, ast.AnnAssign):
                _collect_annotation_names(node.annotation)

        # Фильтруем: убираем определённые/импортированные/builtin
        unresolved = annotation_names - imported_names - _PYTHON_BUILTINS
        for name in sorted(unresolved):
            # Ищем в таблице символов проекта
            found_in = None
            for stem, names in symbol_table.items():
                if stem == file_stem:
                    continue
                if name in names:
                    found_in = project_stems[stem]
                    break
            if found_in:
                file_warnings.append(
                    f"type annotation '{name}' не импортирован в {fname}. "
                    f"Определён в {found_in} — добавь импорт {name} из {Path(found_in).stem}"
                )

        if file_warnings:
            issues[fname] = file_warnings

    return issues

```
### 📄 `config.py`

```python
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# КОНФИГУРАЦИЯ — значения из окружения (.env)
# ─────────────────────────────────────────────

BASE_DIR     = Path(os.getenv("PROJECT_BASE_DIR", "/media/mikhail/RAD/py_proj"))
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1/")
LLM_API_KEY  = os.getenv("LLM_API_KEY",  "ollama")
LLM_TIMEOUT  = float(os.getenv("LLM_TIMEOUT", "300.0"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "16384"))
LLM_NUM_CTX    = int(os.getenv("LLM_NUM_CTX", "16384"))
LOG_LEVEL    = os.getenv("LOG_LEVEL", "INFO")

# ─────────────────────────────────────────────
# Параметры пайплайна (не секреты — хардкод OK)
# ─────────────────────────────────────────────

WAIT_TIMEOUT        = 30
RUN_TIMEOUT         = 6_000
MAX_CONTEXT_CHARS   = 60_000
MIN_COVERAGE        = 40
MAX_ABSOLUTE_ITERS  = 500
MAX_FILE_ATTEMPTS   = 15
MAX_TEST_ATTEMPTS   = 6      # Попытки регенерации тестов перед де-аппрувом кода
MAX_PHASE_TOTAL_FAILS = 90   # Абсолютный потолок фейлов одной фазы за весь проект
MAX_SPEC_REVISIONS    = 9    # Максимум пересмотров спецификации за проект
MAX_FEEDBACK_HISTORY = 3
MAX_A5_PATCHES_PER_FILE = 2   # Лимит патч-ресетов контракта A5 на файл
MAX_ITERS_DEFAULT       = 200 # Начальный max_iters для нового проекта
MAX_ITERS_INCREMENT     = 15  # Добавляем к max_iters при запросе продолжения
MAX_LLM_RETRIES         = 3   # Число retry для ask_agent
SELF_REFLECT_RETRIES    = 1   # max_retries для self_reflect (модель слабая)
FLUSH_EVERY = 20              # сбрасывать на диск каждые N записей

# Пороги безопасности фаз (сколько провалов до пропуска/эскалации)
MAX_ARCH_ATTEMPTS       = 5   # Попытки генерации архитектуры
MAX_A5_REVIEW_ATTEMPTS  = 3   # Попытки ревью A5 контракта
DEVELOP_STALL_THRESHOLD = 6   # develop без прогресса → revise_spec
E2E_TOTAL_SKIP          = 6   # E2E суммарных провалов → пропуск
E2E_CONSECUTIVE_REVISE  = 3   # E2E подряд → revise_spec
INTEGRATION_TOTAL_SKIP  = 4   # Integration суммарных провалов → пропуск
UNIT_TEST_TOTAL_SKIP    = 3   # Unit test суммарных провалов → пропуск
ITERS_BUMP_REVISE       = 10  # max_iters += N после revise_spec
ITERS_BUMP_SMALL        = 5   # max_iters += N при minor escalation

# ─────────────────────────────────────────────
# Лимиты отображения/усечения (символы)
# ─────────────────────────────────────────────
TRUNCATE_FEEDBACK  = 300      # усечение feedbacks в логах
TRUNCATE_CODE      = 3000     # усечение кода разработчика для контекста
TRUNCATE_LOG       = 2000     # усечение stdout/stderr в логах
TRUNCATE_ERROR_MSG = 400      # усечение текста ошибки в ValueError
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB ротация лог-файлов
LOG_INTERACTION_CHARS = 2000  # усечение в log_interaction

# Папки внутри project_path
FACTORY_DIR   = ".factory"       # метаданные — скрыто от Git и Docker
SRC_DIR       = "src"            # исходный код — чистый контекст
ARTIFACTS_DIR = "artifacts"      # A0–A10 внутри .factory/
LOGS_DIR      = "logs"           # логи взаимодействия агентов
CACHEABLE_AGENTS = {"business_analyst", "system_analyst", "architect", "documenter"}

ARTIFACT_LABELS = {
    "A0": "user_intent",
    "A1": "business_requirements",
    "A2": "system_specification",
    "A3": "architecture_map",
    "A4": "file_structure",
    "A5": "api_contract",
    "A6": "db_schema",
    "A7": "test_suite_plan",
    "A8": "ops_manifest",
    "A9": "implementation_logs",
    "A10": "final_summary",
}
```
### 📄 `contract.py`

```python
import json
import logging
from pathlib import Path

from config import TRUNCATE_CODE
from exceptions import LLMError
from llm import ask_agent
from json_utils import parse_if_str
from artifacts import save_artifact
from lang_utils import LANG_DISPLAY
from log_utils import get_model
from cache import ThreadSafeCache
from stats import ModelStats

from contract_validation import (
    _normalize_file_contracts,
    _inject_missing_data_models,
    run_a5_validation_pipeline,
)

# Re-exports: other modules import these from contract
from contract_validation import (  # noqa: F401
    validate_requirements_txt,
    _parse_import_line,
    _validate_data_model_coverage,
)


def _get_req_path(project_path: Path) -> Path:
    return project_path / "src" / "requirements.txt"


def _read_req_content(req_path: Path) -> str:
    return req_path.read_text(encoding="utf-8").strip() if req_path.exists() else "# пусто"


async def _validate_and_patch_contract(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    contract: dict,
    files: list[str],
    randomize: bool = False,
) -> dict:
    """
    Проверяет что все файлы из списка присутствуют в контракте.
    Для отсутствующих файлов запрашивает контракт отдельно.
    Защита от неполной генерации contract_analyst.
    """
    language = state.get("language", "python")
    contract = _normalize_file_contracts(contract)
    fc = contract.setdefault("file_contracts", {})
    gi = contract.setdefault("global_imports", {})

    missing = [f for f in files if f not in fc or not fc[f]]
    if not missing:
        return contract

    logger.warning(f"⚠️  A5 неполный — отсутствуют контракты для: {', '.join(missing)}")

    req_path = _get_req_path(project_path)
    req_content = _read_req_content(req_path)

    for fname in missing:
        logger.info(f"   🔧 Запрашиваю контракт для {fname} ...")
        existing_contracts = {k: v for k, v in fc.items() if k != fname}
        ctx = (
            f"Запрос: {state['task']}\n\n"
            f"Системная спецификация (A2):\n"
            f"{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
            f"Архитектура:\n{json.dumps(state.get('architecture', {}), ensure_ascii=False, indent=2)}\n\n"
            f"Язык: {LANG_DISPLAY.get(language, language)}\n\n"
            f"Доступные pip-пакеты (requirements.txt):\n{req_content}\n\n"
            f"Уже сгенерированные контракты других файлов:\n"
            f"{json.dumps(existing_contracts, ensure_ascii=False, indent=2)}\n\n"
            f"ЗАДАЧА: Сгенерируй API контракт ТОЛЬКО для файла `{fname}`.\n"
            f"Верни JSON с ключами file_contracts и global_imports только для этого файла."
        )
        try:
            patch = await ask_agent(logger, "contract_analyst", ctx, cache, 0, randomize, language)
            patch_fc = parse_if_str(patch.get("file_contracts", {}), dict, {})
            patch_gi = parse_if_str(patch.get("global_imports", {}), dict, {})

            file_contract = patch_fc.get(fname)
            if file_contract is None:
                file_contract = next(iter(patch_fc.values()), [])
            file_imports = patch_gi.get(fname)
            if file_imports is None:
                file_imports = next(iter(patch_gi.values()), [])

            if file_contract:
                fc[fname] = parse_if_str(file_contract, list, [])
                gi[fname] = parse_if_str(file_imports,  list, [])
                logger.info(f"   ✅ Контракт для {fname} получен ({len(fc[fname])} функций).")
                stats.record("contract_analyst", get_model("contract_analyst"), True)
            else:
                logger.warning(f"   ⚠️  Контракт для {fname} пустой — разработчик будет работать без него.")
                stats.record("contract_analyst", get_model("contract_analyst"), False)
        except (LLMError, ValueError) as e:
            logger.exception(f"Патч контракта для {fname} упал: {e}")
            stats.record("contract_analyst", get_model("contract_analyst"), False)

    contract["file_contracts"] = fc
    contract["global_imports"]  = gi
    return run_a5_validation_pipeline(
        contract, state.get("architecture", {}), files, logger,
        requirements_path=req_path if req_path.exists() else None,
    )


async def patch_contract_for_file(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    filename: str,
    developer_code: str,
    feedback: str,
    randomize: bool = False,
) -> bool:
    """
    Патчит A5 контракт для одного файла на основе фидбэка ревьюера.
    Вызывается когда файл не проходит ревью N раз подряд —
    значит контракт не соответствует реальности и нужно его починить.
    Возвращает True если контракт обновлён.
    """
    language = state.get("language", "python")
    contract = state.get("api_contract", {})
    fc = contract.get("file_contracts", {})
    gi = contract.get("global_imports", {})
    current = fc.get(filename, [])

    logger.info(f"🔧 Патч A5 для {filename} на основе фидбэка ревьюера ...")

    req_path = _get_req_path(project_path)
    req_content = _read_req_content(req_path)

    ctx = (
        f"Текущий API контракт (A5) для файла `{filename}`:\n"
        f"{json.dumps(current, ensure_ascii=False, indent=2)}\n\n"
        f"Код разработчика (НЕ прошёл ревью):\n{developer_code[:TRUNCATE_CODE]}\n\n"
        f"Замечания ревьюера (код отклонён из-за этих проблем):\n{feedback[:TRUNCATE_CODE // 2]}\n\n"
        f"Контракты ДРУГИХ файлов проекта (для called_by ссылок):\n"
        f"{json.dumps({k: v for k, v in fc.items() if k != filename}, ensure_ascii=False, indent=2)}\n\n"
        f"Язык: {LANG_DISPLAY.get(language, language)}\n\n"
        f"Доступные pip-пакеты (requirements.txt):\n{req_content}\n\n"
        f"ЗАДАЧА: Исправь контракт A5 ТОЛЬКО для файла `{filename}`.\n"
        f"Проанализируй замечания ревьюера и код разработчика.\n"
        f"Если функция требует дополнительных параметров — добавь их в сигнатуру.\n"
        f"Если нужны дополнительные функции/классы — добавь их.\n"
        f"Если сигнатура неидиоматична — исправь.\n"
        f"Верни JSON с ключами file_contracts и global_imports только для этого файла."
    )

    try:
        patch = await ask_agent(logger, "contract_analyst", ctx, cache, 0, randomize, language)
        patch = _normalize_file_contracts(patch) if isinstance(patch, dict) else {}
        patch_fc = parse_if_str(patch.get("file_contracts", {}), dict, {})
        patch_gi = parse_if_str(patch.get("global_imports", {}), dict, {})

        file_contract = patch_fc.get(filename)
        if file_contract is None:
            file_contract = next(iter(patch_fc.values()), [])
        file_imports = patch_gi.get(filename)
        if file_imports is None:
            file_imports = next(iter(patch_gi.values()), [])

        if file_contract:
            fc[filename] = parse_if_str(file_contract, list, [])
            gi[filename] = parse_if_str(file_imports, list, [])
            contract["file_contracts"] = fc
            contract["global_imports"] = gi
            files_list = state.get("files", [])
            contract = run_a5_validation_pipeline(
                contract, state.get("architecture", {}), files_list, logger,
                requirements_path=req_path if req_path.exists() else None,
            )
            state["api_contract"] = contract
            save_artifact(project_path, "A5", contract)
            stats.record("contract_analyst", get_model("contract_analyst"), True)
            logger.info(f"   ✅ A5 для {filename} обновлён ({len(fc[filename])} функций).")
            return True
        else:
            logger.warning(f"   ⚠️  Патч A5 для {filename} пустой.")
            stats.record("contract_analyst", get_model("contract_analyst"), False)
            return False
    except (LLMError, ValueError) as e:
        logger.exception(f"Патч A5 для {filename} упал: {e}")
        stats.record("contract_analyst", get_model("contract_analyst"), False)
        return False


async def phase_review_api_contract(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    contract: dict,
    arch_resp: dict,
    sa_resp: dict,
    randomize: bool = False,
) -> bool:
    """
    Ревью A5 (API Contract) на согласованность с A2/A3.
    Возвращает True если контракт одобрен, False если отклонён.
    При исключении возвращает True (не блокируем пайплайн), но помечает a5_review_skipped.
    """
    language = state.get("language", "python")
    logger.info("🔍 Ревью A5 (API Contract) ...")

    files_list = [f.get("path", f) if isinstance(f, dict) else f
                  for f in arch_resp.get("files", state.get("files", []))]

    ctx = (
        f"API контракт (A5):\n{json.dumps(contract, ensure_ascii=False, indent=2)}\n\n"
        f"Системная спецификация (A2):\n{json.dumps(sa_resp, ensure_ascii=False, indent=2)}\n\n"
        f"Архитектура (A3/A4):\n{json.dumps(arch_resp, ensure_ascii=False, indent=2)}\n\n"
        f"Файлы проекта: {files_list}\n\n"
        f"Язык: {language}"
    )

    try:
        result = await ask_agent(logger, "a5_validator", ctx, cache, 0, randomize, language)
        status = result.get("status", "REJECT")
        feedback = result.get("feedback", "")
        model = get_model("a5_validator")

        if status == "APPROVE":
            logger.info("✅ A5 прошёл ревью.")
            stats.record("a5_validator", model, True)
            save_artifact(project_path, "A5.1", result)
            return True
        else:
            logger.warning(f"❌ A5 отклонён: {feedback}")
            stats.record("a5_validator", model, False)
            return False
    except (LLMError, ValueError) as e:
        logger.warning(f"⚠️  A5 Validator упал: {e}. Пропускаем ревью (не блокируем пайплайн).")
        state["a5_review_skipped"] = True
        return True


async def phase_generate_api_contract(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    arch_resp: dict,
    sa_resp: dict,
    randomize: bool = False,
) -> dict:
    """
    Генерирует A5 (API & Contract Spec).
    Developer получает явный контракт функций вместо «угадывания».
    """
    language = state.get("language", "python")
    logger.info("📋 Contract Analyst генерирует A5 (API контракт) ...")

    req_path = _get_req_path(project_path)
    req_content = _read_req_content(req_path)

    ctx = (
        f"Запрос: {state['task']}\n\n"
        f"Системная спецификация (A2):\n{json.dumps(sa_resp, ensure_ascii=False, indent=2)}\n\n"
        f"Архитектура (A3/A4):\n{json.dumps(arch_resp, ensure_ascii=False, indent=2)}\n\n"
        f"Язык: {LANG_DISPLAY.get(language, language)}\n\n"
        f"Файлы: {arch_resp.get('files', [])}\n\n"
        f"Доступные pip-пакеты (requirements.txt):\n{req_content}"
    )

    try:
        contract = await ask_agent(logger, "contract_analyst", ctx, cache, 0, randomize, language)
        if not isinstance(contract, dict):
            contract = {}
        contract = _normalize_file_contracts(contract)
        contract.setdefault("file_contracts", {})
        contract.setdefault("global_imports", {})
        stats.record("contract_analyst", get_model("contract_analyst"), True)
        files_list = [f.get("path", f) if isinstance(f, dict) else f
                      for f in arch_resp.get("files", state.get("files", []))]
        contract = await _validate_and_patch_contract(
            logger, project_path, state, cache, stats, contract, files_list, randomize
        )
        contract = _inject_missing_data_models(contract, sa_resp, files_list, logger)
        contract = run_a5_validation_pipeline(
            contract, arch_resp, files_list, logger,
            requirements_path=req_path if req_path.exists() else None,
        )
        save_artifact(project_path, "A5", contract)
        logger.info("✅ A5 (API контракт) готов.")
        return contract
    except (LLMError, ValueError) as e:
        logger.exception(f"Contract Analyst упал: {e}")
        stats.record("contract_analyst", get_model("contract_analyst"), False)
        logger.warning(f"⚠️  Contract Analyst не справился: {e}. Контракт будет пустым.")
        return {"file_contracts": {}, "global_imports": {}}


async def refresh_api_contract(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    randomize: bool = False,
) -> None:
    """
    Каскад: после обновления A2 пересчитывает A5.
    Вызывается из revise_spec().
    """
    language = state.get("language", "python")
    logger.info("🔄 Каскадное обновление A5 после изменения A2 ...")
    req_path = _get_req_path(project_path)
    req_content = _read_req_content(req_path)

    ctx = (
        f"Запрос: {state['task']}\n\n"
        f"Обновлённая спецификация (A2):\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
        f"Файлы: {state.get('files', [])}\n\n"
        f"Язык: {LANG_DISPLAY.get(language, language)}\n\n"
        f"Доступные pip-пакеты (requirements.txt):\n{req_content}"
    )
    try:
        new_contract = await ask_agent(logger, "contract_analyst", ctx, cache, 0, randomize, language)
        if not isinstance(new_contract, dict):
            new_contract = {}
        new_contract = _normalize_file_contracts(new_contract)
        new_contract.setdefault("file_contracts", {})
        new_contract.setdefault("global_imports", {})
        files_list = state.get("files", [])
        new_contract = await _validate_and_patch_contract(
            logger, project_path, state, cache, stats,
            new_contract, files_list, randomize
        )
        new_contract = _inject_missing_data_models(
            new_contract, state.get("system_specs", {}), files_list, logger
        )
        new_contract = run_a5_validation_pipeline(
            new_contract, state.get("architecture", {}), files_list, logger,
            requirements_path=req_path if req_path.exists() else None,
        )
        # Восстановление: если новый A5 потерял валидные импорты из старого A5,
        # сохраняем их, затем прогоняем через validation pipeline для очистки phantom
        old_gi = state.get("api_contract", {}).get("global_imports", {})
        new_gi = new_contract.setdefault("global_imports", {})
        restored_any = False
        for fname in files_list:
            old_imports = old_gi.get(fname, [])
            new_imports = new_gi.get(fname, [])
            if isinstance(old_imports, list) and isinstance(new_imports, list):
                if len(new_imports) < len(old_imports):
                    new_set = set(new_imports)
                    for imp in old_imports:
                        if imp not in new_set:
                            new_imports.append(imp)
                            restored_any = True
                            logger.info(f"  📎 Восстановлен import из старого A5: '{imp}' для {fname}")
                    new_gi[fname] = new_imports
        if restored_any:
            new_contract = run_a5_validation_pipeline(
                new_contract, state.get("architecture", {}), files_list, logger,
                requirements_path=req_path if req_path.exists() else None,
            )
        # Sync: добавляем новые файлы, удаляем призраки
        from state import sync_files_with_a5
        a5_files = set(new_contract.get("file_contracts", {}).keys())
        sync_files_with_a5(state, a5_files, logger)
        state["api_contract"] = new_contract
        save_artifact(project_path, "A5", new_contract)
        logger.info("✅ A5 обновлён каскадно.")
    except (LLMError, ValueError) as e:
        logger.exception(f"Каскадное обновление A5 упало: {e}")
        logger.warning(f"⚠️  Не удалось обновить A5: {e}")

```
### 📄 `contract_validation.py`

```python
import logging
import re
import sys
from pathlib import Path


# ─────────────────────────────────────────────
# Детерминистские валидации A5 контракта
# ─────────────────────────────────────────────


def _auto_add_requirement(requirements_path: Path, package_name: str, logger: logging.Logger) -> None:
    """Авто-добавляет пакет в requirements.txt если его ещё нет."""
    if not requirements_path or not requirements_path.exists():
        return
    # Исправляем невалидные pip-имена (LLM часто пишет import-имя вместо pip-имени)
    from code_context import WRONG_PIP_PACKAGES
    if package_name in WRONG_PIP_PACKAGES:
        correct_pip, _ = WRONG_PIP_PACKAGES[package_name]
        logger.warning(
            f"  ⚠️  _auto_add_requirement: '{package_name}' → '{correct_pip}' "
            f"(невалидный pip-пакет)"
        )
        package_name = correct_pip
    try:
        content = requirements_path.read_text(encoding="utf-8")
    except OSError:
        return
    # Проверяем, не добавлен ли уже
    pkg_lower = package_name.lower()
    for line in content.splitlines():
        line_pkg = re.split(r"[=<>~!\[;]", line.strip())[0].strip().lower()
        if line_pkg.replace("-", "_") == pkg_lower.replace("-", "_"):
            return  # Уже есть
    # Добавляем
    if not content.endswith("\n"):
        content += "\n"
    requirements_path.write_text(content + package_name + "\n", encoding="utf-8")
    logger.info(f"  📦  Авто-добавлен '{package_name}' в requirements.txt")


def validate_requirements_txt(requirements_path: Path, logger: logging.Logger) -> None:
    """Проверяет requirements.txt на невалидные pip-пакеты и исправляет их."""
    if not requirements_path or not requirements_path.exists():
        return
    from code_context import WRONG_PIP_PACKAGES
    try:
        content = requirements_path.read_text(encoding="utf-8")
    except OSError:
        return
    lines = content.splitlines()
    changed = False
    new_lines: list[str] = []
    seen_normalized: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue
        pkg = re.split(r"[=<>~!\[;]", stripped)[0].strip()
        if pkg in WRONG_PIP_PACKAGES:
            correct_pip, _ = WRONG_PIP_PACKAGES[pkg]
            logger.warning(
                f"  ⚠️  requirements.txt: '{pkg}' → '{correct_pip}' (невалидный pip-пакет)"
            )
            # Заменяем на правильный, если его ещё нет
            norm = correct_pip.lower().replace("-", "_")
            if norm not in seen_normalized:
                new_lines.append(correct_pip)
                seen_normalized.add(norm)
            changed = True
            continue
        norm = pkg.lower().replace("-", "_")
        if norm in seen_normalized:
            changed = True
            continue  # Дубликат
        seen_normalized.add(norm)
        new_lines.append(line)
    if changed:
        requirements_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        logger.info("  ✅ requirements.txt: невалидные пакеты исправлены")


def _parse_import_line(imp_line: str) -> tuple[str, list[str]] | None:
    """Парсит строку импорта. Возвращает (source_stem, [imported_names]) или None.

    Поддерживает: 'from X import A', 'from X import A, B', 'from X import A as Z'.
    """
    if not isinstance(imp_line, str):
        return None
    m = re.match(r"from\s+([\w.]+)\s+import\s+(.+)", imp_line.strip())
    if not m:
        return None
    source = m.group(1)
    raw_names = m.group(2)
    names = []
    for part in raw_names.split(","):
        part = part.strip()
        if not part:
            continue
        # 'A as Z' → берём 'A' (оригинальное имя)
        name = part.split()[0].strip()
        if name.isidentifier():
            names.append(name)
    return (source, names) if names else None


def _normalize_file_contracts(contract: dict) -> dict:
    """Нормализация: модель может вернуть file_contracts как list вместо dict."""
    raw_fc = contract.get("file_contracts", {})
    if isinstance(raw_fc, list):
        normalized: dict = {}
        for item in raw_fc:
            if isinstance(item, dict):
                fname = item.get("file") or item.get("path") or item.get("name", "")
                funcs = item.get("functions") or item.get("contracts") or item.get("items") or []
                if fname:
                    normalized[fname] = funcs
        contract["file_contracts"] = normalized
    raw_gi = contract.get("global_imports", {})
    if isinstance(raw_gi, list):
        import logging as _log
        _log.getLogger(__name__).warning(
            f"⚠️  A5 global_imports вернулся как list (ожидался dict) — сброс в {{}}")
        contract["global_imports"] = {}
    # Удаляем записи с не-ASCII именами (LLM может вернуть русские имена из A2)
    contract = _remove_non_ascii_entries(contract)
    # Чистим остаточные garbage tokens из сигнатур (если LLM-level strip не применён)
    _GRB_RE = re.compile(r"<[｜|][\w▁]+[｜|]>")
    fc = contract.get("file_contracts", {})
    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            for key in ("signature", "name", "description", "implementation_hints"):
                val = item.get(key, "")
                if isinstance(val, str) and _GRB_RE.search(val):
                    val = re.sub(r"(\w+)" + r"<[｜|][\w▁]+[｜|]>" + r"\1", r"\1", val)
                    val = _GRB_RE.sub("", val)
                    # Исправляем сломанные аннотации: ") - str" → ") -> str"
                    val = re.sub(r"\)\s*-\s+(\w)", r") -> \1", val)
                    item[key] = val
    return contract


def _remove_non_ascii_entries(contract: dict) -> dict:
    """Удаляет из file_contracts записи с не-ASCII именами (например 'class Видео')."""
    import logging as _log
    _logger = _log.getLogger(__name__)
    fc = contract.get("file_contracts", {})
    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        cleaned = []
        for item in items:
            if not isinstance(item, dict):
                cleaned.append(item)
                continue
            name = item.get("name", "")
            if name and not name.isascii():
                _logger.warning(f"  A5: удалена запись с не-ASCII именем '{name}' из {fname}")
                continue
            cleaned.append(item)
        fc[fname] = cleaned
    return contract


def _validate_data_model_coverage(
    contract: dict,
    system_specs: dict,
    logger: logging.Logger,
) -> list[str]:
    """Проверяет что каждая data_model из A2 определена как класс хотя бы в одном файле A5.

    Возвращает список имён моделей, не покрытых контрактом.
    """
    data_models = system_specs.get("data_models", [])
    if not data_models:
        return []
    # Имена моделей из A2
    model_names: set[str] = set()
    for dm in data_models:
        name = dm.get("name", "") if isinstance(dm, dict) else ""
        if name:
            model_names.add(name)
    if not model_names:
        return []
    # Ищем покрытие в file_contracts A5
    # CamelCase-версии имён моделей для нечувствительного к регистру сравнения
    camel_to_original: dict[str, str] = {}
    for mn in model_names:
        camel = "".join(part.capitalize() for part in mn.split("_"))
        camel_to_original[camel.lower()] = mn  # Camera→camera, Vehicle→vehicle

    defined_names: set[str] = set()
    for fname, items in contract.get("file_contracts", {}).items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            item_name = item.get("name", "")
            sig = item.get("signature", "")
            # Совпадение по name (точное ИЛИ CamelCase) или по "class ..." в signature
            if item_name in model_names:
                defined_names.add(item_name)
            elif item_name.lower() in camel_to_original:
                defined_names.add(camel_to_original[item_name.lower()])
            for mn in model_names:
                camel = "".join(part.capitalize() for part in mn.split("_"))
                if f"class {mn}" in sig or f"class {camel}" in sig:
                    defined_names.add(mn)
    missing = sorted(model_names - defined_names)
    if missing:
        logger.warning(f"⚠️  A5: data models из A2 не покрыты контрактом: {', '.join(missing)}")
    return missing


def _inject_missing_data_models(
    contract: dict,
    system_specs: dict,
    files: list[str],
    logger: logging.Logger,
) -> dict:
    """Добавляет в A5 контракт класс для каждой data_model из A2, которая не покрыта.

    Создаёт models.py для shared data models (предотвращает циклические зависимости).
    """
    missing = _validate_data_model_coverage(contract, system_specs, logger)
    if not missing:
        return contract

    fc = contract.setdefault("file_contracts", {})
    gi = contract.setdefault("global_imports", {})

    # Ищем существующий файл моделей или создаём новый
    target_file = None
    for f in files:
        if Path(f).stem in ("models", "data_models"):
            target_file = f
            break
    if target_file is None:
        ext = Path(files[0]).suffix if files else ".py"
        target_file = f"models{ext}"
        if target_file not in files:
            files.append(target_file)
        fc.setdefault(target_file, [])
        gi.setdefault(target_file, [])
        logger.info(f"  📋 A5: создан файл {target_file} для shared data models")

    data_models = {
        dm.get("name", ""): dm
        for dm in system_specs.get("data_models", [])
        if isinstance(dm, dict) and dm.get("name")
        and dm["name"].isidentifier() and dm["name"].isascii()
    }

    for model_name in missing:
        # Пропускаем не-ASCII имена (русские из A2) и невалидные идентификаторы
        if not model_name.isascii() or not model_name.replace("_", "a").isidentifier():
            logger.info(f"  📋 A5: пропущена не-ASCII data model '{model_name}' из A2")
            continue
        dm = data_models.get(model_name, {})
        fields = dm.get("fields", [])
        # Формируем описание полей для description
        field_desc = ""
        if fields:
            field_names = []
            for f in fields:
                if isinstance(f, dict):
                    field_names.extend(f.keys())
                elif isinstance(f, str):
                    field_names.append(f.split(":")[0].strip())
            if field_names:
                field_desc = f" Поля: {', '.join(field_names)}."

        # CamelCase для имён классов: camera → Camera, license_plate → LicensePlate
        # Если имя уже CamelCase (без подчёркиваний, с заглавной) — оставить как есть
        if "_" not in model_name and model_name[0].isupper():
            class_name = model_name
        else:
            class_name = "".join(part.capitalize() for part in model_name.split("_"))
        entry = {
            "name": class_name,
            "signature": f"class {class_name}",
            "description": f"Data model из A2.{field_desc}",
            "required": True,
            "called_by": [],
        }
        fc.setdefault(target_file, []).append(entry)
        logger.info(f"  📋 A5: добавлен класс {class_name} в контракт файла {target_file} (из data_models A2: '{model_name}')")

    return contract


def _validate_global_imports(
    contract: dict,
    arch_resp: dict,
    project_files: list[str],
    logger: logging.Logger,
    requirements_path: Path | None = None,
) -> dict:
    """Удаляет из global_imports A5 импорты несуществующих пакетов.

    Проверяет: stdlib, файлы проекта, dependencies из архитектуры,
    а также requirements.txt (если передан).
    """
    gi = contract.get("global_imports", {})
    if not gi:
        return contract

    # Допустимые имена: stdlib
    stdlib = sys.stdlib_module_names if hasattr(sys, "stdlib_module_names") else set()
    # Модули проекта (без расширения)
    project_modules = {Path(f).stem for f in project_files}
    # pip-пакеты из dependencies архитектуры
    deps = arch_resp.get("dependencies", []) if isinstance(arch_resp, dict) else []
    pip_names: set[str] = set()
    for dep in deps:
        if isinstance(dep, str):
            pkg = re.split(r"[=<>~!\[]", dep)[0].strip().lower()
            pip_names.add(pkg)
            pip_names.add(pkg.replace("-", "_"))
    # Дополнительно: pip-пакеты из requirements.txt (всегда актуальный источник)
    if requirements_path and requirements_path.exists():
        from code_context import parse_requirements
        pip_names.update(parse_requirements(requirements_path))

    cleaned_gi: dict[str, list[str]] = {}
    for fname, imports in gi.items():
        if not isinstance(imports, list):
            cleaned_gi[fname] = imports
            continue
        valid_imports: list[str] = []
        for imp_line in imports:
            if not isinstance(imp_line, str):
                valid_imports.append(imp_line)
                continue
            # Извлекаем базовый модуль: from X import Y → X; import X → X
            m = re.match(r"(?:from\s+(\S+)\s+import|import\s+(\S+))", imp_line.strip())
            if not m:
                # Bare name без import/from — мусор от LLM, удаляем
                logger.warning(
                    f"  ⚠️  A5 global_imports: удалён '{imp_line}' для {fname} "
                    f"(не является валидным import-выражением)"
                )
                continue
            base_module = (m.group(1) or m.group(2)).split(".")[0]

            # Проверка: base_module должен быть валидным Python-идентификатором
            # (ловит "from opencv-python import cv2" — дефис невалиден)
            if not base_module.isidentifier():
                from code_context import PIP_TO_IMPORT
                correct = PIP_TO_IMPORT.get(base_module.lower())
                if correct:
                    corrected = f"import {correct}"
                    logger.warning(
                        f"  ⚠️  A5 global_imports: '{imp_line}' для {fname} — "
                        f"'{base_module}' невалидный идентификатор → '{corrected}'"
                    )
                    valid_imports.append(corrected)
                else:
                    logger.warning(
                        f"  ⚠️  A5 global_imports: удалён '{imp_line}' для {fname} — "
                        f"'{base_module}' невалидный Python-идентификатор"
                    )
                continue

            base_lower = base_module.lower()
            base_normalized = base_lower.replace("-", "_")

            # Проверка: невалидный pip-пакет как import-имя
            # (ловит "import opencv", "from opencv import ..." — opencv не Python-модуль)
            from code_context import WRONG_PIP_PACKAGES
            if base_module in WRONG_PIP_PACKAGES:
                correct_pip, correct_import = WRONG_PIP_PACKAGES[base_module]
                corrected = imp_line.replace(base_module, correct_import, 1)
                logger.warning(
                    f"  ⚠️  A5 global_imports: '{imp_line}' для {fname} → "
                    f"'{corrected}' ('{base_module}' невалидный модуль)"
                )
                valid_imports.append(corrected)
                if requirements_path:
                    _auto_add_requirement(requirements_path, correct_pip, logger)
                continue

            # Проверяем допустимость
            if base_module in stdlib:
                valid_imports.append(imp_line)  # stdlib — оставляем (не критично)
                continue
            if base_module in project_modules:
                valid_imports.append(imp_line)
                continue
            if base_lower in pip_names or base_normalized in pip_names:
                valid_imports.append(imp_line)
                continue
            # Пакет не найден — определяем: это pip-пакет или фантомный project import?
            # Признаки project import (а не pip): snake_case, нет дефисов,
            # выглядит как "from some_module import ClassName"
            looks_like_project = (
                base_module.isidentifier()
                and "_" in base_module
                and base_module == base_module.lower()
                and not any(c.isdigit() for c in base_module[:3])
            )
            if looks_like_project:
                # Фантомный project import — файла нет в проекте → удаляем
                logger.warning(
                    f"  ⚠️  A5 global_imports: удалён '{imp_line}' для {fname} "
                    f"('{base_module}' выглядит как модуль проекта, но файла нет)"
                )
                continue
            # pip-пакет → авто-добавляем в requirements.txt
            # НЕ добавляем если имя совпадает с файлом проекта (project_modules уже проверены выше)
            if (requirements_path and base_module.isidentifier()
                    and base_lower not in {pm.lower() for pm in project_modules}):
                _auto_add_requirement(requirements_path, base_module, logger)
                pip_names.add(base_lower)
                pip_names.add(base_normalized)
                valid_imports.append(imp_line)
                continue
            # Невалидный import — удаляем
            logger.warning(
                f"  ⚠️  A5 global_imports: удалён '{imp_line}' для {fname} "
                f"('{base_module}' не найден в stdlib, dependencies или файлах проекта)"
            )
        cleaned_gi[fname] = valid_imports

    contract["global_imports"] = cleaned_gi
    return contract


def _validate_import_consistency(
    contract: dict,
    logger: logging.Logger,
) -> dict:
    """Проверяет что cross-file imports в global_imports ссылаются на имена из file_contracts.

    Для каждого `from project_file import Name`:
    - Если Name не найдено в file_contracts целевого файла → удалить import.
    - Если у целевого файла нет контрактов вовсе → оставить (неполный A5).
    """
    fc = contract.get("file_contracts", {})
    gi = contract.get("global_imports", {})
    if not fc or not gi:
        return contract

    # stem → filename маппинг
    file_stems: dict[str, str] = {Path(f).stem: f for f in fc}
    # stem → set(defined names) из file_contracts
    defined_names: dict[str, set[str]] = {}
    for fname, items in fc.items():
        stem = Path(fname).stem
        names: set[str] = set()
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    n = item.get("name", "")
                    if n:
                        names.add(n)
        defined_names[stem] = names

    cleaned_gi: dict[str, list[str]] = {}
    for fname, imports in gi.items():
        if not isinstance(imports, list):
            cleaned_gi[fname] = imports
            continue
        valid: list[str] = []
        for imp_line in imports:
            parsed = _parse_import_line(imp_line)
            if parsed is None:
                valid.append(imp_line)
                continue
            source_stem, imported_names = parsed
            # Только cross-file project imports
            if source_stem not in file_stems:
                valid.append(imp_line)
                continue
            # Если у целевого файла нет контрактов — оставляем (неполный A5)
            if not defined_names.get(source_stem):
                valid.append(imp_line)
                continue
            # Проверяем наличие каждого имени, сохраняя оригинальные части (с as-алиасами)
            m_imp = re.match(r"from\s+[\w.]+\s+import\s+(.+)", imp_line.strip())
            raw_parts = [p.strip() for p in m_imp.group(1).split(",")] if m_imp else []
            valid_parts = []
            for part in raw_parts:
                if not part.strip():
                    continue
                name = part.split()[0].strip()
                if name in defined_names[source_stem]:
                    valid_parts.append(part)
                else:
                    logger.warning(
                        f"  ⚠️  A5 global_imports: удалён '{name}' из '{imp_line}' для {fname} — "
                        f"не определён в file_contracts {file_stems[source_stem]} "
                        f"(доступны: {', '.join(sorted(defined_names[source_stem]))})"
                    )
            if valid_parts:
                valid.append(f"from {source_stem} import {', '.join(valid_parts)}")
            # Если все имена невалидны — строка не добавляется
        cleaned_gi[fname] = valid

    contract["global_imports"] = cleaned_gi
    return contract


def _sanitize_implementation_hints(
    contract: dict,
    logger: logging.Logger,
) -> dict:
    """Убирает из implementation_hints ссылки на несуществующие имена.

    Если hints файла A ссылаются на 'VideoStreamProcessor' но в file_contracts
    файла video_stream_processor.py определён только 'process_frame' → заменяет
    'VideoStreamProcessor' на 'process_frame' (или убирает если нет однозначной замены).
    """
    fc = contract.get("file_contracts", {})
    if not fc:
        return contract

    # stem → set(defined names) из ВСЕХ file_contracts
    all_defined: dict[str, set[str]] = {}
    for fname, items in fc.items():
        stem = Path(fname).stem
        names: set[str] = set()
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    n = item.get("name", "")
                    if n:
                        names.add(n)
        all_defined[stem] = names

    # Все определённые имена (flat set)
    all_names_flat: set[str] = set()
    for names in all_defined.values():
        all_names_flat.update(names)

    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            hints = item.get("implementation_hints", "")
            if not hints:
                continue
            # Ищем CamelCase имена в hints, которые похожи на имена из file_contracts
            # но не существуют ни в одном file_contract
            for word in re.findall(r"\b([A-Z][a-zA-Z0-9]+)\b", hints):
                if word in all_names_flat:
                    continue  # Это имя реально существует
                # Проверяем: это имя похоже на stem файла?
                # VideoStreamProcessor → video_stream_processor
                snake = re.sub(r"(?<!^)(?=[A-Z])", "_", word).lower()
                if snake in all_defined and all_defined[snake]:
                    # Имя совпадает с файлом, но класс не определён
                    available = sorted(all_defined[snake])
                    old_hints = hints
                    hints = re.sub(rf"\b{re.escape(word)}\b", available[0], hints)
                    if hints != old_hints:
                        logger.info(
                            f"  🔧 A5 hints: заменено '{word}' → '{available[0]}' в {fname} "
                            f"('{word}' не определён, доступно: {', '.join(available)})"
                        )
            item["implementation_hints"] = hints

    return contract


# Типы из typing → import line
_TYPING_TYPES = {
    "List": "List", "Dict": "Dict", "Tuple": "Tuple", "Set": "Set",
    "Optional": "Optional", "Union": "Union", "Any": "Any",
    "Callable": "Callable", "Iterator": "Iterator", "Generator": "Generator",
    "Sequence": "Sequence", "Mapping": "Mapping", "Iterable": "Iterable",
}
# Prefix → import line (для np.ndarray, pd.DataFrame и т.д.)
_PREFIX_IMPORTS = {
    "np": "import numpy as np",
    "pd": "import pandas as pd",
    "tf": "import tensorflow as tf",
    "plt": "import matplotlib.pyplot as plt",
    "cv2": "import cv2",
}


def _inject_signature_type_imports(
    contract: dict,
    logger: logging.Logger,
) -> dict:
    """Авто-инжектирует import-строки для типов, используемых в сигнатурах A5.

    Если сигнатура содержит 'np.ndarray' → добавляет 'import numpy as np'.
    Если содержит 'List[...]' → добавляет 'from typing import List'.
    """
    fc = contract.get("file_contracts", {})
    gi = contract.setdefault("global_imports", {})

    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        file_imports = gi.setdefault(fname, [])
        existing_text = " ".join(file_imports)
        needed_typing: set[str] = set()

        for item in items:
            if not isinstance(item, dict):
                continue
            sig = item.get("signature", "")
            if not sig:
                continue

            # Проверяем typing types
            for type_name in _TYPING_TYPES:
                if re.search(rf"\b{type_name}\b", sig):
                    needed_typing.add(type_name)

            # Проверяем prefix-based imports (np.X, pd.X и т.д.)
            for prefix, imp_line in _PREFIX_IMPORTS.items():
                if f"{prefix}." in sig and imp_line not in existing_text:
                    if imp_line not in file_imports:
                        file_imports.append(imp_line)
                        logger.info(f"  📎 A5: авто-добавлен '{imp_line}' для {fname} (из сигнатуры)")

        # Собираем typing imports
        if needed_typing:
            # Проверяем что уже есть
            existing_typing: set[str] = set()
            for imp in file_imports:
                m = re.match(r"from\s+typing\s+import\s+(.+)", imp)
                if m:
                    existing_typing.update(n.strip().split()[0] for n in m.group(1).split(","))
            new_typing = needed_typing - existing_typing
            if new_typing:
                # Удаляем старую typing строку и создаём новую объединённую
                all_typing = sorted(existing_typing | new_typing)
                new_line = f"from typing import {', '.join(all_typing)}"
                file_imports[:] = [
                    imp for imp in file_imports
                    if not re.match(r"from\s+typing\s+import", imp)
                ]
                file_imports.insert(0, new_line)
                logger.info(f"  📎 A5: обновлён typing import для {fname}: {', '.join(new_typing)}")

    return contract


def _inject_requirements_imports(
    contract: dict,
    requirements_path: Path | None,
    logger: logging.Logger,
) -> dict:
    """Инжектирует imports пакетов из requirements.txt если они упоминаются в hints/description.

    Если implementation_hints или description содержат имя пакета (cv2, numpy, requests и т.п.),
    а global_imports не содержит соответствующий import — добавляет его.
    """
    if not requirements_path or not requirements_path.exists():
        return contract
    from code_context import PIP_TO_IMPORT
    fc = contract.get("file_contracts", {})
    gi = contract.setdefault("global_imports", {})

    # Собираем pip → import mapping из requirements.txt
    pkg_to_import: dict[str, str] = {}  # import_name → import_line
    try:
        for line in requirements_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            pkg = re.split(r"[=<>~!\[]", line)[0].strip().lower()
            pkg_norm = pkg.replace("-", "_")
            # Ищем правильное имя импорта
            import_name = PIP_TO_IMPORT.get(pkg, PIP_TO_IMPORT.get(pkg_norm, pkg_norm))
            if import_name and import_name.isidentifier():
                pkg_to_import[import_name] = f"import {import_name}"
    except Exception as exc:
        logger.warning(f"⚠️  Ошибка чтения requirements.txt для inject_requirements_imports: {exc}")
        return contract

    if not pkg_to_import:
        return contract

    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        # Собираем текст hints + description для поиска
        search_parts: list[str] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            sig = item.get("signature", "")
            if sig.strip().startswith("class "):
                continue
            search_parts.append(item.get("implementation_hints", ""))
            search_parts.append(item.get("description", ""))
            search_parts.append(sig)
        if not search_parts:
            continue
        search_text = " ".join(search_parts).lower()

        existing = gi.setdefault(fname, [])

        for import_name, import_line in pkg_to_import.items():
            # Проверяем упоминание пакета в hints/description (word boundary, не substring)
            if (len(import_name) >= 3
                    and re.search(rf'\b{re.escape(import_name.lower())}\b', search_text)
                    and import_line not in existing):
                existing.append(import_line)
                logger.info(f"  📎 A5 global_imports: авто-добавлен '{import_line}' для {fname} (из requirements + hints)")

    return contract


def _inject_cross_file_imports(
    contract: dict,
    logger: logging.Logger,
) -> dict:
    """Детерминистски добавляет в global_imports межфайловые импорты.

    Если класс определён в файле A (signature='class X'), а используется
    в сигнатуре функции файла B (параметр/return type содержит 'X'),
    то в global_imports файла B добавляется 'from A_stem import X'.
    """
    fc = contract.get("file_contracts", {})
    gi = contract.setdefault("global_imports", {})

    # Слова из docstring и Python builtins — НЕ являются именами классов
    _DOCSTRING_NOISE = {
        "Args", "Returns", "Raises", "Yields", "Note", "Notes", "Example",
        "Examples", "Attributes", "References", "See", "Also", "Warnings",
        "Todo", "Param", "Params", "Return", "Keyword",
    }
    _PYTHON_KEYWORDS = {
        "True", "False", "None", "and", "or", "not", "is", "in", "if", "else",
        "elif", "for", "while", "break", "continue", "pass", "def", "class",
        "return", "yield", "import", "from", "as", "with", "try", "except",
        "finally", "raise", "del", "global", "nonlocal", "assert", "lambda",
    }

    # 1. Собираем маппинг class_name → source_file (stem)
    class_to_file: dict[str, str] = {}
    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            sig = item.get("signature", "")
            if sig.strip().startswith("class "):
                class_name = item.get("name", "")
                if class_name and class_name not in _DOCSTRING_NOISE and class_name not in _PYTHON_KEYWORDS:
                    class_to_file[class_name] = fname

    if not class_to_file:
        return contract

    # 2. Для каждого файла проверяем сигнатуры на ссылки к классам из других файлов
    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        needed_imports: dict[str, str] = {}  # class_name → source_file
        for item in items:
            if not isinstance(item, dict):
                continue
            sig = item.get("signature", "")
            desc = item.get("description", "")
            # Не проверяем сигнатуры class (они определяют, а не используют)
            if sig.strip().startswith("class "):
                continue
            # Очищаем сигнатуру от docstring — оставляем только первую строку (def ...)
            sig_first_line = sig.split("\n")[0] if "\n" in sig else sig
            # Ищем ссылки на известные классы в сигнатуре, описании и hints
            hints = item.get("implementation_hints", "")
            search_text = f"{sig_first_line} {desc} {hints}"
            for class_name, source_file in class_to_file.items():
                if source_file == fname:
                    continue  # Класс определён в этом же файле
                # Пропускаем короткие/общие имена — слишком много false positives
                if len(class_name) < 4 or class_name in {
                    "Error", "Data", "Config", "Image", "Result", "Response",
                    "Request", "Event", "Model", "Base", "Item", "Type", "Node",
                    "Info", "State", "Action", "Status", "Value", "Entry", "Record",
                    "Task", "Message", "Handler", "Manager", "Service", "Client",
                    "Server", "Worker", "Logger", "Filter", "Parser", "Builder",
                }:
                    # Для общих имён — проверяем только сигнатуру (без desc/hints)
                    if not re.search(rf'\b{re.escape(class_name)}\b', sig_first_line):
                        continue
                if re.search(rf'\b{re.escape(class_name)}\b', search_text):
                    needed_imports[class_name] = source_file

        if not needed_imports:
            continue

        # 3. Проверяем что import ещё не добавлен в global_imports
        existing = gi.get(fname, [])
        if not isinstance(existing, list):
            existing = []

        # Извлекаем уже импортированные имена из строк import
        imported_names = set()
        for imp in existing:
            parsed = _parse_import_line(imp)
            if parsed:
                imported_names.update(parsed[1])
            else:
                # Fallback для 'import X'
                m = re.search(r'import\s+(\w+)', imp)
                if m:
                    imported_names.add(m.group(1))

        for class_name, source_file in needed_imports.items():
            source_stem = Path(source_file).stem
            import_line = f"from {source_stem} import {class_name}"
            if class_name not in imported_names:
                existing.append(import_line)
                imported_names.add(class_name)
                logger.info(f"  📋 A5 global_imports: добавлен '{import_line}' для {fname}")

        gi[fname] = existing

    return contract


# Встроенные типы Python + частые неклассовые имена — не нужно определять
_BUILTIN_TYPES = {
    "int", "float", "str", "bool", "bytes", "None", "object", "type",
    "list", "dict", "set", "tuple", "frozenset", "complex", "bytearray",
    "memoryview", "range", "slice", "property", "classmethod", "staticmethod",
    "Exception", "ValueError", "TypeError", "KeyError", "IndexError",
    "RuntimeError", "IOError", "OSError", "FileNotFoundError",
    "AttributeError", "ImportError", "StopIteration", "NotImplementedError",
}


def _validate_signature_types(
    contract: dict,
    files: list[str],
    logger: logging.Logger,
) -> dict:
    """Проверяет что все типы (CamelCase) в сигнатурах A5 определены в file_contracts.

    Если тип не определён нигде → создаёт запись class в models.py.
    Также очищает called_by от ссылок на несуществующие классы.
    """
    fc = contract.get("file_contracts", {})
    gi = contract.setdefault("global_imports", {})

    # 1. Собираем все определённые классы: name → file
    defined_classes: dict[str, str] = {}
    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            sig = item.get("signature", "")
            if sig.strip().startswith("class "):
                defined_classes[item.get("name", "")] = fname

    # 2. Сканируем все сигнатуры на CamelCase типы
    undefined_types: dict[str, set[str]] = {}  # type_name → set of files that use it
    _skip = set(_TYPING_TYPES) | _BUILTIN_TYPES | set(defined_classes)
    _skip |= set(_PREFIX_IMPORTS)  # np, pd, tf и т.д. — не типы

    # Слова из docstring-стиля — не являются типами
    _docstring_noise = {
        "Args", "Returns", "Raises", "Yields", "Note", "Notes", "Example",
        "Examples", "Attributes", "References", "Warnings", "Todo",
        "Param", "Params", "Return", "Keyword", "True", "False",
    }
    _skip |= _docstring_noise

    # Типы, импортированные из pip-пакетов (не project files) — не нужно определять
    project_stems = {Path(f).stem for f in files}
    for _fname_gi, _imports_gi in gi.items():
        if not isinstance(_imports_gi, list):
            continue
        for _imp in _imports_gi:
            if not isinstance(_imp, str):
                continue
            parsed = _parse_import_line(_imp)
            if parsed:
                src_stem, names = parsed
                if src_stem not in project_stems:
                    _skip.update(names)  # e.g. Flask, Api, Resource from flask
            else:
                m = re.match(r"import\s+(\w+)(?:\s+as\s+(\w+))?", _imp)
                if m:
                    _skip.add(m.group(2) or m.group(1))

    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            sig = item.get("signature", "")
            if sig.strip().startswith("class "):
                continue
            # Используем только первую строку сигнатуры (def ...), не docstring
            sig_line = sig.split("\n")[0] if "\n" in sig else sig
            # Извлекаем CamelCase слова (начинаются с заглавной, ≥2 символа)
            for m in re.finditer(r'\b([A-Z][a-zA-Z0-9]+)\b', sig_line):
                type_name = m.group(1)
                if type_name not in _skip:
                    undefined_types.setdefault(type_name, set()).add(fname)

    if not undefined_types:
        return contract

    # 3. Создаём undefined типы в models.py
    ext = Path(files[0]).suffix if files else ".py"
    models_file = None
    for f in files:
        if Path(f).stem in ("models", "data_models"):
            models_file = f
            break
    if models_file is None:
        models_file = f"models{ext}"
        if models_file not in files:
            files.append(models_file)
        fc.setdefault(models_file, [])
        gi.setdefault(models_file, [])
        logger.info(f"  📋 A5: создан файл {models_file} для undefined типов из сигнатур")

    existing_names = {
        item.get("name", "")
        for item in fc.get(models_file, [])
        if isinstance(item, dict)
    }

    for type_name, used_in_files in undefined_types.items():
        if type_name in existing_names:
            continue
        entry = {
            "name": type_name,
            "signature": f"class {type_name}",
            "description": f"Data class для типа {type_name} (авто-создан — тип используется в сигнатурах, но не определён)",
            "required": True,
            "called_by": [],
        }
        fc.setdefault(models_file, []).append(entry)
        existing_names.add(type_name)
        logger.warning(
            f"  ⚠️  A5: тип '{type_name}' используется в сигнатурах ({', '.join(sorted(used_in_files))}), "
            f"но не определён → добавлен как класс в {models_file}"
        )

    # 4. Очищаем called_by от ссылок на несуществующие классы
    all_names = set()
    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict):
                all_names.add(item.get("name", ""))
    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            called_by = item.get("called_by", [])
            if not isinstance(called_by, list):
                continue
            cleaned = []
            for ref in called_by:
                if not isinstance(ref, str):
                    cleaned.append(ref)
                    continue
                # "ClassName.method" → проверяем ClassName
                parts = ref.split(".")
                if len(parts) >= 2 and parts[0] not in all_names:
                    logger.warning(
                        f"  ⚠️  A5: called_by '{ref}' для {item.get('name', '?')} в {fname} — "
                        f"класс '{parts[0]}' не определён в контракте → удалён"
                    )
                    continue
                cleaned.append(ref)
            item["called_by"] = cleaned

    return contract


def _dedup_cross_file_classes(
    contract: dict,
    logger: logging.Logger,
) -> dict:
    """Удаляет дублированные классы из file_contracts.

    Если один класс (по name) определён в нескольких файлах,
    оставляем его в файле с наилучшим соответствием (по stem name),
    или в файле с наибольшим количеством полей/методов.
    Пример: Camera в camera.py и models.py → оставляем в camera.py.
    """
    fc = contract.get("file_contracts", {})
    # Маппинг class_name → [(fname, item, field_count)]
    class_locations: dict[str, list[tuple[str, dict, int]]] = {}
    for fname, items in fc.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            sig = item.get("signature", "")
            if sig.strip().startswith("class "):
                name = item.get("name", "")
                if name:
                    # Считаем "richness" — длина сигнатуры как прокси
                    richness = len(sig)
                    class_locations.setdefault(name, []).append((fname, item, richness))

    for class_name, locations in class_locations.items():
        if len(locations) <= 1:
            continue
        # Выбираем лучший файл: сначала по stem match, затем по richness
        best_fname = locations[0][0]
        best_score = -1
        for fname, item, richness in locations:
            stem = Path(fname).stem.lower()
            score = richness
            # Бонус если stem совпадает с именем класса (camera.py для Camera)
            if stem == class_name.lower():
                score += 10000
            # Бонус если это не models.py (предпочитаем бизнес-файл)
            if stem != "models":
                score += 100
            if score > best_score:
                best_score = score
                best_fname = fname
        # Удаляем дубли из других файлов
        for fname, item, _ in locations:
            if fname != best_fname:
                fc[fname] = [i for i in fc[fname] if i is not item]
                logger.info(
                    f"  📋 A5 dedup: удалён дубль класса '{class_name}' из {fname} "
                    f"(оставлен в {best_fname})"
                )

    return contract


def _build_import_graph(
    gi: dict[str, list[str]],
    files: list[str],
    project_stems: set[str],
) -> tuple[dict[str, set[str]], dict[str, list[tuple[str, str]]]]:
    """Строит граф зависимостей из global_imports A5. Возвращает (graph, import_details)."""
    graph: dict[str, set[str]] = {Path(f).stem: set() for f in files}
    import_details: dict[str, list[tuple[str, str]]] = {}
    for fname, imports in gi.items():
        if not isinstance(imports, list):
            continue
        stem = Path(fname).stem
        graph.setdefault(stem, set())
        import_details.setdefault(stem, [])
        for imp_line in imports:
            parsed = _parse_import_line(imp_line)
            if not parsed:
                continue
            src_stem, names = parsed
            if src_stem in project_stems and src_stem != stem:
                graph[stem].add(src_stem)
                for name in names:
                    import_details[stem].append((src_stem, name))
    return graph, import_details


def _find_graph_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """DFS-поиск циклов в графе зависимостей (color-based)."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {v: WHITE for v in graph}
    cycles: list[list[str]] = []

    def _dfs(u: str, path: list[str]) -> None:
        color[u] = GRAY
        for v in graph.get(u, set()):
            if v not in color:
                continue
            if color[v] == GRAY:
                idx = path.index(v) if v in path else -1
                if idx >= 0:
                    cycles.append(path[idx:] + [v])
            elif color[v] == WHITE:
                _dfs(v, path + [v])
        color[u] = BLACK

    for v in graph:
        if color[v] == WHITE:
            _dfs(v, [v])
    return cycles


def _move_classes_to_models(
    classes_to_move: dict[str, str],
    fc: dict, gi: dict,
    files: list[str],
    project_stems: set[str],
    models_file: str, models_stem: str,
    logger: logging.Logger,
) -> int:
    """Переносит классы из file_contracts в models.py, обновляет global_imports. Возвращает кол-во перемещённых."""
    moved = 0
    for class_name, source_stem in classes_to_move.items():
        source_file = next((f for f in files if Path(f).stem == source_stem), None)
        if not source_file:
            continue
        if source_file == models_file:
            continue  # Уже в models — не перемещаем сами в себя
        if source_file not in fc:
            continue
        source_items = fc[source_file]
        for i, item in enumerate(source_items):
            if isinstance(item, dict) and item.get("name") == class_name:
                fc[models_file].append(source_items.pop(i))
                moved += 1
                break
        new_import = f"from {models_stem} import {class_name}"
        for fkey, imp_list in gi.items():
            if not isinstance(imp_list, list):
                continue
            for idx, imp_line in enumerate(imp_list):
                parsed = _parse_import_line(imp_line)
                if not parsed:
                    continue
                imp_src, imp_names = parsed
                if imp_src != source_stem or class_name not in imp_names:
                    continue
                remaining = [n for n in imp_names if n != class_name]
                if remaining:
                    gi[fkey][idx] = f"from {imp_src} import {', '.join(remaining)}"
                else:
                    gi[fkey][idx] = ""
                if new_import not in gi[fkey]:
                    gi[fkey].append(new_import)
                break
            gi[fkey] = [imp for imp in gi[fkey] if imp]
    return moved


def _detect_and_fix_circular_imports(
    contract: dict,
    files: list[str],
    logger: logging.Logger,
) -> dict:
    """Детерминистская проверка циклических зависимостей в A5 global_imports.

    Строит граф из cross-file imports, находит циклы, переносит shared classes
    в models.py для разрыва циклов.
    """
    fc = contract.get("file_contracts", {})
    gi = contract.get("global_imports", {})
    if not fc or not gi:
        return contract

    project_stems = {Path(f).stem for f in files}
    graph, import_details = _build_import_graph(gi, files, project_stems)
    cycles = _find_graph_cycles(graph)
    if not cycles:
        return contract

    cycle_stems: set[str] = set()
    for cycle in cycles:
        cycle_stems.update(cycle)

    logger.warning(
        f"  ⚠️  A5: обнаружены циклические зависимости: "
        f"{'; '.join(' → '.join(c) for c in cycles)}"
    )

    # Находим classes/functions, которые импортируются другим файлом цикла
    classes_to_move: dict[str, str] = {}
    funcs_in_cycle: list[tuple[str, str, str]] = []
    for stem in cycle_stems:
        fname = next((f for f in files if Path(f).stem == stem), None)
        if not fname or fname not in fc:
            continue
        for other_stem in cycle_stems:
            if other_stem == stem:
                continue
            for src_stem, name in import_details.get(other_stem, []):
                if src_stem != stem:
                    continue
                for item in fc.get(fname, []):
                    if isinstance(item, dict) and item.get("name") == name:
                        sig = item.get("signature", "")
                        if sig.strip().startswith("class "):
                            classes_to_move[name] = stem
                        else:
                            funcs_in_cycle.append((name, stem, other_stem))

    if not classes_to_move:
        if funcs_in_cycle:
            logger.warning(
                f"  ⚠️  Циклические imports через функции: "
                + ", ".join(f"{n} ({s}→{d})" for n, s, d in funcs_in_cycle)
                + " — удаляю кросс-импорт из одного направления"
            )
            for name, from_stem, to_stem in funcs_in_cycle:
                # to_stem импортирует name из from_stem — удаляем этот import
                importer_file = next((f for f in files if Path(f).stem == to_stem), None)
                if importer_file and importer_file in gi:
                    cleaned = []
                    for imp in gi[importer_file]:
                        parsed = _parse_import_line(imp)
                        if parsed and parsed[0] == from_stem and name in parsed[1]:
                            remaining = [n for n in parsed[1] if n != name]
                            if remaining:
                                cleaned.append(f"from {parsed[0]} import {', '.join(remaining)}")
                            logger.info(f"    → Удалён import '{name}' из {importer_file}")
                            continue
                        cleaned.append(imp)
                    gi[importer_file] = cleaned
            contract["global_imports"] = gi
            return contract
        logger.info("  ℹ️  Циклы найдены, но нет переносимых элементов.")
        return contract

    # Определяем/создаём models файл
    ext = Path(files[0]).suffix if files else ".py"
    models_file = f"models{ext}"
    models_stem = "models"
    for f in files:
        if Path(f).stem in ("models", "data_models"):
            models_file = f
            models_stem = Path(f).stem
            break
    if models_file not in files:
        files.append(models_file)
    fc.setdefault(models_file, [])
    gi.setdefault(models_file, [])

    moved = _move_classes_to_models(classes_to_move, fc, gi, files, project_stems,
                                     models_file, models_stem, logger)

    # models.py — data-only: удаляем только PROJECT-file imports (не stdlib/pip)
    models_imports = gi.get(models_file, [])
    if isinstance(models_imports, list):
        other_project_stems = project_stems - {models_stem}
        clean = []
        for imp in models_imports:
            parsed = _parse_import_line(imp)
            if parsed and parsed[0] in other_project_stems:
                logger.info(f"  🗑️  Удалён project import из {models_file}: {imp}")
                continue
            clean.append(imp)
        gi[models_file] = clean

    logger.info(
        f"  📋 A5: перенесено {moved} классов в {models_file} для разрыва циклов: "
        f"{', '.join(classes_to_move.keys())}"
    )

    contract["file_contracts"] = fc
    contract["global_imports"] = gi
    return contract


def run_a5_validation_pipeline(
    contract: dict,
    arch_resp: dict,
    files: list[str],
    logger: logging.Logger,
    requirements_path: Path | None = None,
) -> dict:
    """Полный конвейер детерминистских валидаций A5. Вызывается из 4 мест в contract.py."""
    contract = _validate_global_imports(
        contract, arch_resp, files, logger,
        requirements_path=requirements_path,
    )
    contract = _inject_signature_type_imports(contract, logger)
    contract = _sanitize_implementation_hints(contract, logger)
    contract = _inject_requirements_imports(contract, requirements_path, logger)
    contract = _inject_cross_file_imports(contract, logger)
    contract = _dedup_cross_file_classes(contract, logger)
    contract = _validate_signature_types(contract, files, logger)
    contract = _validate_import_consistency(contract, logger)
    contract = _detect_and_fix_circular_imports(contract, files, logger)
    contract = _remove_non_ascii_entries(contract)
    return contract

```
### 📄 `exceptions.py`

```python
"""
Иерархия исключений ai_factory.
"""


class FactoryError(Exception):
    """Базовое исключение фабрики."""


class LLMError(FactoryError):
    """Ошибки LLM-вызовов: API, таймаут, невалидный JSON."""


class DockerError(FactoryError):
    """Ошибки Docker: сборка, запуск, таймаут контейнера."""


class StateError(FactoryError):
    """Ошибки сохранения/загрузки состояния проекта."""


class SpecError(FactoryError):
    """Ошибки валидации контракта/спецификации."""

```
### 📄 `generate_docs.py`

```python
# generate_docs.py
import os
import re
from pathlib import Path
import pathspec
from datetime import datetime
from docx import Document
from docx.shared import Pt

PROJECT_ROOT = Path(__file__).parent
README_FILE = PROJECT_ROOT / "README.md"
DOCS_DIR = PROJECT_ROOT / "documents"

EXTRA_FILES_WITHOUT_EXTENSION = {
    "Dockerfile", "Dockerfile.cpu", "Dockerfile.gpu", "Makefile", ".dockerignore", "LICENSE"
}
INCLUDED_EXTENSIONS = [".py", ".yaml", ".env", ".txt", ".md", ".yml", ".toml", ".sh",'.sql','.api','.webhook','.idoit_webhook','.celery']

EXCLUDED_FILES = {
    ".env", "secrets.py", "config_local.py", "id_rsa", "id_rsa.pub",
    "known_hosts", "docker-compose.override.yml", "token.txt"
}

SYNTAX_HIGHLIGHTING_MAP = {
    ".py": "python",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".sh": "bash",
    ".env": "env",
    ".txt": "",
    ".md": "markdown",
    ".csv": "",
    ".xlsx": "",
    ".json": "json",
    "Dockerfile": "Dockerfile",
    "Makefile": "makefile"
}

# Используем "сырую" строку (r""") или экранируем \
# Также обновим заголовок для лучшего описания
README_HEADER = r"""# 📄 Проект "Ситуационный центр"

## 📝 Описание

Это проект автоматизации полного цикла разработки на нескольких языках программирования.

## 🛠️ Установка

1. Клонируйте репозиторий.
2. Создайте виртуальное окружение: `python -m venv .venv`
3. Активируйте виртуальное окружение:
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`
4. Установите зависимости: `pip install -r requirements.txt`


## ▶️ Запуск

Описан в файле RUN.md

## 📁 Структура проекта
""" # Конец строки README_HEADER

def load_gitignore_spec():
    gitignore_path = PROJECT_ROOT / ".gitignore"
    if not gitignore_path.exists():
        return None
    with open(gitignore_path, "r", encoding="utf-8") as f:
        spec = pathspec.PathSpec.from_lines("gitwildmatch", f)
    return spec

def should_include(path, spec):
    rel_path = path.relative_to(PROJECT_ROOT)
    if path.name in EXCLUDED_FILES:
        return False
    return spec is None or not spec.match_file(rel_path)

def generate_tree(start_path, spec):
    tree = []
    for root, dirs, files in os.walk(start_path):
        filtered_dirs = [d for d in dirs if should_include(Path(root) / d, spec)]
        dirs[:] = filtered_dirs
        level = root.replace(str(start_path), "").count(os.sep)
        indent = "│   " * level
        dir_name = os.path.basename(root)
        if level == 0:
            tree.append(f"├── {dir_name}/")
        else:
            tree.append(f"{indent}├── {dir_name}/")
        subindent = "│   " * (level + 1)
        for f in sorted(files):
            full_path = Path(root) / f
            if should_include(full_path, spec):
                if f in EXTRA_FILES_WITHOUT_EXTENSION:
                    tree.append(f"{subindent}├────── {f}")
                elif any(f.endswith(ext) for ext in INCLUDED_EXTENSIONS):
                    tree.append(f"{subindent}├────── {f}")
    return "\n".join(tree).replace("├────── └──", "└──────").replace("├── └──", "└──")

def read_file_content(file_path):
    file_name = file_path.name
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        if file_name in SYNTAX_HIGHLIGHTING_MAP:
            lang = SYNTAX_HIGHLIGHTING_MAP[file_name]
        else:
            lang = SYNTAX_HIGHLIGHTING_MAP.get(file_path.suffix, "")
        return f"```{lang}\n{content}\n```"
    except Exception as e:
        return f"<!-- Ошибка чтения файла: {e} -->\n\n"

def gather_files(start_path, spec):
    file_contents = []
    for root, dirs, files in os.walk(start_path):
        dirs[:] = [d for d in dirs if should_include(Path(root) / d, spec)]
        for f in sorted(files):
            if f == "README.md":
                continue
            full_path = Path(root) / f
            if should_include(full_path, spec):
                if f in EXTRA_FILES_WITHOUT_EXTENSION or any(f.endswith(ext) for ext in INCLUDED_EXTENSIONS):
                    rel_path = full_path.relative_to(PROJECT_ROOT)
                    file_contents.append(f"### 📄 `{rel_path}`\n")
                    file_contents.append(read_file_content(full_path))
    return "\n".join(file_contents)

# --- Новая функция для очистки текста ---
def clean_text_for_xml(text: str) -> str:
    """
    Убираем недопустимые символы для XML 1.0.
    Разрешаем: \t (0x09), \n (0x0A), \r (0x0D) и U+0020..U+D7FF, U+E000..U+FFFD, U+10000..U+10FFFF
    """
    if not isinstance(text, str):
        text = str(text)

    # Удаляем управляющие символы U+0000 - U+001F, кроме таб(9), lf(10), cr(13)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', text)
    # Удаляем non-characters U+FFFE, U+FFFF and their high-plane equivalents
    text = re.sub(r'[\uFFFE\uFFFF]', '', text)
    # Также принудительно заменить суррогатные пары, если они появились (условный safe)
    # При кодировке/декодировании с 'utf-8' и errors='ignore' мы убираем невалидные суррогаты
    try:
        text = text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
    except Exception:
        # В крайнем случае — убираем всё не-ASCII печатное
        text = ''.join(ch for ch in text if ord(ch) >= 32)

    return text

def build_documentation():
    spec = load_gitignore_spec()
    structure = generate_tree(PROJECT_ROOT, spec)
    code_sections = gather_files(PROJECT_ROOT, spec)
    
    # Используем обновленный заголовок
    documentation = f"""{README_HEADER}
{structure}
## 💻 Коды основных модулей
{code_sections}
"""

    # Запись README.md
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(documentation)
    print("[+] README.md успешно обновлён")

    # --- Создание .docx ---
    # Создаем каталог documents, если он не существует
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    project_name = PROJECT_ROOT.name
    docx_filename = f"{project_name}_{timestamp}.docx"
    docx_path = DOCS_DIR / docx_filename

    doc = Document()
    style = doc.styles['Normal']
    font = style.font # type: ignore
    font.name = 'Consolas'
    font.size = Pt(10)

    # Разбиваем всю документацию на строки
    lines = documentation.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        # Очищаем каждую строку перед добавлением
        clean_line = clean_text_for_xml(line)
        
        if clean_line.startswith("```"):
            # Начало блока кода
            lang = clean_line[3:].strip() # Получаем язык (например, python)
            code_block = ""
            i += 1
            # Собираем строки кода до закрывающей ```
            while i < len(lines) and not lines[i].startswith("```"):
                # Очищаем и добавляем каждую строку кода
                code_block += clean_text_for_xml(lines[i]) + "\n"
                i += 1
            # Добавляем блок кода в документ
            if code_block.strip():
                p_code = doc.add_paragraph(code_block.strip())
                # Простая попытка применить стиль кода (docx не поддерживает подсветку синтаксиса из коробки)
                # Можно рассмотреть использование python-docx-template или других библиотек
                # p_code.style = 'Code' if 'Code' in [s.name for s in doc.styles] else 'Normal'
            i += 1 # Пропускаем закрывающую ```
            continue # Переходим к следующей итерации внешнего цикла
        else:
            # Обычный текст
            if clean_line: # Добавляем только непустые строки
                 p = doc.add_paragraph(clean_line)
                 p.style = doc.styles['Normal'] # type: ignore
        i += 1 # Переход к следующей строке

    try:
        doc.save(docx_path) # type: ignore
        print(f"[+] Документация сохранена как {docx_path}")
    except Exception as e:
        print(f"[!] Ошибка при сохранении .docx файла: {e}")

if __name__ == "__main__":
    build_documentation()
    print("[+] Генерация документации завершена")
```
### 📄 `infra.py`

```python
import hashlib
import logging
import subprocess
from pathlib import Path
from typing import Optional

from config import FACTORY_DIR, RUN_TIMEOUT, TRUNCATE_LOG
from lang_utils import get_docker_image

logger = logging.getLogger(__name__)


def run_command(
    args: list[str],
    cwd: Optional[Path] = None,
    timeout: Optional[int] = None,
) -> tuple[int, str, str]:
    try:
        proc = subprocess.Popen(
            args, cwd=cwd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            return proc.returncode, stdout, stderr
        except subprocess.TimeoutExpired as e:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            partial_out = (e.stdout or "")[-TRUNCATE_LOG:] if e.stdout else ""
            partial_err = (e.stderr or "")[-TRUNCATE_LOG:] if e.stderr else ""
            return -1, partial_out, f"TIMEOUT: процесс не завершился за {timeout}с.\n{partial_err}"
    except OSError as e:
        return -1, "", f"Команда не найдена или недоступна: {e}"


def _make_container_name(src_path: Path) -> str:
    """Генерирует детерминированное имя контейнера по пути src_path."""
    return "factory_" + hashlib.sha256(str(src_path).encode()).hexdigest()[:12]


def _cleanup_docker_container(container_name: str) -> None:
    """Удаляет контейнер по имени (безопасно — не затрагивает чужие контейнеры)."""
    run_command(["docker", "rm", "-f", container_name])


def run_in_docker(
    src_path: Path,
    command: str,
    timeout: int,
    language: str = "python",
    read_only: bool = False,
) -> tuple[int, str, str]:
    """Docker монтирует только src/ — чистый контекст без .factory/.
    Контейнер именован, чтобы cleanup был точечным.
    read_only=True монтирует src/ с :ro для безопасности (ревью/тесты).
    """
    image          = get_docker_image(language)
    container_name = _make_container_name(src_path)
    volume_spec    = f"{src_path}:/app:ro" if read_only else f"{src_path}:/app"
    result = run_command(
        [
            "docker", "run", "--rm",
            "--name", container_name,
            "--network", "bridge",
            "--memory", "512m",
            "--cpus",   "1",
            "-v", volume_spec,
            "-w", "/app",
            image,
            "bash", "-c", command,
        ],
        timeout=timeout,
    )
    if result[0] == -1:
        _cleanup_docker_container(container_name)
    return result


def build_docker_image(src_path: Path, tag: str) -> tuple[bool, str, str]:
    """Dockerfile должен лежать в src/."""
    rc, stdout, stderr = run_command(
        ["docker", "build", "-t", tag, "."],
        cwd=src_path, timeout=RUN_TIMEOUT,
    )
    return rc == 0, stdout, stderr


def check_docker_installed() -> bool:
    rc, _, stderr = run_command(["docker", "version"])
    if rc != 0:
        logger.error(f"❌ Docker не установлен или демон не запущен.\nДетали: {stderr}")
        logger.info("  → Установите Docker: https://docs.docker.com/engine/install/")
        logger.info("  → Убедитесь, что демон запущен: sudo systemctl start docker")
        return False
    return True


def git_init(project_path: Path) -> None:
    run_command(["git", "init"], cwd=project_path)
    gitignore = (
        # .factory/ полностью скрыт от Git
        f"{FACTORY_DIR}/\n"
        "venv/\n__pycache__/\n*.pyc\n"
        "node_modules/\ntarget/\n"
    )
    (project_path / ".gitignore").write_text(gitignore, encoding="utf-8")
    git_commit(project_path, "Initial gitignore")


def git_commit(project_path: Path, message: str) -> None:
    run_command(["git", "add", "."], cwd=project_path)
    run_command(["git", "commit", "-m", message, "--allow-empty"], cwd=project_path)

```
### 📄 `json_utils.py`

```python
import json
import re
from typing import Any, TypeVar

from config import TRUNCATE_ERROR_MSG

T = TypeVar("T")


def parse_if_str(value: Any, expected_type: type[T], fallback: T) -> T:
    """Если value — строка, пробует json.loads. Если тип не совпал — возвращает fallback."""
    if isinstance(value, expected_type):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, expected_type):
                return parsed
        except json.JSONDecodeError:
            pass
    return fallback


def to_str(value: Any) -> str:
    """Приводит любое значение к строке — защита от dict/list в полях feedback."""
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def safe_contract(state: dict) -> dict:
    """
    Возвращает api_contract как правильно типизированный dict.
    Защищает от строк на всех уровнях вложенности — модели иногда
    возвращают {"global_imports": "[]"} или {"file_contracts": "{}"}.
    Исправляет state на месте.
    """
    raw = state.get("api_contract")
    contract = parse_if_str(raw, dict, {})

    # Нормализуем file_contracts: должен быть dict[str, list]
    fc = parse_if_str(contract.get("file_contracts"), dict, {})
    for fname in list(fc.keys()):
        fc[fname] = parse_if_str(fc[fname], list, [])
    contract["file_contracts"] = fc

    # Нормализуем global_imports: должен быть dict[str, list]
    gi = parse_if_str(contract.get("global_imports"), dict, {})
    for fname in list(gi.keys()):
        gi[fname] = parse_if_str(gi[fname], list, [])
    contract["global_imports"] = gi

    state["api_contract"] = contract
    return contract


def repair_json(text: str) -> str:
    text = re.sub(r',\s*([}\]])', r'\1', text)
    text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
    return text


def repair_truncated_json(text: str) -> dict | None:
    """Пытается починить обрезанный JSON (модель исчерпала max_tokens).

    Стратегия: закрыть незавершённую строку, затем закрыть все открытые скобки.
    """
    # Определяем, находимся ли мы внутри строки
    in_string = False
    escape_next = False
    stack = []  # стек открытых скобок: '{' или '['

    for ch in text:
        if escape_next:
            escape_next = False
            continue
        if ch == '\\' and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch in ('{', '['):
            stack.append(ch)
        elif ch == '}' and stack and stack[-1] == '{':
            stack.pop()
        elif ch == ']' and stack and stack[-1] == '[':
            stack.pop()

    if not stack:
        return None  # скобки сбалансированы — не наш случай

    # Собираем suffix для закрытия
    suffix = ""
    if in_string:
        suffix += '"'
    # Закрываем все открытые скобки в обратном порядке
    for bracket in reversed(stack):
        suffix += '}' if bracket == '{' else ']'

    candidate = text + suffix
    try:
        result = json.loads(candidate)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    try:
        result = json.loads(repair_json(candidate))
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    return None


def extract_json_from_text(text: str) -> dict:
    """Надёжный парсер: учитывает строковые литералы с {} внутри и markdown-блоки."""
    text = text.strip()
    if not text:
        raise ValueError("Пустой ответ от модели")

    # Извлекаем JSON из markdown-блоков ```json ... ``` или ``` ... ```
    md_match = re.search(r"```(?:json)?\s*(\{[\s\S]*\})\s*```", text)
    if md_match:
        try:
            return json.loads(md_match.group(1))
        except json.JSONDecodeError:
            try:
                return json.loads(repair_json(md_match.group(1)))
            except json.JSONDecodeError:
                pass

    if text.startswith("{") and text.endswith("}"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    start = text.find("{")
    if start == -1:
        raise ValueError(f"JSON не найден в ответе: {text[:TRUNCATE_ERROR_MSG]}")

    count = 0
    in_string = False
    escape_next = False
    end = -1
    for i in range(start, len(text)):
        ch = text[i]
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            count += 1
        elif ch == "}":
            count -= 1
            if count == 0:
                end = i + 1
                break

    if end == -1:
        # Попытка починить обрезанный JSON (модель исчерпала max_tokens)
        truncated = text[start:]
        repaired = repair_truncated_json(truncated)
        if repaired is not None:
            return repaired
        raise ValueError("Несбалансированные JSON-скобки")

    candidate = text[start:end]

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    try:
        return json.loads(repair_json(candidate))
    except json.JSONDecodeError:
        pass

    try:
        import json_repair  # type: ignore
        repaired = json_repair.loads(candidate)
        if isinstance(repaired, dict) and repaired:
            return repaired
    except (ImportError, json.JSONDecodeError, ValueError, TypeError):
        pass

    raise ValueError(f"Не удалось извлечь JSON: {text[:TRUNCATE_ERROR_MSG]}...")

```
### 📄 `lang_utils.py`

```python
import re
from typing import Any

from prompts import PROMPTS

LANG_DISPLAY = {"python": "Python", "typescript": "TypeScript", "rust": "Rust"}
LANG_EXT     = {"python": "py",     "typescript": "ts",         "rust": "rs"}

DOCKER_IMAGES = {
    "python":     "python:3.12-slim",
    "typescript": "node:20-slim",
    "rust":       "rust:1.75-slim",
}


def get_docker_image(language: str) -> str:
    return DOCKER_IMAGES.get(language, "python:3.12-slim")


def get_execution_command(language: str, entry_point: str) -> str:
    """TypeScript: явная установка ts-node и typescript."""
    if language == "python":
        return f"pip install -r requirements.txt -q && python {entry_point}"
    elif language == "typescript":
        return (
            "npm install -q && "
            "npm install -g ts-node typescript --quiet && "
            f"npx ts-node {entry_point}"
        )
    elif language == "rust":
        return "cargo run --quiet"
    return f"python {entry_point}"


def get_test_command(language: str) -> str:
    if language == "python":
        return (
            "pip install pytest pytest-cov -q && "
            "pip install -r requirements.txt -q && "
            "pytest tests/ --cov=. --cov-report=term-missing -q"
        )
    elif language == "typescript":
        return "npm install -q && npm install -g ts-jest --quiet && npx jest --coverage"
    elif language == "rust":
        return "cargo test"
    return "pytest tests/ -q"


def get_system_prompt(agent: str, language: str = "python") -> str:
    """Подставляет {lang} и {ext} в промпты."""
    if agent not in PROMPTS:
        raise ValueError(f"Неизвестный агент: '{agent}'. Доступны: {', '.join(sorted(PROMPTS))}")
    base = PROMPTS[agent]
    lang_name = LANG_DISPLAY.get(language, "Python")
    ext       = LANG_EXT.get(language, "py")
    return base.replace("{lang}", lang_name).replace("{ext}", ext)


def sanitize_files_list(files_raw: list[Any], language: str = "python") -> list[str]:
    """Санитизация: только безопасные относительные пути."""
    safe: list[str] = []
    for f in files_raw:
        if isinstance(f, dict):
            f = f.get("path", "")
        if not isinstance(f, str):
            continue
        if re.match(r'^[\w/\-\.]+\.\w+$', f) and ".." not in f and not f.startswith("/"):
            safe.append(f)
    if safe:
        return safe
    fallback = {
        "python": "main.py",
        "typescript": "main.ts",
        "rust": "src/main.rs",
    }
    return [fallback.get(language, "main.py")]

```
### 📄 `llm.py`

```python
import asyncio
import json
import logging
import re
from typing import Optional

import httpx

# Regex для garbage tokens deepseek-coder (begin_of_sentence и т.п.)
_GARBAGE_TOKEN_RE = re.compile(r"<[｜|][\w▁]+[｜|]>")
_GARBAGE_DEDUP_RE = re.compile(r"(\w+)" + r"<[｜|][\w▁]+[｜|]>" + r"\1")


def _strip_garbage_tokens(text: str) -> str:
    """Убирает garbage tokens LLM (deepseek-coder) из любого текста.

    Сначала дедупликация: img<token>img_bytes → img_bytes,
    затем удаление оставшихся токенов: gcv<token>_image → gcv_image.
    """
    text = _GARBAGE_DEDUP_RE.sub(r"\1", text)
    text = _GARBAGE_TOKEN_RE.sub("", text)
    return text

from config import CACHEABLE_AGENTS, LLM_BASE_URL, LLM_API_KEY, LLM_TIMEOUT, LLM_MAX_TOKENS, LLM_NUM_CTX, MAX_LLM_RETRIES
from cache import ThreadSafeCache, cache_key
from exceptions import LLMError
from log_utils import get_model, log_model_choice, log_interaction
from json_utils import extract_json_from_text
from lang_utils import get_system_prompt

# Ollama native API base (без /v1/)
_OLLAMA_BASE = LLM_BASE_URL.rstrip("/").removesuffix("/v1").removesuffix("/v1/")
_CHAT_URL = f"{_OLLAMA_BASE}/api/chat"

# Таймаут для httpx: read=120с — только между чанками при streaming,
# НЕ общий таймаут генерации (stream=True решает эту проблему)
_HTTPX_TIMEOUT = httpx.Timeout(
    connect=30.0,
    read=120.0,
    write=30.0,
    pool=30.0,
)

AGENT_TEMPERATURES: dict[str, float] = {
    "developer":        0.1,
    "architect":        0.0,
    "system_analyst":   0.2,
    "business_analyst": 0.3,
    "reviewer":         0.0,
    "e2e_architect":    0.0,
    "e2e_qa":           0.0,
    "a5_business_reviewer": 0.0,
    "a5_architect_reviewer": 0.0,
    "a5_contract_reviewer":  0.0,
    "qa_runtime":       0.2,
    "spec_reviewer":    0.0,
    "test_generator":   0.2,
    "documenter":       0.3,
    "devops_runtime":   0.1,
    "arch_validator":   0.0,
    "supervisor":       0.2,
    "self_reflect":     0.0,
    "contract_analyst": 0.0,
    "a5_validator":     0.0,
}

# Ошибки, после которых имеет смысл retry (сеть, таймаут, формат)
_RETRYABLE_ERRORS = (
    httpx.HTTPStatusError,
    httpx.TimeoutException,
    asyncio.TimeoutError,
    json.JSONDecodeError,
)


async def _ollama_chat(
    client: httpx.AsyncClient,
    model: str,
    messages: list[dict],
    temperature: float,
    max_tokens: int,
    json_mode: bool = False,
) -> tuple[str, str]:
    """Вызывает Ollama native /api/chat со streaming.

    Streaming решает проблему ReadTimeout: чанки приходят каждые ~1с,
    таймаут 120с только между чанками (не общий таймаут генерации).
    Overall timeout (LLM_TIMEOUT) предотвращает бесконечное зависание.
    """
    return await asyncio.wait_for(
        _ollama_chat_inner(client, model, messages, temperature, max_tokens, json_mode),
        timeout=LLM_TIMEOUT,  # 600с overall — предотвращает зависание
    )


async def _ollama_chat_inner(
    client: httpx.AsyncClient,
    model: str,
    messages: list[dict],
    temperature: float,
    max_tokens: int,
    json_mode: bool = False,
) -> tuple[str, str]:
    payload: dict = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {
            "num_ctx": LLM_NUM_CTX,
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }
    if json_mode:
        payload["format"] = "json"

    content_parts: list[str] = []
    done_reason = "stop"

    async with client.stream("POST", _CHAT_URL, json=payload) as resp:
        if resp.status_code >= 400:
            body = await resp.aread()
            raise httpx.HTTPStatusError(
                f"Ollama {resp.status_code}: {body[:500].decode(errors='replace')}",
                request=resp.request,
                response=resp,
            )
        async for line in resp.aiter_lines():
            if not line.strip():
                continue
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError:
                continue
            # Каждый chunk: {"message": {"content": "..."}, "done": false}
            msg = chunk.get("message", {})
            if msg.get("content"):
                content_parts.append(msg["content"])
            if chunk.get("done"):
                done_reason = chunk.get("done_reason", "stop")
                break

    content = _strip_garbage_tokens("".join(content_parts))
    return content, done_reason


async def ask_agent(
    logger: logging.Logger,
    agent: str,
    user_text: str,
    cache: ThreadSafeCache,
    attempt: int = 0,
    randomize: bool = False,
    language: str = "python",
    max_retries: int = MAX_LLM_RETRIES,
    client: Optional[httpx.AsyncClient] = None,
) -> dict:
    model = get_model(agent, attempt, randomize=randomize)
    log_model_choice(logger, agent, model, attempt)

    ckey = cache_key(agent, model, user_text, language) if agent in CACHEABLE_AGENTS and attempt == 0 else None

    if ckey is not None:
        if ckey in cache:
            logger.info(f"[{agent}:{model}] Cache hit")
            return cache[ckey]

    sys_prompt  = get_system_prompt(agent, language)
    temperature = AGENT_TEMPERATURES.get(agent, 0.2)

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user",   "content": user_text},
    ]

    _client = client or httpx.AsyncClient(timeout=_HTTPX_TIMEOUT)
    _own_client = client is None

    last_exc: Exception = LLMError("Нет попыток")
    try:
        for retry in range(max_retries):
            if retry > 0:
                delay = 2 ** retry
                logger.info(f"[{agent}:{model}] Backoff {delay}с (retry={retry})")
                await asyncio.sleep(delay)
            raw: str | None = None
            try:
                raw, done_reason = await _ollama_chat(
                    _client, model, messages, temperature, LLM_MAX_TOKENS, json_mode=True,
                )
                if not raw:
                    raise LLMError(f"[{agent}:{model}] пустой ответ от LLM (json)")
                if done_reason == "length":
                    logger.warning(f"[{agent}:{model}] ⚠️ ответ обрезан (done_reason=length, num_predict={LLM_MAX_TOKENS})")
                result = json.loads(raw)
                if not isinstance(result, dict) or not result:
                    raise json.JSONDecodeError(
                        f"Ожидался непустой dict, получен {type(result).__name__}", raw or "", 0
                    )
                log_interaction(logger, agent, model, sys_prompt + "\n\n" + user_text, raw or "")
                if ckey is not None:
                    cache[ckey] = result
                return result
            except _RETRYABLE_ERRORS as e:
                last_exc = e
                if isinstance(e, (httpx.TimeoutException, asyncio.TimeoutError)):
                    logger.warning(f"[{agent}:{model}] таймаут ({type(e).__name__}), retry {retry+1}/{max_retries}")
                    continue  # retry без fallback на plain text
                logger.warning(f"[{agent}:{model}] json_object failed: {e}, пробую plain text...")
                try:
                    raw, done_reason = await _ollama_chat(
                        _client, model, messages, temperature, LLM_MAX_TOKENS, json_mode=False,
                    )
                    if not raw:
                        raise LLMError(f"[{agent}:{model}] пустой ответ от LLM (plain)")
                    if done_reason == "length":
                        logger.warning(f"[{agent}:{model}] ⚠️ ответ обрезан (done_reason=length)")
                    result = extract_json_from_text(raw)
                    if not isinstance(result, dict) or not result:
                        raise json.JSONDecodeError(
                            f"Ожидался непустой dict, получен {type(result).__name__}", raw or "", 0
                        )
                    log_interaction(logger, agent, model, sys_prompt + "\n\n" + user_text, raw or "")
                    if ckey is not None:
                        cache[ckey] = result
                    return result
                except _RETRYABLE_ERRORS as e2:
                    last_exc = e2
                    logger.warning(f"[{agent}:{model}] plain text fallback failed: {e2}")

        raise LLMError(f"[{agent}:{model}] все попытки исчерпаны") from last_exc
    finally:
        if _own_client:
            await _client.aclose()

```
### 📄 `log_utils.py`

```python
import logging
import queue
import random
import sys
import threading
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import FACTORY_DIR, LOGS_DIR, LOG_LEVEL, LOG_FILE_MAX_BYTES, LOG_INTERACTION_CHARS
from models_pool import MODEL_POOLS


def get_model(agent: str, attempt: int = 0, randomize: bool = False) -> str:
    pool = MODEL_POOLS.get(agent, ["qwen3:latest"])
    if randomize:
        return random.choice(pool)
    return pool[attempt % len(pool)]


def log_model_choice(logger: logging.Logger, agent: str, model: str, attempt: int) -> None:
    logger.info(f"[{agent}] attempt={attempt} → model={model}")


def input_with_timeout(prompt: str, timeout: int, default: str) -> str:
    print(prompt, end="", flush=True)
    q: queue.Queue[str] = queue.Queue()

    def _read() -> None:
        try:
            q.put(input().strip())
        except EOFError:
            q.put(default)

    threading.Thread(target=_read, daemon=True).start()
    try:
        return q.get(timeout=timeout)
    except queue.Empty:
        print(f"\n[⏳ Таймаут {timeout}с → автовыбор: '{default}']")
        return default


def setup_logger(project_path: Path) -> logging.Logger:
    """Логи пишутся в .factory/logs/. Консоль — через StreamHandler на root logger."""
    logs_dir = project_path / FACTORY_DIR / LOGS_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(str(project_path))
    if logger.handlers:
        return logger

    level = logging.getLevelName(LOG_LEVEL)
    if not isinstance(level, int):
        level = logging.INFO
    logger.setLevel(logging.DEBUG)

    # Файловый обработчик (DEBUG — все детали)
    file_handler = RotatingFileHandler(
        logs_dir / "agent_interactions.log",
        maxBytes=LOG_FILE_MAX_BYTES,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(file_handler)

    # Консольный обработчик на root logger — виден и модульным логгерам (infra, state, …)
    root = logging.getLogger()
    if not any(type(h) is logging.StreamHandler for h in root.handlers):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        root.addHandler(console_handler)
        root.setLevel(level)

    return logger


def log_interaction(
    logger: logging.Logger, agent: str, model: str,
    prompt: str, response: str, max_chars: int = LOG_INTERACTION_CHARS
) -> None:
    sep = "=" * 50
    logger.debug(
        f"\n{sep}\nАГЕНТ: {agent} | МОДЕЛЬ: {model}\n"
        f"--- PROMPT ---\n{prompt[:max_chars]}\n"
        f"--- RESPONSE ---\n{response[:max_chars]}\n{sep}"
    )


def log_runtime_error(project_path: Path, stderr: str) -> None:
    """Ошибки рантайма — в .factory/logs/."""
    logs_dir = project_path / FACTORY_DIR / LOGS_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)
    with open(logs_dir / "run_errors.log", "a", encoding="utf-8") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n[{ts}] SYSTEM CRASH:\n{stderr}\n{'-' * 40}\n")

```
### 📄 `models_pool.py`

```python
# ── Пулы моделей по роли ─────────────────────────────────────────────────────
MODEL_POOLS: dict[str, list[str]] = {
    "developer":        ["deepseek-coder:6.7b"],
    "reviewer":         ["deepseek-coder:6.7b"],
    "e2e_architect":    ["qwen3:latest"],
    "e2e_qa":           ["qwen3:latest"],
    "qa_runtime":       ["deepseek-coder:6.7b"],
    "business_analyst": ["qwen3:latest"],
    "system_analyst":   ["deepseek-coder:6.7b"],
    "architect":        ["deepseek-coder:6.7b"],
    "spec_reviewer":    ["qwen3:latest"],
    "test_generator":   ["deepseek-coder:6.7b"],
    "documenter":       ["qwen3:latest"],
    "devops_runtime":   ["qwen3:latest"],
    "arch_validator":   ["deepseek-coder:6.7b"],
    "supervisor":       ["qwen3:latest"],
    "self_reflect":     ["deepseek-coder:6.7b"],
    "contract_analyst": ["deepseek-coder:6.7b"],
    "a5_validator":          ["deepseek-coder:6.7b"],
    "a5_business_reviewer":  ["qwen3:latest"],
    "a5_architect_reviewer": ["qwen3:latest"],
    "a5_contract_reviewer":  ["deepseek-coder:6.7b"],
}
```
### 📄 `phase_develop.py`

```python
import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Optional

from config import (
    MAX_FILE_ATTEMPTS, MAX_CONTEXT_CHARS, SRC_DIR,
    MAX_A5_PATCHES_PER_FILE, SELF_REFLECT_RETRIES, TRUNCATE_FEEDBACK,
)

MAX_CUMULATIVE = MAX_FILE_ATTEMPTS * 3  # После 15 суммарных попыток — принудительный APPROVE

from exceptions import LLMError
from llm import ask_agent
from stats import ModelStats
from json_utils import to_str, safe_contract
from lang_utils import LANG_DISPLAY
from log_utils import get_model
from code_context import (
    get_global_context, get_full_context, build_dependency_order,
    validate_imports, validate_cross_file_names,
)
from state import push_feedback, get_feedback_ctx
from artifacts import update_artifact_a9, save_artifact
from contract import patch_contract_for_file
from cache import ThreadSafeCache
from checks import (
    sanitize_llm_code, ensure_a5_imports,
    check_function_preservation, check_class_duplication,
    check_import_shadowing, check_data_only_violations,
    check_stub_functions, check_contract_compliance,
)


async def _review_file(
    logger: logging.Logger,
    cache: ThreadSafeCache,
    current_file: str,
    code: str,
    attempt: int,
    stats: ModelStats,
    randomize: bool = False,
    language: str = "python",
    file_contract: list | None = None,
    global_imports: list | None = None,
) -> tuple[str, str, bool]:
    """Возвращает (status, feedback, needs_spec_revision)."""
    rev_model = get_model("reviewer", attempt, randomize=randomize)
    logger.info(f"👀 [{rev_model}] Reviewer проверяет {current_file} ...")
    try:
        rev_ctx = ""
        if file_contract:
            rev_ctx += f"API КОНТРАКТ (A5) для {current_file}:\n{json.dumps(file_contract, ensure_ascii=False, indent=2)}\n\n"
        if global_imports:
            rev_ctx += f"ОЖИДАЕМЫЕ ИМПОРТЫ (A5):\n{json.dumps(global_imports, ensure_ascii=False, indent=2)}\n\n"
        rev_ctx += f"Файл: {current_file}\nКод:\n{code}"
        result   = await ask_agent(logger, "reviewer", rev_ctx,
                                   cache, attempt, randomize, language)
        status   = result.get("status", "REJECT")
        feedback = to_str(result.get("feedback", ""))
        needs_spec = bool(result.get("needs_spec_revision", False))
        stats.record("reviewer", rev_model, status == "APPROVE")
        if needs_spec:
            logger.warning(f"  📋 Reviewer: проблема уровня спецификации для {current_file}")
        return status, feedback, needs_spec
    except (LLMError, ValueError) as e:
        logger.exception(f"Reviewer упал: {e}")
        stats.record("reviewer", rev_model, False)
        return "REJECT", f"Reviewer упал: {e}", False


async def do_self_reflect(
    logger: logging.Logger,
    cache: ThreadSafeCache,
    src_path: Path,
    current_file: str,
    code: str,
    state: dict,
    stats: ModelStats,
    randomize: bool = False,
) -> tuple[str, str]:
    """Self-Reflect проверяет соответствие A2 и A5."""
    language  = state.get("language", "python")
    sr_model  = get_model("self_reflect", 0, randomize=randomize)
    logger.info(f"🤔 [{sr_model}] Self-Reflect проверяет {current_file} ...")

    # Контракт для текущего файла из A5
    file_contract  = safe_contract(state).get("file_contracts", {}).get(current_file, [])
    global_imports = safe_contract(state).get("global_imports", {}).get(current_file, [])

    try:
        ctx = (
            f"Файл: {current_file}\nКод:\n{code}\n\n"
            f"Спецификации (A2):\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
            f"МИНИМАЛЬНЫЙ API контракт A5 (все эти функции ДОЛЖНЫ быть реализованы):\n"
            f"{json.dumps(file_contract, ensure_ascii=False, indent=2)}\n\n"
            f"Ключевые внешние импорты из A5 (могут быть расширены разработчиком — это нормально):\n"
            f"{json.dumps(global_imports, ensure_ascii=False, indent=2)}"
        )
        result   = await ask_agent(logger, "self_reflect", ctx, cache, 0, randomize, language, max_retries=SELF_REFLECT_RETRIES)
        status   = result.get("status", "OK")
        feedback = to_str(result.get("feedback", ""))
        improved = sanitize_llm_code(to_str(result.get("improved_code", "")))

        if status == "NEEDS_IMPROVEMENT" and improved:
            (src_path / current_file).write_text(improved, encoding="utf-8")
            logger.info(f"  → Self-Reflect улучшил код: {feedback[:TRUNCATE_FEEDBACK]}")

        stats.record("self_reflect", sr_model, status == "OK")
        return status, feedback
    except (LLMError, ValueError) as e:
        logger.exception(f"Self-Reflect упал: {e}")
        stats.record("self_reflect", sr_model, False)
        return "OK", ""


async def phase_validate_architecture(
    logger: logging.Logger,
    project_path: Path,
    state: Optional[dict],
    cache: ThreadSafeCache,
    stats: ModelStats,
    arch_resp: dict,
    sa_resp: dict,
    task: str,
    language: str = "python",
    randomize: bool = False,
) -> bool:
    arch_text = json.dumps(arch_resp, ensure_ascii=False, indent=2)
    sa_text   = json.dumps(sa_resp,   ensure_ascii=False, indent=2)

    validation_map = [
        ("Системный аналитик", "system_analyst",
         "Проверь соответствие архитектуры бизнес-требованиям и спецификации."),
        ("Architect Validator", "arch_validator",
         "Проверь реализуемость, production-readiness и корректность для языка."),
        ("DevOps-инженер",     "devops_runtime",
         "Проверь Docker-совместимость, корректность зависимостей и базового образа."),
    ]

    rejections = 0
    for label, agent_key, instruction in validation_map:
        logger.info(f"🔍 Валидация архитектуры — {label} ...")
        val_ctx = (
            f"Запрос: {task}\n\n"
            f"Спецификация (SA): {sa_text}\n\n"
            f"Предложенная архитектура: {arch_text}\n\n"
            f"Язык: {LANG_DISPLAY.get(language, language)}\n\n"
            f"Задача проверки: {instruction}"
        )
        try:
            val_resp = await ask_agent(logger, agent_key, val_ctx, cache, 0, randomize, language)
            if val_resp.get("status") in ("REJECT", "CANNOT_FIX"):
                fb = to_str(val_resp.get("feedback", val_resp.get("explanation", "")))
                logger.warning(f"  ❌ {label} отклонил: {fb[:TRUNCATE_FEEDBACK]}")
                rejections += 1
                stats.record(agent_key, get_model(agent_key), False)
            else:
                logger.info(f"  ✅ {label} одобрил.")
                stats.record(agent_key, get_model(agent_key), True)
        except (LLMError, ValueError) as e:
            logger.exception(f"{label} упал: {e}")
            rejections += 1

        if rejections > 1:
            return False

    logger.info("✅ Архитектура прошла многоуровневую валидацию!")
    return True

async def phase_a5_compliance_review(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    randomize: bool = False,
) -> bool:
    logger.info("\n🔍 A5 Compliance Review (BA + Architect + Contract) ...")
    language = state.get("language", "python")
    src_path = project_path / SRC_DIR

    all_code = get_full_context(src_path, state["files"])
    a5_contract = safe_contract(state)

    agents = [
        ("a5_business_reviewer", "Business Analyst"),
        ("a5_architect_reviewer", "Architect"),
        ("a5_contract_reviewer", "Contract Compliance"),
    ]

    gather_results = await asyncio.gather(
        *[ask_agent(logger, ak,
                    f"A5 Contract:\n{json.dumps(a5_contract, ensure_ascii=False, indent=2)}\n\n"
                    f"Код проекта:\n{all_code}\n\n"
                    f"A1/A2:\n{json.dumps(state.get('business_requirements', {}), ensure_ascii=False, indent=2)}\n"
                    f"A3/A4:\n{state.get('architecture', '')}",
                    cache, 0, randomize, language)
          for ak, _ in agents],
        return_exceptions=True,
    )

    rejections = []
    for (agent_key, label), result in zip(agents, gather_results):
        if isinstance(result, Exception):
            logger.exception(f"{label} упал")
            rejections.append((agent_key, "CRITICAL", str(result)))
            continue

        status = result.get("status", "REJECT")
        feedback = to_str(result.get("feedback", ""))
        if status == "REJECT":
            rejections.append((agent_key, label, feedback))
            stats.record(agent_key, get_model(agent_key), False)
        else:
            stats.record(agent_key, get_model(agent_key), True)

    if rejections:
        logger.warning(f"❌ A5 Compliance отклонён ({len(rejections)} ревьюеров)")
        combined_fb = "\n\n".join([f"[{label}] {fb}" for _, label, fb in rejections])
        for f in state["files"]:
            state["feedbacks"][f] = f"A5 COMPLIANCE REJECT:\n{combined_fb}"
            if f in state.get("approved_files", []):
                state["approved_files"].remove(f)
        save_artifact(project_path, "A5.1", {"status": "REJECT", "rejections": rejections})
        return False

    logger.info("✅ A5 полностью соответствует всем артефактам!")
    state["a5_compliance_passed"] = True
    save_artifact(project_path, "A5.1", {"status": "APPROVE_ALL"})
    return True

def _reject_file(
    state: dict,
    file_attempts: dict,
    cumulative_attempts: dict,
    current_file: str,
    attempt: int,
    total_attempts: int,
    feedback: str,
    stats: ModelStats,
    dev_model: str,
    logger: logging.Logger,
) -> None:
    """Записывает REJECT файла: статистика, feedback, инкремент счётчиков."""
    stats.record("developer", dev_model, False)
    push_feedback(state, current_file, feedback)
    file_attempts[current_file] = attempt + 1
    cumulative_attempts[current_file] = total_attempts + 1


def _run_checks(
    code: str,
    existing_code: str,
    current_file: str,
    state: dict,
    file_contract: list,
    global_context: str,
    global_imports: list,
    language: str,
    src_path: Path,
) -> tuple[str, str] | None:
    """Запускает 9 детерминистских проверок на код.

    Возвращает (check_name, feedback) при первом провале, или None если все проверки пройдены.
    """
    req_path = src_path / "requirements.txt"

    # 1. Потеря функций из предыдущей версии
    if existing_code:
        last_fb = state.get("feedbacks", {}).get(current_file, "")
        pres_warnings = check_function_preservation(code, existing_code, last_fb, file_contract)
        if pres_warnings:
            return "function_preservation", (
                "АВТОМАТИЧЕСКИЙ REJECT — потеря функций из предыдущей версии:\n"
                + "\n".join(f"  - {w}" for w in pres_warnings)
                + "\n\n⚠️ НЕ ПЕРЕПИСЫВАЙ файл с нуля. Исправь ТОЛЬКО то, что указано "
                "в фидбэке. Сохрани ВСЮ существующую структуру."
            )

    # 2. Дублирование классов из других файлов
    dup_warnings = check_class_duplication(code, global_context, file_contract)
    if dup_warnings:
        return "class_duplication", (
            "АВТОМАТИЧЕСКИЙ REJECT — дублирование классов из других файлов проекта:\n"
            + "\n".join(f"  - {w}" for w in dup_warnings)
            + "\n\nНЕ ОПРЕДЕЛЯЙ эти классы заново. Используй import."
        )

    # 3. Import shadowing (from X import Y + def Y)
    shadow_warnings = check_import_shadowing(code)
    if shadow_warnings:
        return "import_shadowing", (
            "АВТОМАТИЧЕСКИЙ REJECT — конфликт имён (import + определение):\n"
            + "\n".join(f"  - {w}" for w in shadow_warnings)
            + "\n\nЕсли имя импортировано из другого файла — НЕ определяй его заново."
        )

    # 4. Data-only файл не должен импортировать из проекта
    data_only_warnings = check_data_only_violations(code, current_file, state["files"])
    if data_only_warnings:
        return "data_only", (
            "АВТОМАТИЧЕСКИЙ REJECT — нарушение правил data-only файла:\n"
            + "\n".join(f"  - {w}" for w in data_only_warnings)
            + f"\n\n{current_file} — это файл для ХРАНЕНИЯ data structures.\n"
            "Он НЕ ДОЛЖЕН импортировать из других файлов проекта.\n"
            "Он НЕ ДОЛЖЕН содержать бизнес-логику (функции).\n"
            "Другие файлы импортируют ОТСЮДА, а не наоборот."
        )

    # 5. Валидность импортов (stdlib / pip / проект)
    import_warnings = validate_imports(
        code, current_file, state["files"],
        req_path if req_path.exists() else None, language, src_path,
    )
    if import_warnings:
        expected_hint = ""
        if global_imports:
            expected_hint = (
                "\n\nОЖИДАЕМЫЕ ИМПОРТЫ из A5 контракта для этого файла:\n"
                + "\n".join(f"  {imp}" for imp in global_imports)
            )
        req_content_hint = ""
        if req_path.exists():
            rc = req_path.read_text(encoding="utf-8").strip()
            if rc:
                req_content_hint = f"\n\nСодержимое requirements.txt (доступные пакеты):\n{rc}"
        return "imports", (
            "АВТОМАТИЧЕСКИЙ REJECT — невалидные импорты:\n"
            + "\n".join(f"  - {w}" for w in import_warnings)
            + "\n\nИсправь: используй только stdlib, pip-пакеты из requirements.txt "
            "или модули проекта: " + ", ".join(state["files"])
            + expected_hint
            + req_content_hint
        )

    # 6. Кросс-файловые имена (from X import Y → Y существует в X)
    if language == "python":
        xfile_warnings = validate_cross_file_names(code, current_file, state["files"], src_path)
        if xfile_warnings:
            return "cross_file_names", (
                "АВТОМАТИЧЕСКИЙ REJECT — ошибки кросс-файловых имён:\n"
                + "\n".join(f"  - {w}" for w in xfile_warnings)
                + "\n\nПроверь что все импортируемые имена определены в целевых файлах."
            )

    # 7. Функции-заглушки (pass, ..., NotImplementedError)
    stub_warnings = check_stub_functions(code)
    if stub_warnings:
        return "stubs", (
            "АВТОМАТИЧЕСКИЙ REJECT — функции-заглушки:\n"
            + "\n".join(f"  - {w}" for w in stub_warnings)
            + "\n\nВесь код должен быть полностью рабочим. Заглушки (pass, ..., "
            "raise NotImplementedError) и фиктивные реализации "
            "(захардкоженные return без использования параметров) ЗАПРЕЩЕНЫ."
        )

    # 8. Все required функции/классы из A5 контракта присутствуют
    contract_missing = check_contract_compliance(code, file_contract)
    if contract_missing:
        return "contract_compliance", (
            "АВТОМАТИЧЕСКИЙ REJECT — отсутствуют required элементы из A5 контракта:\n"
            + "\n".join(f"  - {m}" for m in contract_missing)
            + "\n\nРеализуй ВСЕ функции/классы, указанные в API контракте A5."
        )

    return None


def _build_dev_context(
    state: dict,
    current_file: str,
    existing_code: str,
    file_contract: list,
    global_imports: list,
    global_context: str,
    src_path: Path,
) -> str:
    """Собирает контекст для агента-разработчика."""
    dev_ctx = (
        f"Задача:\n{state['task']}\n\n"
        f"СИСТЕМНЫЕ СПЕЦИФИКАЦИИ (A2):\n"
        f"{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
        f"Файл для написания: `{current_file}`.\n\n"
    )

    # Специальная инструкция для entry point
    if current_file == state.get("entry_point"):
        dev_ctx += (
            "⚠️ ЭТОТ ФАЙЛ — ТОЧКА ВХОДА ПРИЛОЖЕНИЯ.\n"
            "НЕ определяй здесь бизнес-классы — они в других файлах, ИМПОРТИРУЙ их.\n"
            "Содержимое: импорты + инициализация + запуск (идиоматичная точка входа для целевого языка).\n\n"
        )

    # Специальная инструкция для data-only файлов
    if Path(current_file).stem in ("models", "data_models"):
        dev_ctx += (
            "⚠️ ЭТОТ ФАЙЛ — ХРАНИЛИЩЕ DATA STRUCTURES (data-only).\n"
            "ОБЯЗАТЕЛЬНО:\n"
            "  - Определи ЗДЕСЬ ВСЕ классы/структуры из контракта ниже\n"
            "  - Используй идиоматичные структуры данных для целевого языка\n"
            "КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО:\n"
            "  - Импортировать из ДРУГИХ ФАЙЛОВ ПРОЕКТА\n"
            "  - Определять PUBLIC top-level функции\n"
            "  - Допускаются ТОЛЬКО: stdlib импорты\n"
            "  - Приватные хелперы допустимы\n"
            "Другие модули будут импортировать структуры ОТСЮДА.\n\n"
        )

    # A5 контракт
    if file_contract:
        dev_ctx += (
            f"API КОНТРАКТ (A5) — реализуй ИМЕННО эти функции/классы:\n"
            f"{json.dumps(file_contract, ensure_ascii=False, indent=2)}\n\n"
        )
    if global_imports:
        dev_ctx += (
            f"ОЖИДАЕМЫЕ ИМПОРТЫ (A5):\n"
            f"{json.dumps(global_imports, ensure_ascii=False, indent=2)}\n\n"
        )

    # requirements.txt
    req_path = src_path / "requirements.txt"
    if req_path.exists():
        req_content = req_path.read_text(encoding="utf-8").strip()
        if req_content:
            dev_ctx += (
                f"ДОСТУПНЫЕ PIP-ПАКЕТЫ (requirements.txt):\n{req_content}\n"
                f"⛔ Импорт пакетов НЕ из этого списка будет отклонён.\n\n"
            )

    # Глобальный контекст
    if global_context:
        dev_ctx += f"ГЛОБАЛЬНЫЙ КОНТЕКСТ (public API других файлов):\n{global_context}\n\n"
        _import_hints: list[str] = []
        _cur_file = ""
        for _gc_line in global_context.splitlines():
            if _gc_line.startswith("--- ") and _gc_line.endswith(" PUBLIC API ---"):
                _cur_file = _gc_line.split("---")[1].strip().replace(" PUBLIC API", "").strip()
            elif _cur_file:
                _m = re.match(r"(?:class|def|async def)\s+(\w+)", _gc_line.strip())
                if _m:
                    _name = _m.group(1)
                    _stem = Path(_cur_file).stem
                    _import_hints.append(f"from {_stem} import {_name}")
        if _import_hints:
            dev_ctx += (
                f"⛔ ЗАПРЕЩЕНО ПЕРЕОПРЕДЕЛЯТЬ эти классы/функции — они УЖЕ СУЩЕСТВУЮТ.\n"
                f"ИСПОЛЬЗУЙ ИМПОРТ:\n"
                + "\n".join(f"  {h}" for h in _import_hints)
                + "\n\n"
            )

    # Существующий код
    if existing_code:
        max_code_chars = MAX_CONTEXT_CHARS // 2
        trimmed = existing_code[:max_code_chars] + "\n# [... код обрезан ...]" if len(existing_code) > max_code_chars else existing_code
        dev_ctx += f"ТЕКУЩИЙ КОД `{current_file}`:\n{trimmed}\n\n"

    # Feedback
    feedback_ctx = get_feedback_ctx(state, current_file)
    if feedback_ctx:
        max_feedback_chars = MAX_CONTEXT_CHARS // 3
        if len(feedback_ctx) > max_feedback_chars:
            feedback_ctx = feedback_ctx[:max_feedback_chars] + "\n[... обрезано ...]"
        if existing_code:
            dev_ctx += (
                "⚠️ ПРАВЬ ТОЧЕЧНО: текущий код уже предоставлен выше. "
                "Исправь ТОЛЬКО проблемы из фидбэка ниже, сохрани работающую структуру.\n\n"
            )
        dev_ctx += feedback_ctx

    return dev_ctx


async def phase_develop(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    randomize: bool = False,
) -> tuple[list[str], list[str]]:
    """Возвращает (exhausted_files, spec_blocked_files)."""
    language  = state.get("language", "python")
    src_path  = project_path / SRC_DIR
    order     = build_dependency_order(state["files"], src_path)
    file_attempts: dict[str, int] = state.setdefault("file_attempts", {})
    exhausted_files: list[str] = []
    spec_blocked_files: list[str] = []
    # Суммарные попытки (не сбрасываются при revise_spec) — для предохранителя
    if not isinstance(state.get("cumulative_file_attempts"), dict):
        state["cumulative_file_attempts"] = {}
    cumulative_attempts: dict[str, int] = state["cumulative_file_attempts"]

    for current_file in order:
        if current_file in state.get("approved_files", []):
            logger.info(f"⏭️  {current_file} уже одобрен.")
            continue

        attempt = file_attempts.get(current_file, 0)
        total_attempts = cumulative_attempts.get(current_file, 0)

        # Предохранитель: файл не проходит ревью после множества попыток → принудительный approve
        force_approve_mode = total_attempts >= MAX_CUMULATIVE
        if force_approve_mode:
            file_path = src_path / current_file
            if file_path.exists() and file_path.read_text(encoding="utf-8").strip():
                # Перед force-approve: инжектируем A5 imports в код на диске
                gi = safe_contract(state).get("global_imports", {}).get(current_file, [])
                if gi:
                    existing = file_path.read_text(encoding="utf-8")
                    patched = ensure_a5_imports(existing, gi)
                    if patched != existing:
                        file_path.write_text(patched, encoding="utf-8")
                        logger.info(f"  📎 {current_file}: A5 imports авто-инжектированы при force-approve")
                logger.warning(
                    f"⚠️  {current_file} не прошёл ревью за {total_attempts} суммарных попыток "
                    f"→ принудительный APPROVE (код есть, проверим при интеграции)."
                )
                approved = state.setdefault("approved_files", [])
                if current_file not in approved:
                    approved.append(current_file)
                state["feedbacks"][current_file] = ""
                file_attempts[current_file] = 0
                continue
            else:
                # Файл не на диске — даём developer ещё попытку, approve после записи
                logger.warning(
                    f"⚠️  {current_file}: cumulative={total_attempts} но файла нет на диске "
                    f"→ пишем код без проверок."
                )
                file_attempts[current_file] = 0
                attempt = 0

        if attempt >= MAX_FILE_ATTEMPTS:
            logger.warning(
                f"⚠️  {current_file} исчерпал {MAX_FILE_ATTEMPTS} попыток → эскалация в spec_reviewer."
            )
            state["feedbacks"][current_file] = (
                f"Файл не удалось написать за {MAX_FILE_ATTEMPTS} попыток. "
                "Возможно, спецификация противоречива. Требуется revise_spec."
            )
            exhausted_files.append(current_file)
            continue

        file_path = src_path / current_file
        # Проверяем, что файл не выходит за пределы src_path (защита от ../атак)
        try:
            file_path.resolve().relative_to(src_path.resolve())
        except ValueError:
            logger.warning(f"Небезопасный путь файла: {current_file} — пропускаю.")
            continue
        file_path.parent.mkdir(parents=True, exist_ok=True)

        existing_code  = file_path.read_text(encoding="utf-8").strip() if file_path.exists() else ""
        global_context = get_global_context(src_path, state["files"], exclude=current_file)

        # A5: контракт для текущего файла
        file_contract  = safe_contract(state).get("file_contracts", {}).get(current_file, [])
        global_imports = safe_contract(state).get("global_imports", {}).get(current_file, [])

        # Патч A5 после 3+ неудачных попыток — контракт может не соответствовать реальности
        # Лимит: не более 2 патч-ресетов на файл (чтобы не откладывать force-approve бесконечно)
        a5_patch_counts: dict = state.setdefault("_a5_patch_counts", {})
        patches_done = a5_patch_counts.get(current_file, 0)
        if attempt >= 3 and file_contract and existing_code and patches_done < MAX_A5_PATCHES_PER_FILE:
            last_feedback = state.get("feedbacks", {}).get(current_file, "")
            if last_feedback:
                patched = await patch_contract_for_file(
                    logger, project_path, state, cache, stats,
                    current_file, existing_code, last_feedback, randomize,
                )
                if patched:
                    a5_patch_counts[current_file] = patches_done + 1
                    file_contract  = safe_contract(state).get("file_contracts", {}).get(current_file, [])
                    global_imports = safe_contract(state).get("global_imports", {}).get(current_file, [])
                    # Сброс попыток после патча A5 — дать developer шанс с новым контрактом
                    file_attempts[current_file] = 0
                    attempt = 0
                    logger.info(f"🔄 A5 для {current_file} обновлён (патч {patches_done + 1}/{MAX_A5_PATCHES_PER_FILE}) → счётчик попыток сброшен.")

        dev_ctx = _build_dev_context(
            state, current_file, existing_code, file_contract, global_imports, global_context, src_path,
        )

        dev_model = get_model("developer", attempt, randomize=randomize)
        logger.info(
            f"💻 [{dev_model}] Разработчик пишет {current_file} (попытка {attempt + 1}/{MAX_FILE_ATTEMPTS}) ..."
        )

        try:
            dev_resp = await ask_agent(logger, "developer", dev_ctx, cache, attempt, randomize, language)
            code     = sanitize_llm_code(dev_resp.get("code", ""))
        except (LLMError, ValueError) as e:
            logger.exception(f"Developer упал: {e}")
            stats.record("developer", dev_model, False)
            state["feedbacks"][current_file] = f"Агент не вернул код: {e}"
            file_attempts[current_file] = attempt + 1
            cumulative_attempts[current_file] = total_attempts + 1
            continue

        if not code:
            stats.record("developer", dev_model, False)
            state["feedbacks"][current_file] = "Агент вернул пустой код."
            file_attempts[current_file] = attempt + 1
            cumulative_attempts[current_file] = total_attempts + 1
            continue

        # Проверка: если код — только imports + пустые строки (модель не написала тело функций),
        # генерируем скелет из A5 контракта и повторяем запрос с ним как "existing_code"
        code_lines = [ln for ln in code.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        has_functions = any(ln.strip().startswith(("def ", "class ", "async def ")) for ln in code_lines)
        if not has_functions and file_contract and attempt < MAX_FILE_ATTEMPTS - 1:
            logger.warning(
                f"  ⚠️  {current_file}: developer вернул код без функций/классов — генерирую скелет из A5"
            )
            skeleton_parts = []
            if global_imports:
                for imp in global_imports:
                    if isinstance(imp, str):
                        skeleton_parts.append(imp)
                skeleton_parts.append("")
            for item in file_contract:
                if not isinstance(item, dict):
                    continue
                sig = item.get("signature", "")
                hints = item.get("implementation_hints", "")
                desc = item.get("description", "")
                if sig.strip().startswith("class "):
                    skeleton_parts.append(f"{sig}:")
                    skeleton_parts.append(f"    \"\"\"{desc}\"\"\"")
                    skeleton_parts.append(f"    # TODO: {hints}")
                    skeleton_parts.append(f"    pass")
                    skeleton_parts.append("")
                elif sig.strip().startswith(("def ", "async def ")):
                    skeleton_parts.append(f"{sig}:")
                    skeleton_parts.append(f"    \"\"\"{desc}\"\"\"")
                    skeleton_parts.append(f"    # Алгоритм: {hints}")
                    skeleton_parts.append(f"    pass")
                    skeleton_parts.append("")
            skeleton_code = "\n".join(skeleton_parts)
            state["feedbacks"][current_file] = (
                f"Ты вернул код БЕЗ функций/классов — только импорты.\n"
                f"НИЖЕ — СКЕЛЕТ из A5 контракта. Заполни ВСЕ функции/классы реальным кодом.\n"
                f"Убери pass и TODO, напиши ПОЛНУЮ рабочую реализацию по алгоритму в комментариях.\n"
            )
            # Записываем скелет как existing_code для следующей попытки
            file_path.write_text(skeleton_code, encoding="utf-8")
            file_attempts[current_file] = attempt + 1
            cumulative_attempts[current_file] = total_attempts + 1
            stats.record("developer", dev_model, False)
            continue

        # Авто-инъекция A5 импортов — developer часто забывает import numpy, from typing и т.д.
        if global_imports:
            code = ensure_a5_imports(code, global_imports)

        # Force-approve mode: файл не на диске после MAX_CUMULATIVE попыток →
        # записываем что есть и approve без проверок
        if force_approve_mode:
            file_path.write_text(code, encoding="utf-8")
            logger.warning(
                f"⚠️  {current_file}: force-approve mode → код записан и одобрен без проверок."
            )
            stats.record("developer", dev_model, True)
            approved = state.setdefault("approved_files", [])
            if current_file not in approved:
                approved.append(current_file)
            state["feedbacks"][current_file] = ""
            file_attempts[current_file] = 0
            continue

        # Детерминистские проверки (9 штук)
        check_result = _run_checks(
            code, existing_code, current_file, state, file_contract,
            global_context, global_imports, language, src_path,
        )
        if check_result:
            check_name, check_feedback = check_result
            logger.warning(f"⛔ {current_file}: {check_name} → авто-REJECT")
            _reject_file(state, file_attempts, cumulative_attempts, current_file,
                         attempt, total_attempts, check_feedback, stats, dev_model, logger)
            continue

        file_path.write_text(code, encoding="utf-8")

        # Self-Reflect с проверкой A5
        sr_status, sr_feedback = await do_self_reflect(
            logger, cache, src_path, current_file, code, state, stats, randomize
        )
        if sr_status == "NEEDS_IMPROVEMENT":
            # Перечитываем файл — self-reflect мог записать улучшенный код
            new_code = file_path.read_text(encoding="utf-8")
            # Повторяем проверки — если self-reflect ввёл ошибки, откатываем
            sr_check = _run_checks(
                new_code, code, current_file, state, file_contract,
                global_context, global_imports, language, src_path,
            )
            if sr_check:
                logger.warning(f"  ⚠️  Self-reflect ввёл ошибки ({sr_check[0]}) → откат")
                file_path.write_text(code, encoding="utf-8")
            else:
                code = new_code

        # Внешний ревью
        rev_status, rev_feedback, needs_spec = await _review_file(
            logger, cache, current_file, code, attempt, stats, randomize, language,
            file_contract=file_contract, global_imports=global_imports,
        )

        if rev_status == "APPROVE":
            stats.record("developer", dev_model, True)
            logger.info(f"✅ {current_file} одобрен.")
            approved = state.setdefault("approved_files", [])
            if current_file not in approved:
                approved.append(current_file)
            state["feedbacks"][current_file] = ""
            state.setdefault("feedback_history", {})[current_file] = []
            file_attempts[current_file] = 0
            # Обновляем A9 (Implementation Logs)
            update_artifact_a9(project_path, current_file, f"Одобрен на попытке {attempt + 1}. Модель: {dev_model}.")
        else:
            stats.record("developer", dev_model, False)
            combined = "\n".join(filter(None, [to_str(sr_feedback), to_str(rev_feedback)]))
            # Защита от пустого feedback при REJECT
            if not combined:
                combined = (
                    f"Reviewer отклонил {current_file} без конкретных замечаний. "
                    "Проверь: корректность импортов из других файлов проекта, "
                    "соответствие API контракту A5, полноту реализации всех функций, "
                    "типы данных параметров и возвращаемых значений."
                )
            # Уведомление: spec зафиксирована
            if needs_spec and len(state.get("spec_history", [])) >= 3:
                combined += (
                    "\n\nСПЕЦИФИКАЦИЯ ЗАФИКСИРОВАНА (лимит ревизий исчерпан). "
                    "НЕ жди изменений спецификации — реши проблему В РАМКАХ текущего API контракта. "
                    "Адаптируй код под текущие интерфейсы файлов проекта."
                )
            logger.warning(f"❌ {current_file} отклонён: {combined[:TRUNCATE_FEEDBACK]}")
            push_feedback(state, current_file, combined)
            file_attempts[current_file] = attempt + 1
            cumulative_attempts[current_file] = total_attempts + 1
            # Эскалация на spec только после 3+ неудачных попыток
            # (до этого patch_contract_for_file попробует починить A5)
            if needs_spec and attempt + 1 >= MAX_FILE_ATTEMPTS and current_file not in spec_blocked_files:
                spec_blocked_files.append(current_file)

    return exhausted_files, spec_blocked_files

```
### 📄 `phase_test.py`

```python
import asyncio
import json
import logging
import re
from pathlib import Path

from config import (
    MAX_FILE_ATTEMPTS, MAX_TEST_ATTEMPTS, MIN_COVERAGE,
    FACTORY_DIR, LOGS_DIR, SRC_DIR, RUN_TIMEOUT,
    TRUNCATE_FEEDBACK, TRUNCATE_LOG, TRUNCATE_ERROR_MSG,
)

MAX_CUMULATIVE = MAX_FILE_ATTEMPTS * 3

from exceptions import LLMError
from llm import ask_agent
from stats import ModelStats
from json_utils import to_str, safe_contract
from lang_utils import LANG_EXT, get_execution_command, get_test_command, get_docker_image
from log_utils import get_model, log_runtime_error
from code_context import (
    get_global_context, get_full_context,
    find_failing_file,
)
from state import update_dependencies, update_dockerfile, update_requirements
from infra import run_in_docker, build_docker_image
from cache import ThreadSafeCache
from checks import sanitize_llm_code, classify_test_error

# Детекция замаскированных ошибок (rc=0 но traceback в stdout)
_EXCEPTION_LINE_RE = re.compile(
    r"^\s*(?:(?:\w+\.)*\w+)?(?:Error|Exception):(?:\s+|\s*$)", re.MULTILINE
)


def _deapprove_file(state: dict, filename: str, feedback_msg: str, cumulative_bump: int = 3) -> None:
    """Де-апрувит файл: убирает из approved, бампит cumulative, ставит feedback."""
    if filename in state.get("approved_files", []):
        state["approved_files"].remove(filename)
    cum = state.setdefault("cumulative_file_attempts", {})
    cum[filename] = cum.get(filename, 0) + cumulative_bump
    state.setdefault("feedbacks", {})[filename] = feedback_msg


async def phase_e2e_review(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    attempt: int = 0,
    randomize: bool = False,
) -> bool:
    logger.info("\n🧐 Parallel E2E-ревью (Architect + QA) ...")
    language = state.get("language", "python")
    src_path = project_path / SRC_DIR
    all_code = get_full_context(src_path, state["files"])
    # Добавляем информацию о файлах проекта, чтобы ревьюер не галлюцинировал
    file_list_info = (
        f"\n\nПРОЕКТ СОСТОИТ РОВНО ИЗ ЭТИХ ФАЙЛОВ (других файлов НЕТ, не требуй создания новых): "
        f"{', '.join(state['files'])}\n"
    )
    all_code = file_list_info + all_code

    agents = [("e2e_architect", "Architect"), ("e2e_qa", "QA Lead")]
    result_ok = True
    rejections: list[tuple[str, str, str]] = []  # (agent_key, target, feedback)

    # Параллельный запуск через asyncio.gather вместо ThreadPoolExecutor
    gather_results = await asyncio.gather(
        *[ask_agent(logger, ak, all_code, cache, attempt, randomize, language) for ak, _ in agents],
        return_exceptions=True,
    )

    for (agent_key, label), result in zip(agents, gather_results):
        model = get_model(agent_key, attempt, randomize)
        if isinstance(result, Exception):
            logger.exception(f"[{label}] future error: {result}")
            stats.record(agent_key, model, False)
            result_ok = False
            continue

        resp = result
        if resp.get("status") == "REJECT":
            # Парсим structured issues (новый формат) с fallback на старый
            issues = resp.get("issues", [])
            if issues and isinstance(issues, list):
                for issue in issues:
                    if not isinstance(issue, dict):
                        continue
                    target = issue.get("file", "").strip()
                    if target not in state["files"]:
                        target = state["files"][0]
                    element  = issue.get("element", "")
                    severity = issue.get("severity", "MAJOR")
                    problem  = issue.get("problem", "")
                    fix_text = issue.get("fix", "")
                    structured_fb = f"[{severity}] {element}: {problem}\n  FIX: {fix_text}"
                    rejections.append((agent_key, target, structured_fb))
                logger.warning(f"❌ E2E [{label}] REJECT: {len(issues)} issues")
            else:
                # Fallback: старый формат target_file + feedback
                target   = resp.get("target_file", "").strip() or state["files"][0]
                feedback = to_str(resp.get("feedback", ""))
                logger.warning(f"❌ E2E [{label}] REJECT на {target}: {feedback[:TRUNCATE_FEEDBACK]}")
                rejections.append((agent_key, target, feedback))
            stats.record(agent_key, model, False)
            result_ok = False
        else:
            stats.record(agent_key, model, True)

    # E2E — селективный сброс с per-file targeted feedback.
    if rejections:
        agents_map = dict(agents)
        # Группируем feedback по файлам
        file_feedbacks: dict[str, list[str]] = {}
        for ak, target, fb in rejections:
            file_feedbacks.setdefault(target, []).append(
                f"[{agents_map.get(ak, ak)}]:\n{fb}"
            )
        target_files = list(file_feedbacks.keys())

        # Если targets пуст или покрывает > 50% файлов — полный сброс
        if not target_files or len(target_files) > len(state["files"]) * 0.5:
            combined_fb = "\n\n".join(
                f"[{agents_map.get(ak, ak)}] → {t}:\n{fb}"
                for ak, t, fb in rejections
            )
            logger.warning(f"❌ E2E REJECT — сброс ВСЕХ файлов (затронуто >{50 if target_files else 0}%).")
            state["approved_files"] = []
            for f in state["files"]:
                state["feedbacks"][f] = f"E2E REJECT (кросс-файловая проблема):\n{combined_fb}"
            files_to_reset = set(state["files"])
        else:
            # Находим зависимые файлы (импортирующие target_files)
            gi = safe_contract(state).get("global_imports", {})
            target_stems = {Path(t).stem for t in target_files}
            dependent_files = set()
            for f in state["files"]:
                if f in target_files:
                    continue
                file_imports = gi.get(f, [])
                imports_str = " ".join(file_imports) if isinstance(file_imports, list) else str(file_imports)
                if any(stem in imports_str for stem in target_stems):
                    dependent_files.add(f)
            files_to_reset = set(target_files) | dependent_files
            logger.warning(
                f"❌ E2E REJECT — селективный сброс: {', '.join(sorted(files_to_reset))} "
                f"(targets: {', '.join(target_files)}, зависимые: {', '.join(sorted(dependent_files)) or 'нет'})"
            )
            state["approved_files"] = [f for f in state.get("approved_files", []) if f not in files_to_reset]
            for f in files_to_reset:
                if f in file_feedbacks:
                    state["feedbacks"][f] = (
                        "E2E REJECT — проблемы в ЭТОМ файле:\n"
                        + "\n\n".join(file_feedbacks[f])
                    )
                else:
                    related = [t for t in target_files if t != f]
                    state["feedbacks"][f] = (
                        f"E2E REJECT (зависимый файл, затронут изменениями в: "
                        f"{', '.join(related) if related else 'проект'})"
                    )

        # Сброс счётчиков: первый E2E-сброс → частичный reset (дать 5 попыток),
        # повторные → не сбрасывать (developer уже пробовал с E2E фидбэком).
        e2e_resets = state.setdefault("e2e_cumulative_resets", {})
        cumulative = state.setdefault("cumulative_file_attempts", {})
        for f in files_to_reset:
            old_cum = cumulative.get(f, 0)
            resets_done = e2e_resets.get(f, 0)
            state["file_attempts"][f] = 0
            if resets_done < 1 and old_cum > 0:
                # Первый E2E-сброс: дать developer MAX_FILE_ATTEMPTS попыток
                new_cum = max(0, old_cum - MAX_FILE_ATTEMPTS)
                cumulative[f] = new_cum
                e2e_resets[f] = resets_done + 1
                logger.info(f"  🔄 {f}: cumulative {old_cum} → {new_cum} "
                            f"(E2E reset #{resets_done + 1}, дано {old_cum - new_cum} попыток)")
            elif old_cum > 0:
                # Повторный E2E-сброс: developer уже пробовал → не сбрасываем cumulative
                logger.info(f"  🔒 {f}: cumulative={old_cum}, E2E уже сбрасывал → "
                            f"оставляем (force-approve мгновенно)")

    if result_ok:
        logger.info("✅ Parallel E2E-ревью пройдено!")
    return result_ok


def phase_cross_file_check(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
) -> bool:
    """Детерминистская кросс-файловая проверка всего проекта перед E2E."""
    language = state.get("language", "python")
    if language != "python":
        return True

    src_path = project_path / SRC_DIR
    from code_context import validate_project_consistency
    issues = validate_project_consistency(src_path, state["files"])

    if not issues:
        logger.info("✅ Кросс-файловая проверка проекта пройдена.")
        return True

    total_issues = sum(len(w) for w in issues.values())
    logger.warning(f"⛔ Кросс-файловая проверка: {total_issues} проблем в {len(issues)} файлах")

    cumulative = state.setdefault("cumulative_file_attempts", {})
    has_actionable = False
    for filename, warnings in issues.items():
        if cumulative.get(filename, 0) >= MAX_CUMULATIVE:
            logger.warning(f"  ⚠️  {filename}: {len(warnings)} кросс-файловых проблем, "
                           f"но cumulative={cumulative[filename]} → оставляем APPROVE")
            continue
        feedback = (
            "АВТОМАТИЧЕСКИЙ REJECT — кросс-файловые ошибки (до E2E):\n"
            + "\n".join(f"  - {w}" for w in warnings)
        )
        was_approved = filename in state.get("approved_files", [])
        _deapprove_file(state, filename, feedback, cumulative_bump=2)
        if was_approved:
            logger.warning(f"  ⛔ {filename}: {len(warnings)} проблем → снят APPROVE")
        has_actionable = True

    if not has_actionable:
        logger.warning("⚠️  Кросс-файловые проблемы есть, но все файлы на cumulative лимите → пропускаем к E2E.")
        return True
    return False


def _fix_docker_requirements(src_path: Path, logger: logging.Logger) -> None:
    """Автоматическая замена пакетов, несовместимых с headless Docker-окружением."""
    req_path = src_path / "requirements.txt"
    if not req_path.exists():
        return
    HEADLESS_SUBSTITUTIONS = {
        "opencv-python": "opencv-python-headless",
        "opencv-contrib-python": "opencv-contrib-python-headless",
    }
    lines = req_path.read_text(encoding="utf-8").splitlines()
    changed = False
    new_lines = []
    for line in lines:
        pkg_base = re.split(r'[=<>~!\[]', line.strip())[0].strip().lower()
        if pkg_base in HEADLESS_SUBSTITUTIONS:
            replacement = HEADLESS_SUBSTITUTIONS[pkg_base]
            suffix = line.strip()[len(pkg_base):]
            new_line = replacement + suffix
            logger.info(f"  🔧 {line.strip()} → {new_line} (headless для Docker)")
            new_lines.append(new_line)
            changed = True
        else:
            new_lines.append(line)
    if changed:
        req_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


async def phase_integration_test(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    randomize: bool = False,
) -> bool:
    language    = state.get("language", "python")
    entry_point = state.get("entry_point", "main.py")
    src_path    = project_path / SRC_DIR
    dockerfile  = src_path / "Dockerfile"
    use_custom  = dockerfile.exists()
    image_tag   = f"{project_path.name}:latest" if use_custom else get_docker_image(language)

    # Превентивная замена пакетов, несовместимых с Docker (opencv → headless)
    if language == "python":
        _fix_docker_requirements(src_path, logger)

    # ── Сборка образа ────────────────────────────────────────────────────────
    if use_custom:
        build_success = False
        for build_attempt in range(1, 4):
            logger.info(f"\n🏗️ Сборка Docker-образа (попытка {build_attempt}/3) ...")
            build_success, _, build_err = build_docker_image(src_path, image_tag)
            if build_success:
                logger.info("✅ Образ собран.")
                break
            logger.error(f"❌ Ошибка сборки:\n{build_err[:TRUNCATE_ERROR_MSG]}")
            try:
                devops_ctx  = (
                    f"Ошибка сборки Docker:\n{build_err}\n\n"
                    f"Текущий Dockerfile:\n{dockerfile.read_text(encoding='utf-8')}"
                )
                devops_resp = await ask_agent(
                    logger, "devops_runtime", devops_ctx, cache, 0, randomize, language
                )
                stats.record("devops_runtime", get_model("devops_runtime"), True)
                patch = devops_resp.get("dockerfile_patch", "")
                if devops_resp.get("status") == "FIX_PROPOSED" and isinstance(patch, str) and patch.strip():
                    update_dockerfile(src_path, patch)
                    logger.info("  → Dockerfile обновлён, пересобираю.")
            except (LLMError, ValueError) as e:
                logger.exception(f"DevOps (build) упал: {e}")
                stats.record("devops_runtime", get_model("devops_runtime"), False)
    else:
        build_success = True

    if not build_success:
        state["feedbacks"][state["files"][0]] = "Не удалось собрать Docker-образ."
        return False

    # ── Запуск приложения ────────────────────────────────────────────────────
    for run_attempt in range(1, 6):
        logger.info(f"\n🚀 Запуск в Docker (попытка {run_attempt}/5) ...")
        cmd = get_execution_command(language, entry_point)

        env_fixes = state.get("env_fixes", {})
        if env_fixes.get("system_packages"):
            cmd = "apt-get update -q && apt-get install -y " + " ".join(env_fixes["system_packages"]) + " && " + cmd
        if language == "python":
            for orig, alt in (env_fixes.get("package_alternatives") or env_fixes.get("pip_alternatives") or {}).items():
                update_requirements(src_path, orig, alt)

        rc, stdout, stderr = run_in_docker(src_path, cmd, RUN_TIMEOUT, language)

        # Логи рантайма — в .factory/logs/
        logs_dir = project_path / FACTORY_DIR / LOGS_DIR
        logs_dir.mkdir(parents=True, exist_ok=True)
        (logs_dir / "test.log").write_text(
            f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}", encoding="utf-8"
        )
        logger.info(f"\n--- STDOUT ---\n{stdout[:TRUNCATE_LOG]}")
        logger.info(f"\n--- STDERR ---\n{stderr[:TRUNCATE_LOG]}")

        if rc == 0:
            combined_output = stdout + "\n" + stderr
            has_traceback = "Traceback (most recent call last)" in combined_output
            has_exception_line = bool(_EXCEPTION_LINE_RE.search(combined_output))
            if has_traceback and has_exception_line:
                logger.warning(
                    "⚠️  rc=0 но обнаружен traceback в выводе! "
                    "Программа поймала исключение через try/except. Считаем как провал."
                )
                log_runtime_error(project_path, combined_output)
                failing_file = find_failing_file(stderr, stdout, state["files"])
                _deapprove_file(state, failing_file, (
                    "ПРОГРАММА ЗАМАСКИРОВАЛА ОШИБКУ (rc=0, но traceback в выводе):\n"
                    f"{combined_output[-TRUNCATE_LOG:]}\n\n"
                    "Исправь причину exception — не ловить его через try/except, а устранить."
                ))
                return False

            logger.info("\n✅ Приложение завершилось успешно!")
            state["env_fixes"] = {}
            return True

        logger.error("\n💥 Ошибка выполнения!")
        log_runtime_error(project_path, stderr)

        # Ошибка pip install/build — проблема зависимостей, не кода
        if language == "python" and any(kw in stderr for kw in [
            "pip subprocess to install build dependencies did not run successfully",
            "Failed building wheel",
            "No matching distribution found",
            "Could not find a version that satisfies",
            "error: subprocess-exited-with-error",
        ]):
            logger.info("🔧 Ошибка pip install — исправляю requirements.txt ...")
            req_path = src_path / "requirements.txt"
            if req_path.exists():
                from code_context import WRONG_PIP_PACKAGES
                lines = req_path.read_text(encoding="utf-8").splitlines()
                new_lines = []
                fixed_wrong = False
                for line in lines:
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        new_lines.append(line)
                        continue
                    pkg_base = re.split(r'[=<>~!]', stripped)[0].strip()
                    if pkg_base in WRONG_PIP_PACKAGES:
                        correct_pip, _ = WRONG_PIP_PACKAGES[pkg_base]
                        logger.info(f"  → {pkg_base} → {correct_pip} (невалидный pip-пакет)")
                        new_lines.append(correct_pip)
                        fixed_wrong = True
                        continue
                    if pkg_base.lower() != stripped.lower():
                        logger.info(f"  → {stripped} → {pkg_base} (убрана версия)")
                        new_lines.append(pkg_base)
                    else:
                        new_lines.append(line)
                req_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
                if fixed_wrong:
                    logger.info("  ✅ requirements.txt: невалидные пакеты исправлены.")
                else:
                    logger.info("  ✅ requirements.txt обновлён (убраны версии).")
            continue

        failing_file = find_failing_file(stderr, stdout, state["files"])

        if any(kw in stderr.lower() for kw in ["lib", ".so", "cannot open shared object", "no such file"]):
            logger.info("🛠️  DevOps анализирует ошибку окружения ...")
            try:
                devops_ctx  = (
                    f"Traceback:\n{stderr}\n\n"
                    f"Dockerfile: {dockerfile.read_text(encoding='utf-8') if dockerfile.exists() else 'Нет'}"
                )
                devops_resp = await ask_agent(
                    logger, "devops_runtime", devops_ctx, cache, 0, randomize, language
                )
                stats.record("devops_runtime", get_model("devops_runtime"), True)
                if devops_resp.get("status") == "FIX_PROPOSED":
                    if devops_resp.get("dockerfile_patch"):
                        update_dockerfile(src_path, devops_resp["dockerfile_patch"])
                        logger.info("  → Dockerfile обновлён, требуется пересборка.")
                        return False
                    state["env_fixes"] = devops_resp
                    continue
            except (LLMError, ValueError) as e:
                logger.exception(f"DevOps (runtime) упал: {e}")
                stats.record("devops_runtime", get_model("devops_runtime"), False)

        qa_model = get_model("qa_runtime", run_attempt - 1, randomize)
        fix         = "Смотри traceback."
        missing_pkg = ""
        try:
            qa_resp     = await ask_agent(
                logger, "qa_runtime",
                f"Traceback:\n{stderr}\n\nФайл с ошибкой: {failing_file}",
                cache, run_attempt - 1, randomize, language,
            )
            fix         = qa_resp.get("fix", "Смотри traceback.")
            missing_pkg = qa_resp.get("missing_package", "").strip()
            agent_file  = qa_resp.get("file", "").strip()
            if agent_file and agent_file in state["files"]:
                failing_file = agent_file
            stats.record("qa_runtime", qa_model, True)
        except (LLMError, ValueError) as e:
            logger.exception(f"QA Runtime упал: {e}")
            stats.record("qa_runtime", qa_model, False)

        if missing_pkg:
            if language == "python":
                req_path = src_path / "requirements.txt"
                current_reqs = req_path.read_text(encoding="utf-8") if req_path.exists() else ""
                pkg_clean    = re.split(r'[=<>~]', missing_pkg)[0].strip().lower()
                existing     = [re.split(r'[=<>~]', l)[0].strip().lower()
                                for l in current_reqs.splitlines() if l.strip() and not l.startswith("#")]
                if pkg_clean in existing:
                    logger.warning(
                        f"⚠️  '{pkg_clean}' уже в requirements, но всё равно падает → возврат разработчику."
                    )
                    _deapprove_file(state, failing_file, (
                        f"ПРОГРАММА УПАЛА. Пакет '{pkg_clean}' установлен, но код падает. "
                        f"Проблема в логике или импортах.\nTraceback:\n{stderr}"
                    ))
                    return False
                else:
                    logger.info(f"🔧 Добавляю пакет: {missing_pkg}")
                    update_dependencies(src_path, language, missing_pkg)
                    continue
            elif language == "typescript":
                logger.info(f"🔧 Добавляю пакет в package.json: {missing_pkg}")
                update_dependencies(src_path, language, missing_pkg)
                continue

        _deapprove_file(state, failing_file, f"ПРОГРАММА УПАЛА.\nTRACEBACK:\n{stderr}\nQA:\n{fix}")
        logger.info("🔄 Возврат к разработчику.")
        return False

    return False


async def phase_unit_tests(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    randomize: bool = False,
) -> bool:
    logger.info("\n🧪 Генерация unit-тестов ...")
    language = state.get("language", "python")
    src_path = project_path / SRC_DIR

    if language == "python":
        _fix_docker_requirements(src_path, logger)

    all_code = get_global_context(src_path, state["files"])

    test_plan = state.get("test_plan", {})

    base_context = (
        f"Спецификации (A2):\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}"
        f"\n\nAPI Контракт (A5):\n{json.dumps(safe_contract(state), ensure_ascii=False, indent=2)}"
        f"\n\nТест-план (A7):\n{json.dumps(test_plan, ensure_ascii=False, indent=2)}"
        f"\n\nКод проекта:\n{all_code}"
    )

    prev_test_code: dict[str, str] = {}
    prev_error: str = ""
    last_stderr: str = ""
    last_stdout: str = ""

    for test_attempt in range(MAX_TEST_ATTEMPTS):
        tg_model = get_model("test_generator", test_attempt, randomize)
        logger.info(
            f"🧪 [{tg_model}] Генерация тестов "
            f"(попытка {test_attempt + 1}/{MAX_TEST_ATTEMPTS}) ..."
        )

        gen_context = base_context
        if prev_test_code and prev_error:
            prev_tests_str = "\n\n".join(
                f"=== {fname} ===\n{code}" for fname, code in prev_test_code.items()
            )
            gen_context += (
                f"\n\n⚠️ ПРЕДЫДУЩИЕ ТЕСТЫ УПАЛИ. Исправь ТОЧЕЧНО — НЕ переписывай с нуля.\n"
                f"\nПРЕДЫДУЩИЙ КОД ТЕСТОВ:\n{prev_tests_str}"
                f"\n\nОШИБКА:\n{prev_error[-TRUNCATE_LOG:]}"
                f"\n\nИСПРАВЬ ТОЛЬКО упавшие тесты. Сохрани работающие."
            )

        try:
            test_resp = await ask_agent(
                logger, "test_generator", gen_context,
                cache, test_attempt, randomize, language,
            )
            test_files = test_resp.get("test_files", [])
            stats.record("test_generator", tg_model, True)
        except (LLMError, ValueError) as e:
            logger.warning(f"⚠️  Не удалось сгенерировать тесты: {e}.")
            stats.record("test_generator", tg_model, False)
            if test_attempt == MAX_TEST_ATTEMPTS - 1:
                return True
            continue

        if not test_files:
            return True

        tests_dir = src_path / "tests"
        tests_dir.mkdir(exist_ok=True)
        if language == "python":
            (tests_dir / "__init__.py").write_text("", encoding="utf-8")

        current_test_code: dict[str, str] = {}
        for tf in test_files:
            if code := sanitize_llm_code(tf.get("code", "")):
                fname = tf.get("filename", f"test_generated.{LANG_EXT.get(language, 'py')}")
                resolved = (tests_dir / fname).resolve()
                if not resolved.is_relative_to(tests_dir.resolve()):
                    logger.warning(f"⚠️  Небезопасное имя теста: {fname} — пропускаю")
                    continue
                resolved.write_text(code, encoding="utf-8")
                current_test_code[fname] = code

        logger.info("🚀 Запуск тестов в Docker ...")
        cmd = get_test_command(language)
        rc, stdout, stderr = run_in_docker(src_path, cmd, RUN_TIMEOUT * 2, language)
        last_stderr = stderr
        last_stdout = stdout

        logs_dir = project_path / FACTORY_DIR / LOGS_DIR
        (logs_dir / "coverage.log").write_text(
            f"ATTEMPT {test_attempt + 1}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}",
            encoding="utf-8",
        )

        if rc == 0:
            m = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", stdout)
            coverage = int(m.group(1)) if m else 100

            if coverage < MIN_COVERAGE:
                logger.warning(f"❌ Покрытие {coverage}% < {MIN_COVERAGE}%")
                entry = state.get("entry_point", "main.py")
                _deapprove_file(state, entry, (
                    f"Покрытие {coverage}% < порога {MIN_COVERAGE}%. "
                    "Добавь публичные функции с понятными сигнатурами."
                ))
                return False

            logger.info(f"✅ Тесты пройдены! Покрытие: {coverage}%")
            return True

        # ── Тесты упали ──
        logger.warning(
            f"❌ Тесты провалены (попытка {test_attempt + 1}/{MAX_TEST_ATTEMPTS})"
        )

        if language == "python" and any(kw in stderr for kw in [
            "cannot open shared object file",
            "ImportError: lib",
            "pip subprocess to install build dependencies",
            "Failed building wheel",
            "No matching distribution found",
        ]):
            logger.warning("  ⚠️  Ошибка окружения Docker, не кода. Файлы не сбрасываем.")
            state["feedbacks"][state.get("entry_point", "main.py")] = (
                f"ОШИБКА ОКРУЖЕНИЯ DOCKER (не кода):\n{stderr[-TRUNCATE_LOG // 2:]}"
            )
            return False

        classification, failing_app_file = classify_test_error(
            stderr, stdout, state["files"]
        )

        if classification == "app_bug" and failing_app_file:
            logger.warning(
                f"  🐛 Ошибка в коде приложения ({failing_app_file}), не в тестах."
            )
            _deapprove_file(state, failing_app_file, (
                f"UNIT-ТЕСТЫ ОБНАРУЖИЛИ БАГ В КОДЕ:\n{stderr[-TRUNCATE_LOG:]}"
                f"\n\nВывод:\n{stdout[-TRUNCATE_LOG // 2:]}"
            ))
            return False

        logger.info(
            f"  🔧 Ошибка в тестах (не в приложении) → повтор генерации "
            f"({test_attempt + 1}/{MAX_TEST_ATTEMPTS})"
        )
        prev_test_code = current_test_code
        prev_error = f"STDERR:\n{stderr[-1500:]}\nSTDOUT:\n{stdout[-500:]}"

    # Исчерпали все попытки генерации тестов
    logger.warning(
        f"⚠️  Тесты не прошли за {MAX_TEST_ATTEMPTS} попыток генерации. "
        "Де-аппрувим по _find_failing_file."
    )
    failing_file = find_failing_file(last_stderr, last_stdout, state["files"])
    _deapprove_file(state, failing_file, (
        f"UNIT-ТЕСТЫ НЕ ПРОЙДЕНЫ ПОСЛЕ {MAX_TEST_ATTEMPTS} ПОПЫТОК ГЕНЕРАЦИИ:\n"
        f"{last_stderr[-TRUNCATE_LOG:]}\n\nВывод:\n{last_stdout[-TRUNCATE_LOG // 2:]}"
    ))
    return False

```
### 📄 `phases.py`

```python
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

```
### 📄 `prompts.py`

```python
# ─────────────────────────────────────────────
# ОБЩИЕ КОНСТАНТЫ ДЛЯ ВСЕХ ПРОМПТОВ
# ─────────────────────────────────────────────

JSON_OUTPUT_RULE = """
ФОРМАТ ОТВЕТА:
- ЗАПРЕЩЕНО использовать теги <think> и выводить процесс размышления.
- Верни СТРОГО JSON без markdown-разметки (без ```json)
- Начни ответ с символа { и закончи }
- Никаких пояснений до или после JSON
- Экранируй кавычки внутри строк правильно
"""
# NB: Эта инструкция дублирует response_format={"type": "json_object"} в ask_agent,
# но необходима как fallback — при ошибке json_object вызов повторяется без response_format.

ANTI_HALLUCINATION_RULE = """
ПРОВЕРКА ДОСТОВЕРНОСТИ:
- Не выдумывай функции, классы или файлы, которых не существует
- Не добавляй зависимости, которые не требуются явно
- Если информации недостаточно — укажи это в соответствующем поле
- Ссылайся только на данные из предоставленного контекста
"""

NO_STUBS_RULE = """
ЗАПРЕТ ЗАГЛУШЕК:
- Категорически запрещено: pass, ..., raise NotImplementedError, todo!(), unimplemented!(), throw new Error('Not implemented'), TODO, FIXME
- Запрещены комментарии: "тут будет код", "implement later", "your code here"
- Весь код должен быть полностью рабочим и исполняемым
"""


# ─────────────────────────────────────────────
# СИСТЕМНЫЕ ПРОМПТЫ
# ─────────────────────────────────────────────

PROMPTS: dict[str, str] = {

# ФАЗА 1: АНАЛИЗ И ПРОЕКТИРОВАНИЕ
# ─────────────────────────────────────────────

"business_analyst": f"""
Ты — Senior Business Analyst.
Цель: проанализировать запрос пользователя и составить чёткие бизнес-требования.

ПРАВИЛА:
1. KISS: не усложняй, не добавляй функционал, о котором не просили
2. Извлекай только явные требования из запроса
3. Не предполагай скрытый функционал
4. Фокусируйся на бизнес-ценности, а не технической реализации

{ANTI_HALLUCINATION_RULE}
{JSON_OUTPUT_RULE}

{{
  "project_goal": "Краткая цель (1-2 предложения)",
  "user_stories": ["Как <актор>, я хочу <действие>, чтобы <цель>"],
  "acceptance_criteria": ["Измеримый критерий 1", "Измеримый критерий 2"],
  "out_of_scope": ["Что явно НЕ входит в проект"]
}}
""",

# ─────────────────────────────────────────────

"system_analyst": f"""
Ты — Senior System Analyst.
На основе запроса и бизнес-требований составь техническую спецификацию.

ПРАВИЛА:
1. Только реально необходимое для выполнения user stories
2. Без конкретных имён файлов, классов и функций (это задача архитектора)
3. Описывай ЧТО система делает, а не КАК
4. Учитывай ограничения из acceptance_criteria
5. Для описания потоков данных, переменных, названий функций, классов ИСПОЛЬЗУЙ ТОЛЬКО АНГЛИЙСКИЙ ЯЗЫК.

{ANTI_HALLUCINATION_RULE}
{JSON_OUTPUT_RULE}

{{
  "data_models": [
    {{"name": "Сущность", "fields": ["поле: тип: описание"], "relationships": ["связь с другой сущностью"]}}
  ],
  "components": ["Логический компонент: ответственность"],
  "business_rules": ["Правило: условие: результат"],
  "external_systems": ["Внешние API/сервисы если нужны"]
}}
""",

# ─────────────────────────────────────────────

"architect": f"""
Ты — Senior Software Architect.
Спроектируй production-ready архитектуру на основе спецификации и целевого языка {{lang}}.

ПРАВИЛА:
1. Укажи ВСЕ внешние зависимости в формате {{lang}} (pip/npm/cargo)
2. Продумай структуру файлов для масштабируемости
3. Учитывай Docker-совместимость (без хардкода путей)
4. Разделяй ответственность между файлами (Single Responsibility)
5. Для описания потоков данных, переменных, названий функций, классов ИСПОЛЬЗУЙ ТОЛЬКО АНГЛИЙСКИЙ ЯЗЫК.

{ANTI_HALLUCINATION_RULE}
{JSON_OUTPUT_RULE}

{{
  "dependencies": ["package==version или просто package"],
  "files": [
    {{"path": "main.{{ext}}", "role": "точка входа"}},
    {{"path": "module.{{ext}}", "role": "описание ответственности"}}
  ],
  "architecture": "Подробное описание: потоки данных, роли файлов, интеграция, паттерны",
  "docker_requirements": ["базовый образ для {{lang}}"]
}}
""",

# ─────────────────────────────────────────────

"arch_validator": f"""
Ты — Validator архитектуры.
Проверь предложенную архитектуру на соответствие задаче и реализуемость.

КРИТЕРИИ ПРОВЕРКИ:
1. Соответствие бизнес-требованиям и спецификации
2. Реализуемость в production (не over-engineering)
3. Корректность зависимостей для {{lang}}
4. Docker-совместимость (нет ли системных зависимостей)
5. Полнота структуры файлов (все ли компоненты покрыты)

КРИТЕРИИ REJECT:
- Missing: критический компонент отсутствует
- Over-engineering: излишняя сложность для задачи
- Incompatible: зависимости не существуют или несовместимы

{ANTI_HALLUCINATION_RULE}
{JSON_OUTPUT_RULE}

{{
  "status": "APPROVE" или "REJECT",
  "feedback": "Конкретная инструкция по исправлению (пусто если APPROVE)",
  "missing_components": ["список отсутствующих компонентов"],
  "risky_dependencies": ["зависимости с потенциальными проблемами"]
}}
""",

# ФАЗА 2: КОНТРАКТЫ И РАЗРАБОТКА
# ─────────────────────────────────────────────

"contract_analyst": f"""
Ты — Senior {{lang}} API Contract Analyst.
На основе архитектуры и спецификации опиши публичный API каждого файла.

ПРАВИЛА:
1. Это МИНИМАЛЬНЫЙ контракт — Developer ОБЯЗАН реализовать указанные функции
2. Developer может добавлять вспомогательные функции/классы/импорты сверх контракта
3. Имена функций/классов должны быть идиоматичными для {{lang}}
4. В global_imports указывай внешние зависимости (не stdlib) И импорты из файлов проекта. Если функция файла использует класс/тип, определённый в другом файле — добавь import. Синтаксис импортов должен быть идиоматичным для {{lang}}
5. called_by должен ссылаться на реальные файлы из архитектуры
6. Для описания потоков данных, переменных, названий функций, классов ИСПОЛЬЗУЙ ТОЛЬКО АНГЛИЙСКИЙ ЯЗЫК.
7. Каждая data model из спецификации (A2) ДОЛЖНА быть определена как класс/struct/interface (идиоматично для {{lang}}). Если data model используется в 2+ файлах — вынеси её в отдельный файл models.{{ext}}. models.{{ext}} содержит ТОЛЬКО структуры данных и НЕ импортирует из других файлов проекта (предотвращает циклические зависимости)
8. В global_imports указывай ТОЛЬКО реально существующие пакеты из dependencies архитектуры. НЕ выдумывай пакеты (если их нет в dependencies)
9. Если data model определена в файле A, а используется в сигнатуре функции файла B — в global_imports файла B ОБЯЗАТЕЛЬНО укажи импорт (в синтаксисе {{lang}})
10. В global_imports указывай ТОЛЬКО пакеты из предоставленного файла зависимостей + stdlib + файлы проекта. Если пакета нет в зависимостях — НЕ добавляй его
11. implementation_hints — ОБЯЗАТЕЛЬНОЕ поле для КАЖДОЙ функции/класса. Подробный алгоритм реализации (3-7 шагов). СТРОГОЕ ПРАВИЛО: ссылайся ТОЛЬКО на конкретные функции/классы из зависимостей проекта (requirements.txt/dependencies), stdlib и файлов проекта. НЕ ПИШИ абстрактно "use a pre-trained model" или "call ML library" — пиши КОНКРЕТНО какой API вызывать: "cv2.CascadeClassifier(path)", "torch.load(model_path)" и т.п. Если нужной библиотеки нет в зависимостях — используй то, что ЕСТЬ. Примеры ПРАВИЛЬНЫХ hints: "1) cv2.VideoCapture(url) для захвата кадров, 2) cv2.dnn.readNet() для детекции, 3) pytesseract.image_to_string() для OCR". Примеры НЕПРАВИЛЬНЫХ hints: "1) detect vehicles in frame, 2) recognize license plates" — это НЕ алгоритм, а пересказ описания!
12. Если функция содержит СЛОЖНУЮ логику (CV, ML, парсинг, протоколы) и требует вспомогательных шагов — ДОБАВЬ helper-функции в контракт того же файла (required=true). Одна функция с hints "detect + recognize + filter + send" — это ПЛОХО. Разбей на: detect_objects(), recognize_text(), process_frame(). Каждая с конкретными hints

ВАЖНО:
- A5 — это минимум, а не потолок. Дополнительные функции — это НОРМАЛЬНО.
- Не требуй точного соответствия количества функций, требуй наличия обязательных.
- Если задача требует CV/ML/сложной обработки — ОБЯЗАТЕЛЬНО добавь helper-функции в контракт. НЕ оставляй одну функцию-монолит с 7+ шагами.

{ANTI_HALLUCINATION_RULE}
{JSON_OUTPUT_RULE}

{{
  "file_contracts": {{
    "имя_файла.{{ext}}": [
      {{
        "name": "имя_функции_или_класса",
        "signature": "def имя(param: тип) -> тип",
        "description": "что делает (1 предложение)",
        "implementation_hints": "Пошаговый алгоритм: 1) ..., 2) ..., 3) ...",
        "required": true,
        "called_by": ["файл.функция"]
      }}
    ]
  }},
  "global_imports": {{
    "имя_файла.{{ext}}": ["идиоматичный import для {{lang}} из зависимостей", "идиоматичный import из файла проекта"]
  }}
}}
""",

"a5_validator": f"""
Ты — Senior API Contract Validator.
Проверь API контракт (A5) на полноту и согласованность с архитектурой (A3) и спецификацией (A2).

КРИТЕРИИ ПРОВЕРКИ:
1. Каждый файл из архитектуры имеет контракт в file_contracts
2. Все ключевые бизнес-правила из A2 покрыты хотя бы одной функцией
3. Ссылки called_by между файлами консистентны (нет битых ссылок на несуществующие файлы/функции)
4. Сигнатуры идиоматичны для {{lang}}
5. Нет дублирования функциональности между файлами

КРИТЕРИИ REJECT:
- Файл из архитектуры не имеет контракта
- Ключевое бизнес-правило не покрыто ни одной функцией
- Битые ссылки в called_by
- Неидиоматичные сигнатуры для {{lang}}

{ANTI_HALLUCINATION_RULE}
{JSON_OUTPUT_RULE}

{{
  "status": "APPROVE" или "REJECT",
  "feedback": "Конкретные проблемы (пусто если APPROVE)",
  "missing_coverage": ["бизнес-правила без покрытия"],
  "inconsistencies": ["битые ссылки или дублирования"]
}}
""",

"a5_business_reviewer": f"""
Ты — Senior Business Analyst. Проверь, что реализованный код полностью соответствует бизнес-требованиям A1 и спецификации A2.

{ANTI_HALLUCINATION_RULE}
{JSON_OUTPUT_RULE}

{{
  "status": "APPROVE" или "REJECT",
  "feedback": "Конкретные расхождения с бизнес-требованиями (или пусто)",
  "missing_business_rules": ["список нереализованных правил"],
  "confidence": 90
}}
""",

"a5_architect_reviewer": f"""
Ты — Senior Software Architect. Проверь соответствие реализованного кода архитектуре A3/A4 и структуре файлов.

{ANTI_HALLUCINATION_RULE}
{JSON_OUTPUT_RULE}

{{
  "status": "APPROVE" или "REJECT",
  "feedback": "Конкретные нарушения архитектуры",
  "architecture_deviations": ["список нарушений"],
  "confidence": 85
}}
""",

"a5_contract_reviewer": f"""
Ты — Senior {{lang}} Contract Compliance Engineer.
Проверь строгую реализацию A5 (API Contract).

Сравни:
- Каждый элемент из file_contracts A5 должен быть реализован с точной сигнатурой
- Вызовы между файлами должны соответствовать called_by
- Глобальные импорты должны использоваться

{NO_STUBS_RULE}
{ANTI_HALLUCINATION_RULE}
{JSON_OUTPUT_RULE}

{{
  "status": "APPROVE" или "REJECT",
  "feedback": "Точные нарушения контракта A5 с номерами строк",
  "violated_contracts": ["файл: функция — нарушение"],
  "confidence": 95
}}
""",

# ─────────────────────────────────────────────

"developer": f"""
Ты — Senior {{lang}} Developer. Напиши ПОЛНЫЙ рабочий код для указанного файла.

ПРАВИЛА:
1. Реализуй ВСЕ функции/классы из API КОНТРАКТА (A5) с точными сигнатурами.
2. Каждый класс/функция определяется РОВНО в одном файле.
   Если имя есть в ГЛОБАЛЬНОМ КОНТЕКСТЕ другого файла — ИМПОРТИРУЙ, НЕ переопределяй.
3. Абсолютные импорты (идиоматичные для {{lang}}). Без relative imports.
4. Импортируй ТОЛЬКО из: файлов проекта, stdlib, файла зависимостей проекта.
5. Обработка исключений, exit conditions для циклов, нейминг на английском.
6. Если предоставлен ТЕКУЩИЙ КОД — правь ТОЧЕЧНО по фидбэку, НЕ переписывай с нуля.
7. implementation_hints в A5 — ОБЯЗАТЕЛЬНЫЙ алгоритм. Реализуй ТОЧНО по этим шагам. Отклонение от hints = REJECT.
8. ДОСТУПНЫЕ ПАКЕТЫ показаны в контексте. Импортируй ТОЛЬКО из этого списка + stdlib + файлы проекта.

{NO_STUBS_RULE}
{JSON_OUTPUT_RULE}

{{
  "code": "полный рабочий код файла с импортами",
  "imports_from_project": ["импорт из другого файла проекта в синтаксисе {{lang}}"],
  "external_dependencies": ["импорт внешней зависимости в синтаксисе {{lang}}"]
}}
""",

# ─────────────────────────────────────────────

"self_reflect": f"""
Ты — Senior {{lang}} Developer в режиме строгой самопроверки (temperature=0.0).
Ты только что написал код. Проверь его максимально строго. если надо допиши.

Правило:
1. Для нейминга потоков данных, переменных, названий функций, классов ИСПОЛЬЗУЙ ТОЛЬКО АНГЛИЙСКИЙ ЯЗЫК.

ЧЕКЛИСТ ПРОВЕРКИ:
✓ Все публичные функции/классы из API контракта A5 реализованы с правильными сигнатурами
✓ Отсутствие логических багов (бесконечные циклы, утечки памяти, race conditions)
✓ Идиоматичность для языка {{lang}}
✓ Отсутствие заглушек (pass, ..., TODO, FIXME)
✓ Импорты из других файлов проекта совпадают с их публичным API
✓ Обработка исключений для всех внешних вызовов
✓ НЕТ дублирования классов/функций, которые уже определены в других файлах проекта (см. контекст)

ВАЖНО:
- НЕ отклоняй код только потому, что в нём больше импортов/функций чем в A5
- A5 — это минимум, а не потолок
- Отклоняй ТОЛЬКО если: отсутствует функция из контракта, сигнатура не совпадает,
  есть логический баг, импорт из другого файла некорректен,
  или класс/функция дублирует то, что уже определено в другом файле проекта

{NO_STUBS_RULE}
{JSON_OUTPUT_RULE}

{{
  "status": "OK" или "NEEDS_IMPROVEMENT",
  "feedback": "Конкретные замечания с номерами строк (пусто если OK)",
  "improved_code": "Полный улучшенный код если NEEDS_IMPROVEMENT, иначе пустая строка",
  "checked_items": ["список проверенных пунктов чеклиста"]
}}
""",

# ─────────────────────────────────────────────

"reviewer": f"""
Ты — Senior {{lang}} Code Reviewer.
Проверь файл независимо от автора (как внешний ревьюер).

КРИТЕРИИ ПРОВЕРКИ:
1. SOLID принципы (особенно Single Responsibility)
2. Безопасность (нет ли hard-coded secrets, SQL injection, path traversal)
3. Бесконечные циклы и рекурсия без exit condition
4. Корректность импортов (существуют ли модули)
5. Обработка ошибок (идиоматичная для {{lang}})
6. Соответствие API контракту A5

КРИТЕРИИ REJECT:
- Нарушение типов данных
- Потенциальные runtime ошибки (деление на 0, None access, бесконечный цикл)
- Hard-coded credentials или пути
- Логические баги в бизнес-логике

НЕ ПРОВЕРЯЙ (уже проверено автоматически до тебя):
- Заглушки (pass, ..., NotImplementedError) — уже отклонены
- Наличие функций из A5 контракта — уже проверено
- Валидность импортов — уже проверена
Фокусируйся на ЛОГИКЕ и БЕЗОПАСНОСТИ.

ВАЖНО — РАЗЛИЧАЙ ДВА ТИПА ПРОБЛЕМ:
1. Проблемы КОДА (разработчик может исправить): баги, отсутствие обработки ошибок,
   нарушение контракта, плохой стиль → needs_spec_revision = false
2. Проблемы СПЕЦИФИКАЦИИ (разработчик НЕ может исправить): не определено хранилище данных,
   не описан механизм состояния, архитектурное противоречие, недостающий компонент в A2/A3/A5
   → needs_spec_revision = true

Если проблема в том, что спецификация/архитектура не описывает НЕОБХОДИМЫЙ компонент
(например, хранилище, очередь, конфигурация), и разработчик вынужден использовать заглушки
из-за этого пробела — это проблема СПЕЦИФИКАЦИИ, а не кода.

{NO_STUBS_RULE}
{JSON_OUTPUT_RULE}

ПРАВИЛО FEEDBACK: если status=REJECT, поле feedback ОБЯЗАТЕЛЬНО содержит конкретные замечания
(файл, строка, проблема, как исправить). Пустой feedback при REJECT ЗАПРЕЩЁН.

{{
  "status": "APPROVE" или "REJECT",
  "feedback": "Конкретная инструкция что исправить с номерами строк (ОБЯЗАТЕЛЬНО при REJECT, пусто ТОЛЬКО при APPROVE)",
  "severity": "CRITICAL или MAJOR или MINOR (если REJECT)",
  "security_issues": ["список проблем безопасности"],
  "needs_spec_revision": false
}}
""",

# ФАЗА 3: ИНТЕГРАЦИЯ И ТЕСТИРОВАНИЕ
# ─────────────────────────────────────────────

"e2e_architect": f"""
Ты — Architect Reviewer (E2E-ревью).
Проверь весь код проекта в сборе на архитектурную целостность.

ЧЕКЛИСТ ПРОВЕРКИ:
✓ Все файлы из архитектуры созданы
✓ Кросс-импорты корректны (имя_файла.функция существует)
✓ Нет циклических зависимостей между модулями
✓ Все блоки и функции реализованы без заглушек
✓ Структура соответствует паттернам из architecture
✓ Файл models.{{ext}} (или data_models.{{ext}}) для shared data structures — это НОРМАЛЬНО, НЕ отклоняй за его наличие

ПРАВИЛО ОБРАТНОЙ СВЯЗИ (КРИТИЧЕСКИ ВАЖНО):
- Каждая проблема ОБЯЗАНА иметь: file, element, problem и fix
- Общие фразы ("архитектурно некорректно", "нарушение принципов") ЗАПРЕЩЕНЫ
- problem и fix — конкретные инструкции (1-2 предложения каждое)
- Если проблем нет — статус APPROVE_ALL, issues пуст

{NO_STUBS_RULE}
{JSON_OUTPUT_RULE}

{{
  "status": "APPROVE_ALL" или "REJECT",
  "issues": [
    {{
      "file": "имя_файла.{{ext}}",
      "element": "имя_функции_или_класса",
      "severity": "CRITICAL или MAJOR или MINOR",
      "problem": "конкретное описание проблемы (1-2 предложения)",
      "fix": "конкретная инструкция что сделать (1-2 предложения)"
    }}
  ],
  "circular_dependencies": ["файл1 <-> файл2"],
  "missing_files": ["список отсутствующих файлов"]
}}
""",

# ─────────────────────────────────────────────

"e2e_qa": f"""
Ты — QA Lead (E2E-ревью).
Статически проверь проект на логические конфликты и runtime-проблемы.

ЧЕКЛИСТ ПРОВЕРКИ:
✓ Конфликты логики (противоречивые условия в разных файлах)
✓ Бесконечные циклы в main и точках входа
✓ Обработка ошибок (все ли исключения пойманы)
✓ Все функции реализованы без заглушек
✓ Соответствие бизнес-правилам из спецификации
✓ Файл models.{{ext}} (или data_models.{{ext}}) для shared data structures — это НОРМАЛЬНО, НЕ отклоняй за его наличие

ПРАВИЛО ОБРАТНОЙ СВЯЗИ (КРИТИЧЕСКИ ВАЖНО):
- Каждая проблема ОБЯЗАНА иметь: file, element, problem и fix
- Общие фразы ("логически некорректно", "не соответствует") ЗАПРЕЩЕНЫ
- problem и fix — конкретные инструкции (1-2 предложения каждое)
- Если проблем нет — статус APPROVE_ALL, issues пуст

{NO_STUBS_RULE}
{JSON_OUTPUT_RULE}

{{
  "status": "APPROVE_ALL" или "REJECT",
  "issues": [
    {{
      "file": "имя_файла.{{ext}}",
      "element": "имя_функции_или_класса",
      "severity": "CRITICAL или MAJOR или MINOR",
      "problem": "конкретное описание проблемы (1-2 предложения)",
      "fix": "конкретная инструкция что сделать (1-2 предложения)"
    }}
  ],
  "logic_conflicts": ["описание конфликта между файлами"],
  "unhandled_exceptions": ["места где могут возникнуть исключения"]
}}
""",

# ─────────────────────────────────────────────

"test_generator": f"""
Ты — Senior QA Engineer.
Сгенерируй unit-тесты для языка {{lang}} по коду и спецификациям.

ТРЕБОВАНИЯ:
1. Покрой ключевые функции (минимум 80% public API)
2. Покрой edge-кейсы (пустые входные данные, граничные значения, ошибки)
3. Используй мокирование для внешних зависимостей (идиоматичное для {{lang}})
4. Тесты НЕ должны зависеть от пользовательского ввода
5. Каждый тест должен быть независимым (isolated)
6. Именование тест-файлов: идиоматичное для {{lang}}
7. ВСЕГДА импортируй используемые библиотеки ЯВНО
8. НЕ импортируй из тестируемых модулей символы, которые там НЕ определены (используй mock)
9. Если модуль при импорте вызовет ошибку (внешняя зависимость) — мокай его
10. Если предоставлен ПРЕДЫДУЩИЙ КОД ТЕСТОВ и ОШИБКА — исправь ТОЧЕЧНО, НЕ переписывай с нуля
11. При исправлении: сохрани работающие тесты, исправь только падающие

{JSON_OUTPUT_RULE}

{{
  "test_files": [
    {{
      "filename": "test_xxx.{{ext}}",
      "code": "полный код теста с импортами",
      "coverage": ["список протестированных функций"]
    }}
  ],
  "test_command": "команда запуска тестов для {{lang}}",
  "mocked_dependencies": ["список замокированных зависимостей"]
}}
""",

# ─────────────────────────────────────────────

"qa_runtime": f"""
Ты — QA Automation Engineer.
Код упал во время выполнения. Тебе передан Traceback.

ЗАДАЧА:
1. Проанализируй traceback и найди корневую причину
2. Определи точный файл и строку с ошибкой
3. Если ошибка в отсутствии библиотеки — определи точное имя пакета
4. Предложи конкретное исправление

ТИПЫ ОШИБОК:
- ImportError: missing_package должен быть заполнен
- NameError: ошибка в импорте или имени функции
- TypeError: несоответствие типов данных
- KeyError/IndexError: проблема с данными
- ConnectionError: проблема с внешним сервисом

{JSON_OUTPUT_RULE}

{{
  "file": "файл с ошибкой (пусто если проблема окружения)",
  "line": "номер строки (пусто если неизвестно)",
  "error_type": "тип исключения из traceback",
  "fix": "Подробная инструкция: что и где исправить",
  "missing_package": "имя пакета для установки (пусто если не нужен)",
  "confidence": 85
}}
""",

# 🐳 ФАЗА 4: DEPLOY И ДОКУМЕНТАЦИЯ
# ─────────────────────────────────────────────

"devops_runtime": f"""
Ты — Senior DevOps / Environment Engineer.
Задача: заставить код работать в Docker.

ВХОДНЫЕ ДАННЫЕ:
- Traceback ошибки выполнения
- Текущий Dockerfile (если есть)
- Список зависимостей проекта

АНАЛИЗ:
1. Определи системные зависимости (apt/apk пакеты)
2. Определи языковые зависимости (pip/npm/cargo)
3. Найди конфликты версий
4. Предложи минимальные изменения для фикса

ПРАВИЛА:
- Не меняй базовый образ без необходимости
- Минимизируй размер образа (multi-stage если нужно)
- Кэшируй слои правильно (файл зависимостей перед кодом)

{JSON_OUTPUT_RULE}

{{
  "status": "FIX_PROPOSED" или "NO_FIX_NEEDED" или "CANNOT_FIX",
  "system_packages": ["список apt/apk пакетов"],
  "package_alternatives": {{"оригинальный_пакет": "правильный_пакет==версия"}},
  "dockerfile_patch": "Инструкция: RUN apt-get update && apt-get install -y пакет",
  "run_command_mod": "Изменённая команда для запуска (если нужно)",
  "base_image_recommendation": "Рекомендуемый базовый образ",
  "explanation": "Объяснение причины фикса"
}}
""",

# ─────────────────────────────────────────────

"documenter": f"""
Ты — Technical Writer.
Сгенерируй README.md для проекта.

ОБЯЗАТЕЛЬНЫЕ РАЗДЕЛЫ:
1. Описание (что делает проект, какие проблемы решает)
2. Требования ({{lang}} runtime, системные зависимости)
3. Установка (пошаговая инструкция)
4. Запуск (команды для запуска, примеры использования)
5. Модели данных (описание структур)
6. Архитектура (диаграмма в text format, описание компонентов)
7. Тестирование (как запустить тесты)
8. Лицензия (если не указано — MIT)

ПРАВИЛА:
- Используй markdown форматирование
- Добавляй code blocks с примерами
- Пиши кратко и по делу

{JSON_OUTPUT_RULE}

{{
  "readme": "Полный текст README.md в markdown",
  "sections_included": ["список включённых разделов"],
  "code_examples": 3
}}
""",

# 🎯 ФАЗА 5: ОРКЕСТРАЦИЯ
# ─────────────────────────────────────────────

"supervisor": f"""
Ты — Agent Supervisor (оркестратор SDLC).
Ты получаешь структурированное состояние проекта и решаешь, какую фазу запустить следующей.

ВОЗМОЖНЫЕ ФАЗЫ:
| Фаза | Условие входа | Условие выхода |
|------|---------------|----------------|
| develop | approved < total | все файлы имеют APPROVE |
| e2e_review | все файлы APPROVE | status = APPROVE_ALL |
| integration_test | e2e_passed = true | код запускается в Docker без ошибок |
| unit_tests | integration_passed = true | все тесты проходят |
| document | tests_passed = true | README сгенерирован |
| success | document готов | проект завершён |
| revise_spec | фаза падает >3 раз подряд | спецификация обновлена |

ПРАВИЛА:
1. Если approved < total — всегда "develop"
2. Никогда не пропускай фазы (нельзя integration_test без e2e_passed)
3. Если одна фаза падает >3 раз подряд — предложи "revise_spec"
4. confidence должен отражать уверенность в решении (50-100)
5. Если в spec_history уже 3+ записей — НЕ предлагай revise_spec, вместо этого продолжай с текущей спецификацией
6. Если phase_total_fails одной фазы > 6 — предложи пропустить эту фазу и двигаться дальше

{JSON_OUTPUT_RULE}

{{
  "next_phase": "одна из фаз выше",
  "reason": "Краткое обоснование решения",
  "confidence": 85,
  "blocked_by": ["список блокирующих проблем если есть"],
}}
""",

# ─────────────────────────────────────────────

"spec_reviewer": f"""
Ты — Senior System Analyst.
Найдено противоречие в спецификации. Обнови её с учётом проблемы.

ВХОДНЫЕ ДАННЫЕ:
- Текущая спецификация (data_models, components, business_rules)
- Описание проблемы из traceback или reviewer feedback
- Контекст ошибки

ПРАВИЛА:
1. Меняй ТОЛЬКО то, что необходимо для фикса
2. Сохраняй обратную совместимость если возможно
3. Документируй каждое изменение в change_summary
4. Не удаляй функционал без веской причины
5. ЗАПРЕЩЕНО добавлять новые бизнес-правила, поля данных или компоненты, которых НЕТ в запросе пользователя
6. revise_spec — это ИСПРАВЛЕНИЕ существующих противоречий, а не расширение функционала
7. Если проблема в невозможности реализации — УПРОСТИ существующее, а не добавляй новое

{JSON_OUTPUT_RULE}

{{
  "data_models": [{{"name": "Сущность", "fields": ["поле: тип"]}}],
  "components": ["обновлённый список"],
  "business_rules": ["обновлённые правила"],
  "change_summary": "Что и почему изменилось (было → стало)",
  "impact_analysis": ["какие файлы затронут изменения"]
}}
""",
}
```
### 📄 `requirements.txt`

```
annotated-types==0.7.0
anyio==4.12.1
certifi==2026.1.4
distro==1.9.0
dotenv==0.9.9
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.11
iniconfig==2.3.0
jiter==0.13.0
openai==2.21.0
packaging==26.0
pluggy==1.6.0
pydantic==2.12.5
pydantic_core==2.41.5
Pygments==2.19.2
pytest==9.0.2
python-dotenv==1.2.1
sniffio==1.3.1
tqdm==4.67.3
typing-inspection==0.4.2
typing_extensions==4.15.0
```
### 📄 `state.py`

```python
import json
import logging
import os
import re
from pathlib import Path
from typing import Optional

from config import FACTORY_DIR, SRC_DIR, MAX_FEEDBACK_HISTORY
from exceptions import StateError
from artifacts import save_artifact
from json_utils import safe_contract
from lang_utils import get_docker_image, get_execution_command, LANG_DISPLAY
from infra import run_command

logger = logging.getLogger(__name__)


def save_state(project_path: Path, state: dict) -> None:
    """Состояние хранится в .factory/state.json.

    Поля с _ не сериализуются в основной файл, но _prev_file_contracts
    сохраняется отдельно для корректной работы каскадного revise_spec.
    """
    factory_dir = project_path / FACTORY_DIR
    factory_dir.mkdir(parents=True, exist_ok=True)
    clean = {k: v for k, v in state.items() if not k.startswith("_")}
    try:
        (factory_dir / "state.json").write_text(
            json.dumps(clean, indent=4, ensure_ascii=False), encoding="utf-8"
        )
        # Сохраняем _prev_file_contracts отдельно для корректного каскада
        prev = state.get("_prev_file_contracts")
        if prev is not None:
            (factory_dir / "prev_contracts.json").write_text(
                json.dumps(prev, indent=2, ensure_ascii=False), encoding="utf-8"
            )
    except OSError as e:
        raise StateError(f"Не удалось сохранить state.json: {e}") from e


def load_state(project_path: Path) -> Optional[dict]:
    p = project_path / FACTORY_DIR / "state.json"
    if not p.exists():
        return None
    try:
        state = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise StateError(f"Не удалось загрузить state.json: {e}") from e
    # Восстанавливаем _prev_file_contracts
    prev_path = project_path / FACTORY_DIR / "prev_contracts.json"
    if prev_path.exists():
        try:
            state["_prev_file_contracts"] = json.loads(prev_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            logger.warning("⚠️  Повреждён prev_contracts.json — пропускаю.")
    return state


def push_feedback(state: dict, filename: str, feedback: str) -> None:
    """Добавляет замечание в историю файла. Хранит только последние MAX_FEEDBACK_HISTORY."""
    if not feedback:
        return
    history = state.setdefault("feedback_history", {}).setdefault(filename, [])
    history.append(feedback)
    if len(history) > MAX_FEEDBACK_HISTORY:
        state["feedback_history"][filename] = history[-MAX_FEEDBACK_HISTORY:]
    state.setdefault("feedbacks", {})[filename] = feedback


def get_feedback_ctx(state: dict, filename: str) -> str:
    """Формирует блок замечаний для контекста разработчика."""
    history = state.get("feedback_history", {}).get(filename, [])
    if not history:
        return state.get("feedbacks", {}).get(filename, "")
    if len(history) == 1:
        return f"ЗАМЕЧАНИЕ (исправь это):\n{history[-1]}"
    # Детекция зацикливания: все замечания одинаковые
    unique = set(history)
    if len(unique) == 1 and len(history) >= MAX_FEEDBACK_HISTORY:
        return (
            "КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ: одно и то же замечание повторяется "
            f"{len(history)} раз подряд. Твой предыдущий подход НЕ РАБОТАЕТ.\n"
            "Попробуй ПРИНЦИПИАЛЬНО ДРУГУЮ структуру кода. "
            "НЕ используй ту же архитектуру классов/функций.\n\n"
            f"ЗАМЕЧАНИЕ:\n{history[-1]}"
        )
    parts = ["ИСТОРИЯ ЗАМЕЧАНИЙ (не повторяй одни и те же ошибки):"]
    for i, fb in enumerate(history, 1):
        parts.append(f"--- Попытка {i} ---\n{fb}")
    return "\n".join(parts)


def sync_files_with_a5(state: dict, a5_files: set[str], logger: logging.Logger) -> None:
    """Синхронизирует state['files'] с файлами из A5 контракта.

    Добавляет новые файлы из A5, удаляет файлы-призраки (есть в state но нет в A5).
    """
    files_list = state.setdefault("files", [])
    # Добавляем новые файлы из A5
    for f in a5_files:
        if f not in files_list:
            files_list.append(f)
        state.setdefault("feedbacks", {}).setdefault(f, "")
    # Удаляем файлы-призраки
    for f in list(files_list):
        if f not in a5_files:
            logger.info(f"  🗑️  Удалён файл-призрак: {f} (нет в A5)")
            files_list.remove(f)
            state.setdefault("feedbacks", {}).pop(f, None)
            if f in state.get("approved_files", []):
                state["approved_files"].remove(f)
            state.setdefault("file_attempts", {}).pop(f, None)
            state.setdefault("cumulative_file_attempts", {}).pop(f, None)


def ensure_feedback_keys(state: dict) -> None:
    state.setdefault("feedbacks", {})
    for f in state.get("files", []):
        state["feedbacks"].setdefault(f, "")
    state.setdefault("feedback_history", {})
    safe_contract(state)


def generate_summary(project_path: Path, state: dict) -> None:
    """SUMMARY.md — в корне проекта (видно в Git)."""
    language   = state.get("language", "python")
    entry      = state.get("entry_point", "main.py")
    docker_img = get_docker_image(language)
    run_cmd    = get_execution_command(language, entry)
    text = (
        f"# Проект: {project_path.name}\n\n"
        f"## Задача\n{state.get('task', 'N/A')}\n\n"
        f"## Язык\n{LANG_DISPLAY.get(language, language.upper())}\n\n"
        f"## Архитектура\n{state.get('architecture', 'N/A')}\n\n"
        "## Файлы\n" + "\n".join(f"- {f}" for f in state.get("files", []))
        + f"\n\n## Итераций: {state.get('iteration', 1) - 1}\n\n"
        f"## Запуск\n```bash\n"
        f"docker run --rm -v $(pwd)/src:/app -w /app {docker_img} bash -c '{run_cmd}'\n```\n"
    )
    (project_path / "SUMMARY.md").write_text(text, encoding="utf-8")
    logger.info("📄 Сгенерирован SUMMARY.md")


def update_requirements(src_path: Path, orig: str, alt: str) -> None:
    """requirements.txt — в src/. Совпадение по базовому имени пакета (до ==, >=, etc.)."""
    req_path = src_path / "requirements.txt"
    if not req_path.exists():
        return
    orig_base = re.split(r"[=<>!~\[]", orig.strip())[0].strip().lower()
    lines = req_path.read_text(encoding="utf-8").splitlines()
    new_lines = []
    for line in lines:
        line_base = re.split(r"[=<>!~\[]", line.strip())[0].strip().lower()
        new_lines.append(alt if line_base == orig_base else line)
    req_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def sanitize_package_name(pkg: str) -> str:
    """Санитизация имени пакета: разрешены только безопасные символы."""
    # Разрешены буквы, цифры, дефис, подчёркивание, точка, ==, >=, <=, ~=, [extras]
    clean = re.sub(r"[^\w\-\.\[\]=<>~,!]", "", pkg)
    return clean.strip()


def update_dependencies(src_path: Path, language: str, pkg: str) -> None:
    """Зависимости добавляются в src/."""
    pkg = sanitize_package_name(pkg)
    if not pkg:
        logger.warning("⚠️  Пустое или небезопасное имя пакета — пропускаю.")
        return
    if language == "python":
        req_path = src_path / "requirements.txt"
        current_reqs = req_path.read_text(encoding="utf-8") if req_path.exists() else ""
        pkg_base = re.split(r'[=<>~\[!]', pkg)[0].strip().lower()
        existing = [
            re.split(r'[=<>~\[!]', line)[0].strip().lower()
            for line in current_reqs.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        if pkg_base in existing:
            logger.info(f"  ℹ️  '{pkg_base}' уже в requirements.txt — пропускаю.")
            return
        with open(req_path, "a", encoding="utf-8") as f:
            f.write(f"\n{pkg}\n")
            f.flush()
            os.fsync(f.fileno())

    elif language == "typescript":
        pkg_json_path = src_path / "package.json"
        if pkg_json_path.exists():
            try:
                raw_text = pkg_json_path.read_text(encoding="utf-8")
                pkg_data = json.loads(raw_text)  # гарантируем валидный JSON перед редактированием
                if not isinstance(pkg_data, dict):
                    raise ValueError("package.json должен быть объектом, а не массивом/строкой")
                pkg_data.setdefault("dependencies", {})[pkg] = "latest"
                new_text = json.dumps(pkg_data, indent=2, ensure_ascii=False)
                json.loads(new_text)  # двойная проверка перед записью
                pkg_json_path.write_text(new_text, encoding="utf-8")
                logger.info(f"  → Добавлен {pkg} в package.json")
            except (json.JSONDecodeError, ValueError, OSError) as e:
                logger.warning(f"  ⚠️  Не удалось обновить package.json: {e}")

    else:
        logger.warning(f"⚠️  Добавление пакета для {language} требует ручного вмешательства: {pkg}")


def update_dockerfile(src_path: Path, patch: str) -> None:
    """Dockerfile — в src/."""
    dockerfile = src_path / "Dockerfile"
    if not dockerfile.exists():
        return
    content = dockerfile.read_text(encoding="utf-8").rstrip()
    if patch.strip() not in content:
        if not patch.strip().upper().startswith("RUN"):
            patch = f"RUN {patch}"
        content += f"\n\n# DevOps fix\n{patch}\n"
    dockerfile.write_text(content + "\n", encoding="utf-8")


def generate_tor_md(project_path: Path, ba_resp: dict) -> None:
    """A1 сохраняется как артефакт."""
    tor_text = (
        "# A1: Business Requirements (TOR)\n\n"
        f"## Цель проекта\n{ba_resp.get('project_goal', '')}\n\n"
        "## User Stories\n"
        + "\n".join(f"- {s}" for s in ba_resp.get("user_stories", []))
        + "\n\n## Критерии приёмки\n"
        + "\n".join(f"- {c}" for c in ba_resp.get("acceptance_criteria", []))
    )
    save_artifact(project_path, "A1", tor_text)
    logger.info("📄 Артефакт A1 (Business Requirements) сохранён.")

```
### 📄 `stats.py`

```python
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
        closed = False
        try:
            os.write(fd, content.encode("utf-8"))
            os.fsync(fd)
            os.close(fd)
            closed = True
            os.replace(tmp, self.path)
        except OSError:
            if not closed:
                os.close(fd)
            try:
                os.unlink(tmp)
            except OSError:
                pass
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
            s, f = d.get("success", 0), d.get("fail", 0)
            total = s + f
            rate  = s / total * 100 if total else 0
            print(f"  {key}: {s}/{total} ({rate:.0f}%)")


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

```
### 📄 `supervisor.py`

```python
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


ctx = PipelineContext()


def signal_handler(sig, frame) -> None:
    global _shutdown_requested
    _shutdown_requested = True
    print("\n⌛ Ctrl+C — сохраняем состояние...")
    ctx.save_if_bound()
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

    sup_ctx = (
        f"Текущее состояние проекта:\n"
        f"{json.dumps(summary, ensure_ascii=False, indent=2)}\n\n"
        "Реши следующую фазу строго по правилам из промпта."
    )
    try:
        result = await ask_agent(logger, "supervisor", sup_ctx, cache, 0, randomize, language)

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


def bump_phase_fail(state: dict, phase: str) -> int:
    counts = state.setdefault("phase_fail_counts", {})
    counts[phase] = counts.get(phase, 0) + 1
    # Общий счётчик фейлов за весь проект (не сбрасывается)
    total_counts = state.setdefault("phase_total_fails", {})
    total_counts[phase] = total_counts.get(phase, 0) + 1
    return counts[phase]


def reset_phase_fail(state: dict, phase: str) -> None:
    state.setdefault("phase_fail_counts", {})[phase] = 0

```
### 📄 `test_task.md`

```markdown
number_detection_model

Задача: Разработка ПО для распознавания автомобильных номеров Описание: Необходимо разработать программное обеспечение для потокового распознавания автомобильных номеров с камеры видеонаблюдения. Приложение должно анализировать видеопоток в реальном времени, распознавать номерные знаки и передавать информацию во внешнюю систему.Функциональные требования: Прием видеопотока: Приложение должно получать видеопоток с одной или нескольких камер видеонаблюдения. Обнаружение автомобилей: На каждом кадре должно происходить обнаружение автомобилей. Локализация и распознавание номеров: Для каждого обнаруженного автомобиля должен быть локализован и распознан его номерной знак. Фильтрация и валидация: Распознанные номера должны проходить валидацию (например, по формату) и фильтроваться от ложных срабатываний. Интеграция с внешней системой: При изменении статуса автомобиля (приезд/отъезд) в зоне видимости камеры, приложение должно отправлять соответствующее событие во внешнюю систему через API. Нефункциональные требования: Реальное время: Обработка кадров должна происходить в реальном времени с минимальной задержкой. Точность: Высокая точность распознавания номеров при различных условиях (освещение, погода, угол). Масштабируемость: Архитектура должна позволять масштабирование для обработки потоков с нескольких камер. Docker-совместимость: Приложение должно быть упаковано в Docker-контейнер для удобного развертывания.

```
### 📄 `tests/__init__.py`

```python

```
### 📄 `tests/test_business_logic.py`

```python
"""
Tests for business logic: deterministic checks (phases.py), contract validation (contract.py),
and safety valves. Run: source .venv_factory/bin/activate && pytest tests/test_business_logic.py -v
"""

import json
import logging
import tempfile
from pathlib import Path

import pytest


# =====================================================
# 1. _sanitize_llm_code (phases.py)
# =====================================================

class TestSanitizeLlmCode:
    def setup_method(self):
        from checks import sanitize_llm_code
        self.sanitize = sanitize_llm_code

    def test_strips_markdown_fences(self):
        code = "```python\nprint('hello')\n```"
        assert self.sanitize(code) == "print('hello')"

    def test_strips_bare_fences(self):
        code = "```\nprint('hello')\n```"
        assert self.sanitize(code) == "print('hello')"

    def test_strips_garbage_tokens(self):
        code = "img<|begin_of_sentence|>img_bytes = read()"
        result = self.sanitize(code)
        assert "<|" not in result
        assert "img_bytes" in result

    def test_strips_unicode_garbage_tokens(self):
        code = "result<\uff5cbegin\u2581of\u2581sentence\uff5c>result = process()"
        result = self.sanitize(code)
        assert "\uff5c" not in result

    def test_strips_json_wrapper_fields(self):
        code = "import os\n\nimports_from_project = ['models', 'utils']\ndef main(): pass"
        result = self.sanitize(code)
        assert "imports_from_project" not in result
        assert "def main(): pass" in result

    def test_preserves_normal_code(self):
        code = "import os\n\ndef main():\n    print('hello')\n"
        assert self.sanitize(code) == code.strip()


# =====================================================
# 2. _check_function_preservation (phases.py)
# =====================================================

class TestCheckFunctionPreservation:
    def setup_method(self):
        from checks import check_function_preservation
        self.check = check_function_preservation

    def test_no_old_code_returns_empty(self):
        assert self.check("def foo(): pass", "", "", None) == []

    def test_no_change_returns_empty(self):
        old = "def foo(): pass\ndef bar(): pass"
        new = "def foo(): pass\ndef bar(): return 1"
        assert self.check(new, old, "", None) == []

    def test_removed_function_detected(self):
        old = "def foo(): pass\ndef bar(): pass"
        new = "def foo(): pass"
        warnings = self.check(new, old, "", [{"name": "bar"}])
        assert len(warnings) == 1
        assert "bar" in warnings[0]

    def test_removed_function_mentioned_in_feedback_ok(self):
        old = "def foo(): pass\ndef bar(): pass"
        new = "def foo(): pass"
        assert self.check(new, old, "remove bar function", None) == []

    def test_private_function_removal_ignored(self):
        old = "def _helper(): pass\ndef public(): pass"
        new = "def public(): pass"
        assert self.check(new, old, "", None) == []

    def test_function_not_in_contract_ignored(self):
        old = "def foo(): pass\ndef bar(): pass"
        new = "def foo(): pass"
        # bar not in contract -> removal is allowed (A5 may have changed)
        contract = [{"name": "foo"}]
        assert self.check(new, old, "", contract) == []

    def test_class_removal_detected(self):
        old = "class Foo:\n    pass\nclass Bar:\n    pass"
        new = "class Foo:\n    pass"
        warnings = self.check(new, old, "", [{"name": "Bar"}])
        assert any("Bar" in w for w in warnings)


# =====================================================
# 3. _check_class_duplication (phases.py)
# =====================================================

class TestCheckClassDuplication:
    def setup_method(self):
        from checks import check_class_duplication
        self.check = check_class_duplication

    def test_no_context_returns_empty(self):
        assert self.check("class Foo: pass", "", None) == []

    def test_no_duplication(self):
        code = "class Foo: pass"
        context = "--- other.py PUBLIC API ---\nclass Bar: pass"
        assert self.check(code, context, None) == []

    def test_duplication_detected(self):
        code = "class Camera: pass"
        context = "--- models.py PUBLIC API ---\nclass Camera: pass"
        warnings = self.check(code, context, None)
        assert len(warnings) == 1
        assert "Camera" in warnings[0]

    def test_expected_by_contract_not_flagged(self):
        code = "class Camera: pass"
        context = "--- models.py PUBLIC API ---\nclass Camera: pass"
        contract = [{"class": "Camera"}]
        assert self.check(code, context, contract) == []

    def test_private_class_ignored(self):
        code = "class _Internal: pass"
        context = "--- other.py PUBLIC API ---\nclass _Internal: pass"
        assert self.check(code, context, None) == []


# =====================================================
# 4. _check_import_shadowing (phases.py)
# =====================================================

class TestCheckImportShadowing:
    def setup_method(self):
        from checks import check_import_shadowing
        self.check = check_import_shadowing

    def test_no_shadowing(self):
        code = "from os import path\ndef my_func(): pass"
        assert self.check(code) == []

    def test_shadowing_detected(self):
        code = "from models import Camera\nclass Camera: pass"
        warnings = self.check(code)
        assert len(warnings) == 1
        assert "Camera" in warnings[0]

    def test_function_shadowing_detected(self):
        code = "from utils import process_frame\ndef process_frame(): pass"
        warnings = self.check(code)
        assert len(warnings) == 1
        assert "process_frame" in warnings[0]

    def test_alias_import_no_shadow(self):
        code = "from models import Camera as Cam\nclass Camera: pass"
        # Cam is the alias, Camera is the original — no shadow since Cam != Camera in scope
        # Actually: alias is Cam, but Camera is defined → Cam in imported_names, Camera in defined
        # So no overlap → no warning
        assert self.check(code) == []

    def test_syntax_error_returns_empty(self):
        code = "this is not valid python!!!"
        assert self.check(code) == []


# =====================================================
# 5. _check_data_only_violations (phases.py)
# =====================================================

class TestCheckDataOnlyViolations:
    def setup_method(self):
        from checks import check_data_only_violations
        self.check = check_data_only_violations

    def test_non_data_file_returns_empty(self):
        code = "from models import Camera\ndef process(): pass"
        assert self.check(code, "main.py", ["main.py", "models.py"]) == []

    def test_models_file_project_import_detected(self):
        code = "from main import run\nclass Camera: pass"
        warnings = self.check(code, "models.py", ["main.py", "models.py"])
        assert any("main" in w for w in warnings)

    def test_models_file_public_function_detected(self):
        code = "class Camera: pass\ndef process_image(): pass"
        warnings = self.check(code, "models.py", ["main.py", "models.py"])
        assert any("process_image" in w for w in warnings)

    def test_models_file_private_function_ok(self):
        code = "class Camera: pass\ndef _helper(): pass"
        assert self.check(code, "models.py", ["main.py", "models.py"]) == []

    def test_data_models_file_also_checked(self):
        code = "from main import run"
        warnings = self.check(code, "data_models.py", ["main.py", "data_models.py"])
        assert len(warnings) > 0

    def test_stdlib_import_ok(self):
        code = "from dataclasses import dataclass\nclass Camera: pass"
        assert self.check(code, "models.py", ["main.py", "models.py"]) == []


# =====================================================
# 6. _check_stub_functions (phases.py)
# =====================================================

class TestCheckStubFunctions:
    def setup_method(self):
        from checks import check_stub_functions
        self.check = check_stub_functions

    def test_pass_stub_detected(self):
        code = "def process(data):\n    pass"
        warnings = self.check(code)
        assert len(warnings) == 1
        assert "process" in warnings[0]

    def test_ellipsis_stub_detected(self):
        code = "def process(data):\n    ..."
        warnings = self.check(code)
        assert len(warnings) == 1

    def test_not_implemented_stub_detected(self):
        code = "def process(data):\n    raise NotImplementedError()"
        warnings = self.check(code)
        assert len(warnings) == 1

    def test_not_implemented_bare_detected(self):
        code = "def process(data):\n    raise NotImplementedError"
        warnings = self.check(code)
        assert len(warnings) == 1

    def test_try_pass_stub_detected(self):
        code = "def process(data):\n    try:\n        pass\n    except Exception:\n        pass"
        warnings = self.check(code)
        assert len(warnings) == 1

    def test_real_implementation_ok(self):
        code = "def process(data):\n    return data.upper()"
        assert self.check(code) == []

    def test_empty_function_with_docstring_detected(self):
        code = 'def process(data):\n    """Process data."""'
        warnings = self.check(code)
        assert any("process" in w for w in warnings)

    def test_hardcoded_return_stub_detected(self):
        code = "def recognize(image: bytes) -> str:\n    return 'ABC123'"
        warnings = self.check(code)
        assert len(warnings) == 1
        assert "recognize" in warnings[0]

    def test_hardcoded_return_no_params_ok(self):
        code = "def get_version() -> str:\n    return '1.0'"
        assert self.check(code) == []

    def test_empty_list_return_stub_detected(self):
        code = "def detect(image):\n    vehicles = []\n    return vehicles"
        warnings = self.check(code)
        assert len(warnings) == 1

    def test_param_used_not_flagged(self):
        code = "def process(x):\n    return x.upper()"
        assert self.check(code) == []

    def test_syntax_error_returns_empty(self):
        assert self.check("def broken(") == []


# =====================================================
# 7. _check_contract_compliance (phases.py)
# =====================================================

class TestCheckContractCompliance:
    def setup_method(self):
        from checks import check_contract_compliance
        self.check = check_contract_compliance

    def test_empty_contract_returns_empty(self):
        assert self.check("def foo(): pass", []) == []
        assert self.check("def foo(): pass", None) == []

    def test_all_required_present(self):
        code = "def process_frame(img): pass\nclass Camera: pass"
        contract = [
            {"name": "process_frame", "signature": "def process_frame(img)", "required": True},
            {"name": "Camera", "signature": "class Camera", "required": True},
        ]
        assert self.check(code, contract) == []

    def test_missing_required_function(self):
        code = "def foo(): pass"
        contract = [
            {"name": "process_frame", "signature": "def process_frame(img)", "required": True},
        ]
        missing = self.check(code, contract)
        assert len(missing) == 1
        assert "process_frame" in missing[0]

    def test_missing_required_class(self):
        code = "def foo(): pass"
        contract = [
            {"name": "Camera", "signature": "class Camera", "required": True},
        ]
        missing = self.check(code, contract)
        assert len(missing) == 1
        assert "Camera" in missing[0]

    def test_non_required_not_flagged(self):
        code = "def foo(): pass"
        contract = [
            {"name": "optional_func", "signature": "def optional_func()", "required": False},
        ]
        assert self.check(code, contract) == []

    def test_indented_method_found(self):
        code = "class MyClass:\n    def process(self, data): pass"
        contract = [
            {"name": "process", "signature": "def process(self, data)", "required": True},
        ]
        assert self.check(code, contract) == []

    def test_async_function_found(self):
        code = "async def fetch_data(url): pass"
        contract = [
            {"name": "fetch_data", "signature": "async def fetch_data(url)", "required": True},
        ]
        assert self.check(code, contract) == []

    def test_fuzzy_match_hint(self):
        code = "def proccess_frame(img): pass"
        contract = [
            {"name": "process_frame", "signature": "def process_frame(img)", "required": True},
        ]
        missing = self.check(code, contract)
        assert len(missing) == 1
        assert "proccess_frame" in missing[0]  # fuzzy hint


# =====================================================
# 8. _ensure_a5_imports (phases.py)
# =====================================================

class TestEnsureA5Imports:
    def setup_method(self):
        from checks import ensure_a5_imports
        self.ensure = ensure_a5_imports

    def test_adds_missing_import(self):
        code = "def process(): pass"
        result = self.ensure(code, ["import numpy as np"])
        assert "import numpy as np" in result

    def test_existing_import_not_duplicated(self):
        code = "import numpy as np\ndef process(): pass"
        result = self.ensure(code, ["import numpy as np"])
        assert result.count("import numpy as np") == 1

    def test_merges_typing_imports(self):
        code = "from typing import List\ndef process(): pass"
        result = self.ensure(code, ["from typing import Dict"])
        assert "Dict" in result
        assert "List" in result

    def test_empty_code_returns_unchanged(self):
        assert self.ensure("", ["import os"]) == ""

    def test_empty_imports_returns_unchanged(self):
        code = "def foo(): pass"
        assert self.ensure(code, []) == code

    def test_non_string_imports_skipped(self):
        code = "def foo(): pass"
        result = self.ensure(code, [None, 42, "import os"])
        assert "import os" in result


# =====================================================
# 9. _is_hardcoded_return_stub (phases.py)
# =====================================================

class TestIsHardcodedReturnStub:
    def setup_method(self):
        from checks import _is_hardcoded_return_stub
        import ast
        self.check = _is_hardcoded_return_stub
        self.ast = ast

    def _parse_func(self, code):
        tree = self.ast.parse(code)
        for node in self.ast.walk(tree):
            if isinstance(node, (self.ast.FunctionDef, self.ast.AsyncFunctionDef)):
                return node
        raise ValueError("No function found")

    def test_hardcoded_string_return(self):
        func = self._parse_func("def f(x): return 'hello'")
        assert self.check(func) is True

    def test_hardcoded_number_return(self):
        func = self._parse_func("def f(x): return 42")
        assert self.check(func) is True

    def test_param_used_not_stub(self):
        func = self._parse_func("def f(x): return x.upper()")
        assert self.check(func) is False

    def test_no_params_not_stub(self):
        func = self._parse_func("def get_version(): return '1.0'")
        assert self.check(func) is False

    def test_self_only_not_stub(self):
        func = self._parse_func("def get_name(self): return 'test'")
        assert self.check(func) is False

    def test_empty_list_return_stub(self):
        func = self._parse_func("def f(data):\n    results = []\n    return results")
        assert self.check(func) is True

    def test_empty_dict_return_stub(self):
        func = self._parse_func("def f(data):\n    result = {}\n    return result")
        assert self.check(func) is True


# =====================================================
# 10. Contract validation: _validate_global_imports
# =====================================================

class TestValidateGlobalImports:
    def setup_method(self):
        from contract_validation import _validate_global_imports
        self.validate = _validate_global_imports
        self.logger = logging.getLogger("test_contract")

    def test_keeps_stdlib_imports(self):
        contract = {"global_imports": {"main.py": ["import os", "import json"]}}
        result = self.validate(contract, {}, ["main.py"], self.logger)
        assert "import os" in result["global_imports"]["main.py"]
        assert "import json" in result["global_imports"]["main.py"]

    def test_keeps_project_imports(self):
        contract = {"global_imports": {"main.py": ["from models import Camera"]}}
        result = self.validate(contract, {}, ["main.py", "models.py"], self.logger)
        assert len(result["global_imports"]["main.py"]) == 1

    def test_removes_phantom_project_import(self):
        contract = {"global_imports": {"main.py": ["from nonexistent_module import Foo"]}}
        result = self.validate(contract, {}, ["main.py", "models.py"], self.logger)
        assert len(result["global_imports"]["main.py"]) == 0

    def test_keeps_pip_dependency(self):
        contract = {"global_imports": {"main.py": ["import flask"]}}
        arch = {"dependencies": ["flask"]}
        result = self.validate(contract, arch, ["main.py"], self.logger)
        assert "import flask" in result["global_imports"]["main.py"]

    def test_removes_bare_name(self):
        contract = {"global_imports": {"main.py": ["flask"]}}
        result = self.validate(contract, {}, ["main.py"], self.logger)
        assert len(result["global_imports"]["main.py"]) == 0

    def test_fixes_wrong_pip_package(self):
        contract = {"global_imports": {"main.py": ["import opencv"]}}
        result = self.validate(contract, {}, ["main.py"], self.logger)
        imports = result["global_imports"]["main.py"]
        # opencv should be corrected to cv2
        assert any("cv2" in imp for imp in imports)

    def test_fixes_invalid_identifier(self):
        contract = {"global_imports": {"main.py": ["from opencv-python import cv2"]}}
        result = self.validate(contract, {}, ["main.py"], self.logger)
        imports = result["global_imports"]["main.py"]
        assert any("cv2" in imp for imp in imports)

    def test_auto_adds_to_requirements(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("flask\n", encoding="utf-8")
            contract = {"global_imports": {"main.py": ["import requests"]}}
            self.validate(contract, {}, ["main.py"], self.logger, requirements_path=req)
            content = req.read_text(encoding="utf-8")
            assert "requests" in content


# =====================================================
# 11. Contract validation: _validate_import_consistency
# =====================================================

class TestValidateImportConsistency:
    def setup_method(self):
        from contract_validation import _validate_import_consistency
        self.validate = _validate_import_consistency
        self.logger = logging.getLogger("test_contract")

    def test_keeps_valid_cross_file_import(self):
        contract = {
            "file_contracts": {
                "models.py": [{"name": "Camera"}],
                "main.py": [{"name": "main"}],
            },
            "global_imports": {
                "main.py": ["from models import Camera"],
            },
        }
        result = self.validate(contract, self.logger)
        assert "from models import Camera" in result["global_imports"]["main.py"]

    def test_removes_invalid_cross_file_import(self):
        contract = {
            "file_contracts": {
                "models.py": [{"name": "Camera"}],
                "main.py": [{"name": "main"}],
            },
            "global_imports": {
                "main.py": ["from models import NonExistent"],
            },
        }
        result = self.validate(contract, self.logger)
        assert len(result["global_imports"]["main.py"]) == 0

    def test_keeps_non_project_imports(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "main"}],
            },
            "global_imports": {
                "main.py": ["from flask import Flask"],
            },
        }
        result = self.validate(contract, self.logger)
        assert "from flask import Flask" in result["global_imports"]["main.py"]

    def test_partial_import_kept(self):
        contract = {
            "file_contracts": {
                "models.py": [{"name": "Camera"}, {"name": "Vehicle"}],
                "main.py": [],
            },
            "global_imports": {
                "main.py": ["from models import Camera, NonExistent"],
            },
        }
        result = self.validate(contract, self.logger)
        imports = result["global_imports"]["main.py"]
        assert len(imports) == 1
        assert "Camera" in imports[0]
        assert "NonExistent" not in imports[0]


# =====================================================
# 12. Contract validation: _validate_requirements_txt
# =====================================================

class TestValidateRequirementsTxt:
    def setup_method(self):
        from contract_validation import validate_requirements_txt
        self.validate_fn = validate_requirements_txt
        self.logger = logging.getLogger("test_contract")

    def test_fixes_wrong_pip_package(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("flask\nopencv\nrequests\n", encoding="utf-8")
            self.validate_fn(req, self.logger)
            content = req.read_text(encoding="utf-8")
            assert "opencv" not in content.split("\n")
            assert "opencv-python-headless" in content

    def test_removes_duplicates(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("flask\nFlask\nrequests\n", encoding="utf-8")
            self.validate_fn(req, self.logger)
            content = req.read_text(encoding="utf-8")
            lines = [l for l in content.splitlines() if l.strip()]
            # Should keep only one flask entry
            flask_lines = [l for l in lines if "flask" in l.lower()]
            assert len(flask_lines) == 1

    def test_preserves_comments(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("# requirements\nflask\n", encoding="utf-8")
            self.validate_fn(req, self.logger)
            content = req.read_text(encoding="utf-8")
            assert "# requirements" in content

    def test_nonexistent_path_no_error(self):
        self.validate_fn(Path("/nonexistent/path/requirements.txt"), self.logger)

    def test_none_path_no_error(self):
        self.validate_fn(None, self.logger)


# =====================================================
# 13. Contract validation: _normalize_file_contracts
# =====================================================

class TestNormalizeFileContracts:
    def setup_method(self):
        from contract_validation import _normalize_file_contracts
        self.normalize = _normalize_file_contracts

    def test_dict_unchanged(self):
        contract = {"file_contracts": {"main.py": [{"name": "main"}]}, "global_imports": {}}
        result = self.normalize(contract)
        assert result["file_contracts"]["main.py"] == [{"name": "main"}]

    def test_list_converted_to_dict(self):
        contract = {
            "file_contracts": [
                {"file": "main.py", "functions": [{"name": "main"}]},
                {"file": "utils.py", "functions": [{"name": "helper"}]},
            ],
            "global_imports": {},
        }
        result = self.normalize(contract)
        assert isinstance(result["file_contracts"], dict)
        assert "main.py" in result["file_contracts"]
        assert "utils.py" in result["file_contracts"]

    def test_removes_non_ascii_entries(self):
        contract = {
            "file_contracts": {
                "main.py": [
                    {"name": "Camera"},
                    {"name": "\u0412\u0438\u0434\u0435\u043e"},  # Russian: Video
                ],
            },
            "global_imports": {},
        }
        result = self.normalize(contract)
        names = [item["name"] for item in result["file_contracts"]["main.py"]]
        assert "Camera" in names
        assert "\u0412\u0438\u0434\u0435\u043e" not in names


# =====================================================
# 14. Contract validation: _inject_signature_type_imports
# =====================================================

class TestInjectSignatureTypeImports:
    def setup_method(self):
        from contract_validation import _inject_signature_type_imports
        self.inject = _inject_signature_type_imports
        self.logger = logging.getLogger("test_contract")

    def test_adds_typing_imports(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "f", "signature": "def f(x: List[int]) -> Dict[str, Any]"}],
            },
            "global_imports": {"main.py": []},
        }
        result = self.inject(contract, self.logger)
        imports = result["global_imports"]["main.py"]
        assert any("typing" in imp and "List" in imp for imp in imports)
        assert any("Dict" in imp for imp in imports)
        assert any("Any" in imp for imp in imports)

    def test_adds_numpy_import(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "f", "signature": "def f(img: np.ndarray) -> np.ndarray"}],
            },
            "global_imports": {"main.py": []},
        }
        result = self.inject(contract, self.logger)
        imports = result["global_imports"]["main.py"]
        assert "import numpy as np" in imports

    def test_no_duplicate_imports(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "f", "signature": "def f(x: np.ndarray)"}],
            },
            "global_imports": {"main.py": ["import numpy as np"]},
        }
        result = self.inject(contract, self.logger)
        imports = result["global_imports"]["main.py"]
        assert imports.count("import numpy as np") == 1


# =====================================================
# 15. Contract validation pipeline order
# =====================================================

class TestContractPipelineOrder:
    """Verifies that the A5 contract validation pipeline applies checks
    in the correct order and that all stages are called."""

    def test_normalize_before_validate(self):
        """List-format file_contracts must be normalized before validation."""
        from contract_validation import _normalize_file_contracts, _validate_import_consistency
        contract = {
            "file_contracts": [
                {"file": "main.py", "functions": [{"name": "main"}]},
            ],
            "global_imports": {"main.py": ["from models import Foo"]},
        }
        # Normalize first
        contract = _normalize_file_contracts(contract)
        assert isinstance(contract["file_contracts"], dict)

    def test_validate_global_imports_removes_phantoms(self):
        """Phantom imports removed before consistency check."""
        from contract_validation import _validate_global_imports, _validate_import_consistency
        logger = logging.getLogger("test")
        contract = {
            "file_contracts": {"main.py": [{"name": "main"}]},
            "global_imports": {"main.py": ["from phantom_module import Foo"]},
        }
        contract = _validate_global_imports(contract, {}, ["main.py"], logger)
        # phantom_module looks like a project import (snake_case) and file doesn't exist
        assert len(contract["global_imports"]["main.py"]) == 0

    def test_full_pipeline_e2e(self):
        """Simulate the full A5 validation pipeline order."""
        from contract_validation import (
            _normalize_file_contracts,
            _validate_global_imports,
            _inject_signature_type_imports,
            _validate_import_consistency,
            _sanitize_implementation_hints,
        )
        logger = logging.getLogger("test")

        contract = {
            "file_contracts": {
                "models.py": [{"name": "Camera", "signature": "class Camera", "required": True}],
                "main.py": [
                    {
                        "name": "process",
                        "signature": "def process(img: np.ndarray) -> List[Camera]",
                        "required": True,
                        "implementation_hints": "Use Camera from models",
                    }
                ],
            },
            "global_imports": {
                "main.py": ["from models import Camera"],
                "models.py": [],
            },
        }

        # Apply pipeline in order
        contract = _normalize_file_contracts(contract)
        contract = _validate_global_imports(contract, {}, ["main.py", "models.py"], logger)
        contract = _inject_signature_type_imports(contract, logger)
        contract = _validate_import_consistency(contract, logger)
        contract = _sanitize_implementation_hints(contract, logger)

        # Verify: Camera import preserved, typing added
        main_imports = contract["global_imports"]["main.py"]
        assert any("Camera" in imp for imp in main_imports)
        assert any("List" in imp for imp in main_imports)


# =====================================================
# 16. Safety valves
# =====================================================

class TestSafetyValves:
    """Test force-approve thresholds and phase skip limits."""

    def test_max_cumulative_threshold(self):
        """MAX_CUMULATIVE = MAX_FILE_ATTEMPTS * 3 = 45."""
        from phase_develop import MAX_CUMULATIVE
        from config import MAX_FILE_ATTEMPTS
        assert MAX_CUMULATIVE == MAX_FILE_ATTEMPTS * 3

    def test_max_file_attempts_escalation(self):
        """File should be escalated after MAX_FILE_ATTEMPTS."""
        from config import MAX_FILE_ATTEMPTS
        assert MAX_FILE_ATTEMPTS == 15

    def test_max_spec_revisions(self):
        """revise_spec limited to MAX_SPEC_REVISIONS."""
        from config import MAX_SPEC_REVISIONS
        assert MAX_SPEC_REVISIONS == 9

    def test_max_test_attempts(self):
        from config import MAX_TEST_ATTEMPTS
        assert MAX_TEST_ATTEMPTS == 6

    def test_bump_phase_fail_counts(self):
        from supervisor import bump_phase_fail
        state = {"phase_fail_counts": {}, "phase_total_fails": {}}
        n = bump_phase_fail(state, "develop")
        assert n == 1
        assert state["phase_total_fails"]["develop"] == 1
        n2 = bump_phase_fail(state, "develop")
        assert n2 == 2
        assert state["phase_total_fails"]["develop"] == 2

    def test_reset_phase_fail_preserves_total(self):
        from supervisor import bump_phase_fail, reset_phase_fail
        state = {"phase_fail_counts": {}, "phase_total_fails": {}}
        bump_phase_fail(state, "develop")
        bump_phase_fail(state, "develop")
        reset_phase_fail(state, "develop")
        assert state["phase_fail_counts"]["develop"] == 0
        assert state["phase_total_fails"]["develop"] == 2  # total not reset

    def test_max_phase_total_fails_threshold(self):
        from config import MAX_PHASE_TOTAL_FAILS
        assert MAX_PHASE_TOTAL_FAILS == 90

    def test_feedback_history_limit(self):
        from state import push_feedback
        from config import MAX_FEEDBACK_HISTORY
        st = {"feedbacks": {}, "feedback_history": {}}
        for i in range(10):
            push_feedback(st, "a.py", f"feedback {i}")
        assert len(st["feedback_history"]["a.py"]) == MAX_FEEDBACK_HISTORY

    def test_cycling_detection_in_feedback(self):
        from state import get_feedback_ctx
        from config import MAX_FEEDBACK_HISTORY
        st = {
            "feedbacks": {},
            "feedback_history": {"a.py": ["same error"] * MAX_FEEDBACK_HISTORY},
        }
        ctx = get_feedback_ctx(st, "a.py")
        assert "КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ" in ctx
        assert "ПРИНЦИПИАЛЬНО ДРУГУЮ" in ctx


# =====================================================
# 17. _parse_import_line (contract.py)
# =====================================================

class TestParseImportLine:
    def setup_method(self):
        from contract_validation import _parse_import_line
        self.parse = _parse_import_line

    def test_simple_import(self):
        result = self.parse("from models import Camera")
        assert result == ("models", ["Camera"])

    def test_multi_import(self):
        result = self.parse("from models import Camera, Vehicle, Plate")
        assert result == ("models", ["Camera", "Vehicle", "Plate"])

    def test_import_with_alias(self):
        result = self.parse("from models import Camera as Cam")
        assert result == ("models", ["Camera"])

    def test_bare_import_returns_none(self):
        assert self.parse("import os") is None

    def test_non_string_returns_none(self):
        assert self.parse(42) is None
        assert self.parse(None) is None

    def test_empty_string_returns_none(self):
        assert self.parse("") is None


# =====================================================
# 18. code_context: validate_imports
# =====================================================

class TestValidateImports:
    def setup_method(self):
        from code_context import validate_imports
        self.validate = validate_imports

    def test_stdlib_import_ok(self):
        code = "import os\nimport json\nimport sys"
        assert self.validate(code, "main.py", ["main.py"], None, "python") == []

    def test_project_import_ok(self):
        code = "from models import Camera"
        assert self.validate(code, "main.py", ["main.py", "models.py"], None, "python") == []

    def test_unknown_module_detected(self):
        code = "import nonexistent_package"
        warnings = self.validate(code, "main.py", ["main.py"], None, "python")
        assert len(warnings) > 0
        assert "nonexistent_package" in warnings[0]

    def test_pip_import_ok_with_requirements(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("flask\nrequests\n", encoding="utf-8")
            code = "import flask\nimport requests"
            assert self.validate(code, "main.py", ["main.py"], req, "python") == []


# =====================================================
# 19. code_context: validate_cross_file_names
# =====================================================

class TestValidateCrossFileNames:
    def setup_method(self):
        from code_context import validate_cross_file_names
        self.validate = validate_cross_file_names

    def test_valid_cross_file_import(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td)
            (src / "models.py").write_text("class Camera:\n    pass\n", encoding="utf-8")
            code = "from models import Camera\ncam = Camera()"
            assert self.validate(code, "main.py", ["main.py", "models.py"], src) == []

    def test_invalid_cross_file_import(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td)
            (src / "models.py").write_text("class Vehicle:\n    pass\n", encoding="utf-8")
            code = "from models import Camera"
            warnings = self.validate(code, "main.py", ["main.py", "models.py"], src)
            assert len(warnings) > 0
            assert "Camera" in warnings[0]

    def test_same_file_import_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td)
            code = "from main import something"
            # Self-import is checked by validate_imports, not cross_file_names
            warnings = self.validate(code, "main.py", ["main.py"], src)
            assert warnings == [], f"Self-import should be skipped, got: {warnings}"

    def test_non_project_import_ignored(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td)
            (src / "main.py").write_text("from flask import Flask", encoding="utf-8")
            code = "from flask import Flask\napp = Flask(__name__)"
            issues = self.validate(code, "main.py", ["main.py"], src)
            assert issues == []


# =====================================================
# 20. code_context: _get_top_level_names
# =====================================================

# =====================================================
# 21. code_context: _find_name_in_classes
# =====================================================

class TestFindNameInClasses:
    def setup_method(self):
        from code_context import find_name_in_classes
        self.find = find_name_in_classes

    def test_finds_method(self):
        code = "class Camera:\n    def take_photo(self): pass"
        assert self.find(code, "take_photo") == "Camera"

    def test_finds_attribute(self):
        code = "class Camera:\n    resolution: int = 1080"
        assert self.find(code, "resolution") == "Camera"

    def test_not_found_returns_none(self):
        code = "class Camera:\n    def take_photo(self): pass"
        assert self.find(code, "nonexistent") is None

    def test_syntax_error_returns_none(self):
        assert self.find("not valid python!!!", "foo") is None


# =====================================================
# 22. _auto_add_requirement (contract.py)
# =====================================================

# =====================================================
# 23. json_utils: _repair_truncated_json
# =====================================================

class TestRepairTruncatedJson:
    def setup_method(self):
        from json_utils import repair_truncated_json
        self.repair = repair_truncated_json

    def test_repairs_truncated_object(self):
        text = '{"code": "def foo(): pass", "status": "ok'
        result = self.repair(text)
        assert result is not None
        assert "code" in result

    def test_repairs_truncated_array(self):
        text = '{"items": [1, 2, 3'
        result = self.repair(text)
        assert result is not None
        assert "items" in result

    def test_balanced_json_returns_none(self):
        text = '{"key": "value"}'
        assert self.repair(text) is None

    def test_deeply_nested(self):
        text = '{"a": {"b": {"c": "val'
        result = self.repair(text)
        assert result is not None
        assert "a" in result


# =====================================================
# 24. _parse_requirements (code_context.py)
# =====================================================

class TestParseRequirements:
    def setup_method(self):
        from code_context import parse_requirements
        self.parse = parse_requirements

    def test_basic_requirements(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("flask\nrequests>=2.0\n", encoding="utf-8")
            result = self.parse(req)
            assert "flask" in result
            assert "requests" in result

    def test_wrong_pip_corrected(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("opencv\n", encoding="utf-8")
            result = self.parse(req)
            assert "cv2" in result
            assert "opencv_python_headless" in result

    def test_transitive_deps(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("tensorflow\n", encoding="utf-8")
            result = self.parse(req)
            assert "tensorflow" in result
            assert "numpy" in result
            assert "keras" in result

    def test_pip_to_import_mapping(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("Pillow\npyyaml\n", encoding="utf-8")
            result = self.parse(req)
            assert "pil" in result  # Pillow -> PIL -> pil (lowered)
            assert "yaml" in result

    def test_comments_and_blanks_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("# comment\n\nflask\n", encoding="utf-8")
            result = self.parse(req)
            assert "flask" in result
            assert len(result) > 0

    def test_nonexistent_file(self):
        result = self.parse(Path("/nonexistent/requirements.txt"))
        assert result == set()


# =====================================================
# contract_validation: _auto_add_requirement
# =====================================================

class TestAutoAddRequirement:
    def setup_method(self):
        from contract_validation import _auto_add_requirement
        self.add = _auto_add_requirement
        self.logger = logging.getLogger("test")

    def test_adds_new_package(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("flask\n", encoding="utf-8")
            self.add(req, "requests", self.logger)
            content = req.read_text()
            assert "requests" in content

    def test_skips_existing_package(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("requests\n", encoding="utf-8")
            self.add(req, "requests", self.logger)
            assert req.read_text().count("requests") == 1

    def test_skips_existing_normalized(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("opencv-python\n", encoding="utf-8")
            self.add(req, "opencv_python", self.logger)
            lines = [l for l in req.read_text().splitlines() if l.strip()]
            assert len(lines) == 1

    def test_nonexistent_path(self):
        self.add(Path("/nonexistent/req.txt"), "flask", self.logger)

    def test_corrects_wrong_pip_name(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("flask\n", encoding="utf-8")
            self.add(req, "opencv", self.logger)
            content = req.read_text(encoding="utf-8")
            assert "opencv-python-headless" in content


# =====================================================
# contract_validation: _detect_and_fix_circular_imports
# =====================================================

class TestDetectAndFixCircularImports:
    def setup_method(self):
        from contract_validation import _detect_and_fix_circular_imports
        self.detect = _detect_and_fix_circular_imports
        self.logger = logging.getLogger("test")

    def test_no_cycles_unchanged(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "main", "signature": "def main()"}],
                "utils.py": [{"name": "helper", "signature": "def helper()"}],
            },
            "global_imports": {
                "main.py": ["from utils import helper"],
                "utils.py": [],
            },
        }
        result = self.detect(contract, ["main.py", "utils.py"], self.logger)
        assert result["global_imports"]["main.py"] == ["from utils import helper"]

    def test_class_cycle_resolved_via_models(self):
        contract = {
            "file_contracts": {
                "a.py": [{"name": "AClass", "signature": "class AClass"}],
                "b.py": [{"name": "BClass", "signature": "class BClass"}],
            },
            "global_imports": {
                "a.py": ["from b import BClass"],
                "b.py": ["from a import AClass"],
            },
        }
        files = ["a.py", "b.py"]
        result = self.detect(contract, files, self.logger)
        # At least one class should be moved to models.py
        assert "models.py" in result["file_contracts"]

    def test_empty_contract(self):
        result = self.detect({"file_contracts": {}, "global_imports": {}}, [], self.logger)
        assert result == {"file_contracts": {}, "global_imports": {}}


# =====================================================
# contract_validation: _inject_cross_file_imports
# =====================================================

class TestInjectCrossFileImports:
    def setup_method(self):
        from contract_validation import _inject_cross_file_imports
        self.inject = _inject_cross_file_imports
        self.logger = logging.getLogger("test")

    def test_injects_missing_import(self):
        contract = {
            "file_contracts": {
                "models.py": [{"name": "Camera", "signature": "class Camera"}],
                "main.py": [{"name": "process", "signature": "def process(cam: Camera) -> str"}],
            },
            "global_imports": {"models.py": [], "main.py": []},
        }
        result = self.inject(contract, self.logger)
        assert any("Camera" in imp for imp in result["global_imports"]["main.py"])

    def test_no_self_import(self):
        contract = {
            "file_contracts": {
                "main.py": [
                    {"name": "MyClass", "signature": "class MyClass"},
                    {"name": "use_it", "signature": "def use_it(x: MyClass)"},
                ],
            },
            "global_imports": {"main.py": []},
        }
        result = self.inject(contract, self.logger)
        assert result["global_imports"]["main.py"] == []

    def test_existing_import_not_duplicated(self):
        contract = {
            "file_contracts": {
                "models.py": [{"name": "Camera", "signature": "class Camera"}],
                "main.py": [{"name": "process", "signature": "def process(cam: Camera)"}],
            },
            "global_imports": {"models.py": [], "main.py": ["from models import Camera"]},
        }
        result = self.inject(contract, self.logger)
        assert result["global_imports"]["main.py"].count("from models import Camera") == 1


# =====================================================
# contract_validation: _validate_data_model_coverage
# =====================================================

class TestValidateDataModelCoverage:
    def setup_method(self):
        from contract_validation import _validate_data_model_coverage
        self.check = _validate_data_model_coverage
        self.logger = logging.getLogger("test")

    def test_all_covered(self):
        contract = {
            "file_contracts": {
                "models.py": [{"name": "Camera", "signature": "class Camera"}],
            },
        }
        specs = {"data_models": [{"name": "Camera"}]}
        assert self.check(contract, specs, self.logger) == []

    def test_missing_model(self):
        contract = {"file_contracts": {"main.py": [{"name": "main", "signature": "def main()"}]}}
        specs = {"data_models": [{"name": "Vehicle"}]}
        missing = self.check(contract, specs, self.logger)
        assert "Vehicle" in missing

    def test_camelcase_match(self):
        contract = {
            "file_contracts": {
                "models.py": [{"name": "LicensePlate", "signature": "class LicensePlate"}],
            },
        }
        specs = {"data_models": [{"name": "license_plate"}]}
        assert self.check(contract, specs, self.logger) == []

    def test_empty_specs(self):
        assert self.check({"file_contracts": {}}, {}, self.logger) == []
        assert self.check({"file_contracts": {}}, {"data_models": []}, self.logger) == []


# =====================================================
# contract_validation: _validate_signature_types
# =====================================================

class TestValidateSignatureTypes:
    def setup_method(self):
        from contract_validation import _validate_signature_types
        self.validate = _validate_signature_types
        self.logger = logging.getLogger("test")

    def test_defined_type_ok(self):
        contract = {
            "file_contracts": {
                "models.py": [{"name": "Camera", "signature": "class Camera"}],
                "main.py": [{"name": "process", "signature": "def process(cam: Camera)"}],
            },
            "global_imports": {"models.py": [], "main.py": []},
        }
        result = self.validate(contract, ["models.py", "main.py"], self.logger)
        # Camera already defined in models.py — no auto-created duplicate should appear
        models_items = result["file_contracts"]["models.py"]
        auto_created = [i for i in models_items if isinstance(i, dict)
                        and i.get("name") == "Camera" and "авто-создан" in i.get("description", "")]
        assert auto_created == [], f"Camera was auto-created despite already existing: {auto_created}"
        # Original Camera item should still be there
        assert any(i.get("name") == "Camera" for i in models_items if isinstance(i, dict))

    def test_undefined_type_creates_class(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "process", "signature": "def process(x: FooBar)"}],
            },
            "global_imports": {"main.py": []},
        }
        result = self.validate(contract, ["main.py"], self.logger)
        assert "models.py" in result["file_contracts"]
        names = [i["name"] for i in result["file_contracts"]["models.py"] if isinstance(i, dict)]
        assert "FooBar" in names

    def test_builtin_types_skipped(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "process", "signature": "def process(x: str, y: int) -> bool"}],
            },
            "global_imports": {"main.py": []},
        }
        result = self.validate(contract, ["main.py"], self.logger)
        assert "models.py" not in result.get("file_contracts", {}) or \
               result["file_contracts"].get("models.py", []) == []

    def test_pip_imported_types_skipped(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "create_app", "signature": "def create_app() -> Flask"}],
            },
            "global_imports": {"main.py": ["from flask import Flask"]},
        }
        result = self.validate(contract, ["main.py"], self.logger)
        # Flask is imported from pip, should NOT be created in models.py
        fc = result["file_contracts"]
        if "models.py" in fc:
            names = [i["name"] for i in fc["models.py"] if isinstance(i, dict)]
            assert "Flask" not in names, f"Flask was auto-created in models.py despite being a pip import: {names}"
        # Either way, main.py should still have create_app
        assert any(i.get("name") == "create_app" for i in fc["main.py"] if isinstance(i, dict))


# =====================================================
# contract_validation: run_a5_validation_pipeline
# =====================================================

class TestRunA5ValidationPipeline:
    def setup_method(self):
        from contract_validation import run_a5_validation_pipeline
        self.run = run_a5_validation_pipeline
        self.logger = logging.getLogger("test")

    def test_basic_contract_passes(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "main", "signature": "def main()"}],
            },
            "global_imports": {"main.py": ["import os"]},
        }
        result = self.run(contract, {}, ["main.py"], self.logger)
        assert "main.py" in result["file_contracts"]
        assert isinstance(result["global_imports"]["main.py"], list)

    def test_removes_phantom_imports(self):
        contract = {
            "file_contracts": {"main.py": [{"name": "main", "signature": "def main()"}]},
            "global_imports": {"main.py": ["from phantom_module import Foo"]},
        }
        result = self.run(contract, {}, ["main.py"], self.logger)
        assert len(result["global_imports"]["main.py"]) == 0


# =====================================================
# code_context: get_top_level_names
# =====================================================

class TestGetTopLevelNames:
    def setup_method(self):
        from code_context import get_top_level_names
        self.get = get_top_level_names

    def test_functions_and_classes(self):
        code = "def foo(): pass\nclass Bar: pass\nx = 1"
        names = self.get(code)
        assert "foo" in names
        assert "Bar" in names
        assert "x" in names

    def test_nested_not_included(self):
        code = "def outer():\n    def inner(): pass"
        names = self.get(code)
        assert "outer" in names
        assert "inner" not in names

    def test_syntax_error_uses_regex_fallback(self):
        names = self.get("def broken(")
        # Regex fallback still finds the name
        assert isinstance(names, set)

    def test_assignments(self):
        code = "X = 42\ny, z = 1, 2"
        names = self.get(code)
        assert "X" in names
        assert "y" in names
        assert "z" in names

    def test_import_aliases(self):
        code = "import os\nfrom pathlib import Path\nimport numpy as np"
        names = self.get(code)
        assert "os" in names
        assert "Path" in names
        assert "np" in names


# =====================================================
# code_context: validate_cross_file_names
# =====================================================

# =====================================================
# phase_test: _deapprove_file
# =====================================================

class TestDeapproveFile:
    def setup_method(self):
        from phase_test import _deapprove_file
        self.deapprove = _deapprove_file

    def test_removes_from_approved(self):
        state = {"approved_files": ["main.py"], "feedbacks": {}, "cumulative_file_attempts": {}}
        self.deapprove(state, "main.py", "broken")
        assert "main.py" not in state["approved_files"]
        assert state["feedbacks"]["main.py"] == "broken"
        assert state["cumulative_file_attempts"]["main.py"] == 3

    def test_cumulative_increments(self):
        state = {"approved_files": [], "feedbacks": {}, "cumulative_file_attempts": {"x.py": 5}}
        self.deapprove(state, "x.py", "err", cumulative_bump=3)
        assert state["cumulative_file_attempts"]["x.py"] == 8

    def test_not_in_approved_no_error(self):
        state = {"approved_files": ["other.py"], "feedbacks": {}, "cumulative_file_attempts": {}}
        self.deapprove(state, "main.py", "msg")
        assert state["feedbacks"]["main.py"] == "msg"
        assert "other.py" in state["approved_files"]


# =====================================================
# 18. sync_files_with_a5 (state.py)
# =====================================================

class TestSyncFilesWithA5:
    def setup_method(self):
        from state import sync_files_with_a5
        self.sync = sync_files_with_a5
        self.logger = logging.getLogger("test")

    def test_adds_new_files(self):
        state = {"files": ["main.py"], "feedbacks": {"main.py": ""}}
        self.sync(state, {"main.py", "utils.py"}, self.logger)
        assert "utils.py" in state["files"]
        assert state["feedbacks"]["utils.py"] == ""

    def test_removes_ghost_files(self):
        state = {
            "files": ["main.py", "old.py"],
            "feedbacks": {"main.py": "", "old.py": "fb"},
            "approved_files": ["old.py"],
            "file_attempts": {"old.py": 3},
            "cumulative_file_attempts": {"old.py": 5},
        }
        self.sync(state, {"main.py"}, self.logger)
        assert "old.py" not in state["files"]
        assert "old.py" not in state["feedbacks"]
        assert "old.py" not in state["approved_files"]
        assert "old.py" not in state["file_attempts"]
        assert "old.py" not in state["cumulative_file_attempts"]

    def test_noop_when_synced(self):
        state = {"files": ["a.py", "b.py"], "feedbacks": {"a.py": "", "b.py": ""}}
        self.sync(state, {"a.py", "b.py"}, self.logger)
        assert len(state["files"]) == 2

```
### 📄 `tests/test_modules.py`

```python
"""
Тесты для проверки модульного разбиения ai_factory.
Запуск: source .venv_factory/bin/activate && pytest tests/ -v
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ─────────────────────────────────────────────
# 1. Import checks
# ─────────────────────────────────────────────

@pytest.mark.parametrize("mod", [
    "config", "models_pool", "prompts",
    "cache", "lang_utils", "log_utils", "json_utils",
    "llm", "stats", "artifacts", "infra", "state",
    "code_context", "contract", "phases", "supervisor", "ai_factory",
    "exceptions",
])
def test_import(mod):
    __import__(mod)


# ─────────────────────────────────────────────
# 2. exceptions.py
# ─────────────────────────────────────────────

def test_exception_hierarchy():
    from exceptions import FactoryError, LLMError, DockerError, StateError, SpecError
    assert issubclass(LLMError, FactoryError)
    assert issubclass(DockerError, FactoryError)
    assert issubclass(StateError, FactoryError)
    assert issubclass(SpecError, FactoryError)
    assert issubclass(FactoryError, Exception)


def test_exceptions_are_raisable():
    from exceptions import LLMError, DockerError, StateError, SpecError
    for exc_cls in (LLMError, DockerError, StateError, SpecError):
        with pytest.raises(exc_cls):
            raise exc_cls("тест")


# ─────────────────────────────────────────────
# 3. config.py
# ─────────────────────────────────────────────

def test_config_env_vars():
    from config import LLM_BASE_URL, LLM_API_KEY, LLM_TIMEOUT, LOG_LEVEL, BASE_DIR
    assert isinstance(LLM_BASE_URL, str) and LLM_BASE_URL.startswith("http")
    assert isinstance(LLM_API_KEY, str) and len(LLM_API_KEY) > 0
    assert isinstance(LLM_TIMEOUT, float) and LLM_TIMEOUT > 0
    assert LOG_LEVEL in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    assert isinstance(BASE_DIR, Path)


def test_config_pipeline_knobs():
    from config import (
        WAIT_TIMEOUT, RUN_TIMEOUT, MAX_CONTEXT_CHARS, MIN_COVERAGE,
        MAX_ABSOLUTE_ITERS, MAX_FILE_ATTEMPTS, MAX_PHASE_TOTAL_FAILS,
        FACTORY_DIR, SRC_DIR, ARTIFACTS_DIR, LOGS_DIR, CACHEABLE_AGENTS,
    )
    assert isinstance(WAIT_TIMEOUT, int)
    assert isinstance(MAX_FILE_ATTEMPTS, int)
    assert isinstance(CACHEABLE_AGENTS, set)
    assert "business_analyst" in CACHEABLE_AGENTS


# ─────────────────────────────────────────────
# 4. cache.py
# ─────────────────────────────────────────────

def test_thread_safe_cache_basic():
    from cache import ThreadSafeCache
    c = ThreadSafeCache({"a": 1})
    assert c.get("a") == 1
    assert "a" in c
    c["b"] = 2
    assert c["b"] == 2
    assert c.to_dict() == {"a": 1, "b": 2}


def test_cache_key_deterministic():
    from cache import cache_key
    k1 = cache_key("agent", "model", "text", "python")
    k2 = cache_key("agent", "model", "text", "python")
    k3 = cache_key("agent", "model", "text", "typescript")
    assert k1 == k2
    assert k1 != k3
    assert len(k1) == 64  # sha256 hex


def test_cache_save_load_roundtrip():
    from cache import ThreadSafeCache, save_cache, load_cache
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        (p / ".factory").mkdir()
        orig = ThreadSafeCache({"x": 42})
        save_cache(p, orig)
        loaded = load_cache(p)
        assert loaded["x"] == 42


# ─────────────────────────────────────────────
# 5. lang_utils.py
# ─────────────────────────────────────────────

def test_lang_display():
    from lang_utils import LANG_DISPLAY, LANG_EXT
    assert LANG_DISPLAY["python"] == "Python"
    assert LANG_EXT["typescript"] == "ts"


def test_docker_image():
    from lang_utils import get_docker_image
    assert get_docker_image("python") == "python:3.12-slim"
    assert get_docker_image("go") == "python:3.12-slim"  # fallback


def test_execution_commands():
    from lang_utils import get_execution_command, get_test_command
    cmd = get_execution_command("python", "main.py")
    assert "main.py" in cmd and "pip install" in cmd
    assert "ts-node" in get_execution_command("typescript", "main.ts")
    assert "cargo run" in get_execution_command("rust", "")
    assert "pytest" in get_test_command("python")
    assert "jest" in get_test_command("typescript")
    assert "cargo test" in get_test_command("rust")


def test_sanitize_files_list():
    from lang_utils import sanitize_files_list
    safe = sanitize_files_list(["main.py", "utils.py", "../evil.py", "/etc/passwd"])
    assert "../evil.py" not in safe
    assert "/etc/passwd" not in safe
    assert "main.py" in safe and "utils.py" in safe

    assert sanitize_files_list([], "python") == ["main.py"]
    assert sanitize_files_list([], "typescript") == ["main.ts"]


# ─────────────────────────────────────────────
# 6. json_utils.py
# ─────────────────────────────────────────────

def test_parse_if_str():
    from json_utils import parse_if_str
    assert parse_if_str([1, 2], list, []) == [1, 2]
    assert parse_if_str("[1,2]", list, []) == [1, 2]
    assert parse_if_str("hello", list, [99]) == [99]
    assert parse_if_str(None, dict, {}) == {}


def test_to_str():
    from json_utils import to_str
    assert to_str("hi") == "hi"
    assert to_str(None) == ""
    assert to_str({"k": 1}) == '{"k": 1}'
    assert to_str(42) == "42"


def test_safe_contract():
    from json_utils import safe_contract
    state = {"api_contract": {"file_contracts": '{"a.py": "[1,2]"}', "global_imports": {}}}
    c = safe_contract(state)
    assert isinstance(c["file_contracts"], dict)


def test_extract_json_from_text():
    from json_utils import extract_json_from_text, repair_json
    assert extract_json_from_text('Some text {"key": "value"} more') == {"key": "value"}
    assert extract_json_from_text('```json\n{"answer": 42}\n```') == {"answer": 42}

    repaired = repair_json('{"a": 1,}')
    assert json.loads(repaired) == {"a": 1}

    with pytest.raises(ValueError):
        extract_json_from_text("no json here")


# ─────────────────────────────────────────────
# 7. log_utils.py
# ─────────────────────────────────────────────

def test_get_model():
    from log_utils import get_model
    m = get_model("developer", 0, randomize=False)
    assert isinstance(m, str) and len(m) > 0


def test_input_with_timeout_default():
    from log_utils import input_with_timeout
    result = input_with_timeout("Test: ", timeout=1, default="default_val")
    assert result == "default_val"


def test_setup_logger():
    from log_utils import setup_logger
    import logging
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        logger = setup_logger(p)
        assert logger is not None
        assert logger is setup_logger(p)  # idempotent
        # Консольный хендлер добавлен на root logger
        root = logging.getLogger()
        has_stream = any(type(h) is logging.StreamHandler for h in root.handlers)
        assert has_stream


def test_log_runtime_error():
    from log_utils import log_runtime_error, setup_logger
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        setup_logger(p)
        log_runtime_error(p, "some stderr")
        err_log = p / ".factory" / "logs" / "run_errors.log"
        assert err_log.exists()
        assert "some stderr" in err_log.read_text()


# ─────────────────────────────────────────────
# 8. stats.py
# ─────────────────────────────────────────────

def test_model_stats_record_and_flush():
    from stats import ModelStats
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        ms = ModelStats(p)
        ms.record("developer", "model_a", True)
        ms.record("developer", "model_a", False)
        ms.flush()
        assert ms.path.exists()
        data = json.loads(ms.path.read_text())
        assert data["developer:model_a"] == {"success": 1, "fail": 1}


def test_print_iteration_table(capsys):
    from stats import print_iteration_table
    state = {
        "language": "python", "approved_files": ["a.py"],
        "files": ["a.py", "b.py"], "iteration": 3, "last_phase": "develop"
    }
    print_iteration_table(state)
    out = capsys.readouterr().out
    assert "ИТЕРАЦИЯ" in out and "1/2" in out


# ─────────────────────────────────────────────
# 9. artifacts.py
# ─────────────────────────────────────────────

def test_artifact_labels():
    from artifacts import ARTIFACT_LABELS
    assert ARTIFACT_LABELS["A0"] == "user_intent"
    assert ARTIFACT_LABELS["A10"] == "final_summary"


def test_save_load_artifact():
    from artifacts import save_artifact, load_artifact, update_artifact_a9
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        save_artifact(p, "A0", "# Test content")
        assert load_artifact(p, "A0") == "# Test content"

        save_artifact(p, "A2", {"key": "val"})
        loaded = load_artifact(p, "A2")
        assert "```json" in loaded and '"key"' in loaded

        assert load_artifact(p, "A6") is None

        update_artifact_a9(p, "main.py", "approved")
        a9 = (p / ".factory" / "artifacts" / "A9_implementation_logs.md").read_text()
        assert "main.py" in a9 and "approved" in a9


# ─────────────────────────────────────────────
# 10. infra.py
# ─────────────────────────────────────────────

def test_run_command():
    from infra import run_command
    rc, out, err = run_command(["echo", "hello"])
    assert rc == 0 and "hello" in out

    rc2, _, _ = run_command(["false"])
    assert rc2 != 0

    rc3, _, err3 = run_command(["nonexistent_cmd_xyz"])
    assert rc3 == -1 and "не найдена" in err3

    rc4, _, _ = run_command(["sleep", "10"], timeout=1)
    assert rc4 == -1


def test_container_name():
    from infra import _make_container_name
    n1 = _make_container_name(Path("/some/path"))
    n2 = _make_container_name(Path("/some/path"))
    n3 = _make_container_name(Path("/other/path"))
    assert n1 == n2
    assert n1 != n3
    assert n1.startswith("factory_")


# ─────────────────────────────────────────────
# 11. state.py
# ─────────────────────────────────────────────

def test_feedback_push_and_trim():
    from state import push_feedback, MAX_FEEDBACK_HISTORY
    assert MAX_FEEDBACK_HISTORY == 3
    st = {"files": ["a.py"], "feedbacks": {}, "feedback_history": {}}
    push_feedback(st, "a.py", "fix this")
    assert st["feedbacks"]["a.py"] == "fix this"
    assert st["feedback_history"]["a.py"] == ["fix this"]
    for i in range(MAX_FEEDBACK_HISTORY + 1):
        push_feedback(st, "a.py", f"feedback {i}")
    assert len(st["feedback_history"]["a.py"]) == MAX_FEEDBACK_HISTORY


def test_feedback_ctx():
    from state import get_feedback_ctx
    st = {"feedbacks": {}, "feedback_history": {}}
    assert get_feedback_ctx(st, "x.py") == ""

    st2 = {"feedbacks": {"a.py": "last"}, "feedback_history": {"a.py": ["only"]}}
    ctx = get_feedback_ctx(st2, "a.py")
    assert len(ctx) > 0


def test_sanitize_package_name():
    from state import sanitize_package_name
    assert sanitize_package_name("requests") == "requests"
    assert sanitize_package_name("requests>=2.0") == "requests>=2.0"
    # Пробел+точка с запятой удаляются
    cleaned = sanitize_package_name("pkg; sys_platform")
    assert ";" not in cleaned and " " not in cleaned


def test_save_load_state():
    from state import save_state, load_state
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        st = {"task": "t", "files": ["a.py"], "feedbacks": {"a.py": ""}, "iteration": 1}
        save_state(p, st)
        loaded = load_state(p)
        assert loaded["task"] == "t" and loaded["iteration"] == 1

        # Приватные ключи не сериализуются
        st2 = {"task": "t", "_private": "secret", "files": [], "feedbacks": {}}
        save_state(p, st2)
        loaded2 = load_state(p)
        assert "_private" not in loaded2


def test_update_requirements():
    from state import update_requirements
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "src"
        src.mkdir()
        (src / "requirements.txt").write_text("requests\nflask\n", encoding="utf-8")
        update_requirements(src, "flask", "flask==2.3.0")
        content = (src / "requirements.txt").read_text()
        assert "flask==2.3.0" in content and "flask\n" not in content


def test_update_dockerfile():
    from state import update_dockerfile
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "src"
        src.mkdir()
        (src / "Dockerfile").write_text("FROM python:3.12\nRUN pip install requests\n", encoding="utf-8")
        update_dockerfile(src, "apt-get install curl")
        df = (src / "Dockerfile").read_text()
        assert "apt-get install curl" in df
        # Идемпотентность
        update_dockerfile(src, "apt-get install curl")
        assert df.count("apt-get install curl") == 1


# ─────────────────────────────────────────────
# 12. code_context.py
# ─────────────────────────────────────────────

def test_extract_public_api():
    from code_context import extract_public_api
    code = "import os\nclass Foo:\n    pass\ndef bar():\n    pass\n_private = 1\nx = 42\n"
    api = extract_public_api(code)
    assert "import os" in api
    assert "class Foo" in api
    assert "def bar" in api
    assert "x = 42" in api
    assert "_private" not in api


def test_global_context():
    from code_context import get_global_context, build_dependency_order
    with tempfile.TemporaryDirectory() as td:
        src = Path(td)
        (src / "a.py").write_text("import b\ndef fa(): pass\n", encoding="utf-8")
        (src / "b.py").write_text("def fb(): pass\n", encoding="utf-8")

        ctx = get_global_context(src, ["a.py", "b.py"])
        assert "a.py" in ctx and "b.py" in ctx

        ctx_excl = get_global_context(src, ["a.py", "b.py"], exclude="a.py")
        assert "a.py" not in ctx_excl and "b.py" in ctx_excl

        order = build_dependency_order(["a.py", "b.py"], src)
        assert order.index("b.py") < order.index("a.py")


def test_find_failing_file():
    from code_context import find_failing_file
    stderr_py = 'Traceback:\n  File "src/utils.py", line 10\nAttributeError'
    assert find_failing_file(stderr_py, "", ["main.py", "utils.py"]) == "utils.py"

    stderr_ts = "error at (main.ts:5:3)"
    assert find_failing_file("", stderr_ts, ["main.ts", "utils.ts"]) == "main.ts"

    assert find_failing_file("", "", ["a.py"]) == "a.py"
    assert find_failing_file("", "", []) == "main.py"


# ─────────────────────────────────────────────
# 13. supervisor.py
# ─────────────────────────────────────────────

def test_pipeline_context():
    from supervisor import PipelineContext, bump_phase_fail, reset_phase_fail, ctx
    ctx = PipelineContext()
    assert ctx.state is None
    ctx.save_if_bound()  # no-op when unbound, must not raise

    st = {"phase_fail_counts": {}, "phase_total_fails": {}}
    n1 = bump_phase_fail(st, "develop")
    n2 = bump_phase_fail(st, "develop")
    assert n1 == 1 and n2 == 2
    assert st["phase_total_fails"]["develop"] == 2

    reset_phase_fail(st, "develop")
    assert st["phase_fail_counts"]["develop"] == 0
    assert st["phase_total_fails"]["develop"] == 2

    # bind() привязывает state и project_path
    ctx.bind(Path("/tmp/test"), st)
    assert ctx.state is st


# ─────────────────────────────────────────────
# 14. llm.py — async tests with AsyncMock
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ask_agent_returns_dict():
    """ask_agent должен вернуть dict при успешном ответе от _ollama_chat."""
    from llm import ask_agent
    from cache import ThreadSafeCache
    import logging

    logger = logging.getLogger("test")
    cache = ThreadSafeCache({})

    with patch("llm._ollama_chat", new=AsyncMock(return_value=('{"result": "ok"}', "stop"))):
        result = await ask_agent(
            logger, "developer", "test prompt", cache,
            attempt=0, language="python",
        )
    assert result == {"result": "ok"}


@pytest.mark.asyncio
async def test_ask_agent_cache_hit():
    """При cache hit _ollama_chat не должен вызываться."""
    from llm import ask_agent
    from cache import ThreadSafeCache, cache_key
    from log_utils import get_model
    import logging

    logger = logging.getLogger("test")
    cache = ThreadSafeCache({})

    # Кладём в кэш заранее
    model = get_model("business_analyst", 0, randomize=False)
    key = cache_key("business_analyst", model, "cached text", "python")
    cache[key] = {"cached": True}

    mock_chat = AsyncMock()
    with patch("llm._ollama_chat", new=mock_chat):
        result = await ask_agent(
            logger, "business_analyst", "cached text", cache,
            attempt=0, language="python",
        )
    assert result == {"cached": True}
    mock_chat.assert_not_called()


@pytest.mark.asyncio
async def test_ask_agent_raises_llm_error_on_all_retries():
    """Если все попытки провалились — должен подняться LLMError."""
    import httpx
    from llm import ask_agent
    from cache import ThreadSafeCache
    from exceptions import LLMError
    import logging

    logger = logging.getLogger("test")
    cache = ThreadSafeCache({})

    with patch("llm._ollama_chat", new=AsyncMock(
        side_effect=httpx.ReadTimeout("timeout")
    )):
        with pytest.raises(LLMError):
            await ask_agent(
                logger, "developer", "fail prompt", cache,
                attempt=0, max_retries=1,
            )


@pytest.mark.asyncio
async def test_ask_agent_fallback_plain_text():
    """При ошибке json parse — должен сделать retry в plain text mode."""
    from llm import ask_agent
    from cache import ThreadSafeCache
    import logging

    logger = logging.getLogger("test")
    cache = ThreadSafeCache({})

    call_count = 0

    async def mock_ollama_chat(client, model, messages, temp, max_tok, json_mode=False):
        nonlocal call_count
        call_count += 1
        if json_mode:
            # json mode возвращает невалидный json → ValueError в json.loads
            return ("not valid json", "stop")
        # plain text → extract_json_from_text найдёт JSON
        return ('some text {"fallback": true} more text', "stop")

    with patch("llm._ollama_chat", new=mock_ollama_chat):
        result = await ask_agent(
            logger, "developer", "test", cache,
            attempt=0, max_retries=1,
        )
    assert result == {"fallback": True}
    assert call_count == 2


# ─────────────────────────────────────────────
# 15. supervisor.ask_supervisor — async
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ask_supervisor_returns_phase():
    """ask_supervisor должен вернуть dict с next_phase."""
    from supervisor import ask_supervisor
    from cache import ThreadSafeCache
    import logging

    logger = logging.getLogger("test")
    cache = ThreadSafeCache({})
    state = {
        "iteration": 1, "approved_files": [], "files": ["main.py"],
        "e2e_passed": False, "integration_passed": False,
        "tests_passed": False, "document_generated": False,
        "feedbacks": {}, "last_phase": "initial",
        "phase_fail_counts": {}, "phase_total_fails": {},
    }

    with patch("supervisor.ask_agent", new=AsyncMock(return_value={"next_phase": "develop", "reason": "ok"})):
        result = await ask_supervisor(logger, state, cache, False, "python")

    assert result["next_phase"] == "develop"


@pytest.mark.asyncio
async def test_ask_supervisor_fallback_on_llm_error():
    """При LLMError supervisor возвращает fallback dict."""
    from supervisor import ask_supervisor
    from cache import ThreadSafeCache
    from exceptions import LLMError
    import logging

    logger = logging.getLogger("test")
    cache = ThreadSafeCache({})
    state = {
        "iteration": 1, "approved_files": [], "files": ["main.py"],
        "e2e_passed": False, "integration_passed": False,
        "tests_passed": False, "document_generated": False,
        "feedbacks": {}, "last_phase": "initial",
        "phase_fail_counts": {}, "phase_total_fails": {},
    }

    with patch("supervisor.ask_agent", new=AsyncMock(side_effect=LLMError("fail"))):
        result = await ask_supervisor(logger, state, cache, False, "python")

    assert result["next_phase"] == "develop"


# ─────────────────────────────────────────────
# 16. ai_factory._init_project_files
# ─────────────────────────────────────────────

def test_init_project_files_python():
    import ai_factory
    assert callable(ai_factory.main)
    assert callable(ai_factory._init_project_files)

    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        files, ep = ai_factory._init_project_files(
            p, "TestProj", "python",
            ["requests"], ["utils.py"],
            {"architecture": "simple", "files": ["utils.py"]},
            {"project_goal": "test"},
            {"components": []},
            "test task",
        )
        assert ep == "main.py"
        assert "main.py" in files
        assert (p / "src").is_dir()
        assert (p / "src" / "requirements.txt").exists()
        assert (p / "ARCHITECTURE.md").exists()
        assert (p / ".factory" / "artifacts" / "A0_user_intent.md").exists()


def test_init_project_files_typescript():
    import ai_factory
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        files, ep = ai_factory._init_project_files(
            p, "TsProj", "typescript", ["express"], [],
            {"architecture": "ts"}, {}, {}, "ts task",
        )
        assert ep == "main.ts"
        assert (p / "src" / "package.json").exists()


def test_init_project_files_rust():
    import ai_factory
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        files, ep = ai_factory._init_project_files(
            p, "rs_proj", "rust", ["serde"], [],
            {"architecture": "rs"}, {}, {}, "rs task",
        )
        assert ep == "src/main.rs"
        assert (p / "src" / "Cargo.toml").exists()

```

import asyncio
import json
import logging
import re
from pathlib import Path

from config import (
    MAX_FILE_ATTEMPTS, MAX_CUMULATIVE, MAX_TEST_ATTEMPTS, MIN_COVERAGE,
    FACTORY_DIR, LOGS_DIR, SRC_DIR, RUN_TIMEOUT,
    TRUNCATE_FEEDBACK, TRUNCATE_LOG, TRUNCATE_ERROR_MSG,
)

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
from checks import sanitize_llm_code, classify_test_error, diagnose_runtime_error

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
            build_success, _, build_err = await build_docker_image(src_path, image_tag)
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

        rc, stdout, stderr = await run_in_docker(src_path, cmd, RUN_TIMEOUT, language)

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

        # Детерминистская диагностика — попытка решить без LLM
        diag = diagnose_runtime_error(stderr, stdout, state["files"], src_path)
        if diag:
            fix = diag["fix"]
            missing_pkg = diag.get("missing_package", "")
            if diag["file"] and diag["file"] in state["files"]:
                failing_file = diag["file"]
            logger.info(f"🔧 Авто-диагностика (без LLM): {fix[:150]}")
        else:
            # LLM-анализ только если детерминистика не справилась
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
        rc, stdout, stderr = await run_in_docker(src_path, cmd, RUN_TIMEOUT * 2, language)
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

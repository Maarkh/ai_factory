import json
import re
import concurrent.futures
import logging
from pathlib import Path
from typing import Optional

from config import MAX_FILE_ATTEMPTS, MAX_CONTEXT_CHARS, MIN_COVERAGE, FACTORY_DIR, LOGS_DIR, SRC_DIR
from llm import ask_agent
from stats import ModelStats
from json_utils import _to_str, _safe_contract
from lang_utils import LANG_DISPLAY, LANG_EXT, get_execution_command, get_test_command, get_docker_image
from log_utils import get_model, log_runtime_error
from code_context import get_global_context, build_dependency_order, _find_failing_file
from state import _push_feedback, _get_feedback_ctx, update_dependencies, update_dockerfile, update_requirements
from artifacts import update_artifact_a9, save_artifact
from infra import run_in_docker, build_docker_image
from contract import _refresh_api_contract
from cache import ThreadSafeCache


def _review_file(
    logger: logging.Logger,
    cache: ThreadSafeCache,
    current_file: str,
    code: str,
    attempt: int,
    stats: ModelStats,
    randomize: bool = False,
    language: str = "python",
) -> tuple[str, str]:
    rev_model = get_model("reviewer", attempt, randomize=randomize)
    print(f"👀 [{rev_model}] Reviewer проверяет {current_file} ...")
    try:
        result   = ask_agent(logger, "reviewer", f"Файл: {current_file}\nКод:\n{code}",
                             cache, attempt, randomize, language)
        status   = result.get("status", "REJECT")
        feedback = _to_str(result.get("feedback", ""))
        stats.record("reviewer", rev_model, status == "APPROVE")
        return status, feedback
    except Exception as e:
        logger.exception(f"Reviewer упал: {e}")
        stats.record("reviewer", rev_model, False)
        return "REJECT", f"Reviewer упал: {e}"


def do_self_reflect(
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
    print(f"🤔 [{sr_model}] Self-Reflect проверяет {current_file} ...")

    # Контракт для текущего файла из A5
    file_contract = _safe_contract(state).get("file_contracts", {}).get(current_file, [])
    global_imports = _safe_contract(state).get("global_imports", {}).get(current_file, [])

    try:
        ctx = (
            f"Файл: {current_file}\nКод:\n{code}\n\n"
            f"Спецификации (A2):\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
            f"МИНИМАЛЬНЫЙ API контракт A5 (все эти функции ДОЛЖНЫ быть реализованы):\n"
            f"{json.dumps(file_contract, ensure_ascii=False, indent=2)}\n\n"
            f"Ключевые внешние импорты из A5 (могут быть расширены разработчиком — это нормально):\n"
            f"{json.dumps(global_imports, ensure_ascii=False, indent=2)}"
        )
        result   = ask_agent(logger, "self_reflect", ctx, cache, 0, randomize, language)
        status   = result.get("status", "OK")
        feedback = _to_str(result.get("feedback", ""))
        improved = _to_str(result.get("improved_code", "")).strip()

        if status == "NEEDS_IMPROVEMENT" and improved:
            (src_path / current_file).write_text(improved, encoding="utf-8")
            print(f"  → Self-Reflect улучшил код: {feedback[:80]}")

        stats.record("self_reflect", sr_model, status == "OK")
        return status, feedback
    except Exception as e:
        logger.exception(f"Self-Reflect упал: {e}")
        stats.record("self_reflect", sr_model, False)
        return "OK", ""


def phase_validate_architecture(
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
        print(f"🔍 Валидация архитектуры — {label} ...")
        val_ctx = (
            f"Запрос: {task}\n\n"
            f"Спецификация (SA): {sa_text}\n\n"
            f"Предложенная архитектура: {arch_text}\n\n"
            f"Язык: {LANG_DISPLAY.get(language, language)}\n\n"
            f"Задача проверки: {instruction}"
        )
        try:
            val_resp = ask_agent(logger, agent_key, val_ctx, cache, 0, randomize, language)
            if val_resp.get("status") in ("REJECT", "CANNOT_FIX"):
                fb = _to_str(val_resp.get("feedback", val_resp.get("explanation", "")))
                print(f"  ❌ {label} отклонил: {fb[:150]}")
                rejections += 1
                stats.record(agent_key, get_model(agent_key), False)
            else:
                print(f"  ✅ {label} одобрил.")
                stats.record(agent_key, get_model(agent_key), True)
        except Exception as e:
            logger.exception(f"{label} упал: {e}")
            rejections += 1

        if rejections > 1:
            return False

    print("✅ Архитектура прошла многоуровневую валидацию!")
    return True


def phase_develop(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    randomize: bool = False,
) -> list[str]:
    language  = state.get("language", "python")
    src_path  = project_path / SRC_DIR
    order     = build_dependency_order(state["files"], src_path)
    file_attempts: dict[str, int] = state.setdefault("file_attempts", {})
    exhausted_files: list[str] = []

    for current_file in order:
        if current_file in state.get("approved_files", []):
            print(f"⏭️  {current_file} уже одобрен.")
            continue

        attempt = file_attempts.get(current_file, 0)

        if attempt >= MAX_FILE_ATTEMPTS:
            print(f"⚠️  {current_file} исчерпал {MAX_FILE_ATTEMPTS} попыток → эскалация в spec_reviewer.")
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
        file_contract  = _safe_contract(state).get("file_contracts", {}).get(current_file, [])
        global_imports = _safe_contract(state).get("global_imports", {}).get(current_file, [])

        dev_ctx = (
            f"Задача:\n{state['task']}\n\n"
            f"СИСТЕМНЫЕ СПЕЦИФИКАЦИИ (A2):\n"
            f"{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
            f"Файл для написания: `{current_file}`.\n\n"
        )

        # Добавляем A5 если он есть
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
        if global_context:
            dev_ctx += f"ГЛОБАЛЬНЫЙ КОНТЕКСТ (public API других файлов):\n{global_context}\n\n"
        if existing_code:
            max_code_chars = MAX_CONTEXT_CHARS // 2
            if len(existing_code) > max_code_chars:
                existing_code = existing_code[:max_code_chars] + "\n# [... код обрезан ...]"
            dev_ctx += f"ТЕКУЩИЙ КОД `{current_file}`:\n{existing_code}\n\n"
        feedback_ctx = _get_feedback_ctx(state, current_file)
        if feedback_ctx:
            max_feedback_chars = MAX_CONTEXT_CHARS // 3
            if len(feedback_ctx) > max_feedback_chars:
                feedback_ctx = feedback_ctx[:max_feedback_chars] + "\n[... обрезано ...]"
            dev_ctx += feedback_ctx

        dev_model = get_model("developer", attempt, randomize=randomize)
        print(f"💻 [{dev_model}] Разработчик пишет {current_file} (попытка {attempt + 1}/{MAX_FILE_ATTEMPTS}) ...")

        try:
            dev_resp = ask_agent(logger, "developer", dev_ctx, cache, attempt, randomize, language)
            code     = dev_resp.get("code", "").strip()
        except Exception as e:
            logger.exception(f"Developer упал: {e}")
            stats.record("developer", dev_model, False)
            state["feedbacks"][current_file] = f"Агент не вернул код: {e}"
            file_attempts[current_file] = attempt + 1
            continue

        if not code:
            stats.record("developer", dev_model, False)
            state["feedbacks"][current_file] = "Агент вернул пустой код."
            file_attempts[current_file] = attempt + 1
            continue

        file_path.write_text(code, encoding="utf-8")

        # Self-Reflect с проверкой A5
        sr_status, sr_feedback = do_self_reflect(
            logger, cache, src_path, current_file, code, state, stats, randomize
        )
        if sr_status == "NEEDS_IMPROVEMENT":
            # Перечитываем файл — self-reflect мог записать улучшенный код
            code = file_path.read_text(encoding="utf-8")

        # Внешний ревью
        rev_status, rev_feedback = _review_file(
            logger, cache, current_file, code, attempt, stats, randomize, language
        )

        if rev_status == "APPROVE":
            stats.record("developer", dev_model, True)
            print(f"✅ {current_file} одобрен.")
            state.setdefault("approved_files", []).append(current_file)
            state["feedbacks"][current_file] = ""
            state.setdefault("feedback_history", {})[current_file] = []
            file_attempts[current_file] = 0
            # Обновляем A9 (Implementation Logs)
            update_artifact_a9(project_path, current_file, f"Одобрен на попытке {attempt + 1}. Модель: {dev_model}.")
        else:
            stats.record("developer", dev_model, False)
            combined = "\n".join(filter(None, [_to_str(sr_feedback), _to_str(rev_feedback)]))
            print(f"❌ {current_file} отклонён: {combined[:100]}")
            _push_feedback(state, current_file, combined)
            file_attempts[current_file] = attempt + 1


    return exhausted_files


def phase_e2e_review(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    attempt: int = 0,
    randomize: bool = False,
) -> bool:
    print("\n🧐 Parallel E2E-ревью (Architect + QA) ...")
    language = state.get("language", "python")
    src_path = project_path / SRC_DIR
    all_code = get_global_context(src_path, state["files"])

    agents = [("e2e_architect", "Architect"), ("e2e_qa", "QA Lead")]
    result_ok = True
    # Локальный список результатов — модифицируем state только после завершения всех потоков
    rejections: list[tuple[str, str, str]] = []  # (agent_key, target, feedback)
    successes:  list[str]                  = []   # agent_keys

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_map: dict[concurrent.futures.Future, tuple[str, str]] = {
            executor.submit(ask_agent, logger, agent_key, all_code, cache, attempt, randomize, language):
            (agent_key, label)
            for agent_key, label in agents
        }

        done, not_done = concurrent.futures.wait(
            future_map, return_when=concurrent.futures.ALL_COMPLETED
        )

        for future in list(done) + list(not_done):
            agent_key, label = future_map[future]
            model = get_model(agent_key, attempt, randomize)
            if future.cancelled():
                continue
            try:
                resp = future.result()
            except Exception as e:
                logger.exception(f"[{label}] future error: {e}")
                stats.record(agent_key, model, False)
                result_ok = False
                continue

            if resp.get("status") == "REJECT":
                target   = resp.get("target_file", "").strip() or state["files"][0]
                feedback = _to_str(resp.get("feedback", ""))
                print(f"❌ E2E [{label}] REJECT на {target}: {feedback[:120]}")
                stats.record(agent_key, model, False)
                rejections.append((agent_key, target, feedback))
                result_ok = False
            else:
                stats.record(agent_key, model, True)
                successes.append(agent_key)

    # Применяем изменения к state после завершения всех потоков (нет гонки)
    for agent_key, target, feedback in rejections:
        label = dict(agents).get(agent_key, agent_key)
        if target in state.get("approved_files", []):
            state["approved_files"].remove(target)
        state["feedbacks"][target] = f"E2E {label} Reject:\n{feedback}"

    if result_ok:
        print("✅ Parallel E2E-ревью пройдено!")
    return result_ok


def phase_integration_test(
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
    dockerfile  = src_path / "Dockerfile"    # Dockerfile теперь в src/
    use_custom  = dockerfile.exists()
    image_tag   = f"{project_path.name}:latest" if use_custom else get_docker_image(language)

    # ── Сборка образа ────────────────────────────────────────────────────────
    build_success = False
    for build_attempt in range(1, 4):
        if use_custom:
            print(f"\n🏗️ Сборка Docker-образа (попытка {build_attempt}/3) ...")
            build_success, _, build_err = build_docker_image(src_path, image_tag)
            if build_success:
                print("✅ Образ собран.")
                break
            print(f"❌ Ошибка сборки:\n{build_err[:400]}")
            try:
                devops_ctx  = (
                    f"Ошибка сборки Docker:\n{build_err}\n\n"
                    f"Текущий Dockerfile:\n{dockerfile.read_text(encoding='utf-8')}"
                )
                devops_resp = ask_agent(logger, "devops_runtime", devops_ctx, cache, 0, randomize, language)
                stats.record("devops_runtime", get_model("devops_runtime"), True)
                patch = devops_resp.get("dockerfile_patch", "")
                if devops_resp.get("status") == "FIX_PROPOSED" and isinstance(patch, str) and patch.strip():
                    update_dockerfile(src_path, patch)
                    print("  → Dockerfile обновлён, пересобираю.")
            except Exception as e:
                logger.exception(f"DevOps (build) упал: {e}")
                stats.record("devops_runtime", get_model("devops_runtime"), False)
        else:
            build_success = True
            break

    if not build_success:
        state["feedbacks"][state["files"][0]] = "Не удалось собрать Docker-образ."
        return False

    # ── Запуск приложения ────────────────────────────────────────────────────
    from config import RUN_TIMEOUT
    for run_attempt in range(1, 6):
        print(f"\n🚀 Запуск в Docker (попытка {run_attempt}/5) ...")
        cmd = get_execution_command(language, entry_point)

        env_fixes = state.get("env_fixes", {})
        if env_fixes.get("system_packages"):
            cmd = "apt-get update -q && apt-get install -y " + " ".join(env_fixes["system_packages"]) + " && " + cmd
        if language == "python":
            for orig, alt in env_fixes.get("pip_alternatives", {}).items():
                update_requirements(src_path, orig, alt)

        rc, stdout, stderr = run_in_docker(src_path, cmd, RUN_TIMEOUT, language)

        # Логи рантайма — в .factory/logs/
        logs_dir = project_path / FACTORY_DIR / LOGS_DIR
        logs_dir.mkdir(parents=True, exist_ok=True)
        (logs_dir / "test.log").write_text(
            f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}", encoding="utf-8"
        )
        print("\n--- STDOUT ---\n", stdout[:2000])
        print("\n--- STDERR ---\n", stderr[:2000])

        if rc == 0:
            print("\n✅ Приложение завершилось успешно!")
            state["env_fixes"] = {}
            return True

        print("\n💥 Ошибка выполнения!")
        log_runtime_error(project_path, stderr)

        failing_file = _find_failing_file(stderr, stdout, state["files"])

        if any(kw in stderr.lower() for kw in ["lib", ".so", "cannot open shared object", "no such file"]):
            print("🛠️  DevOps анализирует ошибку окружения ...")
            try:
                devops_ctx  = (
                    f"Traceback:\n{stderr}\n\n"
                    f"Dockerfile: {dockerfile.read_text(encoding='utf-8') if dockerfile.exists() else 'Нет'}"
                )
                devops_resp = ask_agent(logger, "devops_runtime", devops_ctx, cache, 0, randomize, language)
                stats.record("devops_runtime", get_model("devops_runtime"), True)
                if devops_resp.get("status") == "FIX_PROPOSED":
                    if devops_resp.get("dockerfile_patch"):
                        update_dockerfile(src_path, devops_resp["dockerfile_patch"])
                        print("  → Dockerfile обновлён, требуется пересборка.")
                        return False
                    state["env_fixes"] = devops_resp
                    continue
            except Exception as e:
                logger.exception(f"DevOps (runtime) упал: {e}")
                stats.record("devops_runtime", get_model("devops_runtime"), False)

        qa_model = get_model("qa_runtime", run_attempt - 1, randomize)
        fix         = "Смотри traceback."
        missing_pkg = ""
        try:
            qa_resp     = ask_agent(
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
        except Exception as e:
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
                    print(f"⚠️  '{pkg_clean}' уже в requirements, но всё равно падает → возврат разработчику.")
                    state["feedbacks"][failing_file] = (
                        f"ПРОГРАММА УПАЛА. Пакет '{pkg_clean}' установлен, но код падает. "
                        f"Проблема в логике или импортах.\nTraceback:\n{stderr}"
                    )
                    if failing_file in state.get("approved_files", []):
                        state["approved_files"].remove(failing_file)
                    return False
                else:
                    print(f"🔧 Добавляю пакет: {missing_pkg}")
                    update_dependencies(src_path, language, missing_pkg)
                    continue
            elif language == "typescript":
                print(f"🔧 Добавляю пакет в package.json: {missing_pkg}")
                update_dependencies(src_path, language, missing_pkg)
                continue

        if failing_file in state.get("approved_files", []):
            state["approved_files"].remove(failing_file)
        state["feedbacks"][failing_file] = f"ПРОГРАММА УПАЛА.\nTRACEBACK:\n{stderr}\nQA:\n{fix}"
        print("🔄 Возврат к разработчику.")
        return False

    return False


def phase_unit_tests(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    randomize: bool = False,
) -> bool:
    print("\n🧪 Генерация unit-тестов ...")
    language = state.get("language", "python")
    src_path = project_path / SRC_DIR
    all_code = get_global_context(src_path, state["files"])

    # Передаём A7 (Test Plan) если есть
    test_plan = state.get("test_plan", {})

    tg_model = get_model("test_generator", 0, randomize)
    try:
        test_resp  = ask_agent(
            logger, "test_generator",
            f"Спецификации (A2):\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}"
            f"\n\nAPI Контракт (A5):\n{json.dumps(_safe_contract(state), ensure_ascii=False, indent=2)}"
            f"\n\nТест-план (A7):\n{json.dumps(test_plan, ensure_ascii=False, indent=2)}"
            f"\n\nКод проекта:\n{all_code}",
            cache, 0, randomize, language,
        )
        test_files = test_resp.get("test_files", [])
        stats.record("test_generator", tg_model, True)
    except Exception as e:
        print(f"⚠️  Не удалось сгенерировать тесты: {e}. Пропускаю.")
        stats.record("test_generator", tg_model, False)
        return True

    if not test_files:
        return True

    tests_dir = src_path / "tests"
    tests_dir.mkdir(exist_ok=True)
    if language == "python":
        (tests_dir / "__init__.py").write_text("", encoding="utf-8")

    for tf in test_files:
        if code := tf.get("code", ""):
            (tests_dir / tf.get("filename", f"test_generated.{LANG_EXT.get(language, 'py')}")).write_text(
                code, encoding="utf-8"
            )

    print("🚀 Запуск тестов в Docker ...")
    from config import RUN_TIMEOUT
    cmd = get_test_command(language)
    rc, stdout, stderr = run_in_docker(src_path, cmd, RUN_TIMEOUT * 2, language)

    # Логи покрытия — в .factory/logs/
    logs_dir = project_path / FACTORY_DIR / LOGS_DIR
    (logs_dir / "coverage.log").write_text(stdout + "\n" + stderr, encoding="utf-8")

    if rc != 0:
        print("❌ Тесты провалены!")
        failing_file = _find_failing_file(stderr, stdout, state["files"])
        state["feedbacks"][failing_file] = f"UNIT-ТЕСТЫ УПАЛИ:\n{stderr[-2000:]}\n\nВывод:\n{stdout[-1000:]}"
        if failing_file in state.get("approved_files", []):
            state["approved_files"].remove(failing_file)
        return False

    m        = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", stdout)
    coverage = int(m.group(1)) if m else 100

    if coverage < MIN_COVERAGE:
        print(f"❌ Покрытие {coverage}% < {MIN_COVERAGE}%")
        entry = state.get("entry_point", "main.py")
        state["feedbacks"][entry] = (
            f"Покрытие {coverage}% < порога {MIN_COVERAGE}%. "
            "Добавь публичные функции с понятными сигнатурами."
        )
        if entry in state.get("approved_files", []):
            state["approved_files"].remove(entry)
        return False

    print(f"✅ Тесты пройдены! Покрытие: {coverage}%")
    return True


def phase_document(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    randomize: bool = False,
) -> None:
    print("📝 Генерация README.md (A10) ...")
    language = state.get("language", "python")
    try:
        resp = ask_agent(
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
        print("✅ README.md сгенерирован (A10 сохранён).")
    except Exception as e:
        print(f"⚠️  Documenter не справился: {e}")


def revise_spec(
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
    print("\n🔁 Пересмотр спецификации (каскад A2 → A5) ...")
    language = state.get("language", "python")
    ctx = (
        f"Запрос заказчика:\n{state['task']}\n\n"
        f"Текущая спецификация (A2):\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
        f"Проблема:\n{problem}"
    )
    try:
        new_specs      = ask_agent(logger, "spec_reviewer", ctx, cache, 0, randomize, language)
        change_summary = new_specs.get("change_summary", "нет описания")
        # Извлекаем только ожидаемые ключи спецификации
        state["system_specs"] = {
            "data_models":     new_specs.get("data_models", state.get("system_specs", {}).get("data_models", [])),
            "components":      new_specs.get("components", state.get("system_specs", {}).get("components", [])),
            "business_rules":  new_specs.get("business_rules", state.get("system_specs", {}).get("business_rules", [])),
            "external_systems": new_specs.get("external_systems", state.get("system_specs", {}).get("external_systems", [])),
        }

        # Сохраняем обновлённый A2
        save_artifact(project_path, "A2", state["system_specs"])

        # Каскад: пересчитываем A5
        from stats import ModelStats as _ModelStats
        _refresh_api_contract(logger, project_path, state, cache,
                              stats or _ModelStats(project_path), randomize)

        # Определяем, какие файлы затронуты новым контрактом
        from json_utils import _safe_contract as _sc
        new_contracts     = _sc(state).get("file_contracts", {})
        previously_approved = list(state.get("approved_files", []))
        affected_files = []
        for fname in previously_approved:
            # Если контракт файла изменился — сбрасываем его
            old_contract = state.get("_prev_file_contracts", {}).get(fname)
            new_contract = new_contracts.get(fname)
            if old_contract != new_contract:
                affected_files.append(fname)

        # Если нет информации о предыдущем контракте — сбрасываем всё (безопасно)
        if not state.get("_prev_file_contracts"):
            affected_files = previously_approved

        for fname in affected_files:
            if fname in state.get("approved_files", []):
                state["approved_files"].remove(fname)
            state["feedbacks"][fname] = "Спецификация обновлена, требуется переписать файл."
            state["file_attempts"][fname] = 0

        # Запоминаем текущий контракт для следующего сравнения
        state["_prev_file_contracts"] = new_contracts

        state["env_fixes"]          = {}
        state["phase_fail_counts"]  = {}
        state["e2e_passed"]         = False
        state["integration_passed"] = False
        state["tests_passed"]       = False
        state["document_generated"] = False

        print(f"✅ Спецификация обновлена (A2): {change_summary}")
        if affected_files:
            print(f"ℹ️  Сброшены затронутые файлы: {', '.join(affected_files)}")
        unchanged = [f for f in previously_approved if f not in affected_files]
        if unchanged:
            print(f"✅ Незатронутые файлы сохранены: {', '.join(unchanged)}")

        state.setdefault("spec_history", []).append({
            "iteration":      state["iteration"],
            "problem":        problem,
            "change":         change_summary,
            "reset_files":    affected_files,
            "kept_files":     unchanged,
        })

        # Обновляем ARCHITECTURE.md (в корне — видно в Git)
        arch_path = project_path / "ARCHITECTURE.md"
        arch_md   = arch_path.read_text(encoding="utf-8") if arch_path.exists() else ""
        arch_md  += (
            f"\n\n## Обновление спецификации (итерация {state['iteration']})\n"
            f"**Причина:** {problem}\n**Изменение:** {change_summary}\n"
            f"**Сброшены файлы:** {', '.join(affected_files) or 'нет'}\n\n"
            f"```json\n{json.dumps(state['system_specs'], ensure_ascii=False, indent=2)}\n```"
        )
        arch_path.write_text(arch_md, encoding="utf-8")

    except Exception as e:
        print(f"⚠️  Не удалось обновить спецификацию: {e}")

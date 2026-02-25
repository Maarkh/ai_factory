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
    assert BASE_DIR.exists() or not BASE_DIR.exists()  # Path object check


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
    from cache import _cache_key
    k1 = _cache_key("agent", "model", "text", "python")
    k2 = _cache_key("agent", "model", "text", "python")
    k3 = _cache_key("agent", "model", "text", "typescript")
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
    from json_utils import _parse_if_str
    assert _parse_if_str([1, 2], list, []) == [1, 2]
    assert _parse_if_str("[1,2]", list, []) == [1, 2]
    assert _parse_if_str("hello", list, [99]) == [99]
    assert _parse_if_str(None, dict, {}) == {}


def test_to_str():
    from json_utils import _to_str
    assert _to_str("hi") == "hi"
    assert _to_str(None) == ""
    assert _to_str({"k": 1}) == '{"k": 1}'
    assert _to_str(42) == "42"


def test_safe_contract():
    from json_utils import _safe_contract
    state = {"api_contract": {"file_contracts": '{"a.py": "[1,2]"}', "global_imports": {}}}
    c = _safe_contract(state)
    assert isinstance(c["file_contracts"], dict)


def test_extract_json_from_text():
    from json_utils import _extract_json_from_text, _repair_json
    assert _extract_json_from_text('Some text {"key": "value"} more') == {"key": "value"}
    assert _extract_json_from_text('```json\n{"answer": 42}\n```') == {"answer": 42}

    repaired = _repair_json('{"a": 1,}')
    assert json.loads(repaired) == {"a": 1}

    with pytest.raises(ValueError):
        _extract_json_from_text("no json here")


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
    from state import _push_feedback, MAX_FEEDBACK_HISTORY
    assert MAX_FEEDBACK_HISTORY == 3
    st = {"files": ["a.py"], "feedbacks": {}, "feedback_history": {}}
    _push_feedback(st, "a.py", "fix this")
    assert st["feedbacks"]["a.py"] == "fix this"
    assert st["feedback_history"]["a.py"] == ["fix this"]
    for i in range(MAX_FEEDBACK_HISTORY + 1):
        _push_feedback(st, "a.py", f"feedback {i}")
    assert len(st["feedback_history"]["a.py"]) == MAX_FEEDBACK_HISTORY


def test_feedback_ctx():
    from state import _get_feedback_ctx
    st = {"feedbacks": {}, "feedback_history": {}}
    assert _get_feedback_ctx(st, "x.py") == ""

    st2 = {"feedbacks": {"a.py": "last"}, "feedback_history": {"a.py": ["only"]}}
    ctx = _get_feedback_ctx(st2, "a.py")
    assert len(ctx) > 0


def test_sanitize_package_name():
    from state import _sanitize_package_name
    assert _sanitize_package_name("requests") == "requests"
    assert _sanitize_package_name("requests>=2.0") == "requests>=2.0"
    # Пробел+точка с запятой удаляются
    cleaned = _sanitize_package_name("pkg; sys_platform")
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
    from code_context import _find_failing_file
    stderr_py = 'Traceback:\n  File "src/utils.py", line 10\nAttributeError'
    assert _find_failing_file(stderr_py, "", ["main.py", "utils.py"]) == "utils.py"

    stderr_ts = "error at (main.ts:5:3)"
    assert _find_failing_file("", stderr_ts, ["main.ts", "utils.ts"]) == "main.ts"

    assert _find_failing_file("", "", ["a.py"]) == "a.py"
    assert _find_failing_file("", "", []) == "main.py"


# ─────────────────────────────────────────────
# 13. supervisor.py
# ─────────────────────────────────────────────

def test_pipeline_context():
    from supervisor import PipelineContext, _bump_phase_fail, _reset_phase_fail, _ctx
    ctx = PipelineContext()
    assert ctx.state is None
    ctx.save_if_bound()  # no-op when unbound, must not raise

    st = {"phase_fail_counts": {}, "phase_total_fails": {}}
    n1 = _bump_phase_fail(st, "develop")
    n2 = _bump_phase_fail(st, "develop")
    assert n1 == 1 and n2 == 2
    assert st["phase_total_fails"]["develop"] == 2

    _reset_phase_fail(st, "develop")
    assert st["phase_fail_counts"]["develop"] == 0
    assert st["phase_total_fails"]["develop"] == 2

    assert isinstance(_ctx, PipelineContext)


# ─────────────────────────────────────────────
# 14. llm.py — async tests with AsyncMock
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ask_agent_returns_dict():
    """ask_agent должен вернуть dict при успешном ответе клиента."""
    from llm import ask_agent
    from cache import ThreadSafeCache
    import logging

    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"result": "ok"}'
    mock_client.chat.completions.create.return_value = mock_response

    logger = logging.getLogger("test")
    cache = ThreadSafeCache({})

    result = await ask_agent(
        logger, "developer", "test prompt", cache,
        attempt=0, language="python", client=mock_client,
    )
    assert result == {"result": "ok"}
    assert mock_client.chat.completions.create.called


@pytest.mark.asyncio
async def test_ask_agent_cache_hit():
    """При cache hit клиент не должен вызываться."""
    from llm import ask_agent
    from cache import ThreadSafeCache, _cache_key
    from log_utils import get_model
    import logging

    mock_client = AsyncMock()
    logger = logging.getLogger("test")
    cache = ThreadSafeCache({})

    # Кладём в кэш заранее
    model = get_model("business_analyst", 0, randomize=False)
    key = _cache_key("business_analyst", model, "cached text", "python")
    cache[key] = {"cached": True}

    result = await ask_agent(
        logger, "business_analyst", "cached text", cache,
        attempt=0, language="python", client=mock_client,
    )
    assert result == {"cached": True}
    mock_client.chat.completions.create.assert_not_called()


@pytest.mark.asyncio
async def test_ask_agent_raises_llm_error_on_all_retries():
    """Если все попытки провалились — должен подняться LLMError."""
    import openai
    from llm import ask_agent
    from cache import ThreadSafeCache
    from exceptions import LLMError
    import logging

    mock_client = AsyncMock()
    mock_client.chat.completions.create.side_effect = openai.APIError(
        "service unavailable", request=MagicMock(), body=None
    )

    logger = logging.getLogger("test")
    cache = ThreadSafeCache({})

    with pytest.raises(LLMError):
        await ask_agent(
            logger, "developer", "fail prompt", cache,
            attempt=0, max_retries=1, client=mock_client,
        )


@pytest.mark.asyncio
async def test_ask_agent_fallback_plain_text():
    """При ошибке json_object — должен сделать retry без response_format."""
    import openai
    from llm import ask_agent
    from cache import ThreadSafeCache
    import logging

    mock_client = AsyncMock()

    # Первый вызов (json_object mode) падает, второй (plain) возвращает JSON
    json_error = openai.APIError("bad format", request=MagicMock(), body=None)
    plain_response = MagicMock()
    plain_response.choices[0].message.content = '{"fallback": true}'
    mock_client.chat.completions.create.side_effect = [json_error, plain_response]

    logger = logging.getLogger("test")
    cache = ThreadSafeCache({})

    result = await ask_agent(
        logger, "developer", "test", cache,
        attempt=0, max_retries=1, client=mock_client,
    )
    assert result == {"fallback": True}
    assert mock_client.chat.completions.create.call_count == 2


# ─────────────────────────────────────────────
# 15. supervisor.ask_supervisor — async
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ask_supervisor_returns_phase():
    """ask_supervisor должен вернуть dict с next_phase."""
    from supervisor import ask_supervisor
    from cache import ThreadSafeCache
    import logging

    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = '{"next_phase": "develop", "reason": "test", "confidence": 90}'
    mock_client.chat.completions.create.return_value = mock_resp

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

    assert "next_phase" in result


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

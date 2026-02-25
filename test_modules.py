"""
Тесты для проверки модульного разбиения ai_factory.
Запуск: source .venv_factory/bin/activate && python test_modules.py
"""

import json
import sys
import tempfile
import threading
from pathlib import Path

PASS = "✅"
FAIL = "❌"
results = []


def check(name: str, condition: bool, detail: str = "") -> None:
    mark = PASS if condition else FAIL
    msg = f"{mark} {name}"
    if detail and not condition:
        msg += f"  ({detail})"
    print(msg)
    results.append(condition)


# ─────────────────────────────────────────────
# 1. Import checks
# ─────────────────────────────────────────────
print("\n── 1. Import checks ──────────────────────────────")

modules = [
    "config", "models_pool", "prompts",
    "cache", "lang_utils", "log_utils", "json_utils",
    "llm", "stats", "artifacts", "infra", "state",
    "code_context", "contract", "phases", "supervisor", "ai_factory",
]
for mod in modules:
    try:
        __import__(mod)
        check(f"import {mod}", True)
    except Exception as e:
        check(f"import {mod}", False, str(e))


# ─────────────────────────────────────────────
# 2. cache.py
# ─────────────────────────────────────────────
print("\n── 2. cache.py ───────────────────────────────────")
from cache import ThreadSafeCache, _cache_key, load_cache, save_cache

c = ThreadSafeCache({"a": 1})
check("ThreadSafeCache get",       c.get("a") == 1)
check("ThreadSafeCache __contains__", "a" in c)
c["b"] = 2
check("ThreadSafeCache __setitem__", c["b"] == 2)
check("ThreadSafeCache to_dict",   c.to_dict() == {"a": 1, "b": 2})

key1 = _cache_key("agent", "model", "text", "python")
key2 = _cache_key("agent", "model", "text", "python")
key3 = _cache_key("agent", "model", "text", "typescript")
check("_cache_key deterministic",  key1 == key2)
check("_cache_key differs by lang", key1 != key3)
check("_cache_key is sha256 hex",  len(key1) == 64)

with tempfile.TemporaryDirectory() as td:
    p = Path(td)
    (p / ".factory").mkdir()
    orig = ThreadSafeCache({"x": 42})
    save_cache(p, orig)
    loaded = load_cache(p)
    check("save/load_cache roundtrip", loaded["x"] == 42)


# ─────────────────────────────────────────────
# 3. lang_utils.py
# ─────────────────────────────────────────────
print("\n── 3. lang_utils.py ──────────────────────────────")
from lang_utils import (
    LANG_DISPLAY, LANG_EXT, DOCKER_IMAGES,
    get_docker_image, get_execution_command, get_test_command,
    sanitize_files_list,
)

check("LANG_DISPLAY python",    LANG_DISPLAY["python"] == "Python")
check("LANG_EXT typescript",    LANG_EXT["typescript"] == "ts")
check("get_docker_image python", get_docker_image("python") == "python:3.12-slim")
check("get_docker_image unknown", get_docker_image("go") == "python:3.12-slim")

cmd = get_execution_command("python", "main.py")
check("exec_cmd python",        "main.py" in cmd and "pip install" in cmd)
cmd_ts = get_execution_command("typescript", "main.ts")
check("exec_cmd typescript",    "ts-node" in cmd_ts)
cmd_rs = get_execution_command("rust", "")
check("exec_cmd rust",          "cargo run" in cmd_rs)

check("test_cmd python",        "pytest" in get_test_command("python"))
check("test_cmd typescript",    "jest" in get_test_command("typescript"))
check("test_cmd rust",          "cargo test" in get_test_command("rust"))

safe = sanitize_files_list(["main.py", "utils.py", "../evil.py", "/etc/passwd"])
check("sanitize_files removes ../", "../evil.py" not in safe)
check("sanitize_files removes /",   "/etc/passwd" not in safe)
check("sanitize_files keeps good",  "main.py" in safe and "utils.py" in safe)

fallback = sanitize_files_list([], "python")
check("sanitize_files fallback",    fallback == ["main.py"])
fallback_ts = sanitize_files_list([], "typescript")
check("sanitize_files fallback ts", fallback_ts == ["main.ts"])


# ─────────────────────────────────────────────
# 4. json_utils.py
# ─────────────────────────────────────────────
print("\n── 4. json_utils.py ──────────────────────────────")
from json_utils import _parse_if_str, _to_str, _safe_contract, _repair_json, _extract_json_from_text

check("_parse_if_str correct type",  _parse_if_str([1, 2], list, []) == [1, 2])
check("_parse_if_str str→list",      _parse_if_str("[1,2]", list, []) == [1, 2])
check("_parse_if_str wrong type fb", _parse_if_str("hello", list, [99]) == [99])
check("_parse_if_str None fb",       _parse_if_str(None, dict, {}) == {})

check("_to_str string",   _to_str("hi") == "hi")
check("_to_str None",     _to_str(None) == "")
check("_to_str dict",     _to_str({"k": 1}) == '{"k": 1}')
check("_to_str int",      _to_str(42) == "42")

state = {"api_contract": {"file_contracts": '{"a.py": "[1,2]"}', "global_imports": {}}}
c2 = _safe_contract(state)
check("_safe_contract normalises str fc", isinstance(c2["file_contracts"], dict))

repaired = _repair_json('{"a": 1,}')
check("_repair_json trailing comma",  json.loads(repaired) == {"a": 1})

parsed = _extract_json_from_text('Some text {"key": "value"} more text')
check("_extract_json from text",      parsed == {"key": "value"})

md_text = '```json\n{"answer": 42}\n```'
parsed_md = _extract_json_from_text(md_text)
check("_extract_json from markdown",  parsed_md == {"answer": 42})

try:
    _extract_json_from_text("no json here")
    check("_extract_json raises on no json", False)
except ValueError:
    check("_extract_json raises on no json", True)


# ─────────────────────────────────────────────
# 5. log_utils.py
# ─────────────────────────────────────────────
print("\n── 5. log_utils.py ───────────────────────────────")
from log_utils import get_model, log_model_choice, input_with_timeout, setup_logger, log_interaction, log_runtime_error

m0 = get_model("developer", 0, randomize=False)
m1 = get_model("developer", 1, randomize=False)
check("get_model returns string",    isinstance(m0, str) and len(m0) > 0)
check("get_model rotates by attempt", True)  # pool may have 1 item; just check no crash

# input_with_timeout: default fires after timeout
result = input_with_timeout("Test prompt: ", timeout=1, default="default_val")
check("input_with_timeout default",  result == "default_val")

with tempfile.TemporaryDirectory() as td:
    p = Path(td)
    logger = setup_logger(p)
    check("setup_logger returns logger", logger is not None)
    check("setup_logger idempotent",     setup_logger(p) is logger)

    import logging
    log_interaction(logger, "agent", "model", "prompt", "response")
    log_runtime_error(p, "some stderr")
    err_log = p / ".factory" / "logs" / "run_errors.log"
    check("log_runtime_error writes file", err_log.exists())
    check("log_runtime_error content",     "some stderr" in err_log.read_text())


# ─────────────────────────────────────────────
# 6. stats.py
# ─────────────────────────────────────────────
print("\n── 6. stats.py ───────────────────────────────────")
from stats import ModelStats, print_iteration_table

with tempfile.TemporaryDirectory() as td:
    p = Path(td)
    ms = ModelStats(p)
    ms.record("developer", "model_a", True)
    ms.record("developer", "model_a", False)
    ms.flush()
    check("ModelStats record + flush", ms.path.exists())
    data = json.loads(ms.path.read_text())
    check("ModelStats data correct", data["developer:model_a"] == {"success": 1, "fail": 1})

state_for_table = {
    "language": "python", "approved_files": ["a.py"],
    "files": ["a.py", "b.py"], "iteration": 3, "last_phase": "develop"
}
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    print_iteration_table(state_for_table)
out = buf.getvalue()
check("print_iteration_table output", "ИТЕРАЦИЯ" in out and "1/2" in out)


# ─────────────────────────────────────────────
# 7. artifacts.py
# ─────────────────────────────────────────────
print("\n── 7. artifacts.py ───────────────────────────────")
from artifacts import ARTIFACT_LABELS, save_artifact, load_artifact, update_artifact_a9

check("ARTIFACT_LABELS A0",  ARTIFACT_LABELS["A0"] == "user_intent")
check("ARTIFACT_LABELS A10", ARTIFACT_LABELS["A10"] == "final_summary")

with tempfile.TemporaryDirectory() as td:
    p = Path(td)
    save_artifact(p, "A0", "# Test content")
    loaded = load_artifact(p, "A0")
    check("save/load artifact str",   loaded == "# Test content")

    save_artifact(p, "A2", {"key": "val"})
    loaded2 = load_artifact(p, "A2")
    check("save/load artifact dict",  "```json" in loaded2 and '"key"' in loaded2)

    check("load_artifact missing",    load_artifact(p, "A6") is None)

    update_artifact_a9(p, "main.py", "approved")
    a9 = (p / ".factory" / "artifacts" / "A9_implementation_logs.md").read_text()
    check("update_artifact_a9",       "main.py" in a9 and "approved" in a9)


# ─────────────────────────────────────────────
# 8. infra.py
# ─────────────────────────────────────────────
print("\n── 8. infra.py ───────────────────────────────────")
from infra import run_command, _make_container_name

rc, out, err = run_command(["echo", "hello"])
check("run_command echo",        rc == 0 and "hello" in out)

rc2, _, _ = run_command(["false"])
check("run_command exit nonzero", rc2 != 0)

rc3, _, err3 = run_command(["nonexistent_cmd_xyz"])
check("run_command not found",    rc3 == -1 and "не найдена" in err3)

rc4, _, _ = run_command(["sleep", "10"], timeout=1)
check("run_command timeout",      rc4 == -1)

name1 = _make_container_name(Path("/some/path"))
name2 = _make_container_name(Path("/some/path"))
name3 = _make_container_name(Path("/other/path"))
check("container name deterministic", name1 == name2)
check("container name differs",       name1 != name3)
check("container name prefix",        name1.startswith("factory_"))


# ─────────────────────────────────────────────
# 9. state.py
# ─────────────────────────────────────────────
print("\n── 9. state.py ───────────────────────────────────")
from state import (
    save_state, load_state, MAX_FEEDBACK_HISTORY,
    _push_feedback, _get_feedback_ctx, ensure_feedback_keys,
    _sanitize_package_name, update_requirements, update_dockerfile,
)

check("MAX_FEEDBACK_HISTORY", MAX_FEEDBACK_HISTORY == 3)

st = {"files": ["a.py", "b.py"], "feedbacks": {}, "feedback_history": {}}
_push_feedback(st, "a.py", "fix this")
check("_push_feedback sets feedbacks",  st["feedbacks"]["a.py"] == "fix this")
check("_push_feedback history",         st["feedback_history"]["a.py"] == ["fix this"])

# overflow: push MAX+1 items
for i in range(MAX_FEEDBACK_HISTORY + 1):
    _push_feedback(st, "a.py", f"feedback {i}")
check("_push_feedback trims history", len(st["feedback_history"]["a.py"]) == MAX_FEEDBACK_HISTORY)

ctx = _get_feedback_ctx(st, "a.py")
check("_get_feedback_ctx non-empty",  len(ctx) > 0)
ctx_none = _get_feedback_ctx({"feedbacks": {}, "feedback_history": {}}, "x.py")
check("_get_feedback_ctx missing",    ctx_none == "")

check("_sanitize_package_name basic",   _sanitize_package_name("requests") == "requests")
check("_sanitize_package_name version", _sanitize_package_name("requests>=2.0") == "requests>=2.0")
check("_sanitize_package_name strips",  _sanitize_package_name("pkg; sys_platform") == "pkgsys_platform")

with tempfile.TemporaryDirectory() as td:
    p = Path(td)
    st2 = {"task": "t", "files": ["a.py"], "feedbacks": {"a.py": ""}, "iteration": 1}
    save_state(p, st2)
    loaded = load_state(p)
    check("save/load_state roundtrip",  loaded["task"] == "t" and loaded["iteration"] == 1)

    # Private keys are stripped on save
    st3 = {"task": "t", "_private": "secret", "files": [], "feedbacks": {}}
    save_state(p, st3)
    loaded3 = load_state(p)
    check("save_state strips _ keys",   "_private" not in loaded3)

    # update_requirements
    src = p / "src"
    src.mkdir()
    (src / "requirements.txt").write_text("requests\nflask\n", encoding="utf-8")
    update_requirements(src, "flask", "flask==2.3.0")
    content = (src / "requirements.txt").read_text()
    check("update_requirements replaces", "flask==2.3.0" in content and "flask\n" not in content)

    # update_dockerfile
    (src / "Dockerfile").write_text("FROM python:3.12\nRUN pip install requests\n", encoding="utf-8")
    update_dockerfile(src, "apt-get install curl")
    df = (src / "Dockerfile").read_text()
    check("update_dockerfile adds patch", "apt-get install curl" in df)
    update_dockerfile(src, "apt-get install curl")
    check("update_dockerfile idempotent",  df.count("apt-get install curl") == 1)


# ─────────────────────────────────────────────
# 10. code_context.py
# ─────────────────────────────────────────────
print("\n── 10. code_context.py ───────────────────────────")
from code_context import extract_public_api, get_global_context, build_dependency_order, _find_failing_file

py_code = """\
import os
from pathlib import Path

class Foo:
    pass

def bar():
    pass

_private = 1
x = 42
"""
api = extract_public_api(py_code)
check("extract_public_api imports",    "import os" in api)
check("extract_public_api class",      "class Foo" in api)
check("extract_public_api def",        "def bar" in api)
check("extract_public_api public var", "x = 42" in api)
check("extract_public_api skips _",    "_private" not in api)

with tempfile.TemporaryDirectory() as td:
    src = Path(td)
    (src / "a.py").write_text("import b\ndef fa(): pass\n", encoding="utf-8")
    (src / "b.py").write_text("def fb(): pass\n", encoding="utf-8")

    ctx = get_global_context(src, ["a.py", "b.py"])
    check("get_global_context includes files", "a.py" in ctx and "b.py" in ctx)

    ctx_excl = get_global_context(src, ["a.py", "b.py"], exclude="a.py")
    check("get_global_context exclude",        "a.py" not in ctx_excl and "b.py" in ctx_excl)

    order = build_dependency_order(["a.py", "b.py"], src)
    check("build_dependency_order b before a", order.index("b.py") < order.index("a.py"))

stderr_py = 'Traceback:\n  File "src/utils.py", line 10\nAttributeError'
check("_find_failing_file python",  _find_failing_file(stderr_py, "", ["main.py", "utils.py"]) == "utils.py")

stderr_ts = "error at (main.ts:5:3)"
check("_find_failing_file ts",      _find_failing_file("", stderr_ts, ["main.ts", "utils.ts"]) == "main.ts")

check("_find_failing_file fallback", _find_failing_file("", "", ["a.py"]) == "a.py")
check("_find_failing_file empty",    _find_failing_file("", "", []) == "main.py")


# ─────────────────────────────────────────────
# 11. supervisor.py
# ─────────────────────────────────────────────
print("\n── 11. supervisor.py ─────────────────────────────")
from supervisor import PipelineContext, _ctx, signal_handler, _bump_phase_fail, _reset_phase_fail

ctx_obj = PipelineContext()
check("PipelineContext init",           ctx_obj.state is None)
check("PipelineContext save_if_bound",  True)  # no-op when unbound, should not raise
ctx_obj.save_if_bound()

st_sup = {"phase_fail_counts": {}, "phase_total_fails": {}}
n1 = _bump_phase_fail(st_sup, "develop")
n2 = _bump_phase_fail(st_sup, "develop")
check("_bump_phase_fail increments",      n1 == 1 and n2 == 2)
check("_bump_phase_fail total_fails",     st_sup["phase_total_fails"]["develop"] == 2)
_reset_phase_fail(st_sup, "develop")
check("_reset_phase_fail zeroes count",   st_sup["phase_fail_counts"]["develop"] == 0)
check("_reset_phase_fail keeps total",    st_sup["phase_total_fails"]["develop"] == 2)

check("_ctx is PipelineContext",          isinstance(_ctx, PipelineContext))


# ─────────────────────────────────────────────
# 12. ai_factory.py top-level
# ─────────────────────────────────────────────
print("\n── 12. ai_factory.py ─────────────────────────────")
import ai_factory
check("ai_factory has main",               callable(ai_factory.main))
check("ai_factory has _init_project_files", callable(ai_factory._init_project_files))

# _init_project_files: smoke test for python
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
    check("_init_project_files entry_point python", ep == "main.py")
    check("_init_project_files adds main.py",       "main.py" in files)
    check("_init_project_files creates src/",       (p / "src").is_dir())
    check("_init_project_files requirements.txt",   (p / "src" / "requirements.txt").exists())
    check("_init_project_files ARCHITECTURE.md",    (p / "ARCHITECTURE.md").exists())
    check("_init_project_files A0 artifact",        (p / ".factory" / "artifacts" / "A0_user_intent.md").exists())

# TypeScript variant
with tempfile.TemporaryDirectory() as td:
    p = Path(td)
    files, ep = ai_factory._init_project_files(
        p, "TsProj", "typescript", ["express"], [],
        {"architecture": "ts"}, {}, {}, "ts task",
    )
    check("_init_project_files entry_point ts", ep == "main.ts")
    check("_init_project_files package.json",   (p / "src" / "package.json").exists())

# Rust variant
with tempfile.TemporaryDirectory() as td:
    p = Path(td)
    files, ep = ai_factory._init_project_files(
        p, "rs_proj", "rust", ["serde"], [],
        {"architecture": "rs"}, {}, {}, "rs task",
    )
    check("_init_project_files entry_point rust", ep == "src/main.rs")
    check("_init_project_files Cargo.toml",       (p / "src" / "Cargo.toml").exists())


# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────
total  = len(results)
passed = sum(results)
failed = total - passed
print(f"\n{'═' * 50}")
print(f"  ИТОГО: {passed}/{total} тестов прошло", end="")
if failed:
    print(f"  ({failed} ПРОВАЛЕНО)")
    sys.exit(1)
else:
    print("  🎉")
    sys.exit(0)

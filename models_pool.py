import os

# ── Пулы моделей по роли ─────────────────────────────────────────────────────
# Переопределяются через .env: FACTORY_MODEL_<AGENT>=model_name
# Пример: FACTORY_MODEL_DEVELOPER=qwen3:latest
# DEFAULT_MODEL — fallback если модель не задана ни в пуле, ни в .env

DEFAULT_MODEL = os.getenv("FACTORY_DEFAULT_MODEL", "deepseek-coder:6.7b")

_BASE_POOLS: dict[str, list[str]] = {
    "developer":        ["deepseek-coder:6.7b"],
    "developer_patch":  ["deepseek-coder:6.7b"],
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

# Применяем переопределения моделей из .env
MODEL_POOLS: dict[str, list[str]] = {}
for _agent, _default_pool in _BASE_POOLS.items():
    _env_key = f"FACTORY_MODEL_{_agent.upper()}"
    _env_val = os.getenv(_env_key, "").strip()
    if _env_val:
        MODEL_POOLS[_agent] = [_env_val]
    else:
        MODEL_POOLS[_agent] = _default_pool

# ── Маппинг агент → бэкенд ───────────────────────────────────────────────────
# FACTORY_BACKEND_<AGENT>=<backend_name>  (default: "local")
# Пример: FACTORY_BACKEND_DEVELOPER=remote
AGENT_BACKENDS: dict[str, str] = {}
for _agent in _BASE_POOLS:
    _env_key = f"FACTORY_BACKEND_{_agent.upper()}"
    _env_val = os.getenv(_env_key, "").strip()
    if _env_val:
        AGENT_BACKENDS[_agent] = _env_val.lower()

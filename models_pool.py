"""
Конфигурация моделей для каждого агента.

Чтобы переключить агента на другой сервер или модель —
просто отредактируй соответствующую запись в MODEL_POOLS.
"""

from config import LLM_BASE_URL, LLM_API_KEY, LLM_TIMEOUT, LLM_MAX_TOKENS, LLM_NUM_CTX

# Значения по умолчанию (из .env / config.py) — чтобы не дублировать в каждой записи
_D = {
    "url": LLM_BASE_URL,
    "key": LLM_API_KEY,
    "timeout": LLM_TIMEOUT,
    "max_tokens": LLM_MAX_TOKENS,
    "num_ctx": LLM_NUM_CTX,
}


def _local(model: str) -> dict:
    """Локальная модель с дефолтными параметрами."""
    return {"model": model, **_D}


def _remote(model: str, url: str, key: str = "ollama",
            timeout: float = 0, max_tokens: int = 0, num_ctx: int = 0) -> dict:
    """Удалённая модель с кастомными параметрами."""
    return {
        "model": model,
        "url": url,
        "key": key,
        "timeout": timeout or _D["timeout"],
        "max_tokens": max_tokens or _D["max_tokens"],
        "num_ctx": num_ctx or _D["num_ctx"],
    }


# ── Пулы моделей по роли ─────────────────────────────────────────────────────
# Каждая запись: {model, url, key, timeout, max_tokens, num_ctx}
#
# Примеры:
#   _local("deepseek-coder:6.7b")           — локальный Ollama
#   _local("qwen3:latest")                   — локальный Ollama, другая модель
#   _remote("qwen3:32b",                     — удалённый сервер
#           url="http://work-server:11434/v1/",
#           key="secret", timeout=600,
#           max_tokens=32768, num_ctx=32768)

MODEL_POOLS: dict[str, list[dict]] = {
    "developer":             [_local("deepseek-coder:6.7b")],
    "developer_patch":       [_local("deepseek-coder:6.7b")],
    "reviewer":              [_local("deepseek-coder:6.7b")],
    "e2e_architect":         [_local("qwen3:latest")],
    "e2e_qa":                [_local("qwen3:latest")],
    "qa_runtime":            [_local("deepseek-coder:6.7b")],
    "business_analyst":      [_local("qwen3:latest")],
    "system_analyst":        [_local("deepseek-coder:6.7b")],
    "architect":             [_local("deepseek-coder:6.7b")],
    "spec_reviewer":         [_local("qwen3:latest")],
    "test_generator":        [_local("deepseek-coder:6.7b")],
    "documenter":            [_local("qwen3:latest")],
    "devops_runtime":        [_local("qwen3:latest")],
    "arch_validator":        [_local("deepseek-coder:6.7b")],
    "supervisor":            [_local("qwen3:latest")],
    "self_reflect":          [_local("deepseek-coder:6.7b")],
    "contract_analyst":      [_local("deepseek-coder:6.7b")],
    "a5_validator":          [_local("deepseek-coder:6.7b")],
    "a5_business_reviewer":  [_local("qwen3:latest")],
    "a5_architect_reviewer": [_local("qwen3:latest")],
    "a5_contract_reviewer":  [_local("deepseek-coder:6.7b")],
}

# Конфиг по умолчанию (для неизвестных агентов)
DEFAULT_CONFIG: dict = _local("deepseek-coder:6.7b")

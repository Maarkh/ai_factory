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


def _local(model: str, **overrides) -> dict:
    """Локальная модель с дефолтными параметрами."""
    return {"model": model, **_D, **overrides}


def _remote(model: str, url: str, key: str = "ollama",
            timeout: float = 0, max_tokens: int = 0, num_ctx: int = 0,
            api: str = "auto") -> dict:
    """Удалённая модель с кастомными параметрами.

    api: "auto" — определяется по URL (/v1 → openai, иначе ollama),
         "openai" — принудительно OpenAI-compatible,
         "ollama" — принудительно Ollama native.
    """
    return {
        "model": model,
        "url": url,
        "key": key,
        "timeout": timeout or _D["timeout"],
        "max_tokens": max_tokens or _D["max_tokens"],
        "num_ctx": num_ctx or _D["num_ctx"],
        "api": api,
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

MODEL_POOL_local: dict[str, list[dict]] = {
#MODEL_POOLS: dict[str, list[dict]] = {
    # Код / патчи — deepseek-coder (быстрый, целиком в VRAM)
    "developer":             [_local("deepseek-coder:6.7b")],
    "developer_patch":       [_local("deepseek-coder:6.7b")],
    "reviewer":              [_local("deepseek-coder:6.7b")],
    "test_generator":        [_local("deepseek-coder:6.7b")],
    "self_reflect":          [_local("deepseek-coder:6.7b")],
    "qa_runtime":            [_local("deepseek-coder:6.7b")],
    # JSON-генерация / валидация — deepseek-coder (скорость критична)
    "contract_analyst":      [_local("deepseek-coder:6.7b")],
    "a5_validator":          [_local("deepseek-coder:6.7b")],
    "a5_business_reviewer":  [_local("deepseek-coder:6.7b")],
    "a5_architect_reviewer": [_local("deepseek-coder:6.7b")],
    "a5_contract_reviewer":  [_local("deepseek-coder:6.7b")],
    "arch_validator":        [_local("deepseek-coder:6.7b")],
    "devops_runtime":        [_local("deepseek-coder:6.7b")],
    # Рассуждение / понимание — qwen3 (лучше для анализа задач)
    "business_analyst":      [_local("qwen3:latest")],
    "system_analyst":        [_local("qwen3:latest")],
    "architect":             [_local("qwen3:latest")],
    "spec_reviewer":         [_local("qwen3:latest")],
    "supervisor":            [_local("qwen3:latest")],
    "e2e_architect":         [_local("qwen3:latest")],
    "e2e_qa":                [_local("qwen3:latest")],
    "documenter":            [_local("qwen3:latest")],
}
#MODEL_POOLS_works: dict[str, list[dict]] = {
MODEL_POOLS: dict[str, list[dict]] = {
    # Код / патчи — deepseek-coder (быстрый, целиком в VRAM)
    "developer":             [_remote("qwen3-coder-30b-a3b-instruct-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "developer_patch":       [_remote("qwen3-coder-30b-a3b-instruct-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "reviewer":              [_remote("qwen3-coder-30b-a3b-instruct-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "test_generator":        [_remote("qwen3-coder-30b-a3b-instruct-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "self_reflect":          [_remote("qwen3-coder-30b-a3b-instruct-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "qa_runtime":            [_remote("qwen3-coder-30b-a3b-instruct-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    # JSON-генерация / валидация — deepseek-coder (скорость критична)
    "contract_analyst":      [_remote("qwen3-coder-30b-a3b-instruct-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "a5_validator":          [_remote("qwen3-coder-30b-a3b-instruct-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "a5_business_reviewer":  [_remote("qwen3-coder-30b-a3b-instruct-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "a5_architect_reviewer": [_remote("qwen3-coder-30b-a3b-instruct-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "a5_contract_reviewer":  [_remote("qwen3-coder-30b-a3b-instruct-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "arch_validator":        [_remote("qwen3-coder-30b-a3b-instruct-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "devops_runtime":        [_remote("qwen3-coder-30b-a3b-instruct-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    # Рассуждение / понимание — qwen3 (лучше для анализа задач)
    "business_analyst":      [_remote("qwen3-32b-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "system_analyst":        [_remote("qwen3-32b-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "architect":             [_remote("qwen3-32b-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "spec_reviewer":         [_remote("qwen3-32b-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "supervisor":            [_remote("qwen3-32b-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "e2e_architect":         [_remote("qwen3-32b-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "e2e_qa":                [_remote("qwen3-32b-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
    "documenter":            [_remote("qwen3-32b-fp8",url="https://ai-mlops.russianpost.ru/v1",key="gpustack_637ff66f84deff05_401f764d059e39ce24a2182b3acb2ccb",timeout=600, max_tokens=24000, num_ctx=31955)],
}


# Конфиг по умолчанию (для неизвестных агентов)
DEFAULT_CONFIG: dict = _local("deepseek-coder:6.7b")

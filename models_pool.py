"""
Конфигурация моделей для каждого агента.

Профили запуска:
  python ai_factory.py --local            — локальный Ollama (по умолчанию)
  python ai_factory.py --cloud work       — рабочий GPUstack сервер
  python ai_factory.py --cloud groq       — Groq (бесплатно, rate limited)
  python ai_factory.py --cloud openrouter — OpenRouter (бесплатные модели)
  python ai_factory.py --cloud siliconflow — SiliconFlow
  python ai_factory.py --cloud together   — Together AI

API ключи задаются в .env (GROQ_API_KEY, OPENROUTER_API_KEY и т.д.)
"""

import os

from config import LLM_BASE_URL, LLM_API_KEY, LLM_TIMEOUT, LLM_MAX_TOKENS, LLM_NUM_CTX

# Значения по умолчанию (из .env / config.py)
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
    """Удалённая модель с кастомными параметрами."""
    return {
        "model": model,
        "url": url,
        "key": key,
        "timeout": timeout or _D["timeout"],
        "max_tokens": max_tokens or _D["max_tokens"],
        "num_ctx": num_ctx or _D["num_ctx"],
        "api": api,
    }


# ── Пресеты облачных провайдеров ──────────────────────────────────────────────

def _openrouter(model: str, **kw) -> dict:
    return _remote(model, url="https://openrouter.ai/api/v1",
                   key=os.environ.get("OPENROUTER_API_KEY", ""),
                   timeout=kw.get("timeout", 300), max_tokens=kw.get("max_tokens", 16384),
                   num_ctx=kw.get("num_ctx", 32768))

def _groq(model: str, **kw) -> dict:
    return _remote(model, url="https://api.groq.com/openai/v1",
                   key=os.environ.get("GROQ_API_KEY", ""),
                   timeout=kw.get("timeout", 120), max_tokens=kw.get("max_tokens", 8192),
                   num_ctx=kw.get("num_ctx", 32768))

def _siliconflow(model: str, **kw) -> dict:
    return _remote(model, url="https://api.siliconflow.cn/v1",
                   key=os.environ.get("SILICONFLOW_API_KEY", ""),
                   timeout=kw.get("timeout", 300), max_tokens=kw.get("max_tokens", 16384),
                   num_ctx=kw.get("num_ctx", 32768))

def _together(model: str, **kw) -> dict:
    return _remote(model, url="https://api.together.xyz/v1",
                   key=os.environ.get("TOGETHER_API_KEY", ""),
                   timeout=kw.get("timeout", 300), max_tokens=kw.get("max_tokens", 16384),
                   num_ctx=kw.get("num_ctx", 32768))

def _work(model: str, **kw) -> dict:
    return _remote(model, url="https://ai-mlops.russianpost.ru/v1",
                   key=os.environ.get("WORK_API_KEY", ""),
                   timeout=kw.get("timeout", 600),
                   max_tokens=kw.get("max_tokens", 24000),
                   num_ctx=kw.get("num_ctx", 31955))


# ── Группы агентов ────────────────────────────────────────────────────────────

_CODE_AGENTS = [
    "developer", "developer_patch", "reviewer", "test_generator",
    "self_reflect", "qa_runtime",
]
_JSON_AGENTS = [
    "contract_analyst", "a5_validator", "a5_business_reviewer",
    "a5_architect_reviewer", "a5_contract_reviewer", "arch_validator",
    "devops_runtime",
]
_REASON_AGENTS = [
    "business_analyst", "system_analyst", "architect", "spec_reviewer",
    "supervisor", "e2e_architect", "e2e_qa", "documenter",
]


def _fill(code_cfg: dict, json_cfg: dict, reason_cfg: dict) -> dict[str, list[dict]]:
    """Заполняет пул для всех агентов тремя конфигурациями."""
    pool: dict[str, list[dict]] = {}
    for a in _CODE_AGENTS:
        pool[a] = [code_cfg]
    for a in _JSON_AGENTS:
        pool[a] = [json_cfg]
    for a in _REASON_AGENTS:
        pool[a] = [reason_cfg]
    return pool


# ══════════════════════════════════════════════════════════════════════════════
# ПРОФИЛИ
# ══════════════════════════════════════════════════════════════════════════════

PROFILES: dict[str, dict[str, list[dict]]] = {}

# ── local: домашний Ollama ────────────────────────────────────────────────────
PROFILES["local"] = _fill(
    code_cfg   = _local("deepseek-coder:6.7b"),
    json_cfg   = _local("deepseek-coder:6.7b"),
    reason_cfg = _local("qwen3:latest"),
)

# ── work: рабочий GPUstack (.env: WORK_API_KEY) ─────────────────────────────
PROFILES["work"] = _fill(
    code_cfg   = _work("qwen3-coder-30b-a3b-instruct-fp8", max_tokens=32000),
    json_cfg   = _work("qwen3-coder-30b-a3b-instruct-fp8", max_tokens=32000),
    reason_cfg = _work("qwen3-32b-fp8"),
)

# ── groq: Groq Cloud (.env: GROQ_API_KEY) ───────────────────────────────────
PROFILES["groq"] = _fill(
    code_cfg   = _groq("qwen-qwq-32b"),
    json_cfg   = _groq("qwen-qwq-32b"),
    reason_cfg = _groq("qwen-qwq-32b"),
)

# ── openrouter: OpenRouter (.env: OPENROUTER_API_KEY) ────────────────────────
PROFILES["openrouter"] = _fill(
    code_cfg   = _openrouter("qwen/qwen3-32b:free"),
    json_cfg   = _openrouter("qwen/qwen3-32b:free"),
    reason_cfg = _openrouter("qwen/qwen3-32b:free"),
)

# ── siliconflow: SiliconFlow (.env: SILICONFLOW_API_KEY) ────────────────────
PROFILES["siliconflow"] = _fill(
    code_cfg   = _siliconflow("Qwen/Qwen2.5-Coder-32B-Instruct"),
    json_cfg   = _siliconflow("Qwen/Qwen2.5-Coder-32B-Instruct"),
    reason_cfg = _siliconflow("Qwen/Qwen2.5-72B-Instruct"),
)

# ── together: Together AI (.env: TOGETHER_API_KEY) ──────────────────────────
PROFILES["together"] = _fill(
    code_cfg   = _together("Qwen/Qwen2.5-Coder-32B-Instruct"),
    json_cfg   = _together("Qwen/Qwen2.5-Coder-32B-Instruct"),
    reason_cfg = _together("Qwen/Qwen2.5-72B-Instruct-Turbo"),
)


# ══════════════════════════════════════════════════════════════════════════════
# Активный пул (переключается через set_profile)
# ══════════════════════════════════════════════════════════════════════════════

MODEL_POOLS: dict[str, list[dict]] = dict(PROFILES["local"])

DEFAULT_CONFIG: dict = _local("deepseep-coder:6.7b")


def set_profile(name: str) -> None:
    """Переключает MODEL_POOLS на указанный профиль."""
    if name not in PROFILES:
        available = ", ".join(sorted(PROFILES.keys()))
        raise ValueError(f"Неизвестный профиль '{name}'. Доступные: {available}")
    MODEL_POOLS.clear()
    MODEL_POOLS.update(PROFILES[name])


def get_profile_names() -> list[str]:
    """Возвращает список доступных профилей."""
    return sorted(PROFILES.keys())

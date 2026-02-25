import json
import logging
import time
from typing import Optional

from openai import OpenAI

from config import CACHEABLE_AGENTS
from cache import ThreadSafeCache, _cache_key
from log_utils import get_model, log_model_choice, log_interaction
from json_utils import _extract_json_from_text
from lang_utils import get_system_prompt

CLIENT = OpenAI(base_url="http://localhost:11434/v1/", api_key="ollama", timeout=120.0)

AGENT_TEMPERATURES: dict[str, float] = {
    "developer":        0.1,
    "architect":        0.0,
    "system_analyst":   0.2,
    "business_analyst": 0.3,
    "reviewer":         0.0,
    "e2e_architect":    0.0,
    "e2e_qa":           0.0,
    "qa_runtime":       0.2,
    "spec_reviewer":    0.0,
    "test_generator":   0.2,
    "documenter":       0.3,
    "devops_runtime":   0.1,
    "arch_validator":   0.0,
    "supervisor":       0.2,
    "self_reflect":     0.0,
    "contract_analyst": 0.0,
}


def ask_agent(
    logger: logging.Logger,
    agent: str,
    user_text: str,
    cache: ThreadSafeCache,
    attempt: int = 0,
    randomize: bool = False,
    language: str = "python",
    max_retries: int = 3,
) -> dict:
    model = get_model(agent, attempt, randomize=randomize)
    log_model_choice(logger, agent, model, attempt)

    if agent in CACHEABLE_AGENTS and attempt == 0:
        key = _cache_key(agent, model, user_text, language)
        if key in cache:
            logger.info(f"[{agent}:{model}] Cache hit")
            return cache[key]

    sys_prompt  = get_system_prompt(agent, language)
    temperature = AGENT_TEMPERATURES.get(agent, 0.2)

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user",   "content": user_text},
    ]

    last_exc: Exception = RuntimeError("Нет попыток")
    for retry in range(max_retries):
        if retry > 0:
            delay = 2 ** retry
            logger.info(f"[{agent}:{model}] Backoff {delay}с (retry={retry})")
            time.sleep(delay)
        raw: Optional[str] = None
        try:
            response = CLIENT.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            raw    = response.choices[0].message.content
            result = json.loads(raw)
            log_interaction(logger, agent, model, sys_prompt + "\n\n" + user_text, raw or "")
            if agent in CACHEABLE_AGENTS and attempt == 0:
                cache[_cache_key(agent, model, user_text, language)] = result
            return result
        except Exception as e:
            last_exc = e
            logger.warning(f"[{agent}:{model}] json_object failed: {e}, пробую plain text...")
            try:
                response = CLIENT.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                )
                raw    = response.choices[0].message.content
                result = _extract_json_from_text(raw)
                log_interaction(logger, agent, model, sys_prompt + "\n\n" + user_text, raw or "")
                if agent in CACHEABLE_AGENTS and attempt == 0:
                    cache[_cache_key(agent, model, user_text, language)] = result
                return result
            except Exception as e2:
                last_exc = e2
                logger.warning(f"[{agent}:{model}] plain text fallback failed: {e2}")

    raise RuntimeError(f"[{agent}:{model}] все попытки исчерпаны") from last_exc

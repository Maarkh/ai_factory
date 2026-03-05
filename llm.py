import asyncio
import json
import logging
from typing import Optional

import openai
from openai import AsyncOpenAI

from config import CACHEABLE_AGENTS, LLM_BASE_URL, LLM_API_KEY, LLM_TIMEOUT, LLM_MAX_TOKENS, LLM_NUM_CTX
from cache import ThreadSafeCache, _cache_key
from exceptions import LLMError
from log_utils import get_model, log_model_choice, log_interaction
from json_utils import _extract_json_from_text
from lang_utils import get_system_prompt

CLIENT = AsyncOpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY, timeout=LLM_TIMEOUT)

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


async def ask_agent(
    logger: logging.Logger,
    agent: str,
    user_text: str,
    cache: ThreadSafeCache,
    attempt: int = 0,
    randomize: bool = False,
    language: str = "python",
    max_retries: int = 3,
    client: Optional[AsyncOpenAI] = None,
) -> dict:
    _client = client or CLIENT
    model = get_model(agent, attempt, randomize=randomize)
    log_model_choice(logger, agent, model, attempt)

    cache_key = _cache_key(agent, model, user_text, language) if agent in CACHEABLE_AGENTS and attempt == 0 else None

    if cache_key is not None:
        if cache_key in cache:
            logger.info(f"[{agent}:{model}] Cache hit")
            return cache[cache_key]

    sys_prompt  = get_system_prompt(agent, language)
    temperature = AGENT_TEMPERATURES.get(agent, 0.2)

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user",   "content": user_text},
    ]

    last_exc: Exception = LLMError("Нет попыток")
    for retry in range(max_retries):
        if retry > 0:
            delay = 2 ** retry
            logger.info(f"[{agent}:{model}] Backoff {delay}с (retry={retry})")
            await asyncio.sleep(delay)
        raw: str | None = None
        try:
            response = await _client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=LLM_MAX_TOKENS,
                response_format={"type": "json_object"},
                extra_body={"num_ctx": LLM_NUM_CTX},
            )
            if not response.choices or response.choices[0].message.content is None:
                raise LLMError(f"[{agent}:{model}] пустой ответ от LLM (json_object)")
            if response.choices[0].finish_reason == "length":
                logger.warning(f"[{agent}:{model}] ⚠️ ответ обрезан (finish_reason=length, max_tokens={LLM_MAX_TOKENS})")
            raw    = response.choices[0].message.content
            result = json.loads(raw)
            if not isinstance(result, dict) or not result:
                raise ValueError(f"Ожидался непустой dict, получен {type(result).__name__} (len={len(result) if isinstance(result, dict) else 'N/A'})")
            log_interaction(logger, agent, model, sys_prompt + "\n\n" + user_text, raw or "")
            if cache_key is not None:
                cache[cache_key] = result
            return result
        except (openai.APIError, json.JSONDecodeError, ValueError) as e:
            last_exc = e
            logger.warning(f"[{agent}:{model}] json_object failed: {e}, пробую plain text...")
            try:
                response = await _client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=LLM_MAX_TOKENS,
                    extra_body={"num_ctx": LLM_NUM_CTX},
                )
                if not response.choices or response.choices[0].message.content is None:
                    raise LLMError(f"[{agent}:{model}] пустой ответ от LLM (plain)")
                if response.choices[0].finish_reason == "length":
                    logger.warning(f"[{agent}:{model}] ⚠️ ответ обрезан (finish_reason=length)")
                raw    = response.choices[0].message.content
                result = _extract_json_from_text(raw)
                if not isinstance(result, dict) or not result:
                    raise ValueError(f"Ожидался непустой dict, получен {type(result).__name__}")
                log_interaction(logger, agent, model, sys_prompt + "\n\n" + user_text, raw or "")
                if cache_key is not None:
                    cache[cache_key] = result
                return result
            except (openai.APIError, json.JSONDecodeError, ValueError) as e2:
                last_exc = e2
                logger.warning(f"[{agent}:{model}] plain text fallback failed: {e2}")

    raise LLMError(f"[{agent}:{model}] все попытки исчерпаны") from last_exc

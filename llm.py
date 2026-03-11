import asyncio
import json
import logging
import re
from typing import Protocol, runtime_checkable

import httpx

from config import CACHEABLE_AGENTS, LLM_BASE_URL, LLM_API_KEY, LLM_TIMEOUT, LLM_MAX_TOKENS, LLM_NUM_CTX, MAX_LLM_RETRIES
from cache import ThreadSafeCache, cache_key
from exceptions import LLMError
from log_utils import get_model, log_model_choice, log_interaction
from json_utils import extract_json_from_text
from lang_utils import get_system_prompt

# Regex для garbage tokens deepseek-coder (begin_of_sentence и т.п.)
_GARBAGE_TOKEN_RE = re.compile(r"<[｜|][\w▁]+[｜|]>")
_GARBAGE_DEDUP_RE = re.compile(r"(\w+)" + r"<[｜|][\w▁]+[｜|]>" + r"\1")


def _strip_garbage_tokens(text: str) -> str:
    """Убирает garbage tokens LLM (deepseek-coder) из любого текста."""
    text = _GARBAGE_DEDUP_RE.sub(r"\1", text)
    text = _GARBAGE_TOKEN_RE.sub("", text)
    return text


# ── LLM Backend Protocol ─────────────────────────────────────────────────────
# Для смены провайдера (Ollama → OpenAI, Anthropic, litellm) достаточно
# реализовать этот протокол и присвоить экземпляр в _backend.

@runtime_checkable
class LLMBackend(Protocol):
    async def chat(
        self,
        model: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        json_mode: bool = False,
    ) -> tuple[str, str]:
        """Возвращает (content, done_reason). done_reason='length' если обрезано."""
        ...


class OllamaBackend:
    """Ollama native /api/chat streaming backend."""

    def __init__(self, base_url: str, num_ctx: int, overall_timeout: float) -> None:
        ollama_base = base_url.rstrip("/").removesuffix("/v1").removesuffix("/v1/")
        self._chat_url = f"{ollama_base}/api/chat"
        self._num_ctx = num_ctx
        self._overall_timeout = overall_timeout
        # read=120с — только между чанками (stream=True)
        self._http_timeout = httpx.Timeout(connect=30.0, read=120.0, write=30.0, pool=30.0)

    async def chat(
        self,
        model: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        json_mode: bool = False,
    ) -> tuple[str, str]:
        async with httpx.AsyncClient(timeout=self._http_timeout) as client:
            return await asyncio.wait_for(
                self._stream(client, model, messages, temperature, max_tokens, json_mode),
                timeout=self._overall_timeout,
            )

    async def _stream(
        self,
        client: httpx.AsyncClient,
        model: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        json_mode: bool,
    ) -> tuple[str, str]:
        payload: dict = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {
                "num_ctx": self._num_ctx,
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if json_mode:
            payload["format"] = "json"

        content_parts: list[str] = []
        done_reason = "stop"

        async with client.stream("POST", self._chat_url, json=payload) as resp:
            if resp.status_code >= 400:
                body = await resp.aread()
                raise httpx.HTTPStatusError(
                    f"Ollama {resp.status_code}: {body[:500].decode(errors='replace')}",
                    request=resp.request,
                    response=resp,
                )
            async for line in resp.aiter_lines():
                if not line.strip():
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = chunk.get("message", {})
                if msg.get("content"):
                    content_parts.append(msg["content"])
                if chunk.get("done"):
                    done_reason = chunk.get("done_reason", "stop")
                    break

        content = _strip_garbage_tokens("".join(content_parts))
        return content, done_reason


# Бэкенд по умолчанию — Ollama. Для смены:
#   import llm; llm._backend = MyCloudBackend(...)
_backend: LLMBackend = OllamaBackend(LLM_BASE_URL, LLM_NUM_CTX, LLM_TIMEOUT)


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

# Ошибки, после которых имеет смысл retry (сеть, таймаут, формат)
_RETRYABLE_ERRORS = (
    httpx.HTTPStatusError,
    httpx.TimeoutException,
    asyncio.TimeoutError,
    json.JSONDecodeError,
)


async def ask_agent(
    logger: logging.Logger,
    agent: str,
    user_text: str,
    cache: ThreadSafeCache,
    attempt: int = 0,
    randomize: bool = False,
    language: str = "python",
    max_retries: int = MAX_LLM_RETRIES,
) -> dict:
    model = get_model(agent, attempt, randomize=randomize)
    log_model_choice(logger, agent, model, attempt)

    ckey = cache_key(agent, model, user_text, language) if agent in CACHEABLE_AGENTS and attempt == 0 else None

    if ckey is not None:
        if ckey in cache:
            logger.info(f"[{agent}:{model}] Cache hit")
            return cache[ckey]

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
            raw, done_reason = await _backend.chat(
                model, messages, temperature, LLM_MAX_TOKENS, json_mode=True,
            )
            if not raw:
                raise LLMError(f"[{agent}:{model}] пустой ответ от LLM (json)")
            if done_reason == "length":
                logger.warning(f"[{agent}:{model}] ответ обрезан (done_reason=length, num_predict={LLM_MAX_TOKENS})")
            result = json.loads(raw)
            if not isinstance(result, dict) or not result:
                raise json.JSONDecodeError(
                    f"Ожидался непустой dict, получен {type(result).__name__}", raw or "", 0
                )
            log_interaction(logger, agent, model, sys_prompt + "\n\n" + user_text, raw or "")
            if ckey is not None:
                cache[ckey] = result
            return result
        except _RETRYABLE_ERRORS as e:
            last_exc = e
            if isinstance(e, (httpx.TimeoutException, asyncio.TimeoutError)):
                logger.warning(f"[{agent}:{model}] таймаут ({type(e).__name__}), retry {retry+1}/{max_retries}")
                continue  # retry без fallback на plain text
            logger.warning(f"[{agent}:{model}] json_object failed: {e}, пробую plain text...")
            try:
                raw, done_reason = await _backend.chat(
                    model, messages, temperature, LLM_MAX_TOKENS, json_mode=False,
                )
                if not raw:
                    raise LLMError(f"[{agent}:{model}] пустой ответ от LLM (plain)")
                if done_reason == "length":
                    logger.warning(f"[{agent}:{model}] ответ обрезан (done_reason=length)")
                result = extract_json_from_text(raw)
                if not isinstance(result, dict) or not result:
                    raise json.JSONDecodeError(
                        f"Ожидался непустой dict, получен {type(result).__name__}", raw or "", 0
                    )
                log_interaction(logger, agent, model, sys_prompt + "\n\n" + user_text, raw or "")
                if ckey is not None:
                    cache[ckey] = result
                return result
            except _RETRYABLE_ERRORS as e2:
                last_exc = e2
                logger.warning(f"[{agent}:{model}] plain text fallback failed: {e2}")

    raise LLMError(f"[{agent}:{model}] все попытки исчерпаны") from last_exc

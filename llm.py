import asyncio
import json
import logging
import re
from typing import Protocol, runtime_checkable

import httpx

from config import CACHEABLE_AGENTS, MAX_LLM_RETRIES
from cache import ThreadSafeCache, cache_key
from exceptions import LLMError
from log_utils import get_model_config, log_model_choice, log_interaction
from json_utils import extract_json_from_text
from lang_utils import get_system_prompt

# Regex для garbage tokens deepseek-coder (begin_of_sentence и т.п.)
_GARBAGE_TOKEN_RE = re.compile(r"<[｜|][\w▁]+[｜|]>")
_GARBAGE_DEDUP_RE = re.compile(r"(\w+)" + r"<[｜|][\w▁]+[｜|]>" + r"\1")
# <think>...</think> блоки qwen3 reasoning mode
_THINK_TAG_RE = re.compile(r"<think>[\s\S]*?</think>")


def _strip_garbage_tokens(text: str) -> str:
    """Убирает garbage tokens LLM и <think> блоки из текста."""
    text = _THINK_TAG_RE.sub("", text)
    text = _GARBAGE_DEDUP_RE.sub(r"\1", text)
    text = _GARBAGE_TOKEN_RE.sub("", text)
    return text.strip()


# ── LLM Backend Protocol ─────────────────────────────────────────────────────

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

    def __init__(
        self, base_url: str, num_ctx: int, overall_timeout: float,
        api_key: str = "",
    ) -> None:
        ollama_base = base_url.rstrip("/").removesuffix("/v1").removesuffix("/v1/")
        self._chat_url = f"{ollama_base}/api/chat"
        self._num_ctx = num_ctx
        self._overall_timeout = overall_timeout
        self._headers: dict[str, str] = {}
        if api_key and api_key != "ollama":
            self._headers["Authorization"] = f"Bearer {api_key}"
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
        async with httpx.AsyncClient(
            timeout=self._http_timeout, headers=self._headers,
        ) as client:
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


class OpenAIBackend:
    """OpenAI-compatible /v1/chat/completions streaming backend (GPUstack, vLLM и т.п.)."""

    def __init__(
        self, base_url: str, num_ctx: int, overall_timeout: float,
        api_key: str = "",
    ) -> None:
        api_base = base_url.rstrip("/")
        if not api_base.endswith("/v1"):
            api_base += "/v1"
        self._chat_url = f"{api_base}/chat/completions"
        self._num_ctx = num_ctx          # хранится, но не передаётся (сервер задаёт сам)
        self._overall_timeout = overall_timeout
        self._headers: dict[str, str] = {}
        if api_key and api_key != "ollama":
            self._headers["Authorization"] = f"Bearer {api_key}"
        self._http_timeout = httpx.Timeout(connect=30.0, read=120.0, write=30.0, pool=30.0)

    async def chat(
        self,
        model: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        json_mode: bool = False,
    ) -> tuple[str, str]:
        async with httpx.AsyncClient(
            timeout=self._http_timeout, headers=self._headers,
        ) as client:
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
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        content_parts: list[str] = []
        done_reason = "stop"

        async with client.stream("POST", self._chat_url, json=payload) as resp:
            if resp.status_code >= 400:
                body = await resp.aread()
                raise httpx.HTTPStatusError(
                    f"OpenAI {resp.status_code}: {body[:500].decode(errors='replace')}",
                    request=resp.request,
                    response=resp,
                )
            async for line in resp.aiter_lines():
                line = line.strip()
                if not line or line.startswith(":"):
                    continue
                # SSE формат: "data: {...}" или "data:{...}"
                if line.startswith("data: "):
                    data = line[6:]
                elif line.startswith("data:"):
                    data = line[5:]
                else:
                    continue
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    continue
                choices = chunk.get("choices", [])
                if not choices:
                    continue
                delta = choices[0].get("delta", {})
                # content — полезный текст; reasoning_content (qwen3) пропускаем
                if delta.get("content"):
                    content_parts.append(delta["content"])
                finish = choices[0].get("finish_reason")
                if finish == "length":
                    done_reason = "length"

        content = _strip_garbage_tokens("".join(content_parts))
        return content, done_reason


# ── Backend cache ─────────────────────────────────────────────────────────────
# Бэкенды кэшируются по (url, num_ctx, timeout, key, api) — один инстанс на уникальный сервер.

_backend_cache: dict[tuple, LLMBackend] = {}


def _detect_api_type(url: str) -> str:
    """Автоопределение типа API по URL: /v1 → openai, иначе ollama."""
    clean = url.rstrip("/")
    return "openai" if clean.endswith("/v1") else "ollama"


def _get_or_create_backend(config: dict) -> LLMBackend:
    """Возвращает бэкенд для конфига, создаёт если нет в кэше."""
    api_type = config.get("api", "auto")
    if api_type == "auto":
        api_type = _detect_api_type(config["url"])
    cache_key_tuple = (config["url"], config["num_ctx"], config["timeout"], config["key"], api_type)
    backend = _backend_cache.get(cache_key_tuple)
    if backend is None:
        cls = OpenAIBackend if api_type == "openai" else OllamaBackend
        backend = cls(
            base_url=config["url"],
            num_ctx=config["num_ctx"],
            overall_timeout=config["timeout"],
            api_key=config.get("key", ""),
        )
        _backend_cache[cache_key_tuple] = backend
    return backend


AGENT_TEMPERATURES: dict[str, float] = {
    "developer":        0.1,
    "developer_patch":  0.0,
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
    LLMError,
    ValueError,
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
    config = get_model_config(agent, attempt, randomize=randomize)
    model = config["model"]
    max_tokens = config["max_tokens"]
    backend = _get_or_create_backend(config)

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
    server_error = False  # предыдущий retry был 5xx — нужен длинный backoff
    for retry in range(max_retries):
        if retry > 0:
            delay = min(15 * (2 ** (retry - 1)), 60) if server_error else 2 ** retry
            logger.info(f"[{agent}:{model}] Backoff {delay}с (retry={retry})")
            await asyncio.sleep(delay)
        server_error = False
        raw: str | None = None
        try:
            raw, done_reason = await backend.chat(
                model, messages, temperature, max_tokens, json_mode=True,
            )
            if not raw:
                raise LLMError(f"[{agent}:{model}] пустой ответ от LLM (json)")
            if done_reason == "length":
                logger.warning(f"[{agent}:{model}] ответ обрезан (done_reason=length, num_predict={max_tokens})")
            result = json.loads(raw)
            if not isinstance(result, dict) or not result:
                raise json.JSONDecodeError(
                    f"Ожидался непустой dict, получен {type(result).__name__}", raw or "", 0
                )
            # Модели с reasoning mode (falcon3, qwen3) могут вернуть {"think": "..."}
            # без полезных данных. Удаляем ключ think — если dict стал пустой, retry.
            result.pop("think", None)
            if not result:
                raise json.JSONDecodeError(
                    "Ответ содержит только 'think' без полезных данных", raw or "", 0
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
            # 5xx — сервер перегружен/рестартуется, fallback бесполезен, ждём дольше
            if isinstance(e, httpx.HTTPStatusError) and e.response.status_code >= 500:
                server_error = True
                logger.warning(f"[{agent}:{model}] сервер {e.response.status_code}, retry {retry+1}/{max_retries}")
                continue
            logger.warning(f"[{agent}:{model}] json_object failed: {e}, пробую plain text...")
            try:
                raw, done_reason = await backend.chat(
                    model, messages, temperature, max_tokens, json_mode=False,
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
                result.pop("think", None)
                if not result:
                    raise json.JSONDecodeError(
                        "Ответ содержит только 'think' без полезных данных", raw or "", 0
                    )
                log_interaction(logger, agent, model, sys_prompt + "\n\n" + user_text, raw or "")
                if ckey is not None:
                    cache[ckey] = result
                return result
            except _RETRYABLE_ERRORS as e2:
                last_exc = e2
                logger.warning(f"[{agent}:{model}] plain text fallback failed: {e2}")

    raise LLMError(f"[{agent}:{model}] все попытки исчерпаны") from last_exc

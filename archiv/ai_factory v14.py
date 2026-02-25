"""
Мультифайловая Фабрика Агентов v14.0
=====================================
"""

import os
import re
import sys
import json
import time
import random
import logging
import subprocess
import threading
import queue
import hashlib
import signal
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path
from typing import Optional
from openai import OpenAI
from logging.handlers import RotatingFileHandler
import concurrent.futures


# ─────────────────────────────────────────────
# КОНФИГУРАЦИЯ
# ─────────────────────────────────────────────

BASE_DIR        = Path("/media/mikhail/RAD/py_proj")
WAIT_TIMEOUT    = 30
RUN_TIMEOUT     = 6_000
MAX_CONTEXT_CHARS   = 60_000
MIN_COVERAGE        = 40
MAX_ABSOLUTE_ITERS  = 30000,
   
MAX_FILE_ATTEMPTS   = 40    

CLIENT = OpenAI(base_url="http://localhost:11434/v1/", api_key="ollama")

# ── Пулы моделей по роли ─────────────────────────────────────────────────────
MODEL_POOLS: dict[str, list[str]] = {
    "developer":        ["deepseek-coder:latest", "codellama:latest",  "qwen3-coder:latest"],
    "reviewer":         ["qwen3:latest",           "mistral:latest",    "gemma3:latest"],
    "e2e_architect":    ["qwen3:latest",           "mistral:latest"],
    "e2e_qa":           ["qwen3:latest",           "mistral:latest"],
    "qa_runtime":       ["qwen3:latest",           "mistral:latest"],
    "business_analyst": ["qwen3:latest",           "mistral:latest"],
    "system_analyst":   ["qwen3:latest",           "mistral:latest"],
    "architect":        ["qwen3:latest",           "deepseek-coder:latest"],
    "spec_reviewer":    ["qwen3:latest",           "mistral:latest"],
    "test_generator":   ["deepseek-coder:latest",  "qwen3-coder:latest"],
    "documenter":       ["qwen3:latest",           "mistral:latest"],
    "devops_runtime":   ["qwen3:latest",           "mistral:latest"],
    "arch_validator":   ["qwen3:latest",           "mistral:latest"],
    "supervisor":       ["qwen3:latest"],
    "self_reflect":     ["qwen3:latest",           "mistral:latest"],
}

CACHEABLE_AGENTS = {"business_analyst", "system_analyst", "architect", "documenter"}

# ─────────────────────────────────────────────
# СИСТЕМНЫЕ ПРОМПТЫ
# ─────────────────────────────────────────────

PROMPTS: dict[str, str] = {
    "business_analyst": """Ты — Senior Business Analyst.
Цель: проанализировать запрос и составить чёткие бизнес-требования.
Правило KISS: не усложняй, не добавляй функционал, о котором не просили.
Верни СТРОГО JSON:
{
  "project_goal": "Краткая цель (1-2 предложения)",
  "user_stories": ["Как <актор>, я хочу <действие>, чтобы <цель>"],
  "acceptance_criteria": ["Критерий 1", "Критерий 2"]
}""",

    "system_analyst": """Ты — Senior System Analyst.
На основе запроса и бизнес-требований составь техническую спецификацию.
Только реально необходимое. Без конкретных файлов и имён классов.
Верни СТРОГО JSON:
{
  "data_models": [{"name": "Сущность", "fields": ["поле: тип"]}],
  "components": ["компоненты системы"],
  "business_rules": ["ограничения, формулы, правила"]
}""",

    "architect": """Ты — Senior Software Architect.
Спроектируй production-ready архитектуру на основе спецификации и целевого языка.
Укажи все необходимые внешние зависимости в формате целевого языка.
Верни СТРОГО JSON:
{
  "dependencies": ["зависимость1", "зависимость2"],
  "files": ["main.py / main.ts / main.rs и др."],
  "architecture": "Подробное описание: логика, роли файлов, интеграция"
}""",

    "developer": """Ты — Senior {lang} Developer.
Напиши код для указанного файла на языке {lang}.
ГЛОБАЛЬНЫЙ КОНТЕКСТ — это public API других файлов. Твои импорты и имена функций должны ТОЧНО совпадать с ним.
СИСТЕМНЫЕ СПЕЦИФИКАЦИИ — бизнес-логика. Соблюдай её строго.
ПРАВИЛО: Код должен быть полным и рабочим. КАТЕГОРИЧЕСКИ ЗАПРЕЩАЕТСЯ использовать заглушки вида 'pass', '...' или комментарии 'тут будет код'. Реализуй всю логику.
Верни СТРОГО JSON:
{
  "code": "полный рабочий код файла"
}""",

    "reviewer": """Ты — Senior {lang} Code Reviewer.
Проверь файл на SOLID, безопасность, бесконечные циклы, импорты и исключения.
Верни СТРОГО JSON:
{
  "status": "APPROVE" или "REJECT",
  "feedback": "конкретная инструкция что исправить (пустая строка если APPROVE)"
}""",

    "e2e_architect": """Ты — Architect Reviewer (E2E-ревью).
Проверь весь код проекта в сборе: созданы ли все файлы, корректны ли кросс-импорты.
Верни СТРОГО JSON:
{
  "status": "APPROVE_ALL" или "REJECT",
  "target_file": "имя файла с ошибкой (пусто если APPROVE_ALL)",
  "feedback": "что исправить (пусто если APPROVE_ALL)"
}""",

    "e2e_qa": """Ты — QA Lead (E2E-ревью).
Статически проверь проект: конфликты логики, бесконечные циклы в main, обработка ошибок.
Верни СТРОГО JSON:
{
  "status": "APPROVE_ALL" или "REJECT",
  "target_file": "имя файла с ошибкой (пусто если APPROVE_ALL)",
  "feedback": "инструкция по исправлению (пусто если APPROVE_ALL)"
}""",

    "qa_runtime": """Ты — QA Automation Engineer.
Код упал во время выполнения. Тебе передан Traceback.
Проанализируй его и найди причину. Если ошибка в отсутствии библиотеки, определи её точное имя.
Верни СТРОГО JSON:
{
  "file": "файл с ошибкой (пусто если проблема окружения)",
  "line": "номер строки (пусто если неизвестно)",
  "fix": "подробная инструкция: что и где исправить",
  "missing_package": "имя пакета для установки (пусто если пакет не нужен)"
}""",

    "spec_reviewer": """Ты — Senior System Analyst.
Найдено противоречие в спецификации. Обнови её с учётом проблемы.
Верни СТРОГО JSON:
{
  "data_models": [{"name": "Сущность", "fields": ["поле: тип"]}],
  "components": ["обновлённый список"],
  "business_rules": ["обновлённые правила"],
  "change_summary": "что и почему изменилось"
}""",

    "test_generator": """Ты — Senior QA Engineer.
Сгенерируй unit-тесты для языка {lang} по коду и спецификациям.
Покрой ключевые функции и edge-кейсы. Не делай тесты зависимыми от пользовательского ввода (используй mock/patch).
Верни СТРОГО JSON:
{
  "test_files": [{"filename": "test_xxx.{ext}", "code": "код теста"}]
}""",

    "documenter": """Ты — Technical Writer.
Сгенерируй README.md. Разделы: Описание, Установка, Запуск, Модели данных, Архитектура.
Верни СТРОГО JSON:
{
  "readme": "полный текст README.md в markdown"
}""",

    "devops_runtime": """Ты — Senior DevOps / Environment Engineer.
Задача: заставить код работать в Docker.
Проанализируй ошибку (traceback). Определи системные или языковые зависимости.
Верни СТРОГО JSON:
{
  "status": "FIX_PROPOSED" или "NO_FIX_NEEDED" или "CANNOT_FIX",
  "system_packages": ["список apt-пакетов"],
  "pip_alternatives": {"оригинальный_пакет": "правильный_пакет==версия"},
  "dockerfile_patch": "инструкция для Dockerfile, например: RUN apt-get update && apt-get install -y пакет",
  "run_command_mod": "изменённая команда для запуска (если нужно)",
  "explanation": "объяснение причины фикса"
}""",

    "arch_validator": """Ты — Validator архитектуры.
Проверь предложенную архитектуру на соответствие задаче, реализуемость в production,
корректность зависимостей, Docker-совместимость и корректность для целевого языка.
Верни СТРОГО JSON:
{
  "status": "APPROVE" или "REJECT",
  "feedback": "инструкция по исправлению (пустая строка если APPROVE)"
}""",

    "supervisor": """Ты — Agent Supervisor (оркестратор SDLC).
Ты получаешь структурированное состояние проекта и решаешь, какую фазу запустить следующей.

Возможные фазы:
  "develop"          — писать / переписывать файлы
  "e2e_review"       — E2E статический анализ (запускай только когда ВСЕ файлы одобрены)
  "integration_test" — запуск в Docker (только после e2e_passed=true)
  "unit_tests"       — unit-тесты (только после integration_passed=true)
  "document"         — генерация README (только после tests_passed=true)
  "success"          — проект готов (только если document уже сгенерирован)
  "revise_spec"      — пересмотр спецификации (при системных противоречиях)

Правила:
  - Если approved < total — всегда "develop"
  - Никогда не пропускай фазы (нельзя перейти в integration_test без e2e_passed=true)
  - Если одна фаза падает больше 3 раз подряд — предложи "revise_spec"

Верни СТРОГО JSON:
{
  "next_phase": "одна из фаз выше",
  "reason": "краткое обоснование",
  "confidence": 85
}""",

    "self_reflect": """Ты — Senior {lang} Developer в режиме строгой самопроверки (temperature=0.0).
Ты только что написал код. Проверь его максимально строго:
  - Соответствие спецификациям
  - Отсутствие логических багов
  - Идиоматичность для языка {lang}
  - Отсутствие заглушек (pass, ..., TODO)
  - Корректность импортов

Верни СТРОГО JSON:
{
  "status": "OK" или "NEEDS_IMPROVEMENT",
  "feedback": "конкретные замечания (пустая строка если OK)",
  "improved_code": "полный улучшенный код если NEEDS_IMPROVEMENT, иначе пустая строка"
}""",
}


# ─────────────────────────────────────────────
# PIPELINE CONTEXT
# ─────────────────────────────────────────────

class PipelineContext:
    """Заменяет глобальные переменные — устраняет потенциальный race condition."""

    def __init__(self) -> None:
        self.state: Optional[dict] = None
        self.project_path: Optional[Path] = None

    def bind(self, project_path: Path, state: dict) -> None:
        self.project_path = project_path
        self.state = state

    def save_if_bound(self) -> None:
        if self.state is not None and self.project_path is not None:
            try:
                save_state(self.project_path, self.state)
                print("✅ Состояние сохранено.")
            except Exception as e:
                print(f"⚠️  Не удалось сохранить состояние: {e}")


_ctx = PipelineContext()


def signal_handler(sig, frame) -> None:
    print("\n⌛ Ctrl+C — сохраняем состояние...")
    _ctx.save_if_bound()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


# ─────────────────────────────────────────────
# MULTI-LANGUAGE УТИЛИТЫ
# ─────────────────────────────────────────────

LANG_DISPLAY = {"python": "Python", "typescript": "TypeScript", "rust": "Rust"}
LANG_EXT     = {"python": "py",     "typescript": "ts",         "rust": "rs"}

DOCKER_IMAGES = {
    "python":     "python:3.12-slim",
    "typescript": "node:20-slim",
    "rust":       "rust:1.75-slim",
}


def get_docker_image(language: str) -> str:
    return DOCKER_IMAGES.get(language, "python:3.12-slim")


def get_execution_command(language: str, entry_point: str) -> str:
    """TypeScript: явная установка ts-node и typescript."""
    if language == "python":
        return f"pip install -r requirements.txt -q && python {entry_point}"
    elif language == "typescript":
        return (
            "npm install -q && "
            "npm install -g ts-node typescript --quiet && "
            f"npx ts-node {entry_point}"
        )
    elif language == "rust":
        return "cargo run --quiet"
    return f"python {entry_point}"


def get_test_command(language: str) -> str:
    if language == "python":
        return (
            "pip install pytest pytest-cov -q && "
            "pip install -r requirements.txt -q && "
            "pytest tests/ --cov=. --cov-report=term-missing -q"
        )
    elif language == "typescript":
        return "npm install -q && npm install -g ts-jest --quiet && npx jest --coverage"
    elif language == "rust":
        return "cargo test"
    return "pytest tests/ -q"


def get_system_prompt(agent: str, language: str = "python") -> str:
    """Подставляет {lang} и {ext} в промпты."""
    base = PROMPTS[agent]
    lang_name = LANG_DISPLAY.get(language, "Python")
    ext       = LANG_EXT.get(language, "py")
    return base.replace("{lang}", lang_name).replace("{ext}", ext)


def sanitize_files_list(files_raw: list) -> list[str]:
    """Санитизация: только безопасные относительные пути."""
    safe: list[str] = []
    for f in files_raw:
        if not isinstance(f, str):
            continue
        # Разрешены: буквы, цифры, /, -, _, точки; не абсолютный путь, без '..'
        if re.match(r'^[\w/\-\.]+\.\w+$', f) and ".." not in f and not f.startswith("/"):
            safe.append(f)
    return safe if safe else ["main.py"]


# ─────────────────────────────────────────────
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ─────────────────────────────────────────────

def get_model(agent: str, attempt: int = 0, randomize: bool = False) -> str:
    pool = MODEL_POOLS.get(agent, ["qwen3:latest"])
    if randomize:
        return random.choice(pool)
    return pool[attempt % len(pool)]


def log_model_choice(logger: logging.Logger, agent: str, model: str, attempt: int) -> None:
    logger.info(f"[{agent}] attempt={attempt} → model={model}")


def input_with_timeout(prompt: str, timeout: int, default: str) -> str:
    print(prompt, end="", flush=True)
    q: queue.Queue[str] = queue.Queue()

    def _read() -> None:
        try:
            q.put(input().strip())
        except EOFError:
            q.put(default)

    threading.Thread(target=_read, daemon=True).start()
    try:
        return q.get(timeout=timeout)
    except queue.Empty:
        print(f"\n[⏳ Таймаут {timeout}с → автовыбор: '{default}']")
        return default


def setup_logger(project_path: Path) -> logging.Logger:
    logger = logging.getLogger(str(project_path))
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(
        project_path / "agent_interactions.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(handler)
    return logger


def log_interaction(
    logger: logging.Logger, agent: str, model: str,
    prompt: str, response: str, max_chars: int = 2000
) -> None:
    sep = "=" * 50
    logger.debug(
        f"\n{sep}\nАГЕНТ: {agent} | МОДЕЛЬ: {model}\n"
        f"--- PROMPT ---\n{prompt[:max_chars]}\n"
        f"--- RESPONSE ---\n{response[:max_chars]}\n{sep}"
    )


def log_runtime_error(project_path: Path, stderr: str) -> None:
    with open(project_path / "run_errors.log", "a", encoding="utf-8") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n[{ts}] SYSTEM CRASH:\n{stderr}\n{'-' * 40}\n")


def _cache_key(agent: str, model: str, user_text: str, language: str) -> str:
    return hashlib.sha256(f"{agent}:{model}:{language}:{user_text}".encode()).hexdigest()


def load_cache(project_path: Path) -> dict:
    p = project_path / "llm_cache.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def save_cache(project_path: Path, cache: dict) -> None:
    (project_path / "llm_cache.json").write_text(
        json.dumps(cache, indent=4, ensure_ascii=False), encoding="utf-8"
    )


# ─────────────────────────────────────────────
# JSON-ПАРСЕР
# ─────────────────────────────────────────────

def _repair_json(text: str) -> str:
    text = re.sub(r',\s*([}\]])', r'\1', text)          # trailing comma
    text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)  # JS-комментарии
    return text


def _extract_json_from_text(text: str) -> dict:
    """Надёжный парсер: учитывает строковые литералы с {} внутри."""
    text = text.strip()
    if not text:
        raise ValueError("Пустой ответ от модели")

    # 1. Весь текст — готовый JSON
    if text.startswith("{") and text.endswith("}"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    # 2. Поиск первого { с учётом escape-последовательностей и строк
    start = text.find("{")
    if start == -1:
        raise ValueError(f"JSON не найден в ответе: {text[:300]}")

    count = 0
    in_string = False
    escape_next = False
    end = -1
    for i in range(start, len(text)):
        ch = text[i]
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            count += 1
        elif ch == "}":
            count -= 1
            if count == 0:
                end = i + 1
                break

    if end == -1:
        raise ValueError("Несбалансированные JSON-скобки")

    candidate = text[start:end]

    # 3. Прямая попытка
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    # 4. Ремонт распространённых ошибок
    try:
        return json.loads(_repair_json(candidate))
    except json.JSONDecodeError:
        pass

    # 5. json-repair как последний шанс (опциональная зависимость)
    try:
        import json_repair  # type: ignore
        return json_repair.loads(candidate)
    except (ImportError, Exception):
        pass

    raise ValueError(f"Не удалось извлечь JSON: {text[:400]}...")


# ─────────────────────────────────────────────
# LLM-ВЫЗОВ С BACKOFF
# ─────────────────────────────────────────────

def ask_agent(
    logger: logging.Logger,
    agent: str,
    user_text: str,
    cache: dict,
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

    sys_prompt   = get_system_prompt(agent, language)
    temperature  = {
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
    }.get(agent, 0.2)

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user",   "content": user_text},
    ]

    last_exc: Exception = RuntimeError("Нет попыток")
    for retry in range(max_retries):
        if retry > 0:
            delay = 2 ** retry          # 2с, 4с
            logger.info(f"[{agent}:{model}] Backoff {delay}с (retry={retry})")
            time.sleep(delay)
        raw: Optional[str] = None
        try:
            # Попытка с json_object mode
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

    raise last_exc


# ─────────────────────────────────────────────
# СТАТИСТИКА
# ─────────────────────────────────────────────

class ModelStats:
    def __init__(self, path: Path) -> None:
        self.path = path / "model_stats.json"
        self.data: dict = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {}

    def record(self, agent: str, model: str, success: bool) -> None:
        key   = f"{agent}:{model}"
        entry = self.data.setdefault(key, {"success": 0, "fail": 0})
        if success:
            entry["success"] += 1
        else:
            entry["fail"] += 1
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")

    def print_report(self) -> None:
        print("\n📊 Статистика моделей:")
        if not self.data:
            print("  Нет данных.")
            return
        for key, d in sorted(self.data.items()):
            total = d["success"] + d["fail"]
            rate  = d["success"] / total * 100 if total else 0
            print(f"  {key}: {d['success']}/{total} ({rate:.0f}%)")


# ─────────────────────────────────────────────
# ВИЗУАЛИЗАЦИЯ
# ─────────────────────────────────────────────

def print_iteration_table(state: dict) -> None:
    language = state.get("language", "python")
    approved = len(state.get("approved_files", []))
    total    = len(state.get("files", []))
    status   = "✅ ПОЛНЫЙ УСПЕХ" if approved == total else "⏳ В ПРОЦЕССЕ"
    itr      = state.get("iteration", 0)
    phase    = state.get("last_phase", "—")

    w = 78
    def row(left: str, right: str) -> None:
        content = f"  {left:<20}: {right}"
        print(f"║{content:<{w}}║")

    print("╔" + "═" * w + "╗")
    title = f"ИТЕРАЦИЯ {itr:2d} — {status}"
    print(f"║{title:^{w}}║")
    print("╠" + "═" * w + "╣")
    row("Язык",           LANG_DISPLAY.get(language, language.upper()))
    row("Одобрено файлов", f"{approved}/{total} {'✅' if approved == total else '🔄'}")
    row("Последняя фаза",  phase)
    print("╚" + "═" * w + "╝")



# ─────────────────────────────────────────────
# УТИЛИТЫ КОНТЕКСТА
# ─────────────────────────────────────────────

def extract_public_api(code: str) -> str:
    api_lines: list[str] = []
    total = 0
    PUBLIC_PREFIXES = (
        "import ", "from ", "class ", "def ",   # Python
        "fn ", "pub fn ", "pub struct ", "pub enum ",  # Rust
        "export ", "const ", "let ", "function ",      # TypeScript
    )
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith(PUBLIC_PREFIXES):
            api_lines.append(line)
            total += len(line)
        elif (
            not line.startswith((" ", "\t"))
            and "=" in stripped
            and not stripped.startswith(("_", "#", "//"))
        ):
            api_lines.append(line)
            total += len(line)
        if total >= MAX_CONTEXT_CHARS:
            api_lines.append("# [... обрезано ...]")
            break
    return "\n".join(api_lines)


def get_global_context(
    project_path: Path,
    files: list[str],
    exclude: Optional[str] = None, 
) -> str:
    parts: list[str] = []
    total = 0
    for fname in files:
        if exclude is not None and fname == exclude:
            continue
        fpath = project_path / fname
        if not fpath.exists():
            continue
        api   = extract_public_api(fpath.read_text(encoding="utf-8"))
        chunk = f"\n--- {fname} PUBLIC API ---\n{api}\n"
        if total + len(chunk) > MAX_CONTEXT_CHARS:
            remaining = MAX_CONTEXT_CHARS - total
            if remaining > 200:
                parts.append(chunk[:remaining] + "\n[... обрезано ...]")
            break
        parts.append(chunk)
        total += len(chunk)
    return "".join(parts)


def build_dependency_order(files: list[str], project_path: Path) -> list[str]:
    graph: dict[str, list[str]]  = defaultdict(list)
    indegree: dict[str, int]     = {f: 0 for f in files}
    file_set = set(files)

    for f in files:
        fpath = project_path / f
        if not fpath.exists():
            continue
        code = fpath.read_text(encoding="utf-8")
        imports = (
            re.findall(r"from\s+(\S+)\s+import", code)
            + re.findall(r"^import\s+(\S+)", code, re.MULTILINE)
            + re.findall(r"require\(['\"]([^'\"]+)['\"]", code)
            + re.findall(r"\buse\s+([\w:]+)", code)
        )
        ext = Path(f).suffix
        for imp in imports:
            dep = imp.split(".")[0] + ext
            if dep in file_set and dep != f:
                graph[dep].append(f)
                indegree[f] += 1

    q: deque[str] = deque(f for f in files if indegree[f] == 0)
    order: list[str] = []
    while q:
        curr = q.popleft()
        order.append(curr)
        for dep in graph[curr]:
            indegree[dep] -= 1
            if indegree[dep] == 0:
                q.append(dep)

    if len(order) < len(files):
        order.extend(f for f in files if f not in order)
    return order


def _find_failing_file(stderr: str, stdout: str, files: list[str]) -> str:
    """[v12.1-8] Общая утилита поиска файла с ошибкой."""
    for match in re.findall(r'File "([^"]+)", line \d+', stderr):
        candidate = os.path.basename(match)
        if candidate in files:
            return candidate
    for match in re.findall(r'(?:FAILED|ERROR)\s+([\w/]+\.\w+)', stdout + stderr):
        src = os.path.basename(match).replace("test_", "")
        if src in files:
            return src
    return files[0] if files else "main.py"


# ─────────────────────────────────────────────
# GIT
# ─────────────────────────────────────────────

def git_init(project_path: Path) -> None:
    run_command(["git", "init"], cwd=project_path)
    gitignore = (
        "venv/\n__pycache__/\n*.pyc\n"
        "node_modules/\ntarget/\n"
        "llm_cache.json\nmodel_stats.json\n"
    )
    (project_path / ".gitignore").write_text(gitignore, encoding="utf-8")
    git_commit(project_path, "Initial gitignore")


def git_commit(project_path: Path, message: str) -> None:
    run_command(["git", "add", "."], cwd=project_path)
    run_command(["git", "commit", "-m", message, "--allow-empty"], cwd=project_path)


# ─────────────────────────────────────────────
# ПРОЦЕССЫ / DOCKER
# ─────────────────────────────────────────────

def run_command(
    args: list[str],
    cwd: Optional[Path] = None,
    timeout: Optional[int] = None,
) -> tuple[int, str, str]:
    try:
        proc = subprocess.Popen(
            args, cwd=cwd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            return proc.returncode, stdout, stderr
        except subprocess.TimeoutExpired:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            return -1, "", f"TIMEOUT: процесс не завершился за {timeout}с."
    except FileNotFoundError as e:
        return -1, "", f"Команда не найдена: {e}"


def _cleanup_docker_containers(image: str) -> None:
    """Убиваем зависшие контейнеры после таймаута."""
    rc, stdout, _ = run_command(["docker", "ps", "-q", "--filter", f"ancestor={image}"])
    if rc == 0 and stdout.strip():
        ids = stdout.strip().split()
        run_command(["docker", "rm", "-f"] + ids)


def run_in_docker(
    project_path: Path,
    command: str,
    timeout: int,
    language: str = "python",
) -> tuple[int, str, str]:
    image  = get_docker_image(language)
    result = run_command(
        [
            "docker", "run", "--rm",
            "--network", "bridge",
            "--memory", "512m",
            "--cpus",   "1",
            "-v", f"{project_path}:/app",
            "-w", "/app",
            image,
            "bash", "-c", command,
        ],
        timeout=timeout,
    )
    if result[0] == -1:
        _cleanup_docker_containers(image)
    return result


def build_docker_image(project_path: Path, tag: str) -> tuple[bool, str, str]:
    rc, stdout, stderr = run_command(
        ["docker", "build", "-t", tag, "."],
        cwd=project_path, timeout=RUN_TIMEOUT,
    )
    return rc == 0, stdout, stderr


def check_docker_installed() -> bool:
    rc, _, stderr = run_command(["docker", "version"])
    if rc != 0:
        print(f"❌ Docker не установлен или не запущен: {stderr}")
        return False
    return True


# ─────────────────────────────────────────────
# СОСТОЯНИЕ
# ─────────────────────────────────────────────

def save_state(project_path: Path, state: dict) -> None:
    """Сохраняем только JSON-сериализуемые данные."""
    clean = {k: v for k, v in state.items() if not k.startswith("_")}
    (project_path / "state.json").write_text(
        json.dumps(clean, indent=4, ensure_ascii=False), encoding="utf-8"
    )


def load_state(project_path: Path) -> Optional[dict]:
    p = project_path / "state.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def ensure_feedback_keys(state: dict) -> None:
    for f in state["files"]:
        state["feedbacks"].setdefault(f, "")


def generate_summary(project_path: Path, state: dict) -> None:
    language   = state.get("language", "python")
    entry      = state.get("entry_point", "main.py")
    docker_img = get_docker_image(language)
    run_cmd    = get_execution_command(language, entry)
    text = (
        f"# Проект: {project_path.name}\n\n"
        f"## Задача\n{state['task']}\n\n"
        f"## Язык\n{LANG_DISPLAY.get(language, language.upper())}\n\n"
        f"## Архитектура\n{state['architecture']}\n\n"
        "## Файлы\n" + "\n".join(f"- {f}" for f in state["files"])
        + f"\n\n## Итераций: {state['iteration'] - 1}\n\n"
        f"## Запуск\n```bash\n"
        f"docker run --rm -v $(pwd):/app -w /app {docker_img} bash -c '{run_cmd}'\n```\n"
    )
    (project_path / "SUMMARY.md").write_text(text, encoding="utf-8")
    print("📄 Сгенерирован SUMMARY.md")


def update_requirements(project_path: Path, orig: str, alt: str) -> None:
    req_path = project_path / "requirements.txt"
    if not req_path.exists():
        return
    lines     = req_path.read_text(encoding="utf-8").splitlines()
    new_lines = [line if line.strip() != orig.strip() else alt for line in lines]
    req_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def update_dependencies(project_path: Path, language: str, pkg: str) -> None:
    """Реализован для Python и TypeScript."""
    if language == "python":
        req_path = project_path / "requirements.txt"
        # [v12.1-4] fsync после записи
        with open(req_path, "a", encoding="utf-8") as f:
            f.write(f"\n{pkg}\n")
            f.flush()
            os.fsync(f.fileno())
        if (project_path / ".git").exists():
            run_command(["git", "add", "requirements.txt"], cwd=project_path)

    elif language == "typescript":
        pkg_json_path = project_path / "package.json"
        if pkg_json_path.exists():
            try:
                pkg_data = json.loads(pkg_json_path.read_text(encoding="utf-8"))
                pkg_data.setdefault("dependencies", {})[pkg] = "latest"
                pkg_json_path.write_text(json.dumps(pkg_data, indent=2), encoding="utf-8")
                print(f"  → Добавлен {pkg} в package.json")
            except Exception as e:
                print(f"  ⚠️  Не удалось обновить package.json: {e}")

    else:
        print(f"⚠️  Добавление пакета для {language} требует ручного вмешательства: {pkg}")


def update_dockerfile(project_path: Path, patch: str) -> None:
    dockerfile = project_path / "Dockerfile"
    if not dockerfile.exists():
        return
    content = dockerfile.read_text(encoding="utf-8").rstrip()
    if patch.strip() not in content:
        if not patch.strip().upper().startswith("RUN"):
            patch = f"RUN {patch}"
        content += f"\n\n# DevOps fix\n{patch}\n"
    dockerfile.write_text(content + "\n", encoding="utf-8")


def generate_tor_md(project_path: Path, ba_resp: dict) -> None:
    tor_text = (
        "# Техническое Задание (TOR)\n\n"
        f"## Цель проекта\n{ba_resp.get('project_goal', '')}\n\n"
        "## User Stories\n"
        + "\n".join(f"- {s}" for s in ba_resp.get("user_stories", []))
        + "\n\n## Критерии приёмки\n"
        + "\n".join(f"- {c}" for c in ba_resp.get("acceptance_criteria", []))
    )
    (project_path / "TOR.md").write_text(tor_text, encoding="utf-8")
    print("📄 Сгенерирован TOR.md")



# ─────────────────────────────────────────────
# ФАЗЫ РАЗРАБОТКИ
# ─────────────────────────────────────────────

def _review_file(
    logger: logging.Logger,
    cache: dict,
    current_file: str,
    code: str,
    attempt: int,
    stats: ModelStats,
    randomize: bool = False,
    language: str = "python",
) -> tuple[str, str]:
    rev_model = get_model("reviewer", attempt, randomize=randomize)
    print(f"👀 [{rev_model}] Reviewer проверяет {current_file} ...")
    try:
        result   = ask_agent(logger, "reviewer", f"Файл: {current_file}\nКод:\n{code}",
                             cache, attempt, randomize, language)
        status   = result.get("status", "REJECT")
        feedback = result.get("feedback", "")
        stats.record("reviewer", rev_model, status == "APPROVE")
        return status, feedback
    except Exception as e:
        logger.exception(f"Reviewer упал: {e}")
        stats.record("reviewer", rev_model, False)
        return "REJECT", f"Reviewer упал: {e}"


def do_self_reflect(
    logger: logging.Logger,
    cache: dict,
    project_path: Path,         
    current_file: str,
    code: str,
    state: dict,
    stats: ModelStats,          
    randomize: bool = False,
) -> tuple[str, str]:
    """Self-Reflect: разработчик проверяет себя перед внешним ревью."""
    language  = state.get("language", "python")
    sr_model  = get_model("self_reflect", 0, randomize=randomize)
    print(f"🤔 [{sr_model}] Self-Reflect проверяет {current_file} ...")
    try:
        ctx    = (
            f"Файл: {current_file}\nКод:\n{code}\n\n"
            f"Спецификации:\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}"
        )
        result   = ask_agent(logger, "self_reflect", ctx, cache, 0, randomize, language)
        status   = result.get("status", "OK")
        feedback = result.get("feedback", "")
        improved = result.get("improved_code", "").strip()

        if status == "NEEDS_IMPROVEMENT" and improved:
            (project_path / current_file).write_text(improved, encoding="utf-8")
            print(f"  → Self-Reflect улучшил код: {feedback[:80]}")

        stats.record("self_reflect", sr_model, status == "OK")
        return status, feedback
    except Exception as e:
        logger.exception(f"Self-Reflect упал: {e}")
        stats.record("self_reflect", sr_model, False)
        return "OK", ""   # не блокируем pipeline при падении


def phase_validate_architecture(
    logger: logging.Logger,
    project_path: Path,
    state: Optional[dict],
    cache: dict,
    stats: ModelStats,
    arch_resp: dict,
    sa_resp: dict,
    task: str,
    language: str = "python",
    randomize: bool = False,
) -> bool:
    """
    Трёхуровневая валидация архитектуры семантически корректными агентами:
      1. system_analyst  — соответствие спецификации и требованиям
      2. arch_validator  — реализуемость, production-readiness
      3. devops_runtime  — Docker-совместимость и зависимости
    """
    arch_text = json.dumps(arch_resp, ensure_ascii=False, indent=2)
    sa_text   = json.dumps(sa_resp,   ensure_ascii=False, indent=2)

    validation_map = [
        ("Системный аналитик", "system_analyst",
         "Проверь соответствие архитектуры бизнес-требованиям и спецификации."),
        ("Architect Validator", "arch_validator",
         "Проверь реализуемость, production-readiness и корректность для языка."),
        ("DevOps-инженер",     "devops_runtime",
         "Проверь Docker-совместимость, корректность зависимостей и базового образа."),
    ]

    rejections = 0
    for label, agent_key, instruction in validation_map:
        print(f"🔍 Валидация архитектуры — {label} ...")
        val_ctx = (
            f"Запрос: {task}\n\n"
            f"Спецификация (SA): {sa_text}\n\n"
            f"Предложенная архитектура: {arch_text}\n\n"
            f"Язык: {LANG_DISPLAY.get(language, language)}\n\n"
            f"Задача проверки: {instruction}"
        )
        try:
            val_resp = ask_agent(logger, agent_key, val_ctx, cache, 0, randomize, language)
            if val_resp.get("status") in ("REJECT", "CANNOT_FIX"):
                fb = val_resp.get("feedback", val_resp.get("explanation", ""))
                print(f"  ❌ {label} отклонил: {fb[:150]}")
                rejections += 1
                stats.record(agent_key, get_model(agent_key), False)
            else:
                print(f"  ✅ {label} одобрил.")
                stats.record(agent_key, get_model(agent_key), True)
        except Exception as e:
            logger.exception(f"{label} упал: {e}")
            rejections += 1

        if rejections > 1:
            return False

    print("✅ Архитектура прошла многоуровневую валидацию!")
    return True


def phase_develop(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: dict,
    stats: ModelStats,
    randomize: bool = False,
) -> None:
    language     = state.get("language", "python")
    order        = build_dependency_order(state["files"], project_path)
    file_attempts: dict[str, int] = state.setdefault("file_attempts", {})

    for current_file in order:
        if current_file in state.get("approved_files", []):
            print(f"⏭️  {current_file} уже одобрен.")
            continue

        attempt = file_attempts.get(current_file, 0)

        # [v12.1-3] hard-limit попыток на файл
        if attempt >= MAX_FILE_ATTEMPTS:
            print(f"⚠️  {current_file} исчерпал {MAX_FILE_ATTEMPTS} попыток → эскалация в spec_reviewer.")
            state["feedbacks"][current_file] = (
                f"Файл не удалось написать за {MAX_FILE_ATTEMPTS} попыток. "
                "Возможно, спецификация противоречива. Требуется revise_spec."
            )
            continue

        file_path = project_path / current_file
        file_path.parent.mkdir(parents=True, exist_ok=True)

        existing_code   = file_path.read_text(encoding="utf-8").strip() if file_path.exists() else ""
        global_context  = get_global_context(project_path, state["files"], exclude=current_file)

        dev_ctx = (
            f"Задача:\n{state['task']}\n\n"
            f"СИСТЕМНЫЕ СПЕЦИФИКАЦИИ:\n"
            f"{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
            f"Файл для написания: `{current_file}`.\n\n"
        )
        if global_context:
            dev_ctx += f"ГЛОБАЛЬНЫЙ КОНТЕКСТ:\n{global_context}\n\n"
        if existing_code:
            dev_ctx += f"ТЕКУЩИЙ КОД `{current_file}`:\n{existing_code}\n\n"
        if state["feedbacks"].get(current_file):
            dev_ctx += f"ЗАМЕЧАНИЯ (исправь это):\n{state['feedbacks'][current_file]}"

        dev_model = get_model("developer", attempt, randomize=randomize)
        print(f"💻 [{dev_model}] Разработчик пишет {current_file} (попытка {attempt + 1}/{MAX_FILE_ATTEMPTS}) ...")

        try:
            dev_resp = ask_agent(logger, "developer", dev_ctx, cache, attempt, randomize, language)
            code     = dev_resp.get("code", "").strip()
        except Exception as e:
            logger.exception(f"Developer упал: {e}")
            stats.record("developer", dev_model, False)
            state["feedbacks"][current_file] = f"Агент не вернул код: {e}"
            file_attempts[current_file] = attempt + 1
            continue

        if not code:
            stats.record("developer", dev_model, False)
            state["feedbacks"][current_file] = "Агент вернул пустой код."
            file_attempts[current_file] = attempt + 1
            continue

        file_path.write_text(code, encoding="utf-8")

        # Self-Reflect перед внешним ревью
        sr_status, sr_feedback = do_self_reflect(
            logger, cache, project_path, current_file, code, state, stats, randomize
        )
        if sr_status == "NEEDS_IMPROVEMENT":
            # код уже перезаписан внутри do_self_reflect, берём обновлённый
            code = file_path.read_text(encoding="utf-8")

        # Внешний ревью
        rev_status, rev_feedback = _review_file(
            logger, cache, current_file, code, attempt, stats, randomize, language
        )

        if rev_status == "APPROVE":
            stats.record("developer", dev_model, True)
            print(f"✅ {current_file} одобрен.")
            state.setdefault("approved_files", []).append(current_file)
            state["feedbacks"][current_file] = ""
            file_attempts[current_file] = 0
        else:
            stats.record("developer", dev_model, False)
            # Объединяем замечания Self-Reflect и Reviewer
            combined = "\n".join(filter(None, [sr_feedback, rev_feedback]))
            print(f"❌ {current_file} отклонён: {combined[:100]}")
            state["feedbacks"][current_file] = combined
            file_attempts[current_file] = attempt + 1


def phase_e2e_review(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: dict,
    stats: ModelStats,
    attempt: int = 0,
    randomize: bool = False,
) -> bool:
    """Параллельное E2E — исправлена переменная agent в futures."""
    print("\n🧐 Parallel E2E-ревью (Architect + QA) ...")
    language = state.get("language", "python")
    all_code = get_global_context(project_path, state["files"])   # exclude=None → все файлы

    agents = [("e2e_architect", "Architect"), ("e2e_qa", "QA Lead")]
    result_ok = True

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        #Сохраняем (agent_key, label) в словаре, не полагаемся на внешнюю переменную
        future_map: dict[concurrent.futures.Future, tuple[str, str]] = {
            executor.submit(ask_agent, logger, agent_key, all_code, cache, attempt, randomize, language):
            (agent_key, label)
            for agent_key, label in agents
        }

        for future in concurrent.futures.as_completed(future_map):
            agent_key, label = future_map[future]
            model = get_model(agent_key, attempt, randomize)
            try:
                resp = future.result()
            except Exception as e:
                logger.exception(f"[{label}] future error: {e}")
                stats.record(agent_key, model, False)
                result_ok = False
                continue

            if resp.get("status") == "REJECT":
                target   = resp.get("target_file", "").strip() or state["files"][0]
                feedback = resp.get("feedback", "")
                print(f"❌ E2E [{label}] REJECT на {target}: {feedback[:120]}")
                stats.record(agent_key, model, False)
                if target in state.get("approved_files", []):
                    state["approved_files"].remove(target)
                state["feedbacks"][target] = f"E2E {label} Reject:\n{feedback}"
                result_ok = False
            else:
                stats.record(agent_key, model, True)

    if result_ok:
        print("✅ Parallel E2E-ревью пройдено!")
    return result_ok


def phase_integration_test(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: dict,
    stats: ModelStats,
    randomize: bool = False,
) -> bool:
    language    = state.get("language", "python")
    entry_point = state.get("entry_point", "main.py")
    dockerfile  = project_path / "Dockerfile"
    use_custom  = dockerfile.exists()
    image_tag   = f"{project_path.name}:latest" if use_custom else get_docker_image(language)

    # ── Сборка образа ────────────────────────────────────────────────────────
    build_success = False
    for build_attempt in range(1, 4):
        if use_custom:
            print(f"\n🏗️ Сборка Docker-образа (попытка {build_attempt}/3) ...")
            build_success, _, build_err = build_docker_image(project_path, image_tag)
            if build_success:
                print("✅ Образ собран.")
                break
            print(f"❌ Ошибка сборки:\n{build_err[:400]}")
            try:
                devops_ctx  = (
                    f"Ошибка сборки Docker:\n{build_err}\n\n"
                    f"Текущий Dockerfile:\n{dockerfile.read_text(encoding='utf-8')}"
                )
                devops_resp = ask_agent(logger, "devops_runtime", devops_ctx, cache, 0, randomize, language)
                stats.record("devops_runtime", get_model("devops_runtime"), True)
                if devops_resp.get("status") == "FIX_PROPOSED" and devops_resp.get("dockerfile_patch"):
                    update_dockerfile(project_path, devops_resp["dockerfile_patch"])
                    print("  → Dockerfile обновлён, пересобираю.")
            except Exception as e:
                logger.exception(f"DevOps (build) упал: {e}")
                stats.record("devops_runtime", get_model("devops_runtime"), False)
        else:
            build_success = True
            break

    if not build_success:
        state["feedbacks"][state["files"][0]] = "Не удалось собрать Docker-образ."
        return False

    # ── Запуск приложения ────────────────────────────────────────────────────
    for run_attempt in range(1, 6):
        print(f"\n🚀 Запуск в Docker (попытка {run_attempt}/5) ...")
        cmd = get_execution_command(language, entry_point)

        # Применяем env_fixes из предыдущего прогона
        env_fixes = state.get("env_fixes", {})
        if env_fixes.get("system_packages"):
            cmd = "apt-get update -q && apt-get install -y " + " ".join(env_fixes["system_packages"]) + " && " + cmd
        if language == "python":
            for orig, alt in env_fixes.get("pip_alternatives", {}).items():
                update_requirements(project_path, orig, alt)

        rc, stdout, stderr = run_in_docker(project_path, cmd, RUN_TIMEOUT, language)
        (project_path / "test.log").write_text(
            f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}", encoding="utf-8"
        )
        print("\n--- STDOUT ---\n", stdout[:2000])
        print("\n--- STDERR ---\n", stderr[:2000])

        if rc == 0:
            print("\n✅ Приложение завершилось успешно!")
            state["env_fixes"] = {}
            return True

        print("\n💥 Ошибка выполнения!")
        log_runtime_error(project_path, stderr)

        failing_file = _find_failing_file(stderr, stdout, state["files"])

        # DevOps — системные зависимости
        if any(kw in stderr.lower() for kw in ["lib", ".so", "cannot open shared object", "no such file"]):
            print("🛠️  DevOps анализирует ошибку окружения ...")
            try:
                devops_ctx  = (
                    f"Traceback:\n{stderr}\n\n"
                    f"Dockerfile: {dockerfile.read_text(encoding='utf-8') if dockerfile.exists() else 'Нет'}"
                )
                devops_resp = ask_agent(logger, "devops_runtime", devops_ctx, cache, 0, randomize, language)
                stats.record("devops_runtime", get_model("devops_runtime"), True)
                if devops_resp.get("status") == "FIX_PROPOSED":
                    if devops_resp.get("dockerfile_patch"):
                        update_dockerfile(project_path, devops_resp["dockerfile_patch"])
                        print("  → Dockerfile обновлён, требуется пересборка.")
                        return False
                    state["env_fixes"] = devops_resp
                    continue
            except Exception as e:
                logger.exception(f"DevOps (runtime) упал: {e}")
                stats.record("devops_runtime", get_model("devops_runtime"), False)

        # QA Runtime
        qa_model = get_model("qa_runtime", run_attempt - 1, randomize)
        try:
            qa_resp     = ask_agent(
                logger, "qa_runtime",
                f"Traceback:\n{stderr}\n\nФайл с ошибкой: {failing_file}",
                cache, run_attempt - 1, randomize, language,
            )
            fix         = qa_resp.get("fix", "Смотри traceback.")
            missing_pkg = qa_resp.get("missing_package", "").strip()
            agent_file  = qa_resp.get("file", "").strip()
            if agent_file and agent_file in state["files"]:
                failing_file = agent_file
            stats.record("qa_runtime", qa_model, True)
        except Exception as e:
            logger.exception(f"QA Runtime упал: {e}")
            fix, missing_pkg = "Смотри traceback.", ""
            stats.record("qa_runtime", qa_model, False)

        # Защита от зацикливания установки пакетов
        if missing_pkg:
            if language == "python":
                req_path = project_path / "requirements.txt"
                current_reqs = req_path.read_text(encoding="utf-8") if req_path.exists() else ""
                pkg_clean    = re.split(r'[=<>~]', missing_pkg)[0].strip().lower()
                existing     = [re.split(r'[=<>~]', l)[0].strip().lower()
                                for l in current_reqs.splitlines() if l.strip() and not l.startswith("#")]
                if pkg_clean in existing:
                    print(f"⚠️  '{pkg_clean}' уже в requirements, но всё равно падает → возврат разработчику.")
                    state["feedbacks"][failing_file] = (
                        f"ПРОГРАММА УПАЛА. Пакет '{pkg_clean}' установлен, но код падает. "
                        f"Проблема в логике или импортах.\nTraceback:\n{stderr}"
                    )
                    if failing_file in state.get("approved_files", []):
                        state["approved_files"].remove(failing_file)
                    return False
                else:
                    print(f"🔧 Добавляю пакет: {missing_pkg}")
                    update_dependencies(project_path, language, missing_pkg)
                    continue
            elif language == "typescript":
                print(f"🔧 Добавляю пакет в package.json: {missing_pkg}")
                update_dependencies(project_path, language, missing_pkg)
                continue

        if failing_file in state.get("approved_files", []):
            state["approved_files"].remove(failing_file)
        state["feedbacks"][failing_file] = f"ПРОГРАММА УПАЛА.\nTRACEBACK:\n{stderr}\nQA:\n{fix}"
        print("🔄 Возврат к разработчику.")
        return False

    return False


def phase_unit_tests(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: dict,
    stats: ModelStats,
    randomize: bool = False,
) -> bool:
    print("\n🧪 Генерация unit-тестов ...")
    language = state.get("language", "python")
    all_code = get_global_context(project_path, state["files"])

    tg_model = get_model("test_generator", 0, randomize)
    try:
        test_resp  = ask_agent(
            logger, "test_generator",
            f"Спецификации:\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}"
            f"\n\nКод проекта:\n{all_code}",
            cache, 0, randomize, language,
        )
        test_files = test_resp.get("test_files", [])
        stats.record("test_generator", tg_model, True)
    except Exception as e:
        print(f"⚠️  Не удалось сгенерировать тесты: {e}. Пропускаю.")
        stats.record("test_generator", tg_model, False)
        return True

    if not test_files:
        return True

    tests_dir = project_path / "tests"
    tests_dir.mkdir(exist_ok=True)
    if language == "python":
        (tests_dir / "__init__.py").write_text("", encoding="utf-8")

    for tf in test_files:
        if code := tf.get("code", ""):
            (tests_dir / tf.get("filename", f"test_generated.{LANG_EXT.get(language, 'py')}")).write_text(
                code, encoding="utf-8"
            )

    print("🚀 Запуск тестов в Docker ...")
    cmd = get_test_command(language)
    rc, stdout, stderr = run_in_docker(project_path, cmd, RUN_TIMEOUT * 2, language)
    (project_path / "coverage.log").write_text(stdout + "\n" + stderr, encoding="utf-8")

    if rc != 0:
        print("❌ Тесты провалены!")
        failing_file = _find_failing_file(stderr, stdout, state["files"])  # [v12.1-8]
        state["feedbacks"][failing_file] = f"UNIT-ТЕСТЫ УПАЛИ:\n{stderr[-2000:]}\n\nВывод:\n{stdout[-1000:]}"
        if failing_file in state.get("approved_files", []):
            state["approved_files"].remove(failing_file)
        return False

    # Безопасный re.search без AttributeError
    m        = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", stdout)
    coverage = int(m.group(1)) if m else 100   # если нет строки TOTAL — считаем 100%

    if coverage < MIN_COVERAGE:
        print(f"❌ Покрытие {coverage}% < {MIN_COVERAGE}%")
        state["feedbacks"]["main.py"] = (
            f"Покрытие {coverage}% < порога {MIN_COVERAGE}%. "
            "Добавь публичные функции с понятными сигнатурами."
        )
        if "main.py" in state.get("approved_files", []):
            state["approved_files"].remove("main.py")
        return False

    print(f"✅ Тесты пройдены! Покрытие: {coverage}%")
    return True


def phase_document(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: dict,
    randomize: bool = False,
) -> None:
    print("📝 Генерация README.md ...")
    language = state.get("language", "python")
    try:
        resp = ask_agent(
            logger, "documenter",
            (
                f"Задача: {state['task']}\n"
                f"Бизнес-требования: {json.dumps(state.get('business_requirements', {}), ensure_ascii=False)}\n"
                f"Архитектура: {state['architecture']}\n"
                f"Язык: {LANG_DISPLAY.get(language, language)}"
            ),
            cache, 0, randomize, language,
        )
        (project_path / "README.md").write_text(resp.get("readme", "").strip(), encoding="utf-8")
        print("✅ README.md сгенерирован.")
    except Exception as e:
        print(f"⚠️  Documenter не справился: {e}")


def revise_spec(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: dict,
    problem: str,
    randomize: bool = False,
) -> None:
    """Сбрасывает spec_history и file_attempts при обновлении спецификации."""
    print("\n🔁 Пересмотр спецификации ...")
    language = state.get("language", "python")
    ctx = (
        f"Запрос заказчика:\n{state['task']}\n\n"
        f"Текущая спецификация:\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
        f"Проблема:\n{problem}"
    )
    try:
        new_specs      = ask_agent(logger, "spec_reviewer", ctx, cache, 0, randomize, language)
        change_summary = new_specs.pop("change_summary", "нет описания")
        state["system_specs"] = new_specs

        previously_approved = list(state.get("approved_files", []))
        state["approved_files"] = []
        state["file_attempts"]  = {}    # сброс попыток
        state["feedbacks"]      = {f: "Спецификация обновлена." for f in state["files"]}
        state["env_fixes"]      = {}
        state["phase_fail_counts"] = {}
        state["e2e_passed"] = state["integration_passed"] = state["tests_passed"] = False

        print(f"✅ Спецификация обновлена: {change_summary}")
        if previously_approved:
            print(f"ℹ️  Сброшены файлы: {', '.join(previously_approved)}")

        state.setdefault("spec_history", []).append({
            "iteration":    state["iteration"],
            "problem":      problem,
            "change":       change_summary,
            "reset_files":  previously_approved,
        })

        arch_path = project_path / "ARCHITECTURE.md"
        arch_md   = arch_path.read_text(encoding="utf-8") if arch_path.exists() else ""
        arch_md  += (
            f"\n\n## Обновление спецификации (итерация {state['iteration']})\n"
            f"**Причина:** {problem}\n**Изменение:** {change_summary}\n\n"
            f"```json\n{json.dumps(new_specs, ensure_ascii=False, indent=2)}\n```"
        )
        arch_path.write_text(arch_md, encoding="utf-8")

    except Exception as e:
        print(f"⚠️  Не удалось обновить спецификацию: {e}")



# ─────────────────────────────────────────────
# SUPERVISOR
# ─────────────────────────────────────────────

def ask_supervisor(
    logger: logging.Logger,
    state: dict,
    cache: dict,
    randomize: bool,
    language: str,
) -> dict:
    """
    Передаём Supervisor явные флаги состояния, а не только счётчики.
    Это исключает преждевременный переход в 'success'.
    """
    approved = len(state.get("approved_files", []))
    total    = len(state.get("files", []))

    # Счётчики подряд-провалов по фазам
    phase_fails = state.get("phase_fail_counts", {})

    summary = {
        "iteration":            state.get("iteration", 1),
        "language":             language,
        "approved_files":       approved,
        "total_files":          total,
        "all_files_approved":   approved == total,
        "e2e_passed":           state.get("e2e_passed", False),
        "integration_passed":   state.get("integration_passed", False),
        "tests_passed":         state.get("tests_passed", False),
        "document_generated":   state.get("document_generated", False),
        "has_pending_feedback": any(v for v in state.get("feedbacks", {}).values()),
        "last_phase":           state.get("last_phase", "initial"),
        "phase_fail_counts":    phase_fails,
    }

    ctx = (
        f"Текущее состояние проекта:\n"
        f"{json.dumps(summary, ensure_ascii=False, indent=2)}\n\n"
        "Реши следующую фазу строго по правилам из промпта."
    )
    try:
        result = ask_agent(logger, "supervisor", ctx, cache, 0, randomize, language)
        return result
    except Exception as e:
        logger.exception(f"Supervisor упал: {e}")
        # Fallback: детерминированная логика
        if approved < total:
            return {"next_phase": "develop",           "reason": "fallback: не все файлы одобрены"}
        if not state.get("e2e_passed"):
            return {"next_phase": "e2e_review",        "reason": "fallback: e2e не пройдено"}
        if not state.get("integration_passed"):
            return {"next_phase": "integration_test",  "reason": "fallback: интеграция не пройдена"}
        if not state.get("tests_passed"):
            return {"next_phase": "unit_tests",        "reason": "fallback: тесты не пройдены"}
        if not state.get("document_generated"):
            return {"next_phase": "document",          "reason": "fallback: документация не создана"}
        return {"next_phase": "success",               "reason": "fallback: всё готово"}


def _bump_phase_fail(state: dict, phase: str) -> int:
    """Увеличивает счётчик провалов фазы, возвращает новое значение."""
    counts = state.setdefault("phase_fail_counts", {})
    counts[phase] = counts.get(phase, 0) + 1
    return counts[phase]


def _reset_phase_fail(state: dict, phase: str) -> None:
    state.setdefault("phase_fail_counts", {})[phase] = 0


# ─────────────────────────────────────────────
# ИНИЦИАЛИЗАЦИЯ ПРОЕКТА
# ─────────────────────────────────────────────

def _init_project_files(
    project_path: Path,
    project_name: str,
    language: str,
    deps: list[str],
    files_list: list[str],
    arch_resp: dict,
    ba_resp: dict,
    sa_resp: dict,
    task: str,
) -> tuple[list[str], str]:
    """Создаёт файлы зависимостей и возвращает (files_list, entry_point)."""
    if language == "python":
        entry_point = "main.py"
        if "main.py" not in files_list:
            files_list.append("main.py")
        (project_path / "requirements.txt").write_text(
            "\n".join(deps) if deps else "# No external dependencies\n", encoding="utf-8"
        )

    elif language == "typescript":
        entry_point = "main.ts"
        if "main.ts" not in files_list:
            files_list.append("main.ts")
        pkg_data = {
            "name":         project_name.lower(),
            "version":      "1.0.0",
            "dependencies": {d: "latest" for d in deps},
        }
        (project_path / "package.json").write_text(json.dumps(pkg_data, indent=2), encoding="utf-8")

    elif language == "rust":
        entry_point = "src/main.rs"
        if "src/main.rs" not in files_list:
            files_list.append("src/main.rs")
        (project_path / "src").mkdir(exist_ok=True)
        # Используем "*" вместо "0.1"
        cargo_deps = "\n".join(f'{d} = "*"' for d in deps)
        cargo_toml = (
            f'[package]\nname = "{project_name.lower()}"\n'
            f'version = "0.1.0"\nedition = "2021"\n\n[dependencies]\n{cargo_deps}\n'
        )
        (project_path / "Cargo.toml").write_text(cargo_toml, encoding="utf-8")
    else:
        entry_point = "main.py"

    # ARCHITECTURE.md
    (project_path / "ARCHITECTURE.md").write_text(
        f"# {project_name}\n\n"
        f"## Задача\n{task}\n\n"
        f"## Бизнес-требования\n```json\n{json.dumps(ba_resp, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## Системная спецификация\n```json\n{json.dumps(sa_resp, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## Архитектура\n{arch_resp.get('architecture', '')}",
        encoding="utf-8",
    )

    return files_list, entry_point


# ─────────────────────────────────────────────
# ТОЧКА ВХОДА
# ─────────────────────────────────────────────

def main() -> None:
    if not check_docker_installed():
        return

    print("🚀 Мультифайловая Фабрика Агентов v14.0")
    print("   (Supervisor · Self-Reflect · Parallel E2E · Multi-Language)\n")

    if input("Подтвердите запуск (yes/no): ").strip().lower() != "yes":
        print("Отменено.")
        return

    randomize_models = input("Случайная ротация моделей? (y/n) [n]: ").strip().lower() == "y"
    if randomize_models:
        print("🎲 Режим случайной ротации включён.")

    project_name = input("Имя проекта (латиницей): ").strip()
    if not re.match(r"^[A-Za-z0-9_\-]+$", project_name):
        print("❌ Недопустимое имя проекта.")
        return

    language_input = input("Язык (python / typescript / rust) [python]: ").strip().lower()
    language = language_input if language_input in DOCKER_IMAGES else "python"
    print(f"🌍 Выбран язык: {LANG_DISPLAY.get(language, language)}")

    project_path = BASE_DIR / project_name
    project_path.mkdir(parents=True, exist_ok=True)

    logger = setup_logger(project_path)
    cache  = load_cache(project_path)
    stats  = ModelStats(project_path)

    # ── Загрузка или создание состояния ──────────────────────────────────────
    state = load_state(project_path)
    if state:
        if "language" not in state:
            state["language"] = "python"
        language = state["language"]
        if input_with_timeout(
            f"📁 Найден прогресс (итерация {state.get('iteration', 1)}). Продолжить? (y/n): ",
            WAIT_TIMEOUT, "y"
        ).lower() != "y":
            state = None

    if state:
        ensure_feedback_keys(state)
    else:
        task = input("Опишите задачу: ").strip()
        if not task:
            print("❌ Задача не может быть пустой.")
            return

        git_init(project_path)

        print("\n📊 Business Analyst ...")
        try:
            ba_resp = ask_agent(logger, "business_analyst", f"Запрос:\n{task}", cache, language=language)
            generate_tor_md(project_path, ba_resp)
        except Exception as e:
            print(f"❌ Business Analyst упал: {e}")
            return

        print("⚙️  System Analyst ...")
        try:
            sa_resp = ask_agent(
                logger, "system_analyst",
                f"Запрос:\n{task}\n\nТЗ от БА:\n{json.dumps(ba_resp, ensure_ascii=False, indent=2)}",
                cache, language=language,
            )
        except Exception as e:
            print(f"❌ System Analyst упал: {e}")
            return

        print("🏗️  Architect ...")
        arch_resp: dict = {}
        arch_attempt = 0
        while arch_attempt < 5:
            try:
                arch_resp = ask_agent(
                    logger, "architect",
                    (
                        f"Запрос:\n{task}\n\n"
                        f"Спецификация от SA:\n{json.dumps(sa_resp, ensure_ascii=False, indent=2)}\n\n"
                        f"Целевой язык: {LANG_DISPLAY.get(language, language)}"
                    ),
                    cache, arch_attempt, randomize_models, language,
                )
                if phase_validate_architecture(
                    logger, project_path, None, cache, stats,
                    arch_resp, sa_resp, task, language, randomize_models,
                ):
                    break
                arch_attempt += 1
                print(f"🔄 Перегенерация архитектуры (попытка {arch_attempt}/5) ...")
            except Exception as e:
                print(f"❌ Architect упал: {e}")
                arch_attempt += 1

        if arch_attempt >= 5:
            print("❌ Не удалось валидировать архитектуру за 5 попыток.")
            return

        deps       = arch_resp.get("dependencies", [])
        files_raw  = arch_resp.get("files", [])
        files_list = sanitize_files_list(files_raw)

        files_list, entry_point = _init_project_files(
            project_path, project_name, language,
            deps, files_list, arch_resp, ba_resp, sa_resp, task,
        )

        state = {
            "task":                 task,
            "business_requirements": ba_resp,
            "system_specs":         sa_resp,
            "architecture":         arch_resp.get("architecture", ""),
            "files":                files_list,
            "approved_files":       [],
            "feedbacks":            {f: "" for f in files_list},
            "file_attempts":        {},
            "spec_history":         [],
            "env_fixes":            {},
            "phase_fail_counts":    {},
            "iteration":            1,
            "max_iters":            2000,
            "language":             language,
            "entry_point":          entry_point,
            "last_phase":           "initial",
            # Флаги фаз для Supervisor
            "e2e_passed":           False,
            "integration_passed":   False,
            "tests_passed":         False,
            "document_generated":   False,
        }
        save_state(project_path, state)
        save_cache(project_path, cache)
        git_commit(project_path, "Initial architecture")

    # Привязываем контекст для signal handler
    _ctx.bind(project_path, state)

    # ── Главный цикл ─────────────────────────────────────────────────────────
    e2e_attempt = 0

    while True:
        # Абсолютный потолок
        if state["iteration"] > MAX_ABSOLUTE_ITERS:
            print(f"\n🛑 Достигнут абсолютный потолок {MAX_ABSOLUTE_ITERS} итераций. Завершение.")
            stats.print_report()
            return

        if state["iteration"] > state["max_iters"]:
            if input_with_timeout(
                f"⚠️  Лимит {state['max_iters']} итераций. Дать ещё 15? (y/n): ",
                WAIT_TIMEOUT, "y"
            ).lower() == "y":
                state["max_iters"] += 15
                save_state(project_path, state)
            else:
                stats.print_report()
                return

        # Спрашиваем Supervisor
        decision   = ask_supervisor(logger, state, cache, randomize_models, language)
        next_phase = decision.get("next_phase", "develop")
        confidence = decision.get("confidence", 0)
        reason     = decision.get("reason", "")

        print(f"\n{'─' * 50}")
        print(f"🧭 SUPERVISOR → {next_phase.upper()} (уверенность: {confidence}%) | {reason}")
        state["last_phase"] = next_phase
        save_state(project_path, state)

        # ── Диспетчер фаз ────────────────────────────────────────────────────
        if next_phase == "develop":
            phase_develop(logger, project_path, state, cache, stats, randomize=randomize_models)
            _reset_phase_fail(state, "develop")

        elif next_phase == "e2e_review":
            if not phase_e2e_review(logger, project_path, state, cache, stats, e2e_attempt, randomize=randomize_models):
                fails = _bump_phase_fail(state, "e2e_review")
                e2e_attempt += 1
                if fails >= 3:
                    print("⚠️  E2E падает 3 раза подряд → принудительный revise_spec.")
                    problem = "E2E Review падает несколько итераций подряд. Возможны архитектурные противоречия."
                    revise_spec(logger, project_path, state, cache, problem, randomize_models)
                    state["max_iters"] += 5
            else:
                state["e2e_passed"] = True
                e2e_attempt = 0
                _reset_phase_fail(state, "e2e_review")

        elif next_phase == "integration_test":
            if not phase_integration_test(logger, project_path, state, cache, stats, randomize=randomize_models):
                _bump_phase_fail(state, "integration_test")
                # integration_test сам сбрасывает approved при ошибке
            else:
                state["integration_passed"] = True
                _reset_phase_fail(state, "integration_test")

        elif next_phase == "unit_tests":
            if not phase_unit_tests(logger, project_path, state, cache, stats, randomize=randomize_models):
                _bump_phase_fail(state, "unit_tests")
            else:
                state["tests_passed"] = True
                _reset_phase_fail(state, "unit_tests")

        elif next_phase == "document":
            phase_document(logger, project_path, state, cache, randomize=randomize_models)
            state["document_generated"] = True

        elif next_phase == "revise_spec":
            problem = input("Опишите противоречие (или Enter для авто): ").strip() or "Авто-эскалация от Supervisor"
            revise_spec(logger, project_path, state, cache, problem, randomize_models)
            state["max_iters"] += 10

        elif next_phase == "success":
            git_commit(project_path, f"Successful build: iteration {state['iteration']}")
            print_iteration_table(state)
            generate_summary(project_path, state)

            # Финальная сводка
            print("\n" + "═" * 80)
            print(f"{'🎉 УСПЕХ! Проект готов (v14.0) 🎉':^80}")
            print("═" * 80)
            print(f"📂 Папка      : {project_path}")
            print(f"🌍 Язык       : {LANG_DISPLAY.get(language, language)}")
            print(f"🔢 Итераций   : {state['iteration']}")
            print(f"📄 Файлов     : {len(state['files'])}")
            print(f"🧪 Unit-тесты + покрытие ≥ {MIN_COVERAGE}%")
            print(f"🚀 Docker-ready")
            print("\n📋 Запуск:")
            run_cmd = get_execution_command(language, state.get("entry_point", "main.py"))
            print(f"   docker run --rm -v $(pwd):/app -w /app {get_docker_image(language)} bash -c '{run_cmd}'")
            print("═" * 80)
            stats.print_report()

            act = input_with_timeout(
                f"\nЧто дальше?\n  Enter — принять\n  r — доработать файл\n  spec — пересмотреть спецификацию\n"
                f"👉 [авто через {WAIT_TIMEOUT}с]: ",
                WAIT_TIMEOUT, ""
            ).lower()

            if act == "r":
                target   = input("Файл (main.py): ").strip() or state.get("entry_point", "main.py")
                feedback = input(f"Правки для {target}: ").strip()
                if not feedback:
                    print("Пустые правки — пропускаю.")
                else:
                    if target not in state["files"]:
                        state["files"].append(target)
                        state["feedbacks"][target] = ""
                    if target in state.get("approved_files", []):
                        state["approved_files"].remove(target)
                    state["feedbacks"][target] = f"Требование заказчика: {feedback}"
                    state["file_attempts"][target] = 0
                    # Сбрасываем флаги последующих фаз
                    state["e2e_passed"] = state["integration_passed"] = \
                        state["tests_passed"] = state["document_generated"] = False
                    state["max_iters"] += 5
                    save_state(project_path, state)
            elif act == "spec":
                problem = input("Опишите противоречие: ").strip() or "Запрос заказчика"
                revise_spec(logger, project_path, state, cache, problem, randomize_models)
                state["e2e_passed"] = state["integration_passed"] = \
                    state["tests_passed"] = state["document_generated"] = False
                state["max_iters"] += 10
                save_state(project_path, state)
            else:
                print("✅ Готово. Можно пить кофе ☕")
                return

        else:
            # Неизвестная фаза — безопасный fallback
            logger.warning(f"Неизвестная фаза от Supervisor: '{next_phase}'. Fallback → develop.")
            phase_develop(logger, project_path, state, cache, stats, randomize=randomize_models)

        save_cache(project_path, cache)
        save_state(project_path, state)
        state["iteration"] += 1
        save_state(project_path, state)
        print_iteration_table(state)


if __name__ == "__main__":
    main()
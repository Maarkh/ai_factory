import logging
import queue
import random
import sys
import threading
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import FACTORY_DIR, LOGS_DIR, LOG_LEVEL, LOG_FILE_MAX_BYTES, LOG_INTERACTION_CHARS
from models_pool import MODEL_POOLS, DEFAULT_MODEL


def get_model(agent: str, attempt: int = 0, randomize: bool = False) -> str:
    pool = MODEL_POOLS.get(agent, [DEFAULT_MODEL])
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
    """Логи пишутся в .factory/logs/. Консоль — через StreamHandler на root logger."""
    logs_dir = project_path / FACTORY_DIR / LOGS_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(str(project_path))
    if logger.handlers:
        return logger

    level = logging.getLevelName(LOG_LEVEL)
    if not isinstance(level, int):
        level = logging.INFO
    logger.setLevel(logging.DEBUG)

    # Файловый обработчик (DEBUG — все детали)
    file_handler = RotatingFileHandler(
        logs_dir / "agent_interactions.log",
        maxBytes=LOG_FILE_MAX_BYTES,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(file_handler)

    # Консольный обработчик на root logger — виден и модульным логгерам (infra, state, …)
    root = logging.getLogger()
    if not any(type(h) is logging.StreamHandler for h in root.handlers):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        root.addHandler(console_handler)
        root.setLevel(level)

    return logger


def log_interaction(
    logger: logging.Logger, agent: str, model: str,
    prompt: str, response: str, max_chars: int = LOG_INTERACTION_CHARS
) -> None:
    sep = "=" * 50
    logger.debug(
        f"\n{sep}\nАГЕНТ: {agent} | МОДЕЛЬ: {model}\n"
        f"--- PROMPT ---\n{prompt[:max_chars]}\n"
        f"--- RESPONSE ---\n{response[:max_chars]}\n{sep}"
    )


def log_runtime_error(project_path: Path, stderr: str) -> None:
    """Ошибки рантайма — в .factory/logs/."""
    logs_dir = project_path / FACTORY_DIR / LOGS_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)
    with open(logs_dir / "run_errors.log", "a", encoding="utf-8") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n[{ts}] SYSTEM CRASH:\n{stderr}\n{'-' * 40}\n")

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# КОНФИГУРАЦИЯ — значения из окружения (.env)
# ─────────────────────────────────────────────

BASE_DIR     = Path(os.getenv("PROJECT_BASE_DIR", "/media/mikhail/RAD/py_proj"))
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1/")
LLM_API_KEY  = os.getenv("LLM_API_KEY",  "ollama")
LLM_TIMEOUT  = float(os.getenv("LLM_TIMEOUT", "120.0"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "16384"))
LOG_LEVEL    = os.getenv("LOG_LEVEL", "INFO")

# ─────────────────────────────────────────────
# Параметры пайплайна (не секреты — хардкод OK)
# ─────────────────────────────────────────────

WAIT_TIMEOUT        = 30
RUN_TIMEOUT         = 6_000
MAX_CONTEXT_CHARS   = 60_000
MIN_COVERAGE        = 40
MAX_ABSOLUTE_ITERS  = 500
MAX_FILE_ATTEMPTS   = 15
MAX_TEST_ATTEMPTS   = 6      # Попытки регенерации тестов перед де-аппрувом кода
MAX_PHASE_TOTAL_FAILS = 90   # Абсолютный потолок фейлов одной фазы за весь проект
MAX_SPEC_REVISIONS    = 9    # Максимум пересмотров спецификации за проект
MAX_FEEDBACK_HISTORY = 3
FLUSH_EVERY = 20  # сбрасывать на диск каждые N записей

# Папки внутри project_path
FACTORY_DIR   = ".factory"       # метаданные — скрыто от Git и Docker
SRC_DIR       = "src"            # исходный код — чистый контекст
ARTIFACTS_DIR = "artifacts"      # A0–A10 внутри .factory/
LOGS_DIR      = "logs"           # логи взаимодействия агентов
CACHEABLE_AGENTS = {"business_analyst", "system_analyst", "architect", "documenter"}

ARTIFACT_LABELS = {
    "A0": "user_intent",
    "A1": "business_requirements",
    "A2": "system_specification",
    "A3": "architecture_map",
    "A4": "file_structure",
    "A5": "api_contract",
    "A6": "db_schema",
    "A7": "test_suite_plan",
    "A8": "ops_manifest",
    "A9": "implementation_logs",
    "A10": "final_summary",
}
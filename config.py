import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# КОНФИГУРАЦИЯ — значения из окружения (.env)
# ─────────────────────────────────────────────

BASE_DIR     = Path(os.getenv("PROJECT_BASE_DIR", "/media/mikhail/RAD/py_proj"))
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434")
LLM_API_KEY  = os.getenv("LLM_API_KEY",  "ollama")
LLM_TIMEOUT  = float(os.getenv("LLM_TIMEOUT", "300.0"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "16384"))
LLM_NUM_CTX    = int(os.getenv("LLM_NUM_CTX", "16384"))
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
MAX_CUMULATIVE      = MAX_FILE_ATTEMPTS * 3  # Суммарных попыток до force-approve
MAX_TEST_ATTEMPTS   = 6      # Попытки регенерации тестов перед де-аппрувом кода
MAX_PHASE_TOTAL_FAILS = 90   # Абсолютный потолок фейлов одной фазы за весь проект
MAX_SPEC_REVISIONS    = 9    # Максимум пересмотров спецификации за проект
MAX_FEEDBACK_HISTORY = 5     # Сколько одинаковых feedback до auto-approve (3 было слишком мало)
MAX_A5_PATCHES_PER_FILE = 2   # Лимит патч-ресетов контракта A5 на файл
MAX_ITERS_DEFAULT       = 200 # Начальный max_iters для нового проекта
MAX_ITERS_INCREMENT     = 15  # Добавляем к max_iters при запросе продолжения
MAX_LLM_RETRIES         = 5   # Число retry для ask_agent (5xx нужен запас на рестарт)
SELF_REFLECT_RETRIES    = 1   # max_retries для self_reflect (модель слабая)
FLUSH_EVERY = 20              # сбрасывать на диск каждые N записей

# Пороги безопасности фаз (сколько провалов до пропуска/эскалации)
MAX_ARCH_ATTEMPTS       = 5   # Попытки генерации архитектуры
MAX_A5_REVIEW_ATTEMPTS  = 3   # Попытки ревью A5 контракта
DEVELOP_STALL_THRESHOLD = 6   # develop без прогресса → revise_spec
E2E_TOTAL_SKIP          = 6   # E2E суммарных провалов → пропуск
E2E_CONSECUTIVE_REVISE  = 3   # E2E подряд → revise_spec
INTEGRATION_TOTAL_SKIP  = 4   # Integration суммарных провалов → пропуск
UNIT_TEST_TOTAL_SKIP    = 3   # Unit test суммарных провалов → пропуск
ITERS_BUMP_REVISE       = 10  # max_iters += N после revise_spec
ITERS_BUMP_SMALL        = 5   # max_iters += N при minor escalation

# ─────────────────────────────────────────────
# Лимиты отображения/усечения (символы)
# ─────────────────────────────────────────────
TRUNCATE_FEEDBACK  = 300      # усечение feedbacks в логах
TRUNCATE_CODE      = 3000     # усечение кода разработчика для контекста
TRUNCATE_LOG       = 2000     # усечение stdout/stderr в логах
TRUNCATE_ERROR_MSG = 400      # усечение текста ошибки в ValueError
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB ротация лог-файлов
LOG_INTERACTION_CHARS = 2000  # усечение в log_interaction

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
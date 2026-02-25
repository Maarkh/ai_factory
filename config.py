from pathlib import Path

# ─────────────────────────────────────────────
# КОНФИГУРАЦИЯ
# ─────────────────────────────────────────────

BASE_DIR            = Path("/media/mikhail/RAD/py_proj")
WAIT_TIMEOUT        = 30
RUN_TIMEOUT         = 6_000
MAX_CONTEXT_CHARS   = 60_000
MIN_COVERAGE        = 40
MAX_ABSOLUTE_ITERS  = 30000
MAX_FILE_ATTEMPTS   = 40
MAX_PHASE_TOTAL_FAILS = 50   # Абсолютный потолок фейлов одной фазы за весь проект

# Папки внутри project_path
FACTORY_DIR   = ".factory"       # метаданные — скрыто от Git и Docker
SRC_DIR       = "src"            # исходный код — чистый контекст
ARTIFACTS_DIR = "artifacts"      # A0–A10 внутри .factory/
LOGS_DIR      = "logs"           # логи взаимодействия агентов
CACHEABLE_AGENTS = {"business_analyst", "system_analyst", "architect", "documenter"}
# Запуск AI Factory

## Требования

- **Python 3.11+**
- **Docker** — для запуска сгенерированного кода в изолированных контейнерах
- **Ollama** — локальный LLM сервер

## 1. Установка Docker

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y docker.io
sudo systemctl start docker
sudo usermod -aG docker $USER
# Перелогиньтесь для применения группы
```

Проверка: `docker version`

## 2. Установка Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Проверка: `ollama --version`

## 3. Загрузка моделей

По умолчанию система использует две модели:

```bash
ollama pull deepseek-coder:6.7b
ollama pull qwen3:latest
```

Модели можно переопределить через `.env` (см. раздел "Конфигурация").

## 4. Настройка окружения

```bash
cd ai_factory

# Создание виртуального окружения
python -m venv .venv_factory
source .venv_factory/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Копирование конфигурации
cp .env.example .env
# Отредактируйте .env — укажите PROJECT_BASE_DIR
```

## 5. Запуск

```bash
source .venv_factory/bin/activate
python ai_factory.py
```

Система запросит:
1. Подтверждение запуска (`yes`)
2. Режим ротации моделей (`n` для стандартного)
3. Имя проекта (латиница, например `my_app`)
4. Язык (`python` / `typescript` / `rust`)
5. Описание задачи

## Конфигурация (.env)

| Переменная | По умолчанию | Описание |
|---|---|---|
| `PROJECT_BASE_DIR` | `/media/mikhail/RAD/py_proj` | Корневая папка для проектов |
| `LLM_BASE_URL` | `http://localhost:11434/v1/` | URL Ollama API |
| `LLM_API_KEY` | `ollama` | API ключ (для Ollama — любой) |
| `LLM_TIMEOUT` | `300.0` | Таймаут LLM запроса (секунды) |
| `LLM_MAX_TOKENS` | `16384` | Макс. токенов в ответе |
| `LOG_LEVEL` | `INFO` | Уровень логирования |
| `FACTORY_DEFAULT_MODEL` | `deepseek-coder:6.7b` | Модель по умолчанию |
| `FACTORY_MODEL_<AGENT>` | — | Переопределение модели для агента |

### Переопределение моделей по агентам

Каждый из 24 агентов можно настроить отдельно через `.env`:

```bash
# Пример: использовать 32B модель для developer
FACTORY_MODEL_DEVELOPER=qwen2.5-coder:32b
FACTORY_MODEL_DEVELOPER_PATCH=qwen2.5-coder:32b

# Использовать другую модель для ревьюера
FACTORY_MODEL_REVIEWER=deepseek-coder-v2:16b
```

Список агентов: `developer`, `developer_patch`, `reviewer`, `e2e_architect`, `e2e_qa`,
`qa_runtime`, `business_analyst`, `system_analyst`, `architect`, `spec_reviewer`,
`test_generator`, `documenter`, `devops_runtime`, `arch_validator`, `supervisor`,
`self_reflect`, `contract_analyst`, `a5_validator`, `a5_business_reviewer`,
`a5_architect_reviewer`, `a5_contract_reviewer`.

## Структура проекта на выходе

```
<project_name>/
├── src/                  # Исходный код (чистый контекст для Docker)
│   ├── main.py           # Точка входа
│   ├── *.py              # Модули проекта
│   ├── requirements.txt  # Зависимости
│   └── tests/            # Unit-тесты
├── .factory/             # Метаданные (скрыты от Git)
│   ├── artifacts/        # A0-A10 артефакты
│   ├── logs/             # Логи агентов
│   ├── state.json        # Состояние пайплайна
│   └── cache.json        # Кэш ответов LLM
├── ARCHITECTURE.md       # Архитектура проекта
└── .gitignore
```

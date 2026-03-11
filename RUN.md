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

### Настройка моделей и серверов

Вся конфигурация моделей — в файле `models_pool.py`. Каждый агент имеет запись
с моделью, URL сервера, ключом и параметрами.

Для локальной модели:
```python
"developer": [_local("deepseek-coder:6.7b")],
```

Для модели на удалённом сервере:
```python
"developer": [_remote("qwen3:32b",
                       url="http://work-server:11434/v1/",
                       key="secret",
                       timeout=600,
                       max_tokens=32768,
                       num_ctx=32768)],
```

Откройте `models_pool.py` и замените `_local()` на `_remote()` для нужных агентов.
Агенты с одинаковым URL переиспользуют одно соединение.

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

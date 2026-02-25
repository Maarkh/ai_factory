"""
Иерархия исключений ai_factory.
"""


class FactoryError(Exception):
    """Базовое исключение фабрики."""


class LLMError(FactoryError):
    """Ошибки LLM-вызовов: API, таймаут, невалидный JSON."""


class DockerError(FactoryError):
    """Ошибки Docker: сборка, запуск, таймаут контейнера."""


class StateError(FactoryError):
    """Ошибки сохранения/загрузки состояния проекта."""


class SpecError(FactoryError):
    """Ошибки валидации контракта/спецификации."""

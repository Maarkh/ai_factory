import json
import re
from typing import Any, TypeVar

from config import TRUNCATE_ERROR_MSG

T = TypeVar("T")


def parse_if_str(value: Any, expected_type: type[T], fallback: T) -> T:
    """Если value — строка, пробует json.loads. Если тип не совпал — возвращает fallback."""
    if isinstance(value, expected_type):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, expected_type):
                return parsed
        except json.JSONDecodeError:
            pass
    return fallback


def to_str(value: Any) -> str:
    """Приводит любое значение к строке — защита от dict/list в полях feedback."""
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def safe_contract(state: dict) -> dict:
    """
    Возвращает api_contract как правильно типизированный dict.
    Защищает от строк на всех уровнях вложенности — модели иногда
    возвращают {"global_imports": "[]"} или {"file_contracts": "{}"}.
    Исправляет state на месте.
    """
    raw = state.get("api_contract")
    contract = parse_if_str(raw, dict, {})

    # Нормализуем file_contracts: должен быть dict[str, list]
    fc = parse_if_str(contract.get("file_contracts"), dict, {})
    for fname in list(fc.keys()):
        fc[fname] = parse_if_str(fc[fname], list, [])
    contract["file_contracts"] = fc

    # Нормализуем global_imports: должен быть dict[str, list]
    gi = parse_if_str(contract.get("global_imports"), dict, {})
    for fname in list(gi.keys()):
        gi[fname] = parse_if_str(gi[fname], list, [])
    contract["global_imports"] = gi

    state["api_contract"] = contract
    return contract


def repair_json(text: str) -> str:
    text = re.sub(r',\s*([}\]])', r'\1', text)
    text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
    return text


def repair_truncated_json(text: str) -> dict | None:
    """Пытается починить обрезанный JSON (модель исчерпала max_tokens).

    Стратегия: закрыть незавершённую строку, затем закрыть все открытые скобки.
    """
    # Определяем, находимся ли мы внутри строки
    in_string = False
    escape_next = False
    stack = []  # стек открытых скобок: '{' или '['

    for ch in text:
        if escape_next:
            escape_next = False
            continue
        if ch == '\\' and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch in ('{', '['):
            stack.append(ch)
        elif ch == '}' and stack and stack[-1] == '{':
            stack.pop()
        elif ch == ']' and stack and stack[-1] == '[':
            stack.pop()

    if not stack:
        return None  # скобки сбалансированы — не наш случай

    # Собираем suffix для закрытия
    suffix = ""
    if in_string:
        suffix += '"'
    # Закрываем все открытые скобки в обратном порядке
    for bracket in reversed(stack):
        suffix += '}' if bracket == '{' else ']'

    candidate = text + suffix
    try:
        result = json.loads(candidate)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    try:
        result = json.loads(repair_json(candidate))
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    return None


def extract_json_from_text(text: str) -> dict:
    """Надёжный парсер: учитывает строковые литералы с {} внутри и markdown-блоки."""
    text = text.strip()
    if not text:
        raise ValueError("Пустой ответ от модели")

    # Извлекаем JSON из markdown-блоков ```json ... ``` или ``` ... ```
    md_match = re.search(r"```(?:json)?\s*(\{[\s\S]*\})\s*```", text)
    if md_match:
        try:
            return json.loads(md_match.group(1))
        except json.JSONDecodeError:
            try:
                return json.loads(repair_json(md_match.group(1)))
            except json.JSONDecodeError:
                pass

    if text.startswith("{") and text.endswith("}"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    start = text.find("{")
    if start == -1:
        raise ValueError(f"JSON не найден в ответе: {text[:TRUNCATE_ERROR_MSG]}")

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
        # Попытка починить обрезанный JSON (модель исчерпала max_tokens)
        truncated = text[start:]
        repaired = repair_truncated_json(truncated)
        if repaired is not None:
            return repaired
        raise ValueError("Несбалансированные JSON-скобки")

    candidate = text[start:end]

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    try:
        return json.loads(repair_json(candidate))
    except json.JSONDecodeError:
        pass

    try:
        import json_repair  # type: ignore
        repaired = json_repair.loads(candidate)
        if isinstance(repaired, dict) and repaired:
            return repaired
    except (ImportError, Exception):
        pass

    raise ValueError(f"Не удалось извлечь JSON: {text[:TRUNCATE_ERROR_MSG]}...")

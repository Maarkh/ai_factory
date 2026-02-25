import json
import logging
from pathlib import Path

from llm import ask_agent
from json_utils import _parse_if_str
from artifacts import save_artifact
from lang_utils import LANG_DISPLAY
from log_utils import get_model
from cache import ThreadSafeCache
from stats import ModelStats


def _validate_and_patch_contract(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    contract: dict,
    files: list[str],
    randomize: bool = False,
) -> dict:
    """
    Проверяет что все файлы из списка присутствуют в контракте.
    Для отсутствующих файлов запрашивает контракт отдельно.
    Защита от неполной генерации contract_analyst.
    """
    language = state.get("language", "python")
    fc = contract.setdefault("file_contracts", {})
    gi = contract.setdefault("global_imports", {})

    missing = [f for f in files if f not in fc or not fc[f]]
    if not missing:
        return contract

    print(f"⚠️  A5 неполный — отсутствуют контракты для: {', '.join(missing)}")

    for fname in missing:
        print(f"   🔧 Запрашиваю контракт для {fname} ...")
        # Контекст: задача + архитектура + уже известные контракты других файлов
        existing_contracts = {k: v for k, v in fc.items() if k != fname}
        ctx = (
            f"Запрос: {state['task']}\n\n"
            f"Системная спецификация (A2):\n"
            f"{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
            f"Архитектура:\n{json.dumps(state.get('architecture', {}), ensure_ascii=False, indent=2)}\n\n"
            f"Язык: {LANG_DISPLAY.get(language, language)}\n\n"
            f"Уже сгенерированные контракты других файлов:\n"
            f"{json.dumps(existing_contracts, ensure_ascii=False, indent=2)}\n\n"
            f"ЗАДАЧА: Сгенерируй API контракт ТОЛЬКО для файла `{fname}`.\n"
            f"Верни JSON с ключами file_contracts и global_imports только для этого файла."
        )
        try:
            patch = ask_agent(logger, "contract_analyst", ctx, cache, 0, randomize, language)
            patch_fc = _parse_if_str(patch.get("file_contracts", {}), dict, {})
            patch_gi = _parse_if_str(patch.get("global_imports", {}), dict, {})

            # Берём контракт для нашего файла — или весь ответ если ключ не совпал
            file_contract = patch_fc.get(fname) or next(iter(patch_fc.values()), [])
            file_imports  = patch_gi.get(fname)  or next(iter(patch_gi.values()),  [])

            if file_contract:
                fc[fname] = _parse_if_str(file_contract, list, [])
                gi[fname] = _parse_if_str(file_imports,  list, [])
                print(f"   ✅ Контракт для {fname} получен ({len(fc[fname])} функций).")
                stats.record("contract_analyst", get_model("contract_analyst"), True)
            else:
                print(f"   ⚠️  Контракт для {fname} пустой — разработчик будет работать без него.")
                stats.record("contract_analyst", get_model("contract_analyst"), False)
        except Exception as e:
            logger.exception(f"Патч контракта для {fname} упал: {e}")
            stats.record("contract_analyst", get_model("contract_analyst"), False)

    contract["file_contracts"] = fc
    contract["global_imports"]  = gi
    return contract


def phase_generate_api_contract(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    arch_resp: dict,
    sa_resp: dict,
    randomize: bool = False,
) -> dict:
    """
    Новая фаза v15.0: генерирует A5 (API & Contract Spec).
    Developer получает явный контракт функций вместо «угадывания».
    """
    language = state.get("language", "python")
    print("📋 Contract Analyst генерирует A5 (API контракт) ...")

    ctx = (
        f"Запрос: {state['task']}\n\n"
        f"Системная спецификация (A2):\n{json.dumps(sa_resp, ensure_ascii=False, indent=2)}\n\n"
        f"Архитектура (A3/A4):\n{json.dumps(arch_resp, ensure_ascii=False, indent=2)}\n\n"
        f"Язык: {LANG_DISPLAY.get(language, language)}\n\n"
        f"Файлы: {arch_resp.get('files', [])}"
    )

    try:
        contract = ask_agent(logger, "contract_analyst", ctx, cache, 0, randomize, language)
        # Гарантируем, что контракт — это dict с нужными ключами
        if not isinstance(contract, dict):
            contract = {}
        contract.setdefault("file_contracts", {})
        contract.setdefault("global_imports", {})
        stats.record("contract_analyst", get_model("contract_analyst"), True)
        # Валидация: все файлы должны иметь контракт
        files_list = [f.get("path", f) if isinstance(f, dict) else f
                      for f in arch_resp.get("files", state.get("files", []))]
        contract = _validate_and_patch_contract(
            logger, project_path, state, cache, stats, contract, files_list, randomize
        )
        save_artifact(project_path, "A5", contract)
        print("✅ A5 (API контракт) готов.")
        return contract
    except Exception as e:
        logger.exception(f"Contract Analyst упал: {e}")
        stats.record("contract_analyst", get_model("contract_analyst"), False)
        print(f"⚠️  Contract Analyst не справился: {e}. Контракт будет пустым.")
        return {"file_contracts": {}, "global_imports": {}}


def _refresh_api_contract(
    logger: logging.Logger,
    project_path: Path,
    state: dict,
    cache: ThreadSafeCache,
    stats: ModelStats,
    randomize: bool = False,
) -> None:
    """
    Каскад v15.0: после обновления A2 пересчитывает A5.
    Вызывается из revise_spec().
    """
    language = state.get("language", "python")
    print("🔄 Каскадное обновление A5 после изменения A2 ...")
    ctx = (
        f"Запрос: {state['task']}\n\n"
        f"Обновлённая спецификация (A2):\n{json.dumps(state.get('system_specs', {}), ensure_ascii=False, indent=2)}\n\n"
        f"Файлы: {state.get('files', [])}\n\n"
        f"Язык: {LANG_DISPLAY.get(language, language)}"
    )
    try:
        new_contract = ask_agent(logger, "contract_analyst", ctx, cache, 0, randomize, language)
        if not isinstance(new_contract, dict):
            new_contract = {}
        new_contract.setdefault("file_contracts", {})
        new_contract.setdefault("global_imports", {})
        # Валидация: все файлы должны иметь контракт
        new_contract = _validate_and_patch_contract(
            logger, project_path, state, cache, stats,
            new_contract, state.get("files", []), randomize
        )
        state["api_contract"] = new_contract
        save_artifact(project_path, "A5", new_contract)
        print("✅ A5 обновлён каскадно.")
    except Exception as e:
        logger.exception(f"Каскадное обновление A5 упало: {e}")
        print(f"⚠️  Не удалось обновить A5: {e}")

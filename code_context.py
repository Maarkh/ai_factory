import ast
import os
import re
import sys
from collections import defaultdict, deque
from pathlib import Path

from config import MAX_CONTEXT_CHARS


def _levenshtein_close(a: str, b: str) -> bool:
    """Проверка: compound-имена похожи (общие сегменты по '_').

    vehicle_processing vs video_processing → True (общий сегмент 'processing')
    numpy vs video_processing → False
    """
    parts_a = set(a.split("_"))
    parts_b = set(b.split("_"))
    common = parts_a & parts_b
    # Считаем похожим если есть хотя бы 1 общий значимый сегмент (>2 символов)
    return any(len(p) > 2 for p in common)


def extract_public_api(code: str) -> str:
    """Извлекает публичный API файла: импорты, классы, функции, публичные переменные."""
    api_lines: list[str] = []
    total = 0
    PUBLIC_PREFIXES = (
        "import ", "from ", "class ", "def ",
        "fn ", "pub fn ", "pub struct ", "pub enum ",
        "export ", "const ", "let ", "function ",
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
    src_path: Path,
    files: list[str],
    exclude: str | None = None,
) -> str:
    """Читает файлы из src_path и возвращает их публичный API в виде строки."""
    parts: list[str] = []
    total = 0
    for fname in files:
        if exclude is not None and fname == exclude:
            continue
        fpath = src_path / fname
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


def get_full_context(
    src_path: Path,
    files: list[str],
) -> str:
    """Читает ПОЛНЫЙ код файлов для E2E ревью (не только API)."""
    parts: list[str] = []
    total = 0
    for fname in files:
        fpath = src_path / fname
        if not fpath.exists():
            continue
        code = fpath.read_text(encoding="utf-8")
        chunk = f"\n--- {fname} ---\n{code}\n"
        if total + len(chunk) > MAX_CONTEXT_CHARS:
            remaining = MAX_CONTEXT_CHARS - total
            if remaining > 200:
                parts.append(chunk[:remaining] + "\n[... обрезано ...]")
            break
        parts.append(chunk)
        total += len(chunk)
    return "".join(parts)


def build_dependency_order(files: list[str], src_path: Path) -> list[str]:
    """Возвращает файлы в порядке топологической сортировки по импортам."""
    graph: dict[str, list[str]]  = defaultdict(list)
    indegree: dict[str, int]     = {f: 0 for f in files}
    file_set = set(files)

    for f in files:
        fpath = src_path / f
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
    """Определяет файл с ошибкой по traceback. Возвращает имя файла или files[0]."""
    combined = stderr + "\n" + stdout
    # Python: File "path/file.py", line N
    for match in re.findall(r'File "([^"]+)", line \d+', combined):
        candidate = os.path.basename(match)
        if candidate in files:
            return candidate
    # TypeScript/Node: at ... (file.ts:10:5) or at ... file.js:10:5
    for match in re.findall(r'[( ]([\w/\-\.]+\.(?:ts|js|tsx|jsx)):\d+:\d+', combined):
        candidate = os.path.basename(match)
        if candidate in files:
            return candidate
    # Rust: --> src/file.rs:10:5 or src/file.rs:10
    for match in re.findall(r'(?:-->|error\[).*?([\w/\-\.]+\.rs):\d+', combined):
        candidate = match  # Rust paths are often relative like src/main.rs
        if candidate in files:
            return candidate
        candidate = os.path.basename(match)
        if candidate in files:
            return candidate
    # Generic: FAILED/ERROR pattern
    for match in re.findall(r'(?:FAILED|ERROR)\s+([\w/]+\.\w+)', combined):
        src = os.path.basename(match).replace("test_", "")
        if src in files:
            return src
    return files[0] if files else "main.py"


# ─────────────────────────────────────────────
# Детерминистская валидация импортов
# ─────────────────────────────────────────────

# Маппинг pip-пакет → import-имя (для пакетов, где они различаются)
_PIP_TO_IMPORT: dict[str, str] = {
    "opencv-python":            "cv2",
    "opencv-python-headless":   "cv2",
    "opencv-contrib-python":    "cv2",
    "opencv-contrib-python-headless": "cv2",
    "pillow":                   "PIL",
    "scikit-learn":             "sklearn",
    "scikit-image":             "skimage",
    "python-dateutil":          "dateutil",
    "pyyaml":                   "yaml",
    "beautifulsoup4":           "bs4",
    "python-dotenv":            "dotenv",
    "attrs":                    "attr",
    "python-jose":              "jose",
    "python-multipart":         "multipart",
    "msgpack-python":           "msgpack",
    "ruamel.yaml":              "ruamel",
}


def _parse_requirements(path: Path) -> set[str]:
    """Парсит requirements.txt и возвращает множество допустимых import-имён."""
    if not path.exists():
        return set()
    result: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Убираем маркеры окружения: requests ; python_version >= "3.6"
        line = line.split(";")[0].strip()
        # Извлекаем имя пакета (до ==, >=, <=, ~=, !=, [extras])
        pkg = re.split(r"[=<>~!\[]", line)[0].strip()
        if not pkg:
            continue
        pkg_lower = pkg.lower()
        # Нормализация: pip нормализует дефисы в подчёркивания
        pkg_normalized = pkg_lower.replace("-", "_")
        result.add(pkg_normalized)
        # Маппинг pip→import для известных расхождений
        if pkg_lower in _PIP_TO_IMPORT:
            result.add(_PIP_TO_IMPORT[pkg_lower].lower())
        # Также добавляем оригинальное имя (без нормализации)
        result.add(pkg_lower)
    return result


def _get_stdlib_modules() -> frozenset[str]:
    """Возвращает множество имён стандартной библиотеки Python."""
    if hasattr(sys, "stdlib_module_names"):
        return sys.stdlib_module_names  # Python 3.10+
    # Fallback для Python < 3.10 — основные модули
    return frozenset({
        "abc", "argparse", "ast", "asyncio", "atexit", "base64", "bisect",
        "builtins", "calendar", "cmath", "codecs", "collections", "concurrent",
        "configparser", "contextlib", "copy", "csv", "ctypes", "dataclasses",
        "datetime", "decimal", "difflib", "dis", "email", "encodings", "enum",
        "errno", "faulthandler", "fcntl", "filecmp", "fileinput", "fnmatch",
        "fractions", "ftplib", "functools", "gc", "getpass", "gettext", "glob",
        "gzip", "hashlib", "heapq", "hmac", "html", "http", "idlelib",
        "importlib", "inspect", "io", "ipaddress", "itertools", "json",
        "keyword", "lib2to3", "linecache", "locale", "logging", "lzma",
        "mailbox", "math", "mimetypes", "mmap", "multiprocessing", "netrc",
        "numbers", "operator", "os", "pathlib", "pdb", "pickle", "pkgutil",
        "platform", "plistlib", "poplib", "posixpath", "pprint", "profile",
        "pstats", "py_compile", "pyclbr", "pydoc", "queue", "quopri",
        "random", "re", "readline", "reprlib", "resource", "rlcompleter",
        "runpy", "sched", "secrets", "select", "selectors", "shelve",
        "shlex", "shutil", "signal", "site", "smtplib", "sndhdr", "socket",
        "socketserver", "sqlite3", "ssl", "stat", "statistics", "string",
        "struct", "subprocess", "sunau", "symtable", "sys", "sysconfig",
        "syslog", "tabnanny", "tarfile", "tempfile", "termios", "test",
        "textwrap", "threading", "time", "timeit", "tkinter", "token",
        "tokenize", "tomllib", "trace", "traceback", "tracemalloc", "tty",
        "turtle", "turtledemo", "types", "typing", "unicodedata", "unittest",
        "urllib", "uuid", "venv", "warnings", "wave", "weakref", "webbrowser",
        "wsgiref", "xml", "xmlrpc", "zipapp", "zipfile", "zipimport", "zlib",
        "_thread",
    })


def _find_name_in_classes(code: str, name: str) -> str | None:
    """Ищет имя как метод/атрибут класса в коде. Возвращает имя класса или None.

    Используется для улучшения фидбэка: если `from X import Y` невалиден,
    но Y — метод класса Z в X, подсказываем `from X import Z`.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if item.name == name:
                    return node.name
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == name:
                        return node.name
            elif isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name) and item.target.id == name:
                    return node.name
    return None


def _get_top_level_names(code: str) -> set[str]:
    """Извлекает только TOP-LEVEL определения из Python-кода через AST.

    Обходит ТОЛЬКО tree.body (не вложенные узлы).
    Собирает: FunctionDef.name, ClassDef.name, Assign targets, Import/ImportFrom aliases.
    При SyntaxError — fallback на regex.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        names = set(re.findall(r"^class\s+(\w+)", code, re.MULTILINE))
        names.update(re.findall(r"^def\s+(\w+)", code, re.MULTILINE))
        names.update(re.findall(r"^async\s+def\s+(\w+)", code, re.MULTILINE))
        names.update(re.findall(r"^(\w+)\s*=", code, re.MULTILINE))
        return names

    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, ast.ClassDef):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    names.add(alias.asname or alias.name)
    return names


def _get_all_bound_names(code: str) -> set[str]:
    """Извлекает ВСЕ связанные имена из Python-кода через AST.

    Покрывает: присвоения (на любом уровне вложенности), параметры функций,
    имена классов/функций, for-loop переменные, with-as, except-as, import aliases.
    При SyntaxError — fallback на regex.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        # Fallback: regex с захватом indented assignments
        names = set(re.findall(r"^(?:class|def)\s+(\w+)", code, re.MULTILINE))
        names.update(re.findall(r"^\s*(\w+)\s*=", code, re.MULTILINE))
        return names

    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
            for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
                names.add(arg.arg)
            if node.args.vararg:
                names.add(node.args.vararg.arg)
            if node.args.kwarg:
                names.add(node.args.kwarg.arg)
        elif isinstance(node, ast.ClassDef):
            names.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.asname or alias.name)
    return names


def validate_imports(
    code: str,
    filename: str,
    project_files: list[str],
    requirements_path: Path | None = None,
    language: str = "python",
    src_path: Path | None = None,
) -> list[str]:
    """Детерминистская проверка импортов в сгенерированном коде.

    Проверяет что каждый импортируемый модуль — это:
    - файл проекта (project_files)
    - модуль stdlib
    - пакет из requirements.txt

    Также проверяет циклические импорты (если src_path задан).

    Возвращает список предупреждений (пустой если всё OK).
    """
    if language != "python":
        return []  # Пока только Python

    warnings: list[str] = []
    stdlib = _get_stdlib_modules()
    pip_packages = _parse_requirements(requirements_path) if requirements_path else set()

    # Множество имён проектных модулей (без расширения)
    project_modules = {Path(f).stem for f in project_files}

    # Парсим импорты из кода
    from_imports = re.findall(r"^\s*from\s+(\S+)\s+import", code, re.MULTILINE)
    direct_imports = [imp.rstrip(",") for imp in re.findall(r"^\s*import\s+(\S+)", code, re.MULTILINE)]

    seen: set[str] = set()
    for imp in from_imports + direct_imports:
        # Базовый модуль (до первой точки): from os.path → os
        base = imp.split(".")[0]

        # Relative imports: from .data_models → base="", imp=".data_models"
        # Извлекаем реальное имя модуля
        if base == "":
            # from . import X → пропускаем (текущий пакет)
            rel_module = imp.lstrip(".")
            if not rel_module:
                continue
            # from .data_models import Y → rel_module = "data_models"
            rel_base = rel_module.split(".")[0]
            if rel_base in seen:
                continue
            seen.add(rel_base)
            # Relative import ОБЯЗАН ссылаться на файл проекта
            if rel_base not in project_modules:
                warnings.append(
                    f"relative import 'from {imp} import ...' в {filename}: "
                    f"модуль '{rel_base}' не найден в файлах проекта ({', '.join(project_files)}). "
                    f"Используй абсолютный import или определи класс/функцию в одном из существующих файлов"
                )
            continue

        if base in seen:
            continue
        seen.add(base)

        # 1. Файл проекта?
        if base in project_modules:
            continue

        # 2. Stdlib?
        if base in stdlib:
            continue

        # 3. pip-пакет из requirements.txt?
        base_lower = base.lower()
        base_normalized = base_lower.replace("-", "_")
        if base_lower in pip_packages or base_normalized in pip_packages:
            continue

        # 4. Общеизвестные встроенные модули (typing_extensions, etc.)
        if base.startswith("_"):
            continue

        # Подсказка: если phantom-имя похоже на один из файлов проекта
        hint = ""
        base_lower_nrm = base.lower().replace("-", "_")
        for pm in project_modules:
            # Точное совпадение с учётом типичных ошибок 7B-моделей
            if (base_lower_nrm in pm or pm in base_lower_nrm
                    or _levenshtein_close(base_lower_nrm, pm)):
                hint = f". Возможно, вы имели в виду: from {pm} import ..."
                break
        warnings.append(
            f"import '{base}' в {filename}: не найден в stdlib, "
            f"requirements.txt и файлах проекта ({', '.join(project_files)})"
            f"{hint}"
        )

    # Проверка циклических импортов через граф (1-hop и N-hop)
    if src_path:
        current_stem = Path(filename).stem

        def _get_project_imports(file_stem: str) -> set[str]:
            """Извлекает проектные зависимости из файла."""
            fp = src_path / (file_stem + ".py")
            if not fp.exists():
                return set()
            try:
                fc = fp.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                return set()
            fi = re.findall(r"^\s*from\s+(\S+)\s+import", fc, re.MULTILINE)
            di = re.findall(r"^\s*import\s+(\S+)", fc, re.MULTILINE)
            bases: set[str] = set()
            for imp in fi + di:
                b = imp.split(".")[0]
                if b == "":
                    rel = imp.lstrip(".").split(".")[0]
                    if rel:
                        bases.add(rel)
                else:
                    bases.add(b)
            return bases & project_modules - {file_stem}

        # Строим граф импортов для проектных файлов, доступных текущему файлу
        my_deps = _get_project_imports(current_stem)
        # DFS: ищем путь обратно к current_stem
        visited: set[str] = set()
        stack = [(dep, [current_stem, dep]) for dep in my_deps]
        while stack:
            node, path = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            node_deps = _get_project_imports(node)
            if current_stem in node_deps:
                cycle_path = " → ".join(path + [current_stem])
                warnings.append(
                    f"циклический импорт: {cycle_path} "
                    f"(файлы импортируют друг друга по кругу)"
                )
                break  # Одного цикла достаточно
            for nd in node_deps:
                if nd not in visited:
                    stack.append((nd, path + [nd]))

    # Проверка self-referencing assignments: func = func (до определения)
    self_refs = re.findall(r"^(\w+)\s*=\s*(\w+)\s*(?:#.*)?$", code, re.MULTILINE)
    for lhs, rhs in self_refs:
        if lhs == rhs:
            warnings.append(
                f"бессмысленное присвоение '{lhs} = {lhs}' в {filename}: "
                f"переменная ссылается на саму себя (возможно, пропущен import)"
            )

    # Проверка undefined module references: name.attr где name не импортирован
    # Ловит паттерны вроде: VehicleRecord = data_models.VehicleRecord
    # или: result = some_module.function()
    imported_names = set()
    for imp in from_imports:
        # from X import Y → X импортирован (как модуль)
        base = imp.split(".")[0]
        if base:
            imported_names.add(base)
        else:
            # relative import: from .X import Y → X
            rel = imp.lstrip(".").split(".")[0]
            if rel:
                imported_names.add(rel)
    for imp in direct_imports:
        # import X → X импортирован
        base = imp.split(".")[0]
        if base:
            imported_names.add(base)
    # Добавляем builtins и стандартные имена, которые не требуют import
    imported_names.update({"self", "cls", "super", "type", "print", "len", "range",
                           "str", "int", "float", "bool", "list", "dict", "set",
                           "tuple", "None", "True", "False", "Exception"})
    # Все имена, связанные в файле (def/class/присвоения/параметры на ЛЮБОМ уровне)
    imported_names.update(_get_all_bound_names(code))

    # Ищем name.attr паттерны через AST (не self.X, не cls.X)
    # AST-based подход не ловит ложные срабатывания в строках и комментариях
    seen_refs: set[str] = set()
    try:
        attr_tree = ast.parse(code)
        for node in ast.walk(attr_tree):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                ref_name = node.value.id
                if ref_name in imported_names or ref_name in seen_refs:
                    continue
                if ref_name in stdlib or ref_name in pip_packages:
                    continue
                seen_refs.add(ref_name)
                warnings.append(
                    f"undefined reference '{ref_name}' в {filename}: "
                    f"используется как '{ref_name}.…' но не импортирован "
                    f"(добавь import или from ... import)"
                )
    except SyntaxError:
        pass  # Если код не парсится — пропускаем проверку

    return warnings


def validate_cross_file_names(
    code: str,
    filename: str,
    project_files: list[str],
    src_path: Path,
) -> list[str]:
    """Детерминистская проверка: для каждого `from X import Y` где X — файл проекта,
    проверяет что Y действительно определён на top-level в X.

    Пропускает файлы, которые ещё не существуют на диске.
    Возвращает список предупреждений (пустой если всё ОК).
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    project_stems = {f.removesuffix(".py"): f for f in project_files}
    warnings: list[str] = []
    # Кэш прочитанных файлов: stem → (top_level_names, code) | None
    _cache: dict[str, tuple[set[str], str] | None] = {}

    def _get_for(stem: str) -> tuple[set[str], str] | None:
        if stem in _cache:
            return _cache[stem]
        target_file = project_stems.get(stem)
        if not target_file:
            _cache[stem] = None
            return None
        target_path = src_path / target_file
        if not target_path.exists():
            _cache[stem] = None
            return None
        try:
            target_code = target_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            _cache[stem] = None
            return None
        names = _get_top_level_names(target_code)
        _cache[stem] = (names, target_code)
        return (names, target_code)

    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        module_stem = node.module.split(".")[0]
        if module_stem not in project_stems:
            continue
        # Не проверяем свой же файл
        if project_stems[module_stem] == filename:
            continue
        target_fname = project_stems[module_stem]
        cached = _get_for(module_stem)
        if cached is None:
            continue  # Файл ещё не написан — пропускаем
        target_names, target_code = cached
        for alias in node.names:
            if alias.name == "*":
                continue
            if alias.name not in target_names:
                # Проверяем: может это метод класса в целевом файле?
                owner_class = _find_name_in_classes(target_code, alias.name)
                if owner_class:
                    warnings.append(
                        f"from {module_stem} import {alias.name}: "
                        f"'{alias.name}' — это МЕТОД класса {owner_class} в "
                        f"{project_stems[module_stem]}, а не top-level функция. "
                        f"ИСПРАВЬ: `from {module_stem} import {owner_class}`, "
                        f"затем вызывай `{owner_class}().{alias.name}(...)` или "
                        f"через экземпляр"
                    )
                else:
                    suggestions = sorted(target_names - {"__all__"})[:8]
                    warnings.append(
                        f"from {module_stem} import {alias.name}: "
                        f"'{alias.name}' не определён в {project_stems[module_stem]}. "
                        f"Доступные имена: {', '.join(suggestions) if suggestions else '(пусто)'}"
                    )

    return warnings


# ── Builtins для фильтрации ────────────────────────────────────────────────────

_PYTHON_BUILTINS = {
    "True", "False", "None",
    "int", "float", "str", "bool", "bytes", "bytearray",
    "list", "dict", "set", "tuple", "frozenset",
    "type", "object", "super", "property", "classmethod", "staticmethod",
    "print", "len", "range", "enumerate", "zip", "map", "filter", "sorted",
    "min", "max", "sum", "abs", "round", "pow", "divmod",
    "isinstance", "issubclass", "hasattr", "getattr", "setattr", "delattr",
    "id", "hash", "repr", "format", "chr", "ord",
    "open", "input", "iter", "next", "reversed", "slice",
    "any", "all", "callable", "dir", "vars", "globals", "locals",
    "Exception", "BaseException", "ValueError", "TypeError", "KeyError",
    "IndexError", "AttributeError", "ImportError", "ModuleNotFoundError",
    "RuntimeError", "StopIteration", "FileNotFoundError", "IOError",
    "OSError", "NotImplementedError", "NameError", "ZeroDivisionError",
    "ConnectionError", "TimeoutError", "PermissionError", "UnicodeDecodeError",
    "SystemExit", "KeyboardInterrupt", "GeneratorExit",
    "Optional", "List", "Dict", "Set", "Tuple", "Any", "Union", "Callable",
}


def validate_project_consistency(
    src_path: Path,
    project_files: list[str],
) -> dict[str, list[str]]:
    """Детерминистская кросс-файловая проверка всего проекта.

    Строит таблицу символов проекта, затем для каждого файла:
    1. `from X import Y` → Y определён на top-level в X
    2. Type annotations ссылаются на импортированные/определённые/builtin имена

    Возвращает dict[filename → list[warnings]]. Пустой dict = всё ОК.
    """
    # 1. Строим таблицу символов проекта
    project_stems = {f.removesuffix(".py"): f for f in project_files}
    symbol_table: dict[str, set[str]] = {}  # stem → top-level names
    file_codes: dict[str, str] = {}  # filename → code

    for fname in project_files:
        fpath = src_path / fname
        if not fpath.exists():
            continue
        try:
            code = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        file_codes[fname] = code
        stem = fname.removesuffix(".py")
        symbol_table[stem] = _get_top_level_names(code)

    issues: dict[str, list[str]] = {}

    # 2. Проверяем каждый файл
    for fname, code in file_codes.items():
        try:
            tree = ast.parse(code)
        except SyntaxError:
            continue

        file_warnings: list[str] = []
        file_stem = fname.removesuffix(".py")

        # 2a. Проверяем from X import Y
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or not node.module:
                continue
            module_stem = node.module.split(".")[0]
            if module_stem not in project_stems or module_stem == file_stem:
                continue
            if module_stem not in symbol_table:
                continue  # Файл не существует
            target_names = symbol_table[module_stem]
            target_fname = project_stems[module_stem]
            for alias in node.names:
                if alias.name == "*":
                    continue
                if alias.name not in target_names:
                    # Проверяем: может это метод класса?
                    target_code = file_codes.get(target_fname, "")
                    owner_class = _find_name_in_classes(target_code, alias.name) if target_code else None
                    if owner_class:
                        file_warnings.append(
                            f"from {module_stem} import {alias.name}: "
                            f"'{alias.name}' — метод класса {owner_class} в "
                            f"{target_fname}. ИСПРАВЬ: from {module_stem} import {owner_class}"
                        )
                    else:
                        file_warnings.append(
                            f"from {module_stem} import {alias.name}: "
                            f"'{alias.name}' не определён в {target_fname}"
                        )

        # 2b. Проверяем type annotations на неимпортированные имена
        imported_names = _get_all_bound_names(code)
        annotation_names: set[str] = set()

        def _collect_annotation_names(ann_node):
            """Рекурсивно собирает все ast.Name из аннотации (включая list[X], Optional[X], X|Y)."""
            if ann_node is None:
                return
            for child in ast.walk(ann_node):
                if isinstance(child, ast.Name):
                    annotation_names.add(child.id)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
                    _collect_annotation_names(arg.annotation)
                _collect_annotation_names(node.returns)
            elif isinstance(node, ast.AnnAssign):
                _collect_annotation_names(node.annotation)

        # Фильтруем: убираем определённые/импортированные/builtin
        unresolved = annotation_names - imported_names - _PYTHON_BUILTINS
        for name in sorted(unresolved):
            # Ищем в таблице символов проекта
            found_in = None
            for stem, names in symbol_table.items():
                if stem == file_stem:
                    continue
                if name in names:
                    found_in = project_stems[stem]
                    break
            if found_in:
                file_warnings.append(
                    f"type annotation '{name}' не импортирован в {fname}. "
                    f"Определён в {found_in} — добавь: from {found_in.removesuffix('.py')} import {name}"
                )

        if file_warnings:
            issues[fname] = file_warnings

    return issues

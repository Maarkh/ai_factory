import os
import re
import sys
from collections import defaultdict, deque
from pathlib import Path

from config import MAX_CONTEXT_CHARS


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
    direct_imports = re.findall(r"^\s*import\s+(\S+)", code, re.MULTILINE)

    seen: set[str] = set()
    for imp in from_imports + direct_imports:
        # Базовый модуль (до первой точки): from os.path → os
        base = imp.split(".")[0]
        if base in seen:
            continue
        seen.add(base)

        # Пропускаем relative imports (from . import ...)
        if base == "":
            continue

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

        warnings.append(
            f"import '{base}' в {filename}: не найден в stdlib, "
            f"requirements.txt и файлах проекта ({', '.join(project_files)})"
        )

    # Проверка циклических импортов (только если src_path задан и файлы уже написаны)
    if src_path:
        current_stem = Path(filename).stem
        for imp_module in {imp.split(".")[0] for imp in from_imports + direct_imports}:
            if imp_module not in project_modules or imp_module == current_stem:
                continue
            # Проверяем: импортирует ли imp_module обратно текущий файл?
            other_path = src_path / (imp_module + ".py")
            if not other_path.exists():
                continue
            other_code = other_path.read_text(encoding="utf-8")
            other_imports = (
                re.findall(r"^\s*from\s+(\S+)\s+import", other_code, re.MULTILINE)
                + re.findall(r"^\s*import\s+(\S+)", other_code, re.MULTILINE)
            )
            other_bases = {i.split(".")[0] for i in other_imports}
            if current_stem in other_bases:
                warnings.append(
                    f"циклический импорт: {filename} ↔ {imp_module}.py "
                    f"(оба файла импортируют друг друга)"
                )

    return warnings

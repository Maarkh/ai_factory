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
        try:
            api = extract_public_api(fpath.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
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
        try:
            code = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        chunk = f"\n--- {fname} ---\n{code}\n"
        if total + len(chunk) > MAX_CONTEXT_CHARS:
            remaining = MAX_CONTEXT_CHARS - total
            if remaining > 200:
                parts.append(chunk[:remaining] + "\n[... обрезано ...]")
            break
        parts.append(chunk)
        total += len(chunk)
    return "".join(parts)


def get_a5_deps(current_file: str, global_imports: list, files: list[str]) -> list[str]:
    """Возвращает файлы проекта, от которых зависит current_file по A5 global_imports.

    Из строк типа 'from models import User' извлекает 'models' и ищет
    соответствующий файл в files. Порядок: сначала зависимости, потом остальные.
    """
    file_stems = {Path(f).stem: f for f in files}
    deps: list[str] = []
    rest: list[str] = []
    dep_stems: set[str] = set()

    for imp_line in global_imports:
        if not isinstance(imp_line, str):
            continue
        m = re.match(r"from\s+(\w+)\s+import", imp_line)
        if m:
            stem = m.group(1)
            if stem in file_stems and file_stems[stem] != current_file:
                dep_stems.add(stem)

    for f in files:
        if f == current_file:
            continue
        if Path(f).stem in dep_stems:
            deps.append(f)
        else:
            rest.append(f)

    return deps + rest


def build_dependency_order(
    files: list[str],
    src_path: Path,
    file_attempts: dict[str, int] | None = None,
) -> list[str]:
    """Возвращает файлы в порядке топологической сортировки по импортам.

    При равном indegree (несколько файлов готовы одновременно) приоритет:
    1. Больше зависимых файлов (dependents) → раньше (разблокирует больше работы)
    2. Меньше прошлых реджектов → раньше (выше шанс на approve)
    """
    graph: dict[str, list[str]]  = defaultdict(list)
    indegree: dict[str, int]     = {f: 0 for f in files}
    file_set = set(files)

    for f in files:
        fpath = src_path / f
        if not fpath.exists():
            continue
        try:
            code = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        imports = (
            re.findall(r"from\s+(\S+)\s+import", code)
            + re.findall(r"^import\s+([\w.]+)", code, re.MULTILINE)
            + re.findall(r"require\(['\"]([^'\"]+)['\"]", code)
            + re.findall(r"\buse\s+([\w:]+)", code)
        )
        ext = Path(f).suffix
        for imp in imports:
            dep = imp.split(".")[0] + ext
            if dep in file_set and dep != f:
                graph[dep].append(f)
                indegree[f] += 1

    # Подсчёт зависимых (сколько файлов разблокируется после генерации данного)
    dependents_count = {f: len(graph.get(f, [])) for f in files}
    attempts = file_attempts or {}

    # Priority key: (-dependents, +attempts, name) — больше зависимых и меньше реджектов = раньше
    import heapq
    heap: list[tuple[int, int, str]] = []
    for f in files:
        if indegree[f] == 0:
            heapq.heappush(heap, (-dependents_count[f], attempts.get(f, 0), f))

    order: list[str] = []
    while heap:
        _, _, curr = heapq.heappop(heap)
        order.append(curr)
        for dep in graph[curr]:
            indegree[dep] -= 1
            if indegree[dep] == 0:
                heapq.heappush(heap, (-dependents_count[dep], attempts.get(dep, 0), dep))

    if len(order) < len(files):
        order.extend(f for f in files if f not in order)
    return order


def find_failing_file(stderr: str, stdout: str, files: list[str]) -> str:
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
PIP_TO_IMPORT: dict[str, str] = {
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
    "pyjwt":                    "jwt",
    "python-telegram-bot":      "telegram",
    "psycopg2-binary":          "psycopg2",
    "google-api-python-client": "googleapiclient",
    "python-magic":             "magic",
    "python-pptx":              "pptx",
    "python-docx":              "docx",
    "websocket-client":         "websocket",
    "pyserial":                 "serial",
    "python-rapidjson":         "rapidjson",
    "python-snappy":            "snappy",
    "python-ldap":              "ldap",
    "python-Levenshtein":       "Levenshtein",
    "mysql-connector-python":   "mysql",
    "mysqlclient":              "MySQLdb",
    "cx-Oracle":                "cx_Oracle",
    "grpcio":                   "grpc",
    "grpcio-tools":             "grpc_tools",
    "Twisted":                  "twisted",
    "twisted":                  "twisted",
    "Pygments":                 "pygments",
    "pygments":                 "pygments",
    "Faker":                    "faker",
    "faker":                    "faker",
    "Cython":                   "cython",
    "cython":                   "cython",
    "PyJWT":                    "jwt",
}

# Невалидные pip-пакеты, которые LLM часто галлюцинирует.
# wrong_pip_name → (correct_pip_name, correct_import_name)
WRONG_PIP_PACKAGES: dict[str, tuple[str, str]] = {
    "opencv":                    ("opencv-python-headless", "cv2"),
    "opencv_python":             ("opencv-python-headless", "cv2"),
    "opencv_python_headless":    ("opencv-python-headless", "cv2"),
    "cv2":                       ("opencv-python-headless", "cv2"),
    "tensorflow-gpu":            ("tensorflow",             "tensorflow"),
    "sklearn":                   ("scikit-learn",           "sklearn"),
    "bs4":                       ("beautifulsoup4",         "bs4"),
    "yaml":                      ("pyyaml",                 "yaml"),
    "attr":                      ("attrs",                  "attr"),
    "dotenv":                    ("python-dotenv",          "dotenv"),
    "jwt":                       ("pyjwt",                  "jwt"),
    "serial":                    ("pyserial",               "serial"),
    "PIL":                       ("pillow",                 "PIL"),
    "dateutil":                  ("python-dateutil",        "dateutil"),
}

# Известные транзитивные зависимости: пакет из requirements.txt → {import-имена}
# Если tensorflow в requirements.txt → numpy, keras, h5py тоже валидные импорты
_KNOWN_TRANSITIVE_DEPS: dict[str, set[str]] = {
    "tensorflow":              {"numpy", "keras", "h5py", "absl", "google"},
    "tensorflow_gpu":          {"numpy", "keras", "h5py", "absl", "google"},
    "opencv_python":           {"numpy"},
    "opencv_python_headless":  {"numpy"},
    "opencv_contrib_python":   {"numpy"},
    "opencv_contrib_python_headless": {"numpy"},
    "scipy":                   {"numpy"},
    "pandas":                  {"numpy"},
    "scikit_learn":            {"numpy", "scipy", "joblib"},
    "torch":                   {"numpy"},
    "torchvision":             {"numpy", "torch"},
    "matplotlib":              {"numpy"},
    "seaborn":                 {"numpy", "matplotlib"},
    "jax":                     {"numpy", "jaxlib"},
    "xgboost":                 {"numpy", "scipy"},
}


def parse_requirements(path: Path) -> set[str]:
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
        # Пропускаем невалидные pip-пакеты (LLM-галлюцинации)
        if pkg_lower in WRONG_PIP_PACKAGES:
            correct_pip, correct_import = WRONG_PIP_PACKAGES[pkg_lower]
            result.add(correct_import.lower())
            result.add(correct_pip.lower().replace("-", "_"))
            continue
        # Нормализация: pip нормализует дефисы в подчёркивания
        pkg_normalized = pkg_lower.replace("-", "_")
        result.add(pkg_normalized)
        # Маппинг pip→import для известных расхождений
        # PIP_TO_IMPORT keys могут быть в любом регистре (Twisted, Pygments...)
        _pip_import = PIP_TO_IMPORT.get(pkg_lower) or PIP_TO_IMPORT.get(pkg)
        if _pip_import:
            result.add(_pip_import.lower())
        # Также добавляем оригинальное имя (без нормализации)
        result.add(pkg_lower)
        # Транзитивные зависимости (numpy для tensorflow/opencv и т.д.)
        if pkg_normalized in _KNOWN_TRANSITIVE_DEPS:
            result.update(_KNOWN_TRANSITIVE_DEPS[pkg_normalized])
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


def find_name_in_classes(code: str, name: str) -> str | None:
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


def get_top_level_names(code: str) -> set[str]:
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
                elif isinstance(target, (ast.Tuple, ast.List)):
                    for elt in ast.walk(target):
                        if isinstance(elt, ast.Name):
                            names.add(elt.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    names.add(alias.asname or alias.name)
        # Python 3.12+: type X = ... (TypeAlias)
        elif hasattr(ast, "TypeAlias") and isinstance(node, ast.TypeAlias):
            names.add(node.name.id if isinstance(node.name, ast.Name) else str(node.name))
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
        # except SomeError as e → e
        elif isinstance(node, ast.ExceptHandler) and node.name:
            names.add(node.name)
    return names


def _check_circular_imports(
    code: str,
    filename: str,
    project_files: list[str],
    project_modules: set[str],
    src_path: Path,
) -> list[str]:
    """DFS-поиск циклических импортов через граф проектных файлов."""
    current_stem = Path(filename).stem
    stem_to_file = {Path(f).stem: f for f in project_files}

    def _get_project_imports(file_stem: str, override_code: str | None = None) -> set[str]:
        if override_code is not None:
            fc = override_code
        else:
            target_fname = stem_to_file.get(file_stem)
            if not target_fname:
                return set()
            fp = src_path / target_fname
            if not fp.exists():
                return set()
            try:
                fc = fp.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                return set()
        fi = re.findall(r"^\s*from\s+(\S+)\s+import", fc, re.MULTILINE)
        di = re.findall(r"^\s*import\s+([\w.]+)", fc, re.MULTILINE)
        bases: set[str] = set()
        for imp in fi + di:
            b = imp.split(".")[0]
            if b == "":
                rel = imp.lstrip(".").split(".")[0]
                if rel:
                    bases.add(rel)
            else:
                bases.add(b)
        return (bases & project_modules) - {file_stem}

    my_deps = _get_project_imports(current_stem, override_code=code)
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
            return [
                f"циклический импорт: {cycle_path} "
                f"(файлы импортируют друг друга по кругу)"
            ]
        for nd in node_deps:
            if nd not in visited:
                stack.append((nd, path + [nd]))
    return []


def _check_undefined_refs(
    code: str,
    filename: str,
    direct_imports: list[str],
    stdlib: set[str],
    pip_packages: set[str],
) -> list[str]:
    """Проверяет undefined module references: name.attr где name не импортирован."""
    imported_names: set[str] = set()
    # Только "import X" делает X доступным как namespace
    # "from X import Y" НЕ делает X доступным
    for imp in direct_imports:
        base = imp.split(".")[0]
        if base:
            imported_names.add(base)
    imported_names.update({"self", "cls", "super", "type", "print", "len", "range",
                           "str", "int", "float", "bool", "list", "dict", "set",
                           "tuple", "None", "True", "False", "Exception"})
    imported_names.update(_get_all_bound_names(code))

    warnings: list[str] = []
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
        pass
    return warnings


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
    pip_packages = parse_requirements(requirements_path) if requirements_path else set()

    # Множество имён проектных модулей (без расширения)
    project_modules = {Path(f).stem for f in project_files}

    # Парсим импорты из кода
    from_imports = re.findall(r"^\s*from\s+(\S+)\s+import", code, re.MULTILINE)
    # Ловим все модули из "import X" и "import X, Y, Z"
    direct_imports = []
    for imp_line in re.findall(r"^\s*import\s+(.+)$", code, re.MULTILINE):
        for part in imp_line.split(","):
            mod = part.strip().split()[0].split(".")[0] if part.strip() else ""
            if mod:
                direct_imports.append(mod)

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

        # 4. Общеизвестные встроенные модули с подчёркиванием
        if base in {"_thread", "_io", "_collections", "_abc", "_decimal",
                     "typing_extensions", "_operator", "_functools", "_heapq",
                     "_contextvars", "_signal", "_csv", "_json", "_datetime"}:
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

    # Проверка циклических импортов
    if src_path:
        warnings.extend(_check_circular_imports(code, filename, project_files, project_modules, src_path))

    # Проверка self-referencing assignments: func = func
    self_refs = re.findall(r"^(\w+)\s*=\s*(\w+)\s*(?:#.*)?$", code, re.MULTILINE)
    for lhs, rhs in self_refs:
        if lhs == rhs:
            warnings.append(
                f"бессмысленное присвоение '{lhs} = {lhs}' в {filename}: "
                f"переменная ссылается на саму себя (возможно, пропущен import)"
            )

    # Проверка undefined module references
    warnings.extend(_check_undefined_refs(code, filename, direct_imports, stdlib, pip_packages))

    return warnings


def _collect_class_members(target_code: str) -> dict[str, set[str]]:
    """Собирает {class_name: {methods, attributes}} из кода файла с учётом наследования."""
    try:
        target_tree = ast.parse(target_code)
    except SyntaxError:
        return {}
    file_classes: dict[str, set[str]] = {}
    file_bases: dict[str, list[str]] = {}
    for tnode in target_tree.body:
        if isinstance(tnode, ast.ClassDef):
            members: set[str] = set()
            for item in tnode.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    members.add(item.name)
                elif isinstance(item, ast.Assign):
                    for t in item.targets:
                        if isinstance(t, ast.Name):
                            members.add(t.id)
                elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    members.add(item.target.id)
            file_classes[tnode.name] = members
            file_bases[tnode.name] = [b.id for b in tnode.bases if isinstance(b, ast.Name)]
    # Наследование: добавляем members из базовых классов того же файла
    for cls_name, bases in file_bases.items():
        for base_name in bases:
            if base_name in file_classes:
                file_classes[cls_name] |= file_classes[base_name]
    return file_classes


def _collect_imported_classes(
    tree: ast.Module,
    project_stems: dict[str, str],
    get_file_cached,
) -> dict[str, tuple[str, set[str]]]:
    """Собирает информацию об импортированных классах из проектных файлов.

    Возвращает {local_alias: (source_stem, class_methods)}.
    """
    imported: dict[str, tuple[str, set[str]]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        module_stem = node.module.split(".")[0]
        if module_stem not in project_stems:
            continue
        cached = get_file_cached(module_stem)
        if cached is None:
            continue
        _, target_code = cached
        file_classes = _collect_class_members(target_code)
        for cls_name, cls_methods in file_classes.items():
            for alias in node.names:
                if alias.name == cls_name:
                    local_name = alias.asname or alias.name
                    imported[local_name] = (module_stem, cls_methods)
    return imported


def _validate_method_calls(
    tree: ast.Module,
    imported_classes: dict[str, tuple[str, set[str]]],
    project_stems: dict[str, str],
) -> list[str]:
    """Проверяет что instance.method() вызовы используют существующие методы."""
    if not imported_classes:
        return []

    # variable = ClassName(...) → variable type is ClassName
    instance_types: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Name) and node.value.func.id in imported_classes:
                    instance_types[target.id] = node.value.func.id
            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                if target.value.id == "self" and isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name) and node.value.func.id in imported_classes:
                        instance_types[f"self.{target.attr}"] = node.value.func.id

    warnings: list[str] = []
    seen: set[str] = set()
    for node in ast.walk(tree):
        # var.method()
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            var_name = node.value.id
            method_name = node.attr
            class_name = instance_types.get(var_name)
            if not class_name or method_name.startswith("_"):
                continue
            source_stem, cls_methods = imported_classes[class_name]
            wkey = f"{var_name}.{method_name}"
            if method_name not in cls_methods and wkey not in seen:
                seen.add(wkey)
                public = sorted(m for m in cls_methods if not m.startswith("_") and m != "__init__")
                warnings.append(
                    f"{var_name}.{method_name}(): метод '{method_name}' не найден "
                    f"в классе {class_name} из {project_stems[source_stem]}. "
                    f"Доступные методы: {', '.join(public) if public else '(нет)'}"
                )
        # self.x.method()
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Attribute):
            if isinstance(node.value.value, ast.Name) and node.value.value.id == "self":
                key = f"self.{node.value.attr}"
                class_name = instance_types.get(key)
                if not class_name or node.attr.startswith("_"):
                    continue
                source_stem, cls_methods = imported_classes[class_name]
                wkey = f"{key}.{node.attr}"
                if node.attr not in cls_methods and wkey not in seen:
                    seen.add(wkey)
                    public = sorted(m for m in cls_methods if not m.startswith("_") and m != "__init__")
                    warnings.append(
                        f"self.{node.value.attr}.{node.attr}(): метод '{node.attr}' не найден "
                        f"в классе {class_name} из {project_stems[source_stem]}. "
                        f"Доступные методы: {', '.join(public) if public else '(нет)'}"
                    )
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

    project_stems = {Path(f).stem: f for f in project_files}
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
        names = get_top_level_names(target_code)
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
                owner_class = find_name_in_classes(target_code, alias.name)
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

    # Проверяем что вызываемые методы на импортированных классах существуют
    imported_classes = _collect_imported_classes(tree, project_stems, _get_for)
    warnings.extend(_validate_method_calls(tree, imported_classes, project_stems))

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
    project_stems = {Path(f).stem: f for f in project_files}
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
        stem = Path(fname).stem
        symbol_table[stem] = get_top_level_names(code)

    issues: dict[str, list[str]] = {}

    # 2. Проверяем каждый файл
    for fname, code in file_codes.items():
        try:
            tree = ast.parse(code)
        except SyntaxError:
            continue

        file_warnings: list[str] = []
        file_stem = Path(fname).stem

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
                    owner_class = find_name_in_classes(target_code, alias.name) if target_code else None
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

        # 2b. Проверяем method calls на импортированных классах
        def _get_cached_for_consistency(stem: str):
            target_file = project_stems.get(stem)
            if not target_file or target_file not in file_codes:
                return None
            return (symbol_table.get(stem, set()), file_codes[target_file])

        imported_classes = _collect_imported_classes(tree, project_stems, _get_cached_for_consistency)
        method_warnings = _validate_method_calls(tree, imported_classes, project_stems)
        file_warnings.extend(method_warnings)

        # 2c. Проверяем type annotations на неимпортированные имена
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
                    f"Определён в {found_in} — добавь импорт {name} из {Path(found_in).stem}"
                )

        if file_warnings:
            issues[fname] = file_warnings

    return issues

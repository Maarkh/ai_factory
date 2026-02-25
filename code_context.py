import os
import re
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
    for match in re.findall(r'File "([^"]+)", line \d+', stderr):
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

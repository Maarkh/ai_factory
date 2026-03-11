import asyncio
import hashlib
import logging
import subprocess
from pathlib import Path
from typing import Optional

from config import FACTORY_DIR, RUN_TIMEOUT, TRUNCATE_LOG
from lang_utils import get_docker_image

logger = logging.getLogger(__name__)


def run_command(
    args: list[str],
    cwd: Optional[Path] = None,
    timeout: Optional[int] = None,
) -> tuple[int, str, str]:
    """Синхронный запуск команды. Используется для быстрых операций (git, docker version)."""
    try:
        proc = subprocess.Popen(
            args, cwd=cwd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            return proc.returncode, stdout, stderr
        except subprocess.TimeoutExpired as e:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            partial_out = (e.stdout or "")[-TRUNCATE_LOG:] if e.stdout else ""
            partial_err = (e.stderr or "")[-TRUNCATE_LOG:] if e.stderr else ""
            return -1, partial_out, f"TIMEOUT: процесс не завершился за {timeout}с.\n{partial_err}"
    except OSError as e:
        return -1, "", f"Команда не найдена или недоступна: {e}"


async def run_command_async(
    args: list[str],
    cwd: Optional[Path] = None,
    timeout: Optional[int] = None,
) -> tuple[int, str, str]:
    """Асинхронный запуск команды. Не блокирует event loop."""
    try:
        proc = await asyncio.create_subprocess_exec(
            *args, cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=timeout,
            )
            stdout = (stdout_bytes or b"").decode("utf-8", errors="replace")
            stderr = (stderr_bytes or b"").decode("utf-8", errors="replace")
            return proc.returncode or 0, stdout, stderr
        except asyncio.TimeoutError:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=5)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
            return -1, "", f"TIMEOUT: процесс не завершился за {timeout}с."
    except OSError as e:
        return -1, "", f"Команда не найдена или недоступна: {e}"


def _make_container_name(src_path: Path) -> str:
    """Генерирует детерминированное имя контейнера по пути src_path."""
    return "factory_" + hashlib.sha256(str(src_path).encode()).hexdigest()[:12]


def _cleanup_docker_container(container_name: str) -> None:
    """Удаляет контейнер по имени (безопасно — не затрагивает чужие контейнеры)."""
    run_command(["docker", "rm", "-f", container_name])


async def run_in_docker(
    src_path: Path,
    command: str,
    timeout: int,
    language: str = "python",
    read_only: bool = False,
) -> tuple[int, str, str]:
    """Docker монтирует только src/ — чистый контекст без .factory/.
    Контейнер именован, чтобы cleanup был точечным.
    read_only=True монтирует src/ с :ro для безопасности (ревью/тесты).
    """
    image          = get_docker_image(language)
    container_name = _make_container_name(src_path)
    volume_spec    = f"{src_path}:/app:ro" if read_only else f"{src_path}:/app"
    result = await run_command_async(
        [
            "docker", "run", "--rm",
            "--name", container_name,
            "--network", "bridge",
            "--memory", "512m",
            "--cpus",   "1",
            "-v", volume_spec,
            "-w", "/app",
            image,
            "bash", "-c", command,
        ],
        timeout=timeout,
    )
    if result[0] == -1:
        _cleanup_docker_container(container_name)
    return result


async def build_docker_image(src_path: Path, tag: str) -> tuple[bool, str, str]:
    """Dockerfile должен лежать в src/."""
    rc, stdout, stderr = await run_command_async(
        ["docker", "build", "-t", tag, "."],
        cwd=src_path, timeout=RUN_TIMEOUT,
    )
    return rc == 0, stdout, stderr


def check_docker_installed() -> bool:
    rc, _, stderr = run_command(["docker", "version"])
    if rc != 0:
        logger.error(f"❌ Docker не установлен или демон не запущен.\nДетали: {stderr}")
        logger.info("  → Установите Docker: https://docs.docker.com/engine/install/")
        logger.info("  → Убедитесь, что демон запущен: sudo systemctl start docker")
        return False
    return True


def git_init(project_path: Path) -> None:
    run_command(["git", "init"], cwd=project_path)
    gitignore = (
        # .factory/ полностью скрыт от Git
        f"{FACTORY_DIR}/\n"
        "venv/\n__pycache__/\n*.pyc\n"
        "node_modules/\ntarget/\n"
    )
    (project_path / ".gitignore").write_text(gitignore, encoding="utf-8")
    git_commit(project_path, "Initial gitignore")


def git_commit(project_path: Path, message: str) -> None:
    run_command(["git", "add", "."], cwd=project_path)
    run_command(["git", "commit", "-m", message, "--allow-empty"], cwd=project_path)

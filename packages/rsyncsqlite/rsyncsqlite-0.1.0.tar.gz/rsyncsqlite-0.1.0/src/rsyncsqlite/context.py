import sqlite3
from contextlib import contextmanager

from pathlib import Path
import hashlib
import shutil
import subprocess

default_data_dir = Path.home() / "rsyncsqlite"


def _local_path(remote, data_dir=default_data_dir):
    hash = hashlib.sha512(remote.encode("utf-8")).hexdigest()
    return data_dir / f"{hash}.sqlite"


def _run_command(*args, check_installed=True, silent=False):
    cmd = "sqlite3_rsync"
    if check_installed and shutil.which(cmd) is None:
        raise FileNotFoundError(f"{cmd} is not installed or not in PATH.")
    result = subprocess.run(
        [cmd, *args, "-vvv"], capture_output=silent, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"{cmd} failed with exit code {result.returncode}")


def _sync_down(remote, data_dir=default_data_dir, silent=False):
    data_dir.mkdir(exist_ok=True)
    local = _local_path(remote, data_dir)
    _run_command(remote, local, silent=silent)


def _sync_up(remote, data_dir=default_data_dir, silent=False):
    local = _local_path(remote, data_dir)
    _run_command(local, remote, check_installed=False, silent=silent)


def rsyncforget(remote, data_dir=default_data_dir):
    local = _local_path(remote, data_dir)
    local.unlink(missing_ok=True)


def rsyncnew(remote, data_dir=default_data_dir):
    rsyncforget(remote, data_dir)
    local = _local_path(remote, data_dir)
    conn = sqlite3.connect(local)
    conn.close()
    _sync_up(remote, data_dir)


@contextmanager
def rsyncopen(remote, read_only=False, data_dir=default_data_dir, silent=False):
    local = _local_path(remote, data_dir)
    _sync_down(remote, data_dir, silent=silent)
    mode = "ro" if read_only else "rw"
    conn = sqlite3.connect(f"file:{local}?mode={mode}", uri=True)
    try:
        yield conn
    finally:
        conn.close()
        if not read_only:
            _sync_up(remote, data_dir, silent=silent)

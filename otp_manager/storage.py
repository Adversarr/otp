import tomllib
import tomli_w
from pathlib import Path
from typing import Dict, Any
import os

DATA_DIR = Path(__file__).parent / "data"
SECRETS_FILE = DATA_DIR / "secrets.toml"

def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)
    if not SECRETS_FILE.exists():
        SECRETS_FILE.write_text("", encoding="utf-8")

def load_secrets() -> Dict[str, Any]:
    ensure_data_dir()
    try:
        return tomllib.loads(SECRETS_FILE.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError:
        return {}

def save_secrets(data: Dict[str, Any]):
    ensure_data_dir()
    SECRETS_FILE.write_text(tomli_w.dumps(data), encoding="utf-8")


def secure_delete(filepath: Path, passes: int = 3):
    """Secure file deletion with multiple overwrites"""
    with open(filepath, "ba+") as f:
        length = f.tell()
        for _ in range(passes):
            f.seek(0)
            f.write(os.urandom(length))
    os.unlink(filepath)

def clear_all_secrets():
    """Securely wipe all secrets"""
    ensure_data_dir()
    if SECRETS_FILE.exists():
        secure_delete(SECRETS_FILE)

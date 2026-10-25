"""Configuración del Bot de Telegram para el Portal del Máster."""
import os
import ssl
from pathlib import Path

# Contexto SSL seguro que exige validación de certificados de servidor (sin eludir verificación)
def get_ssl_context() -> ssl.SSLContext:
    """Devuelve un contexto SSL con verificación estricta de certificados."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


BASE_DIR = Path(__file__).resolve().parent.parent
if (BASE_DIR / "index.html").exists():
    PORTAL_DIR = BASE_DIR
    INDEX_HTML = BASE_DIR / "index.html"
else:
    PORTAL_DIR = BASE_DIR / "portal-master"
    INDEX_HTML = PORTAL_DIR / "index.html"

# Cargar .env si existe de forma nativa sin librerías externas
ENV_PATH = Path(__file__).resolve().parent / ".env"
if ENV_PATH.exists():
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))

# Variables de entorno estrictas (sin fallbacks inseguros a permisos totales)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip().strip("'\"")
TELEGRAM_ALLOWED_USER = os.environ.get("TELEGRAM_ALLOWED_USER", "").strip().strip("'\"")
TELEGRAM_ALLOWED_CHAT = os.environ.get("TELEGRAM_ALLOWED_CHAT", "").strip().strip("'\"") or TELEGRAM_ALLOWED_USER
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip().strip("'\"")  # Para commits en la nube
GITHUB_REPO = os.environ.get("GITHUB_REPO", "raquelescuderovr/portal-master").strip().strip("'\"")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main").strip().strip("'\"")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip().strip("'\"")
PORTAL_PUBLIC_URL = os.environ.get("PORTAL_PUBLIC_URL", "https://raquelescuderovr.github.io/portal-master/").strip().strip("'\"")

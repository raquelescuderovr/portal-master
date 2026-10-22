"""Configuración del Bot de Telegram para el Portal del Máster."""
import os
import ssl
from pathlib import Path

# Configurar contexto HTTPS seguro para evitar errores de certificados en entornos locales macOS
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass


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

# Variables obligatorias y opcionales
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_ALLOWED_USER = os.environ.get("TELEGRAM_ALLOWED_USER", "").strip()  # Chat ID de Raquel
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()  # Para commits en la nube
GITHUB_REPO = os.environ.get("GITHUB_REPO", "raquelescuderovr/portal-master").strip()
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
PORTAL_PUBLIC_URL = os.environ.get("PORTAL_PUBLIC_URL", "https://raquelescuderovr.github.io/portal-master/").strip()

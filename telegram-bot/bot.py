"""Bot de Telegram Conversacional para el Máster en Abogacía y Procura.
Soporta diálogo fluido, visión multimodal (casos prácticos y CEPROC) y llamadas a herramientas para actualizar el portal.
"""
import os
import sys
import json
import time
import re
import urllib.request
import urllib.parse
from datetime import datetime

from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USER, GITHUB_TOKEN,
    GITHUB_REPO, PORTAL_PUBLIC_URL, INDEX_HTML, ENV_PATH
)
import updater
import assistant

TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def api_request(method: str, params: dict = None, data: bytes = None, content_type: str = "application/json") -> dict:
    """Realiza una petición a la API de Telegram."""
    url = f"{TELEGRAM_API_BASE}/{method}"
    headers = {"User-Agent": "Master-Portal-Bot/2.0"}

    if data is not None:
        headers["Content-Type"] = content_type
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    elif params:
        query = urllib.parse.urlencode(params)
        req = urllib.request.Request(f"{url}?{query}", headers=headers, method="GET")
    else:
        req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[Telegram API] Error en {method}: {e}", flush=True)
        return {"ok": False, "description": str(e)}

def send_message(chat_id: int, text: str, parse_mode: str = "HTML") -> dict:
    """Envía un mensaje de texto por Telegram."""
    payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": parse_mode}).encode("utf-8")
    return api_request("sendMessage", data=payload)

def send_chat_action(chat_id: int, action: str = "typing"):
    """Envía la acción de 'escribiendo...' a Telegram."""
    payload = json.dumps({"chat_id": chat_id, "action": action}).encode("utf-8")
    api_request("sendChatAction", data=payload)

def download_telegram_file(file_id: str) -> bytes:
    """Descarga un archivo o imagen desde los servidores de Telegram."""
    file_info = api_request("getFile", params={"file_id": file_id})
    if not file_info.get("ok"):
        return b""
    file_path = file_info["result"]["file_path"]
    download_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    req = urllib.request.Request(download_url, headers={"User-Agent": "Master-Portal-Bot/2.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()

def is_authorized(user_id: int) -> bool:
    """Verifica si el remitente es Raquel."""
    if not TELEGRAM_ALLOWED_USER:
        return True  # Permitir primer uso para vincular
    return str(user_id) == str(TELEGRAM_ALLOWED_USER)

def save_gemini_key_from_chat(key: str) -> bool:
    """Guarda automáticamente la clave de Gemini en el .env si Raquel la envía."""
    try:
        lines = []
        if ENV_PATH.exists():
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()

        new_lines = []
        replaced = False
        for line in lines:
            if line.strip().startswith("GEMINI_API_KEY="):
                new_lines.append(f'GEMINI_API_KEY="{key}"\n')
                replaced = True
            else:
                new_lines.append(line)

        if not replaced:
            new_lines.append(f'GEMINI_API_KEY="{key}"\n')

        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        os.environ["GEMINI_API_KEY"] = key
        # Recargar en assistant y config
        import config
        config.GEMINI_API_KEY = key
        assistant.GEMINI_API_KEY = key
        return True
    except Exception as e:
        print(f"[Bot] Error guardando clave: {e}", flush=True)
        return False

def handle_update(update: dict):
    """Procesa un update recibido de Telegram."""
    msg = update.get("message")
    if not msg:
        return

    chat_id = msg["chat"]["id"]
    user_id = msg["from"]["id"]
    user_name = msg["from"].get("first_name", "Raquel")
    text = msg.get("text", "").strip()
    caption = msg.get("caption", "").strip()

    if not is_authorized(user_id):
        send_message(chat_id, f"⛔ Acceso no autorizado. Tu Telegram ID es: <code>{user_id}</code>")
        return

    # Comando /start
    if text == "/start":
        send_message(chat_id, f"""🎓 <b>¡Hola, {user_name}! Asistente conversacional del Máster listo.</b>

Ya no soy un simple bot de comandos: ahora podemos <b>conversar con total fluidez</b>.

<b>¿Qué puedes hacer?</b>
• 📸 <b>Mándame la foto de un caso práctico</b> y cuéntame tus notas (ej: <i>«mira este caso de Sandra Mosteiro, pero la pregunta 2 no se responde y la entrega es el viernes a las 14h»</i>).
• 📩 <b>Reenvíame correos o avisos de CEPROC</b> y dime si quieres cambiar o destacar algo.
• 💬 <b>Pregúntame cualquier duda</b> jurídica, de las asignaturas o del calendario.
• ⚡ <b>Dime «Súbelo al portal»</b> cuando quieras que publique la práctica o el correo.

<b>Comandos útiles:</b>
/hoy — Clases y horarios de la jornada
/entregas — Estado de prácticas de CEPROC
/limpiar — Reinicia el hilo de conversación actual
/web — Enlace a tu web pública""")
        return

    # Comando /limpiar o /reset
    if text in ("/limpiar", "/reset"):
        assistant.reset_chat_history(chat_id)
        send_message(chat_id, "🧹 <i>Historial de conversación reiniciado. ¿En qué te ayudo ahora?</i>")
        return

    # Comando /web
    if text == "/web":
        send_message(chat_id, f"🌐 <b>Tu portal académico:</b>\n{PORTAL_PUBLIC_URL}")
        return

    # Comando /hoy
    if text == "/hoy":
        send_chat_action(chat_id, "typing")
        resp = assistant.execute_tool("consultar_hoy", {})
        sesiones_txt = "\n".join([f"• <b>{s['hora']}:</b> {s.get('docente', s.get('actividad'))} ({s.get('materia', '')})" for s in resp.get("sesiones", [])])
        send_message(chat_id, f"🗓️ <b>Docencia de hoy ({resp.get('fecha')}):</b>\n{sesiones_txt}\n📍 <i>Colegio de Abogados</i>")
        return

    # Comando /entregas
    if text == "/entregas":
        send_chat_action(chat_id, "typing")
        resp = assistant.execute_tool("consultar_entregas", {})
        send_message(chat_id, f"✍️ <b>Estado de entregas en CEPROC:</b>\n• <b>Balance:</b> {resp.get('balance')}\n• " + "\n• ".join(resp.get("ultimas", [])))
        return

    # Detección inteligente de Clave de Gemini (AIzaSy...)
    match_key = re.search(r"AIzaSy[A-Za-z0-9_-]{33}", text)
    if match_key:
        api_key_found = match_key.group(0)
        send_chat_action(chat_id, "typing")
        if save_gemini_key_from_chat(api_key_found):
            send_message(chat_id, """🎉 <b>¡Clave de Gemini activada con éxito!</b>

Ya tengo cerebro conversacional y visión artificial completa. A partir de ahora puedes pasarme fotos de casos prácticos con tus indicaciones y charlaremos fluidamente.""")
            return

    # Manejo de FOTOS / IMÁGENES (con o sin texto de acompañamiento)
    photos = msg.get("photo")
    if photos:
        send_chat_action(chat_id, "typing")
        largest_photo = photos[-1]
        img_bytes = download_telegram_file(largest_photo["file_id"])

        # Pasar la foto y la indicación de Raquel al asistente conversacional
        reply = assistant.chat(chat_id, user_text=caption, image_bytes=img_bytes, mime_type="image/jpeg")
        send_message(chat_id, reply)
        return

    # Manejo de DOCUMENTOS (PDFs o imágenes adjuntas como archivo)
    doc = msg.get("document")
    if doc:
        mime = doc.get("mime_type", "")
        if "image" in mime or "pdf" in mime:
            send_chat_action(chat_id, "typing")
            doc_bytes = download_telegram_file(doc["file_id"])
            reply = assistant.chat(chat_id, user_text=caption, image_bytes=doc_bytes, mime_type=mime)
            send_message(chat_id, reply)
            return

    # Manejo de MENSAJES DE TEXTO CONVERSACIONALES
    if text:
        send_chat_action(chat_id, "typing")
        reply = assistant.chat(chat_id, user_text=text)
        send_message(chat_id, reply)

def run_polling():
    """Bucle principal de polling de Telegram."""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN no está definido en config o en .env", flush=True)
        sys.exit(1)

    print("🚀 Bot de Telegram Conversacional del Máster iniciado y escuchando...", flush=True)
    offset = 0
    while True:
        try:
            updates = api_request("getUpdates", params={"offset": offset, "timeout": 10})
            if updates.get("ok"):
                for u in updates.get("result", []):
                    offset = u["update_id"] + 1
                    handle_update(u)
            else:
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n🛑 Bot detenido.", flush=True)
            break
        except Exception as e:
            print(f"[Polling] Error: {e}", flush=True)
            time.sleep(3)

if __name__ == "__main__":
    run_polling()

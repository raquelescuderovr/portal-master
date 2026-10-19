"""Bot de Telegram para el Portal del Máster (Python nativo, sin dependencias externas)."""
import os
import sys
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime

from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USER, GITHUB_TOKEN,
    GITHUB_REPO, PORTAL_PUBLIC_URL, INDEX_HTML
)
import updater
import ai_parser

TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def api_request(method: str, params: dict = None, data: bytes = None, content_type: str = "application/json") -> dict:
    """Realiza una petición a la API de Telegram."""
    url = f"{TELEGRAM_API_BASE}/{method}"
    headers = {"User-Agent": "Master-Portal-Bot/1.0"}

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

def download_telegram_file(file_id: str) -> bytes:
    """Descarga un archivo o imagen desde los servidores de Telegram."""
    file_info = api_request("getFile", params={"file_id": file_id})
    if not file_info.get("ok"):
        return b""
    file_path = file_info["result"]["file_path"]
    download_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    req = urllib.request.Request(download_url, headers={"User-Agent": "Master-Portal-Bot/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()

def is_authorized(user_id: int) -> bool:
    """Verifica si el remitente es Raquel."""
    if not TELEGRAM_ALLOWED_USER:
        return True  # Si no está configurado, permite el primer uso y avisa
    return str(user_id) == str(TELEGRAM_ALLOWED_USER)

def handle_update(update: dict):
    """Procesa un update recibido de Telegram."""
    msg = update.get("message")
    if not msg:
        return

    chat_id = msg["chat"]["id"]
    user_id = msg["from"]["id"]
    user_name = msg["from"].get("first_name", "Raquel")
    text = msg.get("text", "")
    caption = msg.get("caption", "")

    # Seguridad: comprobar autorización
    if not is_authorized(user_id):
        send_message(chat_id, f"⛔ Acceso no autorizado. Tu Telegram ID es: <code>{user_id}</code>")
        return

    # Comando /start
    if text == "/start":
        send_message(chat_id, f"""🎓 <b>¡Hola, {user_name}! Asistente del Máster conectado.</b>

Tu Telegram ID es: <code>{user_id}</code>

<b>¿Qué puedo hacer por ti?</b>
• 📩 <b>Reenvíame cualquier correo</b> del máster (ICACOR, Procuradores o UDC) y lo publico en el portal.
• 📸 <b>Mándame una captura de CEPROC</b> y extraeré la tarea y su fecha de entrega.
• ✍️ <b>Escríbeme o dicta una nota</b> con avisos de clase.

<b>Comandos útiles:</b>
/hoy — Clases y horario de la jornada actual
/entregas — Prácticas y tareas de CEPROC
/web — Enlace a tu portal en GitHub Pages
/ayuda — Instrucciones completas""")
        return

    # Comando /web
    if text == "/web":
        send_message(chat_id, f"🌐 <b>Tu portal académico:</b>\n{PORTAL_PUBLIC_URL}")
        return

    # Comando /hoy
    if text == "/hoy":
        send_message(chat_id, """🗓️ <b>Docencia de hoy (19 de octubre):</b>
• <b>16:30 – 18:30 h:</b> Sandra Mosteiro Costa (Procura) · <i>Actos de comunicación judicial</i>
• <b>18:45 – 20:45 h:</b> José Luis Delgado Domínguez (Abogacía) · <i>Responsabilidad civil y penal</i>
📍 <i>Colegio de Abogados (A Coruña)</i>""")
        return

    # Comando /entregas
    if text == "/entregas":
        send_message(chat_id, """✍️ <b>Estado de entregas y CEPROC:</b>
• <b>Poder apud acta:</b> Entregado ✓
• <b>Escrito de subsanación:</b> Entregado ✓
• <b>Auto declaración con oferta UP:</b> Entregado (2 envíos) ✓
• <b>Caso Deontología Procura:</b> Entregado ✓
📊 <b>Balance:</b> 4 / 4 prácticas enviadas (0 vencidas).""")
        return

    # Manejo de FOTOS / CAPTURAS (ej. CEPROC)
    photos = msg.get("photo")
    if photos:
        send_message(chat_id, "🔍 <i>Analizando captura de pantalla...</i>")
        largest_photo = photos[-1]  # Mejor resolución
        img_bytes = download_telegram_file(largest_photo["file_id"])

        parsed = ai_parser.parse_text_or_image(text=caption, image_bytes=img_bytes, mime_type="image/jpeg")
        process_and_save(chat_id, parsed)
        return

    # Manejo de MENSAJES DE TEXTO O REENVÍOS DE CORREO
    if text:
        send_message(chat_id, "⚡ <i>Procesando información y actualizando portal...</i>")
        parsed = ai_parser.parse_text_or_image(text=text)
        process_and_save(chat_id, parsed)

def process_and_save(chat_id: int, parsed: dict):
    """Inserta la información en el portal y confirma por Telegram."""
    try:
        # Leer index.html actual
        if not INDEX_HTML.exists():
            send_message(chat_id, "⚠️ No se localizó index.html en local. Verificando repositorio...")
            return

        with open(INDEX_HTML, "r", encoding="utf-8") as f:
            current_content = f.read()

        p_type = parsed.get("type", "mail")
        title = parsed.get("title", "Aviso académico")
        date_str = parsed.get("date", datetime.now().strftime("%d oct %Y"))
        teacher = parsed.get("sender_or_teacher", "Docente asignado")
        subject = parsed.get("subject", "Módulo en curso")
        sub_ref = parsed.get("subject_ref", "Abogacía|Técnicas instrumentales|3")
        summary = parsed.get("summary", title)
        body = parsed.get("body", "")
        meta = parsed.get("meta", "Comunicaciones del Máster")

        if p_type == "ceproc_task":
            deadline = parsed.get("deadline", "Próxima sesión")
            new_html = updater.add_ceproc_task(
                current_content, date_str, title, teacher, subject, sub_ref,
                "Pendiente de realizar", deadline, body or summary
            )
            commit_msg = f"Añadir práctica CEPROC: {title} ({teacher})"
            tipo_label = "✍️ <b>Nueva práctica en CEPROC</b>"
            extra_info = f"⏰ <b>Plazo:</b> {deadline}"
        else:
            key_name = "mail_" + str(int(time.time()))[-6:]
            new_html = updater.add_mail_entry(
                current_content, date_str, title, meta, key_name,
                teacher, sub_ref, summary, body, meta
            )
            commit_msg = f"Incorporar correo: {title} ({meta})"
            tipo_label = "📩 <b>Nuevo correo / aviso incorporado</b>"
            extra_info = f"👤 <b>Docente / Fuente:</b> {teacher}"

        # Guardar y hacer push
        success = updater.save_and_commit(new_html, commit_msg)

        if success:
            send_message(chat_id, f"""✅ <b>¡Portal actualizado y publicado!</b>

{tipo_label}
📌 <b>Título:</b> {title}
{extra_info}
📚 <b>Materia:</b> {subject}

🔗 <a href="{PORTAL_PUBLIC_URL}">Ver cambios en la web del Máster</a>""")
        else:
            send_message(chat_id, f"⚠️ Se procesaron los datos ({title}), pero ocurrió un problema al hacer push a GitHub.")

    except Exception as e:
        send_message(chat_id, f"❌ Error al procesar: <code>{str(e)}</code>")

def run_polling():
    """Bucle principal de polling de Telegram."""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN no está definido en config o en .env")
        print("Por favor, crea tu bot con @BotFather y añade el token a telegram-bot/.env")
        sys.exit(1)

    print("🚀 Bot de Telegram del Máster iniciado y escuchando...", flush=True)
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

"""Bot de Telegram Conversacional para el Máster en Abogacía y Procura.
Soporta diálogo fluido, visión multimodal y confirmación en dos fases antes de publicar.
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
    TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USER, TELEGRAM_ALLOWED_CHAT,
    GITHUB_TOKEN, GITHUB_REPO, PORTAL_PUBLIC_URL, INDEX_HTML, ENV_PATH,
    get_ssl_context
)
import updater
import assistant
import proposals

TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def api_request(method: str, params: dict = None, data: bytes = None, content_type: str = "application/json") -> dict:
    """Realiza una petición a la API de Telegram con verificación SSL estricta."""
    url = f"{TELEGRAM_API_BASE}/{method}"
    headers = {"User-Agent": "Master-Portal-Bot/2.0"}
    ssl_ctx = get_ssl_context()

    if data is not None:
        headers["Content-Type"] = content_type
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    elif params:
        query = urllib.parse.urlencode(params)
        req = urllib.request.Request(f"{url}?{query}", headers=headers, method="GET")
    else:
        req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[Telegram API] Error en {method}: {e.__class__.__name__}", flush=True)
        return {"ok": False, "description": str(e.__class__.__name__)}


def send_message(chat_id: int, text: str, parse_mode: str = "HTML") -> dict:
    """Envía un mensaje de texto por Telegram con fallback automático a texto plano."""
    payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": parse_mode}).encode("utf-8")
    resp = api_request("sendMessage", data=payload)
    if not resp.get("ok") and parse_mode:
        payload_plain = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
        resp = api_request("sendMessage", data=payload_plain)
    return resp


def send_chat_action(chat_id: int, action: str = "typing"):
    """Envía la acción de 'escribiendo...' a Telegram."""
    payload = json.dumps({"chat_id": chat_id, "action": action}).encode("utf-8")
    api_request("sendChatAction", data=payload)


def optimize_image_bytes(raw_bytes: bytes) -> bytes:
    """Optimiza el tamaño de la imagen con sips en macOS para procesado rápido."""
    if len(raw_bytes) < 600 * 1024:
        return raw_bytes
    tmp_in = "/tmp/tg_in.jpg"
    tmp_out = "/tmp/tg_opt.jpg"
    try:
        with open(tmp_in, "wb") as f:
            f.write(raw_bytes)
        import subprocess
        subprocess.run(["sips", "-Z", "1200", tmp_in, "--out", tmp_out], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(tmp_out):
            with open(tmp_out, "rb") as f:
                return f.read()
    except Exception:
        pass
    return raw_bytes


def download_telegram_file(file_id: str) -> bytes:
    """Descarga un archivo o imagen desde los servidores de Telegram con verificación SSL estricta."""
    file_info = api_request("getFile", params={"file_id": file_id})
    if not file_info.get("ok"):
        return b""
    file_path = file_info["result"]["file_path"]
    download_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    req = urllib.request.Request(download_url, headers={"User-Agent": "Master-Portal-Bot/2.0"})
    ssl_ctx = get_ssl_context()
    with urllib.request.urlopen(req, timeout=30, context=ssl_ctx) as resp:
        return resp.read()


def is_authorized(user_id: int, chat_id: int, chat_type: str = "private") -> bool:
    """Verifica si el remitente y el chat corresponden estrictamente a la usuaria autorizada.
    Fail-closed: si falta la configuración de usuario o chat, rechaza terminantemente.
    """
    if not TELEGRAM_ALLOWED_USER or not TELEGRAM_ALLOWED_CHAT:
        return False
    if chat_type != "private":
        return False
    return str(user_id) == str(TELEGRAM_ALLOWED_USER) and str(chat_id) == str(TELEGRAM_ALLOWED_CHAT)


def handle_update(update: dict):
    """Procesa un update recibido de Telegram con control de acceso y confirmación en dos fases."""
    msg = update.get("message")
    if not msg:
        return

    chat = msg.get("chat", {})
    chat_id = chat.get("id")
    chat_type = chat.get("type", "")
    user_id = msg.get("from", {}).get("id")
    user_name = msg.get("from", {}).get("first_name", "Raquel")
    text = msg.get("text", "").strip()
    caption = msg.get("caption", "").strip()

    # Control de acceso estricto (usuario + chat privado autorizado)
    if not is_authorized(user_id, chat_id, chat_type):
        print(f"[Seguridad] Acceso no autorizado denegado: user={user_id}, chat={chat_id}, tipo={chat_type}", flush=True)
        if chat_type == "private":
            send_message(chat_id, "⛔ Acceso denegado. Este bot es de uso privado y exclusivo.")
        return

    # Comando /start
    if text == "/start":
        send_message(chat_id, f"""🎓 <b>¡Hola, {user_name}! Asistente conversacional del Máster listo.</b>

Diálogo fluido, visión multimodal y <b>confirmación segura en dos fases</b>.

<b>¿Qué puedes hacer?</b>
• 📸 <b>Mándame la foto de un caso práctico</b> y cuéntame tus notas.
• 📩 <b>Reenvíame correos o avisos del Máster</b> (CEPROC para Procura, o ICACOR para Abogacía) para resumirlos o incorporarlos.
• 💬 <b>Pregúntame cualquier duda</b> jurídica, de las asignaturas o del calendario.
• 🔒 <b>Confirmación en dos fases:</b> Si el asistente propone publicar una nota, práctica o correo, te mostrará la vista previa exacta y te pedirá confirmar con <code>/confirmar</code>.

<b>Comandos útiles:</b>
/hoy — Clases y horarios de la jornada
/entregas — Estado de entregas y prácticas del Máster
/confirmar — Confirma y publica la propuesta pendiente actual
/cancelar — Descarta la propuesta de cambio pendiente
/limpiar — Reinicia el hilo de conversación actual
/web — Enlace a tu web pública""")
        return

    # Comando /limpiar o /reset
    if text in ("/limpiar", "/reset"):
        assistant.reset_chat_history(chat_id)
        proposals.cancel_proposals(str(user_id), str(chat_id))
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
        send_message(chat_id, f"✍️ <b>Estado de entregas del Máster:</b>\n• <b>Balance:</b> {resp.get('balance')}\n• " + "\n• ".join(resp.get("ultimas", [])))
        return

    # Comando de confirmación en dos fases (Two-Phase Commit)
    if text.startswith("/confirmar"):
        parts = text.split()
        prop_id = parts[1].strip() if len(parts) > 1 else None
        if not prop_id:
            active = proposals.get_active_proposal_for_user(str(user_id), str(chat_id))
            if active:
                prop_id = active["id"]
            else:
                send_message(chat_id, "⚠️ No tienes ninguna propuesta de cambio pendiente de confirmación.")
                return

        ok, msg_conf, prop = proposals.confirm_proposal(prop_id, user_id=str(user_id), chat_id=str(chat_id))
        if not ok:
            send_message(chat_id, f"⛔ <b>Confirmación rechazada:</b> {msg_conf}")
            return

        send_chat_action(chat_id, "typing")
        reply = assistant.execute_action(prop["action_type"], prop["payload"])
        send_message(chat_id, f"✅ <b>Acción confirmada y aplicada:</b>\n{reply}")
        return

    # Comando /cancelar
    if text == "/cancelar":
        count = proposals.cancel_proposals(str(user_id), str(chat_id))
        if count > 0:
            send_message(chat_id, "🛑 <i>Propuesta de cambio cancelada. No se ha modificado nada en el portal.</i>")
        else:
            send_message(chat_id, "ℹ️ No había ninguna propuesta pendiente para cancelar.")
        return

    # Afirmaciones ambiguas en lenguaje natural: exigir comando de confirmación explícito
    clean_lower = text.lower().strip()
    if clean_lower in ("sí", "si", "súbelo", "subelo", "confirmo", "adelante", "dale", "publica"):
        active = proposals.get_active_proposal_for_user(str(user_id), str(chat_id))
        if active:
            send_message(
                chat_id,
                f"🔒 <b>Confirmación requerida fuera de la IA:</b>\n"
                f"Para evitar órdenes accidentales o inducidas por documentos, confirma escribiendo:\n"
                f"<code>/confirmar {active['id']}</code>\n"
                f"O escribe <code>/cancelar</code> para descartar."
            )
            return

    # Rechazar explícitamente el envío de claves por Telegram
    if text.startswith("/key") or clean_lower.startswith("aizasy") or clean_lower.startswith("sk-"):
        send_message(
            chat_id,
            "🔒 <b>Función deshabilitada por seguridad:</b>\n"
            "Por protección, las credenciales nunca deben enviarse a través de un chat de mensajería. "
            "Configura tus claves exclusivamente en el archivo local <code>.env</code> o en <b>GitHub Secrets</b>."
        )
        return

    # Manejo de FOTOS / IMÁGENES
    photos = msg.get("photo")
    if photos:
        send_chat_action(chat_id, "typing")
        largest_photo = photos[-1]
        img_bytes = download_telegram_file(largest_photo["file_id"])

        # Persistir la foto en la carpeta de materiales para que se visualice directamente en el portal
        try:
            from datetime import datetime
            p_mat = BASE_DIR / "portal-master" / "materiales"
            r_mat = BASE_DIR / "materiales"
            if img_bytes:
                with open(p_mat / "foto-caso-delgado.jpg", "wb") as f_out:
                    f_out.write(img_bytes)
                if r_mat.exists():
                    with open(r_mat / "foto-caso-delgado.jpg", "wb") as f_out2:
                        f_out2.write(img_bytes)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(p_mat / f"foto_recibida_{ts}.jpg", "wb") as f_ts:
                    f_ts.write(img_bytes)
                print(f"[Bot] Foto guardada correctamente en materiales/ ({len(img_bytes)} bytes)", flush=True)
        except Exception as err:
            print(f"[Bot] Error guardando foto en disco: {err}", flush=True)

        reply = assistant.chat(chat_id, user_text=caption, image_bytes=img_bytes, mime_type="image/jpeg", user_id=user_id)
        send_message(chat_id, reply)
        return

    # Manejo de NOTAS DE VOZ
    voice = msg.get("voice")
    if voice:
        send_chat_action(chat_id, "typing")
        v_bytes = download_telegram_file(voice["file_id"])
        v_mime = voice.get("mime_type", "audio/ogg")
        reply = assistant.chat(chat_id, user_text=caption or "", media_bytes=v_bytes, mime_type=v_mime, user_id=user_id)
        send_message(chat_id, reply)
        return

    # Manejo de ARCHIVOS DE AUDIO
    audio = msg.get("audio")
    if audio:
        send_chat_action(chat_id, "typing")
        a_bytes = download_telegram_file(audio["file_id"])
        a_mime = audio.get("mime_type", "audio/mpeg")
        reply = assistant.chat(chat_id, user_text=caption or "", media_bytes=a_bytes, mime_type=a_mime, user_id=user_id)
        send_message(chat_id, reply)
        return

    # Manejo de DOCUMENTOS
    doc = msg.get("document")
    if doc:
        mime = doc.get("mime_type", "")
        if "image" in mime or "pdf" in mime or "audio" in mime:
            send_chat_action(chat_id, "typing")
            doc_bytes = download_telegram_file(doc["file_id"])
            reply = assistant.chat(chat_id, user_text=caption, media_bytes=doc_bytes, mime_type=mime, user_id=user_id)
            send_message(chat_id, reply)
            return

    # Manejo de MENSAJES DE TEXTO CONVERSACIONALES
    if text:
        send_chat_action(chat_id, "typing")
        reply = assistant.chat(chat_id, user_text=text, user_id=user_id)
        send_message(chat_id, reply)


def run_polling():
    """Bucle principal de polling de Telegram con validación de configuración estricta (Fail-closed)."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ALLOWED_USER or not TELEGRAM_ALLOWED_CHAT:
        print("❌ Error de configuración crítica: TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USER y TELEGRAM_ALLOWED_CHAT son obligatorios.", flush=True)
        print("   El bot se detiene por seguridad para evitar el acceso de usuarios no autorizados.", flush=True)
        sys.exit(1)

    me = api_request("getMe")
    if not me.get("ok"):
        print(f"❌ Error al conectar con Telegram: {me.get('description')}", flush=True)
        sys.exit(1)

    bot_username = me.get("result", {}).get("username", "MasterBot")
    print(f"🚀 Bot @{bot_username} iniciado y en modo escucha segura (Autorizado: user={TELEGRAM_ALLOWED_USER}, chat={TELEGRAM_ALLOWED_CHAT})...", flush=True)

    offset = 0
    while True:
        try:
            updates = api_request("getUpdates", params={"offset": offset, "timeout": 10})
            if updates.get("ok"):
                for u in updates.get("result", []):
                    offset = u["update_id"] + 1
                    try:
                        handle_update(u)
                    except Exception as err:
                        print(f"[Handler] Error procesando update {u.get('update_id')}: {err.__class__.__name__}", flush=True)
                        c_id = u.get("message", {}).get("chat", {}).get("id")
                        if c_id:
                            send_message(c_id, "⚠️ Ocurrió un error al procesar tu solicitud. Inténtalo de nuevo en unos instantes.")
            else:
                desc = updates.get("description", "Respuesta no OK")
                print(f"[Polling] Error en getUpdates: {desc}", flush=True)
                time.sleep(3)
        except KeyboardInterrupt:
            print("\n🛑 Bot detenido.", flush=True)
            break
        except Exception as e:
            print(f"[Polling] Error inesperado: {e.__class__.__name__}", flush=True)
            time.sleep(3)


if __name__ == "__main__":
    run_polling()

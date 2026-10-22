"""Asistente conversacional inteligente para el Bot de Telegram del Máster.
Soporta multi-turn chat, visión multimodal (fotos de casos y CEPROC) y llamadas a herramientas/acciones para actualizar el portal.
"""
import os
import re
import json
import base64
import urllib.request
import subprocess
from datetime import datetime
from pathlib import Path

from config import (
    GEMINI_API_KEY, PORTAL_PUBLIC_URL, INDEX_HTML, BASE_DIR
)
import updater

HISTORY_FILE = Path(__file__).resolve().parent / "chat_history.json"

def get_portal_summary() -> str:
    """Extrae un resumen actualizado del estado de entregas y agenda desde index.html."""
    try:
        if not INDEX_HTML.exists():
            return "Portal en desarrollo."
        with open(INDEX_HTML, "r", encoding="utf-8") as f:
            content = f.read()

        summary_lines = []

        # 1. Entregas pendientes y completadas
        m_deliv = re.search(r'const deliveries=\[(.*?)\];', content, re.DOTALL)
        if m_deliv:
            raw_delivs = m_deliv.group(1)
            deliv_blocks = re.findall(r'\{(.*?)\}', raw_delivs, re.DOTALL)
            pendientes = []
            completadas = []
            for b in deliv_blocks:
                t = re.search(r"title:'(.*?)'", b)
                te = re.search(r"teacher:'(.*?)'", b)
                st = re.search(r"status:'(.*?)'", b)
                sub = re.search(r"submitted:(true|false)", b)
                title = t.group(1) if t else "Sin título"
                teacher = te.group(1) if te else "Docente"
                status = st.group(1) if st else ""
                is_sub = (sub.group(1) == "true") if sub else False

                if is_sub or "✓" in status:
                    completadas.append(f"  ✓ {title} ({teacher})")
                else:
                    pendientes.append(f"  ⏳ {title} · Docente: {teacher} · Estado: {status}")

            summary_lines.append("ENTREGAS EN EL PORTAL ACADÉMICO:")
            if pendientes:
                summary_lines.append("Prácticas pendientes:")
                summary_lines.extend(pendientes)
            else:
                summary_lines.append("No hay prácticas pendientes registradas.")
            if completadas:
                summary_lines.append(f"Prácticas ya entregadas ({len(completadas)}):")
                summary_lines.extend(completadas[:5])

        # 2. Agenda y clases del día
        today_str = datetime.now().strftime("%Y-%m-%d")
        dates_to_check = [today_str]
        if "2026" not in today_str:
            dates_to_check.append("2026-10-22")

        for d in dates_to_check:
            m_events = re.search(r"'" + d + r"':\s*\[(.*?)\]\s*(?:,|\})", content, re.DOTALL)
            if m_events:
                summary_lines.append(f"\nAGENDA Y CLASES DEL DÍA ({d}):")
                raw_ev = m_events.group(1)
                ev_blocks = re.findall(r'\{(.*?)\}', raw_ev, re.DOTALL)
                for eb in ev_blocks:
                    st = re.search(r"start:'(.*?)'", eb)
                    nm = re.search(r"name:'(.*?)'", eb)
                    tc = re.search(r"teacher:'(.*?)'", eb)
                    pl = re.search(r"place:'(.*?)'", eb)
                    start = st.group(1) if st else ""
                    name = nm.group(1) if nm else ""
                    teacher = f" | {tc.group(1)}" if tc else ""
                    place = f" ({pl.group(1)})" if pl else ""
                    summary_lines.append(f"  • {start}: {name}{teacher}{place}")
                break

        return "\n".join(summary_lines)
    except Exception:
        return "Información del portal disponible."

def build_system_instruction() -> str:
    portal_info = get_portal_summary()
    return f"""Eres el Asistente Académico Personal de Raquel Escudero Valcárcel-Ríos para el Máster Universitario en Abogacía y Procura (MUAP) en A Coruña (UDC, Ilustre Colegio Provincial de Abogados de A Coruña - ICACOR, y Colegio de Procuradores).

Tu personalidad y estilo de conversación:
• Mantén una conversación completamente fluida, inteligente, cercana, resolutiva y jurídicamente precisa (al estilo ChatGPT / Gemini avanzado).
• No eres un simple robot de comandos rígidos: dialogas, explicas casos prácticos, analizas enunciados o leyes (LAJG, LEC, LECrim, etc.), propones esquemas procesales y aceptas instrucciones y matices que te dé Raquel.
• Raquel te enviará con frecuencia fotos o capturas de pantalla de casos prácticos (de CEPROC o repartidos en clase), pantallazos de correos o avisos institucionales, y te dará explicaciones complementarias (por ejemplo: "el profesor dijo que la pregunta 3 es opcional y que el plazo vence el viernes").
• Escucha atentamente sus indicaciones y responde a sus dudas con rigor jurídico y claridad práctica.
• Cuando Raquel te pida que registres una entrega, o cuando te pase una práctica o correo que claramente corresponda añadir al portal académico, incluye al final de tu respuesta una directiva de acción con formato JSON:
  [ACCION:GUARDAR_PRACTICA:{{"titulo": "...", "docente": "...", "materia": "...", "plazo": "...", "detalles": "..."}}]
  o bien para correos y avisos:
  [ACCION:GUARDAR_CORREO:{{"titulo": "...", "remitente": "...", "docente": "...", "materia": "...", "resumen": "...", "cuerpo": "..."}}]
  o cuando Raquel te indique que ya ha entregado o completado una práctica pendiente:
  [ACCION:COMPLETAR_PRACTICA:{{"termino": "título o docente de la práctica"}}]


Estado actual del portal de Raquel:
{portal_info}

Contexto docente y académico:
• Turno de tarde (Grupo 2).
• Docentes actuales destacados:
  - José Luis Delgado Domínguez: Responsabilidad civil y penal, aseguramiento y turno de oficio (Abogacía).
  - Sandra Mosteiro Costa: Actos de comunicación judicial (Procura).
  - Carolina Moreno Vázquez: Justicia digital, poder apud acta y subsanación (Procura).
  - Ana Vázquez Corte: Deontología y responsabilidad profesional (Procura).
• Web pública del portal: {PORTAL_PUBLIC_URL}
"""

def load_histories() -> dict:
    """Carga los historiales de conversación persistidos."""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_histories(histories: dict):
    """Guarda los historiales de conversación."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(histories, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Assistant] Error al guardar historial: {e}")

def reset_chat_history(chat_id: int):
    """Limpia el historial de la conversación para ese chat."""
    h = load_histories()
    cid_str = str(chat_id)
    if cid_str in h:
        del h[cid_str]
        save_histories(h)

def execute_action(action_type: str, args: dict) -> str:
    """Ejecuta una acción detectada en el mensaje de la IA y actualiza el portal."""
    try:
        with open(INDEX_HTML, "r", encoding="utf-8") as f:
            current_content = f.read()

        if action_type == "GUARDAR_PRACTICA":
            titulo = args.get("titulo", "Caso práctico")
            docente = args.get("docente", "Docente asignado")
            materia = args.get("materia", "Actuación procesal")
            plazo = args.get("plazo", "Por determinar")
            detalles = args.get("detalles", "")
            now_str = datetime.now().strftime("%d oct %Y")

            new_html = updater.add_ceproc_task(
                current_content, now_str, titulo, docente, materia,
                "Abogacía|Técnicas instrumentales|3", f"⏳ Pendiente (Plazo: {plazo})", plazo, detalles
            )
            commit_msg = f"Añadir práctica: {titulo} ({docente}) [vía Telegram]"
            updater.save_and_commit(new_html, commit_msg)
            return f"\n\n📌 <b>Registrado en el portal:</b> «{titulo}» ({plazo})\n🌐 <a href='{PORTAL_PUBLIC_URL}'>Ver en tu portal web</a>"

        elif action_type == "GUARDAR_CORREO":
            titulo = args.get("titulo", "Aviso académico")
            remitente = args.get("remitente", "master.abogacia@icacor.org")
            docente = args.get("docente", "Administración del Máster")
            materia = args.get("materia", "Técnicas instrumentales")
            resumen = args.get("resumen", titulo)
            cuerpo = args.get("cuerpo", "")
            now_str = datetime.now().strftime("%d oct %Y (%H:%M)")
            key_name = "mail_" + str(int(datetime.now().timestamp()))[-6:]

            new_html = updater.add_mail_entry(
                current_content, now_str, titulo, remitente, key_name,
                docente, "Abogacía|Técnicas instrumentales|3", resumen, cuerpo, remitente
            )
            commit_msg = f"Incorporar aviso: {titulo} [vía Telegram]"
            updater.save_and_commit(new_html, commit_msg)
            return f"\n\n📌 <b>Aviso incorporado al portal:</b> «{titulo}»\n🌐 <a href='{PORTAL_PUBLIC_URL}'>Ver en tu portal web</a>"

        elif action_type == "COMPLETAR_PRACTICA":
            termino = args.get("termino", "")
            new_html, found = updater.mark_delivery_completed(current_content, termino)
            if found:
                commit_msg = f"Marcar entrega completada: {termino} [vía Telegram]"
                updater.save_and_commit(new_html, commit_msg)
                return f"\n\n✅ <b>Práctica marcada como entregada en tu portal web:</b> «{termino}»\n🌐 <a href='{PORTAL_PUBLIC_URL}'>Ver portal</a>"
            else:
                return f"\n\n⚠️ <i>No se encontró ninguna entrega pendiente que coincida con «{termino}».</i>"

    except Exception as e:
        print(f"[Assistant] Error al ejecutar acción {action_type}: {e}")
        return f"\n\n⚠️ <i>Nota: Hubo un inconveniente al actualizar el archivo local: {e}</i>"

    return ""

def execute_tool(func_name: str, args: dict) -> dict:
    """Función de conveniencia para comandos de consulta directa."""
    try:
        content = ""
        if INDEX_HTML.exists():
            with open(INDEX_HTML, "r", encoding="utf-8") as f:
                content = f.read()

        if func_name == "consultar_hoy":
            today_str = datetime.now().strftime("%Y-%m-%d")
            dates_to_check = [today_str]
            if "2026" not in today_str:
                dates_to_check.append("2026-10-22")

            sesiones = []
            for d in dates_to_check:
                m_events = re.search(r"'" + d + r"':\s*\[(.*?)\]\s*(?:,|\})", content, re.DOTALL)
                if m_events:
                    raw_ev = m_events.group(1)
                    ev_blocks = re.findall(r'\{(.*?)\}', raw_ev, re.DOTALL)
                    for eb in ev_blocks:
                        st = re.search(r"start:'(.*?)'", eb)
                        nm = re.search(r"name:'(.*?)'", eb)
                        tc = re.search(r"teacher:'(.*?)'", eb)
                        pl = re.search(r"place:'(.*?)'", eb)
                        sesiones.append({
                            "hora": st.group(1) if st else "",
                            "actividad": nm.group(1) if nm else "",
                            "docente": tc.group(1) if tc else "",
                            "sede": pl.group(1) if pl else "Colegio de Abogados"
                        })
                    return {"fecha": d, "sesiones": sesiones}

        elif func_name == "consultar_entregas":
            m_deliv = re.search(r'const deliveries=\[(.*?)\];', content, re.DOTALL)
            pendientes = []
            completadas = []
            if m_deliv:
                raw_delivs = m_deliv.group(1)
                deliv_blocks = re.findall(r'\{(.*?)\}', raw_delivs, re.DOTALL)
                for b in deliv_blocks:
                    t = re.search(r"title:'(.*?)'", b)
                    te = re.search(r"teacher:'(.*?)'", b)
                    st = re.search(r"status:'(.*?)'", b)
                    sub = re.search(r"submitted:(true|false)", b)
                    title = t.group(1) if t else "Sin título"
                    teacher = te.group(1) if te else "Docente"
                    status = st.group(1) if st else ""
                    is_sub = (sub.group(1) == "true") if sub else False

                    if is_sub or "✓" in status:
                        completadas.append(f"✓ {title} ({teacher})")
                    else:
                        pendientes.append(f"⏳ {title} ({teacher} · {status})")

            return {
                "balance": f"{len(pendientes)} pendientes · {len(completadas)} completadas",
                "ultimas": pendientes + completadas[:4]
            }
    except Exception as e:
        print(f"[Assistant] Error en execute_tool: {e}")

    return {}

def chat(chat_id: int, user_text: str = "", media_bytes: bytes = None, mime_type: str = "image/jpeg", image_bytes: bytes = None) -> str:
    """Envía un mensaje al LLM manteniendo el hilo conversacional y ejecutando acciones si se solicitan."""
    if not GEMINI_API_KEY:
        return (
            "⚠️ <b>Falta configurar la clave de IA (GEMINI_API_KEY)</b> en el archivo <code>.env</code>.\n\n"
            "Puedes obtener tu clave gratuita en: <a href='https://aistudio.google.com/app/apikey'>Google AI Studio</a>."
        )

    if image_bytes and not media_bytes:
        media_bytes = image_bytes

    histories = load_histories()
    cid_str = str(chat_id)
    chat_history = histories.get(cid_str, [])

    # Construir el nuevo turno de usuario
    user_parts = []
    if media_bytes:
        # Optimizar tamaño si es imagen
        if mime_type.startswith("image/") and len(media_bytes) > 500 * 1024:
            tmp_in = "/tmp/asst_in.jpg"
            tmp_out = "/tmp/asst_opt.jpg"
            try:
                with open(tmp_in, "wb") as f:
                    f.write(media_bytes)
                subprocess.run(["sips", "-Z", "1200", tmp_in, "--out", tmp_out], capture_output=True)
                if os.path.exists(tmp_out):
                    with open(tmp_out, "rb") as f:
                        media_bytes = f.read()
            except Exception:
                pass

        b64_data = base64.b64encode(media_bytes).decode("utf-8")
        user_parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": b64_data
            }
        })

    if user_text:
        user_parts.append({"text": user_text})
    elif media_bytes and not user_text:
        if mime_type.startswith("audio/"):
            user_parts.append({"text": "Mensaje de voz de Raquel. Escucha el audio atentamente, responde con naturalidad y atiende a sus dudas o indicaciones para el Máster."})
        else:
            user_parts.append({"text": "Te comparto esta foto de un documento o caso práctico del Máster. Analízala y cuéntame qué contiene."})

    chat_history.append({"role": "user", "parts": user_parts})

    # Limitar el historial a los últimos 10 turnos para mantener agilidad y frescura de contexto
    if len(chat_history) > 10:
        chat_history = chat_history[-10:]

    system_inst = build_system_instruction()

    # Modelos a intentar (priorizando gemini-3.5-flash-lite para respuesta instantánea en ~1 segundo)
    models_to_try = [
        ("gemini-3.5-flash-lite", {}),
        ("gemini-3.1-flash-lite", {}),
        ("gemini-2.5-flash", {}),
        ("gemini-2.0-flash", {}),
        ("gemini-3.5-flash", {"thinkingConfig": {"thinkingBudget": 0}})
    ]

    resp_text = ""
    last_err = None
    for m_name, extra_gen_cfg in models_to_try:
        clean_key = GEMINI_API_KEY.strip()
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent"
        if not clean_key.startswith("AQ."):
            api_url += f"?key={clean_key}"
        
        gen_cfg = {"temperature": 0.3}
        gen_cfg.update(extra_gen_cfg)

        payload = {
            "system_instruction": {"parts": [{"text": system_inst}]},
            "contents": chat_history,
            "generationConfig": gen_cfg
        }

        req_data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Master-AI-Assistant/2.0",
            "x-goog-api-key": clean_key
        }
        req = urllib.request.Request(
            api_url,
            data=req_data,
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=18) as resp:
                resp_json = json.loads(resp.read().decode())
                candidate = resp_json.get("candidates", [{}])[0]
                parts = candidate.get("content", {}).get("parts", [])
                text_parts = [p["text"] for p in parts if "text" in p]
                resp_text = "\n".join(text_parts).strip()
                if resp_text:
                    break
        except Exception as err:
            last_err = err
            print(f"[Assistant] Error con {m_name}: {err}. Probando siguiente modelo...", flush=True)

    if not resp_text:
        return f"⚠️ Ocurrió un error al procesar tu mensaje: <code>{str(last_err)}</code>"

    # Detectar y procesar posibles acciones automáticas
    action_note = ""
    action_pattern = r'\[ACCION:(GUARDAR_PRACTICA|GUARDAR_CORREO|COMPLETAR_PRACTICA):(\{.*?\})\]'
    match = re.search(action_pattern, resp_text, re.DOTALL)
    if match:
        act_type = match.group(1)
        try:
            act_args = json.loads(match.group(2))
            action_note = execute_action(act_type, act_args)
        except Exception as e:
            print(f"[Assistant] Error al parsear JSON de acción: {e}")
        # Limpiar la etiqueta de acción del texto visible para la usuaria
        resp_text = re.sub(action_pattern, '', resp_text).strip()

    final_reply = resp_text + action_note

    # Guardar en el historial la respuesta limpia del modelo
    chat_history.append({"role": "model", "parts": [{"text": resp_text}]})
    histories[cid_str] = chat_history
    save_histories(histories)

    return final_reply

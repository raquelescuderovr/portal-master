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
    GEMINI_API_KEY, PORTAL_PUBLIC_URL, INDEX_HTML, BASE_DIR, get_ssl_context
)
import updater
import proposals

HISTORY_FILE = Path(__file__).resolve().parent / "chat_history.json"

def get_portal_summary() -> str:
    """Extrae un resumen actualizado del estado de entregas y asignaturas desde index.html."""
    try:
        if not INDEX_HTML.exists():
            return "Portal en desarrollo."
        with open(INDEX_HTML, "r", encoding="utf-8") as f:
            content = f.read()

        summary_lines = []
        # Buscar entregas
        m_deliv = re.search(r'const deliveries=\[(.*?)\];', content, re.DOTALL)
        if m_deliv:
            raw_delivs = m_deliv.group(1)
            titles = re.findall(r"title:'(.*?)'.*?teacher:'(.*?)'.*?status:'(.*?)'", raw_delivs)
            summary_lines.append("Entregas registradas en el portal:")
            for t, te, st in titles[:6]:
                summary_lines.append(f"  • {t} | Docente: {te} | Estado: {st}")

        return "\n".join(summary_lines)
    except Exception:
        return "Información del portal disponible."

def build_system_instruction() -> str:
    portal_info = get_portal_summary()
    return f"""Eres el Asistente Académico Personal de Raquel Escudero Valcárcel-Ríos para el Máster Universitario en Abogacía y Procura (MUAP) en A Coruña (UDC, Ilustre Colegio Provincial de Abogados de A Coruña - ICACOR, y Colegio de Procuradores).

Tu personalidad y estilo de conversación:
• Mantén una conversación completamente fluida, inteligente, cercana, resolutiva y jurídicamente precisa (al estilo ChatGPT / Gemini avanzado).
• No eres un simple robot de comandos rígidos: dialogas, explicas casos prácticos, analizas enunciados o leyes (LAJG, LEC, LECrim, etc.), propones esquemas procesales y aceptas instrucciones y matices que te dé Raquel.
• Raquel te enviará con frecuencia fotos o capturas de pantalla de casos prácticos (de CEPROC o repartidos en clase), pantallazos de correos o avisos institucionales, y te dará explicaciones complementarias.
• Escucha atentamente sus indicaciones y responde a sus dudas con rigor jurídico y claridad práctica.

DIRECTIVAS DE ACCIÓN AUTOMÁTICA EN EL PORTAL ACADÉMICO:
Cuando corresponda guardar información en el portal tras una petición o envío de Raquel, incluye al final de tu respuesta EXACTAMENTE una de las siguientes directivas JSON:

1) Para calificaciones oficiales o notas de tests/evaluaciones:
  [ACCION:GUARDAR_NOTA:{{"titulo": "Título de la prueba o evaluación", "docente": "Nombre del profesor/a", "materia": "Nombre de la asignatura", "nota": "10 / 10", "tipo_nota": "Nota oficial", "remitente": "accesoabogaciaprocura@... o ICA Coruña", "resumen": "Resumen ejecutivo", "cuerpo": "Detalle del correo o acta", "desglose": [{{"label": "Test", "val": "4 / 4"}}, {{"label": "Escritos", "val": "6 / 6"}}]}}]

2) Para nuevas prácticas, casos prácticos o tareas de CEPROC:
  [ACCION:GUARDAR_PRACTICA:{{"titulo": "...", "docente": "...", "materia": "...", "plazo": "...", "detalles": "..."}}]

3) Para correos informativos o avisos generales:
  [ACCION:GUARDAR_CORREO:{{"titulo": "...", "remitente": "...", "docente": "...", "materia": "...", "resumen": "...", "cuerpo": "..."}}]

4) Cuando Raquel indique que ya ha entregado o completado una práctica pendiente:
  [ACCION:COMPLETAR_PRACTICA:{{"termino": "título o docente de la práctica"}}]

Estado actual del portal de Raquel:
{portal_info}

Contexto docente y académico:
• Turno de tarde (Grupo 2).
• Docentes actuales destacados:
  - José Luis Delgado Domínguez: Responsabilidad civil y penal, aseguramiento y turno de oficio (Abogacía).
  - Sandra Mosteiro Costa: Actos de comunicación judicial (Procura).
  - Carolina Moreno Vázquez: Justicia digital, poder apud acta y subsanación (Procura).
  - Carlos M. Sánchez Muiño: Iniciación y marketing de la procura, proceso digital (Procura).
  - Ana Vázquez Corte: Deontología y responsabilidad profesional (Procura).

REGLA FUNDAMENTAL CEPROC vs ICACOR (ABOGACÍA vs PROCURA):
• La plataforma CEPROC / CPROC es ÚNICA Y EXCLUSIVAMENTE para la rama de Procura (procuradores).
• Los abogados (como José Luis Delgado Domínguez o materias de Abogacía) NUNCA dan ni gestionan prácticas por el CEPROC; no tiene nada que ver con ellos.
• Las prácticas de José Luis Delgado se entregan exclusivamente:
  - Por correo electrónico a: secretariatecnico@icacor.org
  - O en mano en formato físico en la sede del Colegio de Abogados de A Coruña (ICACOR).
• NUNCA derives a CEPROC ni sugieras la plataforma CPROC para prácticas o materias de Abogacía.
• Vincula siempre las consultas de Delgado a su correo del módulo ('schedule') o a la foto/enunciado facilitado en clase.
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

        if action_type == "GUARDAR_NOTA":
            titulo = args.get("titulo", "Calificación oficial")
            docente = args.get("docente", "Docente del Máster")
            materia = args.get("materia", "Técnicas instrumentales")
            nota = args.get("nota", "10 / 10")
            tipo_nota = args.get("tipo_nota", "Nota oficial")
            remitente = args.get("remitente", "Secretaría del Máster")
            resumen = args.get("resumen", titulo)
            cuerpo = args.get("cuerpo", "")
            desglose = args.get("desglose", [])
            now_str = datetime.now().strftime("%d oct %Y (%H:%M)")
            timestamp_suffix = str(int(datetime.now().timestamp()))[-6:]
            mail_key = "mail_nota_" + timestamp_suffix
            grade_id = "grade_" + timestamp_suffix

            # 1. Registrar el correo en el portal
            new_html = updater.add_mail_entry(
                current_content, now_str, titulo, remitente, mail_key,
                docente, "Procura|Técnicas instrumentales|2", resumen, cuerpo, remitente
            )

            # 2. Registrar la nota en Notas & Tests, Ficha del Profesor y Asignatura
            kicker_txt = f"Evaluación oficial por correo · {now_str}"
            desc_txt = f"Calificación comunicada oficialmente por {remitente}: {titulo}. Nota: {nota}."
            new_html = updater.add_grade_entry(
                new_html, grade_id, titulo, kicker_txt, nota, tipo_nota,
                docente, "Procura|Técnicas instrumentales|2", mail_key, desc_txt, desglose,
                subject_name=materia
            )

            commit_msg = f"Registrar calificación: {titulo} ({docente}: {nota}) [vía Telegram]"
            updater.save_and_commit(new_html, commit_msg)
            return (
                f"\n\n⭐ <b>¡Calificación registrada con éxito en ambos portales!</b>\n"
                f"• <b>Tu portal personal:</b> Registrada tu nota de {nota} ({tipo_nota}) en expediente, ficha de {docente} y buzón.\n"
                f"• <b>Portal del Estudiante:</b> Sincronizado automáticamente (habilitada la ficha y casilla interactiva en su Cuaderno de Notas para que registren su propia nota privadamente).\n"
                f"• <b>Profesor/a:</b> {docente}\n"
                f"• <b>Asignatura:</b> {materia}\n"
                f"• <b>Correo clasificado:</b> {titulo} (privado en tu buzón)\n"
                f"🌐 <a href='{PORTAL_PUBLIC_URL}'>Ver en tu portal web</a>"
            )

        elif action_type == "GUARDAR_PRACTICA":
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
            return (
                f"\n\n📌 <b>Práctica registrada en el portal:</b> «{titulo}»\n"
                f"• <b>Docente:</b> {docente} (vinculada en su ficha de profesor)\n"
                f"• <b>Asignatura:</b> {materia}\n"
                f"• <b>Plazo:</b> {plazo}\n"
                f"• <b>Ubicación:</b> Pestaña de Entregas y panel docente\n"
                f"🌐 <a href='{PORTAL_PUBLIC_URL}'>Ver en tu portal web</a>"
            )

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
            return f"\n\n📌 <b>Aviso incorporado al portal:</b> «{titulo}» (vinculado con {docente})\n🌐 <a href='{PORTAL_PUBLIC_URL}'>Ver en tu portal web</a>"

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
    if func_name == "consultar_hoy":
        return {
            "fecha": "Martes 20 oct 2026",
            "sesiones": [
                {"hora": "16:30 – 18:30", "docente": "Sandra Mosteiro Costa", "materia": "Actos de comunicación judicial (Sesión 2 de 2)", "sede": "Colegio de Abogados"},
                {"hora": "18:45 – 20:45", "docente": "José Luis Delgado Domínguez", "materia": "Responsabilidad civil y penal (Sesión 2 de 3)", "sede": "Colegio de Abogados"}
            ]
        }
    elif func_name == "consultar_entregas":
        return {
            "balance": "6 prácticas registradas (2 pendientes de Abogacía con José Luis Delgado)",
            "ultimas": [
                "⏳ Casos prácticos: Insostenibilidad y AJG (Plazo: 29 oct 2026 · Delgado · Entrega: secretariatecnico@icacor.org)",
                "⏳ Parte de siniestro y Turno de Oficio (Plazo: 30 oct 2026 · Delgado · Entrega: secretariatecnico@icacor.org)",
                "✓ Actos de comunicación judicial (Sandra Mosteiro · CPROC)",
                "✓ Poder apud acta (Carolina Moreno · CPROC)",
                "✓ Escrito de subsanación (Carolina Moreno · CPROC)",
                "✓ Auto declaración UP (Carolina Moreno · CPROC)",
                "✓ Deontología Procura (Ana Vázquez Corte · CPROC)"
            ]
        }
    return {}

def chat(chat_id: int, user_text: str = "", media_bytes: bytes = None, mime_type: str = "image/jpeg", image_bytes: bytes = None, user_id: int = None) -> str:
    """Envía un mensaje al LLM manteniendo el hilo conversacional y generando propuestas de cambio protegidas."""
    if not GEMINI_API_KEY:
        return (
            "⚠️ <b>Falta configurar la clave de IA (GEMINI_API_KEY)</b> en el archivo <code>.env</code>.\n\n"
            "Puedes obtener tu clave gratuita en: <a href='https://aistudio.google.com/app/apikey'>Google AI Studio</a>."
        )

    if user_id is None:
        user_id = chat_id

    if image_bytes and not media_bytes:
        media_bytes = image_bytes

    histories = load_histories()
    cid_str = str(chat_id)
    chat_history = histories.get(cid_str, [])

    # Construir el nuevo turno de usuario
    user_parts = []
    if media_bytes:
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

    if len(chat_history) > 10:
        chat_history = chat_history[-10:]

    system_inst = build_system_instruction()

    models_to_try = [
        ("gemini-3.5-flash-lite", {}),
        ("gemini-3.1-flash-lite", {}),
        ("gemini-3.5-flash", {"thinkingConfig": {"thinkingBudget": 0}})
    ]

    resp_text = ""
    last_err = None
    ssl_ctx = get_ssl_context()
    for m_name, extra_gen_cfg in models_to_try:
        clean_key = GEMINI_API_KEY.strip()
        # Seguridad: la clave API NUNCA se pasa en la URL para evitar registros en servidores intermedios
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent"
        
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
            with urllib.request.urlopen(req, timeout=18, context=ssl_ctx) as resp:
                resp_json = json.loads(resp.read().decode())
                candidate = resp_json.get("candidates", [{}])[0]
                parts = candidate.get("content", {}).get("parts", [])
                text_parts = [p["text"] for p in parts if "text" in p]
                resp_text = "\n".join(text_parts).strip()
                if resp_text:
                    break
        except Exception as err:
            last_err = err
            # Loguear sin imprimir la clave
            print(f"[Assistant] Error con {m_name}: {err.__class__.__name__}. Probando siguiente modelo...", flush=True)

    if not resp_text:
        return "⚠️ Ocurrió un error al procesar tu mensaje con el servicio de IA. Inténtalo de nuevo en unos instantes."

    # Seguridad: las acciones generadas por la IA NO son autorizaciones directas.
    # Se genera una propuesta pendiente en dos fases que requiere confirmación explícita fuera de la IA.
    proposal_note = ""
    action_pattern = r'\[ACCION:(GUARDAR_NOTA|GUARDAR_PRACTICA|GUARDAR_CORREO|COMPLETAR_PRACTICA):(\{.*?\})\]'
    match = re.search(action_pattern, resp_text, re.DOTALL)
    if match:
        act_type = match.group(1)
        try:
            act_args = json.loads(match.group(2))
            ok_prop, msg_prop, prop = proposals.create_proposal(
                action_type=act_type,
                raw_payload=act_args,
                user_id=str(user_id),
                chat_id=str(chat_id)
            )
            if ok_prop and prop:
                proposal_note = "\n\n" + proposals.format_proposal_preview(prop)
            else:
                proposal_note = f"\n\n⚠️ <i>No se pudo generar la propuesta de cambio: {msg_prop}</i>"
        except Exception as e:
            print(f"[Assistant] Error al parsear JSON de acción: {e}")
        resp_text = re.sub(action_pattern, '', resp_text).strip()

    final_reply = resp_text + proposal_note

    chat_history.append({"role": "model", "parts": [{"text": resp_text}]})
    histories[cid_str] = chat_history
    save_histories(histories)

    return final_reply

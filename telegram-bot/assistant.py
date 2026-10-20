"""Asistente conversacional inteligente para el Bot de Telegram del Máster.
Soporta multi-turn chat, visión multimodal (fotos de casos y CEPROC) y llamadas a herramientas para actualizar el portal.
"""
import os
import re
import json
import base64
import urllib.request
from datetime import datetime
from pathlib import Path

from config import (
    GEMINI_API_KEY, PORTAL_PUBLIC_URL, INDEX_HTML, BASE_DIR
)
import updater

HISTORY_FILE = Path(__file__).resolve().parent / "chat_history.json"

SYSTEM_PROMPT = """Eres el Asistente Académico Personal de Raquel Escudero Valcárcel-Ríos para el Máster Universitario en Abogacía y Procura (MUAP) en A Coruña (UDC, Ilustre Colegio Provincial de Abogados de A Coruña - ICACOR, y Colegio de Procuradores).

Tu personalidad y estilo:
• Mantén una conversación fluida, inteligente, cercana, resolutiva y jurídicamente precisa.
• No eres un simple robot de comandos: respondes, dialogas, debates casos jurídicos, resuelves dudas sobre las asignaturas y aceptas instrucciones matizadas.
• Raquel te enviará a menudo fotos de casos prácticos (de CEPROC o repartidos en clase), pantallazos, correos reenviados o notas de voz, y te dará indicaciones complementarias (por ejemplo: "este caso es de Sandra Mosteiro, pero en clase dijo que la pregunta 3 no se responde y que la entrega es el viernes").
• Escucha atentamente las instrucciones de Raquel. Si te pide que le ayudes con el caso o te hace preguntas, respóndelas con rigor.
• Cuando Raquel te pida que registres o actualices el portal (o cuando te envíe un caso o correo claramente destinado a publicarse en su portal web), utiliza las herramientas disponibles (`guardar_practica` o `guardar_correo`) para actualizar el portal y publicar en GitHub.
• Si falta algún dato esencial (como el profesor o la fecha de entrega y no se puede deducir de la imagen/texto), pregúntaselo con naturalidad antes o al guardar.

Contexto actual del Máster:
• Raquel cursa el primer cuatrimestre (octubre 2026 – enero 2027) en el turno de tarde (Grupo 2).
• Profesores destacados actuales: Sandra Mosteiro Costa (Actos de comunicación judicial · Procura), José Luis Delgado Domínguez (Responsabilidad civil y penal, aseguramiento y turno de oficio · Abogacía), Ana Vázquez Corte (Deontología Procura), Carolina Moreno Vázquez (Justicia digital y poder apud acta), Daniel Garrido Pazos (Iniciación profesional).
• Plataformas: CEPROC (icpcoruna.com), Outlook Web (master.abogacia@icacor.org, accesoabogaciaprocura@..., UDC) y Google Drive.
• Portal publicado: https://raquelescuderovr.github.io/portal-master/
"""

TOOLS_SPEC = [
    {
        "function_declarations": [
            {
                "name": "guardar_practica",
                "description": "Registra una práctica, caso práctico o tarea de CEPROC o de clase en el portal académico y lo publica en GitHub.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "titulo": {"type": "STRING", "description": "Título conciso y claro de la práctica"},
                        "docente": {"type": "STRING", "description": "Nombre del profesor/a responsable"},
                        "materia": {"type": "STRING", "description": "Nombre de la asignatura o bloque"},
                        "plazo": {"type": "STRING", "description": "Fecha y hora límite de entrega"},
                        "detalles": {"type": "STRING", "description": "Descripción del caso, preguntas a resolver o indicaciones de Raquel"}
                    },
                    "required": ["titulo", "docente", "materia", "plazo", "detalles"]
                }
            },
            {
                "name": "guardar_correo",
                "description": "Registra un correo electrónico, comunicado institucional o aviso oficial en el portal académico y lo publica en GitHub.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "titulo": {"type": "STRING", "description": "Título o asunto del aviso"},
                        "remitente": {"type": "STRING", "description": "Dirección o institución remitente (ICACOR, Procuradores, UDC)"},
                        "docente": {"type": "STRING", "description": "Docente relacionado si aplica (o Administración)"},
                        "materia": {"type": "STRING", "description": "Asignatura o materia relacionada"},
                        "resumen": {"type": "STRING", "description": "Resumen ejecutivo en 1 o 2 líneas"},
                        "cuerpo": {"type": "STRING", "description": "Contenido completo o puntos clave del mensaje"}
                    },
                    "required": ["titulo", "remitente", "resumen", "cuerpo"]
                }
            },
            {
                "name": "consultar_hoy",
                "description": "Consulta las clases, horarios y sedes programadas para la jornada actual.",
                "parameters": {"type": "OBJECT", "properties": {}}
            },
            {
                "name": "consultar_entregas",
                "description": "Consulta el estado actual de todas las prácticas y entregas de CEPROC.",
                "parameters": {"type": "OBJECT", "properties": {}}
            }
        ]
    }
]

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
    """Limpia el historial de la conversación."""
    h = load_histories()
    if str(chat_id) in h:
        del h[str(chat_id)]
        save_histories(h)

def execute_tool(func_name: str, args: dict) -> dict:
    """Ejecuta una herramienta solicitada por Gemini."""
    try:
        with open(INDEX_HTML, "r", encoding="utf-8") as f:
            current_content = f.read()

        if func_name == "guardar_practica":
            titulo = args.get("titulo", "Caso práctico")
            docente = args.get("docente", "Docente asignado")
            materia = args.get("materia", "Actuación procesal")
            plazo = args.get("plazo", "Por determinar")
            detalles = args.get("detalles", "")
            now_str = datetime.now().strftime("%d oct %Y")

            new_html = updater.add_ceproc_task(
                current_content, now_str, titulo, docente, materia,
                "Procura|Técnicas instrumentales|2", "Pendiente de realizar", plazo, detalles
            )
            commit_msg = f"Añadir práctica: {titulo} ({docente}) [vía Telegram]"
            success = updater.save_and_commit(new_html, commit_msg)
            return {
                "success": success,
                "action": "guardar_practica",
                "titulo": titulo,
                "docente": docente,
                "plazo": plazo,
                "url": PORTAL_PUBLIC_URL
            }

        elif func_name == "guardar_correo":
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
            success = updater.save_and_commit(new_html, commit_msg)
            return {
                "success": success,
                "action": "guardar_correo",
                "titulo": titulo,
                "remitente": remitente,
                "url": PORTAL_PUBLIC_URL
            }

        elif func_name == "consultar_hoy":
            return {
                "fecha": "Martes 20 oct 2026",
                "sesiones": [
                    {"hora": "08:00 – 09:00", "actividad": "Pilates (personal)"},
                    {"hora": "16:30 – 18:30", "docente": "Sandra Mosteiro Costa", "materia": "Actos de comunicación judicial (Sesión 2 de 2)", "sede": "Colegio de Abogados"},
                    {"hora": "18:45 – 20:45", "docente": "José Luis Delgado Domínguez", "materia": "Responsabilidad civil y penal (Sesión 2 de 3)", "sede": "Colegio de Abogados"}
                ]
            }

        elif func_name == "consultar_entregas":
            return {
                "balance": "4 / 4 prácticas enviadas (0 vencidas)",
                "ultimas": ["Poder apud acta ✓", "Escrito de subsanación ✓", "Auto declaración UP (2 envíos) ✓", "Caso Deontología Procura ✓"]
            }

    except Exception as e:
        return {"success": False, "error": str(e)}

    return {"error": f"Herramienta desconocida: {func_name}"}

def chat(chat_id: int, user_text: str = "", image_bytes: bytes = None, mime_type: str = "image/jpeg") -> str:
    """Envía un mensaje al LLM manteniendo el hilo conversacional y ejecutando herramientas."""
    if not GEMINI_API_KEY:
        return (
            "⚠️ <b>Falta configurar la clave de IA (GEMINI_API_KEY)</b> en el archivo <code>.env</code>.\n\n"
            "Para que pueda mantener una <b>conversación inteligente y fluida contigo</b> (analizar fotos de casos, debatir instrucciones y redactar respuestas como ChatGPT), "
            "solo necesitas obtener tu clave gratuita en 10 segundos en: "
            "<a href='https://aistudio.google.com/app/apikey'>Google AI Studio</a> y añadirla al <code>.env</code>."
        )

    histories = load_histories()
    cid_str = str(chat_id)
    chat_history = histories.get(cid_str, [])

    # Construir el nuevo mensaje del usuario
    user_parts = []
    if image_bytes:
        b64_data = base64.b64encode(image_bytes).decode("utf-8")
        user_parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": b64_data
            }
        })
    if user_text:
        user_parts.append({"text": user_text})
    elif image_bytes and not user_text:
        user_parts.append({"text": "Te paso esta captura o foto de un caso/documento del Máster. Analízala y cuéntame qué contiene."})

    chat_history.append({"role": "user", "parts": user_parts})

    # Limitar tamaño de historial (últimos 16 turnos) para no saturar contexto
    if len(chat_history) > 16:
        chat_history = chat_history[-16:]

    # Llamada a la API de Gemini (soporta Tool Calling y Multi-turn)
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    req_headers = {
        "Content-Type": "application/json",
        "User-Agent": "Master-AI-Assistant/1.0",
        "x-goog-api-key": GEMINI_API_KEY.strip()
    }

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": chat_history,
        "tools": TOOLS_SPEC,
        "generationConfig": {"temperature": 0.4}
    }

    try:
        final_answer = ""
        # Bucle de interacción (soporta llamadas a funciones)
        for _ in range(3):
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                api_url,
                data=req_data,
                headers=req_headers,
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_json = json.loads(resp.read().decode())

            candidate = resp_json.get("candidates", [{}])[0]
            model_parts = candidate.get("content", {}).get("parts", [])

            # Comprobar si hay functionCall
            function_calls = [p["functionCall"] for p in model_parts if "functionCall" in p]
            text_parts = [p["text"] for p in model_parts if "text" in p]

            if not function_calls:
                final_answer = "\n".join(text_parts).strip()
                chat_history.append({"role": "model", "parts": model_parts})
                break

            # Si hay llamadas a funciones: ejecutarlas y devolver el resultado
            chat_history.append({"role": "model", "parts": model_parts})
            func_results_parts = []

            for fc in function_calls:
                f_name = fc["name"]
                f_args = fc.get("args", {})
                res = execute_tool(f_name, f_args)
                func_results_parts.append({
                    "functionResponse": {
                        "name": f_name,
                        "response": {"output": res}
                    }
                })

            chat_history.append({"role": "function", "parts": func_results_parts})
            payload["contents"] = chat_history

        # Guardar historial actualizado
        histories[cid_str] = chat_history
        save_histories(histories)

        return final_answer or "✅ Instrucción procesada correctamente."

    except Exception as e:
        print(f"[Assistant] Error en API Gemini: {e}")
        return f"⚠️ Ocurrió un error al procesar tu mensaje: <code>{str(e)}</code>"

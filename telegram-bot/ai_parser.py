"""Módulo de análisis de texto e imágenes (con Gemini API o heurísticas nativas)."""
import re
import json
import base64
import urllib.request
from datetime import datetime
from config import GEMINI_API_KEY

def parse_text_or_image(text: str = "", image_bytes: bytes = None, mime_type: str = "image/jpeg") -> dict:
    """Extrae información estructurada de un correo o captura de CEPROC."""
    if GEMINI_API_KEY:
        try:
            return call_gemini_api(text, image_bytes, mime_type)
        except Exception as e:
            print(f"[AI Parser] Error con Gemini API: {e}. Usando parser heurístico.")

    return parse_heuristic_text(text)

def call_gemini_api(text: str, image_bytes: bytes = None, mime_type: str = "image/jpeg") -> dict:
    """Llama a la API de Google Gemini (Flash) para analizar texto o capturas de pantalla."""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    
    prompt = """Eres un asistente académico para el Máster en Abogacía y Procura de Raquel Escudero.
Analiza la siguiente información (correo electrónico, aviso o captura de CEPROC) y devuelve EXCLUSIVAMENTE un objeto JSON válido con la siguiente estructura:
{
  "type": "mail" o "ceproc_task",
  "title": "Título conciso y claro",
  "date": "Fecha del correo o publicación (ej. 19 oct 2026)",
  "sender_or_teacher": "Nombre del profesor o remitente",
  "subject": "Nombre de la asignatura o materia",
  "subject_ref": "Rama|Asignatura|0",
  "meta": "Remitente o fuente institucional",
  "deadline": "Fecha y hora límite de entrega si es una tarea, o cadena vacía",
  "summary": "Resumen ejecutivo en 1 o 2 líneas",
  "body": "Texto completo o descripción detallada de la instrucción o tarea"
}
Solo devuelve el JSON sin formato markdown ni texto adicional."""

    contents_parts = [{"text": prompt}]
    if text:
        contents_parts.append({"text": f"Texto de entrada:\n{text}"})
    if image_bytes:
        b64_img = base64.b64encode(image_bytes).decode("utf-8")
        contents_parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": b64_img
            }
        })

    payload = {
        "contents": [{"parts": contents_parts}],
        "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY.strip()
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=25) as resp:
        result = json.loads(resp.read().decode())
        raw_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        # Limpiar posibles bloques ```json ... ```
        raw_text = re.sub(r"^```json\s*", "", raw_text)
        raw_text = re.sub(r"\s*```$", "", raw_text)
        return json.loads(raw_text)

def parse_heuristic_text(text: str) -> dict:
    """Parser heurístico basado en patrones de correo y avisos académicos comunes."""
    t = text.strip()
    is_ceproc = bool(re.search(r"cproc|ceproc|tarea|práctica|entrega|caso práctico", t, re.I))

    # Detección de remitente
    sender = "Administración del Máster"
    meta = "master.abogacia@icacor.org · Máster Abogacía y Procura"
    if "procuradores" in t.lower() or "accesoabogaciaprocura" in t.lower():
        sender = "Secretaría Colegio de Procuradores"
        meta = "accesoabogaciaprocura@procuradores... · Procura"
    elif "decanato" in t.lower() or "facultad" in t.lower() or "udc" in t.lower():
        sender = "Decanato Facultad de Derecho"
        meta = "Decanato Facultade de Dereito · UDC"

    # Detección de título / Asunto
    asunto_match = re.search(r"(?:Asunto|Subject|Título):\s*(.+)", t, re.I)
    title = asunto_match.group(1).strip() if asunto_match else t.split("\n")[0][:75]

    # Fecha actual por defecto
    now_str = datetime.now().strftime("%d oct %Y")

    if is_ceproc:
        return {
            "type": "ceproc_task",
            "title": title or "Nueva práctica publicada en CEPROC",
            "date": now_str,
            "sender_or_teacher": sender,
            "subject": "Procura · Actuación procesal",
            "subject_ref": "Procura|Técnicas instrumentales|2",
            "meta": "Plataforma CEPROC (MUAP)",
            "deadline": "Consultar en plataforma",
            "summary": title,
            "body": t
        }

    return {
        "type": "mail",
        "title": title or "Aviso académico del Máster",
        "date": now_str,
        "sender_or_teacher": sender,
        "subject": "Técnicas instrumentales y deontología",
        "subject_ref": "Abogacía|Técnicas instrumentales|3",
        "meta": meta,
        "deadline": "",
        "summary": t[:150] + ("..." if len(t) > 150 else ""),
        "body": t
    }

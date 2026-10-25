"""Módulo de análisis de texto e imágenes (con Gemini API o heurísticas nativas)."""
import re
import json
import base64
import urllib.request
from datetime import datetime
from config import GEMINI_API_KEY

def parse_text_or_image(text: str = "", image_bytes: bytes = None, mime_type: str = "image/jpeg") -> dict:
    """Extrae información estructurada de un correo, calificación o captura de CEPROC."""
    if GEMINI_API_KEY:
        try:
            return call_gemini_api(text, image_bytes, mime_type)
        except Exception as e:
            print(f"[AI Parser] Error con Gemini API: {e}. Usando parser heurístico.")

    return parse_heuristic_text(text)

def call_gemini_api(text: str, image_bytes: bytes = None, mime_type: str = "image/jpeg") -> dict:
    """Llama a la API de Google Gemini para analizar texto, notas o capturas de pantalla."""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    
    prompt = """Eres un asistente académico experto para el Máster en Abogacía y Procura (MUAP) de Raquel Escudero.
Analiza la siguiente información (correo electrónico, aviso, calificación / nota de test, o captura de CEPROC / plataforma) y devuelve EXCLUSIVAMENTE un objeto JSON válido.

Reglas de clasificación del campo "type":
- "grade": Si es una comunicación de notas, calificaciones de pruebas, resultados de test, actas o correos oficiales de evaluación (ej. "Resultados de las pruebas", "Calificaciones", "Nota: 10/10", "Aptos", etc.).
- "ceproc_task": Si es la publicación de una nueva práctica, caso práctico, tarea con plazo de entrega o instrucción de trabajo en CEPROC.
- "mail": Si es un aviso informativo general, convocatoria, circular o correo organizativo.

Estructura JSON exacta requerida:
{
  "type": "grade" | "ceproc_task" | "mail",
  "title": "Título conciso y claro",
  "date": "Fecha del correo o publicación (ej. 23 oct 2026)",
  "sender_or_teacher": "Nombre del profesor/a o remitente docente",
  "subject": "Nombre de la asignatura o materia",
  "subject_ref": "Rama|Asignatura|0",
  "meta": "Remitente o fuente institucional",
  "score": "Nota obtenida si es calificación (ej. '10 / 10' o '9 / 10') o cadena vacía",
  "score_label": "Etiqueta de la nota (ej. 'Nota oficial', 'Nota docente', 'Test online')",
  "breakdown": [
    {"label": "Parte evaluada", "val": "Puntuación"}
  ],
  "deadline": "Fecha y hora límite de entrega si es una tarea, o cadena vacía",
  "summary": "Resumen ejecutivo en 1 o 2 líneas",
  "body": "Texto completo o descripción detallada"
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
        raw_text = re.sub(r"^```json\s*", "", raw_text)
        raw_text = re.sub(r"\s*```$", "", raw_text)
        return json.loads(raw_text)

def parse_heuristic_text(text: str) -> dict:
    """Parser heurístico basado en patrones de correo, notas y avisos académicos comunes."""
    t = text.strip()
    is_grade = bool(re.search(r"calificaci[oó]n|resultados?\s+de\s+las?\s+pruebas?|notas?|sobresaliente|notable|\b\d{1,2}\s*/\s*10\b|puntuaci[oó]n|aciertos", t, re.I))
    is_ceproc = bool(re.search(r"cproc|ceproc|tarea|práctica|entrega|caso práctico", t, re.I)) and not is_grade

    # Detección de docente / remitente
    sender = "Administración del Máster"
    meta = "master.abogacia@icacor.org · Máster Abogacía y Procura"
    if "carolina moreno" in t.lower():
        sender = "Carolina Moreno Vázquez"
    elif "sandra mosteiro" in t.lower():
        sender = "Sandra Mosteiro Costa"
    elif "delgado" in t.lower():
        sender = "José Luis Delgado Domínguez"
    elif "ana vázquez" in t.lower():
        sender = "Ana Vázquez Corte"
    elif "carlos miguel" in t.lower() or "carlos m. sánchez" in t.lower():
        sender = "Carlos M. Sánchez Muiño"
    elif "javier sánchez" in t.lower():
        sender = "Javier Sánchez García"
    elif "procuradores" in t.lower() or "accesoabogaciaprocura" in t.lower():
        sender = "Secretaría Colegio de Procuradores"
        meta = "accesoabogaciaprocura@procuradores-coruna.com · Procura"
    elif "decanato" in t.lower() or "facultad" in t.lower() or "udc" in t.lower():
        sender = "Decanato Facultad de Derecho"
        meta = "Decanato Facultade de Dereito · UDC"

    # Detección de título / Asunto
    asunto_match = re.search(r"(?:Asunto|Subject|Título):\s*(.+)", t, re.I)
    title = asunto_match.group(1).strip() if asunto_match else t.split("\n")[0][:75]

    now_str = datetime.now().strftime("%d oct %Y")
    if is_grade:
        # Extraer nota aproximada (ej: 'Nota: 9/10', '10 / 10', '9.5/10', evitando fechas tipo 20/10/2026)
        score_match = re.search(r"(?:nota|calificación|puntuación|resultado)?\s*:?\s*(\b(?:10|[0-9](?:[.,][0-9]+)?)\s*/\s*10\b)(?!/\d{2,4})", t, re.I)
        score_val = score_match.group(1).replace(",", ".").strip() if score_match else "10 / 10"
        return {
            "type": "grade",
            "title": title or "Calificaciones oficiales de la asignatura",
            "date": now_str,
            "sender_or_teacher": sender,
            "subject": "Técnicas instrumentales y procesales",
            "subject_ref": "Procura|Técnicas instrumentales|2",
            "meta": meta,
            "score": score_val,
            "score_label": "Nota oficial",
            "breakdown": [{"label": "Calificación global", "val": score_val}],
            "deadline": "",
            "summary": title,
            "body": t
        }

    if is_ceproc:
        is_abogacia = "delgado" in sender.lower() or "abogad" in t.lower()
        sub_default = "Abogacía · Responsabilidad profesional" if is_abogacia else "Procura · Actuación procesal"
        subref_default = "Abogacía|Técnicas instrumentales|3" if is_abogacia else "Procura|Técnicas instrumentales|2"
        meta_default = "Colegio de Abogados (ICACOR) · secretariatecnico@icacor.org" if is_abogacia else "Plataforma CEPROC (MUAP)"
        return {
            "type": "ceproc_task",
            "title": title or ("Nueva práctica de Abogacía (ICACOR)" if is_abogacia else "Nueva práctica publicada en CEPROC"),
            "date": now_str,
            "sender_or_teacher": sender,
            "subject": sub_default,
            "subject_ref": subref_default,
            "meta": meta_default,
            "deadline": "Consultar instrucciones",
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
        "score": "",
        "score_label": "",
        "breakdown": [],
        "deadline": "",
        "summary": t[:150] + ("..." if len(t) > 150 else ""),
        "body": t
    }

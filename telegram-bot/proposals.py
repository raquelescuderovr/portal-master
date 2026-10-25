"""Módulo de gestión y confirmación en dos fases de propuestas de cambio.
Garantiza que ninguna acción del LLM se ejecute sin confirmación explícita,
validando usuario, chat privado, vigencia temporal (TTL) y unicidad (anti-replay).
"""
import time
import json
import hashlib
import secrets
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

PROPOSALS_FILE = Path(__file__).resolve().parent / "pending_proposals.json"

# Esquema estricto de campos permitidos y longitudes máximas por tipo de acción
ACTION_SCHEMAS = {
    "GUARDAR_PRACTICA": {
        "required": ["titulo", "docente", "materia"],
        "fields": {
            "titulo": 150,
            "docente": 100,
            "materia": 100,
            "plazo": 80,
            "detalles": 1500
        }
    },
    "GUARDAR_CORREO": {
        "required": ["titulo", "remitente"],
        "fields": {
            "titulo": 150,
            "remitente": 120,
            "docente": 100,
            "materia": 100,
            "resumen": 500,
            "cuerpo": 5000
        }
    },
    "GUARDAR_NOTA": {
        "required": ["titulo", "docente", "materia", "nota"],
        "fields": {
            "titulo": 150,
            "docente": 100,
            "materia": 100,
            "nota": 30,
            "tipo_nota": 60,
            "remitente": 120,
            "resumen": 500,
            "cuerpo": 5000,
            "desglose": None  # Lista validada específicamente
        }
    },
    "COMPLETAR_PRACTICA": {
        "required": ["termino"],
        "fields": {
            "termino": 150
        }
    }
}

# Almacén en memoria de propuestas
_proposals_cache: Dict[str, Dict[str, Any]] = {}


def _load_proposals() -> Dict[str, Dict[str, Any]]:
    global _proposals_cache
    if not _proposals_cache and PROPOSALS_FILE.exists():
        try:
            with open(PROPOSALS_FILE, "r", encoding="utf-8") as f:
                _proposals_cache = json.load(f)
        except Exception:
            _proposals_cache = {}
    return _proposals_cache


def _save_proposals():
    try:
        # Filtrar propuestas caducadas hace más de 1 hora para evitar crecimiento indefinido
        now = time.time()
        cleaned = {k: v for k, v in _proposals_cache.items() if now - v.get("created_at", 0) < 3600}
        with open(PROPOSALS_FILE, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Proposals] Error al persistir propuestas: {e}", flush=True)


def compute_payload_hash(action_type: str, payload: dict) -> str:
    """Calcula el hash SHA-256 canónico del contenido propuesto."""
    canon = json.dumps({"action": action_type, "payload": payload}, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def validate_action_payload(action_type: str, raw: dict) -> Tuple[bool, str, dict]:
    """Valida los campos, tipos y longitudes de la acción generada por el modelo."""
    if action_type not in ACTION_SCHEMAS:
        return False, f"Tipo de acción no permitido: «{action_type}»", {}

    if not isinstance(raw, dict):
        return False, "La carga útil de la acción debe ser un objeto JSON.", {}

    schema = ACTION_SCHEMAS[action_type]
    req_fields = schema["required"]
    field_limits = schema["fields"]

    # Comprobar campos obligatorios
    for req in req_fields:
        val = raw.get(req)
        if not val or not str(val).strip():
            return False, f"Falta el campo obligatorio «{req}» en la acción {action_type}.", {}

    sanitized = {}
    for k, v in raw.items():
        if k not in field_limits:
            # Rechazar claves inesperadas para evitar inyecciones de campos no permitidos
            continue

        max_len = field_limits[k]
        if k == "desglose":
            if not isinstance(v, list):
                continue
            clean_desglose = []
            for item in v[:8]:  # Máximo 8 elementos en el desglose
                if isinstance(item, dict):
                    lbl = str(item.get("label", ""))[:50].strip()
                    val = str(item.get("val", ""))[:30].strip()
                    if lbl and val:
                        clean_desglose.append({"label": lbl, "val": val})
            sanitized["desglose"] = clean_desglose
        else:
            s_val = str(v).strip()
            if max_len and len(s_val) > max_len:
                s_val = s_val[:max_len]
            sanitized[k] = s_val

    return True, "OK", sanitized


def create_proposal(
    action_type: str,
    raw_payload: dict,
    user_id: str,
    chat_id: str,
    ttl_seconds: int = 900
) -> Tuple[bool, str, Optional[dict]]:
    """Valida y registra una nueva propuesta en espera de confirmación explícita."""
    ok, err, clean_payload = validate_action_payload(action_type, raw_payload)
    if not ok:
        return False, err, None

    proposals = _load_proposals()
    s_user = str(user_id)
    s_chat = str(chat_id)

    # Invalidar cualquier propuesta pendiente previa de esta misma usuaria/chat
    now = time.time()
    for pid, pdata in list(proposals.items()):
        if str(pdata.get("user_id")) == s_user and str(pdata.get("chat_id")) == s_chat and not pdata.get("used"):
            pdata["cancelled"] = True

    prop_id = "p_" + secrets.token_hex(4)  # Identificador corto y unívoco: p_a1b2c3d4
    content_hash = compute_payload_hash(action_type, clean_payload)

    proposal = {
        "id": prop_id,
        "action_type": action_type,
        "payload": clean_payload,
        "content_hash": content_hash,
        "user_id": s_user,
        "chat_id": s_chat,
        "created_at": now,
        "expires_at": now + ttl_seconds,
        "used": False,
        "cancelled": False
    }

    proposals[prop_id] = proposal
    _save_proposals()
    return True, "Propuesta creada", proposal


def get_active_proposal_for_user(user_id: str, chat_id: str) -> Optional[dict]:
    """Devuelve la propuesta activa no caducada y no usada para el usuario/chat."""
    proposals = _load_proposals()
    s_user = str(user_id)
    s_chat = str(chat_id)
    now = time.time()

    for pid, pdata in proposals.items():
        if (
            str(pdata.get("user_id")) == s_user and
            str(pdata.get("chat_id")) == s_chat and
            not pdata.get("used") and
            not pdata.get("cancelled") and
            pdata.get("expires_at", 0) > now
        ):
            return pdata
    return None


def confirm_proposal(
    prop_id: str,
    user_id: str,
    chat_id: str
) -> Tuple[bool, str, Optional[dict]]:
    """Valida estrictamente la confirmación fuera del modelo de IA."""
    proposals = _load_proposals()
    s_user = str(user_id)
    s_chat = str(chat_id)
    now = time.time()

    if prop_id not in proposals:
        return False, "La propuesta solicitada no existe o ha sido eliminada.", None

    prop = proposals[prop_id]

    # 1. Comprobar que no ha sido usada previamente (Anti-Replay)
    if prop.get("used"):
        return False, "Esta propuesta ya fue confirmada y aplicada anteriormente.", None

    # 2. Comprobar que no fue cancelada
    if prop.get("cancelled"):
        return False, "Esta propuesta fue cancelada al generarse un cambio posterior.", None

    # 3. Comprobar caducidad (TTL)
    if prop.get("expires_at", 0) <= now:
        return False, "La propuesta ha caducado (límite de 15 minutos superado). Solicita el cambio de nuevo.", None

    # 4. Comprobar remitente y chat autorizado
    if str(prop.get("user_id")) != s_user or str(prop.get("chat_id")) != s_chat:
        return False, "Operación no autorizada: usuario o chat no coinciden con la propuesta.", None

    # 5. Comprobar integridad del contenido
    expected_hash = compute_payload_hash(prop["action_type"], prop["payload"])
    if prop.get("content_hash") != expected_hash:
        return False, "Error de integridad: el contenido de la propuesta ha sido alterado.", None

    # Marcar como usada
    prop["used"] = True
    prop["confirmed_at"] = now
    _save_proposals()

    return True, "Confirmación verificada con éxito", prop


def cancel_proposals(user_id: str, chat_id: str) -> int:
    """Cancela todas las propuestas pendientes de un usuario."""
    proposals = _load_proposals()
    s_user = str(user_id)
    s_chat = str(chat_id)
    count = 0
    for pid, pdata in proposals.items():
        if str(pdata.get("user_id")) == s_user and str(pdata.get("chat_id")) == s_chat and not pdata.get("used"):
            pdata["cancelled"] = True
            count += 1
    if count > 0:
        _save_proposals()
    return count


def format_proposal_preview(proposal: dict) -> str:
    """Genera la vista previa exacta y comprensible de lo que se publicará."""
    act = proposal["action_type"]
    p = proposal["payload"]
    pid = proposal["id"]
    mins_left = max(1, int((proposal["expires_at"] - time.time()) / 60))

    if act == "GUARDAR_PRACTICA":
        desc = (
            f"📋 <b>Propuesta de publicación: Nueva Práctica</b>\n\n"
            f"• <b>Título:</b> {p.get('titulo')}\n"
            f"• <b>Docente:</b> {p.get('docente')}\n"
            f"• <b>Asignatura:</b> {p.get('materia')}\n"
            f"• <b>Plazo:</b> {p.get('plazo', 'Por determinar')}\n"
            f"• <b>Detalles:</b> {p.get('detalles', 'Ninguno')}"
        )
    elif act == "GUARDAR_CORREO":
        desc = (
            f"📬 <b>Propuesta de publicación: Nuevo Aviso o Correo</b>\n\n"
            f"• <b>Título:</b> {p.get('titulo')}\n"
            f"• <b>Remitente:</b> {p.get('remitente')}\n"
            f"• <b>Docente:</b> {p.get('docente', 'Administración')}\n"
            f"• <b>Asignatura:</b> {p.get('materia', 'General')}\n"
            f"• <b>Resumen:</b> {p.get('resumen')}"
        )
    elif act == "GUARDAR_NOTA":
        desc = (
            f"⭐ <b>Propuesta de publicación: Calificación Oficial</b>\n\n"
            f"• <b>Título:</b> {p.get('titulo')}\n"
            f"• <b>Nota:</b> {p.get('nota')} ({p.get('tipo_nota', 'Oficial')})\n"
            f"• <b>Docente:</b> {p.get('docente')}\n"
            f"• <b>Asignatura:</b> {p.get('materia')}\n"
            f"• <b>Remitente:</b> {p.get('remitente')}"
        )
    elif act == "COMPLETAR_PRACTICA":
        desc = (
            f"✅ <b>Propuesta de cambio: Marcar Práctica como Completada</b>\n\n"
            f"• <b>Práctica:</b> {p.get('termino')}"
        )
    else:
        desc = f"⚠️ <b>Propuesta desconocida ({act})</b>"

    instructions = (
        f"\n\n🔒 <b>Requiere tu confirmación explícita fuera de la IA:</b>\n"
        f"Para publicar en tu portal web, pulsa o escribe:\n"
        f"<code>/confirmar {pid}</code>\n\n"
        f"<i>(Expira en {mins_left} min · Solo ejecutable desde tu chat privado).</i>\n"
        f"Si no es correcto, pulsa <code>/cancelar</code>."
    )
    return desc + instructions

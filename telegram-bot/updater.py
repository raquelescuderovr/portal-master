"""Módulo para actualizar portal-master/index.html (tanto en local como vía GitHub API)."""
import re
import os
import json
import base64
import urllib.request
import subprocess
from datetime import datetime
from config import INDEX_HTML, GITHUB_TOKEN, GITHUB_REPO, GITHUB_BRANCH, PORTAL_DIR

def sanitize_js_string(s: str) -> str:
    """Escapa comillas simples y saltos de línea para incrustar en JavaScript."""
    if not s:
        return ""
    return s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")

def add_mail_entry(content: str, date_str: str, title: str, meta: str, key: str, 
                   teacher: str, subject_ref: str, summary: str, body: str, source: str) -> str:
    """Inserta un nuevo correo en messages, mailSummaries y details en index.html."""
    s_date = sanitize_js_string(date_str)
    s_title = sanitize_js_string(title)
    s_meta = sanitize_js_string(meta)
    s_key = re.sub(r'[^a-zA-Z0-9_]', '_', key.strip().lower())
    s_teacher = sanitize_js_string(teacher)
    s_subref = sanitize_js_string(subject_ref)
    s_summary = sanitize_js_string(summary)
    s_body = sanitize_js_string(body)
    s_source = sanitize_js_string(source)

    # 1. Insertar en const messages=[
    msg_entry = (
        f" {{date:'{s_date}',title:'{s_title}',meta:'{s_meta}',key:'{s_key}',"
        f"teacher:'{s_teacher}',subjectRef:'{s_subref}'}},\n"
    )
    if "const messages=[" in content:
        content = content.replace("const messages=[\n", "const messages=[\n" + msg_entry, 1)

    # 2. Insertar en const mailSummaries={
    summary_entry = f" {s_key}:'{s_summary}',\n"
    if "const mailSummaries={" in content:
        content = content.replace("const mailSummaries={\n", "const mailSummaries={\n" + summary_entry, 1)

    # 3. Insertar en const details={
    detail_entry = f""" {s_key}:{{
  kicker:'Comunicación académica · Máster',
  title:'{s_title}',
  date:'Recibido: {s_date}',
  teacher:'{s_teacher}',
  subjectRef:'{s_subref}',
  body:'{s_body}',
  source:'{s_source}',
  attachments:[
   {{name:'Bandeja de entrada en Outlook',url:outlookUrl,kind:'Outlook Web'}}
  ]
 }},
"""
    if "const details={" in content:
        content = content.replace("const details={\n", "const details={\n" + detail_entry, 1)

    return content

def add_ceproc_task(content: str, date_str: str, title: str, teacher: str, subject: str,
                    subject_ref: str, status: str, deadline_str: str, details_text: str) -> str:
    """Inserta una nueva práctica/tarea de CEPROC en deliveries y details."""
    s_title = sanitize_js_string(title)
    s_teacher = sanitize_js_string(teacher)
    s_subject = sanitize_js_string(subject)
    s_subref = sanitize_js_string(subject_ref)
    s_status = sanitize_js_string(status or "Pendiente de realizar")
    s_details = sanitize_js_string(details_text)
    detail_key = "entrega_" + re.sub(r'[^a-zA-Z0-9_]', '_', title.strip().lower())[:25]

    now = datetime.now()
    delivery_entry = (
        f" {{date:new Date({now.year},{now.month-1},{now.day}),title:'{s_title}',teacher:'{s_teacher}',"
        f"subject:'{s_subject}',subjectRef:'{s_subref}',status:'{s_status}',submitted:false,"
        f"detailKey:'{detail_key}',details:'{s_details}'}},\n"
    )
    if "const deliveries=[" in content:
        content = content.replace("const deliveries=[\n", "const deliveries=[\n" + delivery_entry, 1)

    detail_entry = f""" {detail_key}:{{
  isDelivery:true,
  kicker:'Práctica CEPROC · {s_subject}',
  title:'{s_title}',
  date:'Publicada: {sanitize_js_string(date_str)} · Plazo: {sanitize_js_string(deadline_str)}',
  teacher:'{s_teacher}',
  subjectRef:'{s_subref}',
  body:'{s_details}',
  source:'Plataforma CEPROC (MUAP)',
  attachments:[
   {{name:'Abrir plataforma CPROC (MUAP)',url:cprocUrl,kind:'Plataforma CPROC'}}
  ]
 }},
"""
    if "const details={" in content:
        content = content.replace("const details={\n", "const details={\n" + detail_entry, 1)

    return content

def save_and_commit(new_content: str, commit_msg: str) -> bool:
    """Guarda los cambios localmente o a través de la API de GitHub."""
    # 1. Modo Local si el archivo existe
    if INDEX_HTML.exists():
        with open(INDEX_HTML, "w", encoding="utf-8") as f:
            f.write(new_content)
        try:
            subprocess.run(["git", "-C", str(PORTAL_DIR), "add", "index.html"], check=True)
            subprocess.run(["git", "-C", str(PORTAL_DIR), "commit", "-m", commit_msg], check=True)
            subprocess.run(["git", "-C", str(PORTAL_DIR), "push", "origin", GITHUB_BRANCH], check=True)
            return True
        except Exception as e:
            print(f"[Updater] Error en git local: {e}")
            # Si falla git local (por ejemplo en la nube), intenta GitHub API

    # 2. Modo Nube (GitHub REST API)
    if GITHUB_TOKEN and GITHUB_REPO:
        return commit_via_github_api(new_content, commit_msg)

    return False

def commit_via_github_api(new_content: str, commit_msg: str) -> bool:
    """Realiza un commit en GitHub directamente mediante la API REST oficial."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/index.html"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Master-Telegram-Bot"
    }

    try:
        # Obtener SHA actual del archivo
        req = urllib.request.Request(url + f"?ref={GITHUB_BRANCH}", headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            current_sha = data["sha"]

        # Crear el commit
        b64_content = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")
        payload = {
            "message": commit_msg,
            "content": b64_content,
            "sha": current_sha,
            "branch": GITHUB_BRANCH
        }
        put_data = json.dumps(payload).encode("utf-8")
        put_req = urllib.request.Request(url, data=put_data, headers=headers, method="PUT")
        with urllib.request.urlopen(put_req) as resp:
            return resp.status in (200, 201)
    except Exception as e:
        print(f"[Updater] Error en GitHub API: {e}")
        return False

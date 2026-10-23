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
    return str(s).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")

def update_teacher_directory(content: str, teacher_name: str, grade_score: str = None, 
                             grade_badge: str = None, grade_detail: str = None, 
                             mail_item: dict = None, practice_item: dict = None, 
                             detail_key: str = None) -> str:
    """Actualiza o añade información en la ficha del profesor dentro de const teacherDirectory=[."""
    if not teacher_name:
        return content

    td_match = re.search(r"(const teacherDirectory=\[)(.*?)(\];\s*const catalogMaterials)", content, re.DOTALL)
    if not td_match:
        return content

    td_block = td_match.group(2)
    s_tname = teacher_name.strip()
    idx = td_block.find(f"name:'{s_tname}'")
    if idx == -1:
        # Intentar coincidencia parcial
        pattern = re.compile(rf"name:'([^']*?{re.escape(s_tname)}[^']*?)'", re.IGNORECASE)
        m = pattern.search(td_block)
        if m:
            s_tname = m.group(1)
            idx = td_block.find(f"name:'{s_tname}'")

    if idx == -1:
        return content

    start_obj = td_block.rfind("{\n", 0, idx)
    if start_obj == -1:
        start_obj = td_block.rfind("{", 0, idx)

    depth = 0
    end_obj = -1
    for i in range(start_obj, len(td_block)):
        if td_block[i] == "{":
            depth += 1
        elif td_block[i] == "}":
            depth -= 1
            if depth == 0:
                end_obj = i + 1
                break

    if end_obj == -1:
        return content

    old_obj = td_block[start_obj:end_obj]
    new_obj = old_obj

    # 1. Actualizar gradeBadge
    if grade_badge:
        s_gb = sanitize_js_string(grade_badge)
        new_obj = re.sub(r"gradeBadge:'[^']*'", f"gradeBadge:'{s_gb}'", new_obj)

    # 2. Actualizar o insertar grade: { ... }
    if grade_score or grade_detail:
        s_gscore = sanitize_js_string(grade_score)
        s_gdet = sanitize_js_string(grade_detail)
        s_dkey = sanitize_js_string(detail_key)
        if "grade:{" in new_obj:
            if s_gscore:
                new_obj = re.sub(r"score:'[^']*'", f"score:'{s_gscore}'", new_obj, count=1)
            if s_gdet:
                new_obj = re.sub(r"detail:'[^']*'", f"detail:'{s_gdet}'", new_obj, count=1)
            if s_dkey:
                new_obj = re.sub(r"detailKey:'[^']*'", f"detailKey:'{s_dkey}'", new_obj, count=1)
        else:
            d_key_str = f",detailKey:'{s_dkey}'" if s_dkey else ""
            grade_chunk = f"  grade:{{score:'{s_gscore or '10 / 10'}',scoreLabel:'Calificación',detail:'{s_gdet}'{d_key_str}}},\n"
            new_obj = re.sub(r"(gradeBadge:'[^']*',\n)", r"\1" + grade_chunk, new_obj)

    # 3. Insertar correo en mails: [ ... ]
    if mail_item:
        m_title = sanitize_js_string(mail_item.get("title", ""))
        m_key = sanitize_js_string(mail_item.get("key", ""))
        if f"key:'{m_key}'" not in new_obj:
            m_entry = f"{{title:'{m_title}',key:'{m_key}'}}"
            if "mails:[" in new_obj:
                new_obj = new_obj.replace("mails:[", f"mails:[{m_entry},", 1)
            elif "mails: [" in new_obj:
                new_obj = new_obj.replace("mails: [", f"mails: [{m_entry},", 1)

    # 4. Insertar práctica en practices: [ ... ]
    if practice_item:
        p_title = sanitize_js_string(practice_item.get("title", ""))
        p_status = sanitize_js_string(practice_item.get("status", ""))
        p_key = sanitize_js_string(practice_item.get("key", ""))
        if f"key:'{p_key}'" not in new_obj and p_title not in new_obj:
            p_entry = f"\n   {{title:'{p_title}',status:'{p_status}',key:'{p_key}'}},"
            if "practices:[" in new_obj:
                new_obj = new_obj.replace("practices:[", f"practices:[{p_entry}", 1)
            elif "practices: [" in new_obj:
                new_obj = new_obj.replace("practices: [", f"practices: [{p_entry}", 1)

    new_td_block = td_block[:start_obj] + new_obj + td_block[end_obj:]
    return content[:td_match.start(2)] + new_td_block + content[td_match.end(2):]

def update_course_subject(content: str, subject_name: str = None, teacher_name: str = None, 
                          grade_score: str = None, grade_detail: str = None, 
                          detail_key: str = None, mail_key: str = None, 
                          practice_entry: dict = None) -> str:
    """Actualiza o añade información a la asignatura correspondiente en const courses=[."""
    c_match = re.search(r"(const courses=\[)(.*?)(\];\s*const teacherDirectory)", content, re.DOTALL)
    if not c_match:
        return content

    c_block = c_match.group(2)
    idx = -1
    if subject_name:
        s_sname = sanitize_js_string(subject_name)
        idx = c_block.find(f"name:'{s_sname}'")
        if idx == -1:
            # Búsqueda flexible
            m = re.search(rf"name:'([^']*?{re.escape(s_sname[:20])}[^']*?)'", c_block, re.IGNORECASE)
            if m:
                idx = m.start()

    if idx == -1 and teacher_name:
        s_tname = sanitize_js_string(teacher_name)
        idx = c_block.find(f"teachers:['{s_tname}']")
        if idx == -1:
            idx = c_block.find(f"'{s_tname}'")

    if idx == -1:
        return content

    start_obj = c_block.rfind("{\n", 0, idx)
    if start_obj == -1:
        start_obj = c_block.rfind("{", 0, idx)

    depth = 0
    end_obj = -1
    for i in range(start_obj, len(c_block)):
        if c_block[i] == "{":
            depth += 1
        elif c_block[i] == "}":
            depth -= 1
            if depth == 0:
                end_obj = i + 1
                break

    if end_obj == -1:
        return content

    old_obj = c_block[start_obj:end_obj]
    new_obj = old_obj

    # 1. Calificación en la asignatura
    if grade_score or grade_detail:
        s_gscore = sanitize_js_string(grade_score)
        s_gdet = sanitize_js_string(grade_detail)
        s_dkey = sanitize_js_string(detail_key)
        if "grade:{" in new_obj:
            if s_gscore:
                new_obj = re.sub(r"score:'[^']*'", f"score:'{s_gscore}'", new_obj, count=1)
            if s_gdet:
                new_obj = re.sub(r"detail:'[^']*'", f"detail:'{s_gdet}'", new_obj, count=1)
            if s_dkey:
                new_obj = re.sub(r"detailKey:'[^']*'", f"detailKey:'{s_dkey}'", new_obj, count=1)
        else:
            d_key_str = f",detailKey:'{s_dkey}'" if s_dkey else ""
            grade_chunk = f"    grade:{{score:'{s_gscore or '10 / 10'}',detail:'{s_gdet}'{d_key_str}}},\n"
            new_obj = re.sub(r"(teachers:\[[^\]]*\],\n)", r"\1" + grade_chunk, new_obj)

    # 2. Correo asociado a la asignatura
    if mail_key and f"'{mail_key}'" not in new_obj:
        s_mkey = sanitize_js_string(mail_key)
        if "mails:[" in new_obj:
            new_obj = new_obj.replace("mails:[", f"mails:['{s_mkey}',", 1)
        elif "mails: [" in new_obj:
            new_obj = new_obj.replace("mails: [", f"mails: ['{s_mkey}',", 1)

    # 3. Práctica o nota en notes: [ ... ]
    if practice_entry:
        p_name = sanitize_js_string(practice_entry.get("name", ""))
        p_dkey = sanitize_js_string(practice_entry.get("detailKey", ""))
        p_url = practice_entry.get("url", "cprocTareasUrl")
        p_lbl = sanitize_js_string(practice_entry.get("label", "Ver práctica ↗"))
        if f"'{p_name}'" not in new_obj:
            p_chunk = f"\n     {{name:'{p_name}',detailKey:'{p_dkey}',url:{p_url},label:'{p_lbl}'}},"
            if "notes:[" in new_obj:
                new_obj = new_obj.replace("notes:[", f"notes:[{p_chunk}", 1)
            elif "notes: [" in new_obj:
                new_obj = new_obj.replace("notes: [", f"notes: [{p_chunk}", 1)

    new_c_block = c_block[:start_obj] + new_obj + c_block[end_obj:]
    return content[:c_match.start(2)] + new_c_block + content[c_match.end(2):]

def add_mail_entry(content: str, date_str: str, title: str, meta: str, key: str, 
                   teacher: str, subject_ref: str, summary: str, body: str, source: str) -> str:
    """Inserta un nuevo correo en messages, mailSummaries y details en index.html,
    y propaga la referencia a la ficha del profesor y de la asignatura."""
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

    # 4. Propagación automática al Profesor (teacherDirectory)
    if s_teacher:
        content = update_teacher_directory(
            content,
            teacher_name=s_teacher,
            mail_item={"title": s_title, "key": s_key}
        )

    # 5. Propagación automática a la Asignatura (courses)
    content = update_course_subject(
        content,
        teacher_name=s_teacher,
        mail_key=s_key
    )

    return content

def add_ceproc_task(content: str, date_str: str, title: str, teacher: str, subject: str,
                    subject_ref: str, status: str, deadline_str: str, details_text: str) -> str:
    """Inserta una nueva práctica/tarea de CEPROC en deliveries y details,
    y la vincula automáticamente con la ficha del profesor y la asignatura correspondiente."""
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

    # Propagación automática a la ficha del profesor en teacherDirectory
    if s_teacher:
        content = update_teacher_directory(
            content,
            teacher_name=s_teacher,
            practice_item={"title": s_title, "status": s_status, "key": detail_key}
        )

    # Propagación automática a la asignatura en courses
    content = update_course_subject(
        content,
        subject_name=s_subject,
        teacher_name=s_teacher,
        practice_entry={"name": f"Práctica CPROC: {s_title}", "detailKey": detail_key}
    )

    return content

def mark_delivery_completed(content: str, search_query: str) -> tuple:
    """Busca una entrega por término clave (título o docente) y la marca como completada,
    actualizando también su estado en la ficha del profesor."""
    m = re.search(r'(const deliveries=\[\s*)(.*?)(\s*\];)', content, re.DOTALL)
    if not m:
        return content, False

    deliveries_block = m.group(2)
    lines = deliveries_block.splitlines(True)
    found = False
    new_lines = []
    sq_lower = search_query.strip().lower()
    matched_title = ""
    matched_teacher = ""

    for line in lines:
        if not found and sq_lower in line.lower() and 'submitted:false' in line:
            line = re.sub(r"status:'[^']+'", "status:'Completada y enviada ✓'", line)
            line = line.replace('submitted:false', 'submitted:true')
            found = True
            t_match = re.search(r"title:'([^']+)'", line)
            if t_match:
                matched_title = t_match.group(1)
            te_match = re.search(r"teacher:'([^']+)'", line)
            if te_match:
                matched_teacher = te_match.group(1)
        new_lines.append(line)

    if found:
        new_block = m.group(1) + "".join(new_lines) + m.group(3)
        content = content[:m.start()] + new_block + content[m.end():]

        # Sincronizar estado en teacherDirectory si se conoce el profesor
        if matched_teacher:
            content = update_teacher_directory(
                content,
                teacher_name=matched_teacher,
                practice_item={"title": matched_title or search_query, "status": "Completada y enviada ✓", "key": ""}
            )

        return content, True

    return content, False

def add_grade_entry(content: str, grade_id: str, title: str, kicker: str, score: str, score_label: str,
                    teacher: str, subject_ref: str, mail_key: str, description: str, breakdown: list,
                    subject_name: str = None) -> str:
    """Inserta una calificación oficial en gradeRecords, actualiza teacherGradeMap, 
    y propaga la nota completa tanto a la ficha del profesor (teacherDirectory) como a la asignatura (courses)."""
    s_id = re.sub(r'[^a-zA-Z0-9_]', '_', grade_id.strip().lower())
    s_title = sanitize_js_string(title)
    s_kicker = sanitize_js_string(kicker)
    s_score = sanitize_js_string(score)
    s_score_label = sanitize_js_string(score_label or "Nota docente")
    s_teacher = sanitize_js_string(teacher)
    s_subref = sanitize_js_string(subject_ref)
    s_mail_key = sanitize_js_string(mail_key)
    s_desc = sanitize_js_string(description)

    breakdown_js = ",\n   ".join([
        f"{{label:'{sanitize_js_string(b.get('label', ''))}',val:'{sanitize_js_string(b.get('val', ''))}'}}"
        for b in breakdown
    ]) if breakdown else f"{{label:'Calificación otorgada',val:'{s_score}'}}"

    grade_entry = f""" {{
  id:'{s_id}',
  type:'mail',
  kicker:'{s_kicker}',
  title:'{s_title}',
  score:'{s_score}',
  scoreLabel:'{s_score_label}',
  breakdown:[
   {breakdown_js}
  ],
  teacher:'{s_teacher}',
  subjectRef:'{s_subref}',
  mailKey:'{s_mail_key}',
  description:'{s_desc}',
  links:[
   {{label:'✉ Abrir correo de la nota ↗',detailKey:'{s_mail_key}',cls:'solid-green'}},
   {{label:'Ver asignatura ↗',subjectRef:'{s_subref}'}},
   {{label:'Ficha de {s_teacher} ↗',teacher:'{s_teacher}'}},
   {{label:'Abrir correo en Outlook ↗',url:outlookUrl,cls:'blue'}}
  ]
 }},
"""
    # 1. Insertar en const gradeRecords=[
    if "const gradeRecords=[" in content:
        content = content.replace("const gradeRecords=[\n", "const gradeRecords=[\n" + grade_entry, 1)

    # 2. Actualizar teacherGradeMap
    if s_teacher and "const teacherGradeMap={" in content:
        grade_badge_text = f"{s_score} ★"
        if f"'{s_teacher}'" in content:
            content = re.sub(rf"'{re.escape(s_teacher)}':\s*'[^']*'", f"'{s_teacher}':'{grade_badge_text}'", content)
        else:
            content = content.replace("const teacherGradeMap={\n", f"const teacherGradeMap={{\n '{s_teacher}':'{grade_badge_text}',\n", 1)

    # 3. Propagación al expediente y ficha del docente en teacherDirectory
    if s_teacher:
        badge_txt = f"⭐ {s_score} (Oficial) ✓"
        detail_txt = s_desc or f"Calificación oficial registrada: {s_score}."
        content = update_teacher_directory(
            content,
            teacher_name=s_teacher,
            grade_score=s_score,
            grade_badge=badge_txt,
            grade_detail=detail_txt,
            mail_item={"title": s_title, "key": s_mail_key},
            practice_item={"title": s_title, "status": f"{s_score} ✓", "key": s_mail_key},
            detail_key=s_mail_key
        )

    # 4. Propagación a la asignatura correspondiente en courses
    content = update_course_subject(
        content,
        subject_name=subject_name,
        teacher_name=s_teacher,
        grade_score=f"Nota oficial: {s_score} ★",
        grade_detail=s_desc or f"Calificación oficial comunicada por correo: {s_score}.",
        detail_key=s_mail_key,
        mail_key=s_mail_key
    )

    return content

def save_and_commit(new_content: str, commit_msg: str) -> bool:
    """Guarda los cambios localmente o a través de la API de GitHub."""
    # 1. Modo Local si el archivo existe
    if INDEX_HTML.exists():
        with open(INDEX_HTML, "w", encoding="utf-8") as f:
            f.write(new_content)
        try:
            # Regenerar portal de estudiantes para mantenerlo sincronizado
            gen_script = PORTAL_DIR / "generar_portal_estudiantes.py"
            if gen_script.exists():
                try:
                    subprocess.run([sys.executable, str(gen_script)], check=True)
                    subprocess.run(["git", "-C", str(PORTAL_DIR), "add", "portal-estudiantes.html", "estudiantes.html"], check=True)
                except Exception as eg:
                    print(f"[Updater] Aviso al regenerar portal-estudiantes.html: {eg}")

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

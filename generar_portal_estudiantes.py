#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_portal_estudiantes.py
Genera portal-estudiantes.html y estudiantes.html a partir de index.html:
1. Paleta solemne, austera e institucional ("Modo Derecho / Toga y Estrado Judicial").
2. Filtro 100% estricto de eventos personales, citas médicas y notas fijas de Raquel.
3. Desvinculación de Google Drive y Google Docs: sin enlaces privados inaccesibles.
4. Entregas limpias con inicio a cero (ninguna pre-marcada) y casillas de verificación interactivas con guardado en localStorage.
5. Calificaciones: cuaderno de evaluación interactivo del estudiante con casilla para nota del test, nota final del profesor y anotaciones en localStorage.
6. Filtro del buzón de correo: se excluyen los correos de calificaciones personales y se conservan íntegros todos los comunicados docentes, calendarios y materiales.
7. Horario oficial de clases: turno de tarde de 16:30 a 20:45 h.
"""

import re
import os
import sys

def generate_student_portal_html(html: str) -> str:
    """Transforma el HTML del portal personal de Raquel en el Portal del Estudiante neutral y colaborativo."""
    # -------------------------------------------------------------
    # 1. TÍTULO, METADATOS, FAVICON Y CABECERA DE MARCA
    # -------------------------------------------------------------
    html = re.sub(
        r'<title>.*?</title>',
        '<title>🎓 Portal del Estudiante · MUAP</title>',
        html,
        count=1
    )
    html = html.replace('<meta name="apple-mobile-web-app-title" content="Mi Portal · Raquel">', '<meta name="apple-mobile-web-app-title" content="Portal Estudiantes">')
    html = html.replace('<meta name="apple-mobile-web-app-title" content="Máster Abogacía">', '<meta name="apple-mobile-web-app-title" content="Portal Estudiantes">')
    html = html.replace('<meta name="application-name" content="Mi Portal · Raquel">', '<meta name="application-name" content="Portal Estudiantes">')
    html = html.replace('<meta name="application-name" content="Máster Abogacía">', '<meta name="application-name" content="Portal Estudiantes">')

    # Desvinculación de favicon / icono para que sea 100% propio del estudiante (Birrete en Oxford Navy)
    favicon_original = """<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="favicon-16x16.png">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<link rel="manifest" href="manifest.webmanifest">"""

    favicon_replacement = """<link rel="apple-touch-icon" href="favicon-estudiantes.svg">
<link rel="icon" type="image/svg+xml" href="favicon-estudiantes.svg">
<link rel="alternate icon" href="favicon-estudiantes.svg">
<link rel="manifest" href="manifest-estudiantes.webmanifest">"""

    html = html.replace(favicon_original, favicon_replacement)

    # Identidad del portal (Logo e icono del menú lateral)
    html = html.replace('<div class="brand-icon" title="Mi Portal">⚖️</div>', '<div class="brand-icon" title="Portal del Estudiante">🎓</div>')
    html = html.replace('<div class="brand-icon">⚖️</div>', '<div class="brand-icon" title="Portal del Estudiante">🎓</div>')
    html = html.replace('<div class="brand-name">Mi Portal</div>', '<div class="brand-name">Portal Estudiantes</div>')
    html = html.replace('<div class="brand-name">Cuaderno</div>', '<div class="brand-name">Portal Estudiantes</div>')
    html = html.replace('<div class="brand-user-pill">Raquel Escudero · 2026/27</div>', '<div class="brand-user-pill">🎓 Estudiante · MUAP 2026/27</div>')
    html = html.replace('<div class="avatar" title="Raquel Escudero">RE</div>', '<div class="avatar" title="Portal del Estudiante">🎓</div>')
    html = html.replace('<div class="avatar" title="Máster en Abogacía y Procura">⚖️</div>', '<div class="avatar" title="Portal del Estudiante">🎓</div>')
    html = html.replace('<h1 id="welcomeTitle">Hola, Raquel</h1>', '<h1 id="welcomeTitle">Portal del Estudiante · MUAP</h1>')
    html = html.replace(
        '<p id="welcomeSubtitle">Cuaderno personal de estudio, agenda y seguimiento académico del Máster en Abogacía y Procura.</p>',
        '<p id="welcomeSubtitle">Seguimiento académico, agenda oficial, profesorado, entregas y notas del Máster Universitario en Abogacía y Procura (2026–2027).</p>'
    )

    # Badges de bienvenida
    badge_gold_original = """        <button class="welcome-badge badge-gold" data-switch-view="notas" title="Calificación oficial comunicada por correo">
          <span class="badge-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          </span>
          <div class="badge-texts">
            <span class="badge-label">Oficial por correo</span>
            <strong class="badge-value">10 / 10 · Sobresaliente</strong>
          </div>
        </button>"""
    badge_gold_replacement = """        <div class="welcome-badge badge-gold" title="Máster Universitario en Abogacía y Procura">
          <span class="badge-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          </span>
          <div class="badge-texts">
            <span class="badge-label">Máster oficial</span>
            <strong class="badge-value">1.er Cuatrimestre · 26/27</strong>
          </div>
        </div>"""
    if badge_gold_original in html:
        html = html.replace(badge_gold_original, badge_gold_replacement)

    badge_mint_original = """        <button class="welcome-badge badge-mint" data-switch-view="notas" title="Test de evaluación continua en Testmoz">
          <span class="badge-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
          </span>
          <div class="badge-texts">
            <span class="badge-label">Testmoz 16 oct</span>
            <strong class="badge-value">20 / 20 (100% aciertos)</strong>
          </div>
        </button>"""
    badge_mint_replacement = """        <button class="welcome-badge badge-mint" data-switch-view="notas" title="Mis notas y cuaderno personal de evaluación">
          <span class="badge-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
          </span>
          <div class="badge-texts">
            <span class="badge-label">Evaluación continua</span>
            <strong class="badge-value" id="welcomeGradesSummary">Mi Cuaderno de Notas</strong>
          </div>
        </button>"""
    if badge_mint_original in html:
        html = html.replace(badge_mint_original, badge_mint_replacement)

    # -------------------------------------------------------------
    # 2. FILTRAR EVENTOS PERSONALES EN events = { ... }
    # -------------------------------------------------------------
    m_events = re.search(r'(const events=\{)(.*?)(\n\};\n\nconst gradeRecords=)', html, re.DOTALL)
    if m_events:
        events_code = m_events.group(2)
        days = re.findall(r"('(\d{4}-\d{2}-\d{2})':\s*\[)(.*?)(\])(?=,\s*'\d{4}-\d{2}-\d{2}'|\s*$)", events_code, re.DOTALL)
        new_events_lines = []
        for prefix, day_str, evs_content, suffix in days:
            ev_objects = re.findall(r'(\{[^{}]*?\})', evs_content, re.DOTALL)
            clean_evs = []
            for ev in ev_objects:
                if 'isPersonal:true' in ev or 'isPersonal: true' in ev:
                    continue
                if 'ENTREGADA:' in ev or 'personal_calendar_sync' in ev or 'Pilates' in ev or 'Ortodix' in ev:
                    continue
                clean_evs.append(ev)
            if clean_evs:
                new_events_lines.append(f" '{day_str}':[\n   " + ",\n   ".join(clean_evs) + "\n  ]")
            else:
                new_events_lines.append(f" '{day_str}':[]")
        cleaned_events_code = ",\n".join(new_events_lines)
        html = html[:m_events.start(2)] + cleaned_events_code + html[m_events.end(2):]
        print("✓ Eventos personales filtrados.")

    # -------------------------------------------------------------
    # 3. FILTRAR MENSAJES (CORREO) - EXCLUIR NOTAS PERSONALES
    # -------------------------------------------------------------
    m_msg = re.search(r'(const messages\s*=\s*\[)(.*?)(\];\s*const)', html, re.DOTALL)
    if m_msg:
        excluded_keys = {
            'mail_carolina_carlos_23oct',
            'mail_carlos_sanchez_2oct',
            'test_20oct_sandra',
            'mail_deontologia_ana_vazquez',
            'procura_resultados',
            'grades'
        }
        raw_items = m_msg.group(2)
        clean_msgs = []
        for item in re.finditer(r'\{[^{}]*?\}', raw_items):
            item_str = item.group(0)
            skip = False
            for k in excluded_keys:
                if f"key:'{k}'" in item_str or f'key:"{k}"' in item_str:
                    skip = True
                    break
            if "key:'mail_nota_" in item_str or 'key:"mail_nota_' in item_str:
                skip = True
            if any(term in item_str for term in ['Nota:', 'Calificaciones oficiales', 'Resultados de las pruebas', 'Test online realizado', 'Calificación oficial']):
                skip = True
            if not skip:
                # Limpiar referencias a Drive en el meta
                item_str = item_str.replace(' · subido a Drive y enviado en CPROC', ' · Caso práctico en CPROC')
                clean_msgs.append(item_str)
        
        new_messages_code = "\n " + ",\n ".join(clean_msgs) + "\n"
        html = html[:m_msg.start(2)] + new_messages_code + html[m_msg.end(2):]
        
        # Actualizar badge en pestaña Correo
        html = re.sub(
            r'<button class="view-tab" data-view="correo" role="tab"[^>]*>Correo <span class="tab-badge">\d+</span></button>',
            f'<button class="view-tab" data-view="correo" role="tab" aria-selected="false">Correo <span class="tab-badge">{len(clean_msgs)}</span></button>',
            html
        )
        print(f"✓ Buzón de correo filtrado: {len(clean_msgs)} comunicados académicos oficiales conservados (excluidas notas personales).")

    # -------------------------------------------------------------
    # 4. LIMPIAR OBJETO DETAILS (CITAS MÉDICAS Y ARCHIVOS PRIVADOS)
    # -------------------------------------------------------------
    idx_sync = html.find(' personal_calendar_sync:{')
    idx_grades = html.find(' grades:{', idx_sync if idx_sync != -1 else 0)
    if idx_sync != -1 and idx_grades != -1:
        html = html[:idx_sync] + html[idx_grades+1:]
        print("✓ Objeto personal_calendar_sync eliminado de details.")

    html = html.replace('remitidas oficialmente a Raquel el 19 de octubre', 'remitidas oficialmente al estudiantado el 19 de octubre')
    html = html.replace('Administración del Máster confirma a Raquel la facilitación de justificante oficial', 'Administración del Máster informa sobre justificante oficial')
    html = html.replace('Este justificante permite acreditar la asistencia oficial al evento tras acudir a la cita médica en HM Modelo a las 09:30 h.', 'Este justificante permite acreditar la asistencia oficial al evento ante cualquier trámite o justificación.')
    html = html.replace('La Administración del Máster (master.abogacia@icacor.org) confirma formalmente a Raquel que la asistencia al DATAfórum el viernes 23 de octubre contará con justificante oficial', 'La Administración del Máster informa que la asistencia al DATAfórum el viernes 23 de octubre contará con justificante oficial')
    html = html.replace('DATAFORUM_2026_Itinerario_Personalizado_Raquel_Escudero.pdf', 'https://www.justicia2030.es/dataforum')
    html = html.replace('Itinerario personalizado DATAfórum (PDF elaborado)', 'Programa oficial DATAfórum Justicia 2026')
    html = html.replace('2026-10-22-resolucion-caso-practico-sandra-mosteiro-raquel-escudero.md', '')
    html = html.replace('2026-10-22-grabacion-entrega-caso-practico-sandra-mosteiro.mov', '')

    # -------------------------------------------------------------
    # 5. DESVINCULACIÓN TOTAL DE GOOGLE DRIVE Y GOOGLE DOCS
    # -------------------------------------------------------------
    # Menú lateral inferior (Primer cuatrimestre): solo Bandeja de Outlook y Plataforma CPROC para estudiantes
    html = re.sub(
        r'\s*<a class="side-drive-link"[^>]*>📁 Carpeta Máster en Drive ↗</a>',
        '',
        html
    )
    html = re.sub(
        r'\s*<a class="side-drive-link" href="historial-tests/[^"]*"[^>]*>.*?</a>',
        '',
        html
    )

    # Reemplazo de variables de URL
    html = re.sub(
        r"const driveFolderUrl='[^']*';",
        "const driveFolderUrl='https://www.icpcoruna.com/copia-de-entrega-de-tareas';",
        html
    )
    html = re.sub(
        r"const practicasGdriveUrl='[^']*';",
        "const practicasGdriveUrl='https://www.icpcoruna.com/copia-de-entrega-de-tareas';",
        html
    )
    html = re.sub(
        r"function driveSearchUrl\(q\)\{return 'https://drive\.google\.com/[^']*';\}",
        "function driveSearchUrl(q){return 'https://www.icpcoruna.com/copia-de-entrega-de-tareas';}",
        html
    )
    
    # Reemplazar enlaces específicos a Google Docs y Google Drive por CPROC o BOE
    html = re.sub(r"https://drive\.google\.com/file/d/[a-zA-Z0-9_\-]+/view", "https://www.icpcoruna.com/copia-de-entrega-de-tareas", html)
    html = re.sub(r"https://drive\.google\.com/drive/u/0/folders/[a-zA-Z0-9_\-]+", "https://www.icpcoruna.com/copia-de-entrega-de-tareas", html)
    html = re.sub(r"https://docs\.google\.com/document/d/[a-zA-Z0-9_\-]+/edit(?:\?[^\s\'\"]*)?", "https://www.icpcoruna.com/copia-de-entrega-de-tareas", html)

    # Textos de botones y títulos
    html = html.replace('Raquel Escudero_Derechos y deberes procuradores y responsabilidad profesional (Doc Google)', 'Caso práctico: Derechos, deberes y responsabilidad profesional (CPROC)')
    html = html.replace('2/10_Práctica_Raquel Escudero .pdf (Práctica en Drive)', 'Práctica 2 de octubre (CPROC)')
    html = html.replace('2/10_Práctica_Raquel Escudero .pdf', 'Práctica 2 de octubre')
    html = html.replace('Raquel Escudero_Derechos y deberes procuradores (Doc Google)', 'Caso práctico de Deontología (CPROC)')
    html = html.replace('RESOLUCIÓN ÍNTEGRA DEL CASO PRÁCTICO — SANDRA MOSTEIRO COSTA\\nEstudiante: Raquel Escudero Valcárcel-Ríos', 'RESOLUCIÓN ÍNTEGRA DEL CASO PRÁCTICO — SANDRA MOSTEIRO COSTA\\nCaso práctico oficial evaluable')
    html = html.replace('Abrir en Drive ↗', 'Plataforma CPROC ↗')
    html = html.replace('PDF Drive ↗', 'Documento oficial ↗')
    html = html.replace('Carpeta Drive ↗', 'CPROC Tareas ↗')
    html = html.replace('Buscar en Drive ↗', 'Normativa y CPROC ↗')
    html = html.replace('Google Docs ↗', 'CPROC ↗')
    html = html.replace('Borrador en Drive ↗', 'Plataforma CPROC ↗')
    html = html.replace('Google Docs (Entrega) ↗', 'Enunciado oficial ↗')
    html = html.replace('Vídeo comprobante CPROC ↗', 'Plataforma CPROC ↗')
    html = html.replace('Resolución completa (.md) ↗', 'Instrucciones del caso ↗')
    html = html.replace('Carpeta Prácticas Drive ↗', 'CPROC Tareas ↗')
    html = html.replace('Apuntes y Drive', 'Materiales y Normativa')

    # Reemplazo en barra superior y accesos directos
    html = html.replace(
        '<a href="https://drive.google.com/drive/u/0/folders/1CWnIhmWiTwz061yWbBatcx7Fd2PEwVcQ" target="_blank" rel="noopener noreferrer">Drive ↗</a>',
        '<a href="https://www.icpcoruna.com/copia-de-entrega-de-tareas" target="_blank" rel="noopener noreferrer">CPROC Tareas ↗</a>'
    )
    html = html.replace(
        '<a href="portal-estudiantes.html" target="_blank" rel="noopener noreferrer" style="background:var(--blue-pale);border-color:var(--blue-border);color:var(--blue-dark);font-weight:700">🎓 Portal Estudiantes ↗</a>',
        '<span class="portal-mode-pill">🎓 Portal del Estudiante · Versión Oficial</span>'
    )
    html = html.replace(
        '<a class="home-hub-card hub-blue" href="https://drive.google.com/drive/u/0/folders/1CWnIhmWiTwz061yWbBatcx7Fd2PEwVcQ" target="_blank" rel="noopener noreferrer">',
        '<a class="home-hub-card hub-blue" href="https://www.icpcoruna.com/copia-de-entrega-de-tareas" target="_blank" rel="noopener noreferrer">'
    )
    html = html.replace(
        '<a class="drive-btn" href="https://drive.google.com/drive/u/0/folders/1CWnIhmWiTwz061yWbBatcx7Fd2PEwVcQ" target="_blank" rel="noopener noreferrer">Abrir Carpeta Google Drive ↗</a>',
        '<a class="drive-btn" href="https://www.icpcoruna.com/copia-de-entrega-de-tareas" target="_blank" rel="noopener noreferrer">Acceder a CPROC Tareas ↗</a>'
    )
    print("✓ Enlaces privados a Google Drive y Docs desvinculados por completo.")

    # -------------------------------------------------------------
    # 6. LIMPIAR NOTAS FIJAS EN courses = [...], teacherDirectory Y gradeRecords
    # -------------------------------------------------------------
    # Reemplazar calificaciones fijas en asignaturas por evaluación continua
    html = re.sub(
        r"grade:\{score:'[^']*(?:Sobresaliente|Notable|aciertos|★|Oficial|\d+\s*/\s*10)[^']*',scoreLabel:'[^']*',detail:'[^']*',detailKey:'[^']*'\}",
        "grade:{score:'Evaluación continua',scoreLabel:'Evaluación del módulo',detail:'Ponderación oficial: 40% Cuestionario tipo test + 60% Trabajos y casos prácticos.',detailKey:'dossiers'}",
        html
    )
    # Neutralizar insignias y notas individuales en teacherDirectory
    html = re.sub(r"gradeBadge:\s*'[^']*(?:★|Oficial|Sobresaliente|Notable|\d+\s*/\s*10)[^']*'", "gradeBadge:'⚖️ Evaluación continua'", html)
    html = re.sub(r"gradeScore:\s*'[^']*(?:Sobresaliente|Notable|\d+\s*/\s*10)[^']*'", "gradeScore:'Evaluación continua'", html)
    html = re.sub(r"gradeDetail:\s*'Calificación oficial registrada:[^']*'", "gradeDetail:'Ponderación oficial de evaluación continua (test + trabajos de CPROC).'", html)
    html = re.sub(r" · Calificación oficial:\s*[^'\"<]+", "", html)
    html = re.sub(r" · Test:\s*[^'\"<]+", "", html)
    html = html.replace(' · Práctica entregada en CPROC', '')

    # Neutralizar gradeRecords: excluir notas personales numéricas comunicadas por correo manteniendo cuestionarios didácticos
    m_gr = re.search(r'(const gradeRecords\s*=\s*\[)(.*?)(\];\s*const)', html, re.DOTALL)
    if m_gr:
        raw_gr = m_gr.group(2)
        clean_gr = []
        for item in re.finditer(r'\{[^{}]*?\}', raw_gr):
            item_str = item.group(0)
            if 'grade_16oct_test' in item_str or 'grade_20oct_test' in item_str:
                item_str = re.sub(r"score:'[^']*'", "score:'Cuestionario oficial'", item_str)
                item_str = re.sub(r"scoreLabel:'[^']*'", "scoreLabel:'Preguntas y soluciones'", item_str)
                clean_gr.append(item_str)
        html = html[:m_gr.start(2)] + "\n " + ",\n ".join(clean_gr) + "\n" + html[m_gr.end(2):]

    print("✓ Notas fijas de asignaturas y expedientes convertidas en evaluación continua neutral.")

    # -------------------------------------------------------------
    # 7. ENTREGAS: INICIO A CERO Y CHECKBOXES INTERACTIVOS
    # -------------------------------------------------------------
    m_del = re.search(r'(const deliveries\s*=\s*\[)(.*?)(\];\s*const)', html, re.DOTALL)
    if m_del:
        del_content = m_del.group(2)
        # 1) Excluir el registro de notas de Carolina y Carlos
        del_content = re.sub(
            r'\{\s*date:new Date\(2026,9,23\),\s*title:\'Resultados de pruebas y trabajos[^\}]*?\},?',
            '',
            del_content
        )
        # 2) Todas las entregas inician como no entregadas (submitted: false)
        del_content = del_content.replace('submitted:true', 'submitted:false')
        del_content = del_content.replace('submitted: true', 'submitted: false')
        # 3) Limpiar campos de archivos privados
        del_content = re.sub(r"file2:'2026-10-22-grabacion-entrega-caso-practico-sandra-mosteiro\.mov',?", "", del_content)
        del_content = re.sub(r"file2:'summary\.docx',?", "", del_content)
        # 4) Limpiar estados de Raquel
        del_content = re.sub(r"status:'Entregada con éxito en CPROC ✓[^\']*'", "status:'⏳ Pendiente de marcar'", del_content)
        del_content = re.sub(r"status:'⏳ Pendiente \(Plazo:[^\']*'\)", "status:'⏳ Pendiente de marcar'", del_content)
        # 5) Limpieza rigurosa de textos de entregas (sin estados ni fechas de entrega personales)
        del_content = re.sub(
            r"details:'Caso práctico oficial evaluable entregado con éxito en CPROC[^']*'",
            "details:'Caso práctico oficial evaluable sobre actos de comunicación judicial (citaciones, emplazamientos, LexNET y doctrina jurisprudencial de los 6 supuestos de la LEC). Enunciado en CASO_PRACTICO_2026_SANDRA.pdf para entrega en CPROC.'",
            del_content
        )
        del_content = re.sub(
            r"details:'Certificado de inscripción de apoderamiento apud acta a favor de Carolina Moreno Vázquez[^']*'",
            "details:'Certificado electrónico de apoderamiento apud acta en el REAJ a favor de la docente. Tarea evaluable de tramitación procesal telemática para entrega en plataforma CPROC.'",
            del_content
        )
        del_content = re.sub(
            r"details:'Tarea en CPROC: «ESCRITO SUBSANACIÓN»[^']*'",
            "details:'Redacción y firma de escrito procesal solicitando tener por subsanada la representación procesal mediante poder apud acta. Entrega en plataforma CPROC.'",
            del_content
        )
        del_content = re.sub(
            r"details:'1\.º envío: Documento_anonimizado\.pdf[^']*'",
            "details:'Estudio del auto de concurso y elaboración de resumen procesal ejecutivo con oferta de venta de unidad productiva (UP). Entrega en plataforma CPROC.'",
            del_content
        )
        del_content = re.sub(
            r"details:'Plataforma oficial CPROC \(MUAP\)[^']*'",
            "details:'Caso práctico evaluable sobre derechos, deberes y responsabilidad profesional del procurador, estatuto orgánico y código deontológico. Entrega en CPROC.'",
            del_content
        )
        del_content = del_content.replace(' en Google Drive y Markdown local.', '.')
        del_content = del_content.replace('Subida a Google Drive y enviada en CPROC', 'Plataforma oficial CPROC (MUAP)')
        del_content = del_content.replace('Subida a Drive y enviada en CPROC', 'Plataforma oficial CPROC (MUAP)')
        del_content = del_content.replace('Subidos a Google Drive y enviados con éxito en CPROC.', 'Plataforma oficial CPROC (MUAP).')
        del_content = del_content.replace('Práctica subida a Google Drive y enviada dentro de plazo en CPROC', 'Plataforma oficial CPROC (MUAP)')

        html = html[:m_del.start(2)] + del_content + html[m_del.end(2):]
        print("✓ Colección de entregas reajustada con inicio limpio a cero y descripciones neutrales.")

    # -------------------------------------------------------------
    # 7b. LIMPIAR DETAILS DE ENTREGAS Y DESACOPLAR INTERFAZ
    # -------------------------------------------------------------
    html = re.sub(
        r"kicker:'Práctica entregada con éxito en CPROC ✓ · 22 de octubre de 2026',",
        "kicker:'Caso práctico evaluable · Procura · Actos de comunicación judicial',",
        html
    )
    html = re.sub(
        r"date:'Entregada: jueves, 22 de octubre de 2026 \(12:51 h\) · Estado: Completada y enviada en CPROC \(«✓ La Tarea se ha entregado con éxito»\)',",
        "date:'Sesiones: 19 y 20 de octubre de 2026 · Entrega a través de plataforma CPROC',",
        html
    )
    html = re.sub(
        r"date:'Entregado: viernes, 16 de octubre de 2026 · Estado: Completada en Drive y enviada en CPROC ✓',",
        "date:'Sesión: 16 de octubre de 2026 · Entrega a través de plataforma CPROC',",
        html
    )
    html = re.sub(
        r"date:'Entregado: viernes, 16 de octubre de 2026 · 2 envíos realizados · Estado: Completada en Drive y enviada en CPROC ✓',",
        "date:'Sesión: 16 de octubre de 2026 · Entrega a través de plataforma CPROC',",
        html
    )
    html = re.sub(
        r"kicker:'Práctica entregada · Procura · Técnicas instrumentales / Actuación procesal',",
        "kicker:'Práctica procesal de aula · Procura · Técnicas instrumentales',",
        html
    )
    html = re.sub(
        r"kicker:'Práctica entregada \(2 envíos\) · Procura · Técnicas instrumentales / Actuación procesal',",
        "kicker:'Práctica procesal de aula · Procura · Técnicas instrumentales',",
        html
    )
    html = re.sub(
        r"kicker:'Práctica entregada y apuntes · Procura · Deontología y responsabilidad',",
        "kicker:'Caso práctico evaluable · Procura · Deontología y responsabilidad',",
        html
    )
    html = re.sub(
        r"date:'Estado: Completada en Google Drive y enviada en CPROC ✓ \(Plazo del correo: 15 de octubre de 2026\)',",
        "date:'Sesiones: 8 y 9 de octubre de 2026 · Entrega a través de plataforma CPROC',",
        html
    )
    html = re.sub(
        r"extra:'✓ Entrega confirmada en CPROC[^\']*'",
        "extra:'Entrega telemática a través del aula virtual de tareas CPROC.'",
        html
    )
    html = re.sub(
        r"extra:'✓ Entregada con justificante de éxito en CPROC[^\']*'",
        "extra:'Entrega telemática a través del aula virtual de tareas CPROC.'",
        html
    )
    html = re.sub(
        r"extra:'✓ Ambos archivos están entregados en CPROC[^\']*'",
        "extra:'Entrega telemática a través del aula virtual de tareas CPROC.'",
        html
    )
    html = html.replace('Estudiante: Raquel Escudero Valcárcel-Ríos · Entregada en CPROC el 22/10/2026 a las 12:51 h', 'Caso práctico oficial evaluable (6 escenarios de la LEC + 3 reflexiones)')
    html = html.replace('Plataforma CPROC (MUAP) → Tareas publicadas · Entrega realizada el 22/10/2026 (12:51 h) con resguardo en pantalla «✓ La Tarea se ha entregado con éxito»', 'Plataforma CPROC (MUAP) → Tareas publicadas · Entrega oficial a través de la plataforma CPROC')
    html = html.replace('Resolución jurídica completa elaborada por Raquel Escudero Valcárcel-Ríos para la materia de Sandra Mosteiro Costa.', 'Resolución de supuestos prácticos procesales para la materia de Sandra Mosteiro Costa.')
    html = html.replace("state:'Entregada en CPROC ✓ (22/10/2026, 12:51 h)'", "state:'Entrega telemática en CPROC'")
    html = html.replace("Confirmación: «La Tarea se ha entregado con éxito» · 16 oct 2026", "Entrega telemática a través de la plataforma CPROC")
    html = html.replace("state:'Entregado en CPROC ✓ · «La Tarea se ha entregado con éxito»'", "state:'Entrega telemática en CPROC'")
    html = html.replace('Repositorio privado con tus apuntes, guías, casos prácticos y entregas', 'Repositorio académico con guías, casos prácticos y materiales de estudio')

    # Sidebar: botón de entregas con ID dinámico
    html = html.replace(
        '<span class="nav-label-text">Próximas entregas</span>\\n      <span class="nav-badge-pill badge-terra highlight-pill" style="font-weight:800;padding:2px 7px">⏳ 2 pend.</span>',
        '<span class="nav-label-text">Próximas entregas</span>\\n      <span class="nav-badge-pill badge-terra highlight-pill" id="sideNavDeliveriesBadge" style="font-weight:800;padding:2px 7px">⏳ Entregas</span>'
    )
    html = html.replace(
        '<span class="nav-label-text">Próximas entregas</span>\n      <span class="nav-badge-pill badge-terra highlight-pill" style="font-weight:800;padding:2px 7px">⏳ 2 pend.</span>',
        '<span class="nav-label-text">Próximas entregas</span>\n      <span class="nav-badge-pill badge-terra highlight-pill" id="sideNavDeliveriesBadge" style="font-weight:800;padding:2px 7px">⏳ Entregas</span>'
    )

    # Sidebar: acordeón de prácticas pendientes con ID dinámico
    old_side_pending_accordion = """  <details class="sidebar-pending-details" id="sidebarPendingAccordion" open>
    <summary class="side-pending-summary">
      <div style="display:flex;align-items:center;gap:7px">
        <span class="spa-icon">⏳</span>
        <span class="spa-text">Prácticas pendientes</span>
      </div>
      <span class="nav-badge-pill badge-terra highlight-pill" style="font-size:10px;padding:2px 7px">2 pendientes</span>
      <span class="sta-arrow">▾</span>
    </summary>
    <div class="sidebar-pending-breakdown">
      <div style="font-size:10.5px;color:var(--muted);padding:0 4px 6px;line-height:1.4">Accesos directos con fecha límite y plataforma de entrega:</div>
      <div class="side-pending-items">
        <button class="side-pending-item" data-detail="entrega_delgado_parte_a" title="Plazo: 29 de octubre de 2026 · ICACOR">
          <div class="spi-head">
            <span class="spi-dot amber">●</span>
            <strong class="spi-date">29 oct · En 7 días</strong>
            <span class="spi-platform blue">ICACOR</span>
          </div>
          <div class="spi-title">Parte A: Insostenibilidad y AJG</div>
          <div class="spi-teacher">D. José Luis Delgado Domínguez</div>
        </button>

        <button class="side-pending-item" data-detail="entrega_delgado_parte_b" title="Plazo: 30 de octubre de 2026 · ICACOR">
          <div class="spi-head">
            <span class="spi-dot amber">●</span>
            <strong class="spi-date">30 oct · En 8 días</strong>
            <span class="spi-platform blue">ICACOR</span>
          </div>
          <div class="spi-title">Parte B: Siniestro RC y Turno Oficio</div>
          <div class="spi-teacher">D. José Luis Delgado Domínguez</div>
        </button>
      </div>
    </div>
  </details>"""

    new_side_pending_accordion = """  <details class="sidebar-pending-details" id="sidebarPendingAccordion" open>
    <summary class="side-pending-summary">
      <div style="display:flex;align-items:center;gap:7px">
        <span class="spa-icon">⏳</span>
        <span class="spa-text">Prácticas pendientes</span>
      </div>
      <span class="nav-badge-pill badge-terra highlight-pill" id="sidebarPendingAccordionBadge" style="font-size:10px;padding:2px 7px">Pendientes</span>
      <span class="sta-arrow">▾</span>
    </summary>
    <div class="sidebar-pending-breakdown">
      <div style="font-size:10.5px;color:var(--muted);padding:0 4px 6px;line-height:1.4">Entregas pendientes según tu marcado personal:</div>
      <div class="side-pending-items" id="sidebarPendingItemsList">
      </div>
    </div>
  </details>"""
    if old_side_pending_accordion in html:
        html = html.replace(old_side_pending_accordion, new_side_pending_accordion)

    # Welcome badge de entregas
    html = html.replace(
        '<strong class="badge-value">2 por entregar · Próx: 29 oct</strong>',
        '<strong class="badge-value" id="welcomeDeliveriesSummary">Control de entregas</strong>'
    )

    # View tab badge de entregas
    html = html.replace(
        '<button class="view-tab" data-view="entregas" role="tab" aria-selected="false">Próximas entregas <span class="tab-badge" style="background:var(--terracotta);color:#ffffff;font-weight:800">2 pend.</span></button>',
        '<button class="view-tab" data-view="entregas" role="tab" aria-selected="false">Próximas entregas <span class="tab-badge" id="tabDeliveriesBadge" style="background:var(--terracotta);color:#ffffff;font-weight:800">Entregas</span></button>'
    )

    # Portada: Banner dinámico de prácticas pendientes
    m_ptb = re.search(r'(<!-- 3\. MÓDULO DESTACADO: TITULARES DE PRÁCTICAS Y ENTREGAS PENDIENTES -->\s*<div class="pending-tasks-banner" id="pendingTasksBanner">)(.*?)(</div>\s*</div>\s*</section>)', html, re.DOTALL)
    if m_ptb:
        new_ptb_body = """
      <div class="ptb-header">
        <div class="ptb-title-wrap">
          <div style="display:flex;align-items:center;gap:8px">
            <span class="ptb-badge alert" id="ptbBadgeEl">⚠️ PRÁCTICAS PENDIENTES</span>
            <span class="ptb-urgent-chip" id="ptbUrgentChipEl">📅 Seguimiento individual</span>
          </div>
          <h3 class="ptb-title">Titulares de Prácticas y Entregas</h3>
          <p class="ptb-subtitle">Marca las prácticas que vayas entregando para llevar tu control personal de plazos al día.</p>
        </div>
        <button class="ptb-view-all-btn" data-switch-view="entregas">Ver todas las entregas ➔</button>
      </div>

      <div class="ptb-grid" id="homePendingTasksGrid">
      </div>
    """
        html = html[:m_ptb.start(2)] + new_ptb_body + html[m_ptb.end(2):]

    # Encabezado de la pestaña de Entregas
    html = html.replace(
        '<h2>Próximas entregas y prácticas (2 pendientes · 5 completadas en 3 asignaturas)</h2>\\n        <p>Seguimiento de prácticas y trabajos del Máster: 2 tareas abiertas con plazo activo (ICACOR) y 5 prácticas ya entregadas con éxito agrupadas en desplegables por asignatura.</p>',
        '<h2 id="deliveriesSectionMainHeading">Próximas entregas y prácticas del estudiante</h2>\\n        <p id="deliveriesSectionMainSub">Seguimiento individual de prácticas y trabajos del Máster. Marca cada tarea según la hayas entregado para gestionar tus plazos de forma personalizada.</p>'
    )
    html = html.replace(
        '<h2>Próximas entregas y prácticas (2 pendientes · 5 completadas en 3 asignaturas)</h2>\n        <p>Seguimiento de prácticas y trabajos del Máster: 2 tareas abiertas con plazo activo (ICACOR) y 5 prácticas ya entregadas con éxito agrupadas en desplegables por asignatura.</p>',
        '<h2 id="deliveriesSectionMainHeading">Próximas entregas y prácticas del estudiante</h2>\n        <p id="deliveriesSectionMainSub">Seguimiento individual de prácticas y trabajos del Máster. Marca cada tarea según la hayas entregado para gestionar tus plazos de forma personalizada.</p>'
    )

    # Resumen y filtros en Entregas
    html = html.replace(
        '<span class="status-filter-summary" id="deliveryFilterSummary">Mostrando 7 prácticas (2 pendientes y 5 completadas en 3 asignaturas).</span>',
        '<span class="status-filter-summary" id="deliveryFilterSummary">Mostrando el listado completo de entregas del máster.</span>'
    )
    html = html.replace(
        '<div class="delivery-range" id="deliveryRange">2 pendientes · 5 entregadas</div>',
        '<div class="delivery-range" id="deliveryRange">Control de entregas</div>'
    )

    # Notas y Tests: neutralizar referencias fijas a entregas de Raquel
    html = html.replace(
        '<span class="due-state submitted" style="font-size:11px">2 notas por correo · 2 tests superados · 5 prácticas entregadas</span>',
        '<span class="due-state submitted" style="font-size:11px">Ponderación oficial: 40% Cuestionario tipo test + 60% Trabajos y casos prácticos</span>'
    )
    html = html.replace(
        '<p style="color:var(--ink-soft);margin:0">Redacción y presentación formal de escritos procesales, apoderamientos apud acta, resoluciones de casos y dictámenes entregados en CPROC o remitidos al ICACOR (5 entregadas con éxito y 2 pendientes con Delgado).</p>',
        '<p style="color:var(--ink-soft);margin:0">Redacción y presentación formal de escritos procesales, apoderamientos apud acta, resoluciones de casos y dictámenes evaluables en CPROC o ICACOR (60% de la evaluación continua).</p>'
    )
    html = html.replace(
        '<span class="stat-title">5 entregadas en 3 asignaturas</span>\\n        </div>\\n        <span class="stat-val-pill">5 / 5 ✓</span>',
        '<span class="stat-title">Casos prácticos CPROC e ICACOR</span>\\n        </div>\\n        <span class="stat-val-pill">60% de nota</span>'
    )
    html = html.replace(
        '<span class="stat-title">5 entregadas en 3 asignaturas</span>\n        </div>\n        <span class="stat-val-pill">5 / 5 ✓</span>',
        '<span class="stat-title">Casos prácticos CPROC e ICACOR</span>\n        </div>\n        <span class="stat-val-pill">60% de nota</span>'
    )
    html = html.replace(
        "sumEl.textContent = 'Mostrando casos prácticos, dictámenes y escritos evaluables agrupados por estado de entrega (5 entregadas y 2 pendientes con Delgado).';",
        "sumEl.textContent = 'Mostrando casos prácticos, dictámenes y escritos evaluables según los hayas marcado como entregados o pendientes.';"
    )

    # Calendario mensual: reflejar si el estudiante actual tiene la entrega pendiente
    html = html.replace(
        'hasDue=deliveries.some(x=>keyOf(x.date)===k && !x.submitted);',
        'hasDue=deliveries.some(x=>keyOf(x.date)===k && !isDeliveryChecked(x.detailKey));'
    )
    print("✓ Interfaz de entregas (portada, sidebar, pestaña y calendario) desacoplada con estados dinámicos.")

    # -------------------------------------------------------------
    # 8. CSS: PALETA SOLEMNE INSTITUCIONAL ("MODO DERECHO / TOGA Y ESTRADO")
    # -------------------------------------------------------------
    student_custom_css = """
/* ========================================================
   PALETA SOLEMNE INSTITUCIONAL: ABOGACÍA Y PROCURA (MODO DERECHO)
   ======================================================== */
:root, [data-theme="dark"] {
  /* Fondo y tarjetas: Sala de Togas & Despacho Jurídico Solemne */
  --bg: #0c0f13;
  --paper: #12161e;
  --paper-warm: #181e28;
  --paper-card: #131720;
  --sidebar-bg: #0e1218;

  /* Tipografía: Marfil y plata nítida de alta legibilidad */
  --ink: #e8ecf2;
  --ink-soft: #adb5c2;
  --muted: #727c8a;
  --line: #222936;
  --line-subtle: #191f2b;

  /* Azul Toga Institucional (Austero y Solemne) */
  --green: #294d73;
  --green-dark: #8cb6dc;
  --green-pale: #101a26;
  --green-badge: #152435;
  --green-border: #234263;

  /* Azul Abogacía / Estrado */
  --blue: #325b84;
  --blue-dark: #9bc0e4;
  --blue-pale: #121c27;
  --blue-badge: #182839;
  --blue-border: #284a6e;

  /* Granate Lacre Notarial / Sello Judicial (Entregas y plazos) */
  --terracotta: #8a343c;
  --terra-dark: #dc828c;
  --terra-pale: #221215;
  --terra-badge: #2e171b;
  --terra-border: #54272f;

  /* Bronce Antiguo / Latón de Biblioteca Jurídica */
  --honey: #95722f;
  --honey-dark: #dfba6c;
  --honey-pale: #221a10;
  --honey-badge: #2e2314;
  --honey-border: #564020;

  --plum: #623f5b;
}

[data-theme="light"] {
  /* Fondo y tarjetas: Papel Verjurado Calizo / Alabastro Institucional */
  --bg: #f4f5f7;
  --paper: #ffffff;
  --paper-warm: #eaedf2;
  --paper-card: #ffffff;
  --sidebar-bg: #e5e9f0;

  /* Tipografía: Tinta Ferrogálica Profunda (Negro Solemne de Tribunal) */
  --ink: #0f141a;
  --ink-soft: #2d3642;
  --muted: #5e6875;
  --line: #cbd3de;
  --line-subtle: #dbe2eb;

  /* Azul Marino Toga / Magistratura Institucional */
  --green: #142a42;
  --green-dark: #0a1725;
  --green-pale: #e7eff6;
  --green-badge: #d4e2ee;
  --green-border: #acc4d8;

  /* Azul Abogacía Clásica */
  --blue: #1c3856;
  --blue-dark: #0f2032;
  --blue-pale: #e9f0f7;
  --blue-badge: #d7e4f1;
  --blue-border: #b0c9df;

  /* Granate Sello Notarial / Lacre Procesal */
  --terracotta: #661a22;
  --terra-dark: #450f15;
  --terra-pale: #f7ebed;
  --terra-badge: #edd4d7;
  --terra-border: #d7acb2;

  /* Bronce Antiguo / Latón Noble */
  --honey: #70521e;
  --honey-dark: #4d3713;
  --honey-pale: #f7f3eb;
  --honey-badge: #ede4d1;
  --honey-border: #d7c6a4;

  --plum: #482a42;
}

.portal-mode-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--green-pale);
  border: 1.5px solid var(--green-border);
  color: var(--green-dark);
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 11.5px;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  white-space: nowrap;
}

/* ESTILOS PERSONALIZADOS DEL PORTAL DEL ESTUDIANTE (NOTAS Y CHECKS LOCALSTORAGE) */
.student-eval-bar {
  background: var(--paper-warm);
  border: 1.5px solid var(--line);
  border-radius: 12px;
  padding: 14px 18px;
  margin: 12px 0 16px;
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 16px;
  align-items: start;
}
@media(max-width: 768px) {
  .student-eval-bar {
    grid-template-columns: 1fr;
    gap: 10px;
  }
}
.student-eval-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.student-eval-field label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--green-dark);
  letter-spacing: 0.03em;
}
.student-eval-field input, .student-eval-field textarea {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
  color: var(--ink);
  font: inherit;
  font-size: 13.5px;
  padding: 8px 12px;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.student-eval-field input:focus, .student-eval-field textarea:focus {
  outline: none;
  border-color: var(--green);
  box-shadow: 0 0 0 3px rgba(20, 42, 66, 0.15);
}
.student-save-status {
  font-size: 11.5px;
  font-weight: 600;
  color: var(--green-dark);
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  transition: opacity 0.3s ease;
}
.student-test-row {
  margin-top: 8px;
  padding: 12px 16px;
  background: var(--paper);
  border: 1.5px dashed var(--green-border);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}
.student-test-input-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}
.student-test-input-wrap input {
  width: 120px;
  font-weight: 700;
  color: var(--green-dark);
  text-align: center;
  border: 1.5px solid var(--green-border);
  background: var(--green-pale);
  border-radius: 6px;
  padding: 7px 10px;
  font-size: 14px;
}
.student-test-input-wrap input:focus {
  outline: none;
  border-color: var(--green-dark);
  box-shadow: 0 0 0 3px rgba(20, 42, 66, 0.2);
}
.delivery-check-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1.5px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  padding: 7px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}
.delivery-check-btn:hover {
  border-color: var(--green);
  background: var(--green-pale);
}
.delivery-check-btn.checked {
  background: var(--green);
  color: #ffffff;
  border-color: var(--green-dark);
}
.delivery-check-btn.checked .check-box {
  background: #ffffff;
  color: var(--green-dark);
}
.check-box {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  border: 1.5px solid currentColor;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 900;
}
.privacy-banner {
  background: var(--green-pale);
  border: 1px solid var(--green-border);
  border-radius: 12px;
  padding: 14px 20px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 13px;
  color: var(--green-dark);
  font-weight: 500;
  line-height: 1.5;
}
.privacy-banner svg {
  flex-shrink: 0;
}

/* Logo e icono distintivo del Portal del Estudiante (Oxford Navy y birrete) */
.brand-icon {
  background: linear-gradient(135deg, #101c27 0%, #1a2f45 60%, #294d73 100%) !important;
  color: #fffef9 !important;
  box-shadow: 0 4px 14px rgba(41, 77, 115, 0.45) !important;
  border: 1.5px solid rgba(140, 182, 220, 0.3) !important;
}
[data-theme="light"] .brand-icon {
  background: linear-gradient(135deg, #dbe6f3 0%, #bdd2ea 60%, #9cbde0 100%) !important;
  color: #172b42 !important;
  box-shadow: 0 4px 12px rgba(41, 77, 115, 0.2) !important;
  border: 1.5px solid rgba(41, 77, 115, 0.35) !important;
}
"""
    html = html.replace('</style>', student_custom_css + '\n</style>', 1)

    # -------------------------------------------------------------
    # 9. REEMPLAZAR renderTeacherDossiers CON INTERACTIVIDAD LOCALSTORAGE
    # -------------------------------------------------------------
    idx_dossiers = html.find('function renderTeacherDossiers()')
    end_idx_dossiers = html.find('function renderPracticesGradeView()', idx_dossiers)

    if idx_dossiers != -1 and end_idx_dossiers != -1:
        new_dossiers_code = """function getStudentGradeData(teacherId){
  try {
    const raw = localStorage.getItem('muap_eval_' + teacherId);
    return raw ? JSON.parse(raw) : { finalGrade:'', testGrade:'', notes:'' };
  } catch(e){
    return { finalGrade:'', testGrade:'', notes:'' };
  }
}

function saveStudentGradeData(teacherId, data){
  try {
    const current = getStudentGradeData(teacherId);
    const updated = { ...current, ...data };
    localStorage.setItem('muap_eval_' + teacherId, JSON.stringify(updated));
    updateHomeGradesBadge();
  } catch(e){}
}

function updateHomeGradesBadge(){
  let count = 0;
  try {
    for(let i = 0; i < localStorage.length; i++){
      const k = localStorage.key(i);
      if(k && k.startsWith('muap_eval_')){
        const d = JSON.parse(localStorage.getItem(k));
        if(d && (d.finalGrade || d.testGrade)) count++;
      }
    }
  } catch(e){}
  const el = document.getElementById('welcomeGradesSummary');
  if(el){
    el.textContent = count > 0 ? `${count} evaluadas por ti` : 'Mi Cuaderno de Notas';
  }
}

function renderTeacherDossiers(){
  const dossiers = [
   {
    id: 'dossier-carlos-sanchez',
    teacher: 'Carlos Miguel Sánchez Muiño',
    subject: 'Técnicas instrumentales · Rama Procura (Sesión 2 oct 2026)',
    subjectRef: 'Procura|Técnicas instrumentales|1',
    kicker: 'Materia finalizada · Evaluación de test y caso práctico',
    testName: 'Test de Técnicas instrumentales (40%)',
    blocks: [
     {
      cls: 'highlight-mail',
      title: '✉️ Calificación Docente Conjunta',
      score: 'Ponderación Oficial',
      desc: 'Test 40 % + Casos prácticos y técnica procesal 60 %.',
      subitems: [
       {label: 'Ponderación oficial', val: 'Test 40% + Escritos 60%'},
       {label: 'Fecha de la sesión', val: '2 oct 2026'}
      ]
     },
     {
      cls: 'highlight-test',
      title: '📝 Test de Técnicas instrumentales',
      score: '4.0 ptos máx.',
      desc: 'Cuestionario de evaluación continua presencial sobre iniciación y tramitación procesal.',
      subitems: [
       {label: 'Aporte a nota final', val: '40 % del total'},
       {label: 'Puntuación máx.', val: '4.0 puntos'}
      ]
     },
     {
      cls: 'highlight-practice',
      title: '📁 Práctica Procesal de Aula',
      score: '6.0 ptos máx.',
      desc: 'Resolución de casos de tramitación procesal y técnica forense.',
      subitems: [
       {label: 'Aporte a nota final', val: '60 % del total'},
       {label: 'Puntuación máx.', val: '6.0 puntos'}
      ]
     }
    ],
    actions: [
     {label: 'Ver asignatura ↗', subjectRef: 'Procura|Técnicas instrumentales|1'},
     {label: 'Ficha de Carlos M. Sánchez Muiño ↗', teacher: 'Carlos Miguel Sánchez Muiño'}
    ]
   },
   {
    id: 'dossier-javier-sanchez',
    teacher: 'Javier Carlos Sánchez García',
    subject: 'Técnicas instrumentales · Rama Procura (Sesión 1 oct 2026)',
    subjectRef: 'Procura|Técnicas instrumentales|0',
    kicker: 'Materia finalizada · Evaluación continua de iniciación profesional',
    testName: 'Test de Técnicas instrumentales (40%)',
    blocks: [
     {
      cls: 'highlight-mail',
      title: '✉️ Calificación Docente Conjunta',
      score: 'Ponderación Oficial',
      desc: 'Desglose conjunto oficial de la sesión inaugural.',
      subitems: [
       {label: 'Criterio ponderado', val: 'Test 40% + Práctica 60%'},
       {label: 'Sesión', val: '1 oct 2026'}
      ]
     },
     {
      cls: 'highlight-test',
      title: '📝 Test Presencial / Online',
      score: '4.0 ptos máx.',
      desc: 'Cuestionario de evaluación continua realizado en la sesión inaugural de Técnicas instrumentales.',
      subitems: [
       {label: 'Aporte a nota final', val: '40 % del total'},
       {label: 'Modalidad', val: 'Test presencial'}
      ]
     },
     {
      cls: 'highlight-practice',
      title: '📁 Trabajos y Casos Prácticos',
      score: '6.0 ptos máx.',
      desc: 'Resolución de casos prácticos y técnicas de estrados en sala judicial.',
      subitems: [
       {label: 'Aporte a nota final', val: '60 % del total'},
       {label: 'Puntuación máx.', val: '6.0 puntos'}
      ]
     }
    ],
    actions: [
     {label: 'Ver asignatura ↗', subjectRef: 'Procura|Técnicas instrumentales|0'},
     {label: 'Ficha de Javier Sánchez García ↗', teacher: 'Javier Sánchez García'}
    ]
   },
   {
    id: 'dossier-ana-vazquez',
    teacher: 'Ana Vázquez Corte',
    subject: 'Deontología y técnicas transversales · Rama Procura (Sesiones 8 y 9 oct 2026)',
    subjectRef: 'Procura|Deontología y responsabilidad|0',
    kicker: 'Materia finalizada y evaluada · Calificación docente',
    testName: 'Test de Deontología (40%)',
    blocks: [
     {
      cls: 'highlight-mail',
      title: '✉️ Calificación Docente Conjunta',
      score: 'Ponderación Oficial',
      desc: 'Materia: Deontología y técnicas transversales.',
      subitems: [
       {label: 'Criterio', val: 'Test 40% + Caso CPROC 60%'},
       {label: 'Fecha de impartición', val: '8 y 9 oct 2026'}
      ]
     },
     {
      cls: 'highlight-test',
      title: '📝 Test de Deontología (40 %)',
      score: '4.0 ptos máx.',
      desc: 'Prueba tipo test de 4 puntos sobre deberes, estatuto orgánico y deontología de la Procura.',
      subitems: [
       {label: 'Porcentaje nota', val: '40 % de la calificación'},
       {label: 'Puntuación máx.', val: '4.0 puntos'}
      ]
     },
     {
      cls: 'highlight-practice',
      title: '📁 Caso Práctico CPROC (60 %)',
      score: '6.0 ptos máx.',
      desc: 'Caso «Derechos, deberes y responsabilidad profesional del procurador» entregado en plataforma CPROC.',
      subitems: [
       {label: 'Porcentaje nota', val: '60 % de la calificación'},
       {label: 'Plataforma', val: 'CPROC (MUAP)'}
      ]
     }
    ],
    actions: [
     {label: '📁 Ver caso en CPROC (15 oct) ↗', detailKey: 'assignment'},
     {label: 'Ver asignatura ↗', subjectRef: 'Procura|Deontología y responsabilidad|0'},
     {label: 'Ficha de Ana Vázquez Corte ↗', teacher: 'Ana Vázquez Corte'}
    ]
   },
   {
    id: 'dossier-sandra-mosteiro',
    teacher: 'Sandra Mosteiro Costa',
    subject: 'Actos de comunicación judicial · Rama Procura (Sesiones 19 y 20 oct 2026)',
    subjectRef: 'Procura|Técnicas instrumentales|3',
    kicker: 'Test online y caso práctico evaluable de 6 escenarios LEC',
    testName: 'Test online Testmoz (20 oct)',
    blocks: [
     {
      cls: 'highlight-test',
      title: '📝 Test Online en Testmoz (20 oct)',
      score: '10 preguntas',
      desc: 'Cuestionario oficial en Testmoz sobre citaciones, emplazamientos, LexNET y auxilio judicial.',
      subitems: [
       {label: 'Total preguntas', val: '10 preguntas'},
       {label: 'Plataforma', val: 'Testmoz / CPROC'}
      ]
     },
     {
      cls: 'highlight-practice',
      title: '📁 Caso Práctico 2026 en CPROC',
      score: '6 escenarios LEC',
      desc: 'Caso práctico oficial evaluable relativo a actos de comunicación judicial y reflexiones jurisprudenciales en CPROC.',
      subitems: [
       {label: 'Enunciado', val: 'CASO_PRACTICO_2026_SANDRA.pdf'},
       {label: 'Entrega', val: 'Plataforma CPROC'}
      ]
     },
     {
      cls: 'highlight-mail',
      title: '✉️ Calificación Conjunta por Correo',
      score: 'En ponderación',
      desc: 'La Secretaría y la docente remitirán el desglose oficial conjunto una vez evaluados todos los casos prácticos presentados.',
      subitems: [
       {label: 'Test online', val: 'Evaluado en Testmoz'},
       {label: 'Caso escrito', val: 'En corrección docente'}
      ]
     }
    ],
    actions: [
     {label: '📁 Ver caso práctico en el portal ↗', detailKey: 'entrega_caso_pr_ctico_de_actos_de', cls: 'solid-green'},
     {label: 'Ver asignatura ↗', subjectRef: 'Procura|Técnicas instrumentales|3'},
     {label: 'Ficha de Sandra Mosteiro Costa ↗', teacher: 'Sandra Mosteiro Costa'}
    ]
   },
   {
    id: 'dossier-carolina-moreno',
    teacher: 'Carolina Moreno Vázquez y Carlos M. Sánchez Muiño',
    subject: 'Deontología y técnicas transversales · Proceso digital y TIC (Sesión 16 oct 2026)',
    subjectRef: 'Procura|Técnicas instrumentales|2',
    kicker: 'Test oficial de clase en Testmoz y 3 prácticas en CPROC',
    testName: 'Test online Testmoz (16 oct · 20 preguntas)',
    blocks: [
     {
      cls: 'highlight-test',
      title: '📝 Test Online en Testmoz (16 oct)',
      score: '20 preguntas',
      desc: 'Test oficial de clase completado en Testmoz sobre LexNET, firma electrónica y subsanaciones procesales.',
      subitems: [
       {label: 'Cuestionario', val: '20 preguntas tipo test'},
       {label: 'Plataforma', val: 'Testmoz / CPROC'}
      ]
     },
     {
      cls: 'highlight-practice',
      title: '📁 Prácticas en CPROC (3 tareas)',
      score: '3 prácticas',
      desc: '1) Apoderamiento apud acta, 2) Escrito de subsanación firmado, y 3) Auto concursal UP en CPROC.',
      subitems: [
       {label: 'Poder apud acta', val: 'Certificado oficial'},
       {label: 'Auto UP', val: 'Oferta de venta UP'}
      ]
     },
     {
      cls: 'highlight-mail',
      title: '✉️ Calificación Conjunta por Correo',
      score: 'Ponderación Oficial',
      desc: '40 % Test de evaluación continua + 60 % Prácticas procesales de CPROC.',
      subitems: [
       {label: 'Test online', val: '40 % de la nota'},
       {label: 'Tareas CPROC', val: '60 % de la nota'}
      ]
     }
    ],
    actions: [
     {label: '📁 Ver tareas de CPROC en el portal ↗', detailKey: 'entrega_apud_acta'},
     {label: 'Ver asignatura ↗', subjectRef: 'Procura|Técnicas instrumentales|2'},
     {label: 'Ficha de Carolina Moreno Vázquez ↗', teacher: 'Carolina Moreno Vázquez'}
    ]
   },
   {
    id: 'dossier-jose-luis-delgado',
    teacher: 'José Luis Delgado Domínguez',
    subject: 'Responsabilidad civil y penal, aseguramiento y turno de oficio · Abogacía',
    subjectRef: 'Abogacía|Técnicas instrumentales|3',
    kicker: 'Módulo en desarrollo · 2 prácticas con plazo de entrega activo',
    testName: 'Evaluación continua presencial (ICACOR)',
    blocks: [
     {
      cls: 'highlight-practice',
      title: '📁 Prácticas con Plazo de Entrega Abierto',
      score: '2 casos activos',
      desc: 'Trabajos prácticos encargados en clase: Parte A (Insostenibilidad y AJG) y Parte B (Parte de siniestro y Turno de Oficio).',
      subitems: [
       {label: 'Parte A (Insostenibilidad)', val: 'Plazo: 29 oct 2026'},
       {label: 'Parte B (Parte siniestro)', val: 'Plazo: 30 oct 2026'}
      ]
     },
     {
      cls: 'highlight-test',
      title: '📝 Test / Evaluación Continua',
      score: 'Presencial',
      desc: 'Módulo de responsabilidad profesional del abogado en desarrollo presencial en el Colegio de Abogados.',
      subitems: [
       {label: 'Docencia', val: 'Colegio de Abogados'},
       {label: 'Rama', val: 'Abogacía'}
      ]
     },
     {
      cls: 'highlight-mail',
      title: '✉️ Calificación Conjunta por Correo',
      score: 'Pendiente',
      desc: 'Se remitirá por la secretaría del ICACOR una vez presentados y corregidos los dictámenes y escritos del turno de oficio.',
      subitems: [
       {label: 'Estado', val: 'Plazo activo para entregar'}
      ]
     }
    ],
    actions: [
     {label: '⏳ Ver entrega Parte A (plazo 29 oct) ↗', detailKey: 'entrega_delgado_parte_a', cls: 'solid-green'},
     {label: '⏳ Ver entrega Parte B (plazo 30 oct) ↗', detailKey: 'entrega_delgado_parte_b'},
     {label: 'Ver asignatura ↗', subjectRef: 'Abogacía|Técnicas instrumentales|3'},
     {label: 'Ficha de José Luis Delgado Domínguez ↗', teacher: 'José Luis Delgado Domínguez'}
    ]
   }
  ];

  // Sincronización automática: si hay docentes evaluados en teacherGradeMap o teacherDirectory, integrarlos en el cuaderno del estudiante
  if (typeof teacherGradeMap !== 'undefined' && teacherGradeMap) {
    const knownTeachers = new Set(dossiers.map(d => (d.teacher || '').toLowerCase().trim()));
    Object.keys(teacherGradeMap).forEach(tName => {
      if (!tName) return;
      const clean = tName.toLowerCase().trim();
      const exists = Array.from(knownTeachers).some(kt => kt.includes(clean) || clean.includes(kt));
      if (!exists) {
        const idSafe = 'dossier-' + clean.replace(/[^a-z0-9]+/g, '-');
        const tObj = (typeof teacherDirectory !== 'undefined' && Array.isArray(teacherDirectory))
          ? teacherDirectory.find(t => (t.name || '').toLowerCase().trim().includes(clean) || clean.includes((t.name || '').toLowerCase().trim()))
          : null;
        dossiers.push({
          id: idSafe,
          teacher: tName,
          subject: (tObj && tObj.subject) ? tObj.subject : 'Módulo con actividad evaluable',
          subjectRef: (tObj && tObj.subjectRef) ? tObj.subjectRef : '',
          kicker: 'Evaluación docente registrada · Cuaderno del estudiante',
          testName: 'Test / Prueba de evaluación continua',
          blocks: [
            {
              cls: 'highlight-mail',
              title: '✉️ Calificación Docente',
              score: 'Evaluación continua',
              desc: 'Calificación oficial y ponderación de pruebas y trabajos.',
              subitems: [
                {label: 'Materia', val: (tObj && tObj.subject) ? tObj.subject : 'Evaluación oficial'},
                {label: 'Docente', val: tName}
              ]
            }
          ],
          actions: [
            {label: `Ficha de ${tName} ↗`, teacher: tName}
          ]
        });
        knownTeachers.add(clean);
      }
    });
  }

  const privacyNotice = `
    <div class="privacy-banner">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><circle cx="12" cy="11" r="3"/></svg>
      <div>
        <strong>Tu Cuaderno Privado de Notas (Guardado local en tu dispositivo):</strong>
        Las notas de los tests, las calificaciones del profesor y tus anotaciones personales se guardan únicamente en la memoria de tu navegador (localStorage). Nadie más puede verlas y no se suben a ningún servidor.
      </div>
    </div>
  `;

  return privacyNotice + dossiers.map(d => {
    const sData = getStudentGradeData(d.id);
    const badgeText = sData.finalGrade ? `★ ${sData.finalGrade} · Mi Nota` : (sData.testGrade ? `Test: ${sData.testGrade}` : 'Sin calificar');
    const badgeCls = sData.finalGrade ? 'gold' : (sData.testGrade ? 'blue' : 'terra');

    return `
    <article class="teacher-grade-dossier" id="${d.id}">
      <div class="tgd-header">
        <div class="tgd-title-group" style="width:100%">
          <div class="tgd-kicker">${d.kicker}</div>
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px">
            <h3 class="tgd-teacher-name">
              <button class="teacher-link" data-teacher="${d.teacher}" style="font:inherit;color:inherit;text-align:left;background:none;border:none;padding:0;cursor:pointer">${d.teacher}</button>
            </h3>
            <div class="tgd-badge ${badgeCls}" id="badge_${d.id}">${badgeText}</div>
          </div>
          <div class="tgd-subject"><button class="subject-open" data-subject="${d.subjectRef}" style="font:inherit;color:inherit;background:none;border:none;padding:0;cursor:pointer">${d.subject} ↗</button></div>

          <!-- ZONA AL LADO / DEBAJO DEL NOMBRE PARA NOTA FINAL Y REDACTAR OBSERVACIONES -->
          <div class="student-eval-bar">
            <div class="student-eval-field">
              <label for="input_final_${d.id}">★ Nota final del profesor:</label>
              <input type="text" id="input_final_${d.id}" placeholder="Ej: 10 / 10 o 8.8" value="${sData.finalGrade}" oninput="handleStudentGradeChange('${d.id}')">
            </div>
            <div class="student-eval-field">
              <label for="input_notes_${d.id}">✍️ Anotaciones personales / Criterios de corrección:</label>
              <textarea id="input_notes_${d.id}" rows="2" placeholder="Escribe aquí tus comentarios, qué dijo el profesor, dudas o fechas de revisión..." oninput="handleStudentGradeChange('${d.id}')">${sData.notes}</textarea>
            </div>
            <div style="grid-column:1 / -1;display:flex;justify-content:space-between;align-items:center">
              <span class="student-save-status" id="status_${d.id}">✓ Guardado automáticamente</span>
            </div>
          </div>
        </div>
      </div>

      <!-- CASILLA DE CALIFICACIÓN DEL PROPIO TEST -->
      <div class="student-test-row">
        <div style="display:flex;align-items:center;gap:8px">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          <strong style="font-size:13px;color:var(--ink)">${d.testName || 'Test de evaluación continua:'}</strong>
        </div>
        <div class="student-test-input-wrap">
          <label for="input_test_${d.id}" style="font-size:12px;font-weight:700;color:var(--ink-soft)">Mi nota en el test:</label>
          <input type="text" id="input_test_${d.id}" placeholder="Ej: 9 / 10" value="${sData.testGrade}" oninput="handleStudentGradeChange('${d.id}')">
        </div>
      </div>

      <div class="tgd-blocks-grid" style="margin-top:14px">
        ${d.blocks.map(b => `
          <div class="tgd-block ${b.cls}">
            <div>
              <div class="tgd-block-title">
                <span>${b.title}</span>
              </div>
              <div class="tgd-block-score">${b.score}</div>
              <p class="tgd-block-desc">${b.desc}</p>
            </div>
            <div class="tgd-sublist">
              ${b.subitems.map(si => `
                <div class="tgd-subitem">
                  <span style="color:var(--ink-soft)">${si.label}</span>
                  <b style="color:var(--ink);text-align:right">${si.val}</b>
                </div>
              `).join('')}
            </div>
          </div>
        `).join('')}
      </div>

      <div class="action-pills" style="margin-top:10px">
        ${d.actions.map(l => l.detailKey ? `<button class="pill-btn ${l.cls||''}" data-detail="${l.detailKey}">${l.label}</button>` : l.subjectRef ? `<button class="pill-btn ${l.cls||''}" data-subject="${l.subjectRef}">${l.label}</button>` : l.teacher ? `<button class="pill-btn ${l.cls||''}" data-teacher="${l.teacher}">${l.label}</button>` : `<a class="pill-link ${l.cls||''}" href="${l.url}" target="_blank" rel="noopener noreferrer">${l.label}</a>`).join('')}
      </div>
    </article>
    `;
  }).join('');
}

function handleStudentGradeChange(teacherId){
  const fInput = document.getElementById('input_final_' + teacherId);
  const tInput = document.getElementById('input_test_' + teacherId);
  const nInput = document.getElementById('input_notes_' + teacherId);
  const statusEl = document.getElementById('status_' + teacherId);
  const badgeEl = document.getElementById('badge_' + teacherId);

  const finalGrade = fInput ? fInput.value.trim() : '';
  const testGrade = tInput ? tInput.value.trim() : '';
  const notes = nInput ? nInput.value.trim() : '';

  saveStudentGradeData(teacherId, { finalGrade, testGrade, notes });

  if(badgeEl){
    badgeEl.textContent = finalGrade ? `★ ${finalGrade} · Mi Nota` : (testGrade ? `Test: ${testGrade}` : 'Sin calificar');
    badgeEl.className = 'tgd-badge ' + (finalGrade ? 'gold' : (testGrade ? 'blue' : 'terra'));
  }

  if(statusEl){
    statusEl.textContent = '✓ Guardado en tu equipo';
    statusEl.style.opacity = '1';
    setTimeout(() => { if(statusEl) statusEl.style.opacity = '0.7'; }, 1500);
  }
}
\n\n"""
        html = html[:idx_dossiers] + new_dossiers_code + html[end_idx_dossiers:]
        print("✓ renderTeacherDossiers adaptada con inputs interactivos de test, nota final y redacción.")

    # -------------------------------------------------------------
    # 10. REEMPLAZAR renderDeliveries CON CONTROL TOTAL DINÁMICO EN LOCALSTORAGE
    # -------------------------------------------------------------
    idx_render_del = html.find('function renderDeliveries(filter = currentDeliveryFilter){')
    idx_end_render_del = html.find('\nlet toastNotificationTimer', idx_render_del)
    if idx_end_render_del == -1:
        idx_end_render_del = html.find('\nfunction renderMail(', idx_render_del)
    if idx_render_del != -1 and idx_end_render_del != -1:
        custom_render_deliveries_code = """function isDeliveryChecked(detailKey){
  try {
    return localStorage.getItem('muap_deliv_check_' + detailKey) === 'true';
  } catch(e){
    return false;
  }
}

function toggleDeliveryCheck(detailKey, btnEl){
  try {
    const current = isDeliveryChecked(detailKey);
    const newVal = !current;
    localStorage.setItem('muap_deliv_check_' + detailKey, newVal ? 'true' : 'false');
    
    // Sincronizar en el array deliveries en memoria
    deliveries.forEach(d => {
      if(d.detailKey === detailKey){
        d.submitted = newVal;
        d.status = newVal ? 'Entregada por mí ✓' : '⏳ Pendiente de marcar';
      }
    });

    // Re-renderizar entregas, portada, menú lateral, contadores y calendario
    renderDeliveries(currentDeliveryFilter);
    renderHomePendingTasks();
    renderSidebarPendingItems();
    updateDeliveryCounts();
    if(typeof renderMonth === 'function') renderMonth();
  } catch(e){}
}

function updateDeliveryCounts(){
  deliveries.forEach(d => {
    d.submitted = isDeliveryChecked(d.detailKey);
    d.status = d.submitted ? 'Entregada por mí ✓' : '⏳ Pendiente de marcar';
  });

  const pending = deliveries.filter(d => !d.submitted);
  const pendingCount = pending.length;
  const completedCount = deliveries.length - pendingCount;

  // 1. Sidebar badge
  const sideBadge = document.getElementById('sideNavDeliveriesBadge') || document.querySelector('.nav-btn-entregas .nav-badge-pill');
  if(sideBadge){
    sideBadge.textContent = pendingCount > 0 ? `⏳ ${pendingCount} pend.` : '✓ Al día';
    sideBadge.className = 'nav-badge-pill ' + (pendingCount > 0 ? 'badge-terra highlight-pill' : 'badge-green');
  }

  // 2. Tab badge
  const tabBadge = document.getElementById('tabDeliveriesBadge') || document.querySelector('[data-view="entregas"] .tab-badge');
  if(tabBadge){
    tabBadge.textContent = pendingCount > 0 ? `${pendingCount} pend.` : '¡Al día! ✓';
    tabBadge.style.background = pendingCount > 0 ? 'var(--terracotta)' : 'var(--green)';
  }

  // 3. Welcome badge
  const welcomeDeliveriesBadge = document.getElementById('welcomeDeliveriesSummary') || document.querySelector('.welcome-badge.badge-terra .badge-value');
  if(welcomeDeliveriesBadge){
    welcomeDeliveriesBadge.textContent = pendingCount > 0 ? `${pendingCount} por entregar` : '¡Todas entregadas! 🎉';
  }

  // 4. Banner en portada
  const ptbBadge = document.getElementById('ptbBadgeEl') || document.querySelector('.ptb-badge');
  if(ptbBadge){
    ptbBadge.textContent = pendingCount > 0 ? `⚠️ ${pendingCount} PRÁCTICAS PENDIENTES` : '🎉 ¡TODAS LAS PRÁCTICAS ENTREGADAS!';
    ptbBadge.className = 'ptb-badge ' + (pendingCount > 0 ? 'alert' : 'success');
  }

  const ptbUrgent = document.getElementById('ptbUrgentChipEl');
  if(ptbUrgent){
    ptbUrgent.textContent = pendingCount > 0 ? '📅 Próxima entrega: 29 oct' : '✓ Al día';
  }

  // 5. Encabezado de sección
  const mainHeading = document.getElementById('deliveriesSectionMainHeading');
  if(mainHeading){
    mainHeading.textContent = `Próximas entregas y prácticas (${pendingCount} pendientes · ${completedCount} entregadas por ti)`;
  }

  const rangeEl = document.getElementById('deliveryRange');
  if(rangeEl){
    rangeEl.textContent = `${pendingCount} pendientes · ${completedCount} marcadas como entregadas`;
  }
}

function renderHomePendingTasks(){
  const grid = document.getElementById('homePendingTasksGrid');
  if(!grid) return;

  const pending = deliveries.filter(d => !isDeliveryChecked(d.detailKey));
  
  if(!pending.length){
    grid.innerHTML = `
      <div style="grid-column:1 / -1;background:var(--paper-warm);border:1.5px dashed var(--green-border);border-radius:12px;padding:26px 20px;text-align:center">
        <span style="font-size:28px">🎉</span>
        <h4 style="color:var(--green-dark);font-size:16px;margin:8px 0 4px;font-family:var(--serif)">¡Todas las prácticas marcadas como entregadas!</h4>
        <p style="color:var(--ink-soft);font-size:13px;margin:0 0 14px">Has marcado como entregadas todas las tareas del Máster en tu dispositivo.</p>
        <button class="pill-btn solid-green" onclick="setView('entregas', false)">Ver entregas completadas en el portal ➔</button>
      </div>
    `;
    return;
  }

  grid.innerHTML = pending.map(d => {
    const isChk = false;
    const isAbogacia = (d.subjectRef||'').includes('Abogacía');
    const tagLabel = isAbogacia ? '⚖️ Práctica ICACOR · Abogacía' : '🏛️ Práctica CPROC · Procura';
    const tagCls = isAbogacia ? 'blue' : 'terra';
    const dueTxt = fmtShort(d.date);

    return `
      <article class="ptb-card" id="homePendingCard_${d.detailKey}" data-detail="${d.detailKey}" style="cursor:pointer" onclick="openDetail('${d.detailKey}')" title="Pincha para ver las instrucciones">
        <div class="ptb-card-top">
          <span class="ptb-tag ${tagCls}">${tagLabel}</span>
          <span class="ptb-due-badge amber">⏳ Plazo: ${dueTxt}</span>
        </div>
        <h4 class="ptb-card-title">${d.title}</h4>
        <div class="ptb-card-meta">
          <div>👤 Docente: <b>${d.teacher}</b></div>
          <div>📚 Materia: <b>${d.subject}</b></div>
          ${d.details ? `<div style="margin-top:6px;font-size:12.5px;color:var(--ink-soft);line-height:1.4">${d.details}</div>` : ''}
        </div>
        <div style="margin-top:12px;padding-top:10px;border-top:1px dashed var(--line);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
          <button class="pill-btn" data-detail="${d.detailKey}" onclick="event.stopPropagation(); openDetail('${d.detailKey}')">Instrucciones ↗</button>
          <button class="delivery-check-btn" data-delivery-check-key="${d.detailKey}" onclick="event.stopPropagation(); toggleDeliveryCheck('${d.detailKey}', this)">
            <span class="check-box"></span>
            <span class="check-text">Marcar como entregada</span>
          </button>
        </div>
      </article>
    `;
  }).join('');
}

function renderSidebarPendingItems(){
  const container = document.getElementById('sidebarPendingItemsList');
  const badgeEl = document.getElementById('sidebarPendingAccordionBadge');
  if(!container) return;

  const pending = deliveries.filter(d => !isDeliveryChecked(d.detailKey));
  if(badgeEl){
    badgeEl.textContent = pending.length > 0 ? `${pending.length} pendientes` : '✓ Al día';
    badgeEl.className = 'nav-badge-pill ' + (pending.length > 0 ? 'badge-terra highlight-pill' : 'badge-green');
  }

  if(!pending.length){
    container.innerHTML = `
      <div style="font-size:11px;color:var(--green-dark);padding:8px;background:var(--paper-warm);border-radius:8px;text-align:center;font-weight:700">
        🎉 ¡Al día! 0 entregas pendientes
      </div>
    `;
    return;
  }

  container.innerHTML = pending.map(d => {
    const isAbogacia = (d.subjectRef||'').includes('Abogacía');
    const platform = isAbogacia ? 'ICACOR' : 'CPROC';
    const platCls = isAbogacia ? 'blue' : 'terra';
    const dueTxt = fmtShort(d.date);

    return `
      <button class="side-pending-item" data-detail="${d.detailKey}" onclick="openDetail('${d.detailKey}')" title="Ver entrega: ${d.title}">
        <div class="spi-head">
          <span class="spi-dot amber">●</span>
          <strong class="spi-date">${dueTxt}</strong>
          <span class="spi-platform ${platCls}">${platform}</span>
        </div>
        <div class="spi-title">${d.title}</div>
        <div class="spi-teacher">${d.teacher}</div>
      </button>
    `;
  }).join('');
}

function renderDeliveries(filter = currentDeliveryFilter){
 if(filter !== undefined) currentDeliveryFilter = filter;
 const listContainer = document.getElementById('deliveryList');
 if(!listContainer) return;

 document.querySelectorAll('[data-delivery-filter]').forEach(b=>{
  b.classList.toggle('active', b.getAttribute('data-delivery-filter') === currentDeliveryFilter);
 });

 deliveries.forEach(d => {
  d.submitted = isDeliveryChecked(d.detailKey);
  d.status = d.submitted ? 'Entregada por mí ✓' : '⏳ Pendiente de marcar';
 });

 const pendingCount = deliveries.filter(d => !d.submitted).length;
 const completedCount = deliveries.filter(d => d.submitted).length;

 const rangeEl = document.getElementById('deliveryRange');
 if(rangeEl){
  rangeEl.textContent = `${pendingCount} pendientes · ${completedCount} marcadas como entregadas`;
 }

 let filtered = deliveries;
 if(currentDeliveryFilter === 'pending'){
  filtered = deliveries.filter(d => !d.submitted);
 } else if(currentDeliveryFilter === 'completed'){
  filtered = deliveries.filter(d => d.submitted);
 } else if(currentDeliveryFilter === 'cproc'){
  filtered = deliveries.filter(d => (d.subject||'').toLowerCase().includes('procura') || (d.status||'').toLowerCase().includes('cproc') || (d.details||'').toLowerCase().includes('cproc'));
 } else if(currentDeliveryFilter === 'icacor'){
  filtered = deliveries.filter(d => (d.subject||'').toLowerCase().includes('abogacía') || (d.details||'').toLowerCase().includes('icacor') || (d.teacher||'').toLowerCase().includes('delgado'));
 }

 const summaryEl = document.getElementById('deliveryFilterSummary');
 if(summaryEl){
  if(currentDeliveryFilter === 'pending'){
   summaryEl.textContent = `Mostrando tus prácticas pendientes (${filtered.length}).`;
  } else if(currentDeliveryFilter === 'completed'){
   summaryEl.textContent = `Mostrando tus prácticas marcadas como entregadas (${filtered.length}).`;
  } else if(currentDeliveryFilter === 'cproc'){
   summaryEl.textContent = `Mostrando prácticas de la plataforma CPROC (${filtered.length}).`;
  } else if(currentDeliveryFilter === 'icacor'){
   summaryEl.textContent = `Mostrando prácticas del Colegio de Abogados (${filtered.length}).`;
  } else {
   summaryEl.textContent = `Mostrando el listado completo de entregas del máster (${filtered.length}).`;
  }
 }

 const renderRow = (d) => {
  const isChk = d.submitted;
  return `
  <div class="delivery-row" id="delivery-row-${d.detailKey}">
   <div style="flex:1;min-width:0">
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
     <strong style="color:var(--ink);font-size:14.5px">${d.title}</strong>
    </div>
    <div class="delivery-meta" style="margin-top:4px">
     <span>Docente: <b>${d.teacher}</b></span>
     <span>Materia: <b>${d.subject}</b></span>
     <span>Fecha / Plazo: <b>${fmtShort(d.date)}</b></span>
    </div>
    ${d.details ? `<div style="font-size:12.5px;color:var(--ink-soft);margin-top:6px;line-height:1.45">${d.details}</div>` : ''}

    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-top:10px;padding-top:8px;border-top:1px dashed var(--line)">
     <div class="action-pills">
      <button class="pill-btn" data-detail="${d.detailKey}">Ver instrucciones completas ↗</button>
      <a class="pill-link blue" href="${cprocUrl}" target="_blank" rel="noopener noreferrer">Plataforma CPROC ↗</a>
     </div>
     <button class="delivery-check-btn ${isChk ? 'checked' : ''}" data-delivery-check-key="${d.detailKey}" onclick="event.stopPropagation(); toggleDeliveryCheck('${d.detailKey}', this)">
      <span class="check-box">${isChk ? '✓' : ''}</span>
      <span class="check-text">${isChk ? '✓ Entregada por mí' : 'Marcar como entregada'}</span>
     </button>
    </div>
   </div>
   <span class="due-state ${isChk ? 'delivered' : 'pending'}">${d.status}</span>
  </div>
  `;
 };

 const renderCompletedGroup = (items) => {
  if(!items.length) return '';
  return `
  <details class="delivered-group-accordion" open style="margin-top:18px">
   <summary class="delivered-main-summary">
    <div style="display:flex;align-items:center;gap:10px">
     <span style="font-size:18px">📦</span>
     <span>Prácticas marcadas como entregadas por ti (${items.length})</span>
    </div>
    <div style="display:flex;align-items:center;gap:10px">
     <span class="due-state submitted" style="font-size:11px">Completadas ✓</span>
     <span class="sta-arrow">▾</span>
    </div>
   </summary>
   <div class="delivered-subjects-tree" style="padding:10px 14px">
    ${items.map(renderRow).join('')}
   </div>
  </details>
  `;
 };

 if(!filtered.length){
  listContainer.innerHTML = `<div class="empty" style="padding:28px;text-align:center;background:var(--paper-card);border:1.5px dashed var(--line);border-radius:14px">
   <p style="font-size:14px;color:var(--ink);font-weight:700;margin-bottom:6px">No hay prácticas para el filtro seleccionado.</p>
   <button type="button" class="pill-btn" onclick="renderDeliveries('all')" style="margin-top:8px">Restablecer filtros de entregas ↺</button>
  </div>`;
  return;
 }

 if(currentDeliveryFilter === 'pending'){
  let html = `<div class="delivery-group-header"><span>⏳ Prácticas y tareas pendientes de entrega (${filtered.length})</span><span style="font-size:11px;color:var(--honey-dark);font-weight:800">Próx. vencimiento: 29 oct</span></div>`;
  html += filtered.map(renderRow).join('');
  listContainer.innerHTML = html;
 } else if(currentDeliveryFilter === 'completed'){
  listContainer.innerHTML = renderCompletedGroup(filtered);
 } else {
  const pendingItems = filtered.filter(d => !d.submitted);
  const completedItems = filtered.filter(d => d.submitted);
  let html = '';
  if(pendingItems.length){
   html += `<div class="delivery-group-header"><span>⏳ Prácticas y tareas pendientes de entrega (${pendingItems.length})</span><span style="font-size:11px;color:var(--honey-dark);font-weight:800">Próx. vencimiento: 29 oct</span></div>`;
   html += pendingItems.map(renderRow).join('');
  }
  if(completedItems.length){
   html += renderCompletedGroup(completedItems);
  }
  listContainer.innerHTML = html;
 }
}
"""
        html = html[:idx_render_del] + custom_render_deliveries_code + html[idx_end_render_del:]
        print("✓ Función renderDeliveries y renderHomePendingTasks completamente adaptadas con persistencia en localStorage.")

    # -------------------------------------------------------------
    # 11 & 12. INICIALIZAR CONTADORES Y RENDERIZADO AL ARRANCAR
    # -------------------------------------------------------------
    init_script = """
window.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    deliveries.forEach(d => {
      d.submitted = isDeliveryChecked(d.detailKey);
      d.status = d.submitted ? 'Entregada por mí ✓' : '⏳ Pendiente de marcar';
    });
    if(typeof updateDeliveryCounts === 'function') updateDeliveryCounts();
    if(typeof renderHomePendingTasks === 'function') renderHomePendingTasks();
    if(typeof renderSidebarPendingItems === 'function') renderSidebarPendingItems();
    if(typeof renderDeliveries === 'function') renderDeliveries();
    if(typeof updateHomeGradesBadge === 'function') updateHomeGradesBadge();
    if(typeof renderMonth === 'function') renderMonth();
  }, 50);
});
"""
    html = html.replace('</script>', init_script + '\n</script>', 1)

    # -------------------------------------------------------------
    # 13. ASEGURAR HORARIO EXACTO DEL TURNO DE TARDE (16:30 — 20:45 h)
    # -------------------------------------------------------------
    html = re.sub(r'16:30\s*[—–-]\s*20:30\s*h', '16:30 — 20:45 h', html)
    html = re.sub(r'4:30\s*[—–-]\s*8:30', '4:30 a 20:45 h', html)

    return html

def build_student_portal():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(base_dir, 'index.html')
    out_path = os.path.join(base_dir, 'portal-estudiantes.html')
    alias_path = os.path.join(base_dir, 'estudiantes.html')

    if not os.path.exists(src_path):
        print(f"Error: {src_path} no encontrado.")
        sys.exit(1)

    with open(src_path, 'r', encoding='utf-8') as f:
        html = f.read()

    student_html = generate_student_portal_html(html)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(student_html)

    with open(alias_path, 'w', encoding='utf-8') as f:
        f.write(student_html)

    print(f"✅ ¡Portal de estudiantes generado con éxito en:\n   - {out_path}\n   - {alias_path}\n   ({len(student_html)} bytes)!")

if __name__ == '__main__':
    build_student_portal()

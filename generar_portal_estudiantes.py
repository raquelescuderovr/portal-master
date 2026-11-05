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

    # Badges de bienvenida: añadir insignia interactiva de Mi Cuaderno de Notas en welcome-badges-row
    html = re.sub(
        r'(<div class="welcome-badges-row">\s*<button class="welcome-badge badge-terra"[^>]*>.*?</button>)',
        r'''\1

        <button class="welcome-badge badge-mint" data-switch-view="notas" title="Mis notas y cuaderno personal de evaluación">
          <span class="badge-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          </span>
          <div class="badge-texts">
            <span class="badge-label">Evaluación continua</span>
            <strong class="badge-value" id="welcomeGradesSummary">Mi Cuaderno de Notas</strong>
          </div>
        </button>''',
        html,
        count=1,
        flags=re.DOTALL
    )

    # Neutralizar badge de Notas en el menú lateral y en las pestañas horizontales
    html = re.sub(
        r'(<button class="nav-btn-notas" data-view="notas">.*?<span class="nav-label-text">Notas y Tests</span>\s*)<span class="nav-badge-pill[^"]*">[^<]*</span>',
        r'\1<span class="nav-badge-pill badge-honey" id="sideNavGradesBadge">Mi Cuaderno</span>',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<button class="view-tab" data-view="notas" role="tab"[^>]*>Notas y Tests <span class="tab-badge">[^<]*</span></button>',
        '<button class="view-tab" data-view="notas" role="tab" aria-selected="false">Notas y Tests <span class="tab-badge" id="tabGradesBadge">0</span></button>',
        html
    )

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
                # Limpiar notas y calificaciones fijas de los eventos del calendario
                ev = re.sub(r"kind:\s*'Clase \+ (?:Pruebas|Nota|Test) \([^']*\)'", "kind:'Clase · Procura'", ev)
                ev = re.sub(r"mailKey:\s*'(?:grades|mail_deontologia_ana_vazquez|mail_carmen_belo_13oct)',?\s*", "", ev)
                ev = re.sub(r"detailKey:\s*'test_16oct',?\s*", "", ev)
                clean_evs.append(ev)
            if clean_evs:
                new_events_lines.append(f" '{day_str}':[\n   " + ",\n   ".join(clean_evs) + "\n  ]")
            else:
                new_events_lines.append(f" '{day_str}':[]")
        cleaned_events_code = ",\n".join(new_events_lines)
        html = html[:m_events.start(2)] + cleaned_events_code + html[m_events.end(2):]
        # Limpiar también cualquier tarjeta estática pre-renderizada de eventos personales en #todayList y #nextThreeDaysList
        html = re.sub(
            r'\s*<button class="headline-item"[^>]*>(?:(?!</button>).)*(?:Pilates|Personal · Google|ENTREGAD[OA])(?:(?!</button>).)*</button>',
            '',
            html,
            flags=re.DOTALL
        )
        html = re.sub(
            r'\s*<button class="next-day-card"[^>]*>(?:(?!</button>).)*(?:Pilates|Personal · Google|ENTREGAD[OA])(?:(?!</button>).)*</button>',
            '',
            html,
            flags=re.DOTALL
        )
        print("✓ Eventos personales filtrados.")

    # -------------------------------------------------------------
    # 3. FILTRAR MENSAJES (CORREO) - EXCLUIR NOTAS PERSONALES
    # -------------------------------------------------------------
    m_msg = re.search(r'(const messages\s*=\s*\[)(.*?)(\];\s*const)', html, re.DOTALL)
    if m_msg:
        excluded_keys = {
            'mail_carolina_carlos_23oct',
            'mail_carlos_sanchez_2oct',
            'mail_carmen_belo_13oct',
            'mail_digna_dataforum_26oct',
            'mail_acuse_mediacion_29oct',
            'mail_acuse_ficha_raquel_24sep',
            'test_20oct_sandra',
            'test_28oct_carnota',
            'test_29oct_susana',
            'test_30oct_susana',
            'test_2nov_carnota',
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
            if any(term in item_str for term in ['Nota:', 'Calificaciones oficiales', 'Resultados de las pruebas', 'Test online realizado', 'Calificación oficial', 'Acuse de recibo de entrega', 'Confirmación de recepción']):
                skip = True
            if not skip:
                # Limpiar referencias a Drive en el meta
                item_str = item_str.replace(' · subido a Drive y enviado en CPROC', ' · Caso práctico en CPROC')
                clean_msgs.append(item_str)
        
        new_messages_code = "\n " + ",\n ".join(clean_msgs) + "\n"
        html = html[:m_msg.start(2)] + new_messages_code + html[m_msg.end(2):]
        
        # Actualizar badge en pestaña Correo y menú lateral
        html = re.sub(
            r'<button class="view-tab" data-view="correo" role="tab"[^>]*>Correo <span class="tab-badge">\d+</span></button>',
            f'<button class="view-tab" data-view="correo" role="tab" aria-selected="false">Correo <span class="tab-badge">{len(clean_msgs)}</span></button>',
            html
        )
        html = re.sub(
            r'(<button class="nav-btn-correo" data-view="correo">.*?<span class="nav-badge-pill badge-peach">)\d+(</span>)',
            rf'\g<1>{len(clean_msgs)}\2',
            html,
            flags=re.DOTALL
        )
        print(f"✓ Buzón de correo filtrado: {len(clean_msgs)} comunicados académicos oficiales conservados (excluidas notas personales).")

    # -------------------------------------------------------------
    # 4. LIMPIAR OBJETO DETAILS Y MAILSUMMARIES (NOTAS PERSONALES Y CITAS MÉDICAS)
    # -------------------------------------------------------------
    # Limpiar claves de notas en mailSummaries
    for k in ['mail_carolina_carlos_23oct', 'mail_carlos_sanchez_2oct', 'mail_carmen_belo_13oct', 'mail_digna_dataforum_26oct', 'mail_acuse_mediacion_29oct', 'mail_acuse_ficha_raquel_24sep', 'mail_deontologia_ana_vazquez', 'grades', 'procura_resultados']:
        html = re.sub(rf'\s*{k}:\s*\'[^\']*?\',?', '', html)

    def remove_details_key(content: str, key: str) -> str:
        pattern = re.compile(rf'\s*{key}\s*:\s*\{{', re.DOTALL)
        m = pattern.search(content)
        if not m:
            return content
        start_pos = m.start()
        depth = 0
        in_string = None
        pos = m.end() - 1
        while pos < len(content):
            ch = content[pos]
            if in_string:
                if ch == '\\':
                    pos += 2
                    continue
                elif ch == in_string:
                    in_string = None
            else:
                if ch in ("'", '"', '`'):
                    in_string = ch
                elif ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        end_pos = pos + 1
                        if end_pos < len(content) and content[end_pos] == ',':
                            end_pos += 1
                        return content[:start_pos] + content[end_pos:]
            pos += 1
        return content

    # Conservamos todos los cuestionarios didácticos (test_16oct, test_20oct_sandra, test_28oct_carnota, test_29oct_susana, test_30oct_susana, test_2nov_carnota)
    for k in ['personal_calendar_sync', 'grades', 'mail_deontologia_ana_vazquez', 'mail_carlos_sanchez_2oct', 'mail_carolina_carlos_23oct', 'mail_carmen_belo_13oct', 'mail_digna_dataforum_26oct', 'mail_acuse_mediacion_29oct', 'mail_acuse_ficha_raquel_24sep', 'procura_resultados', 'all_tests_summary']:
        html = remove_details_key(html, k)

    # Neutralizar menciones a calificaciones personales en los detalles de los 6 tests oficiales
    html = re.sub(r"kicker:'Nota de Test:[^']*'", "kicker:'Cuestionario oficial de autoevaluación · Preguntas y respuestas'", html)
    html = re.sub(r"date:'Realizado:\s*([^'·]+)\s*·[^']*Calificación:[^']*'", r"date:'Sesión: \1 · Cuestionario oficial Testmoz'", html)
    html = html.replace(
        "Puntuación obtenida: 20 de 20 respuestas correctas (100 % · 10 sobre 10). Todos los tests del máster hasta la fecha están realizados (con un 10 en todos salvo en uno con ~8). Debajo tienes las 20 preguntas íntegras con sus cuatro opciones y la respuesta correcta marcada.",
        "Cuestionario de evaluación y preguntas oficiales resueltas. Debajo tienes las 20 preguntas íntegras con sus cuatro opciones y la respuesta correcta indicada."
    )
    html = re.sub(r"Puntuación obtenida(?: por Raquel Escudero)?:\s*[^.]*\.", "Cuestionario oficial resuelto con preguntas, opciones y fundamentos jurídicos.", html)
    html = html.replace("Usuario: raquel.escudero@udc.es", "Usuario: tu correo institucional (@udc.es)")
    print("✓ Claves de notas y eventos personales eliminados de details y mailSummaries (conservando los 6 tests oficiales).")

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

    # Reemplazo de variables de URL: desvincular Google Drive y redirigir a CPROC oficial
    html = re.sub(
        r"const driveFolderUrl\s*=\s*'[^']*';",
        "const driveFolderUrl='https://www.icpcoruna.com/copia-de-entrega-de-tareas';",
        html
    )
    html = re.sub(
        r"const practicasGdriveUrl\s*=\s*'[^']*';",
        "const practicasGdriveUrl='https://www.icpcoruna.com/copia-de-entrega-de-tareas';",
        html
    )
    html = re.sub(
        r"const driveSearchUrl\s*=\s*[^;]+;",
        "const driveSearchUrl=()=>'https://www.icpcoruna.com/copia-de-entrega-de-tareas';",
        html
    )

    # Eliminar enlaces web específicos a Google Docs y Google Drive
    html = re.sub(r"https://drive\.google\.com/file/d/[a-zA-Z0-9_\-]+/view(?:\?[^\s\'\"]*)?", "https://www.icpcoruna.com/copia-de-entrega-de-tareas", html)
    html = re.sub(r"https://drive\.google\.com/drive/u/\d+/(?:folders|search)[^\s\'\"]*", "https://www.icpcoruna.com/copia-de-entrega-de-tareas", html)
    html = re.sub(r"https://docs\.google\.com/document/d/[a-zA-Z0-9_\-]+/edit(?:\?[^\s\'\"]*)?", "https://www.icpcoruna.com/copia-de-entrega-de-tareas", html)

    # Quitar el botón de carpeta de Drive de las tarjetas de profesorado
    html = re.sub(
        r'\$\{\(t\.driveFiles\|\|\[\]\)\[0\]\?`<a class="pill-link terra" href="\$\{t\.driveFiles\[0\]\.url\}" target="_blank" rel="noopener noreferrer">📁 Drive ↗</a>`:?\'\'\}',
        '',
        html
    )
    html = html.replace("${(t.driveFiles||[])[0]?`<a class=\"pill-link terra\" href=\"${t.driveFiles[0].url}\" target=\"_blank\" rel=\"noopener noreferrer\">📁 Drive ↗</a>`:''}", "")

    # Eliminar enlaces y textos a Drive en modales de profesorado y paneles de apuntes
    html = html.replace('<a class="pill-link solid-green" href="${driveFolderUrl}" target="_blank" rel="noopener noreferrer">Carpeta Drive del Máster ↗</a>', '<a class="pill-link solid-green" href="${cprocUrl}" target="_blank" rel="noopener noreferrer">Campus CPROC ↗</a>')
    html = html.replace('<div class="visual-resource-sub">Google Drive · Documento de estudio</div>', '<div class="visual-resource-sub">Material de estudio · CPROC</div>')
    html = html.replace('<a class="pill-link solid-green" href="${d.url}" target="_blank" rel="noopener noreferrer">Abrir archivo en Drive ↗</a>', '<a class="pill-link solid-green" href="${d.url}" target="_blank" rel="noopener noreferrer">Abrir documento ↗</a>')
    html = html.replace('<p style="margin-bottom:14px">Puedes consultar la carpeta compartida en Google Drive donde se alojan los materiales de todas las asignaturas.</p>', '<p style="margin-bottom:14px">Puedes consultar las guías didácticas y materiales docentes oficiales en la plataforma CPROC.</p>')
    html = html.replace('<a class="cozy-btn cozy-btn-mint" href="${driveFolderUrl}" target="_blank" rel="noopener noreferrer">Abrir Carpeta Google Drive ↗</a>', '<a class="cozy-btn cozy-btn-mint" href="${cprocUrl}" target="_blank" rel="noopener noreferrer">Acceder a Campus CPROC ↗</a>')
    html = html.replace('<a class="st-sec-link" href="${driveFolderUrl}" target="_blank" rel="noopener noreferrer">Drive ↗</a>', '<a class="st-sec-link" href="${cprocUrl}" target="_blank" rel="noopener noreferrer">CPROC ↗</a>')
    html = html.replace('Clases, apuntes en Drive, prácticas, correos y notas del docente:', 'Clases, materiales de estudio, prácticas, correos y notas del docente:')

    # Tarjeta de Portada (Home Hub Card) para sustituir el bloque de Google Drive por CPROC oficial
    html = html.replace('<span class="hub-card-kicker">Google Drive</span>', '<span class="hub-card-kicker">Plataforma CPROC</span>')
    html = html.replace('<strong class="hub-card-title">Carpeta «Máster»</strong>', '<strong class="hub-card-title">Tareas y Entregas</strong>')
    html = html.replace('<span class="hub-card-meta">Apuntes, guías y casos en PDF</span>', '<span class="hub-card-meta">Campus oficial de Procura</span>')

    # Banner de Materiales (sección 6) para reemplazar la caja de Google Drive
    html = html.replace('<!-- 6. APUNTES, DOCUMENTOS Y GOOGLE DRIVE -->', '<!-- 6. APUNTES, DOCUMENTOS Y RECURSOS ACADÉMICOS -->')
    html = html.replace('<h2>Apuntes, documentos por asignatura y Google Drive</h2>', '<h2>Apuntes, documentos por asignatura y materiales oficiales</h2>')
    html = html.replace('<strong>Carpeta «Máster» en Google Drive</strong>', '<strong>Materiales docentes y plataforma CPROC</strong>')
    html = re.sub(
        r'Repositorio[^<]*localizarlo en Drive\.',
        'Repositorio de guías didácticas, resoluciones y recursos de estudio oficiales del Máster Universitario en Abogacía y Procura.',
        html,
        flags=re.IGNORECASE
    )
    html = html.replace('Abrir carpeta Máster en Drive ↗', 'Acceder a Tareas y Materiales CPROC ↗')

    # Enlaces de la barra superior y accesos
    html = html.replace('>Drive ↗</a>', '>CPROC Tareas ↗</a>')
    html = re.sub(
        r'<a href="[^"]*" target="_blank" rel="noopener noreferrer">Drive ↗</a>',
        '<a href="https://www.icpcoruna.com/copia-de-entrega-de-tareas" target="_blank" rel="noopener noreferrer">CPROC Tareas ↗</a>',
        html
    )

    # Lista exhaustiva de reemplazos de textos y etiquetas relacionados con Google Drive
    drive_replacements = [
        # Enlaces, botones y modales
        ('Abrir en Drive ↗', 'Plataforma CPROC ↗'),
        ('PDF Drive ↗', 'Documento oficial ↗'),
        ('Carpeta Drive ↗', 'CPROC Tareas ↗'),
        ('Buscar en Drive ↗', 'Normativa y CPROC ↗'),
        ('y conservado en Google Drive.', '.'),
        ('y conservado en Google Drive', ''),
        ('en Google Drive', ''),
        ('// Collect Drive docs & notes:', '// Collect official docs & notes:'),
        ('Google Docs ↗', 'CPROC ↗'),
        ('Borrador en Drive ↗', 'Plataforma CPROC ↗'),
        ('Google Docs (Entrega) ↗', 'Enunciado oficial ↗'),
        ('Vídeo comprobante CPROC ↗', 'Plataforma CPROC ↗'),
        ('Resolución completa (.md) ↗', 'Instrucciones del caso ↗'),
        ('Carpeta Prácticas Drive ↗', 'CPROC Tareas ↗'),
        ('Apuntes y Drive', 'Materiales y Normativa'),
        ('Ver en Drive ↗', 'Consultar en CPROC ↗'),
        ('En Drive ↗', 'Campus CPROC ↗'),
        ('Ver apuntes en Drive', 'Ver apuntes de clase'),
        ('Ver apuntes y prácticas en Drive', 'Ver materiales y prácticas'),
        ('Proceso digital, TIC y Prácticas procesales en Drive', 'Proceso digital, TIC y Prácticas procesales'),
        ('📁 Explorar apuntes en Drive ↗', '📚 Explorar materiales y apuntes ↗'),
        ('Puedes consultar los apuntes en Drive, revisar las notas o explorar las próximas asignaturas.', 'Puedes consultar los materiales en CPROC, revisar tus notas o explorar las próximas asignaturas.'),
        ('(4 docs en Drive)', '(4 documentos de estudio)'),
        ('(Acceso directo a Drive / Documento)', '(Acceso a documento CPROC)'),
        ("badge: 'Apunte / Drive'", "badge: 'Apunte / Material'"),
        ("badge:'Apunte / Drive'", "badge:'Apunte / Material'"),
        ("materiales:'Apuntes y Drive'", "materiales:'Materiales y Normativa'"),
        ("renderGroup('Apuntes y Drive'", "renderGroup('Materiales y Normativa'"),
        ("label: n.label || 'Abrir en Drive ↗'", "label: n.label || 'Consultar documento ↗'"),
        ("${d.label || 'Abrir en Drive ↗'}", "${d.label || 'Consultar documento ↗'}"),
        ("Abrir ${d.file} en Drive ↗", "Abrir ${d.file} en CPROC ↗"),
        ("Abrir ${d.file2} en Drive ↗", "Abrir ${d.file2} en CPROC ↗"),

        # Calificadores en nombres de archivos
        ('(Doc Google en Drive)', '(Doc Google)'),
        ('(PDF en Drive)', '(Documento oficial)'),
        ('(Documento en Drive)', '(Documento oficial)'),
        ('(Doc Google editable en Drive)', '(Plantilla editable CPROC)'),
        ('(Resumen procesal en Drive)', '(Resumen procesal)'),
        ('(Poder apud acta en Drive)', '(Poder apud acta oficial)'),
        ('(Práctica en Drive)', '(Práctica CPROC)'),
        ('2/10_Práctica_Raquel Escudero .pdf (Práctica en Drive)', 'Práctica 2 de octubre (CPROC)'),
        ('2/10_Práctica_Raquel Escudero .pdf', 'Práctica 2 de octubre'),
        ('Raquel Escudero_Derechos y deberes procuradores y responsabilidad profesional (Doc Google)', 'Caso práctico: Derechos, deberes y responsabilidad profesional (CPROC)'),
        ('Raquel Escudero_Derechos y deberes procuradores (Doc Google)', 'Caso práctico de Deontología (CPROC)'),
        ('RESOLUCIÓN ÍNTEGRA DEL CASO PRÁCTICO — SANDRA MOSTEIRO COSTA\\nEstudiante: Raquel Escudero Valcárcel-Ríos', 'RESOLUCIÓN ÍNTEGRA DEL CASO PRÁCTICO — SANDRA MOSTEIRO COSTA\\nCaso práctico oficial evaluable'),
        ('(Drive)', '(CPROC)'),
        ('Carpeta «Máster apuntes» en Google Drive', 'Materiales y apuntes en CPROC'),
        ('Carpeta «Máster apuntes» en Drive', 'Materiales y apuntes en CPROC'),
        ('Carpeta general Máster en Google Drive', 'Campus Virtual CPROC (MUAP)'),
        ('Guardado en Google Drive', 'Documento oficial CPROC'),
        ('y carpeta «Máster» en Google Drive', ''),
        (', subida a la carpeta «Máster» de Google Drive', ''),
        (', subida a la carpeta «Máster» en Google Drive', ''),
        (', subida a Google Drive', ''),
        ('subida a Google Drive y ', ''),
        ('subida a la carpeta «Máster» de Google Drive y ', ''),
        ('subida a Google Drive', ''),
        ('carpeta «Máster» de Google Drive', 'plataforma CPROC'),
        ('carpeta «Máster» en Google Drive', 'plataforma CPROC'),
        ('Práctica resuelta en carpeta «Máster» de Google Drive', 'Práctica oficial en plataforma CPROC'),
        ('Abrir carpeta Prácticas en Google Drive', 'Campus Virtual CPROC (MUAP)'),
        ("kind:'Carpeta Drive'", "kind:'Plataforma CPROC'"),
        ("kind:'Google Drive ↗'", "kind:'CPROC ↗'"),
        ("kind:'Buscar en Drive'", "kind:'Consultar normativa'"),
        ("kind:'Archivo en Drive'", "kind:'Documento CPROC'"),
        ('CertificadoRegistro.pdf (Abrir en Google Drive)', 'CertificadoRegistro.pdf (Poder apud acta oficial)'),
        ('Escrito de subsanación_signed.pdf (Abrir en Google Drive)', 'Escrito de subsanación (Plantilla procesal)'),
        ('Documento_anonimizado.pdf (11 págs. · Abrir en Drive)', 'Documento_anonimizado.pdf (Auto concursal UP · 11 págs.)'),
        ('summary.docx (1 pág. · Abrir en Drive)', 'summary.docx (Resumen concursal)'),
        ('Word Drive ↗', 'Word CPROC ↗'),
        ("urlLabel:'Drive ↗'", "urlLabel:'CPROC ↗'"),
        ("label:'Drive ↗'", "label:'CPROC ↗'"),
        ('Documento sin título (Apuntes complementarios en Drive)', 'Apuntes complementarios de deontología'),
        ('Deontología abogacía (Google Docs en Drive)', 'Deontología de la abogacía (Apuntes)'),
        ('Jurisprudencia sobre responsabilidad civil del abogado (CPROC)', 'Jurisprudencia sobre responsabilidad civil del abogado'),
        ('Jurisprudencia sobre responsabilidad civil del abogado (Drive)', 'Jurisprudencia sobre responsabilidad civil del abogado'),
        ('Archivo en Drive', 'Archivo CPROC'),
        ("{name:'Grabación de pantalla de la entrega (vídeo .mov)',url:casoSandraVideoLocalUrl,label:'Vídeo ↗'},", ""),

        # Comentarios CSS
        ("/* 4. Google Drive */", "/* 4. Plataforma CPROC */"),
        ("/* 3. Google Drive: Menta / Laurel Suave */", "/* 3. Recursos y Materiales */"),
        ("Google Drive y Apuntes", "Recursos y Apuntes"),
        ("Correos, Drive, Tests", "Correos y Tests"),
        ("Correos, Drive", "Correos"),
    ]
    for old_val, new_val in drive_replacements:
        html = html.replace(old_val, new_val)

    # Limpiar entradas residuales en teacherDirectory de Alex Sánchez y Daniel Garrido
    html = html.replace("driveFiles:[{name:'Carpeta «Máster apuntes» en Google Drive',url:'https://www.icpcoruna.com/copia-de-entrega-de-tareas',label:'Carpeta Drive ↗'}]", "driveFiles:[]")
    html = html.replace("driveFiles:[{name:'2/10_Práctica_Raquel Escudero .pdf (Práctica en Drive)',url:'https://www.icpcoruna.com/copia-de-entrega-de-tareas'}]", "driveFiles:[]")

    print("✓ Enlaces privados a Google Drive y Docs desvinculados por completo.")

    # -------------------------------------------------------------
    # 6. LIMPIAR NOTAS FIJAS EN courses = [...], teacherDirectory Y gradeRecords
    # -------------------------------------------------------------
    # Reemplazar calificaciones fijas en asignaturas por evaluación continua
    html = re.sub(
        r"grade:\s*\{score:'[^']*(?:Sobresaliente|Notable|aciertos|★|Oficial|Media|\d+\s*/\s*10|Práctica entregada)[^']*',[^}]*\},?",
        "grade:{score:'Evaluación continua',scoreLabel:'Evaluación del módulo',detail:'Ponderación oficial: 40% Cuestionario tipo test + 60% Trabajos y casos prácticos.',detailKey:'dossiers'},",
        html
    )
    # Neutralizar insignias y notas individuales en teacherDirectory
    html = re.sub(r"gradeBadge:\s*'[^']*(?:★|Oficial|Sobresaliente|Notable|aciertos|Testmoz|\d+\s*/\s*10)[^']*'", "gradeBadge:'⚖️ Evaluación continua'", html)
    html = re.sub(r"gradeScore:\s*'[^']*(?:Sobresaliente|Notable|\d+\s*/\s*10)[^']*'", "gradeScore:'Evaluación continua'", html)
    html = re.sub(r"gradeDetail:\s*'Calificación oficial registrada:[^']*'", "gradeDetail:'Ponderación oficial de evaluación continua (test + trabajos de CPROC).'", html)
    html = re.sub(r"\s*·\s*Calificación oficial:\s*[^'\"<\n]+", "", html)
    html = re.sub(r"\s*·\s*Test:\s*[^'\"<\n]+", "", html)
    html = html.replace(' · Práctica entregada en CPROC', '')

    # Neutralizar objetos grade:{...} en teacherDirectory que tenían notas de Raquel
    html = re.sub(
        r"grade:\{score:'(?:10 / 10|8\.8 / 10|7\.6 / 10|Nota oficial:|Test:|Tests:|Doble 10|🟢 Práctica entregada)[^']*',[^}]*\},?",
        "grade:{score:'Evaluación continua',scoreLabel:'Cuaderno de evaluación',detail:'Registra aquí tu calificación de test, casos prácticos y nota conjunta del módulo.',detailKey:'dossiers'},",
        html
    )
    # Eliminar breakdown personal de Carmen Belo en teacherDirectory
    html = re.sub(r"breakdown:\[\s*\{label:'I\. Test \(40 %\)',val:'3,4 / 4 puntos[^\]]*\],?", "", html)

    # Limpiar notas específicas en materials / notes de courses
    html = re.sub(r"\s*\{name:'Calificaciones oficiales Carlos Miguel Sánchez Muiño[^']*'[^}]*\},?", "", html)
    html = re.sub(r"\s*\{name:'Tabla oficial de calificaciones[^']*'[^}]*\},?", "", html)
    html = re.sub(r"\s*\{name:'Calificaciones oficiales[^']*'[^}]*\},?", "", html)
    html = re.sub(r"\s*\{name:'Comprobante de entrega: Grabación de pantalla[^']*'[^}]*\},?", "", html)
    html = re.sub(r"\s*\{name:'Grabación entrega en CEPROC:[^']*'[^}]*\},?", "", html)
    html = html.replace("Plataforma CPROC: Tareas publicadas (Entregada 22 oct ✓)", "Plataforma CPROC: Tareas publicadas")
    html = html.replace("CPROC: Tareas publicadas (Entregada 22 oct ✓)", "CPROC: Tareas publicadas")

    # Limpiar mails y practices en teacherDirectory de todos los profesores con notas personales
    html = html.replace(
        "mails:[{title:'Calificación pruebas 14-16 oct con Carolina Moreno (10/10 · 23 oct)',key:'mail_carolina_carlos_23oct'},{title:'Calificación pruebas 2 oct (10/10 · 22 oct)',key:'mail_carlos_sanchez_2oct'},{title:'Calificaciones oficiales Procura (14 oct)',key:'grades'},{title:'Materiales TIC y justicia digital (15 oct)',key:'materials'}]",
        "mails:[{title:'Materiales TIC y justicia digital (15 oct)',key:'materials'}]"
    )
    html = html.replace(
        "{title:'Pruebas evaluables del 14-16 oct con Carolina Moreno (Test 4 + Escritos 6)',status:'10 / 10 (Sobresaliente) ✓',key:'mail_carolina_carlos_23oct'},",
        ""
    )
    html = html.replace(
        "{title:'Pruebas evaluables del 2 oct (Test 4 + Escritos 6)',status:'10 / 10 (Sobresaliente) ✓',key:'mail_carlos_sanchez_2oct'},",
        ""
    )
    html = html.replace(
        "{title:'Test online de justicia digital (20/20 aciertos)',status:'10 / 10 ✓',key:'test_16oct'}",
        "{title:'Test online de justicia digital (20 preguntas)',status:'Cuestionario oficial',key:'test_16oct'}"
    )
    html = html.replace(
        "{title:'Escrito de subsanación procesal telemática',status:'Enviado en CPROC ✓',key:'entrega_subsanacion'}",
        "{title:'Escrito de subsanación procesal telemática',status:'⏳ Pendiente de marcar',key:'entrega_subsanacion'}"
    )

    # Limpiar Carolina Moreno
    html = html.replace(
        "{title:'Calificaciones oficiales · Deontología y TIC (Nota: 10 / 10 · 23 oct)',key:'mail_carolina_carlos_23oct'},",
        ""
    )
    html = html.replace(
        "{title:'Pruebas evaluables del 14-16 oct (Test 4 + Escritos 6)',status:'10 / 10 (Sobresaliente) ✓',key:'mail_carolina_carlos_23oct'},",
        ""
    )
    html = html.replace(
        "{title:'Test online de justicia digital (20/20 aciertos)',status:'10 / 10 (100 %) ✓',key:'test_16oct'},",
        "{title:'Test online de justicia digital (20 preguntas)',status:'Cuestionario oficial',key:'test_16oct'},"
    )
    html = html.replace(
        "{title:'Subsanación de defecto procesal telemático',status:'Enviado en CPROC ✓',key:'entrega_subsanacion'},",
        "{title:'Subsanación de defecto procesal telemático',status:'⏳ Pendiente de marcar',key:'entrega_subsanacion'},"
    )
    html = html.replace(
        "{title:'Caso práctico Auto Concursal UP',status:'Enviado en CPROC ✓',key:'entrega_auto_up'}",
        "{title:'Caso práctico Auto Concursal UP',status:'⏳ Pendiente de marcar',key:'entrega_auto_up'}"
    )

    # Limpiar Javier Sánchez García, Carmen Belo, Sandra Mosteiro, María Carnota, Susana Díaz, Delgado, Moure
    html = html.replace("{title:'Calificaciones oficiales Procura',key:'grades'},", "")
    html = html.replace("{title:'Calificaciones oficiales Procura',key:'grades'}", "")
    html = html.replace("{title:'Cuestionario y caso práctico de iniciación profesional',status:'Calificación: 10/10 ✓',key:'grades'}", "{title:'Cuestionario y caso práctico de iniciación profesional',status:'Evaluación continua',key:''}")
    html = html.replace("{title:'Resultados pruebas 13/10/2026 (Nota: 7.6 / 10)',key:'mail_carmen_belo_13oct'}", "{title:'Carta de presentación MUAP 2026-2027 (8 oct)',key:'mail_carmen_belo_carta_08oct'}")
    html = html.replace("{title:'Actividades evaluables (Test + Trabajos: 7.6 / 10)',status:'Superado ✓',key:'mail_carmen_belo_13oct'}", "{title:'Actividades evaluables de Responsabilidad Disciplinaria (Test 40% + Trabajos 60%)',status:'Evaluación continua',key:'mail_carmen_belo_carta_08oct'}")
    html = html.replace("{title:'Test online de actos de comunicación (20 oct · 9/10)',key:'test_20oct_sandra'}", "{title:'Test online de actos de comunicación (20 oct)',key:'test_20oct_sandra'}")
    html = html.replace("{title:'Caso práctico 2026: Actos de comunicación judicial',status:'Completada y entregada en CPROC (22 oct) ✓',key:'entrega_caso_pr_ctico_de_actos_de'}", "{title:'Caso práctico 2026: Actos de comunicación judicial',status:'⏳ Pendiente de marcar',key:'entrega_caso_pr_ctico_de_actos_de'}")
    html = html.replace("{title:'Test online: Actos de comunicación judicial (9/10)',status:'Superado (9/10 · 90 %) ✓',key:'test_20oct_sandra'}", "{title:'Test online: Actos de comunicación judicial (10 preguntas)',status:'Cuestionario oficial',key:'test_20oct_sandra'}")
    html = html.replace("{title:'Práctica procesal de subsanación telemática',status:'Completada ✓',key:'entrega_subsanacion'}", "{title:'Práctica procesal de subsanación telemática',status:'⏳ Pendiente de marcar',key:'entrega_subsanacion'}")
    html = html.replace("{title:'Caso práctico: Turno de Oficio y Responsabilidad Civil Profesional (Parte A y Parte B)',status:'Entregada por correo electrónico ✓ (27 oct 2026, mañana)',key:'entrega_delgado'}", "{title:'Caso práctico: Turno de Oficio y Responsabilidad Civil Profesional (Parte A y Parte B)',status:'⏳ Pendiente de marcar',key:'entrega_delgado'}")
    html = html.replace("{title:'Test online realizado: Recursos, ejecución y costas (2 nov · 10/10 ★)',key:'test_2nov_carnota'}", "{title:'Test online: Recursos, ejecución y costas (2 nov)',key:'test_2nov_carnota'}")
    html = html.replace("{title:'Test online Testmoz Sesión 2: Recursos, ejecución, costas y nulidad (10/10 aciertos)',status:'10 / 10 ★ (Sobresaliente pleno)',key:'test_2nov_carnota'}", "{title:'Test online Testmoz Sesión 2: Recursos, ejecución, costas y nulidad (10 preguntas)',status:'Cuestionario oficial',key:'test_2nov_carnota'}")
    html = html.replace("{title:'Test online Testmoz Sesión 1: Registros, notarías y administraciones (10/10 aciertos)',status:'10 / 10 ★ (Sobresaliente)',key:'test_28oct_carnota'}", "{title:'Test online Testmoz Sesión 1: Registros, notarías y administraciones (10 preguntas)',status:'Cuestionario oficial',key:'test_28oct_carnota'}")
    html = html.replace("{title:'Test online Testmoz (Sesión 2): Medidas cautelares y tutela judicial (10/10 aciertos)',status:'10 / 10 ★ (Sobresaliente pleno)',key:'test_30oct_susana'}", "{title:'Test online Testmoz (Sesión 2): Medidas cautelares y tutela judicial (10 preguntas)',status:'Cuestionario oficial',key:'test_30oct_susana'}")
    html = html.replace("{title:'Test online Testmoz (Sesión 1): Procesos declarativos de la Procura (9/10 aciertos)',status:'9 / 10 (Sobresaliente)',key:'test_29oct_susana'}", "{title:'Test online Testmoz (Sesión 1): Procesos declarativos de la Procura (10 preguntas)',status:'Cuestionario oficial',key:'test_29oct_susana'}")
    html = html.replace("{title:'Tarea: CASOS PRÁCTICOS DIA 30_10_2026 (Proceso Cautelar)',status:'Entregada en CPROC ✓ (30 oct 20:08 h)',key:'entrega_susana_diaz_casos_30oct'}", "{title:'Tarea: CASOS PRÁCTICOS DIA 30_10_2026 (Proceso Cautelar)',status:'⏳ Pendiente de marcar',key:'entrega_susana_diaz_casos_30oct'}")
    html = html.replace("{title:'Tarea: REDACCION ESCRITOS DE SUBSANACION 29/10/2026',status:'Entregada en CPROC ✓ (30 oct)',key:'entrega_susana_diaz_subsanacion'}", "{title:'Tarea: REDACCION ESCRITOS DE SUBSANACION 29/10/2026',status:'⏳ Pendiente de marcar',key:'entrega_susana_diaz_subsanacion'}")
    html = html.replace("Plenos absolutos en ambos tests de clase (10/10 el 28 oct y 10/10 el 2 nov).", "Incluye 2 cuestionarios oficiales tipo test (28 oct y 2 nov).")
    html = html.replace("Ambas sesiones superadas con 9/10 y 10/10 en los tests de clase.", "Incluye 2 cuestionarios oficiales tipo test (29 y 30 oct) y 2 casos prácticos en CPROC.")
    html = html.replace("Módulo finalizado con test oficial superado (9/10). Calificación final global pendiente de remitir por correo.", "Incluye cuestionario tipo test oficial y caso práctico de 6 escenarios LEC.")
    html = html.replace("Práctica de MASC de demanda de divorcio entregada.", "Incluye práctica de MASC de demanda de divorcio.")
    html = re.sub(r"\((?:10/10|9/10|20/20) aciertos · HTML original\)", "(HTML original Testmoz)", html)
    html = html.replace("Revisión oficial Testmoz (9/10 · HTML conservado)", "Revisión oficial Testmoz (HTML conservado)")

    # Neutralizar gradeRecords: conservar los 6 cuestionarios tipo test (type:'test') y limpiar las notas personales de Raquel
    m_gr = re.search(r'(const gradeRecords\s*=\s*\[)(.*?)(\];\s*const)', html, re.DOTALL)
    if m_gr:
        raw_gr = m_gr.group(2)
        def extract_objects(s):
            res = []
            idx = 0
            while idx < len(s):
                start = s.find('{', idx)
                if start == -1:
                    break
                depth = 0
                in_string = None
                pos = start
                while pos < len(s):
                    ch = s[pos]
                    if in_string:
                        if ch == '\\':
                            pos += 2
                            continue
                        elif ch == in_string:
                            in_string = None
                    else:
                        if ch in ("'", '"', '`'):
                            in_string = ch
                        elif ch == '{':
                            depth += 1
                        elif ch == '}':
                            depth -= 1
                            if depth == 0:
                                res.append(s[start:pos+1])
                                idx = pos + 1
                                break
                    pos += 1
                else:
                    break
            return res

        clean_gr = []
        for item_str in extract_objects(raw_gr):
            if "type:'test'" in item_str:
                item_str = re.sub(r"score:'[^']*'", "score:'Cuestionario oficial'", item_str)
                item_str = re.sub(r"scoreLabel:'[^']*'", "scoreLabel:'Preguntas y soluciones'", item_str)
                item_str = re.sub(r"\{label:'Respuestas correctas',val:'[^']*'\}", "{label:'Formato',val:'Cuestionario oficial resuelto'}", item_str)
                item_str = re.sub(r"\{label:'Calificación',val:'[^']*'\}", "{label:'Evaluación',val:'Autoevaluación en tu cuaderno'}", item_str)
                item_str = re.sub(r"\s*por Raquel Escudero", "", item_str)
                item_str = re.sub(r"Superado con [^.]*\.", "Incluye todas las preguntas oficiales y sus respuestas.", item_str)
                item_str = re.sub(r"\(10/10\)|\(con fallo analizado\)", "", item_str)
                clean_gr.append(item_str)
        html = html[:m_gr.start(2)] + "\n " + ",\n ".join(clean_gr) + "\n" + html[m_gr.end(2):]

    # Vaciar teacherGradeMap por completo para que ningún docente tenga nota fija por defecto
    html = re.sub(
        r'const teacherGradeMap\s*=\s*\{.*?\};',
        'const teacherGradeMap = {};',
        html,
        flags=re.DOTALL
    )

    # Limpiar nota fija de Ana Vázquez en courses
    html = re.sub(
        r"grade:\s*\{score:'8\.8\s*/\s*10[^']*'[^}]*\},?",
        "grade:{score:'Evaluación continua',scoreLabel:'Evaluación del módulo',detail:'Ponderación oficial: 40% Cuestionario tipo test + 60% Trabajos y casos prácticos.',detailKey:'dossiers'},",
        html
    )

    # Reemplazar las 4 tarjetas superiores de estadísticas en #gradesSection con IDs dinámicos
    html = re.sub(
        r'<button class="stat-card" data-grade-filter="teachers"[^>]*>.*?</button>',
        '''<button class="stat-card" data-grade-filter="teachers" title="Ver expedientes agrupados por profesor">
        <div>
          <span class="stat-kicker">Expediente docente</span>
          <span class="stat-title" id="statTeachersTitle">14 módulos y profesores evaluables</span>
        </div>
        <span class="stat-val-pill" id="statTeachersPill">Mi Cuaderno</span>
      </button>''',
        html,
        flags=re.DOTALL
    )

    html = re.sub(
        r'<button class="stat-card" data-grade-filter="mail"[^>]*>.*?</button>',
        '''<button class="stat-card" data-grade-filter="mail" title="Ver calificaciones conjuntas de docentes">
        <div>
          <span class="stat-kicker">Notas conjuntas de profesores</span>
          <span class="stat-title" id="statMailTitle">Ponderación oficial por docente (test + casos prácticos)</span>
        </div>
        <span class="stat-val-pill" id="statMailPill">Por rellenar</span>
      </button>''',
        html,
        flags=re.DOTALL
    )

    html = re.sub(
        r'<button class="stat-card highlight-test" data-grade-filter="test"[^>]*>.*?</button>',
        '''<button class="stat-card highlight-test" data-grade-filter="test" title="Ver cuestionarios tipo test">
        <div>
          <span class="stat-kicker">Tests online de clase</span>
          <span class="stat-title" id="statTestTitle">6 cuestionarios oficiales disponibles con soluciones</span>
        </div>
        <span class="stat-val-pill" id="statTestPill">6 tests</span>
      </button>''',
        html,
        flags=re.DOTALL
    )

    html = re.sub(
        r'<button class="stat-card" data-grade-filter="practices"[^>]*>.*?</button>',
        '''<button class="stat-card" data-grade-filter="practices" title="Ver solo casos prácticos y entregas">
        <div>
          <span class="stat-kicker">Casos prácticos y trabajos</span>
          <span class="stat-title" id="statPracticesTitle">Seguimiento de entregas y notas de prácticas</span>
        </div>
        <span class="stat-val-pill" id="statPracticesPill">60% de nota</span>
      </button>''',
        html,
        flags=re.DOTALL
    )

    # Reemplazar textos estáticos con notas de ejemplo/reales en la sección de notas
    html = html.replace(
        '<p>Notas oficiales por correo de profesores (10/10 con Javier Sánchez y 8.8 con Ana Vázquez) y tests online de clase (20/20 con Carolina Moreno y 9/10 con Sandra Mosteiro).</p>',
        '<p>Cuaderno personal de evaluación continua: anota tus calificaciones de tests, prácticas, notas de profesores y observaciones de cada módulo.</p>'
    )
    html = html.replace(
        '(ej. <strong>Javier Sánchez 10/10</strong> y <strong>Ana Vázquez 8.8/10</strong>)',
        '(ponderación oficial: 40% examen o test + 60% trabajos prácticos y escritos)'
    )
    html = html.replace(
        '(ej. <strong>20/20 con Carolina Moreno</strong> el 16 oct y <strong>9/10 con Sandra Mosteiro</strong> el 20 oct)',
        '(cuestionarios tipo test realizados en clase o mediante la plataforma CPROC)'
    )

    # Reemplazar accesos rápidos en la portada (home hub cards de Notas y Entregas)
    html = re.sub(
        r'<button class="home-hub-card hub-honey"[^>]*>.*?</button>',
        '''<button class="home-hub-card hub-honey" data-switch-view="notas">
        <div class="hub-card-icon honey">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        </div>
        <div class="hub-card-text">
          <span class="hub-card-kicker">Evaluación continua</span>
          <strong class="hub-card-title" id="homeHubGradesTitle">Cuaderno de Notas</strong>
          <span class="hub-card-meta" id="homeHubGradesMeta">Anota tus calificaciones de tests y docentes</span>
        </div>
        <span class="hub-card-arrow">↗</span>
      </button>''',
        html,
        flags=re.DOTALL
    )

    html = re.sub(
        r'<button class="home-hub-card hub-terra"[^>]*>.*?</button>',
        '''<button class="home-hub-card hub-terra" data-switch-view="entregas">
        <div class="hub-card-icon terra">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
        </div>
        <div class="hub-card-text">
          <span class="hub-card-kicker">Tareas y Prácticas</span>
          <strong class="hub-card-title" id="homeHubPendingTitle">Control de Prácticas</strong>
          <span class="hub-card-meta" id="homeHubPendingMeta">Marca tus entregas completadas y pendientes</span>
        </div>
        <span class="hub-card-arrow">↗</span>
      </button>''',
        html,
        flags=re.DOTALL
    )

    # Reemplazar textos en renderDay() y resúmenes de filtros
    html = html.replace(
        '⭐ Ver notas y tests (10/10) →',
        '⭐ Ver cuaderno de notas y tests →'
    )
    html = html.replace(
        "sumEl.textContent = 'Mostrando solo calificaciones conjuntas oficiales comunicadas formalmente por correo electrónico (Javier Sánchez 10/10 y Ana Vázquez 8.8/10).';",
        "sumEl.textContent = 'Mostrando expedientes docentes para registrar la calificación oficial conjunta comunicada por correo.';"
    )
    html = html.replace(
        "sumEl.textContent = 'Mostrando exclusivamente tests online realizados en clase (16 oct: 20/20 y 20 oct: 9/10), con desglose interactivo de preguntas y respuestas.';",
        "sumEl.textContent = 'Mostrando cuestionarios tipo test de evaluación continua con preguntas, soluciones y casilla para tu nota.';"
    )

    # Limpiar referencias a notas personales en teacherDirectory
    html = html.replace(
        "{title:'Calificaciones oficiales de Deontología (19 oct · Nota: 8.8)',key:'mail_deontologia_ana_vazquez'},",
        ""
    )
    html = html.replace(
        "status:'Calificación: 5.0 / 6 (Trabajos) ✓',key:'mail_deontologia_ana_vazquez'",
        "status:'⏳ Pendiente de marcar',key:'assignment'"
    )

    # Neutralizar portal de estudiantes con bandera estricta
    html = html.replace('const isStudentPortal = false;', 'const isStudentPortal = true;')

    print("✓ Notas fijas de asignaturas, profesorado y expedientes convertidas en evaluación continua neutral.")

    # -------------------------------------------------------------
    # 7. ENTREGAS: INICIO A CERO Y CHECKBOXES INTERACTIVOS
    # -------------------------------------------------------------
    m_del = re.search(r'(const deliveries\s*=\s*\[)(.*?)(\];\s*const)', html, re.DOTALL)
    if m_del:
        del_content = m_del.group(2)
        # 1) Excluir el registro de notas de Carolina y Carlos si existiera
        del_content = re.sub(
            r'\{\s*date:new Date\(2026,9,23\),\s*title:\'Resultados de pruebas y trabajos[^\}]*?\},?',
            '',
            del_content
        )
        # 2) Todas las entregas inician como no entregadas (submitted: false) y estado pendiente de marcar
        del_content = del_content.replace('submitted:true', 'submitted:false')
        del_content = del_content.replace('submitted: true', 'submitted: false')
        del_content = re.sub(r"status:'[^']*'", "status:'⏳ Pendiente de marcar'", del_content)
        # 3) Limpiar campos de archivos privados o nombres personales
        del_content = re.sub(r"file2:'2026-10-22-grabacion-entrega-caso-practico-sandra-mosteiro\.mov',?", "", del_content)
        del_content = re.sub(r"file2:'2026-10-30-grabacion-entrega-casos-practicos-susana-diaz\.mp4',?", "", del_content)
        del_content = re.sub(r"file2:'summary\.docx',?", "", del_content)
        del_content = del_content.replace("file:'ESCUDERO VALCÁRCEL-RÍOS RAQUEL PONENCIAS DATAFORUM'", "file:'APELLIDOS NOMBRE PONENCIAS DATAFORUM'")
        del_content = del_content.replace("file:'MASC Demanda de divorcio - Raquel Escudero'", "file:'Propuesta de convenio MASC y demanda de divorcio'")
        # 4) Limpieza rigurosa de textos de entregas (sin estados ni fechas de entrega personales)
        del_content = del_content.replace(' en Google Drive y Markdown local.', '.')
        del_content = del_content.replace('Subida a Google Drive y enviada en CPROC', 'Plataforma oficial CPROC (MUAP)')
        del_content = del_content.replace('Subida a Drive y enviada en CPROC', 'Plataforma oficial CPROC (MUAP)')
        del_content = del_content.replace('Subidos a Google Drive y enviados con éxito en CPROC.', 'Plataforma oficial CPROC (MUAP).')
        del_content = del_content.replace('Práctica subida a Google Drive y enviada dentro de plazo en CPROC', 'Plataforma oficial CPROC (MUAP)')
        del_content = re.sub(
            r"Entrega completada el 26 de octubre de 2026 \(13:18 h\) mediante correo remitido a D\.ª Digna Braña \(branaabogada@icacor\.es\), Coordinadora del Máster, con acuse de recibo oficial \(«Recibido, ¡muchas gracias!»\)\. Documento entregado:",
            "Entrega oficial antes del 2 de noviembre mediante correo a D.ª Digna Braña (branaabogada@icacor.es), Coordinadora del Máster. Contenido:",
            del_content
        )
        del_content = re.sub(
            r"Caso práctico completado y enviado por correo electrónico en la mañana del martes 27 de octubre de 2026 \(antes del vencimiento fijado para el 29 de octubre\)\.",
            "Caso práctico oficial evaluable del módulo (plazo oficial: 29 de octubre de 2026).",
            del_content
        )
        del_content = re.sub(
            r"Enviada por correo electrónico en la tarde del martes 27 de octubre de 2026\.",
            "Entrega por correo electrónico tras la sesión presencial.",
            del_content
        )
        del_content = re.sub(
            r"Entregada telemáticamente con éxito el viernes 30 de octubre de 2026 a las 20:08 h \(«La Tarea se ha entregado con éxito\.»\), antes del plazo fijado para el 2 de noviembre\. Comprobante de entrega registrado en vídeo de pantalla \(2026-10-30-grabacion-entrega-casos-practicos-susana-diaz\.mp4\)\.",
            "Entrega telemática a través de la plataforma oficial CPROC (plazo: 2 de noviembre de 2026).",
            del_content
        )
        del_content = re.sub(
            r"Entregada telemáticamente en el portal CEPROC el viernes 30 de octubre de 2026 a las 17:20 h \(«La Tarea se ha entregado con éxito\.»\), con vídeo de grabación de pantalla guardado en el repositorio\.",
            "Entrega telemática a través de la plataforma oficial CPROC (plazo: 2 de noviembre de 2026).",
            del_content
        )
        del_content = del_content.replace("(Grupo Tarde · Escudero)", "(Grupo Tarde / Mañana según apellido)")

        html = html[:m_del.start(2)] + del_content + html[m_del.end(2):]
        print("✓ Colección de entregas reajustada con inicio limpio a cero y descripciones neutrales.")

    # -------------------------------------------------------------
    # 7b. LIMPIAR DETAILS DE ENTREGAS Y DESACOPLAR INTERFAZ
    # -------------------------------------------------------------
    html = re.sub(
        r"kicker:'Práctica entregada[^']*',",
        "kicker:'Caso práctico evaluable · Seguimiento de entrega',",
        html
    )
    html = re.sub(
        r"date:'Entregad[ao]:[^']*',",
        "date:'Entrega académica oficial · Marca tu estado en el portal',",
        html
    )
    html = re.sub(
        r"date:'Estado: Completada[^']*',",
        "date:'Sesiones: 8 y 9 de octubre de 2026 · Entrega a través de plataforma CPROC',",
        html
    )
    html = re.sub(
        r"extra:'✓[^']*'",
        "extra:'Entrega telemática a través del aula virtual o secretaría académica.'",
        html
    )
    html = html.replace('Estudiante: Raquel Escudero Valcárcel-Ríos · Entregada en CPROC el 22/10/2026 a las 12:51 h', 'Caso práctico oficial evaluable (6 escenarios de la LEC + 3 reflexiones)')
    html = html.replace('Plataforma CPROC (MUAP) → Tareas publicadas · Entrega realizada el 22/10/2026 (12:51 h) con resguardo en pantalla «✓ La Tarea se ha entregado con éxito»', 'Plataforma CPROC (MUAP) → Tareas publicadas · Entrega oficial a través de la plataforma CPROC')
    html = html.replace('Resolución jurídica completa elaborada por Raquel Escudero Valcárcel-Ríos para la materia de Sandra Mosteiro Costa.', 'Resolución de supuestos prácticos procesales para la materia de Sandra Mosteiro Costa.')
    html = html.replace("state:'Entregada en CPROC ✓ (22/10/2026, 12:51 h)'", "state:'Entrega telemática en CPROC'")
    html = html.replace("Confirmación: «La Tarea se ha entregado con éxito» · 16 oct 2026", "Entrega telemática a través de la plataforma CPROC")
    html = html.replace("state:'Entregado en CPROC ✓ · «La Tarea se ha entregado con éxito»'", "state:'Entrega telemática en CPROC'")
    html = html.replace('Repositorio privado con tus apuntes, guías, casos prácticos y entregas', 'Repositorio académico con guías, casos prácticos y materiales de estudio')

    # Sidebar: botón de entregas con ID dinámico (independiente del número de pendientes en index.html)
    html = re.sub(
        r'(<span class="nav-label-text">Próximas entregas</span>\s*)<span class="nav-badge-pill[^"]*"[^>]*>[^<]*</span>',
        r'\1<span class="nav-badge-pill badge-terra highlight-pill" id="sideNavDeliveriesBadge" style="font-weight:800;padding:2px 7px">⏳ Entregas</span>',
        html
    )

    # Sidebar: acordeón de prácticas pendientes con ID dinámico
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
    html = re.sub(r'  <details class="sidebar-pending-details" id="sidebarPendingAccordion" open>.*?</details>', new_side_pending_accordion, html, flags=re.DOTALL)

    # Welcome badge de entregas (independiente del texto fijo en index.html)
    html = re.sub(
        r'(<button class="welcome-badge badge-terra"[^>]*>.*?<span class="badge-label">Prácticas pendientes</span>\s*)<strong class="badge-value">[^<]*</strong>',
        r'\1<strong class="badge-value" id="welcomeDeliveriesSummary">Control de entregas</strong>',
        html,
        flags=re.DOTALL
    )

    # View tab badge de entregas (independiente del número en index.html)
    html = re.sub(
        r'<button class="view-tab" data-view="entregas" role="tab"[^>]*>Próximas entregas <span class="tab-badge"[^>]*>[^<]*</span></button>',
        '<button class="view-tab" data-view="entregas" role="tab" aria-selected="false">Próximas entregas <span class="tab-badge" id="tabDeliveriesBadge" style="background:var(--terracotta);color:#ffffff;font-weight:800">Entregas</span></button>',
        html
    )

    # Portada: Banner dinámico de prácticas pendientes
    m_ptb = re.search(r'<!-- 3\. MÓDULO DESTACADO: TITULARES DE PRÁCTICAS Y ENTREGAS PENDIENTES -->\s*<div class="pending-tasks-banner" id="pendingTasksBanner">.*?</div>\s*</div>\s*</section>', html, re.DOTALL)
    if m_ptb:
        new_ptb = """<!-- 3. MÓDULO DESTACADO: TITULARES DE PRÁCTICAS Y ENTREGAS PENDIENTES -->
    <div class="pending-tasks-banner" id="pendingTasksBanner">
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
    </div>
  </section>"""
        html = html[:m_ptb.start(0)] + new_ptb + html[m_ptb.end(0):]

    # Encabezado de la pestaña de Entregas (independiente del número de pendientes en index.html)
    html = re.sub(
        r'(<section class="section view-hidden" id="deliverySection"[^>]*>\s*<div class="section-title">\s*<div>\s*)<h2>[^<]*</h2>\s*<p>[^<]*</p>',
        r'\1<h2 id="deliveriesSectionMainHeading">Próximas entregas y prácticas del estudiante</h2>\n        <p id="deliveriesSectionMainSub">Seguimiento individual de prácticas y trabajos del Máster. Marca cada tarea según la hayas entregado y anota tu calificación u observación personal.</p>',
        html,
        flags=re.DOTALL
    )

    # Resumen, rango y botones de filtro en Entregas
    html = re.sub(
        r'<span class="status-filter-summary" id="deliveryFilterSummary">[^<]*</span>',
        '<span class="status-filter-summary" id="deliveryFilterSummary">Mostrando el listado completo de entregas del máster.</span>',
        html
    )
    html = re.sub(
        r'<div class="delivery-range" id="deliveryRange">[^<]*</div>',
        '<div class="delivery-range" id="deliveryRange">Control de entregas</div>',
        html
    )
    html = re.sub(r'(<button class="status-filter-btn[^"]*" data-delivery-filter="all">)[^<]*(</button>)', r'\1Todas las prácticas\2', html)
    html = re.sub(r'(<button class="status-filter-btn[^"]*" data-delivery-filter="pending">)[^<]*(</button>)', r'\1⏳ Pendientes de entrega\2', html)
    html = re.sub(r'(<button class="status-filter-btn[^"]*" data-delivery-filter="completed">)[^<]*(</button>)', r'\1✓ Ya entregadas\2', html)
    html = re.sub(r'(<button class="status-filter-btn[^"]*" data-delivery-filter="cproc">)[^<]*(</button>)', r'\1🏛️ Procura / CPROC\2', html)
    html = re.sub(r'(<button class="status-filter-btn[^"]*" data-delivery-filter="icacor">)[^<]*(</button>)', r'\1⚖️ Abogacía / Coordinación\2', html)

    # Notas y Tests: neutralizar referencias fijas a notas/entregas de Raquel en #gradesSection
    html = re.sub(
        r'<span class="due-state submitted" style="font-size:11px">[^<]*notas[^<]*</span>',
        '<span class="due-state submitted" id="gradesModelBannerPill" style="font-size:11px">Ponderación oficial: 40% Cuestionario tipo test + 60% Trabajos y casos prácticos</span>',
        html
    )
    html = html.replace(
        '<p style="color:var(--ink-soft);margin:0">Redacción y presentación formal de escritos procesales, apoderamientos apud acta, resoluciones de casos y dictámenes entregados en CPROC o remitidos al ICACOR (5 entregadas con éxito y 2 pendientes con Delgado).</p>',
        '<p style="color:var(--ink-soft);margin:0">Redacción y presentación formal de escritos procesales, apoderamientos apud acta, resoluciones de casos y dictámenes evaluables en CPROC o ICACOR (60% de la evaluación continua).</p>'
    )
    html = html.replace(
        "sumEl.textContent = 'Mostrando casos prácticos, dictámenes y escritos evaluables agrupados por estado de entrega (5 entregadas y 2 pendientes con Delgado).';",
        "sumEl.textContent = 'Mostrando casos prácticos, dictámenes y escritos evaluables según los hayas marcado como entregados o pendientes.';"
    )

    # Calendario mensual: reflejar si el estudiante actual tiene la entrega pendiente y quitar botón de citas personales
    html = html.replace(
        '<button class="pill-btn blue" data-detail="personal_calendar_sync">★ Citas personales y avisos que te afectan ↗</button>',
        ''
    )
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
.teacher-grade-dossier {
  grid-column: 1 / -1;
  width: 100%;
}
.privacy-banner {
  grid-column: 1 / -1;
  width: 100%;
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
  box-sizing: border-box;
}
.privacy-banner svg {
  flex-shrink: 0;
}
.student-eval-bar {
  background: var(--paper-warm);
  border: 1.5px solid var(--line);
  border-radius: 12px;
  padding: 14px 18px;
  margin: 12px 0 16px;
  display: grid;
  grid-template-columns: minmax(180px, 240px) 1fr;
  gap: 16px;
  align-items: start;
}
@media(max-width: 768px) {
  .student-eval-bar {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
.student-eval-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
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
  width: 100%;
  max-width: 100%;
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
  box-sizing: border-box;
}
.student-test-input-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.student-test-input-wrap input {
  width: 130px;
  max-width: 100%;
  font-weight: 700;
  color: var(--green-dark);
  text-align: center;
  border: 1.5px solid var(--green-border);
  background: var(--green-pale);
  border-radius: 6px;
  padding: 7px 10px;
  font-size: 14px;
  box-sizing: border-box;
}
.student-test-input-wrap input:focus {
  outline: none;
  border-color: var(--green-dark);
  box-shadow: 0 0 0 3px rgba(20, 42, 66, 0.2);
}
.tgd-blocks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px;
}
.tgd-block {
  min-width: 0;
  box-sizing: border-box;
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
    end_idx_dossiers = html.find('function getDeliverySavedNote(', idx_dossiers)
    if end_idx_dossiers == -1:
        end_idx_dossiers = html.find('function saveDeliveryNote(', idx_dossiers)
    if end_idx_dossiers == -1:
        end_idx_dossiers = html.find('function renderPracticesGradeView()', idx_dossiers)

    if idx_dossiers != -1 and end_idx_dossiers != -1:
        new_dossiers_code = """// Limpieza estricta de cualquier nota previa residual o de versiones antiguas en localStorage
try {
  for(let i = localStorage.length - 1; i >= 0; i--){
    const k = localStorage.key(i);
    if(k && (k.startsWith('muap_eval_') || k.startsWith('muap_student_v2_'))){
      localStorage.removeItem(k);
    }
  }
} catch(e){}

function getStudentGradeData(teacherId){
  try {
    const raw = localStorage.getItem('muap_clean_v3_' + teacherId);
    const parsed = raw ? JSON.parse(raw) : { finalGrade:'', testGrade:'', notes:'' };
    if(!parsed.finalGrade && typeof getTeacherNamesForDossier === 'function'){
      const tNames = getTeacherNamesForDossier(teacherId);
      for(const tn of tNames){
        const savedT = localStorage.getItem('muap_teacher_grade_' + encodeURIComponent(tn));
        if(savedT && savedT.trim()){
          parsed.finalGrade = savedT.trim();
          break;
        }
      }
    }
    return {
      finalGrade: parsed.finalGrade || '',
      testGrade: parsed.testGrade || '',
      notes: parsed.notes || ''
    };
  } catch(e){
    return { finalGrade:'', testGrade:'', notes:'' };
  }
}

function getTeacherNamesForDossier(dossierId){
  if(!dossierId) return [];
  const map = {
    'dossier-carolina-moreno': ['Carolina Moreno Vázquez', 'Carlos M. Sánchez Muiño', 'Alex Sánchez Barge', 'Carolina Moreno Vázquez y Carlos M. Sánchez Muiño'],
    'dossier-carlos-sanchez': ['Carlos Miguel Sánchez Muiño', 'Carlos M. Sánchez Muiño'],
    'dossier-sandra-mosteiro': ['Sandra Mosteiro Costa'],
    'dossier-ana-vazquez': ['Ana Vázquez Corte'],
    'dossier-javier-sanchez': ['Javier Sánchez García', 'Javier Carlos Sánchez García', 'Javier C. Sánchez García'],
    'dossier-carmen-belo': ['Carmen Belo González'],
    'dossier-jose-luis-delgado': ['José Luis Delgado Domínguez'],
    'dossier-maria-carnota': ['María Pilar Carnota García', 'María P. Carnota García'],
    'dossier-susana-diaz': ['Susana Díaz Gallego'],
    'dossier-maria-luisa-moure': ['María Luisa Moure Sagasti', 'Mª Luisa Moure'],
    'dossier-javier-garcia-santiago-varela': ['Javier García y Santiago Varela', 'Javier García', 'Santiago Varela', 'Patricia González Figueroa'],
    'dossier-fernando-lousada': ['Fernando Lousada', 'Fernando Lousada Arochena'],
    'dossier-daniel-garrido': ['Daniel Garrido Pazos'],
    'dossier-alejandra-sanchez': ['Alejandra Sánchez'],
    'dossier-vanessa-amarelle': ['Vanessa Amarelle y Carlos Tomé', 'Vanessa Amarelle', 'Carlos Tomé']
  };
  const list = map[dossierId] ? [...map[dossierId]] : [];
  if(typeof teacherDirectory !== 'undefined' && typeof getDossierIdForTeacher === 'function'){
    teacherDirectory.forEach(t => {
      if(getDossierIdForTeacher(t.name) === dossierId && !list.includes(t.name)){
        list.push(t.name);
      }
    });
  }
  return list;
}

function saveStudentGradeData(teacherId, data){
  try {
    const raw = localStorage.getItem('muap_clean_v3_' + teacherId);
    const current = raw ? JSON.parse(raw) : { finalGrade:'', testGrade:'', notes:'' };
    const updated = { ...current, ...data };
    localStorage.setItem('muap_clean_v3_' + teacherId, JSON.stringify(updated));
    const effective = (updated.finalGrade || updated.testGrade || '').trim();
    const tNames = getTeacherNamesForDossier(teacherId);
    tNames.forEach(tn => {
      if(effective){
        localStorage.setItem('muap_teacher_grade_' + encodeURIComponent(tn), effective);
      } else {
        localStorage.removeItem('muap_teacher_grade_' + encodeURIComponent(tn));
      }
    });
    if(typeof courses !== 'undefined' && tNames.length){
      courses.forEach(c => {
        const cKey = typeof courseKey === 'function' ? courseKey(c) : `${c.branch}|${c.name}`;
        (c.subjects || []).forEach((sub, sIdx) => {
          const subTeachers = sub.teachers || [];
          if(subTeachers.length === 1 && tNames.some(tn => subTeachers[0] === tn || subTeachers[0].includes(tn) || tn.includes(subTeachers[0]))){
            const cleanSubName = sub.name.replace(/\\s*\\(Sesión[^)]*\\)/i, '').trim();
            if(effective){
              localStorage.setItem('muap_sub_grade_' + encodeURIComponent(cleanSubName), effective);
              localStorage.setItem('muap_sub_grade_' + encodeURIComponent(cKey + '|' + sIdx), effective);
            } else {
              localStorage.removeItem('muap_sub_grade_' + encodeURIComponent(cleanSubName));
              localStorage.removeItem('muap_sub_grade_' + encodeURIComponent(cKey + '|' + sIdx));
            }
          }
        });
      });
    }
    updateHomeGradesBadge();
    if(typeof renderSubjectsList === 'function') renderSubjectsList();
    if(typeof renderSidebarTree === 'function') renderSidebarTree();
    if(typeof renderTeachers === 'function') renderTeachers();
    if(typeof renderDay === 'function') renderDay();
    if(typeof renderActiveMasterBanner === 'function') renderActiveMasterBanner();
    if(typeof activeView !== 'undefined' && activeView === 'asignaturas'){
      const s2 = document.getElementById('subjectsScreen2');
      const s3 = document.getElementById('subjectsScreen3');
      if(s3 && !s3.classList.contains('hidden') && typeof currentActiveTeacher === 'string' && currentActiveTeacher){
        showScreen3(currentActiveTeacher);
      } else if(s2 && !s2.classList.contains('hidden') && typeof currentActiveSubject === 'object' && currentActiveSubject){
        showScreen2(currentActiveSubject.cKey, currentActiveSubject.sIdx);
      }
    }
  } catch(e){}
}

function clearAllStudentGrades(){
  if(!confirm('¿Deseas vaciar todas las notas guardadas y dejar el cuaderno completamente limpio a cero?')) return;
  try {
    for(let i = localStorage.length - 1; i >= 0; i--){
      const k = localStorage.key(i);
      if(k && (k.startsWith('muap_eval_') || k.startsWith('muap_student_v2_') || k.startsWith('muap_clean_v3_') || k.startsWith('muap_sub_grade_') || k.startsWith('muap_teacher_grade_') || k.startsWith('muap_test_card_grade_') || k.startsWith('muap_deliv_note_'))){
        localStorage.removeItem(k);
      }
    }
  } catch(e){}
  renderGrades();
  updateHomeGradesBadge();
  if(typeof renderSubjectsList === 'function') renderSubjectsList();
  if(typeof renderSidebarTree === 'function') renderSidebarTree();
  if(typeof renderTeachers === 'function') renderTeachers();
  if(typeof renderDeliveries === 'function') renderDeliveries();
  if(typeof renderDay === 'function') renderDay();
  if(typeof renderActiveMasterBanner === 'function') renderActiveMasterBanner();
  if(typeof showToastNotification === 'function') showToastNotification('Cuaderno de notas reiniciado a cero en este navegador.');
}

function updateHomeGradesBadge(){
  const evaluatedDossiers = new Set();
  try {
    for(let i = 0; i < localStorage.length; i++){
      const k = localStorage.key(i);
      if(!k) continue;
      if(k.startsWith('muap_clean_v3_')){
        try {
          const d = JSON.parse(localStorage.getItem(k));
          if(d && ((d.finalGrade && d.finalGrade.trim()) || (d.testGrade && d.testGrade.trim()) || (d.notes && d.notes.trim()))){
            evaluatedDossiers.add(k.replace('muap_clean_v3_', ''));
          }
        } catch(e){}
      } else if(k.startsWith('muap_teacher_grade_')){
        const val = (localStorage.getItem(k) || '').trim();
        if(val){
          const tName = decodeURIComponent(k.replace('muap_teacher_grade_', ''));
          const dId = typeof getDossierIdForTeacher === 'function' ? getDossierIdForTeacher(tName) : ('teacher-' + tName);
          evaluatedDossiers.add(dId || ('teacher-' + tName));
        }
      } else if(k.startsWith('muap_sub_grade_')){
        const val = (localStorage.getItem(k) || '').trim();
        if(val){
          const subKey = decodeURIComponent(k.replace('muap_sub_grade_', ''));
          let mappedDossier = '';
          if(typeof courses !== 'undefined' && typeof getDossierIdForTeacher === 'function'){
            courses.forEach(c => {
              const cKey = typeof courseKey === 'function' ? courseKey(c) : `${c.branch}|${c.name}`;
              (c.subjects || []).forEach((s, idx) => {
                const cleanS = s.name.replace(/\\s*\\(Sesión[^)]*\\)/i, '').trim();
                if(cleanS === subKey || `${cKey}|${idx}` === subKey){
                  if(s.teachers && s.teachers.length === 1){
                    mappedDossier = getDossierIdForTeacher(s.teachers[0]);
                  }
                }
              });
            });
          }
          if(mappedDossier){
            evaluatedDossiers.add(mappedDossier);
          } else if(!subKey.includes('|')){
            evaluatedDossiers.add('sub-' + subKey);
          }
        }
      }
    }
  } catch(e){}

  let testCardsCount = 0;
  try {
    if(typeof gradeRecords !== 'undefined' && Array.isArray(gradeRecords)){
      gradeRecords.filter(g => g.type === 'test').forEach(g => {
        const byId = g.id ? (localStorage.getItem('muap_test_card_grade_' + g.id) || '').trim() : '';
        const byMail = g.mailKey ? (localStorage.getItem('muap_test_card_grade_' + g.mailKey) || '').trim() : '';
        let byDossier = '';
        if(g.teacher && typeof getDossierIdForTeacher === 'function'){
          const dId = getDossierIdForTeacher(g.teacher);
          if(dId){
            const sd = getStudentGradeData(dId);
            if(sd && sd.testGrade) byDossier = sd.testGrade.trim();
          }
        }
        if(byId || byMail || byDossier){
          testCardsCount++;
          if(g.teacher && typeof getDossierIdForTeacher === 'function'){
            const dId = getDossierIdForTeacher(g.teacher);
            if(dId) evaluatedDossiers.add(dId);
          }
        }
      });
    }
  } catch(e){}

  const count = evaluatedDossiers.size;

  const el = document.getElementById('welcomeGradesSummary');
  if(el){
    el.textContent = count > 0 ? `${count} evaluada${count === 1 ? '' : 's'} por ti` : 'Mi Cuaderno de Notas';
  }
  const sideBadge = document.getElementById('sideNavGradesBadge') || document.querySelector('.nav-btn-notas .nav-badge-pill');
  if(sideBadge){
    sideBadge.textContent = count > 0 ? `★ ${count} eval.` : 'Mi Cuaderno';
    sideBadge.className = 'nav-badge-pill ' + (count > 0 ? 'badge-honey highlight-pill' : 'badge-honey');
  }
  const tabBadge = document.getElementById('tabGradesBadge') || document.querySelector('[data-view="notas"] .tab-badge');
  if(tabBadge){
    tabBadge.textContent = count > 0 ? `${count}` : '0';
  }
  const hubTitle = document.getElementById('homeHubGradesTitle');
  if(hubTitle){
    hubTitle.textContent = count > 0 ? `${count} Calificación${count === 1 ? '' : 'es'} Guardada${count === 1 ? '' : 's'}` : 'Mi Cuaderno de Notas';
  }
  const hubMeta = document.getElementById('homeHubGradesMeta');
  if(hubMeta){
    hubMeta.textContent = count > 0 ? `${count} módulo${count === 1 ? '' : 's'} evaluado${count === 1 ? '' : 's'} (${testCardsCount}/6 tests con nota) en tu navegador` : '6 cuestionarios interactivos · Registro privado en tu navegador';
  }
  const statTeachersPill = document.getElementById('statTeachersPill');
  if(statTeachersPill){
    statTeachersPill.textContent = count > 0 ? `★ ${count} con nota guardada` : 'Anota tus notas →';
  }
  const statMailPill = document.getElementById('statMailPill');
  if(statMailPill){
    statMailPill.textContent = count > 0 ? `★ ${count} registrada${count === 1 ? '' : 's'}` : 'Ver actas →';
  }
  const statTestPill = document.getElementById('statTestPill');
  if(statTestPill){
    statTestPill.textContent = testCardsCount > 0 ? `★ ${testCardsCount}/6 con nota` : 'Ver preguntas y respuestas →';
  }
}

function renderTeacherDossiers(){
  const dossiers = [
   {
    id: 'dossier-carlos-sanchez',
    teacher: 'Carlos Miguel Sánchez Muiño',
    subject: 'Técnicas instrumentales · Rama Procura (Sesión 2 oct 2026)',
    subjectRef: 'Procura|Técnicas instrumentales|0',
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
     {label: 'Ver asignatura ↗', subjectRef: 'Procura|Técnicas instrumentales|0'},
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
    id: 'dossier-carmen-belo',
    teacher: 'Carmen Belo González',
    subject: 'Colegiación, estatuto y previsión social · Rama Procura (Sesión 9 oct 2026)',
    subjectRef: 'Procura|Deontología y responsabilidad|1',
    kicker: 'Materia finalizada · Evaluación mediante trabajo práctico en CPROC',
    testName: 'Evaluación del módulo (CPROC)',
    blocks: [
     {
      cls: 'highlight-practice',
      title: '📁 Trabajo Práctico CPROC (100 %)',
      score: 'Caso práctico',
      desc: 'Supuesto práctico sobre colegiación, estatutos corporativos y previsión social de los procuradores.',
      subitems: [
       {label: 'Plataforma', val: 'CPROC (MUAP)'},
       {label: 'Fecha límite', val: '12 oct 2026'}
      ]
     },
     {
      cls: 'highlight-mail',
      title: '✉️ Calificación Docente',
      score: 'Evaluación CPROC',
      desc: 'Calificación comunicada tras la revisión del trabajo práctico entregado en CPROC.',
      subitems: [
       {label: 'Modalidad', val: '100% Caso práctico'},
       {label: 'Sesión', val: '9 oct 2026'}
      ]
     }
    ],
    actions: [
     {label: '📁 Ver práctica de Colegiación ↗', detailKey: 'entrega_colegiacion'},
     {label: 'Ver asignatura ↗', subjectRef: 'Procura|Deontología y responsabilidad|1'},
     {label: 'Ficha de Carmen Belo González ↗', teacher: 'Carmen Belo González'}
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
    id: 'dossier-sandra-mosteiro',
    teacher: 'Sandra Mosteiro Costa',
    subject: 'Actos de comunicación judicial · Rama Procura (Sesiones 19 y 20 oct 2026)',
    subjectRef: 'Procura|Técnicas instrumentales|3',
    kicker: 'Test online y caso práctico evaluable de 6 escenarios LEC',
    testName: 'Test online Testmoz (20 oct · 10 preguntas)',
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
      score: 'Ponderación Oficial',
      desc: 'Ponderación conjunta del test online en Testmoz y el caso práctico escrito de 6 escenarios.',
      subitems: [
       {label: 'Test online', val: 'Testmoz (20 oct)'},
       {label: 'Caso escrito', val: 'CPROC (22 oct)'}
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
    id: 'dossier-maria-carnota',
    teacher: 'María Pilar Carnota García',
    subject: 'Aranceles, presupuestos y cuenta del procurador · Rama Procura (27 y 28 oct 2026)',
    subjectRef: 'Procura|Actuación procesal|1',
    kicker: '2 tests online en Testmoz (28 oct y 2 nov) y liquidación arancelaria',
    testName: 'Tests de Aranceles en Testmoz (28 oct y 2 nov)',
    blocks: [
     {
      cls: 'highlight-test',
      title: '📝 Tests Online en Testmoz (28 oct y 2 nov)',
      score: '2 cuestionarios (10 + 10 preg.)',
      desc: 'Cuestionarios oficiales sobre el Arancel de Derechos de los Procuradores (RD 1373/2003 y RD 307/2022).',
      subitems: [
       {label: 'Test 1 (28 oct)', val: '10 preguntas'},
       {label: 'Test 2 (2 nov)', val: '10 preguntas'}
      ]
     },
     {
      cls: 'highlight-practice',
      title: '📁 Liquidación Arancelaria y Cuenta',
      score: 'Supuestos prácticos',
      desc: 'Cálculo de derechos arancelarios, provisión de fondos y jura de cuentas (art. 34 LEC).',
      subitems: [
       {label: 'Normativa', val: 'RD 1373/2003 y RD 307/2022'},
       {label: 'Sesiones', val: '27 y 28 oct 2026'}
      ]
     }
    ],
    actions: [
     {label: '📝 Ver Test 1 (28 oct) ↗', detailKey: 'test_28oct_carnota'},
     {label: '📝 Ver Test 2 (2 nov) ↗', detailKey: 'test_2nov_carnota'},
     {label: 'Ver asignatura ↗', subjectRef: 'Procura|Actuación procesal|1'},
     {label: 'Ficha de María Pilar Carnota ↗', teacher: 'María Pilar Carnota García'}
    ]
   },
   {
    id: 'dossier-susana-diaz',
    teacher: 'Susana Díaz Gallego',
    subject: 'Representación procesal, poder y turno de oficio · Rama Procura (29 y 30 oct 2026)',
    subjectRef: 'Procura|Actuación procesal|2',
    kicker: '2 tests en Testmoz (29 y 30 oct) y 2 prácticas en CPROC',
    testName: 'Tests de Deontología y Representación (29 y 30 oct)',
    blocks: [
     {
      cls: 'highlight-test',
      title: '📝 Tests Online en Testmoz (29 y 30 oct)',
      score: '2 cuestionarios (10 + 10 preg.)',
      desc: 'Test de Deontología Profesional (29 oct) y Test de Representación Procesal (30 oct) en Testmoz.',
      subitems: [
       {label: 'Test 29 oct', val: '10 preguntas (Testmoz)'},
       {label: 'Test 30 oct', val: '10 preguntas (Testmoz)'}
      ]
     },
     {
      cls: 'highlight-practice',
      title: '📁 Prácticas en CPROC (Subsanación y 3 Casos)',
      score: '2 entregas CPROC',
      desc: '1) Subsanación de apoderamiento apud acta (29 oct) y 2) Tres casos prácticos de representación procesal (2 nov).',
      subitems: [
       {label: 'Subsanación poder', val: 'CPROC (29 oct)'},
       {label: '3 Casos prácticos', val: 'CPROC (2 nov)'}
      ]
     }
    ],
    actions: [
     {label: '📁 Ver 3 Casos Prácticos (2 nov) ↗', detailKey: 'entrega_susana_diaz_casos_30oct'},
     {label: '📁 Ver Subsanación Poder (29 oct) ↗', detailKey: 'entrega_susana_diaz_subsanacion'},
     {label: 'Ver asignatura ↗', subjectRef: 'Procura|Actuación procesal|2'},
     {label: 'Ficha de Susana Díaz Gallego ↗', teacher: 'Susana Díaz Gallego'}
    ]
   },
   {
    id: 'dossier-jose-luis-delgado',
    teacher: 'José Luis Delgado Domínguez',
    subject: 'Responsabilidad civil y penal, aseguramiento y turno de oficio · Abogacía',
    subjectRef: 'Abogacía|Técnicas instrumentales|3',
    kicker: 'Caso práctico (Parte A y Parte B) y evaluación del módulo',
    testName: 'Evaluación continua presencial (ICACOR)',
    blocks: [
     {
      cls: 'highlight-practice',
      title: '📁 Caso Práctico (Parte A y Parte B)',
      score: 'Partes A y B',
      desc: 'Parte A (Insostenibilidad y Asistencia Jurídica Gratuita) y Parte B (Parte de siniestro de RCP y Turno de Oficio).',
      subitems: [
       {label: 'Plazo oficial', val: '29 oct 2026 (ICACOR)'},
       {label: 'Estructura', val: 'Parte A y Parte B'}
      ]
     },
     {
      cls: 'highlight-test',
      title: '📝 Evaluación Continua del Módulo',
      score: 'ICACOR',
      desc: 'Módulo de responsabilidad profesional del abogado, aseguramiento y turno de oficio en el Colegio de Abogados.',
      subitems: [
       {label: 'Docencia', val: 'Colegio de Abogados'},
       {label: 'Rama', val: 'Abogacía'}
      ]
     }
    ],
    actions: [
     {label: '📁 Ver caso práctico (Parte A y Parte B) ↗', detailKey: 'entrega_delgado', cls: 'solid-green'},
     {label: 'Ver asignatura ↗', subjectRef: 'Abogacía|Técnicas instrumentales|3'},
     {label: 'Ficha de José Luis Delgado Domínguez ↗', teacher: 'José Luis Delgado Domínguez'}
    ]
   },
   {
    id: 'dossier-maria-luisa-moure',
    teacher: 'María Luisa Moure Sagasti',
    subject: 'Mediación y resolución alternativa de conflictos (MASC) · Abogacía',
    subjectRef: 'Abogacía|Técnicas instrumentales|4',
    kicker: 'Caso práctico de mediación civil y mercantil (LO 1/2025)',
    testName: 'Evaluación continua de Mediación y MASC',
    blocks: [
     {
      cls: 'highlight-practice',
      title: '📁 Caso Práctico de Mediación (ICACOR)',
      score: 'Caso evaluable',
      desc: 'Resolución del caso práctico sobre mediación, confidencialidad y requisito de procedibilidad MASC.',
      subitems: [
       {label: 'Plazo oficial', val: '29 oct 2026'},
       {label: 'Vía de entrega', val: 'master.abogacia@icacor.org'}
      ]
     }
    ],
    actions: [
     {label: '📁 Ver caso práctico de Mediación ↗', detailKey: 'entrega_mediacion_moure'},
     {label: 'Ver asignatura ↗', subjectRef: 'Abogacía|Técnicas instrumentales|4'},
     {label: 'Ficha de María Luisa Moure ↗', teacher: 'María Luisa Moure Sagasti'}
    ]
   },
   {
    id: 'dossier-javier-garcia-santiago-varela',
    teacher: 'Javier García y Santiago Varela',
    subject: 'Escritura forense y técnicas de expresión escrita · Abogacía',
    subjectRef: 'Abogacía|Técnicas instrumentales|7',
    kicker: 'Caso práctico de Escritura Forense (plazo 30 nov 2026)',
    testName: 'Evaluación de Escritura Forense',
    blocks: [
     {
      cls: 'highlight-practice',
      title: '📁 Caso Práctico de Escritura Forense',
      score: 'Plazo 30 nov 2026',
      desc: 'Redacción forense y estructuración técnica de escritos procesales remitida por el ICACOR.',
      subitems: [
       {label: 'Fecha límite', val: '30 nov 2026'},
       {label: 'Vía de entrega', val: 'master.abogacia@icacor.org'}
      ]
     }
    ],
    actions: [
     {label: '📁 Ver caso de Escritura Forense (30 nov) ↗', detailKey: 'mail_caso_escritura_30oct'},
     {label: 'Ver asignatura ↗', subjectRef: 'Abogacía|Técnicas instrumentales|7'},
     {label: 'Ficha de Javier García y Santiago Varela ↗', teacher: 'Javier García y Santiago Varela'}
    ]
   },
   {
    id: 'dossier-fernando-lousada',
    teacher: 'Fernando Lousada',
    subject: 'Práctica procesal civil · Rama Abogacía (Sesiones 11, 12, 16 y 19 nov 2026)',
    subjectRef: 'Abogacía|Procesal civil|0',
    kicker: '4 casos prácticos asignados por sesión (envío previo a cada clase)',
    testName: 'Evaluación continua de Práctica Procesal Civil',
    blocks: [
     {
      cls: 'highlight-practice',
      title: '📁 4 Casos Prácticos de Procesal Civil',
      score: '4 entregas (11, 12, 16 y 19 nov)',
      desc: 'Resolución de las preguntas asignadas y comunes antes de las 20:00 h de la víspera de cada sesión.',
      subitems: [
       {label: 'Correo docente', val: 'fernando.lousada@udc.es'},
       {label: 'Sesiones', val: '11, 12, 16 y 19 nov 2026'}
      ]
     }
    ],
    actions: [
     {label: '📁 Ver Caso 1 (11 nov) ↗', detailKey: 'entrega_lousada_1_demanda'},
     {label: 'Ver asignatura ↗', subjectRef: 'Abogacía|Procesal civil|0'},
     {label: 'Ficha de Fernando Lousada ↗', teacher: 'Fernando Lousada'}
    ]
   }
  ];

  const privacyNotice = `
    <div class="privacy-banner" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:14px">
      <div style="display:flex;align-items:center;gap:12px;flex:1;min-width:240px">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><circle cx="12" cy="11" r="3"/></svg>
        <div>
          <strong>Tu Cuaderno Privado de Notas (Guardado local en tu dispositivo):</strong>
          Las notas de los tests, las calificaciones del profesor y tus anotaciones personales se guardan únicamente en la memoria de tu navegador (localStorage). El portal inicia 100% limpio y a cero para que cada estudiante lo rellene de forma privada.
        </div>
      </div>
      <button type="button" class="pill-btn" onclick="clearAllStudentGrades()" style="border:1.5px solid var(--green-border);background:var(--paper);color:var(--green-dark);cursor:pointer;white-space:nowrap;padding:7px 14px;font-weight:700">🗑️ Limpiar todas mis notas</button>
    </div>
  `;

  return privacyNotice + dossiers.map(d => {
    const sData = getStudentGradeData(d.id);
    const safeFinal = typeof escapeHtml === 'function' ? escapeHtml(sData.finalGrade) : (sData.finalGrade || '');
    const safeTest = typeof escapeHtml === 'function' ? escapeHtml(sData.testGrade) : (sData.testGrade || '');
    const safeNotes = typeof escapeHtml === 'function' ? escapeHtml(sData.notes) : (sData.notes || '');
    const badgeText = sData.finalGrade ? `★ ${safeFinal} · Mi Nota` : (sData.testGrade ? `Test: ${safeTest}` : 'Sin calificar');
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
              <input type="text" id="input_final_${d.id}" placeholder="Anota la calificación..." value="${safeFinal}" oninput="handleStudentGradeChange('${d.id}')">
            </div>
            <div class="student-eval-field">
              <label for="input_notes_${d.id}">✍️ Anotaciones personales / Criterios de corrección:</label>
              <textarea id="input_notes_${d.id}" rows="2" placeholder="Escribe aquí tus comentarios, dudas o criterios de corrección..." oninput="handleStudentGradeChange('${d.id}')">${safeNotes}</textarea>
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
          <input type="text" id="input_test_${d.id}" placeholder="Anota la nota del test..." value="${safeTest}" oninput="handleStudentGradeChange('${d.id}')">
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
  const notes = nInput ? nInput.value : '';

  saveStudentGradeData(teacherId, { finalGrade, testGrade, notes });

  if(badgeEl){
    badgeEl.textContent = finalGrade ? `★ ${finalGrade} · Mi Nota` : (testGrade ? `Test: ${testGrade}` : 'Sin calificar');
    badgeEl.className = 'tgd-badge ' + (finalGrade ? 'gold' : (testGrade ? 'blue' : 'terra'));
  }

  if(statusEl){
    statusEl.textContent = '✓ Guardado en tu navegador';
    statusEl.style.opacity = '1';
    setTimeout(() => { if(statusEl) statusEl.style.opacity = '0.7'; }, 1500);
  }
}
\n\n"""
        html = html[:idx_dossiers] + new_dossiers_code + html[end_idx_dossiers:]
        print("✓ renderTeacherDossiers adaptada con los 12 dossiers evaluables e interactividad localStorage completa.")

    # -------------------------------------------------------------
    # 10. REEMPLAZAR renderDeliveries CON CONTROL TOTAL DINÁMICO EN LOCALSTORAGE
    # -------------------------------------------------------------
    idx_render_del = html.find('function renderDeliveries(filter = currentDeliveryFilter){')
    idx_end_render_del = html.find('\nlet toastNotificationTimer', idx_render_del)
    if idx_end_render_del == -1:
        idx_end_render_del = html.find('\nfunction renderMail(', idx_render_del)
    if idx_render_del != -1 and idx_end_render_del != -1:
        custom_render_deliveries_code = """function isDeliveryChecked(detailKey){
  if(!detailKey) return false;
  try {
    return localStorage.getItem('muap_deliv_check_' + detailKey) === 'true';
  } catch(e){
    return false;
  }
}

function toggleDeliveryCheck(detailKey, btnEl){
  if(!detailKey) return;
  try {
    const current = isDeliveryChecked(detailKey);
    const newVal = !current;
    localStorage.setItem('muap_deliv_check_' + detailKey, newVal ? 'true' : 'false');
    
    let toggledTitle = '';
    deliveries.forEach(d => {
      if(d.detailKey === detailKey){
        d.submitted = newVal;
        d.status = newVal ? 'Entregada por mí ✓' : '⏳ Pendiente de marcar';
        toggledTitle = d.title || '';
      }
    });

    renderDeliveries(currentDeliveryFilter);
    renderHomePendingTasks();
    renderSidebarPendingItems();
    updateDeliveryCounts();
    if(typeof renderCalendar === 'function') renderCalendar();
    if(typeof renderGrades === 'function' && typeof activeView !== 'undefined' && activeView === 'notas') renderGrades();
    if(typeof renderSubjectsList === 'function') renderSubjectsList();
    if(typeof renderSidebarTree === 'function') renderSidebarTree();
    if(typeof renderTeachers === 'function') renderTeachers();
    if(typeof activeView !== 'undefined' && activeView === 'asignaturas'){
      const s2 = document.getElementById('subjectsScreen2');
      const s3 = document.getElementById('subjectsScreen3');
      if(s3 && !s3.classList.contains('hidden') && typeof currentActiveTeacher === 'string' && currentActiveTeacher){
        showScreen3(currentActiveTeacher);
      } else if(s2 && !s2.classList.contains('hidden') && typeof currentActiveSubject === 'object' && currentActiveSubject){
        showScreen2(currentActiveSubject.cKey, currentActiveSubject.sIdx);
      }
    }
    if(typeof showToastNotification === 'function'){
      showToastNotification(newVal
        ? `✓ Práctica marcada como entregada${toggledTitle ? ': «' + toggledTitle + '»' : ''} (guardado en tu navegador).`
        : `⏳ Práctica devuelta a pendientes${toggledTitle ? ': «' + toggledTitle + '»' : ''}.`);
    }
  } catch(e){}
}

function updateDeliveryCounts(){
  deliveries.forEach(d => {
    d.submitted = isDeliveryChecked(d.detailKey);
    d.status = d.submitted ? 'Entregada por mí ✓' : '⏳ Pendiente de marcar';
  });

  const pending = deliveries.filter(d => !d.submitted).sort((a,b) => a.date.getTime() - b.date.getTime());
  const pendingCount = pending.length;
  const completedCount = deliveries.length - pendingCount;
  const totalCount = deliveries.length;

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
    ptbBadge.textContent = pendingCount > 0 ? `⚠️ ${pendingCount} PRÁCTICA${pendingCount === 1 ? '' : 'S'} PENDIENTE${pendingCount === 1 ? '' : 'S'}` : '🎉 ¡TODAS LAS PRÁCTICAS ENTREGADAS!';
    ptbBadge.className = 'ptb-badge ' + (pendingCount > 0 ? 'alert' : 'success');
  }

  const ptbUrgent = document.getElementById('ptbUrgentChipEl');
  if(ptbUrgent){
    ptbUrgent.textContent = pendingCount > 0 ? `📅 Próxima: ${fmtShort(pending[0].date)}` : '✓ Al día';
  }

  // 5. Encabezado de sección y subtítulo
  const mainHeading = document.getElementById('deliveriesSectionMainHeading');
  if(mainHeading){
    mainHeading.textContent = `Próximas entregas y prácticas (${pendingCount} pendientes · ${completedCount} entregadas por ti)`;
  }

  const rangeEl = document.getElementById('deliveryRange');
  if(rangeEl){
    rangeEl.textContent = `${pendingCount} pendientes · ${completedCount} marcadas como entregadas`;
  }

  // 6. Tarjeta resumen en portada y píldora en Notas
  const hubPendingTitle = document.getElementById('homeHubPendingTitle');
  if(hubPendingTitle){
    hubPendingTitle.textContent = pendingCount > 0 ? `${pendingCount} Práctica${pendingCount === 1 ? '' : 's'} por Entregar` : '¡Todas las Prácticas al Día!';
  }
  const hubPendingMeta = document.getElementById('homeHubPendingMeta');
  if(hubPendingMeta){
    hubPendingMeta.textContent = `${completedCount} entregada${completedCount === 1 ? '' : 's'} por ti · ${pendingCount} pendiente${pendingCount === 1 ? '' : 's'} de marcar`;
  }
  const statPracticesTitle = document.getElementById('statPracticesTitle');
  if(statPracticesTitle){
    statPracticesTitle.textContent = `${completedCount}/${totalCount} Prácticas Entregadas`;
  }
  const statPracticesPill = document.getElementById('statPracticesPill');
  if(statPracticesPill){
    statPracticesPill.textContent = pendingCount > 0 ? `⏳ ${pendingCount} pendiente${pendingCount === 1 ? '' : 's'} →` : '✓ Todas al día →';
  }

  // 7. Botones de filtro en la sección Entregas
  const cprocCount = deliveries.filter(d => (d.subject||'').toLowerCase().includes('procura') || (d.status||'').toLowerCase().includes('cproc') || (d.details||'').toLowerCase().includes('cproc')).length;
  const icacorCount = deliveries.filter(d => (d.subject||'').toLowerCase().includes('abogacía') || (d.details||'').toLowerCase().includes('icacor') || (d.teacher||'').toLowerCase().includes('delgado') || (d.details||'').toLowerCase().includes('dataforum')).length;
  const btnAll = document.querySelector('[data-delivery-filter="all"]');
  if(btnAll) btnAll.textContent = `Todas (${totalCount})`;
  const btnPend = document.querySelector('[data-delivery-filter="pending"]');
  if(btnPend) btnPend.textContent = `⏳ Pendientes (${pendingCount})`;
  const btnComp = document.querySelector('[data-delivery-filter="completed"]');
  if(btnComp) btnComp.textContent = `✓ Entregadas (${completedCount})`;
  const btnCproc = document.querySelector('[data-delivery-filter="cproc"]');
  if(btnCproc) btnCproc.textContent = `🏛️ Procura · CPROC (${cprocCount})`;
  const btnIcacor = document.querySelector('[data-delivery-filter="icacor"]');
  if(btnIcacor) btnIcacor.textContent = `⚖️ Abogacía · ICACOR (${icacorCount})`;
}

function renderHomePendingTasks(){
  const grid = document.getElementById('homePendingTasksGrid');
  if(!grid) return;

  const pending = deliveries.filter(d => !isDeliveryChecked(d.detailKey)).sort((a,b) => a.date.getTime() - b.date.getTime());
  
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

  const pending = deliveries.filter(d => !isDeliveryChecked(d.detailKey)).sort((a,b) => a.date.getTime() - b.date.getTime());
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
  filtered = deliveries.filter(d => (d.subject||'').toLowerCase().includes('abogacía') || (d.details||'').toLowerCase().includes('icacor') || (d.teacher||'').toLowerCase().includes('delgado') || (d.details||'').toLowerCase().includes('dataforum'));
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
   summaryEl.textContent = `Mostrando el listado completo de entregas del máster (${filtered.length} prácticas: ${pendingCount} pendientes y ${completedCount} entregadas por ti).`;
  }
 }

 const renderRow = (d) => {
  const isChk = d.submitted;
  const isAbogacia = (d.subjectRef||'').includes('Abogacía') || (d.teacher||'').includes('Delgado');
  const det = details[d.detailKey] || {};
  const mailKey = det.mailKey || 'schedule';
  const delivNote = typeof getDeliverySavedNote === 'function' ? getDeliverySavedNote(d.detailKey) : '';
  return `
  <div class="delivery-row" id="delivery-row-${d.detailKey}" data-delivery-key="${d.detailKey}">
   <div class="delivery-date">${d.date.getDate()}<small>${new Intl.DateTimeFormat('es-ES',{month:'short'}).format(d.date).replace('.','')}</small></div>
   <div style="flex:1;min-width:0">
    <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap">
     <strong style="color:var(--ink);font-size:15px"><button class="teacher-link" data-detail="${d.detailKey}" style="font-weight:800;color:inherit;text-align:left;background:none;border:none;padding:0;cursor:pointer">${d.title} ↗</button></strong>
    </div>
    <div class="delivery-meta" style="margin-top:4px">
     <span>Docente: <button class="teacher-link" data-teacher="${d.teacher}">${d.teacher}${typeof getTeacherGradeBadgeHtml === 'function' ? getTeacherGradeBadgeHtml(d.teacher, true) : ''}</button></span> · 
     <span>Materia: <b>${d.subject}</b></span> · 
     <span>Plazo: <b>${fmtShort(d.date)}</b></span>
    </div>

    <div style="margin-top:8px;display:flex;align-items:center;gap:8px;flex-wrap:wrap">
     <label style="font-size:11.5px;font-weight:700;color:var(--ink-soft)">✍️ Mi nota / observación en esta práctica:</label>
     <input type="text" value="${typeof escapeHtml === 'function' ? escapeHtml(delivNote) : delivNote}" placeholder="Ej. Entregada el 15/10, Apto, 9.5..." oninput="if(typeof saveDeliveryNote==='function') saveDeliveryNote('${d.detailKey}', this.value)" style="padding:4px 9px;border-radius:7px;border:1px solid var(--line-strong);background:var(--paper);color:var(--ink);font-size:12px;font-weight:600;min-width:210px">
    </div>

    <!-- Desplegable con enunciado e instrucciones: cerrado y oculto por defecto -->
    <details class="delivery-details-card">
     <summary class="delivery-summary-toggle">
      <span class="dst-label">
       <span>📋</span> Enunciado, instrucciones y cuestiones a resolver
      </span>
      <span class="dst-arrow">Ver enunciado y detalles ▾</span>
     </summary>
     <div class="delivery-statement-content">
      ${formatDeliveryStatementHtml(det.body || d.details, isAbogacia)}

      <div class="statement-actions-strip" style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding-top:10px;border-top:1px dashed var(--line);margin-top:4px">
       <button class="pill-btn" data-detail="${d.detailKey}">Ficha de detalles ↗</button>
       ${isAbogacia ? `
        <a class="pill-link blue" href="materiales/2026-10-19-caso-practico-delgado-dominguez.md" target="_blank" rel="noopener noreferrer">📄 Guía completa en Markdown (.md) ↗</a>
        <button class="pill-btn blue" data-detail="${mailKey}">✉️ Correo del módulo ↗</button>
        <a class="pill-link blue" href="mailto:secretariatecnico@icacor.org?subject=Entrega%20pr%C3%A1ctica%20MUAP" target="_blank" rel="noopener noreferrer">📩 Enviar a ICACOR ↗</a>
       ` : `
        ${d.detailKey === 'entrega_caso_pr_ctico_de_actos_de' ? `
         <a class="pill-link" href="${casoSandraPdfLocalUrl}" target="_blank" rel="noopener noreferrer">📄 PDF oficial del caso (Sandra Mosteiro) ↗</a>
        ` : ''}
        <a class="pill-link blue" href="${cprocUrl}" target="_blank" rel="noopener noreferrer">Plataforma oficial CPROC ↗</a>
       `}
      </div>
     </div>
    </details>
   </div>
   <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px">
    <button class="delivery-check-btn ${isChk ? 'checked' : ''}" data-delivery-check-key="${d.detailKey}" onclick="event.stopPropagation(); toggleDeliveryCheck('${d.detailKey}', this)">
     <span class="check-box">${isChk ? '✓' : ''}</span>
     <span class="check-text">${isChk ? '✓ Entregada por mí' : 'Marcar como entregada'}</span>
    </button>
    <span class="due-state ${isChk ? 'submitted' : 'pending'}" style="font-size:11px">${isChk ? '✓ Entregada por mí' : '⏳ Pendiente de marcar'}</span>
   </div>
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

 const getNextDueBadgeText = (items) => {
  if(!items.length) return 'Al día ✓';
  const sorted = [...items].sort((a,b) => a.date.getTime() - b.date.getTime());
  return `Próx. vencimiento: ${fmtShort(sorted[0].date)}`;
 };

 if(currentDeliveryFilter === 'pending'){
  const sortedPending = [...filtered].sort((a,b) => a.date.getTime() - b.date.getTime());
  let html = `<div class="delivery-group-header"><span>⏳ Prácticas y tareas pendientes de entrega (${sortedPending.length})</span><span style="font-size:11px;color:var(--honey-dark);font-weight:800">${getNextDueBadgeText(sortedPending)}</span></div>`;
  html += sortedPending.map(renderRow).join('');
  listContainer.innerHTML = html;
 } else if(currentDeliveryFilter === 'completed'){
  listContainer.innerHTML = renderCompletedGroup(filtered);
 } else {
  const pendingItems = filtered.filter(d => !d.submitted).sort((a,b) => a.date.getTime() - b.date.getTime());
  const completedItems = filtered.filter(d => d.submitted);
  let html = '';
  if(pendingItems.length){
   html += `<div class="delivery-group-header"><span>⏳ Prácticas y tareas pendientes de entrega (${pendingItems.length})</span><span style="font-size:11px;color:var(--honey-dark);font-weight:800">${getNextDueBadgeText(pendingItems)}</span></div>`;
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
    # 11 & 12. INICIALIZAR CONTADORES Y RENDERIZADO AL ARRANCAR (ANTES Y DESPUÉS DEL ARRANQUE)
    # -------------------------------------------------------------
    html = html.replace('⭐ Ver notas y tests (10/10) →', '⭐ Ver mi cuaderno de notas y tests →')

    pre_boot_target = 'applyTheme(null, false);\n\nrenderDay();'
    if pre_boot_target in html:
        html = html.replace(
            pre_boot_target,
            """applyTheme(null, false);

// Sincronizar estado de entregas con localStorage antes del primer renderizado
deliveries.forEach(d => {
  d.submitted = isDeliveryChecked(d.detailKey);
  d.status = d.submitted ? 'Entregada por mí ✓' : '⏳ Pendiente de marcar';
});

renderDay();""",
            1
        )

    target_boot_call = 'renderMail();'
    idx_mail_call = html.rfind(target_boot_call)
    if idx_mail_call != -1:
        student_boot = """
// Sincronizar entregas y notas con localStorage en el portal de estudiantes
deliveries.forEach(d => {
  d.submitted = isDeliveryChecked(d.detailKey);
  d.status = d.submitted ? 'Entregada por mí ✓' : '⏳ Pendiente de marcar';
});
if(typeof updateDeliveryCounts === 'function') updateDeliveryCounts();
if(typeof renderHomePendingTasks === 'function') renderHomePendingTasks();
if(typeof renderSidebarPendingItems === 'function') renderSidebarPendingItems();
if(typeof renderDeliveries === 'function') renderDeliveries();
if(typeof updateHomeGradesBadge === 'function') updateHomeGradesBadge();
if(typeof renderCalendar === 'function') renderCalendar();
"""
        insert_pos = idx_mail_call + len(target_boot_call)
        html = html[:insert_pos] + student_boot + html[insert_pos:]
        print("✓ Secuencia de arranque del portal de estudiantes insertada limpiamente al final del script.")

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

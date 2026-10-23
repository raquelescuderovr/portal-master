# Portal Académico · Máster en Abogacía y Procura (MUAP)

Portal personal de seguimiento académico del **Máster Universitario en Abogacía y Procura**, diseñado en un único archivo (`index.html`) con HTML, CSS y JavaScript nativos, sin dependencias externas.

🔗 **Web publicada (Personal de Raquel):** [https://raquelescuderovr.github.io/portal-master/](https://raquelescuderovr.github.io/portal-master/)  
🎓 **Portal para Estudiantes (Compartido):** [https://raquelescuderovr.github.io/portal-master/portal-estudiantes.html](https://raquelescuderovr.github.io/portal-master/portal-estudiantes.html) o [https://raquelescuderovr.github.io/portal-master/estudiantes.html](https://raquelescuderovr.github.io/portal-master/estudiantes.html)

---

## Estado actual (actualizado a 19 de octubre de 2026)

- **Selector de tema (Modo Noche / Modo Día / Automático):**
  - Selector accesible en la cabecera que permite alternar entre `🌙 Noche`, `☀️ Día` y `💻 Auto`.
  - El modo automático detecta la preferencia del sistema operativo o navegador (`prefers-color-scheme`).
  - Persistencia automática de la preferencia elegida en `localStorage`.
- **Accesibilidad y contraste en filtros:**
  - Optimización visual con contraste reforzado y variables semánticas para los botones y selectores de filtro de estado tanto en modo claro como en modo oscuro.
- **Vista de materias y vinculación interactiva:**
  - Vinculación bidireccional entre asignaturas y docentes asignados, con acceso directo a la ficha de cada profesor.
  - Detección y distintivo automático `🔥 Hoy` en las materias con clases programadas para la jornada actual.
  - Modo de visualización cronológica completa de todas las asignaturas del curso además de las materias en curso.
- **Menú de la izquierda (árbol jerárquico completo e interactivo):**
  - Incorpora en la barra lateral izquierda la jerarquía en 5 niveles:
    **`Abogado / Procurador ➔ Bloque del máster ➔ Asignatura ➔ Profesor (con días y horas de clase) ➔ Material del profesor`**.
  - Cada nivel es colapsable/desplegable (`<details>`) con acceso directo a fichas, bloques y recursos.
  - Filtro interactivo en el menú izquierdo:
    - **`⏳ Por venir (no impartidos)`** (activo por defecto): muestra de inmediato los docentes con sesiones a partir de hoy, destacando las sesiones del día.
    - **`🗓️ Todo el curso`**: despliega todos los bloques y el claustro al completo.
- **Días y horas exactas por profesor:**
  - Desglose cronológico de cada sesión con fecha, día de la semana, horario (`16:30–18:30`, `18:45–20:45`, etc.), número de horas, tema específico y sede (Colegio de Abogados, Juzgado de 1.ª Instancia n.º 4, etc.).
  - Distintivos visuales de estado: `🔥 Hoy` (lunes 19 oct), `⏳ Por venir` o `✓ Ya impartida`.
- **Sesiones de hoy (lunes 19 de octubre de 2026):**
  - **Sandra Mosteiro Costa** (Procura · *Actos de comunicación judicial*): 16:30 – 18:30 (Colegio de Abogados). Materiales recibidos el 15 oct (4 documentos disponibles).
  - **José Luis Delgado Domínguez** (Abogacía · *Responsabilidad civil y penal, aseguramiento y turno de oficio*): 18:45 – 20:45 (Colegio de Abogados). Documentación recibida el 16 oct.
- **Profesorado completo (29 docentes) y división en 3 apartados (`correos` / `prácticas` / `apuntes`):**
  - Cada docente cuenta con sus sesiones cronológicas y sus recursos divididos de forma homogénea en 3 bloques (además de la calificación y evaluación):
    1. ✉️ **Correos:** correos y comunicaciones directas (con enlace a Outlook).
    2. ✍️ **Prácticas:** casos prácticos, pruebas y tests (con acceso a CPROC).
    3. 📚 **Apuntes:** documentos, esquemas y presentaciones (con acceso directo a Drive).
  - En los docentes que aún no han impartido clase o no tienen materiales enviados todavía, los campos permanecen vacíos (`[]`) pero los apartados se mantienen visibles con un estado informativo para facilitar su cumplimentación progresiva.
- **Calificaciones y tests al día:**
  - **10 / 10 (Sobresaliente)** en la evaluación inicial de *Técnicas instrumentales · Procura* (comunicada el 14 oct).
  - **20 / 20 (100 %)** en el test online de *Justicia digital y proceso telemático* (16 oct).
  - **4 / 4 prácticas completadas y enviadas en CPROC** (0 vencidas).

---

## Estructura del repositorio

```text
.
├── index.html                                                      # Portal completo (HTML + CSS + JS)
├── README.md                                                       # Documentación y estado del proyecto
└── historial-tests/
    ├── 2026-10-16-procura-deontologia-tecnicas-transversales.md    # Apuntes y 20 preguntas resueltas del test
    └── originales/
        └── 2026-10-16-testmoz-15705122.html                        # Copia HTML original de la revisión en Testmoz
```

---

## Uso local

No requiere instalación ni compilación. Basta con abrir `index.html` directamente en cualquier navegador o servir la carpeta con un servidor estático local:

```bash
python3 -m http.server 8000
```

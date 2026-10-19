# 🤖 Bot de Telegram · Asistente del Máster

Bot en Python nativo (sin dependencias externas) que te permite alimentar y actualizar tu portal académico ([raquelescuderovr.github.io/portal-master](https://raquelescuderovr.github.io/portal-master/)) directamente desde el móvil:

1. **Reenvío de correos:** Reenvía cualquier correo de `master.abogacia@icacor.org`, `accesoabogaciaprocura@...` o UDC.
2. **Capturas de CEPROC:** Envía una foto o pantallazo de una tarea y se extraen los plazos, el profesor y la entrega.
3. **Consultas rápidas:** `/hoy` (horario de hoy), `/entregas` (estado de prácticas), `/web` (enlace al portal).

---

## 🚀 Pasos para activarlo en 2 minutos

### Paso 1: Crear tu Bot en Telegram (Desde el móvil o PC)
1. Abre Telegram y busca **`@BotFather`** (el bot oficial con la insignia azul).
2. Escribe `/newbot`.
3. Dale un nombre visible (ejemplo: `Máster Raquel`).
4. Elige un usuario que termine en `bot` (ejemplo: `raquel_master_bot`).
5. BotFather te dará un **Token** como este:  
   `7482910482:AAFlw9-xK3J98Z_Abc123...`

### Paso 2: Configurar las variables
Copia `.env.example` a `.env` en la carpeta `telegram-bot/` y pega tu token:
```bash
TELEGRAM_BOT_TOKEN="tu_token_aqui"
```

### Paso 3: Ejecutar el bot
* **En tu Mac:**
  ```bash
  python3 telegram-bot/bot.py
  ```
* **24/7 en la nube (Render / Railway / Fly.io):**
  Solo tienes que conectar tu repositorio de GitHub a un servicio como Render (Background Worker gratuito) con el `Procfile` incluido y añadir tu `TELEGRAM_BOT_TOKEN` y `GITHUB_TOKEN`.

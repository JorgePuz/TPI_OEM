# ─────────────────────────────────────────────
# bot.py — Punto de entrada del bot de Telegram
# ─────────────────────────────────────────────

import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes
)
from fsm import procesar_mensaje, reiniciar_sesion

# ── 1. CARGAR EL TOKEN ────────────────────────
# Lee el archivo .env y carga el TOKEN del bot
load_dotenv()
TOKEN = os.getenv("TOKEN")


# ── 2. HANDLER DE /start ──────────────────────
# Se ejecuta cuando el usuario escribe /start
async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    chat_id = update.effective_chat.id
    
    # Reinicia la sesión del usuario en la FSM
    reiniciar_sesion(chat_id)
    
    await update.message.reply_text(
        "Bienvenido al Bot de Gestion de Vacaciones de Bikes Benitez S.A.\n\n"
        "Por favor ingresa tu numero de legajo para comenzar.\n"
        "Ejemplo: EMP001"
    )


# ── 3. HANDLER DE /cancelar ───────────────────
# Se ejecuta cuando el usuario escribe /cancelar
async def comando_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    chat_id = update.effective_chat.id
    
    # Reinicia la sesión del usuario
    reiniciar_sesion(chat_id)
    
    await update.message.reply_text(
        "Operacion cancelada.\n"
        "Tu sesion fue reiniciada.\n\n"
        "Cuando quieras comenzar de nuevo, "
        "ingresa tu legajo."
    )


# ── 4. HANDLER DE /ayuda ──────────────────────
# Se ejecuta cuando el usuario escribe /ayuda
async def comando_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    await update.message.reply_text(
        "COMANDOS DISPONIBLES:\n\n"
        "/start    → Inicia el proceso\n"
        "/cancelar → Cancela y reinicia\n"
        "/ayuda    → Muestra esta ayuda\n\n"
        "COMO USAR EL BOT:\n\n"
        "1. Ingresa tu legajo (ej: EMP001)\n"
        "2. Elegis que queres hacer:\n"
        "   1 = Consultar saldo de dias\n"
        "   2 = Solicitar vacaciones\n"
        "3. Si elegis solicitar, ingresa\n"
        "   la fecha y la cantidad de dias."
    )


# ── 5. HANDLER DE MENSAJES DE TEXTO ──────────
# Se ejecuta con CUALQUIER mensaje que no sea
# un comando (es decir, texto normal)
async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    # Obtenemos el ID del chat (identifica al usuario)
    chat_id = update.effective_chat.id
    
    # Obtenemos el texto que escribió el usuario
    texto = update.message.text.strip()
    
    # Pasamos el mensaje a la FSM para que lo procese
    # y nos devuelva la respuesta correspondiente
    respuesta = procesar_mensaje(chat_id, texto)
    
    # Enviamos la respuesta de vuelta al usuario
    await update.message.reply_text(respuesta)


# ── 6. FUNCION PRINCIPAL ──────────────────────
# Acá se inicializa y arranca el bot
def main():
    
    # Verificar que el token esté cargado
    if not TOKEN:
        print("ERROR: No se encontro el TOKEN.")
        print("Verificá que el archivo .env exista")
        print("y contenga: TOKEN=tu_token_aqui")
        return
    
    print("Iniciando bot...")
    
    # Crear la aplicación con el token del bot
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Registrar los handlers de comandos
    app.add_handler(CommandHandler("start",    comando_start))
    app.add_handler(CommandHandler("cancelar", comando_cancelar))
    app.add_handler(CommandHandler("ayuda",    comando_ayuda))
    
    # Registrar el handler de mensajes de texto
    # filters.TEXT captura todo mensaje de texto
    # ~filters.COMMAND excluye los comandos (/)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        manejar_mensaje
    ))
    
    print("Bot funcionando. Presiona Ctrl+C para detener.")
    
    # Arrancar el bot (queda escuchando mensajes)
    app.run_polling()


# ── 7. PUNTO DE ENTRADA ───────────────────────
# Esto hace que main() se ejecute solo cuando
# corres el archivo directamente con Python
if __name__ == "__main__":
    main()
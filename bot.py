from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

import pandas as pd

# ============================================
# TOKEN DEL BOT
# ============================================

TOKEN = "8749525848:AAHBvPwmQ3oF2a-Yhg8jH69NRL2RHUhmMpA"

# ============================================
# CARGAR BASE DE DATOS
# ============================================

archivo_excel = "empleados.xlsx"

# ============================================
# ESTADOS
# ============================================

usuarios = {}

# ============================================
# COMANDO /start
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    usuarios[user_id] = {
        "estado": "esperando_nombre"
    }

    await update.message.reply_text(
        "Bienvenido al Bot de Vacaciones.\n"
        "Ingrese su nombre:"
    )

# ============================================
# MANEJO DE MENSAJES
# ============================================

async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    texto = update.message.text.lower()

    if user_id not in usuarios:
        await update.message.reply_text(
            "Escriba /start para comenzar."
        )
        return

    estado = usuarios[user_id]["estado"]

    # ============================================
    # ESTADO: ESPERANDO NOMBRE
    # ============================================

    if estado == "esperando_nombre":

        df = pd.read_excel(archivo_excel)

        empleado = df[
            df["nombre"].str.lower() == texto
        ]

        if empleado.empty:

            await update.message.reply_text(
                "Empleado no encontrado."
            )

            return

        usuarios[user_id]["nombre"] = texto
        usuarios[user_id]["estado"] = "esperando_dias"

        dias = empleado.iloc[0]["dias_disponibles"]

        await update.message.reply_text(
            f"Empleado encontrado.\n"
            f"Días disponibles: {dias}\n\n"
            f"Ingrese cantidad de días:"
        )

    # ============================================
    # ESTADO: ESPERANDO DÍAS
    # ============================================

    elif estado == "esperando_dias":

        if not texto.isdigit():

            await update.message.reply_text(
                "Ingrese un número válido."
            )

            return

        dias_solicitados = int(texto)

        df = pd.read_excel(archivo_excel)

        nombre = usuarios[user_id]["nombre"]

        empleado = df[
            df["nombre"].str.lower() == nombre
        ]

        saldo = empleado.iloc[0]["dias_disponibles"]

        # ============================================
        # VALIDAR SALDO
        # ============================================

        if dias_solicitados <= saldo:

            nuevo_saldo = saldo - dias_solicitados

            indice = empleado.index[0]

            df.at[indice, "dias_disponibles"] = nuevo_saldo

            df.to_excel(archivo_excel, index=False)

            await update.message.reply_text(
                "Vacaciones aprobadas.\n"
                f"Saldo restante: {nuevo_saldo}"
            )

        else:

            await update.message.reply_text(
                "Saldo insuficiente."
            )

        usuarios[user_id]["estado"] = "finalizado"

# ============================================
# MAIN
# ============================================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(filters.TEXT, manejar_mensaje)
)

print("Bot funcionando...")

app.run_polling()
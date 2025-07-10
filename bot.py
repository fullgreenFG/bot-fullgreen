from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = "8080496078:AAES4ghFOnxUwBLZJvCicyx-0LtSyJmlOQg"

CHOOSING, SUREBET, LAY = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Calcular Surebet", "Calcular Lay"]]
    await update.message.reply_text(
        "Fala, fenômeno! O que você quer calcular hoje?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return CHOOSING

async def choosing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if "Surebet" in choice:
        await update.message.reply_text("Manda as odds das duas casas separadas por espaço (ex: 2.10 1.95)")
        return SUREBET
    if "Lay" in choice:
        await update.message.reply_text("Manda a odd back, odd lay e o stake separados por espaço (ex: 2.20 2.12 100)")
        return LAY
    await update.message.reply_text("Opção inválida.")
    return CHOOSING

async def calc_surebet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        odd1, odd2 = map(float, update.message.text.strip().split())
        inv1 = 1/odd1
        inv2 = 1/odd2
        surebet = (inv1 + inv2) * 100
        lucro = 100 - surebet
        await update.message.reply_text(f"Surebet: {surebet:.2f}%\nLucro garantido: {lucro:.2f}% sobre o investimento.")
    except:
        await update.message.reply_text("Envia no formato: 2.10 1.95")
    return ConversationHandler.END

async def calc_lay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        odd_back, odd_lay, stake = map(float, update.message.text.strip().split())
        lay_stake = (odd_back * stake) / (odd_lay - 0.05)
        await update.message.reply_text(f"Valor a apostar no Lay: R$ {lay_stake:.2f}")
    except:
        await update.message.reply_text("Envia no formato: 2.20 2.12 100")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choosing)],
            SUREBET: [MessageHandler(filters.TEXT & ~filters.COMMAND, calc_surebet)],
            LAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, calc_lay)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)
import os

TOKEN = os.environ.get("TOKEN")

# Estados da conversa
ODD1, STAKE1, LAY_ODD, FREEBET = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🟩 FULL GREEN | CÁLCULO APOSTA SEGURA 🟩\n\n"
        "Vamos começar!\n\n"
        "Me informe a odd da entrada 1:"
    )
    return ODD1

async def receber_odd1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        odd1 = float(update.message.text.replace(",", "."))
        context.user_data["odd1"] = round(odd1, 2)
    except:
        await update.message.reply_text("Por favor, digite uma odd válida (apenas números).")
        return ODD1
    await update.message.reply_text("Agora, informe o valor apostado na entrada 1 (ex: 10):")
    return STAKE1

async def receber_stake1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        stake1 = float(update.message.text.replace(",", "."))
        context.user_data["stake1"] = round(stake1, 2)
    except:
        await update.message.reply_text("Por favor, digite um valor válido (apenas números).")
        return STAKE1
    await update.message.reply_text("Informe agora a odd da aposta lay (ex: 8):")
    return LAY_ODD

async def receber_lay_odd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        lay_odd = float(update.message.text.replace(",", "."))
        context.user_data["lay_odd"] = round(lay_odd, 2)
    except:
        await update.message.reply_text("Por favor, digite uma odd válida (apenas números).")
        return LAY_ODD
    await update.message.reply_text("Por fim, informe o valor da freebet (ex: 10):")
    return FREEBET

async def receber_freebet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        freebet = float(update.message.text.replace(",", "."))
        context.user_data["freebet"] = round(freebet, 2)
    except:
        await update.message.reply_text("Por favor, digite um valor válido (apenas números).")
        return FREEBET

    # Pegando todas as variáveis
    odd1 = context.user_data["odd1"]
    stake1 = context.user_data["stake1"]
    lay_odd = context.user_data["lay_odd"]
    freebet = context.user_data["freebet"]
    commission = 0.045  # 4,5%

    # Cálculos (tudo com DUAS casas decimais)
    lay = (stake1 * (odd1 - 1) + stake1 - (freebet * 0.7)) / (lay_odd - commission)
    lay = round(lay, 2)
    responsa = round((lay_odd * lay) - lay, 2)
    casa = round(odd1 * stake1 - stake1 - responsa, 2)
    i12 = round(commission * lay, 2)
    exchange = round(lay - stake1 - i12, 2)
    freebet_girar = casa

    # Mensagem visual Full Green
    mensagem = (
        "🟩 FULL GREEN | APURADO NA APOSTA SEGURA 🟩\n\n"
        "🔢 Dados informados:\n"
        f"• Odd entrada 1: {odd1:.2f}\n"
        f"• Valor apostado na entrada 1: R$ {stake1:.2f}\n"
        f"• Odd da aposta lay: {lay_odd:.2f}\n"
        f"• Valor da freebet: R$ {freebet:.2f}\n"
        "------------------------------------------\n\n"
        f"💰 Valor a apostar no Lay: R$ {lay:.2f}\n"
        f"🛡 Responsabilidade (saldo necessário): R$ {responsa:.2f}\n\n"
        f"🏠 Se bater na casa: R$ {casa:.2f}\n"
        f"🏦 Se bater na exchange: R$ {exchange:.2f}\n"
        f"🎁 Lucro ao girar a freebet: R$ {freebet_girar:.2f}\n"
        "------------------------------------------\n"
        "🟢 E lembre-se sempre: sorte é para quem não tem método! 🧠"
    )

    await update.message.reply_text(mensagem)
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ODD1: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_odd1)],
            STAKE1: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_stake1)],
            LAY_ODD: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_lay_odd)],
            FREEBET: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_freebet)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()

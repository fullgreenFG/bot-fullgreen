from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
    ConversationHandler, filters
)
import os

TOKEN = os.environ.get("TOKEN")

# Estados da conversa
ESCOLHER_ENTRADAS, RECEBER_ODDS, RECEBER_STAKE = range(3)

# Dados temporários
user_data_dict = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🟩 *FULL GREEN | CALCULADORA SUREBET*\n\n"
        "Quantas entradas (resultados diferentes) tem sua surebet?\n\n"
        "Responda com um número de 2 a 5.",
        parse_mode='Markdown'
    )
    return ESCOLHER_ENTRADAS

async def escolher_entradas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    if not msg.isdigit() or int(msg) < 2 or int(msg) > 5:
        await update.message.reply_text("Por favor, escolha um número entre 2 e 5.")
        return ESCOLHER_ENTRADAS
    entradas = int(msg)
    context.user_data['entradas'] = entradas
    await update.message.reply_text(
        f"Ótimo! Agora envie as odds das {entradas} entradas, separadas por espaço.\n"
        "Exemplo: 2.10 3.25 7.00"
    )
    return RECEBER_ODDS

async def receber_odds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    odds_text = update.message.text.strip().replace(",", ".")
    odds = odds_text.split()
    entradas = context.user_data['entradas']
    if len(odds) != entradas:
        await update.message.reply_text(f"Você precisa informar {entradas} odds. Tente novamente.")
        return RECEBER_ODDS
    try:
        odds = [float(o) for o in odds]
    except ValueError:
        await update.message.reply_text("Digite apenas números válidos para as odds.")
        return RECEBER_ODDS
    context.user_data['odds'] = odds
    await update.message.reply_text(
        f"Agora, informe o valor da aposta (stake) da primeira entrada. Exemplo: 100"
    )
    return RECEBER_STAKE

async def receber_stake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stake_text = update.message.text.strip().replace(",", ".")
    try:
        stake1 = float(stake_text)
    except ValueError:
        await update.message.reply_text("Digite um valor numérico válido para o stake.")
        return RECEBER_STAKE

    odds = context.user_data['odds']
    entradas = context.user_data['entradas']

    # Calcula stakes para todas entradas
    investido = stake1
    stakes = [stake1]
    for i in range(1, entradas):
        stake_i = (stake1 * odds[0]) / odds[i]
        stakes.append(stake_i)
        investido += stake_i

    # Calcula lucro garantido para cada cenário
    lucros = [stake1 * odds[0] - investido]
    for i in range(1, entradas):
        lucros.append(stakes[i] * odds[i] - investido)
    lucro_min = min(lucros)

    # Monta tabela visual
    tabela = (
        "🟩 *FULL GREEN | CÁLCULO SUREBET*\n\n"
        "| # | Odd     | Aposta        | Lucro Garantido |\n"
        "|---|---------|---------------|-----------------|\n"
    )
    for i in range(entradas):
        tabela += f"| {i+1} | {odds[i]:.2f}   | R$ {stakes[i]:.2f}      | R$ {lucros[i]:.2f} |\n"
    tabela += (
        "|---|---------|---------------|-----------------|\n"
        f"*Aposta total:* R$ {investido:.2f}\n"
        f"✅ *Lucro garantido:* R$ {lucro_min:.2f} ({lucro_min/investido*100:.2f}%)"
    )

    await update.message.reply_text(
        tabela,
        parse_mode='Markdown'
    )
    await update.message.reply_text(
        "🟢 E lembre-se sempre: sorte é para quem não tem método! 🧠"
    )
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ESCOLHER_ENTRADAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, escolher_entradas)],
            RECEBER_ODDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_odds)],
            RECEBER_STAKE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_stake)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()

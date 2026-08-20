#!/usr/bin/env python3
import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

TELEGRAM_TOKEN = "8849803431:AAEPi0FseWHGh6-EmgfAEvws1mLT9-XZDoU"
GROQ_API_KEY = "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"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
groq_client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Siz O'zbekiston buxgalterlari uchun AI yordamchisisiz.
Qisqa, aniq, amaliy javob bering. Emoji ishlating.

QQS: 12% stavka. Ajratish: Narx*12/112. Qo'shish: Narx*0.12. Hisobot: oyning 20-sanasiga qadar.
Foyda solig'i: 15%. Daromad solig'i: 12%.
INPS: ish beruvchi 12%, ishchi 8%. JSDS: 0.5-3%.
Mehnat ta'tili: 15 kun/yil. Kasallik: staj 8y=60%, 8-15y=80%, 15+y=100%.
Homiladorlik: 126 kun. Ishdan bo'shatish: 2 oy ogohlantirish, 2 oylik kompensatsiya.
Bola nafaqasi: my.gov.uz dan. EDS: e-imzo.uz dan. Didox faktura muddati: 5 kun.
Yuridik shaxs ro'yxat: my.gov.uz, bepul, 1 kun."""

def keyboard():
    return ReplyKeyboardMarkup([
        ["💰 QQS", "👷 Mehnat"],
        ["🏛️ Nafaqa", "🏦 INPS/JSDS"],
        ["📄 Didox", "🏷️ MXIK"],
        ["📊 Soliq", "🏢 Ro'yxat"]
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom! Men BuxYordamUzBot!\n\n"
        "💰 QQS, 👷 Mehnat, 🏛️ Nafaqa,\n"
        "🏦 INPS, 📄 Didox, 🏷️ MXIK\n\n"
        "Savolingizni yozing! 👇",
        reply_markup=keyboard()
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    mapping = {
        "💰 QQS": "QQS hisoblash haqida ayt",
        "👷 Mehnat": "Mehnat huquqlari haqida ayt",
        "🏛️ Nafaqa": "Nafaqalar haqida ayt",
        "🏦 INPS/JSDS": "INPS va JSDS haqida ayt",
        "📄 Didox": "Didox elektron faktura haqida ayt",
        "🏷️ MXIK": "MXIK kodlari haqida ayt",
        "📊 Soliq": "Soliq xizmatlari haqida ayt",
        "🏢 Ro'yxat": "Yuridik shaxs ro'yxatga olish haqida ayt",
    }
    question = mapping.get(text, text)
    await update.message.chat.send_action("typing")
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            max_tokens=600,
            temperature=0.2
        )
        answer = response.choices[0].message.content
        await update.message.reply_text(answer[:4000], reply_markup=keyboard())
    except Exception as e:
        logger.error(f"Xato: {e}")
        await update.message.reply_text("⚠️ Xatolik. Qayta urining.", reply_markup=keyboard())

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("✅ Bot ishga tushdi!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

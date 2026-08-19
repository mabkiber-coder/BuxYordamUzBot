#!/usr/bin/env python3
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

TELEGRAM_TOKEN = "8849803431:AAEPi0FseWHGh6-EmgfAEvws1mLT9-XZDoU"
GROQ_API_KEY = "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"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
groq_client = Groq(api_key=GROQ_API_KEY)
SYSTEM_PROMPT = """Siz O'zbekiston buxgalterlari va tadbirkorlari uchun professional AI yordamchisisiz.
Faqat O'zbekiston qonunchiligiga asosan javob bering. Javoblar qisqa, aniq, amaliy bo'lsin. Emoji ishlating.

=== SOLIQ.UZ — BARCHA XIZMATLAR ===
QQS (Qo'shilgan qiymat solig'i):
- Stavka: 12% (2024)
- QQS ajratish: Narx × 12 / 112
- QQS qo'shish: Narx × 0.12
- Hisobot: har oyning 20-sanasiga qadar
- QQS to'lovchi: yillik aylanma 1 mlrd so'mdan oshsa majburiy

Foyda solig'i: 15% (yuridik shaxslar)
Daromad solig'i: 12% (jismoniy shaxslar)
Mol-mulk solig'i: 1.5% (kadastr qiymatidan)
Yer solig'i: belgilangan me'yor bo'yicha
Suv resurslari solig'i: hajmga qarab

Soliq rejimlari:
- Umumiy tartib: QQS + foyda solig'i
- Soddalashtirilgan: yillik aylanma 1 mlrd gacha, QQS to'lanmaydi

Soliq hisobotlari muddatlari:
- QQS: har oyning 20-sanasi
- Foyda solig'i: chorak oxiridan 25 kun ichida
- Yillik deklaratsiya: mart 1-sanasiga qadar

Soliq xizmatlari online:
- my.soliq.uz — shaxsiy kabinet, qarzdorlik, hisobot
- soliq.uz — qonunlar, me'yorlar, yangiliklar

YURIDIK SHAXS GUVOHNOMASI (Davlat ro'yxatidan o'tkazish):
- Olish joyi: my.gov.uz → "Tadbirkorlik" → "Yuridik shaxsni ro'yxatdan o'tkazish"
- Yoki: business.reg.uz saytida
- Hujjatlar: Ariza, Ustav, Asoschining qarori, Passport nusxasi
- Muddati: 1 ish kuni (elektron)
- Narxi: BEPUL (2021-yildan davlat boji bekor qilindi)
- Natija: STIR (INN) va Guvohnoma beriladi

Yakka tartibli tadbirkor (YaTT) ro'yxati:
- my.gov.uz → "Yakka tartibli tadbirkorni ro'yxatdan o'tkazish"
- Hujjat: Passport, ariza
- Muddati: 1 kun, BEPUL

=== MY.MEHNAT.UZ — TO'LIQ TIZIM ===
Ishchi qo'shish (mehnat shartnomasi tuzish):
- my.mehnat.uz ga kirish (EDS yoki OneID bilan)
- "Mehnat shartnomalari" → "Yangi shartnoma"
- Kiritiladi: Ishchi FIO, PINFL, lavozim, ish haqi, boshlanish sanasi
- Shartnoma turlari: Muddatsiz, Belgilangan muddatli (max 5 yil), Mavsumiy
- MUHIM: 3 kun ichida ro'yxatdan o'tkazish shart!

Ishchi bo'shatish:
- my.mehnat.uz → "Shartnomani bekor qilish"
- Sabablar: o'z xohishi, kelishuv, qisqartirish, intizom
- Ogohlantirish: 2 oy oldin (qisqartirish uchun)
- Kompensatsiya: 2 oylik o'rtacha ish haqi (qisqartirish)
- Hisob-kitob: oxirgi ish kunida

Mehnat ta'tili:
- Asosiy: 15 ish kuni/yil
- +1 kun har 2 yil uchun (max 21 kun)
- Pul bilan almashtirish: faqat qo'shimcha qismi
- Grafik: yanvar oyida tuziladi

Kasallik varaqasi:
- Staj 8 yilgacha: 60%
- Staj 8-15 yil: 80%
- Staj 15+ yil: 100%
- To'lov: o'rtacha kunlik ish haqidan

Homiladorlik:
- Ta'til: 126 kun (70+56)
- Qiyin tug'ruq: 140 kun (70+70)
- Bola parvarish: 3 yoshgacha, ish joyi saqlanadi
- To'lov: o'rtacha ish haqidan, mib.uz orqali

Ish vaqti:
- Kuniga 8 soat, haftasiga 40 soat
- Qisqartirilgan: 16 yoshgacha 24 soat/hafta, 16-18 yosh 36 soat
- Tungi ish: 22:00-06:00, 20% ustama
- Qo'shimcha ish: kuniga 2 soat, oyiga 4 soat, yiliga 120 soat max

Ish haqi:
- Minimal ish haqi (MIH): 980,000 so'm (2024)
- To'lash muddati: oyda 2 marta yoki bir marta (shartnomaga qarab)
- Kechiktirilsa: har kun uchun ustama to'lanadi

=== DIDOX — TO'LIQ XUJJATLAR ===
Elektron faktura (Hisob-faktura):
- Yaratish: didox.uz → "Yangi hujjat" → "Faktura"
- Majburiy maydonlar: Sana, Raqam, Sotuvchi/Xaridor INN, Tovar/xizmat, MXIK kodi, Miqdor, Narx, QQS
- Muddati: tovar/xizmatdan 5 kun ichida
- Imzolash: EDS bilan
- MXIK kodi: tasnif.soliq.uz dan tekshirish

Ishonchнома (Доверенность):
- Didox → "Yangi hujjat" → "Ishonchнома"
- Yoki erkin shaklda: Word da yozib, EDS bilan imzolash
- Majburiy: Kim berdi (Ishonch beruvchi), Kimga berildi, Nima uchun, Muddati
- Notarial tasdiqlash: faqat ko'chmas mulk, meros, sud uchun

Shartnoma (Договор):
- Didox → "Yangi hujjat" → "Shartnoma"
- Yoki erkin shaklda tuzib, ikki tomon EDS imzosi
- Turlari: Yetkazib berish, Xizmat ko'rsatish, Ijara, Pudrat, Qarz
- Raqam va sana: majburiy
- Predmet, Narx, Muddat, Tomonlar: majburiy bo'limlar

Erkin shakldagi hujjatlar:
- Didox → "Erkin shakl" yoki Word da yozish
- Akt (Qabul-topshirish dalolati), Xat, Bildirishnoma va h.k.
- Ikki tomon EDS bilan imzolaydi

EDS (Elektron raqamli imzo):
- Olish: e-imzo.uz
- Narxi: 180,000 so'm/yil (jismoniy), 360,000 so'm/yil (yuridik)
- Muddati: 1 yil, keyin yangilanadi
- Ishlatish: Didox, my.mehnat.uz, soliq.uz, my.gov.uz

Keng tarqalgan xatolar:
- INN/STIR noto'g'ri
- MXIK kodi mos kelmaydi
- EDS muddati o'tgan
- Faktura muddati o'tgan (5 kundan keyin)
- Tovar nomi va MXIK mos emas

=== MIB.UZ — IJTIMOIY SУГУРТА ===
INPS (Pensiya sug'urtasi) 2024:
- Ish beruvchi: 12%
- Ishchi: 8%
- Hisoblash: Ish haqi × stavka / 100
- Misol: 3,000,000 so'm ish haqi
  Ish beruvchi: 360,000 so'm
  Ishchi: 240,000 so'm

JSDS (Jarohatlanish sug'urtasi):
- Xavfsiz: 0.5%
- O'rtacha xavfli: 1-2%
- Xavfli: 3%

Hisobot: har oyning 15-sanasiga qadar mib.uz

=== MY.GOV.UZ — DAVLAT XIZMATLARI ===
Yuridik shaxs:
- Ro'yxatga olish: my.gov.uz → "Tadbirkorlik"
- Guvohnoma olish: avtomatik (elektron)
- STIR olish: ro'yxatdan o'tganda beriladi
- Ustav o'zgartirish: my.gov.uz → "Yuridik shaxs ma'lumotlarini o'zgartirish"
- Tugatish (likvidatsiya): my.gov.uz → "Yuridik shaxsni tugatish"

YaTT:
- Ro'yxat: my.gov.uz, 1 kun, bepul
- Patent: soliq.uz dan
- Tugatish: my.gov.uz, 1 kun

Nafaqalar:
- Bola tug'ilganda: my.gov.uz → "Ijtimoiy xizmatlar"
- Homiladorlik: my.gov.uz
- Nogironlik: my.gov.uz → "Ijtimoiy himoya"
- Ko'p bolali: mahalla orqali

=== MXIK ===
- Kod qidirish: tasnif.soliq.uz
- 17 xonali to'liq kod
- Markirovka majburiy: kiyim, poyabzal, dori, alkogol, sigareta, sut
- Didox da har bir qatorda MXIK bo'lishi shart

=== BUXGALTERIYA ===
Hisoblar:
- 10: Materiallar
- 20: Ishlab chiqarish
- 50: Kassa
- 51: Bank
- 60: Ta'minotichilar
- 62: Xaridorlar
- 68: Soliqlar
- 69: Ijtimoiy sug'urta
- 70: Ish haqi
- 90: Sotish

Moddiy hisobot:
- KRIM (kirim) + CQIM (chiqim)
- Oy boshi qoldiq + Kirim - Chiqim = Oy oxiri qoldiq

JAVOB QOIDALARI:
1. O'zbek tilida, qisqa va aniq
2. Raqamli misol keltiring
3. Rasmiy sayt havolasini qo'shing
4. 5-10 qator yetarli
5. Noaniq bo'lsa qo'shimcha savol bering"""

def main_keyboard():
    keyboard = [
        ["💰 QQS", "👷 Mehnat"],
        ["🏛️ Nafaqa/Gov", "🏦 INPS/JSDS"],
        ["📄 Didox", "🏷️ MXIK"],
        ["📊 Soliq", "🏢 Ro'yxatga olish"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """👋 Salom! Men **BuxYordamUzBot**!

📚 Quyidagi sohalarda yordam beraman:
💰 QQS va soliqlar
👷 Mehnat (my.mehnat.uz) — ishchi qo'shish/bo'shatish
🏛️ Davlat xizmatlari (my.gov.uz)
🏦 INPS/JSDS (mib.uz)
📄 Didox — faktura, shartnoma, ishonchнома
🏷️ MXIK — tovar kodlari
🏢 Yuridik shaxs/YaTT ro'yxatga olish

❓ Savolingizni yozing! 👇"""
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=main_keyboard())

async def ai_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Tugmalar
    mapping = {
        "💰 QQS": "QQS hisoblash va soliq stavkalari haqida batafsil ayt",
        "👷 Mehnat": "my.mehnat.uz tizimi: ishchi qo'shish, bo'shatish, ta'til, kasallik haqida ayt",
        "🏛️ Nafaqa/Gov": "my.gov.uz orqali nafaqalar va davlat xizmatlari haqida ayt",
        "🏦 INPS/JSDS": "INPS va JSDS stavkalari va hisoblash haqida ayt",
        "📄 Didox": "Didox tizimida faktura, shartnoma, ishonchнома haqida ayt",
        "🏷️ MXIK": "MXIK kodlari va markirovka haqida ayt",
        "📊 Soliq": "soliq.uz xizmatlari va hisobotlar haqida ayt",
        "🏢 Ro'yxatga olish": "Yuridik shaxs va YaTT ro'yxatga olish haqida ayt",
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
            max_tokens=800,
            temperature=0.2
        )
        answer = response.choices[0].message.content
        if len(answer) > 4000:
            for part in [answer[i:i+4000] for i in range(0, len(answer), 4000)]:
                await update.message.reply_text(part, reply_markup=main_keyboard())
        else:
            await update.message.reply_text(answer, reply_markup=main_keyboard())
    except Exception as e:
        logger.error(f"Xato: {e}")
        await update.message.reply_text("⚠️ Xatolik. Qayta urining yoki /start bosing.", reply_markup=main_keyboard())

def main():
    print("🤖 BuxYordamUzBot ishga tushmoqda...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_answer))
    print("✅ Bot tayyor! @BuxYordamUzBot")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

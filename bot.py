"""
Телеграм-бот для создания резюме
Генерирует красивый PDF и текстовое резюме
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters, ContextTypes
)
from resume_generator import generate_pdf, generate_text_resume

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота — вставь свой из @BotFather
BOT_TOKEN = os.getenv("TOKEN")

# Шаги анкеты
(NAME, PROFESSION, EXPERIENCE, SKILLS, EDUCATION, CONTACTS, FORMAT) = range(7)

QUESTIONS = {
    NAME:       "👤 Введи своё *полное имя*:\n_Пример: Иванов Иван Иванович_",
    PROFESSION: "💼 Твоя *профессия / желаемая должность*:\n_Пример: Python-разработчик_",
    EXPERIENCE: "🏢 Опиши свой *опыт работы*:\n_Пример: 2 года в ООО 'Ромашка' — backend разработчик. До этого 1 год фриланс._",
    SKILLS:     "⚡ Твои *навыки* (через запятую):\n_Пример: Python, Django, PostgreSQL, Git, Docker_",
    EDUCATION:  "🎓 *Образование*:\n_Пример: МГТУ им. Баумана, Информатика, 2019_",
    CONTACTS:   "📞 *Контакты* (телефон, email, Telegram, город):\n_Пример: +7 900 000-00-00, ivan@mail.ru, @ivan, Москва_",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я помогу тебе создать *профессиональное резюме* за 2 минуты.\n\n"
        "Отвечай на вопросы — и получишь резюме в PDF и текстовом формате.\n\n"
        "Начнём? 🚀",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Создать резюме", callback_data="start_resume")
        ]])
    )

async def start_resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.message.reply_text(QUESTIONS[NAME], parse_mode="Markdown")
    return NAME

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text(QUESTIONS[PROFESSION], parse_mode="Markdown")
    return PROFESSION

async def handle_profession(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['profession'] = update.message.text
    await update.message.reply_text(QUESTIONS[EXPERIENCE], parse_mode="Markdown")
    return EXPERIENCE

async def handle_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['experience'] = update.message.text
    await update.message.reply_text(QUESTIONS[SKILLS], parse_mode="Markdown")
    return SKILLS

async def handle_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['skills'] = update.message.text
    await update.message.reply_text(QUESTIONS[EDUCATION], parse_mode="Markdown")
    return EDUCATION

async def handle_education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['education'] = update.message.text
    await update.message.reply_text(QUESTIONS[CONTACTS], parse_mode="Markdown")
    return CONTACTS

async def handle_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['contacts'] = update.message.text
    await update.message.reply_text(
        "✨ Отлично! Данные собраны. Выбери формат резюме:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📄 PDF", callback_data="fmt_pdf")],
            [InlineKeyboardButton("📝 Текст в Telegram", callback_data="fmt_text")],
            [InlineKeyboardButton("📄 + 📝 Оба формата", callback_data="fmt_both")],
        ])
    )
    return FORMAT

async def handle_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    fmt = query.data  # fmt_pdf / fmt_text / fmt_both
    data = context.user_data

    await query.message.reply_text("⏳ Генерирую резюме...")

    # Текстовое резюме
    if fmt in ("fmt_text", "fmt_both"):
        text = generate_text_resume(data)
        await query.message.reply_text(text, parse_mode="Markdown")

    # PDF резюме
    if fmt in ("fmt_pdf", "fmt_both"):
        pdf_path = generate_pdf(data)
        with open(pdf_path, "rb") as f:
            await query.message.reply_document(
                document=f,
                filename=f"resume_{data['name'].replace(' ', '_')}.pdf",
                caption="📄 Твоё резюме в PDF"
            )
        os.remove(pdf_path)

    await query.message.reply_text(
        "🎉 Готово! Резюме создано.\n\n"
        "Хочешь создать ещё одно или изменить данные?",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Создать новое резюме", callback_data="start_resume")
        ]])
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Создание резюме отменено. Напиши /start чтобы начать заново.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_resume, pattern="^start_resume$")],
        states={
            NAME:       [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            PROFESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_profession)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_experience)],
            SKILLS:     [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_skills)],
            EDUCATION:  [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_education)],
            CONTACTS:   [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contacts)],
            FORMAT:     [CallbackQueryHandler(handle_format, pattern="^fmt_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)

    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()

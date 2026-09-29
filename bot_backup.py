import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛍️ Welcome to D2S Sale Bot!\n\n"
        "🔥 Latest deals & useful products\n"
        "💰 Amazon offers\n\n"
        "Use /deals to see deals."
    )

async def deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 D2S Sale Deals\n\n"
        "Deals section is coming soon! 🚀"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 D2S Sale Bot Help\n\n"
        "/start - Start bot\n"
        "/deals - Latest deals\n"
        "/help - Help"
    )

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing in .env")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("deals", deals))
    app.add_handler(CommandHandler("help", help_command))

    print("D2S Sale Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

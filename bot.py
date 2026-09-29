import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from deals import fetch_deals, filter_deals

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@D2SSale")
AMAZON_TAG = os.getenv("AMAZON_TAG", "shivazon09-21")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

def is_admin(update: Update):
    return update.effective_user and update.effective_user.id == ADMIN_USER_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛍️ Welcome to D2S Sale Bot!\n\n"
        "🔥 D2S Sale deals\n"
        "💰 Offers & discounts\n\n"
        "Use /help for commands."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 D2S Sale Bot\n\n"
        "/post Product | Price | Old Price | Affiliate Link | Image URL\n"
        "/help - Help"
    )

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ You are not authorized to post deals.")
        return

    if not context.args:
        await update.message.reply_text(
            "Format:\n"
            "/post Product | Price | Old Price | Affiliate Link | Image URL"
        )
        return

    data = " ".join(context.args).split("|")

    if len(data) != 5:
        await update.message.reply_text(
            "❌ Format galat hai.\n\n"
            "/post Product | Price | Old Price | Affiliate Link | Image URL"
        )
        return

    product, price, old_price, link, image_url = [x.strip() for x in data]

    # Add Amazon Associates tag automatically
    if "amazon.in" in link:
        separator = "&" if "?" in link else "?"
        link = f"{link}{separator}tag={AMAZON_TAG}"

    try:
        deal_price = float(price.replace(",", ""))
        original_price = float(old_price.replace(",", ""))
        discount = round((original_price - deal_price) / original_price * 100)
    except (ValueError, ZeroDivisionError):
        discount = 0

    message = (
        "🔥 D2S SALE — DEAL ALERT 🔥\n\n"
        f"🛍️ {product}\n\n"
        f"💰 Deal Price: ₹{price}\n"
        f"🏷️ Old Price: ₹{old_price}\n"
        f"🏷️ {discount}% OFF\n\n"
        "🛒 Tap below to view the deal 👇\n\n"
        "⚠️ Price & availability may change."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 VIEW DEAL", url=link)]
    ])

    try:
        await context.bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=image_url,
            caption=message,
            reply_markup=keyboard
        )
        await update.message.reply_text("✅ Deal channel par post ho gayi!")
    except Exception as e:
        await update.message.reply_text(f"❌ Posting failed: {e}")


async def automatic_deals(app):
    """
    Automatic deal pipeline.
    Amazon API/deal source will be connected here later.
    """
    deals = fetch_deals()
    deals = filter_deals(deals)
    from deals import remove_duplicates
    deals = remove_duplicates(deals)

    if not deals:
        print("No qualifying automatic deals available.")
        return

    for deal in deals:
        print(f"Automatic deal found: {deal.product}")


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN missing in .env")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("post", post))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(automatic_deals, "interval", minutes=30, args=[app])
    scheduler.start()

    print("D2S Sale Bot is running...")
    print("Automatic deal checker: every 30 minutes")
    app.run_polling()

if __name__ == "__main__":
    main()

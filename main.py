from dotenv import load_dotenv
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import bot_sections
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
import open_position
load_dotenv()
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome & navigation menu."""
    await update.message.reply_text(
        "👋 Welcome! Choose an option below:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🧪 Open Position", callback_data=open_position.OPEN_POS)],
            [
                InlineKeyboardButton("📊 Portfolio", callback_data="portfolio"),
                InlineKeyboardButton("💼 Wallet",    callback_data="wallet")
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
                InlineKeyboardButton("❓ Help",     callback_data="help")
            ],
        ])
    )

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    bot_sections.register_handlers(app)
    # /start
    app.add_handler(CommandHandler("start", start_cmd))
    
    # Add new command handlers
    app.add_handler(CommandHandler("open", open_position.open_entry))

    # ---- Open Position flow ----
    app.add_handler(CallbackQueryHandler(open_position.open_entry,      pattern=f"^{open_position.OPEN_POS}$"))
    app.add_handler(CallbackQueryHandler(open_position.show_trending,   pattern=f"^{open_position.TRENDING}$"))
    app.add_handler(CallbackQueryHandler(open_position.paginate_trending, pattern=f"^{open_position.PAGE_PREFIX}\\d+$"))
    app.add_handler(CallbackQueryHandler(open_position.show_pool_detail, pattern=f"^{open_position.TOKEN_PREFIX}\\d+_\\d+$"))
    app.add_handler(CallbackQueryHandler(open_position.manual_entry,    pattern=f"^{open_position.MANUAL}$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,     open_position.handle_manual_text))

    # the remainder of the Open Position flow (strategy → rebalance → amount → preview → confirm)
    app.add_handler(CallbackQueryHandler(open_position.handle_open_pos_click,pattern=f"^{open_position.OPEN_POS_NEXT}$"))
    app.add_handler(CallbackQueryHandler(open_position.handle_strategy, pattern=f"^{open_position.STRAT_SPOT}$|^{open_position.STRAT_SINGLE}$"))
    app.add_handler(CallbackQueryHandler(open_position.handle_rebalance,pattern=f"^{open_position.REB_YES}$|^{open_position.REB_NO}$"))
    app.add_handler(CallbackQueryHandler(open_position.handle_time_selection, 
                                        pattern=f"^{open_position.REBALANCE_15M}$|^{open_position.REBALANCE_30M}$|^{open_position.REBALANCE_1H}$|^{open_position.REBALANCE_3H}$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,     open_position.handle_amount_or_interval))
    app.add_handler(CallbackQueryHandler(open_position.handle_confirm,  pattern=f"^{open_position.CONFIRM_POS}$|^{open_position.CANCEL_POS}$"))

    # ---- Stubs for other modules ----
    stub = lambda u,c: u.callback_query.message.reply_text("🚧 This feature will be activated soon.")
    for cb in ("portfolio","wallet","settings","help"):
        app.add_handler(CallbackQueryHandler(stub, pattern=f"^{cb}$"))

    app.run_polling()

if __name__ == "__main__":
    main()

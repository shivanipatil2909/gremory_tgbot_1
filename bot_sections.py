from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

# -------------------------------
# Callback Identifiers
# -------------------------------
PORTFOLIO = "portfolio"
WALLET = "wallet"
SETTINGS = "settings"
HELP = "help"

SET_VAULT = "set_vault"
SET_PRIORITY = "set_priority"
SET_REBALANCE = "set_rebalance"

PRIORITY_HIGH = "priority_high"
PRIORITY_MEDIUM = "priority_medium"
PRIORITY_VERY_HIGH = "priority_very_high"

REBALANCE_15M = "reb_15m"
REBALANCE_30M = "reb_30m"
REBALANCE_1H = "reb_1h"
REBALANCE_3H = "reb_3h"

# -------------------------------
# Main Menu
# -------------------------------
def start_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Portfolio", callback_data=PORTFOLIO)],
        [InlineKeyboardButton("💼 Wallet", callback_data=WALLET)],
        [InlineKeyboardButton("⚙️ Settings", callback_data=SETTINGS)],
        [InlineKeyboardButton("🧪 Open Position", callback_data="open_pos")],
        [InlineKeyboardButton("❓ Help", callback_data=HELP)]
    ])

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Choose an option:", reply_markup=start_menu_kb())

# -------------------------------
# Portfolio (Mock)
# -------------------------------
async def show_portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle both command and callback query
    if update.callback_query:
        q = update.callback_query; await q.answer()
        message = q.message
    else:
        message = update.message
        
    text = (
        "📊 Your Portfolio\n\n"
        "🪪 Wallet: DUMMY123XYZ456\n"
        "💰 Total Deposited: 12.3 SOL\n"
        "🔄 Active Strategies: 2\n\n"
        "1️⃣ SOL-USDC | 5 SOL | APR: 12.5%\n"
        "2️⃣ ETH-USDT | 7.3 SOL | APR: 10.1%"
    )
    await message.reply_text(text)

# -------------------------------
# Wallet (Mock)
# -------------------------------
def wallet_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Transfer Token", callback_data="transfer_token")],
        [InlineKeyboardButton("🔓 Export Key", callback_data="export_key")],
        [InlineKeyboardButton("🌐 View on Solscan", callback_data="view_solscan")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_wallet")],
        [InlineKeyboardButton("❌ Close", callback_data="close_wallet")]
    ])

async def show_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle both command and callback query
    if update.callback_query:
        q = update.callback_query; await q.answer()
        message = q.message
    else:
        message = update.message
        
    text = (
        "💼 Wallet Overview\n\n"
        "🔗 Geeklad: https://geeklad.io/portfolio/DUMMY123\n"
        "📬 Wallet: DUMMY123XYZ456\n"
        "💳 Balance: 9.2 SOL\n"
        "🏦 Vault PNL: +6.4%"
    )
    await message.reply_text(text, reply_markup=wallet_kb())

async def wallet_stub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    actions = {
        "transfer_token": "🚧 Transfer feature coming soon!",
        "export_key": "⚠️ Your key: DUMMY-KEY-123 (don't share this!)",
        "view_solscan": "🌐 Opening Solscan link (mock)...",
        "refresh_wallet": "🔄 Wallet refreshed!",
        "close_wallet": "❌ Wallet view closed."
    }
    await q.message.reply_text(actions.get(q.data, "🚧 Feature not available."))

# -------------------------------
# Settings Section
# -------------------------------
def settings_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Change Vault Address", callback_data=SET_VAULT)],
        [InlineKeyboardButton("🧱 Change Priority Fees", callback_data=SET_PRIORITY)],
        [InlineKeyboardButton("🕒 Default Rebalancing Time", callback_data=SET_REBALANCE)],
        [InlineKeyboardButton("❌ Close", callback_data="close_settings")]
    ])

def priority_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Very High", callback_data=PRIORITY_VERY_HIGH)],
        [InlineKeyboardButton("⚡ High", callback_data=PRIORITY_HIGH)],
        [InlineKeyboardButton("⚙️ Medium", callback_data=PRIORITY_MEDIUM)],
        [InlineKeyboardButton("⬅️ Back", callback_data=SETTINGS)]
    ])

def rebalance_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏱ 15 min", callback_data=REBALANCE_15M)],
        [InlineKeyboardButton("⏱ 30 min", callback_data=REBALANCE_30M)],
        [InlineKeyboardButton("⏱ 1 hr", callback_data=REBALANCE_1H)],
        [InlineKeyboardButton("⏱ 3 hr", callback_data=REBALANCE_3H)],
        [InlineKeyboardButton("⬅️ Back", callback_data=SETTINGS)]
    ])

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle both command and callback query
    if update.callback_query:
        q = update.callback_query; await q.answer()
        message = q.message
    else:
        message = update.message
        
    await message.reply_text("⚙️ Settings", reply_markup=settings_kb())

async def handle_settings_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    mapping = {
        SET_VAULT: "🔐 Vault change: Please enter new vault address (stub).",
        SET_PRIORITY: "🧱 Choose your priority fee level:",
        SET_REBALANCE: "🕒 Choose your default rebalancing interval:",
        "close_settings": "❌ Settings view closed."
    }
    key = q.data
    if key == SET_PRIORITY:
        await q.message.reply_text(mapping[key], reply_markup=priority_kb())
    elif key == SET_REBALANCE:
        await q.message.reply_text(mapping[key], reply_markup=rebalance_kb())
    else:
        await q.message.reply_text(mapping.get(key, "🚧 Not implemented."))

async def handle_priority_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    labels = {
        PRIORITY_HIGH: "⚡ High priority fee selected.",
        PRIORITY_MEDIUM: "⚙️ Medium priority fee selected.",
        PRIORITY_VERY_HIGH: "🔥 Very high priority fee selected."
    }
    await q.message.reply_text(labels.get(q.data, "✅ Priority set."))

async def handle_rebalance_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    labels = {
        REBALANCE_15M: "⏱ Rebalancing interval set to 15 minutes.",
        REBALANCE_30M: "⏱ Rebalancing interval set to 30 minutes.",
        REBALANCE_1H: "⏱ Rebalancing interval set to 1 hour.",
        REBALANCE_3H: "⏱ Rebalancing interval set to 3 hours."
    }
    await q.message.reply_text(labels.get(q.data, "✅ Rebalance setting saved."))

# -------------------------------
# Help & FAQ
# -------------------------------
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle both command and callback query
    if update.callback_query:
        q = update.callback_query; await q.answer()
        message = q.message
    else:
        message = update.message
        
    await message.reply_text("📖 Please refer to FAQs.")

# -------------------------------
# Register with Application
# -------------------------------
def register_handlers(app):
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("portfolio", show_portfolio))
    app.add_handler(CommandHandler("wallet", show_wallet))
    app.add_handler(CommandHandler("settings", show_settings))
    app.add_handler(CommandHandler("help", show_help))
    
    app.add_handler(CallbackQueryHandler(show_portfolio, pattern=f"^{PORTFOLIO}$"))
    app.add_handler(CallbackQueryHandler(show_wallet, pattern=f"^{WALLET}$"))
    app.add_handler(CallbackQueryHandler(wallet_stub, pattern="^(transfer_token|export_key|view_solscan|refresh_wallet|close_wallet)$"))
    app.add_handler(CallbackQueryHandler(show_settings, pattern=f"^{SETTINGS}$"))
    app.add_handler(CallbackQueryHandler(handle_settings_click, pattern=f"^{SET_VAULT}$|^{SET_PRIORITY}$|^{SET_REBALANCE}$|^close_settings$"))
    app.add_handler(CallbackQueryHandler(handle_priority_change, pattern=f"^{PRIORITY_HIGH}$|^{PRIORITY_MEDIUM}$|^{PRIORITY_VERY_HIGH}$"))
    app.add_handler(CallbackQueryHandler(handle_rebalance_change, pattern=f"^{REBALANCE_15M}$|^{REBALANCE_30M}$|^{REBALANCE_1H}$|^{REBALANCE_3H}$"))
    app.add_handler(CallbackQueryHandler(show_help, pattern=f"^{HELP}$"))

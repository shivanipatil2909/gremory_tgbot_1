import asyncio
from typing import List, Dict, Any
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# -------------------------------------------------------------------
# Callback Identifiers
# -------------------------------------------------------------------
BASE_URL       = "https://dlmm-api.meteora.ag/pair/all_with_pagination"
PAGE_SIZE      = 100  # fetch 100 total, paginate locally

OPEN_POS       = "open_pos"
TRENDING       = "trending_pools"
MANUAL         = "manual_entry"
PAGE_PREFIX    = "page_"
TOKEN_PREFIX   = "token_"
OPEN_POS_NEXT  = "open_pos_next"
STRAT_SPOT     = "spot_strategy"
STRAT_SINGLE   = "single_sided"
REB_YES        = "rebalance_yes"
REB_NO         = "rebalance_no"
CONFIRM_POS    = "confirm_position"
CANCEL_POS     = "cancel_position"
REBALANCE_15M  = "timer_15m"
REBALANCE_30M  = "timer_30m"
REBALANCE_1H   = "timer_1h"
REBALANCE_3H   = "timer_3h"

# -------------------------------------------------------------------
# API Calls
# -------------------------------------------------------------------

async def fetch_trending_pools(page: int) -> List[Dict[str, Any]]:
    offset = page * PAGE_SIZE
    url = f"{BASE_URL}?limit={PAGE_SIZE}&offset={offset}"
    async with aiohttp.ClientSession() as s:
        r = await s.get(url)
        data = await r.json()
        return data.get("pairs", [])

async def fetch_pool_details(pool_addr: str) -> Dict[str, Any]:
    url = f"https://dlmm-api.meteora.ag/pair/{pool_addr}"
    async with aiohttp.ClientSession() as s:
        r = await s.get(url)
        return await r.json()

async def fetch_position_preview(pool_id: str, amount_usd: float, strategy: str, rebalance_hrs: int) -> Dict[str, Any]:
    await asyncio.sleep(0.1)
    return {
        "position_range_low": 7.426,
        "position_range_high": 9.156,
        "token_amount": round(amount_usd * 0.084 / 100, 4),
        "usdc_amount": round(amount_usd * 0.693 / 100, 4),
    }

# -------------------------------------------------------------------
# Keyboards
# -------------------------------------------------------------------

def entry_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌊 Trending Pools", callback_data=TRENDING)],
        [InlineKeyboardButton("🔍 Enter Pool Address", callback_data=MANUAL)],
        [InlineKeyboardButton("🔙 Back", callback_data="start")]
    ])

def pools_list_kb(pools: List[Dict], page: int, total_pages: int) -> InlineKeyboardMarkup:
    kb = []
    for i, p in enumerate(pools):
        text = f"{p['name']} | TVL: {p['liquidity']} | Vol₍24h₎: {p['trade_volume_24h']}"
        kb.append([InlineKeyboardButton(text, callback_data=f"{TOKEN_PREFIX}{page}_{i}")])
    
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ Back", callback_data=f"{PAGE_PREFIX}{page - 1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("Next ▶️", callback_data=f"{PAGE_PREFIX}{page + 1}"))
    
    kb.append(nav)
    kb.append([InlineKeyboardButton(f"📄 Page {page + 1} of {total_pages}", callback_data="noop")])
    return InlineKeyboardMarkup(kb)



def detail_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧪 Open Position", callback_data=OPEN_POS_NEXT)],
        [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_detail")],
        [InlineKeyboardButton("❌ Close", callback_data="close_detail")]
    ])

def strategy_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧠 Spot Strategy", callback_data=STRAT_SPOT)],
        [InlineKeyboardButton("🚀 Single‑Sided Strategy", callback_data=STRAT_SINGLE)]
    ])

def rebalance_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Yes", callback_data=REB_YES)],
        [InlineKeyboardButton("❌ No",  callback_data=REB_NO)]
    ])

def time_interval_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏱ 15 min", callback_data=REBALANCE_15M)],
        [InlineKeyboardButton("⏱ 30 min", callback_data=REBALANCE_30M)],
        [InlineKeyboardButton("⏱ 1 hr", callback_data=REBALANCE_1H)],
        [InlineKeyboardButton("⏱ 3 hr", callback_data=REBALANCE_3H)]
    ])

def confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm", callback_data=CONFIRM_POS)],
        [InlineKeyboardButton("❌ Cancel",  callback_data=CANCEL_POS)]
    ])

# -------------------------------------------------------------------
# Handlers
# -------------------------------------------------------------------

async def open_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle both command and callback query
    if update.callback_query:
        q = update.callback_query; await q.answer()
        message = q.message
    else:
        message = update.message
        
    await message.reply_text("Select how to pick a pool:", reply_markup=entry_kb())

async def show_trending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    all_pools = await fetch_trending_pools(0)
    context.user_data["all_pools"] = all_pools
    context.user_data["page_index"] = 0

    total_pages = (len(all_pools) + 4) // 5
    page_pools = all_pools[:5]

    await q.message.reply_text(
        "🌊 Trending Pools (Page 1):",
        reply_markup=pools_list_kb(page_pools, 0, total_pages)
    )


async def paginate_trending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.split("_")[1])

    all_pools = context.user_data.get("all_pools", [])
    total_pages = (len(all_pools) + 4) // 5
    start = page * 5
    end = start + 5
    page_pools = all_pools[start:end]

    context.user_data["page_index"] = page
    await query.message.edit_reply_markup(
        reply_markup=pools_list_kb(page_pools, page, total_pages)
    )



async def show_pool_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    _, payload = q.data.split(TOKEN_PREFIX, 1)
    page, idx = map(int, payload.split("_"))
    pool = context.user_data["all_pools"][page * 5 + idx]
    details = await fetch_pool_details(pool["address"])
    context.user_data["pool_addr"] = pool["address"]
    await q.message.reply_text(
        f"🔍 {details['name']}\n\n"
        f"• Bin step: {details['bin_step']}\n"
        f"• Base fee: {details['base_fee_percentage']}%\n"
        f"• TVL: {details['liquidity']}\n"
        f"• 24h Volume: {details['trade_volume_24h']}\n"
        f"• 24h Fees: {details['fee_tvl_ratio']['hour_24']}",
        reply_markup=detail_kb()
    )

async def manual_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.message.reply_text("🔍 Please enter the pool address or Meteora link:")
    context.user_data["awaiting_manual"] = True

async def handle_manual_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.pop("awaiting_manual", False):
        return
    pool_addr = update.message.text.strip().split("/")[-1]
    details = await fetch_pool_details(pool_addr)
    context.user_data["pool_addr"] = pool_addr
    await update.message.reply_text(
        f"🔍 {details['name']}\n\n"
        f"• Bin step: {details['bin_step']}\n"
        f"• Base fee: {details['base_fee_percentage']}%\n"
        f"• TVL: {details['liquidity']}\n"
        f"• 24h Volume: {details['trade_volume_24h']}\n"
        f"• 24h Fees: {details['fee_tvl_ratio']['hour_24']}",
        reply_markup=detail_kb()
    )

async def handle_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("🔄 Pool data refreshed (stub).")

async def handle_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("❌ Closed pool detail view.")

async def handle_open_pos_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.message.reply_text("🚀 Choose your strategy:", reply_markup=strategy_kb())

async def handle_strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    strategy = "Spot" if q.data == STRAT_SPOT else "Single-Sided"
    context.user_data["strategy"] = strategy
    await q.message.reply_text(
        "🔄 Would you like to enable auto-monitoring and rebalancing every hour?",
        reply_markup=rebalance_kb()
    )

async def handle_rebalance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.data == REB_YES:
        context.user_data["rebalance_hrs"] = 1
        context.user_data["rebalance_label"] = "1 hour"
        await q.message.reply_text("💵 Enter the amount in SOL you want to allocate:")
        context.user_data["awaiting_amount"] = True
    else:
        await q.message.reply_text("⏱ Choose how often rebalancing should occur:", 
                                  reply_markup=time_interval_kb())
        context.user_data["awaiting_time_selection"] = True

async def handle_time_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    time_mapping = {
        REBALANCE_15M: 0.25,
        REBALANCE_30M: 0.5,
        REBALANCE_1H: 1,
        REBALANCE_3H: 3
    }
    time_labels = {
        REBALANCE_15M: "15 minutes",
        REBALANCE_30M: "30 minutes",
        REBALANCE_1H: "1 hour",
        REBALANCE_3H: "3 hours"
    }
    
    context.user_data["rebalance_hrs"] = time_mapping.get(q.data, 1)
    context.user_data["rebalance_label"] = time_labels.get(q.data, "1 hour")
    context.user_data.pop("awaiting_time_selection", None)
    context.user_data["awaiting_amount"] = True
    
    await q.message.reply_text("💵 Enter the amount in SOL you want to allocate:")
        
async def handle_amount_or_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if context.user_data.get("awaiting_amount"):
        try:
            amt = float(text)
            context.user_data["amount_usd"] = amt
            context.user_data.pop("awaiting_amount", None)

            preview = await fetch_position_preview(
                context.user_data["pool_addr"],
                amt,
                context.user_data["strategy"],
                context.user_data["rebalance_hrs"]
            )
            
            rebalance_label = context.user_data.get("rebalance_label", f"{context.user_data['rebalance_hrs']} hr(s)")
            
            msg = (
                "👀 Position Preview\n\n"
                f"Strategy: {context.user_data['strategy']}\n"
                f"Pool: {context.user_data['pool_addr']}\n"
                f"Position Range: {preview['position_range_low']} - {preview['position_range_high']}\n"
                f"Amount: {preview['token_amount']} / {preview['usdc_amount']} USDC\n"
                f"Auto‑rebalance: every {rebalance_label}"
            )
            await update.message.reply_text(msg, reply_markup=confirm_kb())
        except ValueError:
            await update.message.reply_text("❗ Please enter a valid number.")
    elif context.user_data.get("awaiting_interval"):
        try:
            hrs = int(text)
            context.user_data["rebalance_hrs"] = hrs
            context.user_data.pop("awaiting_interval", None)
            context.user_data["awaiting_amount"] = True
            await update.message.reply_text("💵 Now enter the amount in USD you want to allocate:")
        except ValueError:
            await update.message.reply_text("❗ Enter a whole number.")
    else:
        await update.message.reply_text("❓ Please use the flow buttons or /start to begin.")

async def handle_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == CONFIRM_POS:
        rebalance_label = context.user_data.get("rebalance_label", f"{context.user_data['rebalance_hrs']} hr(s)")
        await q.message.reply_text(f"✅ Position created successfully and the autorebalancing time is set to {rebalance_label}! 🚀")
    else:
        await q.message.reply_text("❌ Position creation cancelled.")
    context.user_data.clear()

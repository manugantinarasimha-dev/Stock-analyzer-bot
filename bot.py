import os
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# =========================
# CONFIG
# =========================

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not found")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# =========================
# UTILS
# =========================

def format_symbol(symbol: str) -> str:
    symbol = symbol.upper().strip()
    if not symbol.endswith(".NS"):
        symbol += ".NS"
    return symbol


def fetch_stock_price(symbol: str):
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?region=IN&interval=1d&range=5d"
    )
    res = requests.get(url, headers=HEADERS, timeout=10)
    data = res.json()

    try:
        price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
        return round(price, 2)
    except Exception:
        return None


def market_status():
    return "OPEN", "Mid-session"


# =========================
# PRICE RANGE LOGIC
# =========================

def calc_ranges(cmp: float):
    intraday = {
        "buy": f"{cmp*0.998:.2f} – {cmp*1.002:.2f}",
        "target": f"{cmp*1.01:.2f}",
        "sl": f"{cmp*0.99:.2f}"
    }

    swing = {
        "buy": f"{cmp*0.98:.2f} – {cmp*0.99:.2f}",
        "target": f"{cmp*1.04:.2f} – {cmp*1.06:.2f}",
        "sl": f"{cmp*0.98:.2f}"
    }

    short_term = {
        "buy": f"{cmp*0.95:.2f} – {cmp*0.97:.2f}",
        "target": f"{cmp*1.08:.2f} – {cmp*1.12:.2f}",
        "sl": f"{cmp*0.95:.2f}"
    }

    long_term = {
        "buy": f"{cmp*0.90:.2f} – {cmp*0.95:.2f}",
        "add_more": f"{cmp*0.85:.2f}, {cmp*0.80:.2f}",
        "target": f"{cmp*1.30:.2f} – {cmp*1.80:.2f}",
        "sl": "Fundamentals-based (Soft SL)"
    }

    return intraday, swing, short_term, long_term


# =========================
# COMMANDS
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📊 *Stock Analyzer Bot*\n\n"
        "Commands:\n"
        "/analyse SYMBOL\n"
        "/intraday SYMBOL\n"
        "/swing SYMBOL\n"
        "/short SYMBOL\n"
        "/long SYMBOL\n\n"
        "⚠️ Educational purpose only"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /analyse SBIN")
        return

    symbol = format_symbol(context.args[0])
    cmp = fetch_stock_price(symbol)

    if not cmp:
        await update.message.reply_text("❌ Stock data not available")
        return

    market, session = market_status()
    intraday, swing, short_term, long_term = calc_ranges(cmp)

    text = (
        f"📌 *Analysis – {symbol}*\n\n"
        f"Market: *{market}*\n"
        f"Session: *{session}*\n"
        f"CMP: *₹{cmp}*\n\n"
        f"*Intraday*\n"
        f"Buy: {intraday['buy']}\n"
        f"Target: {intraday['target']}\n"
        f"SL: {intraday['sl']}\n\n"
        f"*Swing (5–10 days)*\n"
        f"Buy: {swing['buy']}\n"
        f"Target: {swing['target']}\n"
        f"SL: {swing['sl']}\n\n"
        f"*Short Term (1–4 weeks)*\n"
        f"Buy: {short_term['buy']}\n"
        f"Target: {short_term['target']}\n"
        f"SL: {short_term['sl']}\n\n"
        f"*Long Term (6 months – 3 years)*\n"
        f"Buy: {long_term['buy']}\n"
        f"Add more at: {long_term['add_more']}\n"
        f"Target: {long_term['target']}\n"
        f"SL: {long_term['sl']}\n\n"
        f"ℹ️ Logic-only mode (Live broker feed pending)"
    )

    await update.message.reply_text(text, parse_mode="Markdown")


async def intraday_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /intraday SBIN")
        return

    symbol = format_symbol(context.args[0])
    cmp = fetch_stock_price(symbol)

    if not cmp:
        await update.message.reply_text("❌ Stock data not available")
        return

    intraday, _, _, _ = calc_ranges(cmp)

    text = (
        f"📊 *Intraday – {symbol}*\n\n"
        f"CMP: ₹{cmp}\n"
        f"Buy: {intraday['buy']}\n"
        f"Target: {intraday['target']}\n"
        f"SL: {intraday['sl']}\n\n"
        f"ℹ️ Logic-only mode"
    )

    await update.message.reply_text(text, parse_mode="Markdown")


# =========================
# MAIN
# =========================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyse", analyse))
    app.add_handler(CommandHandler("intraday", intraday_cmd))
    app.add_handler(CommandHandler("swing", analyse))
    app.add_handler(CommandHandler("short", analyse))
    app.add_handler(CommandHandler("long", analyse))

    print("🤖 Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()

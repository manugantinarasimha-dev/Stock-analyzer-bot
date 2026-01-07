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
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        data = res.json()
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
    return {
        "intraday": {
            "buy": f"{cmp*0.998:.2f} – {cmp*1.002:.2f}",
            "target": f"{cmp*1.01:.2f}",
            "sl": f"{cmp*0.99:.2f}"
        },
        "swing": {
            "buy": f"{cmp*0.98:.2f} – {cmp*0.99:.2f}",
            "target": f"{cmp*1.04:.2f} – {cmp*1.06:.2f}",
            "sl": f"{cmp*0.98:.2f}"
        },
        "short": {
            "buy": f"{cmp*0.95:.2f} – {cmp*0.97:.2f}",
            "target": f"{cmp*1.08:.2f} – {cmp*1.12:.2f}",
            "sl": f"{cmp*0.95:.2f}"
        },
        "long": {
            "buy": f"{cmp*0.90:.2f} – {cmp*0.95:.2f}",
            "add_more": f"{cmp*0.85:.2f}, {cmp*0.80:.2f}",
            "target": f"{cmp*1.30:.2f} – {cmp*1.80:.2f}",
            "sl": "Fundamentals based (Soft SL)"
        }
    }


# =========================
# COMMANDS
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Stock Analyzer Bot\n\n"
        "/analyse SBIN\n"
        "/intraday SBIN\n"
        "/swing SBIN\n"
        "/short SBIN\n"
        "/long SBIN\n\n"
        "⚠️ Educational purpose only"
    )


async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /analyse SBIN")
        return

    symbol = format_symbol(context.args[0])
    cmp = fetch_stock_price(symbol)

    if not cmp:
        await update.message.reply_text("Stock data not available")
        return

    ranges = calc_ranges(cmp)
    market, session = market_status()

    msg = (
        f"📌 {symbol}\n\n"
        f"CMP: ₹{cmp}\n"
        f"Market: {market}\n"
        f"Session: {session}\n\n"
        f"🔹 Intraday\nBuy: {ranges['intraday']['buy']}\n"
        f"Target: {ranges['intraday']['target']}\n"
        f"SL: {ranges['intraday']['sl']}\n\n"
        f"🔹 Swing\nBuy: {ranges['swing']['buy']}\n"
        f"Target: {ranges['swing']['target']}\n"
        f"SL: {ranges['swing']['sl']}\n\n"
        f"🔹 Short Term\nBuy: {ranges['short']['buy']}\n"
        f"Target: {ranges['short']['target']}\n"
        f"SL: {ranges['short']['sl']}\n\n"
        f"🔹 Long Term\nBuy: {ranges['long']['buy']}\n"
        f"Add more: {ranges['long']['add_more']}\n"
        f"Target: {ranges['long']['target']}\n"
        f"SL: {ranges['long']['sl']}"
    )

    await update.message.reply_text(msg)


# =========================
# MAIN (IMPORTANT CHANGE)
# =========================

def main():
    TOKEN = os.environ.get("BOT_TOKEN")

    if not TOKEN:
        print("❌ BOT_TOKEN not found. Set it in Render Environment Variables.")
        return  # ❗ DO NOT crash Render

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyse", analyse))
    app.add_handler(CommandHandler("intraday", analyse))
    app.add_handler(CommandHandler("swing", analyse))
    app.add_handler(CommandHandler("short", analyse))
    app.add_handler(CommandHandler("long", analyse))

    print("🤖 Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()

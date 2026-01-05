import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("8305829590:AAHf4QZX7qZYOBqdCxcqgw2cqnSozZz3UCk")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def format_symbol(symbol: str) -> str:
    symbol = symbol.upper().strip()
    if not symbol.endswith(".NS"):
        symbol += ".NS"
    return symbol

def fetch_stock(symbol: str):
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?region=IN&interval=1d&range=1d"
    )

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()

        result = data["chart"]["result"]
        if not result:
            return None

        meta = result[0]["meta"]
        return {
            "price": meta.get("regularMarketPrice"),
            "currency": meta.get("currency"),
            "exchange": meta.get("exchangeName"),
            "symbol": meta.get("symbol")
        }

    except Exception:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 *Stock Analyzer Bot*\n\n"
        "Use command:\n"
        "`/analyse WIPRO`\n"
        "`/analyse INFY`\n"
        "`/analyse RELIANCE`",
        parse_mode="Markdown"
    )

async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /analyse WIPRO")
        return

    raw_symbol = context.args[0]
    symbol = format_symbol(raw_symbol)

    await update.message.reply_text("🔍 Fetching data...")

    stock = fetch_stock(symbol)

    if not stock or not stock["price"]:
        await update.message.reply_text("❌ Unable to fetch stock data")
        return

    verdict = "LONG-TERM BUY / HOLD" if stock["price"] > 0 else "HOLD"

    msg = f"""
📈 *{stock['symbol']}*

💰 Price: ₹{stock['price']}
🏦 Exchange: {stock['exchange']}

⭐ Verdict: *{verdict}*
"""
    await update.message.reply_text(msg, parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyse", analyse))
    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()

import os
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("8305829590:AAGzx8uUA6kRUZrV1WxFIzhtXci-FMiKVlM")

def fetch_stock(symbol):
    stock = yf.Ticker(symbol + ".NS")
    info = stock.info

    name = info.get("shortName", symbol)
    price = info.get("currentPrice", "N/A")
    market_cap = info.get("marketCap", "N/A")
    pe = info.get("trailingPE", "N/A")
    roe = info.get("returnOnEquity", "N/A")

    return name, price, market_cap, pe, roe

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Stock Analyzer Bot\n\nUse:\n/analyse TCS"
    )

async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Usage: /analyse TCS")
        return

    symbol = context.args[0].upper()

    try:
        name, price, mc, pe, roe = fetch_stock(symbol)

        msg = (
            f"🏢 {name}\n"
            f"💰 Price: {price}\n"
            f"🏦 Market Cap: {mc}\n"
            f"📊 P/E: {pe}\n"
            f"📈 ROE: {roe}"
        )

        await update.message.reply_text(msg)

    except Exception:
        await update.message.reply_text("❌ Unable to fetch stock data")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyse", analyse))

    print("🤖 Bot running...")
    app.run_polling()

import logging
import requests
import yfinance as yf
import ta
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Replace this with your actual Telegram bot token
TOKEN = "7702515683:AAHLpM4LqEQPR_Lz8HBfN3-S5saMxqYqFn4"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Initialize bot application
app = Application.builder().token(TOKEN).build()

# Start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "📈 Welcome to TradeBot!\n\n"
        "Use /stock <symbol> to get stock trade signals.\n"
        "Use /crypto <symbol> to get crypto trade signals."
    )

# Get stock trade signal
async def get_stock(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        await update.message.reply_text("❌ Please provide a stock symbol. Example: /stock AAPL")
        return

    ticker = context.args[0].upper()
    stock = yf.Ticker(ticker)
    data = stock.history(period="1mo")

    if data.empty:
        await update.message.reply_text("❌ Invalid stock symbol.")
        return

    rsi = ta.momentum.RSIIndicator(data["Close"]).rsi().iloc[-1]
    macd = ta.trend.MACD(data["Close"]).macd().iloc[-1]

    recommendation = "📈 BUY" if rsi < 30 and macd > 0 else "📉 SELL" if rsi > 70 and macd < 0 else "⚖️ HOLD"

    message = (
        f"📊 *{ticker} Trade Signal*\n\n"
        f"🔹 RSI: {round(rsi, 2)}\n"
        f"🔹 MACD: {round(macd, 2)}\n"
        f"🔹 Recommendation: *{recommendation}*"
    )

    await update.message.reply_text(message, parse_mode="Markdown")

# Get crypto trade signal
async def get_crypto(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        await update.message.reply_text("❌ Please provide a crypto symbol. Example: /crypto BTC")
        return

    symbol = context.args[0].upper()
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT"
    response = requests.get(url).json()

    if "priceChangePercent" in response:
        message = (
            f"📊 *{symbol}/USDT Trade Signal*\n\n"
            f"🔹 Price Change (24h): {response['priceChangePercent']}%\n"
            f"🔹 Current Price: ${response['lastPrice']}\n"
            f"🔹 High: ${response['highPrice']} | Low: ${response['lowPrice']}"
        )
        await update.message.reply_text(message, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Invalid crypto symbol.")

# Main function to start the bot
def main():
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stock", get_stock))
    app.add_handler(CommandHandler("crypto", get_crypto))

    logging.info("Bot is running...")
    app.run_polling()  # Runs the bot synchronously

if __name__ == "__main__":
    main()

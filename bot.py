import os
import logging
import requests
from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment variable
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Gold price API endpoint for AED
GOLD_PRICE_API = "https://data-asg.goldprice.org/dbXRates/AED"

# Conversion constants
GRAMS_PER_OUNCE = 31.1035

# UAE timezone (GMT+4)
UAE_TIMEZONE = timezone(timedelta(hours=4))


def fetch_gold_price_aed() -> dict:
    """Fetch current gold prices in AED from goldprice.org API"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(GOLD_PRICE_API, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if "items" not in data or not data["items"]:
            return {}
        
        item = data["items"][0]
        
        # Get price per ounce
        price_per_ounce = item.get("xauPrice", 0)
        
        # Calculate price per gram and per kilo
        price_per_gram = price_per_ounce / GRAMS_PER_OUNCE
        price_per_kilo = price_per_gram * 1000
        
        # Get change info
        change = item.get("chgXau", 0)
        change_percent = item.get("pcXau", 0)
        
        # Get current UAE time
        uae_time = datetime.now(UAE_TIMEZONE)
        timestamp = uae_time.strftime("%b %d, %Y %I:%M:%S %p UAE")
        
        prices = {
            "ounce": f"{price_per_ounce:,.2f}",
            "gram": f"{price_per_gram:,.2f}",
            "kilo": f"{price_per_kilo:,.2f}",
            "change": f"{change:+,.2f}",
            "change_percent": f"{change_percent:+.2f}%",
            "timestamp": timestamp
        }
        
        return prices
        
    except requests.RequestException as e:
        logger.error(f"Error fetching gold price: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    welcome_message = """
🥇 *Welcome to Gold Price Bot!*

I can help you check the current gold prices in AED (UAE Dirham).

*Available Commands:*
/gold - Get current gold prices in AED
/help - Show this help message

_Data sourced from goldprice.org_
"""
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help information."""
    help_text = """
🥇 *Gold Price Bot Help*

*Commands:*
/start - Start the bot
/gold - Get current gold prices in AED
/help - Show this help message

*About:*
This bot fetches real-time gold prices from goldprice.org and displays them in UAE Dirham (AED).

_Prices are updated in real-time._
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def gold_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch and send current gold prices in AED."""
    await update.message.reply_text("⏳ Fetching current gold prices...")
    
    prices = fetch_gold_price_aed()
    
    if prices:
        # Determine trend emoji
        change_val = float(prices.get('change', '0').replace(',', '').replace('+', ''))
        trend = "📈" if change_val >= 0 else "📉"
        
        message = f"🥇 *Current Gold Prices in AED* {trend}\n\n"
        
        message += f"💰 *Per Ounce:* {prices['ounce']} AED\n"
        message += f"💰 *Per Gram:* {prices['gram']} AED\n"
        message += f"💰 *Per Kilo:* {prices['kilo']} AED\n\n"
        
        message += f"📊 *Change:* {prices['change']} AED ({prices['change_percent']})\n"
        
        if prices.get('timestamp'):
            message += f"\n🕐 _{prices['timestamp']}_"
        
        message += "\n_Source: goldprice.org_"
        
        await update.message.reply_text(message, parse_mode="Markdown")
    else:
        await update.message.reply_text(
            "❌ Sorry, I couldn't fetch the gold prices at the moment. Please try again later.",
            parse_mode="Markdown"
        )


def main() -> None:
    """Start the bot."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set!")
        return
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("gold", gold_price))
    
    # React when "gold" or "دهب" is mentioned in a message (e.g. in groups)
    gold_word_filter = filters.Regex(r"(?i)\bgold\b|دهب")
    application.add_handler(MessageHandler(gold_word_filter, gold_price))
    
    # Run the bot
    logger.info("Starting Gold Price Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()


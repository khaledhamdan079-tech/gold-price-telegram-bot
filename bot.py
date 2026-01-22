import os
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment variable
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Gold price URL for AED
GOLD_PRICE_URL = "https://goldprice.org/gold-price-united-arab-emirates.html"


def fetch_gold_price_aed() -> dict:
    """Fetch current gold prices in AED from goldprice.org"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(GOLD_PRICE_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find the gold price table
        prices = {}
        
        # Look for price per ounce
        ounce_element = soup.select_one("#gpxtickerLeft_price")
        if ounce_element:
            prices["ounce"] = ounce_element.get_text(strip=True)
        
        # Look for price per gram
        gram_element = soup.select_one("#gpxtickerLeft_price_gram")
        if gram_element:
            prices["gram"] = gram_element.get_text(strip=True)
        
        # Look for price per kilo
        kilo_element = soup.select_one("#gpxtickerLeft_price_kilo")
        if kilo_element:
            prices["kilo"] = kilo_element.get_text(strip=True)
        
        # Alternative selectors if the above don't work
        if not prices:
            # Try alternative approach - look for specific data attributes or classes
            price_spans = soup.find_all("span", class_="price")
            for span in price_spans:
                text = span.get_text(strip=True)
                if text and "AED" in text or text.replace(",", "").replace(".", "").isdigit():
                    if "ounce" not in prices:
                        prices["ounce"] = text
                        break
        
        # If still no prices, try to get from the main price display
        if not prices:
            main_price = soup.select_one(".gpxMainPriceValue, .price-value, [data-price]")
            if main_price:
                prices["ounce"] = main_price.get_text(strip=True)
        
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
        message = "🥇 *Current Gold Prices in AED*\n\n"
        
        if "ounce" in prices:
            message += f"📊 *Per Ounce:* {prices['ounce']} AED\n"
        if "gram" in prices:
            message += f"📊 *Per Gram:* {prices['gram']} AED\n"
        if "kilo" in prices:
            message += f"📊 *Per Kilo:* {prices['kilo']} AED\n"
        
        message += "\n_Source: goldprice.org_"
        message += "\n_Updated in real-time_"
        
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
    
    # Run the bot
    logger.info("Starting Gold Price Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()


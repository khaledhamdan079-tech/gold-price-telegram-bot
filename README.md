# 🥇 Telegram Gold Price Bot (AED)

A Telegram bot that fetches real-time gold prices in UAE Dirham (AED) from [goldprice.org](https://goldprice.org/).

## Features

- Get current gold prices per ounce, gram, and kilo in AED
- Real-time data from goldprice.org
- Simple commands interface
- Ready for Railway deployment

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and see welcome message |
| `/gold` | Get current gold prices in AED |
| `/help` | Show help information |

## Setup

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the **API Token** you receive

### 2. Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd telegram_gold_price_bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
# Windows (PowerShell):
$env:TELEGRAM_BOT_TOKEN="your_bot_token_here"
# Linux/Mac:
export TELEGRAM_BOT_TOKEN="your_bot_token_here"

# Run the bot
python bot.py
```

## Deploy to Railway

### Method 1: Deploy via GitHub

1. Push this code to a GitHub repository
2. Go to [Railway](https://railway.app/) and sign up/login
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Add environment variable:
   - Click on your service → **Variables**
   - Add: `TELEGRAM_BOT_TOKEN` = `your_bot_token_here`
6. Railway will automatically deploy!

### Method 2: Deploy via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Add environment variable
railway variables set TELEGRAM_BOT_TOKEN=your_bot_token_here

# Deploy
railway up
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram Bot API Token from BotFather | Yes |

## Project Structure

```
telegram_gold_price_bot/
├── bot.py              # Main bot application
├── requirements.txt    # Python dependencies
├── Procfile           # Railway/Heroku process file
├── runtime.txt        # Python version specification
└── README.md          # This file
```

## Dependencies

- `python-telegram-bot` - Telegram Bot API wrapper
- `requests` - HTTP library for fetching gold prices
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast XML/HTML parser

## License

MIT License - feel free to use and modify!

## Data Source

Gold prices are sourced from [goldprice.org](https://goldprice.org/gold-price-united-arab-emirates.html)


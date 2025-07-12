
# Matcha Bot

A Python-based stock availability notification bot that monitors online shops and sends alerts when specific items (like matcha products) are back in stock. Designed for practical automation using web scraping, scheduled checks, and messaging integrations.

## Features

- Checks product availability from specific URLs
- Scheduled or periodic scraping logic
- Sends notifications through messaging platforms (e.g., Telegram or WhatsApp)
- Easily customizable for other products or websites

## Use Case

Originally developed to track stock for matcha powder from niche online shops. Can be repurposed to monitor sneakers, electronics, or any frequently out-of-stock item.

## Tech Stack

- Python 3
- `requests`, `beautifulsoup4` – for scraping product pages
- `schedule` or `time` – for repeated execution
- Messaging integrations (e.g., Telegram, Twilio)
- `.env` file for environment-based configuration

## Project Structure

```

matcha\_bot/
├── bot.py              # Main logic to check availability and send notifications
├── config.py           # Product URLs and configuration constants
├── notifier.py         # Messaging service integrations
├── utils.py            # Helper functions for parsing and formatting
├── .env                # Environment variables (not committed)
└── README.md           # This file
````

## Setup and Installation

1. Clone the repository  
   ```bash
   git clone https://github.com/nicoleromeroo/matcha_bot.git
   cd matcha_bot
   ```


2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with the following variables:

   ```
   TELEGRAM_API_KEY=your_telegram_bot_api_key
   TELEGRAM_CHAT_ID=your_chat_id
   PRODUCT_URL=https://example.com/product
   ```

4. Run the bot

   ```bash
   python bot.py
   ```


## Example Output

```
🍵 Matcha Stock Summary Report
Total Products Monitored: 27
🟢 In Stock
1 products available
🔴 Out of Stock
26 products unavailable
⚠️ Errors
0 products with errors
📋 Available Products Sample
• Matcha Fuji-no-Shiro,Can 30g - €9,95 EUR
Report generated: 2025-07-08 08:34:01 UTC
```

## Extending the Bot

* Deploy on a server or schedule with a task runner
* Use Docker for containerization and deployment

## Motivation

This project was created to automate a common personal task: tracking availability of matcha products online. It also served as a hands-on opportunity to work with automation, scraping, and API integration.

## License

This project is licensed under the MIT License.

---

Developed by Nicole Romero

```


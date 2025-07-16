import asyncio
import requests
from telegram import Bot

# Telegram bot setup
TELEGRAM_BOT_TOKEN = "8128008808:AAGFbxEBwpv5zc4jtVb9SJ5yF-Np20z8OWc"
TELEGRAM_CHAT_ID = 953349213
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Apify setup
APIFY_TOKEN = "apify_api_tkDeQRJ2TRU08Tefp6tC2shXa4qdEb1CZlQq"
ACTOR_ID = "jupri~mercari-scraper"
API_URL = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={APIFY_TOKEN}"

# Keywords to search on Mercari
SEARCH_KEYWORDS = ["スニーカー", "Suicoke", "Mihara Yasuhiro"]
LIMIT = 5  # How many listings to fetch per search

async def send_telegram_message(text):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
    except Exception as e:
        print("Telegram error:", e)

async def run_apify_scraper():
    payload = {
        "query": SEARCH_KEYWORDS,
        "limit": LIMIT
    }

    print("🔍 Starting Apify Mercari scraper...")
    run_response = requests.post(API_URL, json=payload)
    run_id = run_response.json()["data"]["id"]

    # Wait until the run finishes
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
    dataset_url = None

    while True:
        status = requests.get(status_url).json()
        if status["data"]["status"] == "SUCCEEDED":
            dataset_id = status["data"]["defaultDatasetId"]
            dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?clean=true"
            break
        elif status["data"]["status"] == "FAILED":
            print("❌ Apify run failed.")
            return
        await asyncio.sleep(5)

    # Fetch results and send to Telegram
    results = requests.get(dataset_url).json()
    for item in results:
        title = item.get('title', 'No title')
        price = item.get('price', 'No price')
        url = item.get('url', 'No link')
        message = f"{title}\nPrice: {price}\n{url}"
        print("➡️ Sending:", message)
        await send_telegram_message(message)

async def main():
    await run_apify_scraper()

if __name__ == "__main__":
    asyncio.run(main())

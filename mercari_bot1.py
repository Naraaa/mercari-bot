import os
import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# === Configuration ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8128008808:AAGFbxEBwpv5zc4jtVb9SJ5yF-Np20z8OWc")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "953349213")
KEYWORDS = os.getenv("KEYWORDS", "スニーカー,時計,バッグ").split(",")
MIN_PRICE = int(os.getenv("MIN_PRICE", "1000"))
MAX_PRICE = int(os.getenv("MAX_PRICE", "5000"))

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def send_to_telegram(item):
    message = (
        f"🛍 {item['title']}\n"
        f"💴 {item['price']}\n"
        f"🔗 {item['link']}"
    )
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def parse_price(price_str):
    digits = ''.join(filter(str.isdigit, price_str))
    return int(digits) if digits else 0

def search_mercari_html(keyword):
    url = f"https://www.mercari.jp/search/?keyword={keyword}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    items = []
    
    for item_tag in soup.select("section.items-box"):
        title_tag = item_tag.select_one(".items-box-name")
        price_tag = item_tag.select_one(".items-box-price")
        link_tag = item_tag.select_one("a")

        if not (title_tag and price_tag and link_tag):
            continue

        title = title_tag.text.strip()
        price_str = price_tag.text.strip()
        price = parse_price(price_str)
        link = "https://www.mercari.jp" + link_tag["href"]

        if price < MIN_PRICE or price > MAX_PRICE:
            continue

        items.append({
            "title": title,
            "price": price_str,
            "link": link
        })
    return items

def run_bot():
    seen_links = set()
    print("🔍 Mercari scraping bot started...")
    while True:
        try:
            for keyword in KEYWORDS:
                print(f"Searching for '{keyword}'...")
                results = search_mercari_html(keyword)
                for item in results:
                    if item["link"] not in seen_links:
                        send_to_telegram(item)
                        seen_links.add(item["link"])
            time.sleep(60)  # 1 minute delay between searches
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    run_bot()


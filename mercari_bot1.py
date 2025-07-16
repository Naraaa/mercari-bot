import os
import time
import requests
from bs4 import BeautifulSoup
import asyncio
import urllib.parse
from telegram import Bot

# Your Telegram bot token and chat ID (hardcoded)
TELEGRAM_BOT_TOKEN = "8128008808:AAGFbxEBwpv5zc4jtVb9SJ5yF-Np20z8OWc"
TELEGRAM_CHAT_ID = 953349213

# Keywords, price range
KEYWORDS = "Kapital,Mihara Yasuhiro,Takahiromiyahista,Visvim,Wtaps,Final Home,Maharishi,Issey Miyake,PPFM,Mercibeaucoup,Tete Homme,Vivienne Westwood,Hysteric Glamour,Number Nine,Yohji Yamamoto,Jean Paul Gaultier,Dolce & Gabbana,Bottega Veneta,Maison Margiela,Comme Des Garçons,Comme Des Garcons,Junya Watanabe,Undercover,Sacai,GOA,ifsixwasnine,L.G.B,Semantic Design,In The Attic,beauty:beast,14th Addiction,Y Project,Martine Rose,Yasuyuki Ishii,Hyoma (20471120),Doublet,291295=homme,Wacko Maria,Courreges,Avirex,Evisu,Balenciaga,Suicoke,Supreme,Marithe Francois Girbaud,Facetasm,Yellow Corn,Kadoya,Fucking Awesome,Morgan Homme".split(",")
MIN_PRICE = 1000
MAX_PRICE = 5000

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Referer": "https://www.mercari.com/jp/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def send_telegram_message(text):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
    except Exception as e:
        print(f"Telegram send_message error: {e}")

def build_search_url(keyword, min_price, max_price):
    keyword_encoded = urllib.parse.quote(keyword)
    base_url = "https://www.mercari.com/jp/search/"
    params = (
        f"?keyword={keyword_encoded}"
        f"&price_min={min_price}"
        f"&price_max={max_price}"
        "&status=on_sale"
        "&sort=created_time"
        "&order=desc"
    )
    return base_url + params

def parse_items_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for item_section in soup.select('section[data-testid="item-cell"]'):
        title_tag = item_section.select_one('h3[data-testid="item-title"]')
        price_tag = item_section.select_one('div[data-testid="item-price"]')
        link_tag = item_section.find('a', href=True)

        if not title_tag or not price_tag or not link_tag:
            continue

        title = title_tag.get_text(strip=True)
        price = price_tag.get_text(strip=True)
        url = "https://www.mercari.com" + link_tag['href']

        items.append({"title": title, "price": price, "url": url})

    return items

async def main():
    print("🔍 Mercari scraping bot started...")
    session = requests.Session()
    session.headers.update(HEADERS)

    while True:
        for keyword in KEYWORDS:
            keyword = keyword.strip()
            print(f"Searching for '{keyword}'...")
            url = build_search_url(keyword, MIN_PRICE, MAX_PRICE)
            try:
                response = session.get(url)
                if response.status_code != 200:
                    print(f"Failed to retrieve {url}, status code: {response.status_code}")
                    continue

                items = parse_items_from_html(response.text)
                if not items:
                    print(f"No items found for '{keyword}'.")
                    continue

                for item in items:
                    message = f"{item['title']}\nPrice: {item['price']}\n{item['url']}"
                    print(f"Sending to Telegram:\n{message}\n")
                    await send_telegram_message(message)

            except Exception as e:
                print(f"Error during search for '{keyword}': {e}")

            await asyncio.sleep(3)  # delay between keyword searches

        print("Waiting 60 seconds before next cycle...\n")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())

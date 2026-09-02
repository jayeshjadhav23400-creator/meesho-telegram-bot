import os
import re
import requests
from bs4 import BeautifulSoup

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
COLLECTION_URL = os.environ["MEESHO_COLLECTION_URL"]

def telegram(method, data):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    r = requests.post(url, data=data, timeout=30)
    r.raise_for_status()
    return r.json()

html = requests.get(
    COLLECTION_URL,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
).text

soup = BeautifulSoup(html, "html.parser")

products = []
seen = set()

for a in soup.find_all("a", href=True):
    href = a["href"]

    if "/p/" not in href:
        continue

    if href.startswith("/"):
        href = "https://www.meesho.com" + href

    title = a.get_text(" ", strip=True)

    if not title:
        continue

    key = href.split("?")[0]

    if key in seen:
        continue

    seen.add(key)
    products.append((title[:150], key))

# Maximum 10 products per run
products = products[:10]

for title, link in products:
    message = f"🛍️ {title}\n\n👉 Buy / View Product:\n{link}"

    try:
        telegram(
            "sendMessage",
            {
                "chat_id": CHAT_ID,
                "text": message,
                "disable_web_page_preview": False
            }
        )
        print("Posted:", title)
    except Exception as e:
        print("Telegram error:", e)

print(f"Finished. Products found: {len(products)}")

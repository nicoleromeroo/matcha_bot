import requests
from bs4 import BeautifulSoup
from datetime import datetime
import schedule
import time
import json
import os
from urllib.parse import urlparse

# CONFIG
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1389954965140672574/vRcJC01JiXHDwciXQJ0heQVA3ymNsBsqBVap1s72W_4QNG8xZFK_Ig4tSIZoFriMyPiX"
YEN_TO_EURO = 0.0061
STATUS_FILE = "status.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

PRODUCT_URLS = [
    "https://global.tokichi.jp/products/mc2",
    "https://global.tokichi.jp/products/mc1",
    "https://global.tokichi.jp/products/mc21",
    "https://global.tokichi.jp/products/mc5",
    "https://global.tokichi.jp/products/mc6",
    "https://global.tokichi.jp/products/mc9",
    "https://global.tokichi.jp/products/mc2-p100",
    "https://horiishichimeien.com/en/products/matcha-premiumnarino",
    "https://horiishichimeien.com/en/products/matcha-narino",
    "https://horiishichimeien.com/en/products/matcha-okunoyama",
    "https://horiishichimeien.com/en/products/matcha-mumon",
    "https://horiishichimeien.com/en/products/matcha-choukounomukashi",
    "https://horiishichimeien.com/en/products/matcha-shichimeinomukashi",
    "https://horiishichimeien.com/en/products/matcha-todounomukashi",
    "https://horiishichimeien.com/en/products/matcha-agatanoshiro",
    "https://horiishichimeien.com/en/products/matcha-ujimukashi",
    "https://global.ippodo-tea.co.jp/collections/matcha/products/matcha387424",
    "https://global.ippodo-tea.co.jp/collections/matcha/products/matcha306024",
    "https://global.ippodo-tea.co.jp/collections/matcha/products/matcha101024",
    "https://global.ippodo-tea.co.jp/collections/matcha/products/matcha101044",
    "https://global.ippodo-tea.co.jp/collections/matcha/products/matcha103644",
    "https://global.ippodo-tea.co.jp/collections/matcha/products/matcha173512",
    "https://global.ippodo-tea.co.jp/collections/matcha/products/matcha104033",
    "https://global.ippodo-tea.co.jp/collections/matcha/products/matcha105033",
    "https://global.ippodo-tea.co.jp/collections/matcha/products/matcha175512",
    "https://global.ippodo-tea.co.jp/collections/matcha/products/matcha108643",
    "https://global.ippodo-tea.co.jp/collections/matcha/products/matcha109643"
]

def convert_price(jpy_str):
    try:
        num = float(jpy_str.replace('JPY','').replace('¥','').replace(',','').strip())
        return f"€{round(num * YEN_TO_EURO, 2)}"
    except:
        return jpy_str

def fetch_product_status(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        name = soup.find("h1").get_text(strip=True)
        price_jpy = soup.find("span", {"class":"price-item--regular"}).get_text(strip=True)
        price = convert_price(price_jpy)
        btn = soup.find("button", {"name":"add"})
        in_stock = bool(btn and not btn.has_attr("disabled") and "Add to cart" in btn.get_text())
        return {"name": name, "price": price, "in_stock": in_stock, "url": url}
    except Exception as e:
        return {"name":"Error","price":"N/A","in_stock":False,"url":url,"error":str(e)}

def build_embed_block(products, title, description, site_label):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    embed = {
      "username": "Matcha Bot",
      "embeds": [{
        "title": f"\U0001f375 {title}",
        "description": f"**Site:** {site_label}\n**{description}**",
        "color": 5763719,
        "fields": [],
        "thumbnail": {"url":"https://em-content.zobj.net/source/telegram/358/teacup-without-handle_1f375.png"},
        "footer": {"text": f"Last updated: {ts}"}
      }]
    }
    for p in products:
        emoji = "\U0001f7e2" if p["in_stock"] else "\U0001f534"
        status = "IN STOCK" if p["in_stock"] else "OUT OF STOCK"
        embed["embeds"][0]["fields"].append({
          "name": f"{emoji} {status} {p['name']}",
          "value": f"**Price:** {p['price']}\n[View Product]({p['url']})",
          "inline": True
        })
    return embed

def send_report(payload):
    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        resp.raise_for_status()
    except Exception as e:
        print(f"Webhook error: {e}")

def send_grouped_reports(items, title_base, desc):
    # group by domain
    by_domain = {}
    for it in items:
        domain = urlparse(it["url"]).netloc
        by_domain.setdefault(domain, []).append(it)

    # small groups (<2 items) go to mixed
    mixed = []
    mixed_sites = []
    for domain, lst in list(by_domain.items()):
        if len(lst) < 2:
            mixed.extend(lst)
            mixed_sites.append(domain)
            del by_domain[domain]

    # send per-domain reports
    for domain, lst in by_domain.items():
        payload = build_embed_block(
            lst,
            title=f"{title_base} — {domain}",
            description=desc + f" ({len(lst)}/{len(lst)} items)",
            site_label=domain
        )
        send_report(payload)

    # send mixed if any
    if mixed:
        payload = build_embed_block(
            mixed,
            title=f"{title_base} — Mixed",
            description=desc + f" ({len(mixed)}/{len(items)} items from {len(mixed_sites)} sites)",
            site_label=",".join(sorted(set(mixed_sites)))
        )
        send_report(payload)

# --- INITIAL RUN ---
print("▶ Initial full report…")
all_status = [fetch_product_status(u) for u in PRODUCT_URLS]
send_grouped_reports(all_status, "Matcha Stock Report", "Full stock update")
last_status = {p["url"]: p["in_stock"] for p in all_status}
with open(STATUS_FILE, "w") as f:
    json.dump(last_status, f)

# --- JOB ---
def job():
    global last_status
    print("🔄 Checking for changes…")
    restocked, depleted = [], []
    current = {}

    for url in PRODUCT_URLS:
        st = fetch_product_status(url)
        current[url] = st["in_stock"]
        if st["in_stock"] and not last_status.get(url):
            restocked.append(st)
        if not st["in_stock"] and last_status.get(url, False):
            depleted.append(st)

    last_status = current
    with open(STATUS_FILE, "w") as f:
        json.dump(last_status, f)

    if restocked:
        print("✅ Restocks!")
        send_grouped_reports(restocked, "Matcha Stock Alert", "Restocked items")
    if depleted:
        print("⚠ Out of stock again!")
        send_grouped_reports(depleted, "Out of Stock Alert", "Now out of stock")
    if not (restocked or depleted):
        print("— No changes.")

schedule.every(30).seconds.do(job)

print("🟢 Bot running…")
while True:
    schedule.run_pending()
    time.sleep(1)
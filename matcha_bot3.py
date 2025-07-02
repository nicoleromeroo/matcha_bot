import requests
from bs4 import BeautifulSoup
from datetime import datetime
import schedule
import time
import json
import os
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# CONFIG
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1389954965140672574/vRcJC01JiXHDwciXQJ0heQVA3ymNsBsqBVap1s72W_4QNG8xZFK_Ig4tSIZoFriMyPiX"
YEN_TO_EURO = 0.0061
STATUS_FILE = "status.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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
    """Convert Japanese Yen price to Euro"""
    try:
        clean_str = jpy_str.replace('JPY', '').replace('¥', '').replace(',', '').replace('円', '').strip()
        num = float(clean_str)
        return f"€{round(num * YEN_TO_EURO, 2)}"
    except:
        return jpy_str


def create_selenium_driver():
    """Create and configure Selenium WebDriver"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"Failed to create driver: {e}")
        return None


def check_stock_selenium(url):
    """Check stock status using Selenium for JS-heavy sites"""
    driver = create_selenium_driver()
    if not driver:
        return {"name": "Driver Error", "price": "N/A", "in_stock": False, "url": url,
                "error": "Failed to create driver"}

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)

        # Get product name
        try:
            name_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            name = name_element.text.strip()
        except:
            name = "Unknown Product"

        # Get price with multiple selectors
        price = "N/A"
        price_selectors = [".price-item--regular", ".price", "[data-price]", ".product-price"]

        for selector in price_selectors:
            try:
                price_element = driver.find_element(By.CSS_SELECTOR, selector)
                price = convert_price(price_element.text.strip())
                break
            except:
                continue

        # CRITICAL: Check if "Add to cart" button exists and is visible
        # For out of stock items, this button won't exist at all
        in_stock = False
        try:
            # Look for visible add to cart button (not hidden)
            add_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[name="add"]')

            for btn in add_buttons:
                # Check if button is displayed and not hidden
                if btn.is_displayed() and btn.is_enabled():
                    btn_text = btn.text.lower()
                    if "add to cart" in btn_text:
                        # Check if button doesn't have display:none style
                        style = btn.get_attribute('style') or ''
                        if 'display: none' not in style and 'display:none' not in style:
                            in_stock = True
                            break
        except Exception as e:
            print(f"Stock check error for {url}: {e}")
            in_stock = False

        return {"name": name, "price": price, "in_stock": in_stock, "url": url}

    except Exception as e:
        print(f"Selenium error for {url}: {str(e)}")
        return {"name": "Error", "price": "N/A", "in_stock": False, "url": url, "error": str(e)}
    finally:
        try:
            driver.quit()
        except:
            pass


def check_stock_requests(url):
    """Check stock status using requests for regular sites"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get product name
        name_element = soup.find("h1")
        name = name_element.get_text(strip=True) if name_element else "Unknown Product"

        # Get price
        price = "N/A"
        price_selectors = [
            {"class": "price-item--regular"},
            {"class": "price"},
            {"data-price": True}
        ]

        for selector in price_selectors:
            price_element = soup.find("span", selector) or soup.find("div", selector)
            if price_element:
                price = convert_price(price_element.get_text(strip=True))
                break

        # Check stock - look for visible "Add to cart" button
        in_stock = False
        add_buttons = soup.find_all("button", {"name": "add"})

        for btn in add_buttons:
            # Skip hidden buttons
            style = btn.get('style', '')
            if 'display: none' in style or 'display:none' in style:
                continue

            btn_text = btn.get_text(strip=True).lower()
            if "add to cart" in btn_text and not btn.has_attr("disabled"):
                in_stock = True
                break

        return {"name": name, "price": price, "in_stock": in_stock, "url": url}

    except Exception as e:
        print(f"Request error for {url}: {str(e)}")
        return {"name": "Error", "price": "N/A", "in_stock": False, "url": url, "error": str(e)}


def fetch_product_status(url):
    """Main function to check product status"""
    print(f"    Checking: {url}")

    # Use Selenium for Ippodo (requires JS) and Tokichi (might need JS)
    if "ippodo-tea.co.jp" in url or "tokichi.jp" in url:
        return check_stock_selenium(url)
    else:
        return check_stock_requests(url)


def send_discord_webhook(payload):
    """Send message to Discord webhook"""
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        print("  ✅ Discord notification sent")
        return True
    except Exception as e:
        print(f"  ❌ Discord webhook error: {e}")
        return False


def create_summary_embed(all_products):
    """Create summary report embed"""
    in_stock = [p for p in all_products if p["in_stock"] and "error" not in p]
    out_of_stock = [p for p in all_products if not p["in_stock"] and "error" not in p]
    errors = [p for p in all_products if "error" in p]

    # Sample of available products
    available_sample = ""
    if in_stock:
        sample_products = in_stock[:3]
        for product in sample_products:
            name = product["name"][:40] + "..." if len(product["name"]) > 40 else product["name"]
            available_sample += f"• {name} - {product['price']}\n"
        if len(in_stock) > 3:
            available_sample += f"... and {len(in_stock) - 3} more available\n"
    else:
        available_sample = "No products currently in stock"

    embed = {
        "username": "Matcha Stock Monitor",
        "embeds": [{
            "title": "🍵 Matcha Stock Summary Report",
            "description": f"**Total Products Monitored:** {len(all_products)}",
            "color": 5763719,
            "fields": [
                {
                    "name": "🟢 In Stock",
                    "value": f"**{len(in_stock)}** products available",
                    "inline": True
                },
                {
                    "name": "🔴 Out of Stock",
                    "value": f"**{len(out_of_stock)}** products unavailable",
                    "inline": True
                },
                {
                    "name": "⚠️ Errors",
                    "value": f"**{len(errors)}** products with errors",
                    "inline": True
                },
                {
                    "name": "📋 Available Products Sample",
                    "value": available_sample,
                    "inline": False
                }
            ],
            "thumbnail": {"url": "https://em-content.zobj.net/source/telegram/358/teacup-without-handle_1f375.png"},
            "footer": {"text": f"Report generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"}
        }]
    }

    return embed


def create_product_embed(products, title, description, site_name):
    """Create detailed product listing embed"""
    embed = {
        "username": "Matcha Stock Monitor",
        "embeds": [{
            "title": f"🍵 {title}",
            "description": f"**Site:** {site_name}\n{description}",
            "color": 5763719,
            "fields": [],
            "thumbnail": {"url": "https://em-content.zobj.net/source/telegram/358/teacup-without-handle_1f375.png"},
            "footer": {"text": f"Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"}
        }]
    }

    for product in products:
        if product["in_stock"]:
            emoji = "🟢"
            status = "IN STOCK"
        elif "error" in product:
            emoji = "⚠️"
            status = "ERROR"
        else:
            emoji = "🔴"
            status = "OUT OF STOCK"

        # Truncate long product names
        display_name = product["name"][:50] + "..." if len(product["name"]) > 50 else product["name"]

        field_value = f"**{display_name}**\n**Price:** {product['price']}\n[View Product]({product['url']})"

        if "error" in product:
            field_value += f"\n*Error: {product['error'][:50]}...*"

        embed["embeds"][0]["fields"].append({
            "name": f"{emoji} {status}",
            "value": field_value,
            "inline": True
        })

    return embed


def send_reports(all_products, report_type="Full Stock Report"):
    """Send all reports to Discord"""
    print(f"\n📨 Sending {report_type} to Discord...")

    # Send summary first
    summary_embed = create_summary_embed(all_products)
    send_discord_webhook(summary_embed)
    time.sleep(2)  # Rate limiting

    # Group products by domain
    by_domain = {}
    for product in all_products:
        domain = urlparse(product["url"]).netloc
        by_domain.setdefault(domain, []).append(product)

    # Send detailed reports by domain
    for domain, products in by_domain.items():
        title = f"Stock Report — {domain}"
        description = f"Detailed status for {len(products)} products"

        embed = create_product_embed(products, title, description, domain)
        send_discord_webhook(embed)
        time.sleep(1)  # Rate limiting between embeds


def load_previous_status():
    """Load previous stock status from file"""
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, "r") as f:
                data = json.load(f)
                print(f"📂 Loaded previous status for {len(data)} products")
                return data
    except Exception as e:
        print(f"⚠️ Error loading status file: {e}")
    return {}


def save_current_status(status_dict):
    """Save current stock status to file"""
    try:
        with open(STATUS_FILE, "w") as f:
            json.dump(status_dict, f, indent=2)
        print(f"💾 Saved status for {len(status_dict)} products")
    except Exception as e:
        print(f"⚠️ Error saving status file: {e}")


def check_all_products():
    """Check status of all products"""
    print(f"\n🔍 Checking {len(PRODUCT_URLS)} products...")
    all_products = []

    for i, url in enumerate(PRODUCT_URLS, 1):
        print(f"  [{i}/{len(PRODUCT_URLS)}] Checking product...")
        product_status = fetch_product_status(url)
        all_products.append(product_status)

        # Show status in console
        if product_status["in_stock"]:
            status_emoji = "✅"
            status_text = "IN STOCK"
        elif "error" in product_status:
            status_emoji = "⚠️"
            status_text = "ERROR"
        else:
            status_emoji = "❌"
            status_text = "OUT OF STOCK"

        print(f"    {status_emoji} {status_text} - {product_status['name']} - {product_status['price']}")

        # Be respectful to servers
        time.sleep(3)

    return all_products


def monitor_stock_changes():
    """Monitor for stock changes and send alerts"""
    print(f"\n🔄 Monitoring stock changes - {datetime.now().strftime('%H:%M:%S')}")

    # Load previous status
    previous_status = load_previous_status()

    # Check current status
    current_products = check_all_products()
    current_status = {p["url"]: p["in_stock"] for p in current_products}

    # Find changes
    restocked = []
    out_of_stock = []

    for product in current_products:
        url = product["url"]
        current_stock = product["in_stock"]
        previous_stock = previous_status.get(url, None)

        if current_stock and not previous_stock:
            restocked.append(product)
        elif not current_stock and previous_stock:
            out_of_stock.append(product)

    # Send change alerts
    if restocked:
        print(f"🎉 Found {len(restocked)} restocked items!")
        send_reports(restocked, "🎉 RESTOCK ALERT")

    if out_of_stock:
        print(f"😢 Found {len(out_of_stock)} items now out of stock")
        send_reports(out_of_stock, "😢 OUT OF STOCK ALERT")

    if not restocked and not out_of_stock:
        print("📊 No stock changes detected")

    # Save current status
    save_current_status(current_status)


# === MAIN EXECUTION ===

print("🚀 Starting Matcha Stock Monitor Bot")
print(f"📊 Monitoring {len(PRODUCT_URLS)} products")
print("=" * 50)

# Always run initial full report
print("📋 Running initial stock report...")
initial_products = check_all_products()
send_reports(initial_products, "📋 Initial Stock Report")

# Save initial status
initial_status = {p["url"]: p["in_stock"] for p in initial_products}
save_current_status(initial_status)

print("\n" + "=" * 50)
print("✅ Initial report complete!")
print("🔄 Starting continuous monitoring...")
print("⏰ Checking every 5 minutes for changes")
print("🛑 Press Ctrl+C to stop")

# Schedule monitoring job
schedule.every(5).minutes.do(monitor_stock_changes)

# Main monitoring loop
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Stopping Matcha Stock Monitor...")
    print("👋 Goodbye!")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print("🔄 Restarting monitoring...")
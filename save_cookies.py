from playwright.sync_api import sync_playwright

# Ziel-Dateiname für Cookies
STORAGE_STATE = "storage_state.json"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Gehe zur Login-Seite
    page.goto("https://www.marukyu-koyamaen.co.jp/english/my-account/")

    print("Bitte logge dich manuell ein. Danach drücke [ENTER] hier im Terminal...")
    input()  # Warten bis Benutzer sich eingeloggt hat

    # Speicher die Session
    context.storage_state(path=STORAGE_STATE)
    print(f"✅ Cookies wurden gespeichert nach: {STORAGE_STATE}")

    browser.close()

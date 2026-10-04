import os
import time
import requests
from playwright.sync_api import sync_playwright

# Installazione dipendenze su Railway
os.system("playwright install-deps chromium")
os.system("playwright install chromium")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# SOGLIA RITARDI (Metti 1 per test immediato, imposta a 8 a test superato)
SOGLIA_CHANCE = 1

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print(f"Errore Telegram: {e}")

ROSSI = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
NERI = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

def analizza_ritardi(numeri):
    if len(numeri) < SOGLIA_CHANCE:
        return

    ultimi = numeri[-SOGLIA_CHANCE:]

    # 1. Rosso / Nero
    if all(n in ROSSI for n in ultimi):
        send_telegram(f"🔴 ALLARME ROSSO ({SOGLIA_CHANCE} di fila!)\nUltimi: {ultimi}")
    elif all(n in NERI for n in ultimi):
        send_telegram(f"⚫ ALLARME NERO ({SOGLIA_CHANCE} di fila!)\nUltimi: {ultimi}")

    # 2. Pari / Dispari (escluso 0)
    if all(n != 0 and n % 2 == 0 for n in ultimi):
        send_telegram(f"🔢 ALLARME PARI ({SOGLIA_CHANCE} di fila!)\nUltimi: {ultimi}")
    elif all(n != 0 and n % 2 != 0 for n in ultimi):
        send_telegram(f"🔢 ALLARME DISPARI ({SOGLIA_CHANCE} di fila!)\nUltimi: {ultimi}")

    # 3. Manche (1-18) / Passe (19-36)
    if all(1 <= n <= 18 for n in ultimi):
        send_telegram(f"📉 ALLARME MANCHE 1-18 ({SOGLIA_CHANCE} di fila!)\nUltimi: {ultimi}")
    elif all(19 <= n <= 36 for n in ultimi):
        send_telegram(f"📈 ALLARME PASSE 19-36 ({SOGLIA_CHANCE} di fila!)\nUltimi: {ultimi}")

def run_bot():
    send_telegram("🚀 Bot avviato! Connessione alla roulette in corso...")
    
    while True:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled"
                    ]
                )
                
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    viewport={"width": 1366, "height": 768}
                )
                
                page = context.new_page()
                
                # Maschera l'automazione a Cloudflare (Stealth Mode)
                page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                url = "https://tracksino.com/mega-fire-blaze-roulette"
                
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                except Exception:
                    pass

                time.sleep(10)
                
                titolo = page.title()
                if "Just a moment" in titolo or "Cloudflare" in titolo:
                    send_telegram("⚠️ Protezione Cloudflare attiva, attendo sblocco...")
                    time.sleep(15)

                conferma_inviata = False

                while True:
                    try:
                        elementi = page.query_selector_all("span, div, td, p")
                        estrazioni = []
                        for el in elementi:
                            try:
                                txt = el.inner_text().strip()
                                if txt.isdigit() and 0 <= int(txt) <= 36 and len(txt) <= 2:
                                    estrazioni.append(int(txt))
                            except Exception:
                                pass

                        if estrazioni:
                            if not conferma_inviata:
                                send_telegram(f"✅ Connessione riuscita! Primi 10 numeri estratti: {estrazioni[:10]}")
                                conferma_inviata = True
                                
                            analizza_ritardi(estrazioni)

                        time.sleep(10)
                    except Exception as e:
                        print(f"Errore lettura: {e}")
                        time.sleep(5)

        except Exception as e:
            print(f"Riavvio browser: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_bot()

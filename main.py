import os
import time
import requests

# Installazione dipendenze e Chromium
os.system("playwright install-deps chromium")
os.system("playwright install chromium")

from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SOGLIA_CHANCE = 1

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Errore: TELEGRAM_TOKEN o CHAT_ID non trovati.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

ROSSI = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
NERI = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

def analizza_ritardi(numeri):
    if len(numeri) < SOGLIA_CHANCE:
        return

    ultimi = numeri[-SOGLIA_CHANCE:]

    if all(n in ROSSI for n in ultimi):
        send_telegram(f"🔴 ALLARME ROSSO ({SOGLIA_CHANCE} di fila!)\nUltimi: {ultimi}")
    elif all(n in NERI for n in ultimi):
        send_telegram(f"⚫ ALLARME NERO ({SOGLIA_CHANCE} di fila!)\nUltimi: {ultimi}")

    if all(n != 0 and n % 2 == 0 for n in ultimi):
        send_telegram(f"🔢 ALLARME PARI ({SOGLIA_CHANCE} di fila!)\nUltimi: {ultimi}")
    elif all(n != 0 and n % 2 != 0 for n in ultimi):
        send_telegram(f"🔢 ALLARME DISPARI ({SOGLIA_CHANCE} di fila!)\nUltimi: {ultimi}")

    if all(1 <= n <= 18 for n in ultimi):
        send_telegram(f"📉 ALLARME MANCHE 1-18 ({SOGLIA_CHANCE} di fila!)\nUltimi: {ultimi}")
    elif all(19 <= n <= 36 for n in ultimi):
        send_telegram(f"📈 ALLARME PASSE 19-36 ({SOGLIA_CHANCE} di fila!)\nUltimi: {ultimi}")

def run_bot():
    send_telegram("🚀 Bot avviato. Test diagnostico in corso...")
    
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
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 720}
                )
                page = context.new_page()
                
                url = "https://tracksino.com/mega-fire-blaze-roulette"
                
                try:
                    page.goto(url, timeout=60000, wait_until="networkidle")
                    titolo_pagina = page.title()
                    send_telegram(f"🌐 Pagina caricata: '{titolo_pagina}'")
                except Exception as e:
                    send_telegram(f"❌ Errore caricamento pagina: {e}")

                while True:
                    try:
                        elementi = page.query_selector_all("span, div, td")
                        
                        estrazioni = []
                        for el in elementi:
                            try:
                                txt = el.inner_text().strip()
                                if txt.isdigit() and 0 <= int(txt) <= 36 and len(txt) <= 2:
                                    estrazioni.append(int(txt))
                            except:
                                pass

                        if estrazioni:
                            # Prende i primi 10 numeri trovati
                            numeri_rilevati = estrazioni[:10]
                            send_telegram(f"🎯 Numeri estratti live: {numeri_rilevati}")
                            analizza_ritardi(numeri_rilevati)
                            time.sleep(15)
                        else:
                            send_telegram("⚠️ Nessun numero letto nella struttura. In attesa di aggiornamento...")
                            time.sleep(20)

                    except Exception as e:
                        print(f"Errore lettura: {e}")
                        time.sleep(10)

        except Exception as e:
            print(f"Errore browser: {e}")
            time.sleep(15)

if __name__ == "__main__":
    run_bot()

import os
import time
import requests

# Installazione dipendenze e Chromium su Railway
os.system("playwright install-deps chromium")
os.system("playwright install chromium")

from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# SOGLIA RITARDI PER ALLARME (Impostata a 1 per il test)
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

    # 1. Rosso / Nero
    if all(n in ROSSI for n in ultimi):
        send_telegram(f"🔴 ALLARME ROSSO ({SOGLIA_CHANCE} di fila!)\nUltimi: {ultimi}")
    elif all(n in NERI for n in ultimi):
        send_telegram(f"⚫ ALLARME NERO ({SOGLIA_CHANCE} di fila!)\nUltimi: {ultimi}")

    # 2. Pari / Dispari (escluso lo 0)
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
    send_telegram(f"🚀 Bot Roulette attivo! Monitoraggio via CasinoScores (Soglia test: {SOGLIA_CHANCE}).")
    
    while True:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
                )
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                
                # URL del tracker pubblico con i dati live di Mega Fire Blaze Roulette
                url = "https://www.casinoscores.com/mega-fire-blaze-roulette/"
                try:
                    page.goto(url, timeout=60000, wait_until="domcontentloaded")
                    time.sleep(5)
                except Exception as e:
                    print(f"Errore caricamento pagina: {e}")

                while True:
                    try:
                        # Lettura numeri estratti dalla tabella live
                        elementi = page.query_selector_all("[class*='history'] div, [class*='result'] div, .game-history div")
                        
                        estrazioni = []
                        for el in elementi:
                            txt = el.inner_text().strip()
                            if txt.isdigit() and 0 <= int(txt) <= 36:
                                estrazioni.append(int(txt))

                        if estrazioni:
                            analizza_ritardi(estrazioni)

                        time.sleep(8)
                    except Exception as e:
                        print(f"Errore ciclo lettura: {e}")
                        time.sleep(5)
        except Exception as e:
            print(f"Errore browser: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_bot()

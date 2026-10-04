import os
import time
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# SOGLIA RITARDI PER ALLARME (8 colpi di fila)
SOGLIA_CHANCE = 8

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Errore: TELEGRAM_TOKEN o CHAT_ID non trovati.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

# Tabelle delle Chance Semplici
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
    send_telegram(f"🚀 Bot Roulette attivo! Monitoraggio impostato a quota {SOGLIA_CHANCE} ritardi.")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # URL del tavolo da monitorare
        url = "https://www.bet365.it"
        try:
            page.goto(url, timeout=60000)
        except Exception as e:
            print(f"Errore caricamento pagina: {e}")

        ultimi_numeri = []
        while True:
            try:
                # Il bot esegue il controllo ad ogni estrazione
                analizza_ritardi(ultimi_numeri)
                time.sleep(8)
            except Exception as e:
                print(f"Errore durante il ciclo: {e}")
                time.sleep(3)

if __name__ == "__main__":
    run_bot()

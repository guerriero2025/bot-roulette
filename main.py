import os
import time
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Errore: TELEGRAM_TOKEN o CHAT_ID non trovati nelle variabili.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

def run_bot():
    send_telegram("🚀 Bot Roulette avviato correttamente su Railway 24/7!")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Browser avviato. Inizio monitoraggio...")
        
        # Inserisci qui l'URL della roulette live
        url = "https://www.bet365.it"
        
        try:
            page.goto(url, timeout=60000)
        except Exception as e:
            print(f"Errore caricamento pagina: {e}")

        ultimi_numeri = []

        while True:
            try:
                # Ciclo di controllo ogni 8 secondi
                print("Controllo dati tavolo live...")
                time.sleep(8)
            except Exception as e:
                print(f"Errore durante il ciclo: {e}")
                time.sleep(5)

if __name__ == "__main__":
    run_bot()

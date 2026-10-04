import os
import time
import requests

# Installazione automatica delle librerie necessarie (senza Chromium)
os.system("pip install curl-cffi beautifulsoup4")

from bs4 import BeautifulSoup
from curl_cffi import requests as crequests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# SOGLIA RITARDI (1 per il test immediato, imposta a 8 a test superato)
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
    send_telegram("🚀 Bot avviato! Connessione diretta con impronta Chrome reale...")
    
    url = "https://tracksino.com/mega-fire-blaze-roulette"
    conferma_inviata = False

    while True:
        try:
            # impersonate="chrome120" supera i blocchi di Cloudflare senza aprire browser
            res = crequests.get(url, impersonate="chrome120", timeout=15)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                
                # Estrazione pulita dei testi numerici dall'HTML
                testi = soup.get_text(separator=" ").split()
                estrazioni = []
                for t in testi:
                    if t.isdigit():
                        val = int(t)
                        if 0 <= val <= 36:
                            estrazioni.append(val)

                if estrazioni:
                    if not conferma_inviata:
                        send_telegram(f"✅ Connessione riuscita! Primi numeri intercettati: {estrazioni[:8]}")
                        conferma_inviata = True
                    
                    analizza_ritardi(estrazioni)
            else:
                print(f"Risposta HTTP: {res.status_code}")

        except Exception as e:
            print(f"Errore connessione: {e}")

        time.sleep(10)

if __name__ == "__main__":
    run_bot()

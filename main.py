import os
import time
import json
import requests
import websocket

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# SOGLIA RITARDI (1 per test rapido, impostare a 8 a test superato)
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

conferma_inviata = False

def on_message(ws, message):
    global conferma_inviata
    try:
        # Decodifica dei pacchetti dati dal socket
        if "spinHistory" in message or "result" in message or "number" in message:
            # Estrazione numeri interi dal messaggio JSON/Socket
            import re
            numeri_trovati = [int(n) for n in re.findall(r'\b\d+\b', message) if 0 <= int(n) <= 36]
            
            if numeri_trovati:
                if not conferma_inviata:
                    send_telegram(f"⚡ WEBSOCKET AGGANCIATO! Ricevuti numeri live: {numeri_trovati[:8]}")
                    conferma_inviata = True
                
                analizza_ritardi(numeri_trovati)
    except Exception as e:
        print(f"Errore parsing WS: {e}")

def on_open(ws):
    send_telegram("📡 Connessione WebSocket stabilita. In ascolto dei pacchetti dati live...")

def on_error(ws, error):
    print(f"Errore WS: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket chiuso, riconnessione in corso...")
    time.sleep(5)

def run_bot():
    send_telegram("🚀 Avvio connessione diretta WebSocket al feed della roulette...")
    
    # Assicuriamo la presenza della libreria websocket-client
    os.system("pip install websocket-client")
    
    ws_url = "wss://tracksino.com/socket.io/?EIO=4&transport=websocket"
    
    while True:
        try:
            ws = websocket.WebSocketApp(
                ws_url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                header={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
            )
            ws.run_forever()
        except Exception as e:
            print(f"Errore connessione WS: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()

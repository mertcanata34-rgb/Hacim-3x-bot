import requests
import time

TELEGRAM_TOKEN = "8759173702:AAE7aulQPRzcbO70ZZoJeNUY80t50leXsgk"
CHAT_ID = "1697272388"
VOLUME_MULTIPLIER = 3
CHECK_INTERVAL = 900
MIN_24H_VOLUME_USD = 10000000

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data, timeout=10)
    except: pass

def get_filtered_symbols():
    print("Bybit 24s hacim > 10M coinler cekiliyor...")
    url = "https://api.bybit.com/v5/market/tickers"
    params = {"category": "linear"}
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=15)
        if r.status_code!= 200:
            send_telegram(f"Bybit Hata: {r.status_code}")
            return []
        data = r.json()['result']['list']
        symbols = [
            s['symbol'] for s in data
            if float(s.get('turnover24h', 0)) > MIN_24H_VOLUME_USD
            and s['symbol'].endswith('USDT')
        ]
        print(f"{len(symbols)} coin 10M USD ustu")
        return symbols
    except Exception as e:
        send_telegram(f"Bybit Hata: {e}")
        return []

def check_volume_spike(symbol):
    url = "https://api.bybit.com/v5/market/kline"
    params = {"category": "linear", "symbol": symbol, "interval": "15", "limit": 3}
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        if r.status_code!= 200: return None
        data = r.json()['result']['list']
        if len(data) < 3: return None
        # Bybit data: [start, open, high, low, close, volume, turnover]
        prev_vol = float(data[1][5])
        curr_vol = float(data[0][5])
        curr_close = float(data[0][4])
        if prev_vol == 0: return None
        if curr_vol >= prev_vol * VOLUME_MULTIPLIER:
            kat = curr_vol / prev_vol
            return {"symbol": symbol, "kat": kat, "price": curr_close}
    except: return None
    return None

def main():
    send_telegram("RAILWAY HACIM X3 BOT BYBIT AKTIF. 15dk | 24s > 10M")
    symbols = get_filtered_symbols()
    if not symbols:
        send_telegram("HATA: Bybit coin listesi cekilemedi. Bot durdu.")
        return

    send_telegram(f"{len(symbols)} coin taranıyor. İlk tarama başlıyor...")
    while True:
        print("\n--- 15DK HACIM X3 TARAMA BYBIT ---")
        alerts = []
        for i, symbol in enumerate(symbols):
            if i % 50 == 0: print(f"{i}/{len(symbols)}")
            r = check_volume_spike(symbol)
            if r:
                alerts.append(f"X3 {r['symbol']} {r['kat']:.1f} KAT F:{r['price']}")
            time.sleep(0.1)

        if alerts:
            mesaj = "15DK HACIM X3 ALARM BYBIT\n" + "\n".join(alerts[:15])
            send_telegram(mesaj)
            print(f"Alarm gitti. {len(alerts)} sinyal")
        else:
            print("Sinyal yok. 15dk bekleniyor...")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()

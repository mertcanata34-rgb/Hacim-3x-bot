import requests
import time
import random

TELEGRAM_TOKEN = "8759173702:AAE7aulQPRzcbO70ZZoJeNUY80t50leXsgk"
CHAT_ID = "1697272388"
VOLUME_MULTIPLIER = 3
CHECK_INTERVAL = 900
MIN_24H_VOLUME_USD = 10000000

# Ücretsiz proxy listesi - biri patlarsa diğeri dener
PROXY_LIST = [
    None, # İlk önce proxy'siz dene
    'http://51.158.68.133:8811',
    'http://51.158.172.165:8811',
    'http://163.172.146.210:3128'
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def get_with_proxy(url, params=None):
    for proxy in PROXY_LIST:
        try:
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            r = requests.get(url, params=params, headers=HEADERS, proxies=proxies, timeout=15)
            if r.status_code == 200:
                return r
            print(f"Proxy {proxy} hata: {r.status_code}")
        except Exception as e:
            print(f"Proxy {proxy} patladı: {e}")
            continue
    return None

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data, timeout=10)
    except: pass

def get_filtered_symbols():
    print("24s hacim > 10M olan coinler cekiliyor...")
    url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
    r = get_with_proxy(url)
    if not r:
        send_telegram("Binance Hata: 451. Tum proxyler banlı. 1 saat sonra dener.")
        return []
    try:
        data = r.json()
        symbols = [
            s['symbol'] for s in data
            if float(s.get('quoteVolume', 0)) > MIN_24H_VOLUME_USD
            and s['symbol'].endswith('USDT')
        ]
        print(f"{len(symbols)} coin 10M USD ustu")
        return symbols
    except Exception as e:
        send_telegram(f"JSON Hata: {e}")
        return []

def check_volume_spike(symbol):
    url = "https://fapi.binance.com/fapi/v1/klines"
    params = {"symbol": symbol, "interval": "15m", "limit": 3}
    r = get_with_proxy(url, params=params)
    if not r: return None
    try:
        data = r.json()
        if len(data) < 3: return None
        prev_vol = float(data[-2][5])
        curr_vol = float(data[-1][5])
        curr_close = float(data[-1][4])
        if prev_vol == 0: return None
        if curr_vol >= prev_vol * VOLUME_MULTIPLIER:
            kat = curr_vol / prev_vol
            return {"symbol": symbol, "kat": kat, "price": curr_close}
    except: return None
    return None

def main():
    send_telegram("RAILWAY HACIM X3 BOT PROXY MOD AKTIF. 15dk | 24s > 10M")
    symbols = get_filtered_symbols()
    if not symbols:
        send_telegram("HATA: Coin listesi cekilemedi. Bot 1 saat uyuyacak.")
        time.sleep(3600)
        return

    send_telegram(f"{len(symbols)} coin taranıyor. İlk tarama başlıyor...")
    while True:
        print("\n--- 15DK HACIM X3 TARAMA ---")
        alerts = []
        for i, symbol in enumerate(symbols):
            if i % 50 == 0: print(f"{i}/{len(symbols)}")
            r = check_volume_spike(symbol)
            if r:
                alerts.append(f"X3 {r['symbol']} {r['kat']:.1f} KAT F:{r['price']}")
            time.sleep(0.05)

        if alerts:
            mesaj = "15DK HACIM X3 ALARM\n" + "\n".join(alerts[:15])
            send_telegram(mesaj)
            print(f"Alarm gitti. {len(alerts)} sinyal")
        else:
            print("Sinyal yok. 15dk bekleniyor...")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()

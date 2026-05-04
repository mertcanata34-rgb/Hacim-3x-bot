   import requests
   import time

   TELEGRAM_TOKEN = "8759173702:AAE7aulQPRzcbO70ZZoJeNUY80t50leXsgk"
   CHAT_ID = "1697272388"
   VOLUME_MULTIPLIER = 3
   CHECK_INTERVAL = 900
   MIN_24H_VOLUME_USD = 10000000

   HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

   def send_telegram(msg):
       url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
       data = {"chat_id": CHAT_ID, "text": msg}
       try:
           r = requests.post(url, data=data, timeout=10)
           print(f"TG: {r.status_code}")
       except Exception as e:
           print(f"TG Hata: {e}")

   def get_filtered_symbols():
       print("24s hacim > 10M olan coinler cekiliyor...")
       url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
       try:
           r = requests.get(url, headers=HEADERS, timeout=15)
           if r.status_code!= 200:
               send_telegram(f"Binance Hata: {r.status_code}. IP engeli olabilir.")
               print(f"Binance Hata: {r.status_code} {r.text[:100]}")
               return []
           data = r.json()
           symbols = [
               s['symbol'] for s in data
               if float(s.get('quoteVolume', 0)) > MIN_24H_VOLUME_USD
               and s['symbol'].endswith('USDT')
           ]
           print(f"{len(symbols)} coin 10M USD ustu")
           return symbols
       except Exception as e:
           print(f"24hr Hata: {e}")
           send_telegram(f"HATA: Coin listesi cekilemedi. {e}")
           return []

   def check_volume_spike(symbol):
       url = "https://fapi.binance.com/fapi/v1/klines"
       params = {"symbol": symbol, "interval": "15m", "limit": 3}
       try:
           r = requests.get(url, params=params, headers=HEADERS, timeout=10)
           if r.status_code!= 200:
               return None
           data = r.json()
           if len(data) < 3: return None
           prev_vol = float(data[-2][5])
           curr_vol = float(data[-1][5])
           curr_close = float(data[-1][4])
           if prev_vol == 0: return None
           if curr_vol >= prev_vol * VOLUME_MULTIPLIER:
               kat = curr_vol / prev_vol
               return {"symbol": symbol, "kat": kat, "price": curr_close}
       except:
           return None
       return None

   def main():
       send_telegram("RAILWAY HACIM X3 BOT AKTIF. 15dk | 24s > 10M")
       symbols = get_filtered_symbols()
       if not symbols:
           send_telegram("HATA: Coin listesi cekilemedi. Bot durdu.")
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

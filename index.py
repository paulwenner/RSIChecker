import ccxt
import pandas as pd
import time
from ta.momentum import RSIIndicator
from pushover import Client, init
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Pushover client
user_key = os.getenv("PUSHOVER_USER_KEY")
api_token = os.getenv("PUSHOVER_API_TOKEN")

if not user_key or not api_token:
    raise ValueError("Pushover user key and API token must be set in the environment variables.")

# Initialize the Pushover module with the API token
init(api_token)

client = Client(user_key)

def send_notification(message):
    """
    Sends a push notification via Pushover.
    """
    client.send_message(message, title="RSI Alert")

def get_rsi(exchange, symbol, timeframe='1d', limit=100):
    """
    Fetches OHLCV data for 'symbol' and 'timeframe' from the 'exchange'
    and calculates the RSI value of the last candle.
    """
    # Load OHLCV data: [Timestamp, Open, High, Low, Close, Volume]
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    
    # Convert to DataFrame
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # Make timestamp readable
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Calculate RSI (standard window: 14 periods)
    rsi_series = RSIIndicator(df['close'], window=14).rsi()
    
    # Return the last RSI value
    return rsi_series.iloc[-1]


def main():
    crypto_symbols = [
        "BTC/USDT",
        "ETH/USDT",
        "SOL/USDT",
        "ADA/USDT",
        "TRUMP/USDT",
        "XRP/USDT",
        "LTC/USDT",
        "DOT/USDT",
        "DOGE/USDT",
        "BNB/USDT",
        "SHIB/USDT",
        "MATIC/USDT",
        "LINK/USDT",
        "UNI/USDT",
        "AVAX/USDT",
        "ALGO/USDT",
    ]
    timeframes = ["1d", "1h", "15m", "5m", "1w"]
    exchange = ccxt.binance()
    interval_map = {
        "5m": 5,
        "15m": 15,
        "1h": 60,
        "1d": 1440,
        "1w": 10080
    }
    
    last_notification = {symbol: {tf: None for tf in timeframes} for symbol in crypto_symbols}
    
    while True:
        current_time = datetime.datetime.now()
        for symbol in crypto_symbols:
            for tf in timeframes:
                try:
                    rsi_value = get_rsi(exchange, symbol, tf)
                    interval_minutes = interval_map.get(tf, 60)
                    
                    if rsi_value > 75 or rsi_value < 25:
                        last_notif_time = last_notification[symbol][tf]
                        if (last_notif_time is None or
                            (current_time - last_notif_time).total_seconds() >= interval_minutes * 60):
                            message = f"{symbol} RSI on {tf} is {rsi_value:.2f}!"
                            send_notification(message)
                            print(message)
                            last_notification[symbol][tf] = current_time
                
                except Exception as e:
                    print(f"Error with {symbol} on {tf} basis: {e}")
        
        time.sleep(30)
            

if __name__ == "__main__":
    send_notification("RSI Observer started.")
    main()
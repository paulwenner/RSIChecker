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
    # List of your crypto symbols
    crypto_symbols = [
        "BTC/USDT",
        "ETH/USDT",
        "SOL/USDT",  
        "ADA/USDT",  
        "TRUMP/USDT" 
    ]
    
    # Desired intervals (timeframes)
    timeframes = ["1d", "1h", "15m", "5m", "1w"]  # daily, hourly, 15 min, 5 min, weekly
    
    # Create exchange object (here: Binance)
    exchange = ccxt.binance()
    
    # Define intervals in minutes for each timeframe
    interval_map = {
        "5m": 5,
        "15m": 15,
        "1h": 60,
        "1d": 1440,
        "1w": 10080
    }

    # Initialize last run times for each timeframe
    last_run = {tf: None for tf in timeframes}

    while True:
        current_time = datetime.datetime.now()
        for symbol in crypto_symbols:
            for tf in timeframes:
                interval = interval_map.get(tf, 60)
                last = last_run[tf]
                if last is None or (current_time - last).total_seconds() >= interval * 60:
                    try:
                        rsi_value = get_rsi(exchange, symbol, tf)
                        
                        if rsi_value > 75:
                            message = f"{symbol} RSI on {tf} basis is {rsi_value:.2f} (over 75)!"
                            send_notification(message)
                            print(message)
                        elif rsi_value < 25:
                            message = f"{symbol} RSI on {tf} basis is {rsi_value:.2f} (under 25)!"
                            send_notification(message)
                            print(message)
                        
                        last_run[tf] = current_time
                
                    except Exception as e:
                        print(f"Error with {symbol} on {tf} basis: {e}")
            
            time.sleep(60)  # Check every minute
            

if __name__ == "__main__":
    send_notification("RSI Observer started.")
    main()
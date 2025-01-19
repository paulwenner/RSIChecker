import ccxt
import pandas as pd
import time
from ta.momentum import RSIIndicator

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
    
    while True:
        # Single run: Calculate and check RSI for each symbol and each interval
        for symbol in crypto_symbols:
            for tf in timeframes:
                try:
                    rsi_value = get_rsi(exchange, symbol, tf)
                    
                    # Condition: RSI > 75 or < 25
                    if rsi_value > 75:
                        print(f"{symbol} RSI on {tf} basis is {rsi_value:.2f} (over 75)!")
                    elif rsi_value < 25:
                        print(f"{symbol} RSI on {tf} basis is {rsi_value:.2f} (under 25)!")
                    # Optionally, you can print nothing or print the value anyway:
                    # else:
                    #    print(f"{symbol} RSI on {tf} basis is {rsi_value:.2f} (in normal range).")
                
                except Exception as e:
                    print(f"Error with {symbol} on {tf} basis: {e}")
        
        # Wait time between runs (e.g., 60 seconds)
        time.sleep(60)

if __name__ == "__main__":
    main()
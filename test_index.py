import unittest
from unittest.mock import MagicMock
import pandas as pd
from index import get_rsi, main

class TestRSIObserver(unittest.TestCase):
    
    def setUp(self):
        # Mock exchange object
        self.mock_exchange = MagicMock()
        self.mock_exchange.fetch_ohlcv.return_value = [
            [1609459200000, 29000, 29500, 28500, 29000, 1000],
            [1609545600000, 29000, 30000, 28000, 29500, 2000],
            # ... more mock data ...
        ]
    
    def test_get_rsi(self):
        symbol = "BTC/USDT"
        timeframe = "1d"
        rsi_value = get_rsi(self.mock_exchange, symbol, timeframe)
        
        # Check if the RSI value is a float
        self.assertIsInstance(rsi_value, float)
    
    def test_main(self):
        # Mock print to capture print statements
        with unittest.mock.patch('builtins.print') as mocked_print:
            main()
            # Check if print was called (indicating RSI values were printed)
            self.assertTrue(mocked_print.called)

if __name__ == "__main__":
    unittest.main()

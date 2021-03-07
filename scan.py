import os, csv
import talib
import pandas as pd
from patterns import candlestick_patterns

def scanStocks(pattern):
    bullish = []
    bearish = []

    for filename in os.listdir('current'):
        df = pd.read_csv('current/{}'.format(filename))
        pattern_function = getattr(talib, pattern)
        symbol = filename.split('.')[0]

        try:
            results = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
            #print(results)
            last = results.tail(1).values[0]

            #print(f"last for {symbol} is {last}")
            if last > 0:
                bullish.append(symbol)
            elif last < 0:
                bearish.append(symbol)

        except Exception as e:
            print('failed on filename: ', filename)

    return bullish, bearish
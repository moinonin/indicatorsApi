from fileinput import close
import ccxt, fire
from datetime import datetime
import pandas as pd

import plotly.graph_objects as go
# collect the candlestick data from Binance
binance = ccxt.binance()



class Stream:
    def __init__(self, pair, timeframe):
        self.pair = pair.upper()
        self.timeframe = timeframe

    def get_dataframe(self):
        candles = binance.fetch_ohlcv(self.pair, self.timeframe)
        dates = []
        open_data = []
        high_data = []
        low_data = []
        close_data = []
        volume_data = []
        # format the data to match the charting library
        for candle in candles:
            dates.append(datetime.fromtimestamp(candle[0] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f'))
            open_data.append(candle[1])
            high_data.append(candle[2])
            low_data.append(candle[3])
            close_data.append(candle[4])
            volume_data.append(candle[5])

        df = pd.DataFrame()
        df['date'] = dates
        df['open'] = open_data
        df['high'] = high_data
        df['low'] = low_data
        df['close'] = close_data
        df['volume'] = volume_data

        return df
    
    def plot_candles(self):
        # plot the candlesticks
        dates = self.get_dataframe().date
        open_data = self.get_dataframe().open
        high_data = self.get_dataframe().high
        low_data = self.get_dataframe().low
        close_data = self.get_dataframe().close

        fig = go.Figure(data=[go.Candlestick(x=dates,
                            open=open_data, high=high_data,
                            low=low_data, close=close_data)])
        return fig.show()

def main(pair, timeframe):
    obj = Stream(pair, timeframe).get_dataframe()
    return obj


if __name__ == '__main__':
    fire.Fire(main())
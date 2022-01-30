#!/usr/bin/env python3
import talib.abstract as ta
import numpy as np
from fetchdata.stream import Stream
from fetchdata import estimators as qtpylib
#from data import *
import gc
from regpredict import regbot




def pop_indicators(pair,timeframe):
#for pair in whitelist:
    dataframe = Stream(f'{pair}', f'{timeframe}').get_dataframe()
    # Bollinger Bands
    bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
    dataframe.loc[:,'bb_lowerband'] = bollinger['lower']
    dataframe.loc[:,'bb_middleband'] = bollinger['mid']
    dataframe.loc[:,'bb_upperband'] = bollinger['upper']

    dataframe['adx'] = ta.ADX(dataframe, timeperiod=5)
    # RSI
    dataframe['rsi'] = ta.RSI(dataframe, timeperiod=15)
    # MACD
    macd = ta.MACD(dataframe)
    dataframe['macd'] = macd['macd']
    dataframe['macdsignal'] = macd['macdsignal']
    # Exponential moving averages
    dataframe['ema12'] = ta.EMA(dataframe, timeperiod=12)
    dataframe['ema26'] = ta.EMA(dataframe, timeperiod=26)
    # SMA - Simple Moving Average
    dataframe['sma-03'] = ta.SMA(dataframe, timeperiod=3)
    dataframe['sma-05'] = ta.SMA(dataframe, timeperiod=5)
    dataframe['sma-07'] = ta.SMA(dataframe, timeperiod=7)
    dataframe['sma-10'] = ta.SMA(dataframe, timeperiod=10)
    dataframe['sma-21'] = ta.SMA(dataframe, timeperiod=21)
    dataframe['sma-15'] = ta.SMA(dataframe, timeperiod=15)
    dataframe['sma-25'] = ta.SMA(dataframe, timeperiod=25)
    dataframe['sma-30'] = ta.SMA(dataframe, timeperiod=30)
    dataframe['sma-50'] = ta.SMA(dataframe, timeperiod=50)
    dataframe['sma-100'] = ta.SMA(dataframe, timeperiod=100)
    # Additional indicators
    dataframe['rsi-05'] = ta.RSI(dataframe['close'], timeperiod=5)
    dataframe['rsi-15'] = ta.RSI(dataframe['close'], timeperiod=15)
    dataframe['rsi-25'] = ta.RSI(dataframe['close'], timeperiod=25)
    dataframe['sma-99'] = ta.SMA(dataframe['close'], timeperiod=99)
    dataframe['grad-rsi-05'] = np.gradient(dataframe.loc[:,'rsi-05'].rolling(center=False,window=15).mean())
    dataframe['grad-rsi-15'] = np.gradient(dataframe.loc[:,'rsi-15'].rolling(center=False,window=15).mean())
    dataframe['grad-sma-99'] = np.gradient(dataframe.loc[:,'sma-99'].rolling(center=False,window=15).mean())
    dataframe['grad-sma-05'] = np.gradient(dataframe.loc[:,'sma-05'].rolling(center=False,window=15).mean())
    dataframe['grad-sma-07'] = np.gradient(dataframe.loc[:,'sma-07'].rolling(center=False,window=15).mean())
    dataframe['grad-sma-25'] = np.gradient(dataframe.loc[:,'sma-25'].rolling(center=False,window=15).mean())
    # EVX ML model
    row = dataframe.iloc[-1].squeeze()
    opening = row['open']
    closing = row['close']
    volume = row['volume']
    gc.collect()
    dataframe['regbot-min'] = regbot.signal(opening,closing,volume) # 0.0018, 0.0022

    dataframe.loc[:,'c'] = dataframe.loc[:,'close'] -   dataframe.loc[:,'open']
    dataframe.loc[:,'bid-ind'] = abs(dataframe.loc[:,'volume']*(dataframe.loc[:,'c'] - dataframe.loc[:,'close'])/(dataframe.loc[:,'open'] + dataframe.loc[:,'close']))
    dataframe.loc[:,'ask-ind'] = abs(dataframe.loc[:,'volume']*(dataframe['c'] + dataframe.loc[:,'open'])/(dataframe.loc[:,'open'] + dataframe.loc[:,'close']))
    dataframe.loc[:,'by'] = dataframe.loc[:,'bid-ind']*dataframe.loc[:,'close']
    dataframe.loc[:,'ax'] = dataframe.loc[:,'ask-ind']*dataframe.loc[:,'open']
    dataframe.loc[:,'bx'] = dataframe.loc[:,'bid-ind']*dataframe.loc[:,'open']
    dataframe.loc[:,'ay'] = dataframe.loc[:,'ask-ind']*dataframe.loc[:,'close']
    dataframe.loc[:,'momentum-ind'] = ((dataframe.loc[:,'bid-ind'] - dataframe.loc[:,'ask-ind']) / dataframe.loc[:,'ask-ind'])
    dataframe.loc[:,'ratio1'] = dataframe.loc[:,'by'] / dataframe.loc[:,'ax']
    dataframe.loc[:,'ratio2'] = dataframe.loc[:,'bx'] / dataframe.loc[:,'ay']
    dataframe.loc[:,'obj_func'] = dataframe.loc[:,'by'] - dataframe.loc[:,'ax']
    dataframe.loc[:,'MACD-LINE'] = dataframe['ema12'] - dataframe['ema26']
    dataframe.loc[:,'DEM'] = ta.EMA(dataframe.loc[:,'MACD-LINE'], timeperiod=9)
    dataframe.loc[:,'DIF'] = dataframe.loc[:,'DEM'] + dataframe.loc[:,'MACD-LINE']
    dataframe.loc[:,'ratio3'] = dataframe.loc[:,'DIF'] / dataframe.loc[:,'DEM']
    dataframe.loc[:,'dif-dem'] = abs(dataframe.loc[:,'DIF']) / abs(dataframe.loc[:,'DEM'])
    dataframe.loc[:,'momentum-gradient'] = np.gradient(dataframe.loc[:,'momentum-ind'].rolling(center=False,window=7).mean())
    dataframe.loc[:,'rsi-gradient'] = np.gradient(dataframe.loc[:,'rsi'].rolling(center=False,window=15).mean())
    dataframe.loc[:,'ratio4'] = dataframe.loc[:,'close'] / dataframe.loc[:,'open']
    dataframe.loc[:,'close-gradient'] = np.gradient(dataframe.loc[:,'ratio4'].rolling(center=False,window=7).mean())
    dataframe.loc[:,'slope-obj'] = np.gradient(dataframe.loc[:,'obj_func'].rolling(center=False,window=4).mean())
    dataframe.loc[:,'slope-ratio4'] = ta.LINEARREG_SLOPE(dataframe.loc[:,'ratio4'], timeperiod=14)
    dataframe.loc[:,'slope-bbm'] = np.gradient(dataframe.loc[:,'bb_middleband'].rolling(center=False,window=14).mean())
    dataframe.loc[:,'stabilizer'] = dataframe.loc[:,'high']*dataframe.loc[:,'open'] - dataframe.loc[:,'close']*dataframe.loc[:,'low']
    dataframe['alpha'] = (dataframe['high']/dataframe['open']) -1

    return dataframe

def get_indicators_dict(pair,timeframe):
    dataframe = pop_indicators(pair, timeframe)
    params = dataframe.iloc[-1].squeeze()
    mydict = dict(zip(params.index, params.values))
    return mydict

def main(pair,timeframe):
    indicator = {
        'pair': pair,
        'indicators': [get_indicators_dict(pair, timeframe)]
    }

    return indicator

if __name__ == '__main__':
    main()
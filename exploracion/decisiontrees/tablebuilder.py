"""
El Proposito de este archivo es crear una tabla gigante con osciladores y diferenciales para explorar que combinación de
osciladores/indicadores general los mejores y peores diferenciales entre sesiones

Para la generac ion de las columnas de oscilaciones e indicadores me baso en las funciones de la ruta
techanalysys.oscillators
"""

import MetaTrader5
from mt5interface.placingorders import getratesaspandasdataframe, gettickerlist
from techanalysis.oscillators import rsi, macd, sma, ema
import pandas
import os

MetaTrader5.initialize(login=30383295, password="Pknrp2h8@", server="AdmiralMarkets-Live")


def buildtableintocsv(ticker):
    df = getratesaspandasdataframe(ticker, MetaTrader5.TIMEFRAME_D1, "01-01-2017 08:00", "31-12-2021 18:30")
    todrop = ["open", "high", "low", "tick_volume", "spread", "real_volume", "date"]
    df.drop(todrop,axis=1, inplace=True)
    #filling differences up to n sessions
    for i in range(1,6):
        df["diff_" + str(i)] = (df["close"].shift(-i) - df["close"])/df["close"]

    #annotate the number of diff sessions are above 4% (0.04)
    df["diff_n_sessions_above_4_perc"] = pandas.Series()
    for i, row in df.iterrows():
        counter = 0
        for j in range(1, 6):
            if row["diff_" + str(j)] > 0.04:
                counter += 1
        df["diff_n_sessions_above_4_perc"][i] = counter
    df["session_has_above_4perc_returns"] = (df["diff_n_sessions_above_4_perc"]>0)

    #filling rsi columns
    rsiperiods = [14,28,42,56,70,84,98]
    for i in rsiperiods:
        rsi_ = rsi(df["close"].values, i)
        df["rsi_" + str(i)] = pandas.Series(rsi_)
        df["rsi_" + str(i) + "_shift"] = df["rsi_" + str(i)].shift(4)
        df["rsi_" + str(i) + "_trend"] = df["rsi_" + str(i)] - df["rsi_" + str(i) + "_shift"]
    #filling macd values
    macdline, signalline, diff = macd(df["close"].values, 12, 26, 9)
    df["macd_macdline"] = pandas.Series(macdline)
    df["macd_signalline"] = pandas.Series(signalline)
    df["macd_diff"] = pandas.Series(diff)
    df["macd_diff_shift"] = df["macd_diff"].shift(-4)
    df["macd_diff_trend"] = df["macd_diff"] - df["macd_diff_shift"]

    #filling sma's and ema's
    maperiods = [5,10,20,50,70,150,200]
    shifts = [2, 5, 10, 25, 35, 75, 100]
    for index, i in enumerate(maperiods):
        sma_ = sma(df["close"].values, i)
        ema_ = ema(df["close"].values, i)
        df["sma_" + str(i)] = pandas.Series(sma_)
        df["sma_" + str(i) + "_shift"] = df["sma_" + str(i)].shift(shifts[index])
        df["sma_" + str(i) + "_trend"] = df["sma_" + str(i)] - df["sma_" + str(i) + "_shift"]
        df["ema_" + str(i)] = pandas.Series(ema_)
        df["ema_" + str(i) + "_shift"] = df["ema_" + str(i)].shift(shifts[index])
        df["ema_" + str(i) + "_trend"] = df["ema_" + str(i)] - df["ema_" + str(i) + "_shift"]

    df.to_csv(os.getcwd() + "\\files\\" + ticker + '.csv')
    print(ticker)




# tickers = gettickerlist()
tickers = ["ALMSA"]
for t in tickers:
    buildtableintocsv(t)


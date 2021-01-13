#en este archivo hago exploraciones de operaciones con la mediamobil de 6 dias.
import MetaTrader5 as mt5
from mt5interface.placingorders import getratesaspandasdataframe, gettickerlist
import pandas
import math
import matplotlib.pyplot as plt
from techanalysis.oscillators import getrsi
import os

def issignalpoint(row):
    # return (row["ma6d"] > row["ma20d"]) and (row["ma6d"]<=(row["ma20d"]*1.02)) and (row["ma5slopema6"]>=0) and (row["ma2slopema20"]>=0)
    # rule = (row["close"]>row["ma6"])
    # rule &= (row["ma6"]<row["ma20"])
    # rule &= (row["rsi20"]<30)
    # rule &= (row["rsi70"]<15)
    # rule &= (row["slopema6"] > 0)
    # rule &= (row["slopema20"] < 0)
    return False





#rescato datos
def plotchartforticker(ticker):
    df = getratesaspandasdataframe(ticker,mt5.TIMEFRAME_H1, "01-01-2020 08:00", "09-01-2021 18:30")
    todrop = ["open", "high", "low", "date" ]
    df.drop(labels=todrop, axis=1, inplace=True)

    df["ma20"] = df["close"].rolling(window=20).mean()
    df["ma20"] = df["ma20"].shift(-20)











    fig, (ax1, ax2) = plt.subplots(2,1,sharex=True, gridspec_kw={"height_ratios":(0.75,0.25)})
    fig.set_size_inches((10,8))
    ax1.set_title(ticker)
    ax1.plot(df["tts"],df["close"], color="red", linewidth=0.5)
    ax1.plot(df["tts"],df["ma20"], color="orange", linewidth=0.5)






    for index, row in df.iterrows():
        if   issignalpoint(row):
            ax1.scatter(row["tts"],row["close"],color="blue", label=index)
            # ax1.annotate(str(index) + "/" + str(row["close"]), (row["tts"], row["close"]))
        else:
            pass
            # ax1.scatter(row["tts"], row["close"], color="brown")



    path = os.path.dirname(os.path.abspath(__file__))
    # plt.savefig(path + "\\images\\"+ticker+".jpg", dpi=400)
    plt.show()
mt5.initialize(login=30383295, password="Pknrp2h8@", server="AdmiralMarkets-Live")

tickers = gettickerlist()
for t in tickers:
    plotchartforticker(t)
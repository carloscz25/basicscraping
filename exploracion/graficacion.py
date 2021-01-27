"""El proposito de este archivo es analizar los resultados producidos con la tabla generada en el archivo
tablebuilder.py para cada ticker analizado"""

import pandas
import matplotlib.pyplot as pyplot
from mt5interface.placingorders import gettickerlist
import os


def dograficacion(ticker):
    #0. cargamos el dataframe
    df = pandas.read_csv(os.getcwd() + "\\files\\" + ticker + ".csv")

    #El primer filtro debería ser las columnas diff, para ver donde tenemos diferenciales superiores al 4%
    filter = df["rsi_14_trend"]<0
    filter &= df["macd_diff_trend"]>0
    filter &= df["ema_5_trend"]<0
    filter &= df["ema_5"] < df["ema_20"]
    filter &= df["ema_20_trend"] > 0

    sdf = df.loc[filter]

    fig = pyplot.figure()
    pyplot.title(ticker)
    ax1 = pyplot.subplot2grid((5,5),(0,0),rowspan=4, colspan=4)
    ax2 = pyplot.subplot2grid((5, 5), (4, 0), rowspan=1, colspan=4)
    ax3 = pyplot.subplot2grid((5, 5), (0, 4), rowspan=5, colspan=1)

    fig.set_size_inches(18.5, 10.5)
    # ax1.hist(sdf["diff_n_sessions_above_4_perc"].values, orientation='horizontal', bins=[0,1,6])


    ax1.plot(df["tts"], df["close"], linewidth=0.5)
    ax1.plot(df["tts"], df["ema_5"], linewidth=0.5)
    ax1.plot(df["tts"], df["ema_20"], linewidth=0.5)
    for index, row in sdf.iterrows():
        if row["diff_n_sessions_above_4_perc"]>0:
            ax1.scatter(row["tts"], row["close"], color='blue')
        else:
            ax1.scatter(row["tts"], row["close"], color='red')


    ax2.plot(df["tts"], df["rsi_14"], linewidth=0.5, color='orange')

    a = sdf.loc[sdf["diff_n_sessions_above_4_perc"] == 0]["diff_n_sessions_above_4_perc"].count()
    b = sdf.loc[sdf["diff_n_sessions_above_4_perc"]>0]["diff_n_sessions_above_4_perc"].count()
    ax3.bar(["0", "1-5"], [a,b])


    print(len(sdf))

    pyplot.savefig(os.getcwd() + "\\files\\" + ticker + ".jpg")
    # pyplot.show()
    y=2

tickers = gettickerlist()
for t in tickers:
    dograficacion(t)
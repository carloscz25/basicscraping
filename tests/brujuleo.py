import mt5interface as mt5
import MetaTrader5
from mt5interface.placingorders import getratesaspandasdataframe, gettickerlist
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
from mpl_candlestics.mpl_candlesticks import plot_candlesticks
import math
import os
from datetime import datetime
import time
from matplotlib import ticker
import numpy as np
import PyPDF2 as pdf2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image
import os
import io
from datetime import timedelta





path = os.path.dirname(os.path.abspath(__file__))
datenow = datetime.now()
datefrom = datenow + timedelta(days=-365)
dateto = datenow
datefromstr = datefrom.strftime("%d-%m-%Y %H:%M")
datetostr = dateto.strftime("%d-%m-%Y %H:%M")
dateprod = datetime.now().strftime("%d_%m_%Y_%H_%M")

#creamos el canvas en landscape especificando los puntos width/height
c = canvas.Canvas('brujuleo' + dateprod + '.pdf', pagesize=(1121,793))


MetaTrader5.initialize(login=30383295, password="Pknrp2h8@", server="AdmiralMarkets-Live")

tickers = gettickerlist()
d = {}
for t in tickers:
    d[t] = {}
    df = getratesaspandasdataframe(t, MetaTrader5.TIMEFRAME_D1,datefromstr, datetostr)
    #remove outliers
    df["perc_osc"] = df["high"] - df["low"]
    df["perc_osc"] = df["perc_osc"].abs()
    df["perc_osc"] = df["perc_osc"] / df["open"]

    df["high_low_perc"] = df["perc_osc"].rolling(window=5).mean()

    try:
        d[t]["high_low_perc"] = df["high_low_perc"].iloc[-1]
    except:
        d[t]["high_low_perc"] = 0
        pass
    df["volatility"] = df["close"].rolling(window=5).std()
    try:
        d[t]["volatility"] = df["volatility"].iloc[-1]
    except:
        d[t]["volatility"] = 0
        pass
    y = 2



fig, (ax1, ax2) = plt.subplots(2,1, sharex=False)
#sort descending first 15 values of high-low-perc
firstn = 15

sortedbyHLperc = sorted(d, key=lambda k: d[k]["high_low_perc"], reverse=True)
sortedbyHLperc = sortedbyHLperc[0:(firstn-1)]
sortedvaluesHLperc = [d[s]["high_low_perc"] for s in sortedbyHLperc]
sortedvaluesHLperc = sortedvaluesHLperc[0:(firstn-1)]
ax1.bar(sortedbyHLperc, sortedvaluesHLperc)
ax1.set_title("High-Low Oscillation")
#sort descending first 15 values of volatility

sortedbyVOLAT = sorted(d, key=lambda k: d[k]["volatility"], reverse=True)
sortedbyVOLAT = sortedbyVOLAT[0:(firstn-1)]
sortedvaluesVOLAT = [d[s]["volatility"] for s in sortedbyVOLAT]
sortedvaluesVOLAT = sortedvaluesVOLAT[0:(firstn-1)]

ax2.bar(sortedbyVOLAT, sortedvaluesVOLAT)
ax2.set_title("Volatility")
fig.set_size_inches(15,10)

#guardo la imagen del grafico en una imagen en memoria y la adjunto al pdf y creo nueva pagina (showpage)
buf = io.BytesIO()
plt.savefig(buf, dpi=150, format='jpeg')
image = ImageReader(buf)
c.drawImage(image, 0,0,1121, 793)
c.showPage()



#uniques
selectedtickers = set(sortedbyHLperc + sortedbyVOLAT)
selectedtickers = sorted(selectedtickers)

for t in selectedtickers:
    print(t)
    datefromstr = (dateto + timedelta(days=-365)).strftime("%d-%m-%Y %H:%M")
    dfD = getratesaspandasdataframe(t, MetaTrader5.TIMEFRAME_D1, datefromstr, datetostr)
    datefromstr = (dateto + timedelta(days=-90)).strftime("%d-%m-%Y %H:%M")
    dfH4 = getratesaspandasdataframe(t, MetaTrader5.TIMEFRAME_H4, datefromstr, datetostr)
    datefromstr = (dateto + timedelta(days=-45)).strftime("%d-%m-%Y %H:%M")
    dfH1 = getratesaspandasdataframe(t, MetaTrader5.TIMEFRAME_H1, datefromstr, datetostr)
    datefromstr = (dateto + timedelta(days=-20)).strftime("%d-%m-%Y %H:%M")
    df30M = getratesaspandasdataframe(t, MetaTrader5.TIMEFRAME_M30, datefromstr, datetostr)
    fig, ((ax1,ax2),(ax3,ax4)) = plt.subplots(2,2, sharex=False)
    fig.set_size_inches(25,12)
    #ax1.plot(dfD["tts"], dfD["close"], linewidth=0.5)
    plot_candlesticks(dfD, ax1)
    ax1.set_title(t + " D1")
    plot_candlesticks(dfH4, ax2)
    ax2.set_title(t + " H4")
    plot_candlesticks(dfH1, ax3)
    ax3.set_title(t + " H1")
    plot_candlesticks(df30M, ax4)
    ax4.set_title(t + " M30")
    # plt.savefig(path + "\\images\\"+t+".jpg", dpi=400)
    #repetimos proceso de guardar la imagen y saltar de pagina
    buf = io.BytesIO()
    plt.savefig(buf, dpi=150, format='jpeg')
    image = ImageReader(buf)
    c.drawImage(image, 0, 0, 1121, 793)
    c.showPage()

c.save()
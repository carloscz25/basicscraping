import MetaTrader5 as mt5
from mt5interface.placingorders import getratesaspandasdataframe
import pandas
import math
import matplotlib.pyplot as plt


smoothfactor = 2

mt5.initialize(login=30383295, password="Pknrp2h8@", server="AdmiralMarkets-Live")

#reprogramar
#1. Agrupar segmentos por pendiente negativa, pseudocero y positiva
#2. Los ordeno inragrupo de menor a mayor
#3. Determino por grupo valor umbral de longitud de segmento a partir del cual se ahogan los segmentos pequeños
#4. Los que quedan por debajo del valor umbral

df = getratesaspandasdataframe("GRF",mt5.TIMEFRAME_M30, "10-10-2020 10:30", "14-12-2020 17:30")
df["ma"] = df["close"].rolling(window=smoothfactor).mean()
df["slope"] = pandas.Series(dtype=float)
df["line"] = pandas.Series(dtype=int)

prevm2 = None

currlineindex = 0
for index, row in df.iterrows():
    df["line"][index] = currlineindex
    if index >=smoothfactor:
        df["slope"][index] = row["ma"] - df.iloc[index-1]["ma"]
        prevslope = df["slope"][index-1]
        a, b = df["slope"][index], prevslope
        if math.isnan(a) or math.isnan(b):
            continue
        if (abs(a)+abs(b))!=abs(a+b):
            #hay cambio de signo
            currlineindex += 1
            df["line"][index] = currlineindex
nlines = currlineindex+1

lines = []
timestamps = []
closefrom = None
tsfrom = None
for i in range(nlines):
    df_ = df.loc[df["line"]==i]
    if i==0:
        timestamps.append(df["tts"][df_.index.values[0]])
        lines.append(df["close"][df_.index.values[0]])
    if closefrom == None:
        closefrom = df["close"][df_.index.values[0]]
        tsfrom = df["tts"][df_.index.values[0]]
    closeto = df["close"][df_.index.values[len(df_.index.values)-1]]
    tsto = df["tts"][df_.index.values[len(df_.index.values)-1]]
    y = 2
    lines.append(closeto)
    timestamps.append(tsto)
    closefrom = closeto
    tsfrom = tsto

#compute the length of the lines
lengthlines = []
for i in range(len(lines)):
    if i == 0:
        continue
    ts_1 = timestamps[i-1]
    l_1 = lines[i-1]
    ts = timestamps[i]
    l = lines[i]
    lengthlines.append(l - l_1)

    y = 2

#run k means in lengthlines data for 2 clusters
import numpy as np
np_lengthlines = np.array(lengthlines)
np_lengthlines = np.absolute(np_lengthlines)
np_lengthlines2D = np_lengthlines.reshape(-1,1)
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=2, random_state=0).fit(np_lengthlines2D)
labels = kmeans.labels_
y = 2

dflengths = pandas.DataFrame()
dflengths["lengths"] = pandas.Series(lengthlines)
dflengths["abs_lengths"] = pandas.Series(np_lengthlines)
dflengths["group"] = labels
cum_sum_0 = dflengths.loc[dflengths["group"]==0]["abs_lengths"].count()
cum_sum_1 = dflengths.loc[dflengths["group"]==1]["abs_lengths"].count()

#the group with less number of lines is the one that persists. The other segments must be molt with the surrounding segments


plt.plot(df["tts"].values, df["close"].values, label="close", color="blue")
plt.plot(df["tts"].values, df["ma"].values, label="ma", color="red")
plt.plot(timestamps, lines, color="green")

plt.show()
y = 2




mt5.shutdown()
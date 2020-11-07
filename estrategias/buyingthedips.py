from globalutils import getconsolidatedcotizacionesforticker
from globalutils import gettickerlist
from model import getaitraderengine
import datetime
import numpy as np
import pandas

engine = getaitraderengine()

def dt642date(dt64):
    ts = (dt64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
    return datetime.datetime.fromtimestamp(ts).date()

tickers = gettickerlist(engine)
percs = []
for t in tickers:
    if t.find("ABG")!=-1:
        continue
    df = getconsolidatedcotizacionesforticker(t, engine)
    df["todate"] = df["derivedsourcetimestamp"].apply(dt642date)
    mindate = min(df["todate"].values)
    maxdate = max(df["todate"].values)

    datelist = pandas.date_range(start=mindate, end=maxdate).tolist()

    for i in range(len(datelist)-1):
        sdf = df.loc[df["todate"]==datelist[i]]
        if len(sdf.index)==0:
            continue
        last = sdf["ultimo"][sdf.index.values[len(sdf.index.values)-1]]
        sdf2 = df.loc[df["todate"] == datelist[i+1]]
        if len(sdf2.index)==0:
            continue
        first2 = sdf2["ultimo"][sdf2.index.values[0]]
        max2 = sdf2["ultimo"].max()
        potentialperc = (max2-first2) / first2

        if (first2*1.0499) < last:
            print(t + ": " + str(datelist[i]) + "=" + str(last) + "-" + str(first2) + " potential:" + str(potentialperc))
            y=2 #bingo!
            percs.append(potentialperc)

avg = sum(percs) / len(percs)

y = 0
t = 0
for p in percs:
    if p > 0.025:
        y +=1
        t +=1
    else:
        t+=1



print(str(avg))

print(str(y) + "-" + str(t))

import pandas
from mt5interface.placingorders import *
from model import getaitraderengine
from globalutils import getconsolidatedcotizacionesforticker
import datetime
from datetime import timedelta
import numpy as np

mt5.initialize()

engine = getaitraderengine()
df = getconsolidatedcotizacionesforticker("TEF", engine)
rates = getrates('TEF', mt5.TIMEFRAME_M1, "29-09-2020 11:00", "06-11-2020 19:30")
ratesadj = [[datetime.datetime.fromtimestamp(r[0]),r[1], r[2], r[3], r[4], r[5], r[6], r[7]] for r in rates]

df2 = pandas.DataFrame(ratesadj, columns=["tts","open","high","low",  "close", "tick_volume", "spread", "real_volume"])
df2["datecol"] = df2["tts"].apply(lambda v: v.date())
dates = df2["datecol"].unique()
df2["difhor"] = pandas.Series(dtype=np.int)
df2["derivedsourcetimestamp"] = pandas.Series()
for d in dates:
    mn = df2.loc[df2["datecol"]==d]["tts"].min()
    mx = df2.loc[df2["datecol"]==d]["tts"].max()
    hmn = mn.strftime("%H")
    hmx = mx.strftime("%H")
    if (hmn==str(12)) and hmx == str(20):
        df2.loc[df2["datecol"]==d, "difhor"] = 3
        df2.loc[df2["datecol"]==d, "derivedsourcetimestamp"] = df2["tts"] - timedelta(hours=3)
    if (hmn==str(11)) and hmx == str(19):
        df2.loc[df2["datecol"]==d,"difhor"] = 2
        df2.loc[df2["datecol"] == d, "derivedsourcetimestamp"] = df2["tts"] - timedelta(hours=2)

#ahora escribo
df["mt5price"] = pandas.Series()

for index, row in df.iterrows():
    val = df2.loc[df2["derivedsourcetimestamp"]==row["derivedsourcetimestamp"], "close"]
    try:
        df.loc[df["derivedsourcetimestamp"]==row["derivedsourcetimestamp"],"mt5price"] = val.values[0]
    except:
        pass
df["diff"] = df["ultimo"] - df["mt5price"]
y = 2
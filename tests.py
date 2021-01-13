
from model import getaitraderengine

engine = getaitraderengine()

import MetaTrader5 as mt5
import matplotlib.pyplot as plt
mt5.initialize(login=30383295, password="Pknrp2h8@", server="AdmiralMarkets-Live")

from mt5interface.placingorders import getratesaspandasdataframe

df = getratesaspandasdataframe("UNI2", mt5.TIMEFRAME_H1, "01-09-2020 06:00", "25-11-2020 19:30")

fig, (ax1, ax2, ax3) = plt.subplots(3,1, sharex=True)

ax1.plot(df["tts"], df["close"], linewidth=1)
ax2.plot(df["tts"], df["real_volume"].rolling(3).mean(), linewidth=1)
ax3.plot(df["tts"], df["tick_volume"].rolling(3).mean(), linewidth=1)
plt.show()
y = 2



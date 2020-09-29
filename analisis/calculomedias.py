import pandas as pd
import math
from sqlalchemy import create_engine
from matplotlib import pyplot as plt

def pop(l, val):
    import collections
    d = collections.deque(l)
    d.rotate(1)
    l = list(d)
    l[0] = val
    return l

engine = create_engine("mysql+mysqlconnector://root:dtisat@localhost:3306/aitrader")

ticker = "ACX"

outcome = 0
investment = [0,0]
saldostart = 1000
saldo = saldostart

sql = "SELECT *, STR_TO_DATE(fechatexto,'%d-%m-%Y') as fecha FROM aitrader.cotizaciones_hist_mc where ticker like '" + ticker + "' order by ticker asc, STR_TO_DATE(fechatexto,'%d-%m-%Y') asc"
col = 4
# sql = "select distinct ticker, ultimo, ts from cotizacionesconsolidadas_mc where ticker = '" + ticker + "' order by ts asc"
# col = 1

ana = pd.read_sql(sql, engine)

ana.set_index("fecha", inplace=True)
ana['ultimo'] = ana['valorcierre']
ana['Roll5'] = ana.iloc[:,col].rolling(window=5).mean()
ana['Roll10'] = ana.iloc[:,col].rolling(window=10).mean()
ana['Roll15'] = ana.iloc[:,col].rolling(window=15).mean()
ana['S2_5'] = ana.iloc[:,col].rolling(window=5).var()

ana['S2_15'] = ana.iloc[:,col].rolling(window=15).var()

# max = 2600
# min = 2550

vvcc = ana.loc[:,'ultimo'].tolist()
roll5 = ana.loc[:,'Roll5'].tolist()
roll10 = ana.loc[:,'Roll10'].tolist()
roll15 = ana.loc[:,'Roll15'].tolist()

markers = []
actions = []












# plt.figure(figsize=[15,10])
import matplotlib.gridspec
import matplotlib.dates as mdates
gs = matplotlib.gridspec.GridSpec(2,1,height_ratios=(0.8,0.2))
axs = []
fig = plt.figure(figsize=(15,10))
axs.append(fig.add_subplot(gs[0]))
axs.append(fig.add_subplot(gs[1], sharex = axs[0]))

plt.grid(True)
axs[0].plot(ana['ultimo'].iloc[:],label='valorcierre', linewidth=0.5)
axs[0].plot(ana['Roll5'].iloc[:], label='Roll5', linestyle="--", marker='o', markevery=markers, linewidth=0.5)
axs[0].plot(ana['Roll10'].iloc[:],label='Roll10', linestyle="--", linewidth=0.5)
axs[0].plot(ana['Roll15'].iloc[:],label='Roll15', linestyle="--", linewidth=0.5)
axs[0].set_title("Valores de Cierre y Medias Moviles")
axs[0].legend(loc=1)
axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
axs[0].xaxis.set_major_locator(mdates.DayLocator())






axs[1].plot(ana['S2_5'].iloc[:],label='S2_3', linestyle=":", linewidth=1)
axs[1].set_title("Varianza")
# axy2.plot(ana['S2_15'].iloc[min:max-1],label='S2_15', linestyle=":")
axs[1].legend(loc=1)
fig.suptitle(ticker)

print(saldostart)
print(saldo)
print(investment[1])
print(actions)
plt.show()
y = 2






y = 2



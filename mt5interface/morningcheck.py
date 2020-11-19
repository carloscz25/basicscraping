from  mt5interface.placingorders import *
import mt5interface.placingorders as placingorders
from globalutils import *
import MetaTrader5 as mt5

mt5.initialize()

datefrom = "09-11-2020 17:00"
dateto = "09-11-2020 21:00"

tickersdict = {}
tickers = placingorders.gettickerlist()
for t in tickers:
    df = getratesaspandasdataframe(t, mt5.TIMEFRAME_M1, datefrom, dateto)
    if df.empty==True:
        continue
    lastrate = df["close"].values[len(df["close"].values)-1]
    tickersdict[t] = lastrate

while(True):
    for t in tickers:
        val = mt5.symbol_info(t)
        if val is None:
            continue
        try:
            val2 = tickersdict[t]
            val_ = val.bid
            if (val_ * 1.04999) < val2:
                from globalutils import dobeep
                dobeep()
                print("ALERT: DIPOPP FOR TICKER " + t + " BidPrice = " + str(val.bid) + " LASTSESSIONCLOSE:" + str(tickersdict[t]))
            else:
                # print(t + " last: " + str(val2) + " first:" + str(val_) + " => " + str(val2/val_))
                pass
        except:
            pass
    print("Check compeltado!")
    time.sleep(3)
y = 2

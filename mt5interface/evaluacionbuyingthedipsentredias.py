import MetaTrader5 as mt5
from mt5interface.placingorders import *
import datetime
from datetime import timedelta

mt5.initialize(login=30383295, password="Pknrp2h8@", server="AdmiralMarkets-Live")

tickers = gettickerlist()
fromdate = "31-10-2019"
todate = "10-11-2020"

fdate = datetime.datetime.strptime(fromdate, "%d-%m-%Y")
tdate = datetime.datetime.strptime(todate, "%d-%m-%Y")

currdate = fdate
while(currdate <= tdate):
    print(currdate.strftime("%d-%m-%Y"))
    for t in tickers:
        currdateto = currdate + timedelta(days=1)
        timefrom = currdate.strftime("%d-%m-%Y") + " 13:00"
        timeto = currdateto.strftime("%d-%m-%Y") + " 13:00"

        ratesconv = getratesaspandasdataframe(t, mt5.TIMEFRAME_M1, timefrom,timeto)

        lastrate, firstrate = None, None
        if len(ratesconv) == 0:
            continue

        from globalutils import dt642date
        currday = dt642date(sorted(ratesconv["tts"].unique())[0]).day

        for i, r in ratesconv.iterrows():
            day = dt642date(r["tts"]).day
            if day != currday:
                lastrate = ratesconv["close"][i-1]
                firstrate = ratesconv["close"][i]
                break


        if (firstrate!=None and lastrate!=None) and lastrate > (firstrate * 1.04999):
            fromtime = currdateto.strftime("%d-%m-%Y") + " 06:59"
            totime = currdateto.strftime("%d-%m-%Y") + " 20:31"
            df = ratesconv.loc[ratesconv[""]]
            mx = df["close"].max()
            v = "(" + str((lastrate/firstrate)) + ") " + t + ":" + "LR:" + str(lastrate) + "FR:" + str(firstrate) + " - " + "MX:" + str(mx) + "  " + str(mx/firstrate)
            print(v)
    currdate = currdateto
import MetaTrader5 as mt5
from mt5interface.placingorders import *
import datetime
from datetime import timedelta

mt5.initialize(login=30383295, password="Pknrp2h8@", server="AdmiralMarkets-Live")

tickers = gettickerlist()
fromdate = "01-10-2020"
todate = "31-10-2020"

fdate = datetime.datetime.strptime(fromdate, "%d-%m-%Y")
tdate = datetime.datetime.strptime(todate, "%d-%m-%Y")

currdate = fdate
while(currdate <= tdate):
    print(currdate.strftime("%d-%m-%Y"))
    for t in tickers:
        currdateto = currdate + timedelta(days=1)
        timefrom = currdate.strftime("%d-%m-%Y") + " 13:00"
        timeto = currdateto.strftime("%d-%m-%Y") + " 13:00"

        rates = getrates(t, mt5.TIMEFRAME_M1, timefrom,timeto)
        if (rates==None):
            continue
        ratesconv = []
        for r in rates:
            rc = list(r)
            ratesconv.append(rc)
            rc[0] = datetime.datetime.fromtimestamp(r[0]).strftime("%d-%m-%Y %H:%M")
        #tomando el ultimo valor del dia y el primero del siguiente
        lastrate, firstrate = None, None
        if len(rates) == 0:
            continue
        currday = datetime.datetime.fromtimestamp(rates[0][0]).day
        rates = sorted(rates, key=lambda k: k[0])
        for i in range(len(rates)):
            day = datetime.datetime.fromtimestamp(rates[i][0]).day
            if day != currday:
                lastrate = rates[i-1][1]
                firstrate = rates[i][1]
                break


        if (firstrate!=None and lastrate!=None) and lastrate > (firstrate * 1.04999):
            v = "(" + str((lastrate/firstrate)) + ") " + t + ":" + "LR:" + str(lastrate) + "FR:" + str(firstrate) + " - " + str(ratesconv)
            print(v)
    currdate = currdateto
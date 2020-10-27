from sqlalchemy import create_engine
from model import getaitraderengine
import pandas
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta
from estrategias.bollingerbandsignals.commons import issalesignal, isacquisitionsignal
import math
import numpy as np

engine = getaitraderengine("localhost",3306, "aitrader")

def U(values):
    if (values[1]-values[0])>0:
        return values[1]-values[0]
    else:
        return 0

def D(values):
    if (values[1]-values[0])<0:
        return abs(values[1]-values[0])
    else:
        return 0

def calcSMMs(df, n_period):
    df["SMMAD"] = pandas.Series()
    df["SMMAU"] = pandas.Series()
    counter = 1
    previousSMMU = None
    previousSMMD = None
    for index, row in df.iterrows():
        if not math.isnan(row["U"]) and not math.isnan(row["D"]):
            if previousSMMU == None:
                row["SMMAU"] = row["U"]
            else:
                if counter < n_period:
                    row["SMMAU"] = (((counter-1)*previousSMMU) + row["U"])/counter
                else:
                    row["SMMAU"] = (((n_period - 1) * previousSMMU) + row["U"]) / n_period
            if previousSMMD == None:
                row["SMMAD"] = row["D"]

            else:
                if counter < n_period:
                    row["SMMAD"] = (((counter - 1) * previousSMMD) + row["D"]) / counter
                else:
                    row["SMMAD"] = (((n_period - 1) * previousSMMD) + row["D"]) / n_period
            previousSMMU = row["SMMAU"]
            previousSMMD = row["SMMAD"]
            counter += 1



def dosimulation(ticker, plot=False, dateinterval = ("2010-01-01", "2020-12-31")):


    # sql = "select distinct ticker,str_to_date(fechatexto, \'%d-%m-%Y\') as fecha, valorcierre, split from ( select *, str_to_date(fechatexto, \'%d-%m-%Y\') from cotizaciones_hist_mc ) as st1  where  ticker = '" + ticker + "' order by ticker asc, fecha asc"

    sql = "select * from (select distinct ticker,str_to_date(fechatexto, '%d-%m-%Y') as fecha, valorcierre, split from ( select *, str_to_date(fechatexto, '%d-%m-%Y') from cotizaciones_hist_mc ) as st1  where  ticker = '" + ticker  + "' order by ticker asc, fecha asc) as st2 where fecha between '" + dateinterval[0]  + "' and '" + dateinterval[1] + "'"

    df = pandas.read_sql(sql, engine)
    dfp = df.pivot(index="fecha",columns="ticker", values="valorcierre")
    bollingermultup = 4
    bollingermultdown = 4
    dfp["mean"] = dfp[ticker].rolling(10).mean()
    dfp["var"] = dfp[ticker].rolling(10).var()
    dfp["bollup"] = dfp["mean"]+(bollingermultup*dfp["var"])
    dfp["bolldown"] = dfp["mean"]-(bollingermultdown * dfp["var"])

    dfp["U"] = dfp[ticker].rolling(2).apply(U)
    dfp["D"] = dfp[ticker].rolling(2).apply(D)

    calcSMMs(dfp, 20)

    dfp["RS"] = dfp["SMMAU"] / dfp["SMMAD"]
    dfp["RSI"] = 100 - (100/(1+dfp["RS"]))

    if plot == True:
        fix, ax = plt.subplots(2, sharex=True)
        xvals = dfp.index.values
        tickervals = dfp[ticker].values
        meanvals = dfp["mean"].values
        bollup = dfp["bollup"].values
        bolldown = dfp["bolldown"].values
        ax[0].plot(xvals, tickervals)
        ax[0].plot(xvals,meanvals)
        ax[0].plot(xvals, bollup)
        ax[0].plot(xvals, bolldown)
        rsivals = dfp["RSI"].values
        ax[1].plot(xvals, rsivals)


    prevvaluesn = 5
    prevvalues = []
    acq_signals = []
    sale_signals = []

    counter = -1
    for index, row in dfp.iterrows():
        counter += 1
        val = row[ticker]
        mean = row["mean"]
        bollup = row["bollup"]
        bolldown = row["bolldown"]
        values = [val, mean, bollup, bolldown, index]

        prevvalues.insert(0,values)

        if counter>=11:
            if isacquisitionsignal(prevvalues):
                values.append("AS")
                acq_signals.insert(0, values)
            if issalesignal(prevvalues):
                values.append("SS")
                sale_signals.insert(0, values)

        if (len(prevvalues)>prevvaluesn):
            prevvalues.pop(5)

    allsignals = acq_signals + sale_signals
    allsignals = sorted(allsignals, key=lambda v: v[4])

    if plot == True:
        for v in acq_signals:
            ax[0].scatter(v[4], v[0], c="#FFFF00", s=50)
        for v in sale_signals:
            ax[0].scatter(v[4], v[0], c="#EE82EE", s=50)

    for s in allsignals:
        pass
        # print(s[5] + ":" + str(s[0]) + " " + s[4].strftime("%d/%m/%Y"))

    #accounting operations
    #buy on first AS and sell on first SS
    ops = []
    inoperation = False
    for s in allsignals:
        if (s[5] == "AS") and inoperation == False:
            op = [s[0], None, None, s[4], None]
            inoperation = True
        if (s[5] == "SS") and inoperation == True:
            op[1] = s[0]
            profit = (op[1] - op[0])/op[0]
            if profit < 0 and profit < -0.03:
                profit = -0.03
            op = [op[0], op[1], profit, op[3], s[4]]
            ops.append(op)
            inoperation = False
            op = None


    cumprofit = 0
    positiveopscount = 0
    negativeopscount = 0
    for i,o in enumerate(ops):
        # print(str(i) + ":" + str(o[0]) + "(" + o[3].strftime("%d/%m/%Y") + ")/" + str(o[1]) + "(" + o[4].strftime("%d/%m/%Y") + ") = " + str(o[2]))
        cumprofit += o[2]
        if o[2] >=0:
            positiveopscount +=1
        else:
            negativeopscount +=1

    print(ticker + ": " + str(cumprofit) + "   (+)=" + str(positiveopscount) + "  " + "(-)" + str(negativeopscount))

    if plot == True:
        plt.show()

    for op in ops:
        datefrom = op[3]
        dateto = op[4]
        d = datefrom
        while(d <= dateto):
            dfnumops["N"][np.datetime64(d)] += 1
            d += timedelta(days=1)

    return (cumprofit, positiveopscount, negativeopscount)

datefrom = "2020-01-01"
dateto = "2020-07-31"
daterange = pandas.date_range(datetime.datetime.strptime(datefrom, "%Y-%m-%d"),datetime.datetime.strptime(dateto, "%Y-%m-%d"), freq='d')
dfnumops = pandas.DataFrame(index=daterange)
dfnumops["N"] = 0

sql = "select * from tickers_mc"
df = pandas.read_sql(sql, engine)

cumposops = 0
cumnegops = 0
cumprofit = 0

for index, row in df.iterrows():
    ticker = row["ticker"]
    try:
        results = dosimulation(ticker, plot=False, dateinterval=(datefrom,dateto))
        cumprofit += results[0]
        cumposops += results[1]
        cumnegops += results[2]
    except Exception as e:
        print(ticker + " : " + str(e))

print("CumProfit: " + str(cumprofit) + "   (total+)=" + str(cumposops) + "    (total-)=" + str(cumnegops))
print("PercPos:" + str((cumposops/(cumposops+cumnegops))*100)+"%")
print("PercNeg:" + str((cumnegops/(cumposops+cumnegops))*100)+"%")
print("NumPosOps:" + str(cumposops))
print("NumNegOps:" + str(cumnegops))
print("TotalOps:" + str(cumposops + cumnegops))
print("MaxNumberOfSimultaneousOps: " + str(max(dfnumops["N"].values)))
plt.show()
y=2

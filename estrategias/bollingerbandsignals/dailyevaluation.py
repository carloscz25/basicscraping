from model import getaitraderengine
import pandas
import datetime
from datetime import timedelta
from estrategias.bollingerbandsignals.commons import isacquisitionsignal, issalesignal
from matplotlib import pyplot as plt

engine = getaitraderengine()

def getdefaultfordates():
    todate = datetime.datetime.now().strftime("%Y-%m-%d")
    fromdate = (datetime.datetime.now()-timedelta(days=365)).strftime("%Y-%m-%d")
    return (fromdate, todate)

def SMMA_U(x, *v):
    y = 2

def SMMA_D(values):
    y = 2

def discoversignals(ticker, fordates=getdefaultfordates(), dateforsignalmonitoring=datetime.datetime.now(), plot=True):
    """fordates : tuple => (Y%-m%-%d,%Y-%m-%d)"""
    sql = "select distinct * from (select distinct ticker,str_to_date(fechatexto, '%d-%m-%Y') as fecha, valorcierre, split from ( select *, str_to_date(fechatexto, '%d-%m-%Y') from cotizaciones_hist_mc ) as st1  where  ticker = '" + ticker + "' order by ticker asc, fecha asc) as st2 where fecha between '" + \
          fordates[0] + "' and '" + fordates[1] + "'"
    df = pandas.read_sql(sql, engine)
    dfp = df.pivot(index="fecha", columns="ticker", values="valorcierre")
    if (len(dfp)==0):
        return
    bollingermultup = 4
    bollingermultdown = 4
    dfp["mean"] = dfp[ticker].rolling(10).mean()
    dfp["var"] = dfp[ticker].rolling(10).var()
    dfp["bollup"] = dfp["mean"] + (bollingermultup * dfp["var"])
    dfp["bolldown"] = dfp["mean"] - (bollingermultdown * dfp["var"])


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


        prevvalues.insert(0, values)

        if counter >= 11:
            if isacquisitionsignal(prevvalues):
                values.append("AS")
                acq_signals.insert(0, values)
            if issalesignal(prevvalues):
                values.append("SS")
                sale_signals.insert(0, values)

        if (len(prevvalues) > prevvaluesn):
            prevvalues.pop(5)

    allsignals = acq_signals + sale_signals
    allsignals = sorted(allsignals, key=lambda v: v[4])


    signals = ""
    for s in allsignals:
        # print(s[5] + ":" + str(s[0]) + " " + s[4].strftime("%d/%m/%Y"))
        signaldatetime = s[4]
        #if the signal is between today and the last 5 days
        if (dateforsignalmonitoring.date()-timedelta(days=3)) <= s[4] <= dateforsignalmonitoring.date():
            signals += s[5] + ":" + str(s[0]) + " " + s[4].strftime("%d/%m/%Y")
    if (signals != ""):
        print(ticker + " :    " + signals)
        #generating chart and saving it
        plotonly_lastNdays = 70
        if plot == True:
            _df = dfp.tail(plotonly_lastNdays)
            firstdate = _df.index.tolist()[0]
            _df.plot(y=[ticker, "mean", "bollup", "bolldown"], figsize=(24,8))
            for v in acq_signals:
                if v[4] >= firstdate:
                    plt.scatter(v[4], v[0], c="#FFFF00", s=100)

            for v in sale_signals:
                # plt.scatter(v[4], v[0], c="#EE82EE", s=50)
                if v[4] >= firstdate:
                    plt.scatter(v[4], v[0], c="#EE82EE", s=100)
                pass
            plt.savefig("charts/" + ticker + ".jpg")

sql = "select * from tickers_mc"
df = pandas.read_sql(sql, engine)

for index, row in df.iterrows():
    ticker = row["ticker"]
    discoversignals(ticker)

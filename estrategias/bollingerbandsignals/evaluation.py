from sqlalchemy import create_engine
from model import getaitraderengine
import pandas
import matplotlib.pyplot as plt
import datetime

engine = getaitraderengine("localhost",3306, "aitrader")

def isacquisitionsignal(values):
    curr = values[0]
    prev_1 = values[1]
    prev_2 = values[2]
    #current value is greater than BollDown
    #and current value is lower than mean and lower than BollUp
    #and current BollDown is greater than previous value
    isas =  ((curr[0]>curr[3] and curr[0] < curr[1] and curr[0] < curr[2]) and prev_1[0]<curr[3])
    return isas

def issalesignal(values):
    curr = values[0]
    prev_1 = values[1]
    prev_2 = values[2]
    # current value is lower than BollUp
    # and current value is bigger than mean and bigger than BollDown
    # and current BollUp is lower than previous value
    isas = ((curr[0] < curr[2] and curr[0] > curr[1] and curr[0] > curr[3]) and prev_1[0] > curr[2])
    return isas



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

    if plot == True:
        dfp.plot(y=[ticker,"mean","bollup","bolldown"])

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
            plt.scatter(v[4], v[0], c="#FFFF00", s=50)
        for v in sale_signals:
            plt.scatter(v[4], v[0], c="#EE82EE", s=50)

    # for s in allsignals:
    #     print(s[5] + ":" + str(s[0]) + " " + s[4].strftime("%d/%m/%Y"))

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
    return (cumprofit, positiveopscount, negativeopscount)
    # plt.show()

sql = "select * from tickers_mc"
df = pandas.read_sql(sql, engine)
cumposops = 0
cumnegops = 0
cumprofit = 0
for index, row in df.iterrows():
    ticker = row["ticker"]
    try:
        results = dosimulation(ticker, dateinterval=("2018-01-01","2018-12-31"))
        cumprofit += results[0]
        cumposops += results[1]
        cumnegops += results[2]
    except Exception as e:
        print(ticker + " : " +  str(e))

print("CumProfit: " + str(cumprofit) + "   (total+)=" + str(cumposops) + "    (total-)=" + str(cumnegops))
print("PercPos:" + str((cumposops/(cumposops+cumnegops))*100)+"%")
print("PercNeg:" + str((cumnegops/(cumposops+cumnegops))*100)+"%")
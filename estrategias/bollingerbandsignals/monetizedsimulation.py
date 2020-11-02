from sqlalchemy import create_engine
from model import getaitraderengine
import pandas
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta
from estrategias.bollingerbandsignals.commons import issalesignal, isacquisitionsignal
import math
import numpy as np
from estrategias.simulationmodel import Portfolio, Operation

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

    df["SMMAD"] = pandas.Series(np.float)
    df["SMMAU"] = pandas.Series(np.float)
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

def determineinvestmentamount(assetprice, desiredinvestmentamount):
    num = desiredinvestmentamount // assetprice
    module = desiredinvestmentamount % assetprice
    if (num < 0):
        return assetprice
    elif(module == 0):
        return num
    else:
        return assetprice * (num+1)

portfolio = Portfolio(liquidassets=20000, growassetsautomatically=True)
investmentamount = 400


def dosimulation(ticker, plot=False, dateinterval = ("2010-01-01", "2020-12-31")):

    # sql = "select distinct ticker,str_to_date(fechatexto, \'%d-%m-%Y\') as fecha, valorcierre, split from ( select *, str_to_date(fechatexto, \'%d-%m-%Y\') from cotizaciones_hist_mc ) as st1  where  ticker = '" + ticker + "' order by ticker asc, fecha asc"

    sql = "select * from (select distinct ticker,str_to_date(fechatexto, '%d-%m-%Y') as fecha, valorcierre, split from ( select *, str_to_date(fechatexto, '%d-%m-%Y') from cotizaciones_hist_mc ) as st1  where  ticker = '" + ticker  + "' order by ticker asc, fecha asc) as st2 where fecha between '" + dateinterval[0]  + "' and '" + dateinterval[1] + "'"

    df = pandas.read_sql(sql, engine)
    dfp = df.pivot(index="fecha",columns="ticker", values="valorcierre")
    bollingermultup = 2
    bollingermultdown = 2
    windowsize = 20
    dfp["mean"] = dfp[ticker].rolling(windowsize).mean()
    dfp["var"] = dfp[ticker].rolling(windowsize).std()
    dfp["bollup"] = dfp["mean"]+(bollingermultup*dfp["var"])
    dfp["bolldown"] = dfp["mean"]-(bollingermultdown * dfp["var"])

    # dfp["U"] = dfp[ticker].rolling(2).apply(U)
    # dfp["D"] = dfp[ticker].rolling(2).apply(D)
    #
    # calcSMMs(dfp, 20)
    #
    # dfp["RS"] = dfp["SMMAU"] / dfp["SMMAD"]
    # dfp["RSI"] = 100 - (100/(1+dfp["RS"]))

    prevvaluesn = 5
    prevvalues = []
    acq_signals = []
    sale_signals = []

    counter = -1
    op = None
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
                if not portfolio.isholdingoperationforticker(ticker):
                    price = prevvalues[0][0]
                    bdate = prevvalues[0][4]
                    op = portfolio.dobuyingoperation(ticker, determineinvestmentamount(price, investmentamount) / price, price, 1, bdate)
            if issalesignal(prevvalues):
                price = prevvalues[0][0]
                cdate = prevvalues[0][4]
                if op != None:
                    op.closeoperation(price, cdate, 1, portfolio)
                    op = None

        if (len(prevvalues)>prevvaluesn):
            prevvalues.pop(5)

    portfolio.operationvalue_lastsimulationperiod[ticker] = values[0]

    return None


datefrom = "2020-01-01"
dateto = "2020-12-31"


sql = "select * from tickers_mc"
df = pandas.read_sql(sql, engine)

cumposops = 0
cumnegops = 0
cumprofit = 0

for index, row in df.iterrows():
    ticker = row["ticker"]
    try:
        dosimulation(ticker, plot=False, dateinterval=(datefrom,dateto))
        print("Incorporando " + ticker + " a simulacion!")
    except BaseException as e:
       print(ticker + " : " + str(e))

print(portfolio.positiveVsNegativeHistoricOps())


print("LiqAssets: " + str(portfolio.liquidassets))
print("TotalValueEndPeriod:" + str(portfolio.totalvaluelastsimulationperiod()))
print("FinancialExp:" + str(portfolio.financialexpenses))
print("GainsInPeriod:" + str(portfolio.gainsinperiod))
print("LossesInPeriod:" + str(portfolio.lossesinperiod))


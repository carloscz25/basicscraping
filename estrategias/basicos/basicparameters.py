from model import getaitraderengine
import pandas
import math

engine = getaitraderengine()

sql = "select * from tickers_mc"
tickersdf = pandas.read_sql(sql, engine)

dicttickers = {}
for index, row in tickersdf.iterrows():
    ticker = row["ticker"]

    sql = "select * from cotizaciones_mc where ticker = '{}'".format(ticker)
    df = pandas.read_sql(sql, engine)
    std = math.sqrt(df.loc[df["ticker"]==ticker, 'ultimo'].var())
    mean = df.loc[df["ticker"]==ticker, 'ultimo'].mean()
    nombre = df["nombre"].values[0]
    dictticker = {}
    dicttickers[ticker] = dictticker
    dictticker["nombre"] = nombre
    dictticker["mean"] = mean
    dictticker["std"] = std
    dictticker["volatility"] = std/mean

counter = 0
for i in sorted(dicttickers.keys(),key=lambda k: dicttickers[k]["volatility"], reverse=True):
    print(i + ":" + str(dicttickers[i]))
    counter += 1
    if counter == 30:
        break
y = 2
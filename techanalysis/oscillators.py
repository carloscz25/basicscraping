import pandas
import numpy

def getrsi(prices, periodnumber):
    df = pandas.DataFrame()
    series = pandas.Series(prices)
    df["price"] = series
    df["rsi"] = pandas.Series()
    df["avgpos"] = pandas.Series()
    df["avgneg"] = pandas.Series()
    for i in range(1, (periodnumber+1)):
        df["+" + str(i)] = (df["price"]-df["price"].shift(i))/df["price"].shift(i)
        df["+" + str(i)].loc[df["+" + str(i)]<0] = 0
        df["-" + str(i)] = (df["price"]-df["price"].shift(i))/df["price"].shift(i)
        df["-" + str(i)].loc[df["+" + str(i)] > 0] = 0
    for index, row in df.iterrows():
        avgpos, avgneg = 0, 0
        for j in range(1, (periodnumber+1)):
            avgpos += row["+" + str(j)]
            avgneg += row["-" + str(j)]
        avgneg = abs(avgneg)
        avgpos = avgpos / periodnumber
        avgneg = avgneg / periodnumber
        df["avgpos"][index] = avgpos
        df["avgneg"][index] = avgneg
        df["rsi"][index] = 100-(100/(1+(avgpos/avgneg)))

    return df["rsi"].values





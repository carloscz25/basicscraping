import pandas
import numpy

def sma(prices, period):
    sma = numpy.full(len(prices), None)
    for i in range(period,len(prices)):
        sma[i] = sum(prices[i-period:i])/period
    return sma

def macd(prices, shortmmperiod, largemmperiod, signalmmperiod):
    shortmm = numpy.full(len(prices), None) #create array of Nones. np.empty returned arbitrary zero like data
    largemm = numpy.full(len(prices), None)
    #1.Calculation of the shortmm
    shortmm = ema(prices, shortmmperiod)
    largemm = ema(prices, largemmperiod)
    #2.Calculatin the macd line by substracting the two ema's
    macdline = numpy.subtract(shortmm[largemmperiod:], largemm[largemmperiod:])
    #3.Calculating the ema over the macdline
    signalline =ema(macdline, signalmmperiod)

    diff = numpy.subtract(signalline[signalmmperiod:], macdline[signalmmperiod:])

    #preparing result: adjusting arrays
    macdline = numpy.concatenate([numpy.full(largemmperiod, None), macdline])
    signalline = numpy.concatenate([numpy.full(signalmmperiod, None),numpy.full(largemmperiod, None),signalline[signalmmperiod:]])
    diff = numpy.concatenate([numpy.full(signalmmperiod, None), numpy.full(largemmperiod, None),diff])

    return macdline, signalline, diff






def ema(prices, period, smoothingfactor=2):
    ema = numpy.full(len(prices), None)

    #1.calculate simple moving average as the first ema value
    sma = sum(prices[0:period])/period
    #2.calculate weighting factor
    wf = smoothingfactor / (period + 1)
    #3.calculate the ema based on the ema of yesterday, taking the sma value as the first ema value
    for i in range(period,len(prices)):
        if i==(period):
            ema[i] = sma
        else:
            ema[i] = (prices[i]*wf) + (ema[i-1]*(1-wf))

    return ema



def rsi(prices, periodnumber):
    df = pandas.DataFrame()
    series = pandas.Series(prices)
    df["price"] = series
    df["rsi"] = pandas.Series()
    df["avgpos"] = pandas.Series()
    df["avgneg"] = pandas.Series()
    for i in range(1, (periodnumber+1)):
        df["+" + str(i)] = (df["price"].shift(i-1)-df["price"].shift(i))/df["price"].shift(i)
        df["+" + str(i)].loc[df["+" + str(i)]<0] = 0
        df["-" + str(i)] = (df["price"].shift(i-1)-df["price"].shift(i))/df["price"].shift(i)
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





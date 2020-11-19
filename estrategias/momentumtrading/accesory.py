from mt5interface.placingorders import gettickerlist, getratesaspandasdataframe
from datetime import timedelta
import MetaTrader5 as mt5
import datetime
import estrategias.momentumtrading.parameters as pams


"""
Functions for mesuring performance: Understanding performance for the time being only the difference 
between the close prices of first and last day of the period evaluated. 
IMPROVEMENTS: Incorporate other factors for performance index ponderation such as overall variance (the lower the
better). Moving Variance weekly is at first glance the best approach. Then average all variances. The lowers 
go in.
"""

def getbestperformingtickersforstageW(datereference):
    """Returns a tuple (list, dict) containing the list of the 5 best tickers and a dict with
    its profits along the period"""
    return __getbestperformingtickersforstageN(datereference,"W")
def getbestperformingtickersforstage2W(datereference):
    """Returns a tuple (list, dict) containing the list of the 5 best tickers and a dict with
        its profits along the period"""
    return __getbestperformingtickersforstageN(datereference,"2W")
def getbestperformingtickersforstageM(datereference):
    """Returns a tuple (list, dict) containing the list of the 5 best tickers and a dict with
        its profits along the period"""
    return __getbestperformingtickersforstageN(datereference,"M")
def getbestperformingtickersforstageQ(datereference):
    """Returns a tuple (list, dict) containing the list of the 5 best tickers and a dict with
        its profits along the period"""
    return __getbestperformingtickersforstageN(datereference,"Q")

def __getbestperformingtickersforstageN(datereference, N):
    ndays = -1
    daysdict = {"Q":90,"M":30,"2W":15,"W":7}
    tickers = gettickerlist()
    performancedict = {}
    dateto = datetime.datetime.strptime(datereference, pams.datetimeformatstring)
    datefrom = dateto + timedelta(days=-daysdict[N])

    for t in tickers:
        datefromstr = datefrom.strftime(pams.datetimeformatstring)
        datetostr = dateto.strftime(pams.datetimeformatstring)
        rates = getratesaspandasdataframe(t, mt5.TIMEFRAME_D1, datefromstr + " 00:00", datetostr + " 20:30")
        firstindex, lastindex = -1, -1
        try:
            datefromstr = datefrom.strftime(pams.reverse_datetimeformatstring)
            datetostr = dateto.strftime(pams.reverse_datetimeformatstring)
            firstindex = rates[rates["date"].apply(lambda d: d.strftime(pams.reverse_datetimeformatstring)) == datefromstr]["close"].index[0]
            lastindex = rates[rates["date"].apply(lambda d: d.strftime(pams.reverse_datetimeformatstring)) == datetostr]["close"].index[0]
            first = rates[rates["date"].apply(lambda d: d.strftime(pams.reverse_datetimeformatstring)) == datefromstr]["close"][firstindex]
            last = rates[rates["date"].apply(lambda d: d.strftime(pams.reverse_datetimeformatstring)) == datetostr]["close"][lastindex]
            profit = (last - first) / first
            performancedict[t] = profit
        except:
            print("Information incorrect for ticker " + t)

    res = sorted(performancedict, key=lambda k: performancedict[k], reverse=True)
    res =  res[0:4]
    performancedict = {r:performancedict[r] for r in res}
    return res, performancedict

def process_classification_of_tickers_in_stages():
    """this function adjusts the classification of tickers at each stage by updating the dicts
    in the parameters file : dict_tickercounterforstageN. At the same time it returns a dict
    with the tickers that must be taken off each of the stages. The function already puts off
    the tickers that must leave each stage"""
    dict_off_tickers = {"W":[], "2W":[], "M":[], "Q":[]}

    stages = ["W","2W","M","Q"]
    dicts = [pams.dict_tickercounterforstage_W, pams.dict_tickercounterforstage_2W, pams.dict_tickercounterforstage_M,pams.dict_tickercounterforstage_Q]
    for i, s in zip(stages):
        tickersN, profitsN = __getbestperformingtickersforstageN("18-11-2020", s)
        for t in tickersN:
            if t in dicts[i].keys():
                dicts[i][t] = dicts[0][t] + 1
            else:
                dicts[i][t] = 1
        for t in dicts[i].keys():
            if not (t in tickersN):
                dict_off_tickers[s].append(t)
                del(dicts[i][t])
    return dict_off_tickers



    if __name__ == "__main__":
    mt5.initialize()

    tickersW, profitsW = getbestperformingtickersforstageW("18-11-2020")
    tickers2W, profits2W = getbestperformingtickersforstage2W("18-11-2020")
    tickersM, profitsM = getbestperformingtickersforstageM("18-11-2020")
    tickersQ, profitsQ = getbestperformingtickersforstageQ("18-11-2020")
    tickers = list(set(tickersW + tickers2W + tickersM + tickersQ)) #uniques

    y = 2

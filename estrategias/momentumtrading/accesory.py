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
        if len(rates)==0:
            continue
        firstindex, lastindex = -1, -1
        try:
            datefromstr = datefrom.strftime(pams.reverse_datetimeformatstring)
            datetostr = dateto.strftime(pams.reverse_datetimeformatstring)
            #obteniendo firstindex: si no es dia bursatil avanzo un dia hasta que lo encuentre
            while(firstindex==-1):
                try:
                    firstindex = rates[rates["date"].apply(lambda d: d.strftime(pams.reverse_datetimeformatstring)) == datefromstr]["close"].index[0]
                except BaseException as be:
                    datefrom = datefrom + timedelta(days=1)
                    datefromstr = datefrom.strftime(pams.reverse_datetimeformatstring)
            # obteniendo lastindex: si no es dia bursatil retrocedo un dia hasta que lo encuentre
            while (lastindex == -1):
                try:
                    lastindex = rates[rates["date"].apply(lambda d: d.strftime(pams.reverse_datetimeformatstring)) == datetostr]["close"].index[0]
                except BaseException as be:
                    dateto = dateto + timedelta(days=-1)
                    datetostr = dateto.strftime(pams.reverse_datetimeformatstring)



            first = rates[rates["date"].apply(lambda d: d.strftime(pams.reverse_datetimeformatstring)) == datefromstr]["close"][firstindex]
            last = rates[rates["date"].apply(lambda d: d.strftime(pams.reverse_datetimeformatstring)) == datetostr]["close"][lastindex]
            profit = (last - first) / first
            performancedict[t] = profit
        except BaseException as be:
            print("Information incorrect for ticker " + t)

    res = sorted(performancedict, key=lambda k: performancedict[k], reverse=True)
    #put in all positives
    res2 =  [p for p in performancedict if performancedict[p] > 0]
    performancedict = {r:performancedict[r] for r in res2}
    return res2, performancedict

def process_classification_of_tickers_in_stages(datereference, tickersN):
    """
    datereference: Date as string, from which make all calculations
    this function adjusts the classification of tickers at each stage by updating the dicts
    in the parameters file : dict_tickercounterforstageN. At the same time it returns a dict
    with the tickers that must be taken off each of the stages. The function already puts off
    the tickers that must leave each stage"""
    dict_off_tickers = {"W":[], "2W":[], "M":[], "Q":[]}
    dict_in_tickers = {"W": [], "2W": [], "M": [], "Q": []}

    stages = ["W","2W","M","Q"]
    dicts = [pams.dict_tickercounterforstage_W, pams.dict_tickercounterforstage_2W, pams.dict_tickercounterforstage_M,pams.dict_tickercounterforstage_Q]


    for t in tickersN:
        #if the ticker is at a higgher stage store the dict index in tindict_index
        tindict_index = -1
        #check if the ticker exists already in any of the dicts
        for i, d in enumerate(dicts):
            if t in d.keys():
                tindict_index = i
        #end check
        #if it doesn't do the process at first dict: check if exists for adding or if not
        #include with value 1
        if tindict_index == -1:
            if t in dicts[0].keys():
                dicts[0][t] = dicts[0][t] + 1
            else:
                dicts[0][t] = 1
                dict_in_tickers[stages[0]].append(t)
        else:
            if tindict_index > 1:
                if dicts[tindict_index][t] != -1:
                    dicts[tindict_index][t] = dicts[tindict_index][t] + 1
                else:
                    dicts[tindict_index][t] = 1
                    dict_in_tickers[stages[tindict_index]].append(t)
            else:
                dicts[tindict_index][t] = dicts[tindict_index][t] + 1

    #adjust: if the ticker is already present in any of the dicts for at least two periods
    #delete it from that index and append it one stage above
    for i, d in enumerate(dicts):
        dkeys = list(d.keys())
        for t in dkeys:
            if d[t] == 2:
                if i < (len(dicts)-1):
                    dicts[i+1][t] = 1
                    dict_in_tickers[stages[i+1]].append(t)
                    del(d[t])
    #end adjust

    #adjust: for dicts below stage 2 (below M) if the ticker is not among the bestperforming delete it
    #if it is on 2 or above (M or Q) then if it is not among the best performing give it one chance setting
    #its value to -1. If for two periods it is not among the BP, then remove
    keys = tickersN
    for i in range(4):
        d = dicts[i]
        if i <2:
            dictsi = list(dicts[i])
            for t in dictsi:
                if not t in keys:
                    del(dicts[i][t])
                    dict_off_tickers[stages[i]].append(t)
        else:
            dictsi = list(dicts[i])
            for t in dictsi:
                if not t in keys:
                    if dicts[i][t] != -1:
                        dicts[i][t] = -1
                    else:
                        del(dicts[i][t])
                        dict_off_tickers[stages[i]].append(t)
    #end adjust
    return dict_off_tickers, dict_in_tickers



def process_classification_of_tickers_in_stages_OLD(datereference):
    """
    datereference: Date as string, from which make all calculations
    this function adjusts the classification of tickers at each stage by updating the dicts
    in the parameters file : dict_tickercounterforstageN. At the same time it returns a dict
    with the tickers that must be taken off each of the stages. The function already puts off
    the tickers that must leave each stage"""
    dict_off_tickers = {"W":[], "2W":[], "M":[], "Q":[]}

    stages = ["W","2W","M","Q"]
    dicts = [pams.dict_tickercounterforstage_W, pams.dict_tickercounterforstage_2W, pams.dict_tickercounterforstage_M,pams.dict_tickercounterforstage_Q]
    for i, s in enumerate(stages):
        tickersN, profitsN = __getbestperformingtickersforstageN(datereference, s)
        for t in tickersN:
            if t in dicts[i].keys():
                dicts[i][t] = dicts[i][t] + 1
            else:
                dicts[i][t] = 1
        keys = list(dicts[i].keys())
        for t in keys:
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

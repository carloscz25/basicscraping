import MetaTrader5 as mt5
import datetime

def getrequest_placeorderbuyatexchangeexecution(symbol, volumeinlots):
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volumeinlots,
        "type": mt5.ORDER_TYPE_BUY,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    return request

def getrequest_placeorderbuypendingexecution(symbol, volumeinlots, price):
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volumeinlots,
        "price": price,
        "stoplimit": price,
        # "sl": None,
        # "tp": None,
        "type": mt5.ORDER_TYPE_BUY_LIMIT,
        "type_filling": mt5.ORDER_FILLING_FOK,
        "type_time": mt5.ORDER_TIME_DAY,
        # "expiration": None
    }
    return request

def getrequest_cancelbuypendingexecution(orderid):
    request = {
        "action": mt5.TRADE_ACTION_REMOVE,
        "order": orderid
    }
    return request

def getrates(symbolstr, timeframe, datefrom, dateto):
    """

    :param symbolstr: str
    :param timeframe:
    :param datefrom:  str "%d-%m-%Y %H:%M"
    :param dateto: str "%d-%m-%Y %H:%M"
    :return:
    """
    dfrom = datetime.datetime.strptime(datefrom, "%d-%m-%Y %H:%M")
    dto = datetime.datetime.strptime(dateto, "%d-%m-%Y %H:%M")
    rates = mt5.copy_rates_range(symbolstr, timeframe, dfrom, dto)
    if rates == None:
        return None
    ratesadj = [[datetime.datetime.fromtimestamp(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7],datetime.datetime.fromtimestamp(r[0]).date()] for r in rates]
    return ratesadj

def getratesaspandasdataframe(symbolstr, timeframe, datefrom, dateto):
    import pandas
    rates = getrates(symbolstr, timeframe, datefrom, dateto)
    df = pandas.DataFrame(rates, columns=["tts", "open", "high", "low", "close", "tick_volume", "spread", "real_volume", "date"])

    return df

def gettickerlist():
    return  ["A3M","ACS","ACX","AENA","ALB",
              "ALMSA","ANA","APPS","BBVA","BKIA",
              "BKT","CABK","CAF","CLNX","COL",
              "DIA1","DOM1","EBRO","EDR1","EKT1",
              "ELE","ENC","ENG","FAE","FCC",
              "FDR","FER","GAS","GCO","GEST",
              "GRF","HOME","IBE","IDR","ITX",
              "LBK","LOG","MAP","MAS","MEL",
              "MRL","NHH","OHL","PHMA","PSG",
              "REE","REP","SAB2","SANES","SCYR",
              "TEF","TL5","TLGO","TRE","TUB",
              "UNI2","VID","VIS","ZOT"]
from estrategias.simulationmodel import *
from estrategias.momentumtrading.accesory import __getbestperformingtickersforstageN, process_classification_of_tickers_in_stages
import  estrategias.momentumtrading.parameters as pams
from datetime import timedelta
import MetaTrader5 as mt5

mt5.initialize()

datestart = "03-01-2020"

dateend = "31-12-2020"
porfolio = Portfolio()
porfolio.liquidassets = 10000

currdate = datestart
step = 0
while(currdate != dateend):
    tickersN, profitsN = __getbestperformingtickersforstageN(currdate, "W")
    offs, ins = process_classification_of_tickers_in_stages(currdate, tickersN)
    #Logging
    print("")
    print("Step {} : {}".format(step, currdate))
    print("BestPerforming : " + str(tickersN))
    print( "Offs : " + str(offs))
    print("Ins : " + str(ins))
    print("W" + str(pams.dict_tickercounterforstage_W))
    print("2W" + str(pams.dict_tickercounterforstage_2W))
    print("M" + str(pams.dict_tickercounterforstage_M))
    print("Q" + str(pams.dict_tickercounterforstage_Q))
    #End Logging
    currdate = (datetime.datetime.strptime(currdate, pams.datetimeformatstring) + timedelta(days=7)).strftime(pams.datetimeformatstring)
    step += 1
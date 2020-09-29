import os
from pathlib import Path

import sys
#comment if running on windows
sys.path.append("/home/carloscz25_gmail_com/aitrader/basicscraping")
import defaults
sys.path.pop(0)
print(sys.path)

from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine
from tickermanagement.utils import gettickersdictionary, INFOBOLSA, BOLSADEMADRID, BSMARKETS



import threading
from globalutils import isopentime, isopentimefordataconsolidation, isopentimefortickermanagement,logexception2mail,logmessage2mail
from globalutils import mthprint


import datetime, time
import sys



#dictionary of errors
errors = []



def infobolsa(engine):
    from extracciondiaria.infobolsa import doimportinfobolsa
    contador = 1
    while(True):
        if (isopentime(datetime.datetime.now())):
            try:
                doimportinfobolsa(engine, contador)
                mthprint("INFOBOLSA: Iteracion " + str(contador) + " exitosa " + str(datetime.datetime.now()))
                contador = contador + 1
            except BaseException as e:
                import traceback
                stacktrace = traceback.format_exc()
                title = str(e)
                logexception2mail(stacktrace, title)
                errors.append({"fatal":"No","stacktrace":stacktrace, "title":title})


        else:
            mthprint("INFOBOLSA: Fuera de horario")
        time.sleep(120)

def bolsademadrid(engine):
    from extracciondiaria.bolsademadrid import doimportbolsademadrid
    contador = 1
    while(True):
        if (isopentime(datetime.datetime.now())):
            try:
                doimportbolsademadrid(engine, contador)
                mthprint("BOLSADEMADRID: Iteracion " + str(contador) + " exitosa")
                contador = contador + 1
            except BaseException as e:
                import traceback
                logexception2mail(traceback.format_exc(), e)
        else:
            mthprint("BOLSADEMADRID: Fuera de horario")
        time.sleep(120)

def bsmarkets(engine):
    from extracciondiaria.bsmarkets import doimportbsmarkets
    contador = 1
    while (True):
        if (isopentime(datetime.datetime.now())):
            try:
                doimportbsmarkets(engine, contador)
                mthprint("BSMARKETS: Iteracion " + str(contador) + " exitosa")
                contador = contador + 1
            except BaseException as e:
                import traceback
                logexception2mail(traceback.format_exc(), e)

        else:
            mthprint("BSMARKETS: Fuera de horario")
        time.sleep(120)

def dataconsolidation(engine):
    from dataconsolidation.consolidation import consolidatedata
    while(True):
        if (isopentimefortickermanagement(datetime.datetime.now())):
            from tickermanagement.bsmarkets import checktickers_bsmarkets
            from tickermanagement.bolsademadrid import checktickers_bolsademadrid
            try:
                # checktickers_bsmarkets(engine)
                # checktickers_bolsademadrid(engine)
                pass
            except BaseException as e:
                mthprint("Exception at TickerManagement: " + str(e))
                import traceback
                logexception2mail(traceback.format_exc(), e)
                pass
            time.sleep(300)
            pass
        elif (isopentimefordataconsolidation(datetime.datetime.now())):
            try:
                consolidatedata(engine)
                mthprint("DATACONSOLIDATION: Data consolidation run successfully")
            except BaseException as e:
                import traceback
                logexception2mail(traceback.format_exc(), e)
            time.sleep(15)
        else:
            mthprint("DATACONSOLIDATION: Fuera de horario")
            time.sleep(60)

    consolidatedata(engine)


from model import getaitraderengine
engineinfobolsa = getaitraderengine()
enginebsmarkets = getaitraderengine()
enginebolsademadrid = getaitraderengine()
enginedataconsolidation = getaitraderengine()



#loading tickers dictionaries for the different sources
gettickersdictionary(INFOBOLSA, engineinfobolsa)
gettickersdictionary(BOLSADEMADRID, enginebolsademadrid)
gettickersdictionary(BSMARKETS, enginebsmarkets)






th1 = threading.Thread(None, infobolsa, args=([engineinfobolsa]))
th2 = threading.Thread(None, bolsademadrid, args=([enginebolsademadrid]))
th3 = threading.Thread(None, bsmarkets, args=([enginebsmarkets]))
th4 = threading.Thread(None, dataconsolidation, args=([enginedataconsolidation]))


print("pasa modulo:" + __name__)
if (__name__ == "__main__"):
    print("Lanzando threads de extraccion y consolidación...")
    th1.start()
    th2.start()
    th3.start()
    th4.start()
else:
    print("Ejecutada via falsa en Main...")


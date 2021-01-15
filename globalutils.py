import datetime
import time
from tickermanagement.utils import INFOBOLSA, BOLSADEMADRID, BSMARKETS
from sqlalchemy import create_engine
import threading
mthprintlock = threading.Lock()

def mthprint(v):
    mthprintlock.acquire()
    print(v,flush=True)
    mthprintlock.release()

def isprocessrunninginubuntu(servicename):
    import os
    s = os.system("systemctl is-active --quiet " + servicename)
    if s == 0:
        return True
    else:
        return False



def str2float(str):
    try:
        return float(str.replace(",","."));
    except BaseException as be:
        if type(be) == ValueError:
            raise be
        else:
            return None

def evaluate(f, maxtimes=10):
    counter = 0
    val = None
    while(val==None):
        try:
            val = f()
        except BaseException as be:
            if type(be)==ValueError:
                return None
            counter = counter + 1
            if (counter > maxtimes):
                raise BaseException("evaluate couldn't execute successfuly: " + str(be))
            else:
                time.sleep(10)
    return val


def isopentime(time):
    if (True):
        return True
    hour = int(datetime.datetime.strftime(time, "%H"))
    minute = int(datetime.datetime.strftime(time, "%M"))
    weekday = int(datetime.datetime.strftime(time, "%w"))
    #Lunes a Viernes de 9 a 17h
    if (weekday not in (1,2,3,4,5)):
        return False
    if ((hour >= 9) & (hour <= 17)):
        if (hour==17):
            if (minute<=55):
                return True
            else:
                return False
        else:
            return True

def isopentimefordataconsolidation(time):
    # if (True):
    #     return True
    hour = int(datetime.datetime.strftime(time, "%H"))
    minute = int(datetime.datetime.strftime(time, "%M"))
    weekday = int(datetime.datetime.strftime(time, "%w"))
    #Lunes a Viernes de 9 a 17h
    if (weekday not in (1,2,3,4,5)):
        return False
    if ((hour >= 9) & (hour <= 18)):
        return True
    else:
        return False

def isopentimefortickermanagement(time):
    hour = int(datetime.datetime.strftime(time, "%H"))
    minute = int(datetime.datetime.strftime(time, "%M"))
    weekday = int(datetime.datetime.strftime(time, "%w"))
    #Lunes a Viernes de 9 a 17h
    if (weekday not in (1,2,3,4,5)):
        return False
    if hour == 8:
        if (minute>=0) and (minute<=10):
            return True
    else:
        return False

def gettimestampfromfechatexto(source, cotizacionMc):
    if cotizacionMc.source == INFOBOLSA:
        #it might be HH:MM or dd/mm
        if cotizacionMc.fechaTexto.find(":") != -1:
            hour = cotizacionMc.fechaTexto[0:2]
            minute = cotizacionMc.fechaTexto[3:5]
            #timestamp
            #ts as string
            strts = str(cotizacionMc.ts)
            year = strts[0:4]
            month = strts[5:7]
            day = strts[8:10]
            datestring = day +"/" + month + "/" + year
            datestring = datestring + " " + cotizacionMc.fechaTexto
            timestamp = datetime.datetime.strptime(datestring, "%d/%m/%Y %H:%M")
            return timestamp
        elif cotizacionMc.fechaTexto.find("/") != -1:
            year = str(cotizacionMc.ts)[0:4]
            day = cotizacionMc.fechaTexto[0:2]
            month = cotizacionMc.fechaTexto[3:5]
            datestring = cotizacionMc.fechaTexto + "/" + year + " 17:00"
            timestamp = datetime.datetime.strptime(datestring, "%d/%m/%Y %H:%M")
            return timestamp
    if cotizacionMc.source == BOLSADEMADRID:
        if cotizacionMc.fechaTexto.find(":") != -1:
            #date and time
            if (cotizacionMc.fechaTexto.count(":") == 1):
                try:
                    timestamp = datetime.datetime.strptime(cotizacionMc.fechaTexto.strip(), "%d/%m/%Y %H:%M")
                except:
                    timestamp = None

            if (cotizacionMc.fechaTexto.count(":") == 2):
                datestring = cotizacionMc.fechaTexto[0:16]
                timestamp = datetime.datetime.strptime(datestring, "%d/%m/%Y %H:%M")
            return timestamp
        else:
            #only date
            datestring = cotizacionMc.fechaTexto.strip() + " 17:00"
            timestamp = datetime.datetime.strptime(datestring, "%d/%m/%Y %H:%M")
            return timestamp
    if cotizacionMc.source == BSMARKETS:
        #only time
        year = str(cotizacionMc.ts)[0:4]
        month = str(cotizacionMc.ts)[5:7]
        day = str(cotizacionMc.ts)[8:10]
        datestring = day + "/" + month + "/" + year
        datetimestring = datestring + " " + cotizacionMc.fechaTexto
        try:
            timestamp = datetime.datetime.strptime(datetimestring, "%d/%m/%Y %H:%M")
            return timestamp
        except:
            return None

def getconsolidatedcotizacionesforticker(ticker, engine):
    import pandas
    """
    Function queries and consolidates data directly from cotizaciones_mc
    :param ticker: 
    :return: Pandas DataFrame
    """
    sql = "SELECT distinct derivedsourcetimestamp, ticker, avg(ultimo) as ultimo, avg(percdiff) as percdiff, avg(max) as max, " \
          "avg(min) as min, avg(vol) as vol, avg(efectivo) as efectivo FROM aitrader.cotizaciones_mc " \
          "where ticker = '{}' " \
          "group by derivedsourcetimestamp, ticker " \
          "order by derivedsourcetimestamp asc;".format(ticker)
    res = pandas.read_sql(sql, engine)
    try:
        res.pivot(index="derivedsourcetimestamp",
                  columns=["ticker", "ultimo", "percdiff", "max", "min", "vol", "efectivo"])
        return res
    except BaseException as e:
        raise e

def gettickerlist(engine):
    import pandas
    sql = "SELECT * FROM tickers_mc"
    res = pandas.read_sql(sql, engine)
    return res["ticker"].tolist()


def dobeep():
    import winsound
    frequency = 1500  # Set Frequency To 2500 Hertz
    duration = 200  # Set Duration To 1000 ms == 1 second
    for i in range(5):
        winsound.Beep(frequency, duration)

def send_email(to, subject, content):
    import smtplib

    gmail_user = 'aitrader21@gmail.com'
    gmail_password = 'washablemarkets'

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
    except BaseException as e:
        print(str(e))
        'Something went wrong...'
    from email.mime.text import MIMEText
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = 'aitrader21@gmail.com'
    msg['To'] = to


    message = msg.as_string()


    try:
        server.sendmail("aitrader21@gmail.com", [to], message)
    except:
        print("Error en sendmail: " + subject)

def logmessage2mail(title, description):
    try:
        send_email("carloscz25@gmail.com", title, description)
    except:
        pass
def logexception2mail(stacktrace, e):
    try:
        send_email("carloscz25@gmail.com", str(e), stacktrace)
    except:
        pass

def dt642date(dt64):
    import numpy as np
    ts = (dt64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
    return datetime.datetime.fromtimestamp(ts).date()

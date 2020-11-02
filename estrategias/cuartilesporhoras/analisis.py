from model import getaitraderengine
import pandas
import numpy
from tickermanagement.utils import INFOBOLSA, BOLSADEMADRID, BSMARKETS
import datetime

def gettimestampfromfechatexto(source, values):
    """
    Function derived and adapted to pandas Series instead of class CotizacionMc in the values param
    from the globalutils file
    :param source:
    :param values:
    :return:
    """
    if values["source"] == INFOBOLSA:
        #it might be HH:MM or dd/mm
        if values["fechaTexto"].find(":") != -1:
            hour = values["fechaTexto"][0:2]
            minute = values["fechaTexto"][3:5]
            #timestamp
            #ts as string
            strts = str(values["ts"])
            year = strts[0:4]
            month = strts[5:7]
            day = strts[8:10]
            datestring = day +"/" + month + "/" + year
            datestring = datestring + " " + values["fechaTexto"]
            timestamp = datetime.datetime.strptime(datestring, "%d/%m/%Y %H:%M")
            return timestamp
        elif values["fechaTexto"].find("/") != -1:
            year = values["ts"][0:4]
            day = values["fechaTexto"][0:2]
            month = values["fechaTexto"][3:5]
            datestring = values["fechaTexto"] + "/" + year + " 17:00"
            timestamp = datetime.datetime.strptime(datestring, "%d/%m/%Y %H:%M")
            return timestamp
    if values["source"] == BOLSADEMADRID:
        if values["fechaTexto"].find(":") != -1:
            #date and time
            if (values["fechaTexto"].count(":") == 1):
                timestamp = datetime.datetime.strptime(values["fechaTexto"].strip(), "%d/%m/%Y %H:%M")
            if (values["fechaTexto"].count(":") == 2):
                datestring = values["fechaTexto"][0:16]
                timestamp = datetime.datetime.strptime(datestring, "%d/%m/%Y %H:%M")
            return timestamp
        else:
            #only date
            datestring = values["fechaTexto"].strip() + " 17:00"
            timestamp = datetime.datetime.strptime(datestring, "%d/%m/%Y %H:%M")
            return timestamp
    if values["source"] == BSMARKETS:
        #only time
        val = None
        if  type(values["ts"]) == str:
            val = values["ts"]
        elif type(values["ts"]==datetime):
            val = values["ts"].strftime("%Y-%m-%d %H:%M")
        year = val[0:4]
        month = val[5:7]
        day = val[8:10]
        datestring = day + "/" + month + "/" + year
        datetimestring = datestring + " " + values["fechaTexto"]
        timestamp = datetime.datetime.strptime(datetimestring, "%d/%m/%Y %H:%M")
        return timestamp


engine = getaitraderengine()
df = pandas.read_sql("select * from cotizaciones_mc where ticker = 'REP'", engine)
#creation of a datetime like column -> conversion of fechatexto column to a truth timestamp for the value
#ts column is the record timestamp, not the course timestamp

df["extractionts"] = pandas.Series(dtype='datetime64[ns]')
df["year"] = pandas.Series(dtype=numpy.int)
df["month"] = pandas.Series(dtype=numpy.int)
df["day"] = pandas.Series(dtype=numpy.int)
df["hour"] = pandas.Series(dtype=numpy.int)
df["das"] = pandas.Series()
df["max"] = pandas.Series(dtype=numpy.float)
df["min"] = pandas.Series(dtype=numpy.float)
df["percvar"] = pandas.Series(dtype=numpy.float)

# df.apply(createcolumnsdaymonthyearfromts, axis=1)

#1. Writting values from the extraction time in the columns
for index, row in df.iterrows():
    fechaTexto = row["fechaTexto"]
    ts = row["ts"]
    ats = gettimestampfromfechatexto(row["source"], row)
    df["extractionts"][index] = ats
    df["year"][index] = int(ats.strftime("%Y"))
    df["month"][index] = int(ats.strftime("%m"))
    df["day"][index] = int(ats.strftime("%d"))
    df["hour"][index] = int(ats.strftime("%H"))
    df["das"][index] = ats.strftime("%Y-%m-%d")


#2. Writing columns of max/min/percvariation per day
df["maxd"] = pandas.Series(dtype=numpy.float)
df["mind"] = pandas.Series(dtype=numpy.float)
df["percvard"] = pandas.Series(dtype=numpy.float)
df["til"] = pandas.Series(dtype=numpy.int)
df["UD"] = pandas.Series(dtype='str')

distinctdates = df["das"].unique()
num_tiles = 6
for d in distinctdates:
    max = df.where(df["das"]==d, inplace=False)["ultimo"].max()
    min = df.where(df["das"] == d, inplace=False)["ultimo"].min()
    perc = (max-min)/min
    df.loc[df["das"]==d,'maxd'] = max
    df.loc[df["das"]==d,'mind'] = min
    df.loc[df["das"] == d, 'percvard'] = perc
    first = df.loc[df["das"] == d, 'ultimo'].values[0]
    last = df.loc[df["das"] == d, 'ultimo'].values[len(df.loc[df["das"] == d, 'ultimo'])-1]
    df.loc[df["das"]==d, "UD"] = "U" if last > first else "D"

    #assigning the tin
    for index, row in df.loc[df["das"] == d].iterrows():
        df["til"][index] = (df["ultimo"][index]-df["mind"][index])//((df["maxd"][index]-df["mind"][index])/num_tiles)


res6 = {}
res0 = {}
cnt = 0
for d in distinctdates:
    for h in range(9,17):
        s = df.loc[(df["das"]==d) & (df["hour"]==h) & ((df["til"]>=5)) & (df["UD"]=="D"), 'til'].count()
        if not h in res6.keys():
            res6[h] = 0
        if s > 0:
            res6[h] += 1

        s = df.loc[(df["das"] == d) & (df["hour"] == h) & ((df["til"] <= 1)), 'til'].count()
        if not h in res0.keys():
            res0[h] = 0
        if s > 0:
            res0[h] += 1
y = 2


#Check if continuous descent/increase in closing price afects the following day closing price and the intensity in the
#shift if any

#read the data
sql = "select distinct ticker,str_to_date(fechatexto, '%d-%m-%Y') as fecha, valorcierre, split from \
( \
select *, str_to_date(fechatexto, '%d-%m-%Y') from cotizaciones_hist_mc \
) as st1 \
order by ticker asc, fecha asc"

import pandas
from model import getaitraderengine
engine = getaitraderengine("localhost",3306, "aitrader")
df = pandas.read_sql(sql, engine)


tikers = {}

for i in range(len(df)):

    if (not df["ticker"][i] in tikers.keys()):
        prevvalue = None
        prevpercdiff = None
        percdiff = None
        lastiterationshiftsign = None
        numsessions = None
        tikers[df["ticker"][i]] = {}
        tikers[df["ticker"][i]]["fechas"] = {}
        tikers[df["ticker"][i]]["shiftaftersessionsbullish"] = {}
        tikers[df["ticker"][i]]["shiftaftersessionsbearish"] = {}
        tikers[df["ticker"][i]]["noshiftaftersessions"] = {}
        tikers[df["ticker"][i]]["totalsessions"] = 0
        tikers[df["ticker"][i]]["totalshiftsessions"] = 0
        tikers[df["ticker"][i]]["totalnoshiftsessions"] = 0
        tikers[df["ticker"][i]]["tssplustnss"] = 0
        # totalsessions = 0
    # totalsessions += 1
    tikers[df["ticker"][i]]["totalsessions"] += 1
    tikers[df["ticker"][i]]["fechas"][df["fecha"][i]] = df['valorcierre'][i]
    if (prevvalue!=None):
        percdiff = (df['valorcierre'][i] - prevvalue) / prevvalue


    if prevpercdiff != None:
        if (percdiff>0 and prevpercdiff<0) or (percdiff<0 and prevpercdiff>0):
            bullishbearish = None
            dictname = None
            if percdiff > 0:
                bullishbearish = True
                dictname = "shiftaftersessionsbearish"
            else:
                bullishbearish = False
                dictname = "shiftaftersessionsbullish"

            if lastiterationshiftsign!=None:
                numsessions = i - lastiterationshiftsign
                if (numsessions in tikers[df["ticker"][i]][dictname].keys()):
                    # shiftaftersessions[numsessions] += 1
                    tikers[df["ticker"][i]][dictname][numsessions] += 1
                else:
                    # shiftaftersessions[numsessions] = 1
                    tikers[df["ticker"][i]][dictname][numsessions] = 1
                # totalshiftsessions += 1
                tikers[df["ticker"][i]]["totalshiftsessions"] += 1
            lastiterationshiftsign = i
        else:
            if lastiterationshiftsign == None:
                numsessions = i
            else:
                numsessions = i - lastiterationshiftsign
            if (numsessions in tikers[df["ticker"][i]]["noshiftaftersessions"].keys()):
                # noshiftaftersessions[numsessions] += 1
                tikers[df["ticker"][i]]["noshiftaftersessions"][numsessions] += 1
            else:
                # noshiftaftersessions[numsessions] = 1
                tikers[df["ticker"][i]]["noshiftaftersessions"][numsessions] = 1
            # totalnoshiftsessions += 1
            tikers[df["ticker"][i]]["totalnoshiftsessions"] += 1


    prevvalue = df['valorcierre'][i]
    prevpercdiff = percdiff
    tikers[df["ticker"][i]]["tssplustnss"] = tikers[df["ticker"][i]]["totalshiftsessions"] + tikers[df["ticker"][i]]["totalnoshiftsessions"]


#displayando chart de ticker

def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

import matplotlib.pyplot as plt
import numpy as np

for t in tikers:

    vs = [tikers[t]['shiftaftersessionsbullish'][i] if i in tikers[t]['shiftaftersessionsbullish'].keys() else 0 for i in range(16)]
    vs2 = [tikers[t]['shiftaftersessionsbearish'][i] if i in tikers[t]['shiftaftersessionsbearish'].keys() else 0 for i in range(16)]
    vs3 = [tikers[t]['noshiftaftersessions'][i] if i in tikers[t]['noshiftaftersessions'].keys() else 0 for i in range(16)]

    fig, ax = plt.subplots()
    fig.set_figwidth(17)
    fig.set_figheight(8)
    x = np.arange(16)
    width = 0.35

    rects1 = ax.bar(x - width/2, vs, width/2, label='ShiftBullish')
    rects2 = ax.bar(x , vs2, width/2, label='ShiftBearish')
    rects3 = ax.bar(x + width/2 , vs3, width/2, label='NoShift')


    ax.legend()

    fig.tight_layout()
    plt.title(t)
    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    # plt.show()
    y=2
    plt.savefig("results/" + t + ".jpg")
y = 2
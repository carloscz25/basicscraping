from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from tickermanagement.utils import INFOBOLSA, BOLSADEMADRID, BSMARKETS
from model import CotizazionHistMC, TickerMC, CotizacionMC, CotizacionConsolidadaMC
from globalutils import gettimestampfromfechatexto
from sqlalchemy import and_

def consolidatedata(engine):

    #to be used with the string.find() fuction
    priority = BOLSADEMADRID + "," + BSMARKETS + "," + INFOBOLSA

    Session = sessionmaker(bind=engine)
    session = Session()
    tickers = session.query(TickerMC).filter(TickerMC.avoid_consolidation == None).all()

    for ticker in tickers:

        tickerdict = __buildtickerdictwithcotizaciones__(ticker, engine, session)

        if tickerdict == None:
            continue

        for k,v in tickerdict.items():
            if len(v.keys()) == 1:
                c = CotizacionConsolidadaMC()
                c.ts = k
                #verification that the timestamp has not been previously recorded
                #otherwhise we can duplicate data across several calls
                prevcc = session.query(CotizacionConsolidadaMC).filter(and_(CotizacionConsolidadaMC.ts == c.ts, CotizacionConsolidadaMC.ticker == ticker.ticker)).first()
                if (prevcc != None):
                    continue

                c.ultimo = v[list(v.keys())[0]]["ultimo"]
                c.volumen = v[list(v.keys())[0]]["vol"]
                c.efectivo = v[list(v.keys())[0]]["efectivo"]
                if "lastid" in v[list(v.keys())[0]].keys():
                    c.cotizacioneslastid = v[list(v.keys())[0]]["lastid"]
                c.ticker = ticker.ticker
                session.add(c)
            if len(v.keys()) > 1:
                #priority index
                priorityindex = -1
                prioritysource = None
                for i in range(len(v.keys())):
                    if priorityindex == -1:
                        priorityindex = i
                        prioritysource = list(v.keys())[i]
                    else:
                        source = prioritysource
                        prioritysource = list(v.keys())[i]
                        if (priority.find(prioritysource)<priority.find(source)):
                            priorityindex = i
                            prioritysource = list(v.keys())[i]
                #end priority index determination

                c = CotizacionConsolidadaMC()
                c.ts = k
                #if having the two sources for the same timestamp, I prefer data from
                #infobolsa
                c.ultimo = v[prioritysource]["ultimo"]
                c.volumen = v[prioritysource]["vol"]
                c.efectivo = v[prioritysource]["efectivo"]
                #annotating the lastid: whichever record has it
                for k in v.keys():
                    if "lastid" in v[k].keys():
                        c.cotizacioneslastid = v[k]["lastid"]
                #end annotating lastid
                c.ticker = ticker.ticker
                session.add(c)
        session.commit()
    session.close()

def __buildtickerdictwithcotizaciones__(ticker, engine, session):
    tickerdict = {}
    # getting last entered index

    ccmc = session.query(CotizacionConsolidadaMC).filter(CotizacionConsolidadaMC.ticker == ticker.ticker).order_by(
        CotizacionConsolidadaMC.cotizacioneslastid.desc()).first()
    lastid = None
    if ccmc != None:
        lastid = ccmc.cotizacioneslastid


    ids = []
    with engine.connect() as conn:
        sql = "SELECT id from cotizaciones_mc WHERE ticker = '" + ticker.ticker + "'"
        if lastid != None:
            sql = sql + " AND id > " + str(int(lastid))
        sql = sql + " order by id asc"
        rs = conn.execute(sql)
        for row in rs:
            ids.append(row['id'])

    conn.close()
    hasrows = False
    Session_ = sessionmaker(bind=engine)
    session_ = Session_()
    for id in ids:
        hasrows = True

        cotizacionMc = session_.query(CotizacionMC).filter(CotizacionMC.id == id).first()
        timestamp = gettimestampfromfechatexto(cotizacionMc.source, cotizacionMc)
        if timestamp not in tickerdict.keys():
            tickerdict[timestamp] = {}
        tickerdict[timestamp][cotizacionMc.source] = {}
        tickerdict[timestamp][cotizacionMc.source]["ultimo"] = cotizacionMc.ultimo
        tickerdict[timestamp][cotizacionMc.source]["efectivo"] = cotizacionMc.efectivo
        tickerdict[timestamp][cotizacionMc.source]["vol"] = cotizacionMc.vol



    if hasrows:
        tickerdict[timestamp][cotizacionMc.source]["lastid"] = id
    else:
        tickerdict = None

    session_.commit()
    session_.close()

    return tickerdict




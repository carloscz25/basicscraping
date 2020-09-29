from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from model import CotizazionHistMC, TickerMC, CotizacionMC, CotizacionConsolidadaMC

INFOBOLSA = "infobolsa"
BOLSADEMADRID = "bolsademadrid"
BSMARKETS = "bsmarkets"

TICKERS_INFOBOLSA = {}
TICKERS_BOLSADEMADRID = {}
TICKERS_BSMARKETS = {}
tickerdicts = {}
tickerdicts[INFOBOLSA] = TICKERS_INFOBOLSA
tickerdicts[BOLSADEMADRID] = TICKERS_BOLSADEMADRID
tickerdicts[BSMARKETS] = TICKERS_BSMARKETS

loaded = {}
loaded[INFOBOLSA] = False
loaded[BOLSADEMADRID] = False
loaded[BSMARKETS] = False

def gettickersdictionary(source, engine):

    if loaded[source] == True:
        return tickerdicts[source]

    Session = sessionmaker(bind=engine)
    session = Session()

    tickers = session.query(TickerMC).all()
    for t in tickers:

        if source == INFOBOLSA:
            tickerdicts[source][t.infobolsa] = t.ticker
        elif source == BOLSADEMADRID:
            tickerdicts[source][t.bolsademadrid] = t.ticker
        elif source == BSMARKETS:
            tickerdicts[source][t.bsmarkets] = t.ticker
    session.close()
    tickerdict = tickerdicts[source]
    loaded[source] = True

    return tickerdict

# engine = create_engine("mysql+mysqlconnector://root:dtisat@localhost:3306/aitrader")
# dict = gettickersdictionary(INFOBOLSA, engine)
# y = 2
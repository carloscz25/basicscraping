import pandas
from model import getaitraderengine
from globalutils import getconsolidatedcotizacionesforticker, gettickerlist

engine = getaitraderengine()

tickers = gettickerlist(engine)
for t in tickers:

    df = getconsolidatedcotizacionesforticker(t, engine)

    y=2
y = 2
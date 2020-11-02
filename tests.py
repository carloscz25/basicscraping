
from model import getaitraderengine

engine = getaitraderengine()
from model import table_TickerMC
table_TickerMC.create(engine)
engine.dispose()



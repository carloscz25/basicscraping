
from globalutils import gettimestampfromfechatexto
from model import TickerMC
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from model import CotizacionMC
from dataconsolidation.consolidation import __buildtickerdictwithcotizaciones__
import traceback


from techanalysis.utils import plot_emas_and_stochoscilators_for_ticker
from model import getaitraderengine

plot_emas_and_stochoscilators_for_ticker("CABK", [10,25,50], [10,25,50], getaitraderengine())

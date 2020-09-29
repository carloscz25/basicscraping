from abc import abstractmethod
from sqlalchemy import create_engine
from sqlalchemy.orm import Session ,sessionmaker
from model import TickerMC

class BaseStrategy():

    buyrule = None
    sellrule = None
    tickers = None
    engine = None

    def __init__(self, engine):
        self.engine = engine


    def gettickers(self):
        if self.tickers == None:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            self.tickers = session.query(TickerMC).filter(TickerMC.avoid_consolidation == None).all()
        return self.tickers

    def setbuyrule(self, buyrule):
        self.buyrule = buyrule

    def getbuyrule(self):
        return self.buyrule








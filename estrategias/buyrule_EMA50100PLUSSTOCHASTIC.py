from estrategias.basebuyrule import BuyRule
import pandas


def EMA50100PLUSSTOCHASTIC(BuyRule):

    engine = None

    def __init__(self, engine):
        self.engine = engine

    def mustbuytickers(self, ticker):
        pass

    def getadditionalinfo(self, ticker):
        raise NotImplementedError()

    def __calc_10_last_ema50(self, ticker):
        pandas.read_sql("",engine=self.engine)


from abc import abstractmethod


class BuyRule():

    def __init(self):
        pass

    @abstractmethod
    def mustbuy(self):
        raise NotImplementedError()

    @abstractmethod
    def mustbuyticker(self, ticker):
        raise NotImplementedError()

    @abstractmethod
    def getadditionalinfo(self, ticker):
        raise NotImplementedError()
import datetime





class Diary:
    datesandongoingops = {}


class Portfolio:
    """
    liquidassets : amount of liquid in Portfolio
    operations : dict of ongoing operations
    historicops : dict of closed operations
    growassetsautomatically : set if porfolio liquidassets will grow as strategy demands require increase investments
    maxassetsnecessary : variable holding the max value of liquidassets to deploy the currently tested strategy
    financialexpenses : variable holding the total amount of fees related to all operations
    """
    liquidassets = 0
    operations = {}
    historicops = {}
    growassetsautomatically = True
    maxassetsnecessary = 0
    financialexpenses = 0
    gainsinperiod = 0
    lossesinperiod = 0
    diary = Diary()
    operationvalue_lastsimulationperiod = {}

    def __init__(self, **kwargs):
        self.growassetsautomatically = kwargs.get("growassetsautomatically", True)
        self.liquidassets = kwargs.get("liquidassets", 0)
        self.maxassetsnecessary = self.liquidassets


    def totalvalueinbooks(self):
        total = self.liquidassets
        for o in self.operations:
            total += self.operations[o].numassets * self.operations[o].buyingprice
        return total

    def totalvalueatsimulationend(self):
        total = self.liquidassets
        for o in self.operations:
            id = o
            ticker = id[0:o.find("_")]
            price = self.operationvalue_lastsimulationperiod[ticker]
            total += self.operations[o].numassets * price
        return total



    def dobuyingoperation(self, ticker, numassets, price, fees, buyingdate):
        o = Operation()
        o.id = ticker + "_" + buyingdate.strftime("%Y%m%d")
        o.ticker = ticker
        o.numassets = numassets
        o.buyingprice = price
        o.fees += fees
        o.buyingdate = buyingdate
        operationvalue = price * numassets
        self.liquidassets -= operationvalue
        self.operations[o.id] = o
        if self.diary != None:
            if buyingdate in self.diary.datesandongoingops:
                self.diary.datesandongoingops[buyingdate] += 1
            else:
                self.diary.datesandongoingops[buyingdate] = 1
        return o

    def isholdingoperationforticker(self, ticker):
        for o in self.operations:
            if self.operations[o].ticker == ticker:
                return True
        return False

    def positiveVsNegativeHistoricOps(self):
        positives = 0
        negatives = 0
        for o in self.historicops:
            op = self.historicops[o]
            if op.result > 0:
                positives += 1
            elif op.result <= 0:
                negatives += 1
        return (positives, negatives)

class Operation:

    """
    id : Id for the portfolio dict. Easen deletion from ongoing operatiosn
    rest : SE (Self Explanatory)

    """

    id = None
    ticker = None
    numassets = None
    buyingprice = None
    closingprice = None
    fees = 0
    buyingdate = None
    closingdate = None
    result = None


    def closeoperation(self, closingprice, closingdate, fees, portfolio):
        self.closingprice = closingprice
        self.closingdate = closingdate
        self.fees += fees
        self.result = (self.closingprice*self.numassets)-(self.buyingprice * self.numassets)-self.fees
        brutoresult = (self.closingprice*self.numassets)-(self.buyingprice * self.numassets)
        if brutoresult > 0:
            portfolio.gainsinperiod += brutoresult
        else:
            portfolio.lossesinperiod += abs(brutoresult)
        operationvalue = self.numassets * self.closingprice
        portfolio.liquidassets += operationvalue - self.fees
        portfolio.financialexpenses += self.fees
        del portfolio.operations[self.id]
        portfolio.historicops[self.id] = self





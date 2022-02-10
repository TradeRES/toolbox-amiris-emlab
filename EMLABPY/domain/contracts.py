
"""
This file contains Loans, CashFlow
"""
from energy import PowerPlant

class Loan:
    def __init__(self):
        #instance fields found by Java to Python Converter:
        self.from_keyword_conflict = None
        self.to = None
        self.regardingPowerPlant = None
        self.amountPerPayment = 0
        self.totalNumberOfPayments = 0
        self.numberOfPaymentsDone = 0
        self.loanStartTime = 0

    #    @RelatedTo(type = "LEND_TO_AGENT", elementClass = EMLabAgent.class, direction = Direction.OUTGOING)
    #    @RelatedTo(type = "LEND_BY_AGENT", elementClass = EMLabAgent.class, direction = Direction.OUTGOING)
    #    @RelatedTo(type = "LOAN_POWERPLANT", elementClass = PowerPlant.class, direction = Direction.OUTGOING)

    def getLoanStartTime(self):
        return self.loanStartTime

    def setLoanStartTime(self, loanStartTime):
        self.loanStartTime = loanStartTime

    def getTotalNumberOfPayments(self):
        return self.totalNumberOfPayments

    def getAmountPerPayment(self):
        return self.amountPerPayment

    def setAmountPerPayment(self, amountPerPayment):
        self.amountPerPayment = amountPerPayment

    def setTotalNumberOfPayments(self, totalNumberOfPayments):
        self.totalNumberOfPayments = totalNumberOfPayments

    def getNumberOfPaymentsDone(self):
        return self.numberOfPaymentsDone

    def setNumberOfPaymentsDone(self, numberOfPaymentsDone):
        self.numberOfPaymentsDone = numberOfPaymentsDone

    def getFrom(self):
        return self.from_keyword_conflict

    def setFrom(self, from_keyword_conflict):
        self.from_keyword_conflict = from_keyword_conflict

    def getTo(self):
        return self.to

    def setTo(self, to):
        self.to = to

    def getRegardingPowerPlant(self):
        return self.regardingPowerPlant

    def setRegardingPowerPlant(self, regardingPowerPlant):
        self.regardingPowerPlant = regardingPowerPlant

class CashFlow:

    def __init__(self):
        #instance fields found by Java to Python Converter:
        self.__from_keyword_conflict = None
        self.__to = None
        self.__regardingPowerPlant = None
        self.__type = 0
        self.__money = 0
        self.__time = 0


    # UNCLASSIFIED = 0
    # ELECTRICITY_SPOT = 1
    # ELECTRICITY_LONGTERM = 2
    # FIXEDOMCOST = 3
    # COMMODITY = 4
    # CO2TAX = 5
    # CO2AUCTION = 6
    # LOAN = 7
    # DOWNPAYMENT = 8
    # NATIONALMINCO2 = 9
    # STRRESPAYMENT = 10
    # CAPMARKETPAYMENT = 11
    # CO2HEDGING = 12

    def getTime(self):
        return self.__time

    def setTime(self, time):
        self.__time = time

    def getFrom(self):
        return self.__from_keyword_conflict

    def setFrom(self, from_keyword_conflict):
        self.__from_keyword_conflict = from_keyword_conflict

    def getTo(self):
        return self.__to

    def setTo(self, to):
        self.__to = to

    def getMoney(self):
        return self.__money

    def setMoney(self, money):
        self.__money = money

    def getType(self):
        return self.__type

    def setType(self, type):
        self.__type = type

    def toString(self):
        return "from " + self.getFrom() + " to " + self.getTo() + " type " + str(self.getType()) + " amount " + str(self.getMoney())

    def getRegardingPowerPlant(self):
        return self.__regardingPowerPlant

    def setRegardingPowerPlant(self, regardingPowerPlant):
        self.__regardingPowerPlant = regardingPowerPlant

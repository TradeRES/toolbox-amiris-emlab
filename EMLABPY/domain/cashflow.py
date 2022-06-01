
"""
This file contains Loans, CashFlow
"""

class CashFlow:

    def __init__(self):

        self.from_agent = None
        self.to = None
        self.regardingPowerPlant = None
        self.type = 0 # can be LOAN
        self.money = 0
        self.time = 0
        self.UNCLASSIFIED = "UNCLASSIFIED"
        self.ELECTRICITY_SPOT = "ELECTRICITY_SPOT"
        self.ELECTRICITY_LONGTERM = "ELECTRICITY_LONGTERM"
        self.FIXEDOMCOST = "FIXEDOMCOST"
        self.COMMODITY = "COMMODITY"
        self.CO2TAX = "CO2TAX"
        self.CO2AUCTION = "CO2AUCTION"
        self.LOAN = "LOAN"
        self.DOWNPAYMENT = "DOWNPAYMENT"
        self.NATIONALMINCO2 = "NATIONALMINCO2"
        self.STRRESPAYMENT = "STRRESPAYMENT"
        self.CAPMARKETPAYMENT = "CAPMARKETPAYMENT"
        self.CO2HEDGING = "CO2HEDGING"

    def getTime(self):
        return self.time

    def setTime(self, time):
        self.time = time

    def getFrom(self):
        return self.from_agent

    def setFrom(self, from_agent):
        self.from_agent = from_agent

    def getTo(self):
        return self.to

    def setTo(self, to):
        self.to = to

    def getMoney(self):
        return self.money

    def setMoney(self, money):
        self.money = money

    def getType(self):
        return self.type

    def setType(self, type):
        self.type = type

    def toString(self):
        return "from " + self.getFrom() + " to " + self.getTo() + " type " + str(self.getType()) + " amount " + str(self.getMoney())

    def getRegardingPowerPlant(self):
        return self.regardingPowerPlant

    def setRegardingPowerPlant(self, regardingPowerPlant):
        self.regardingPowerPlant = regardingPowerPlant


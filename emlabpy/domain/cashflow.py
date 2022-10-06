
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


    def setTime(self, time):
        self.time = time

    def setFrom(self, from_agent):
        self.from_agent = from_agent

    def setTo(self, to):
        self.to = to

    def setMoney(self, money):
        self.money = money

    def setType(self, type):
        self.type = type


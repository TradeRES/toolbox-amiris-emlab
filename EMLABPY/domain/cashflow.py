
"""
This file contains Loans, CashFlow
"""
from energy import PowerPlant

class CashFlow:

    def __init__(self):
        #instance fields found by Java to Python Converter:
        self.__from_keyword_conflict = None
        self.__to = None
        self.__regardingPowerPlant = None
        self.__type = 0
        self.__money = 0
        self.__time = 0

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

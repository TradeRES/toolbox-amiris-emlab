import logging
import pandas as pd
from domain.actors import EMLabAgent
from domain.import_object import *


class EnergyProducer(EMLabAgent):

    def __init__(self, name):
        super().__init__(name)
        self.investmentRole = None
        self.investorMarket = None
        self.priceMarkUp = None
        self.longTermContractMargin = None
        self.longTermContractPastTimeHorizon = None
        self.equityInterestRate = None
        self.downpaymentFractionOfCash = None  # this is to establish if there is enough money for downpayment in investment algorithm
        self.debtRatioOfInvestments = None
        self.willingToInvest = None
        self.loanInterestRate = None
        self.dismantlingProlongingYearsAfterTechnicalLifetime = None
        self.dismantlingRequiredOperatingProfit = None
        self.pastTimeHorizon = None
        self.readytoInvest = True
        self.cash = 0
        self.CF_ELECTRICITY_SPOT = 0
        self.CF_LOAN = 0
        self.CF_DOWNPAYMENT = 0
        self.CF_STRRESPAYMENT = 0
        self.CF_CAPMARKETPAYMENT = 0
        self.CF_FIXEDOMCOST = 0
        self.CF_COMMODITY = 0

    def add_parameter_value(self, reps, parameter_name, parameter_value: object, alternative):
        # according to the scenario.yaml, if is has energy carrier then it is intermittent
        # if parameter_name == 'cash':
        #     self.cash = parameter_value
        # From here are the inputs from emlab unit
        if parameter_name == 'debtRatioOfInvestments':
            self.debtRatioOfInvestments = float(parameter_value)
        elif parameter_name == 'dismantlingProlongingYearsAfterTechnicalLifetime':
            self.dismantlingProlongingYearsAfterTechnicalLifetime = int(parameter_value)
        elif parameter_name == 'dismantlingRequiredOperatingProfit':
            self.dismantlingRequiredOperatingProfit = int(parameter_value)
        elif parameter_name == 'downpaymentFractionOfCash':
            self.downpaymentFractionOfCash = float(parameter_value)
        elif parameter_name == 'equityInterestRate':
            self.equityInterestRate = float(parameter_value)
        elif parameter_name == 'investmentRole':
            self.investmentRole = parameter_value
        elif parameter_name == 'investorMarket':
            self.investorMarket = parameter_value
        elif parameter_name == 'loanInterestRate':
            self.loanInterestRate = float(parameter_value)
        elif parameter_name == 'longTermContractMargin':
            self.longTermContractMargin = float(parameter_value)
        elif parameter_name == 'longTermContractPastTimeHorizon':
            self.longTermContractPastTimeHorizon = int(parameter_value)
        elif parameter_name == 'priceMarkUp':
            self.priceMarkUp = float(parameter_value)
        elif parameter_name == 'willingToInvest':
            self.willingToInvest = parameter_value
        elif parameter_name in ["CF_ELECTRICITY_SPOT", "CF_LOAN", "CF_DOWNPAYMENT", "CF_STRRESPAYMENT",
                                "CF_CAPMARKETPAYMENT", "CF_FIXEDOMCOST", "CF_COMMODITY"] and reps.runningModule == "plotting":
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            pd_series = pd.Series(values, index = index)
            setattr(self, parameter_name, pd_series)

    def calculateAveragePastOperatingProfit(self, pp, horizon):
        averagePastOperatingProfit = 0
        for i in range(-horizon, 1):
            averagePastOperatingProfit += calculatePastOperatingProfitInclFixedOMCost(pp,
                                                                                      getCurrentTick() + i) / horizon
        logging.INFO(" %s has had an average operating profits of %s", pp, averagePastOperatingProfit)
        return averagePastOperatingProfit

    def calculatePastOperatingProfitInclFixedOMCost(self, plant, clearingTick):
        rep = self.reps.findFinancialPowerPlantReportsForPlantForTime(plant, clearingTick)
        if rep is not None:
            logging.INFO(
                " %s report: tick %s , revenue: %s  + rep.getOverallRevenue()  var cost: rep.getVariableCosts()  fixed om cost: rep.getFixedOMCosts()",
                plant, clearingTick)
            return rep.getOverallRevenue() - rep.getVariableCosts() - rep.getFixedOMCosts()
        logging.INFO("No financial report for %s for tick %s, so returning 0", plant, clearingTick)
        return Double.MAX_VALUE  # TODO avoid dismantling simply becuase you have no data for the full horizon?

    def isWillingToInvest(self):
        return self.willingToInvest

    def setWillingToInvest(self, willingToInvest):
        self.willingToInvest = willingToInvest

    def getDownpaymentFractionOfCash(self):
        return self.downpaymentFractionOfCash

    def setDownpaymentFractionOfCash(self, downpaymentFractionOfCash):
        self.downpaymentFractionOfCash = downpaymentFractionOfCash

    def getLoanInterestRate(self):
        return self.loanInterestRate

    def setLoanInterestRate(self, loanInterestRate):
        self.loanInterestRate = loanInterestRate

    def getNumberOfYearsBacklookingForForecasting(self):
        return self.numberOfYearsBacklookingForForecasting

    def setNumberOfYearsBacklookingForForecasting(self, numberOfYearsBacklookingForForecasting):
        self.numberOfYearsBacklookingForForecasting = numberOfYearsBacklookingForForecasting

    def getDismantlingProlongingYearsAfterTechnicalLifetime(self):
        return self.dismantlingProlongingYearsAfterTechnicalLifetime

    def setDismantlingProlongingYearsAfterTechnicalLifetime(self, dismantlingProlongingYearsAfterTechnicalLifetime):
        self.dismantlingProlongingYearsAfterTechnicalLifetime = dismantlingProlongingYearsAfterTechnicalLifetime

    def getDismantlingRequiredOperatingProfit(self):
        return self.dismantlingRequiredOperatingProfit

    def setDismantlingRequiredOperatingProfit(self, dismantlingRequiredOperatingProfit):
        self.dismantlingRequiredOperatingProfit = dismantlingRequiredOperatingProfit

    def getEquityInterestRate(self):
        return self.equityInterestRate

    def setEquityInterestRate(self, investmentDiscountRate):
        self.equityInterestRate = investmentDiscountRate

    def getLongTermContractMargin(self):
        return self.longTermContractMargin

    def setLongTermContractMargin(self, longTermContractMargin):
        self.longTermContractMargin = longTermContractMargin

    def getLongTermContractPastTimeHorizon(self):
        return self.longTermContractPastTimeHorizon

    def setLongTermContractPastTimeHorizon(self, longTermContractPastTimeHorizon):
        self.longTermContractPastTimeHorizon = longTermContractPastTimeHorizon

    def getDebtRatioOfInvestments(self):
        return self.debtRatioOfInvestments

    def setDebtRatioOfInvestments(self, debtRatioOfInvestments):
        self.debtRatioOfInvestments = debtRatioOfInvestments

    def getPriceMarkUp(self):
        return self.priceMarkUp

    def setPriceMarkUp(self, priceMarkUp):
        self.priceMarkUp = priceMarkUp

    def getInvestmentRole(self):
        return self.investmentRole

    def setInvestmentRole(self, investmentRole):
        self.investmentRole = investmentRole

    def getInvestorMarket(self):
        return self.investorMarket

    def setInvestorMarket(self, investorMarket):
        self.investorMarket = investorMarket

    def getNumberOfYearsBacklookingForForecasting(self):
        return self.numberOfYearsBacklookingForForecasting

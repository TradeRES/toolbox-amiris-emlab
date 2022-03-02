from emlabpy.domain.import_object import *

class EnergyProducer(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.investmentRole = None
        self.investorMarket = None
        self.priceMarkUp = None
        self.longTermContractMargin = None
        self.longTermContractPastTimeHorizon = None
        self.investmentFutureTimeHorizon = None
        self.equityInterestRate = None
        self.downpaymentFractionOfCash = None
        self.debtRatioOfInvestments = None
        self.willingToInvest = None
        self.loanInterestRate = None
        self.numberOfYearsBacklookingForForecasting = None
        self.dismantlingProlongingYearsAfterTechnicalLifetime = None
        self.dismantlingRequiredOperatingProfit = None
        self.pastTimeHorizon = None

    def add_parameter_value(self, reps, parameter_name, parameter_value: object, alternative):
        # according to the scenario.yaml, if is has energy carrier then it is intermittent
        if parameter_name == 'cash':
            self.cash = int(parameter_value)
        #From here are the inputs from emlab unit
        elif parameter_name == 'debtRatioOfInvestments':
            self.debtRatioOfInvestments = float(parameter_value)
        elif parameter_name == 'dismantlingProlongingYearsAfterTechnicalLifetime':
            self.dismantlingProlongingYearsAfterTechnicalLifetime = int(parameter_value)
        elif parameter_name == 'dismantlingRequiredOperatingProfit':
            self.dismantlingRequiredOperatingProfit = int(parameter_value)
        elif parameter_name == 'downpaymentFractionOfCash':
            self.downpaymentFractionOfCash = float(parameter_value)
        elif parameter_name == 'equityInterestRate':
            self.equityInterestRate = float(parameter_value)
        elif parameter_name == 'investmentFutureTimeHorizon':
            self.investmentFutureTimeHorizon = int(parameter_value)
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
        elif parameter_name == 'numberOfYearsBackLookingForForecasting':
            self.numberOfYearsBackLookingForForecasting = int(parameter_value)
        elif parameter_name == 'pastTimeHorizon':
            self.pastTimeHorizon = int(parameter_value)
        elif parameter_name == 'priceMarkUp':
            self.priceMarkUp = float(parameter_value)
        elif parameter_name == 'willingToInvest':
            self.willingToInvest = parameter_value

    def determineLoanAnnuities(self, totalLoan, payBackTime, interestRate):
        q = 1 + interestRate
        annuity = totalLoan * (q ** payBackTime * (q - 1)) / (q ** payBackTime - 1)
        return annuity

    def predictFuelPrices(self, agent, futureTimePoint):
        # Fuel Prices
        expectedFuelPrices = {}


        # for substance in self.reps.substances:
        #     cps = reps.findAllClearingPointsForSubstanceTradedOnCommodityMarkesAndTimeRange(substance, getCurrentTick() - (agent.getNumberOfYearsBacklookingForForecasting() - 1), getCurrentTick(), False)
        #     gtr = GeometricTrendRegression()
        #     for clearingPoint in cps:
        #         gtr.addData(clearingPoint.getTime(), clearingPoint.getPrice())
        #     expectedFuelPrices.update({substance: gtr.predict(futureTimePoint)})
        return expectedFuelPrices

    #    @RelatedTo(type = "PRODUCER_INVESTMENTROLE", elementClass = GenericInvestmentRole.class, direction = Direction.OUTGOING)
    #    @RelatedTo(type = "INVESTOR_MARKET", elementClass = ElectricitySpotMarket.class, direction = Direction.OUTGOING)
    #    @SimulationParameter(label = "Price Mark-Up for spotmarket (as multiplier)", from = 1, to = 2)
    #    @SimulationParameter(label = "Long-term contract margin", from = 0, to = 1)
    #    @SimulationParameter(label = "Long-term contract horizon", from = 0, to = 10)
    #Investment
    #    @SimulationParameter(label = "Investment horizon", from = 0, to = 15)
    #    @SimulationParameter(label = "Equity Interest Rate", from = 0, to = 1)
    #    @SimulationParameter(label = "Debt ratio in investments", from = 0, to = 1)
    # Loan
    #    @SimulationParameter(label = "Loan Interest Rate", from = 0, to = 1)



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

    def getPastTimeHorizon(self):
        return self.pastTimeHorizon

    def setPastTimeHorizon(self, pastTimeHorizon):
        self.pastTimeHorizon = pastTimeHorizon

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

    def getInvestmentFutureTimeHorizon(self):
        return self.investmentFutureTimeHorizon

    def setInvestmentFutureTimeHorizon(self, investmentFutureTimeHorizon):
        self.investmentFutureTimeHorizon = investmentFutureTimeHorizon

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
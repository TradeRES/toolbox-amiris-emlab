from emlabpy.domain.import_object import *

class EnergyProducer(ImportObject):
    def __init__(self, name):
        super().__init__(name)
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
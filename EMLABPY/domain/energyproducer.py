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

    def determineLoanAnnuities(self, totalLoan, payBackTime, interestRate):
        q = 1 + interestRate
        annuity = totalLoan * (q ** payBackTime * (q - 1)) / (q ** payBackTime - 1)
        return annuity
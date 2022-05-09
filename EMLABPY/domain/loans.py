
"""
This file contains Loans
"""
import numpy_financial as npf

class Loan:
    def __init__(self):
        self.from_agent = None
        self.to = None
        self.regardingPowerPlant = None
        self.amountPerPayment = 0
        self.totalNumberOfPayments = 0
        self.numberOfPaymentsDone = 0
        self.loanStartTime = 0

    #    @RelatedTo(type = "LEND_TO_AGENT", elementClass = EMLabAgent.class, direction = Direction.OUTGOING)
    #    @RelatedTo(type = "LEND_BY_AGENT", elementClass = EMLabAgent.class, direction = Direction.OUTGOING)
    #    @RelatedTo(type = "LOAN_POWERPLANT", elementClass = PowerPlant.class, direction = Direction.OUTGOING)

    def determineLoanAnnuities(self, totalLoan, payBackTime, interestRate):
        annuity = npf.pmt(interestRate, payBackTime, totalLoan, fv=0, when='end')
#        annuity_like_emlab = (totalLoan * interestRate) / (1 - ((1+interestRate)**(-interestRate)))
        return annuity

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
        return self.from_agent

    def setFrom(self, from_agent):
        self.from_agent = from_agent

    def getTo(self):
        return self.to

    def setTo(self, to):
        self.to = to

    def getRegardingPowerPlant(self):
        return self.regardingPowerPlant

    def setRegardingPowerPlant(self, regardingPowerPlant):
        self.regardingPowerPlant = regardingPowerPlant


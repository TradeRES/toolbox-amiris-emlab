
"""
This file contains Loans
"""


class Loan:
    def __init__(self):
        self.from_agent = ""
        self.to = ""
        self.regardingPowerPlant = None
        self.amountPerPayment = None
        self.totalNumberOfPayments = 0
        self.numberOfPaymentsDone = 0
        self.loanStartTick = 0

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        setattr(self, parameter_name, parameter_value)


    def getLoanStartTime(self):
        return self.loanStartTick

    def setLoanStartTime(self, loanStartTime):
        self.loanStartTick = loanStartTime

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


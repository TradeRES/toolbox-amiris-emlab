from domain.cashflow import CashFlow
from modules.defaultmodule import DefaultModule
from util.repository import Repository
from domain.loans import Loan
import logging

class PayForLoansRole(DefaultModule):

    def __init__(self, reps: Repository):
        super().__init__('pay Loans', reps)

    def act(self, producer):

        for plant in self.reps.get_power_plants_by_owner(producer):
            loan = plant.getLoan()
            if loan is not None:
                logging.info("Found a loan: %s " ,loan)
                if loan.getNumberOfPaymentsDone() < loan.getTotalNumberOfPayments():
                    payment = loan.getAmountPerPayment()
                                        #   ( from_agent, to,       amount,   type,         time,                     plant)
                    self.reps.createCashFlow(producer, loan.getTo(), payment, CashFlow.LOAN, self.reps.current_tick, loan.getRegardingPowerPlant())

                    loan.setNumberOfPaymentsDone(loan.getNumberOfPaymentsDone() + 1)

                    logging.info("Paying {0} (euro) for loan {1}".format(payment, loan))
                    logging.info("Number of payments done {0}, total needed: {1}".format( loan.getNumberOfPaymentsDone(), loan.getTotalNumberOfPayments()))

            downpayment = plant.getDownpayment()
            if downpayment is not None:
                logging.info("Found downpayment")
                if downpayment.getNumberOfPaymentsDone() < downpayment.getTotalNumberOfPayments():
                    payment = downpayment.getAmountPerPayment()
                    self.reps.createCashFlow(producer, downpayment.getTo(), payment, CashFlow.DOWNPAYMENT, self.reps.current_tick, downpayment.getRegardingPowerPlant())
                    downpayment.setNumberOfPaymentsDone(downpayment.getNumberOfPaymentsDone() + 1)
                    logging.info( "Paying {0} (euro) for downpayment {1}".format(payment, downpayment))
                    logging.info("Number of payments done {0}, total needed: {1}".format(downpayment.getNumberOfPaymentsDone(), downpayment.getTotalNumberOfPayments()))

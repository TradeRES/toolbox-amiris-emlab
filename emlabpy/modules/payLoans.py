from domain.cashflow import CashFlow
from modules.defaultmodule import DefaultModule
from util import globalNames
from util.repository import Repository
from domain.loans import Loan
import logging

class PayForLoansRole(DefaultModule):

    def __init__(self, reps: Repository):
        super().__init__('pay Loans', reps)
        reps.dbrw.stage_init_loans_structure()
        self.agent = reps.energy_producers[reps.agent]

    def act(self):
        for plant in self.reps.get_power_plants_by_owner(self.agent.name):
            if plant.status == globalNames.power_plant_status_decommissioned:
                pass
            else:
                # laons are paid only when the power plant is installed
                if plant.age >= 0 :
                    loan = plant.getLoan()
                    if loan is not None:
                        if loan.getNumberOfPaymentsDone() < loan.getTotalNumberOfPayments():
                            payment = loan.getAmountPerPayment()
                                                #   createCashFlow(  from_agent: object, to: object, amount, type, time, plant):
                            self.reps.createCashFlow(plant , self.reps.bigBank , payment, globalNames.CF_LOAN, self.reps.current_tick, loan.getRegardingPowerPlant())
                            loan.setNumberOfPaymentsDone(loan.getNumberOfPaymentsDone() + 1)
                            plant.loan_payments_in_year += payment
                            self.reps.dbrw.set_number_loan_payments(plant)

                            # print("Paying {0} (euro) for loan {1}".format(payment, plant.name))
                            # print("Number of payments done {0}, total needed: {1}".format( loan.getNumberOfPaymentsDone(), loan.getTotalNumberOfPayments()))
                else:
                    downpayment = plant.getDownpayment()
                    if downpayment is not None:
                        if downpayment.getNumberOfPaymentsDone() < downpayment.getTotalNumberOfPayments():
                            payment = downpayment.getAmountPerPayment()
                            self.reps.createCashFlow(plant, self.reps.manufacturer , payment, globalNames.CF_DOWNPAYMENT, self.reps.current_tick, downpayment.getRegardingPowerPlant())
                            downpayment.setNumberOfPaymentsDone(downpayment.getNumberOfPaymentsDone() + 1)
                            self.reps.dbrw.set_number_downpayments(plant)
                            plant.loan_payments_in_year += payment
                            # print( "Paying {0} (euro) for downpayment {1}".format(payment, plant.name))
                            # print("Number of payments done {0}, total needed: {1}".format(downpayment.getNumberOfPaymentsDone(), downpayment.getTotalNumberOfPayments()))

                self.reps.dbrw.stage_cash_plant(plant)
        self.reps.dbrw.stage_cash_agent(self.agent)

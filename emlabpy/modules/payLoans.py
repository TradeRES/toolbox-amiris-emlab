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
                if plant.age >= 0:
                    loan = plant.getLoan()
                    if loan is not None:
                        if loan.getNumberOfPaymentsDone() < loan.getTotalNumberOfPayments():
                            payment = loan.getAmountPerPayment()
                            loan.setNumberOfPaymentsDone(loan.getNumberOfPaymentsDone() + 1)

                            if int(plant.name) > 100000:
                                self.agent.CF_LOAN_NEW_PLANTS -= payment
                            else:

                                self.agent.CF_LOAN -= payment

                            plant.loan_payments_in_year += payment
                            self.reps.dbrw.set_number_loan_payments(plant)
                            # print("Paying {0} (euro) for loan {1}".format(payment, plant.name))
                            # print("Number of payments done {0}, total needed: {1}".format( loan.getNumberOfPaymentsDone(), loan.getTotalNumberOfPayments()))
                else:
                    downpayment = plant.downpayment
                    if downpayment is not None:
                        if downpayment.getNumberOfPaymentsDone() < downpayment.getTotalNumberOfPayments():
                            # downpayment are made after the permit time
                            # print("--------------------------" + plant.name + " "+ plant.technology.name)
                            # print(plant.age)
                            # print(plant.technology.expected_permittime)
                            # print(plant.technology.expected_leadtime)

                            if - plant.getActualLeadtime() <= plant.age:
                                payment = downpayment.getAmountPerPayment()
                                downpayment.setNumberOfPaymentsDone(downpayment.getNumberOfPaymentsDone() + 1)

                                if int(plant.name) > 100000:
                                    self.agent.CF_DOWNPAYMENT_NEW_PLANTS -= payment


                                else:
                                    self.agent.CF_DOWNPAYMENT -= payment
                                self.reps.dbrw.set_number_downpayments(plant)
                                plant.downpayment_in_year += payment
                            # print( "Paying {0} (euro) for downpayment {1}".format(payment, plant.name))
                            # print("Number of payments done {0}, total needed: {1}".format(downpayment.getNumberOfPaymentsDone(), downpayment.getTotalNumberOfPayments()))

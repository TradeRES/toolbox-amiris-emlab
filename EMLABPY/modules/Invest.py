# Determine for which assets there is enough budget to invest in
# budget is the sum of all cash flow
# it is the sum of the revenues minus the debt
# once an investment is done, decrease the amount from the investment budget
from emlabpy.domain.energyproducer import EnergyProducer
from emlabpy.domain.energy import PowerGeneratingTechnology
from emlabpy.modules.defaultmodule import DefaultModule

import numpy_financial as npf
from domain.energy import *
from domain.actors import *

from util.repository import Repository

from emlabpy.helpers.helper_functions import get_current_ticks
import sys

class Investmentdecision(DefaultModule):
    """
    The class that decides to invest in some technologies
    """

    def __init__(self, reps: Repository):
        super().__init__('EM-Lab Investment decisions', reps)
        self.expectedInstalledCapacityOfTechnology = 0
        self.expectedInstalledCapacityOfTechnologyInNode = 0
        # self.expectedOwnedTotalCapacityInMarket = 0
        # self.expectedOwnedCapacityInMarketOfThisTechnology = 0
        self.capacityOfTechnologyInPipeline = 0
        self.operationalCapacityOfTechnology = 0
        self.capacityInPipelineInMarket = 0
        self.viableInvestment = False
        self.technology = None
        self.plant = None
        # self.node = None
        # self.pgtNodeLimit = Double.MAX_VALUE
        #agent = ENERGY PRODUCER
        self.agent = "Producer1"
        self.budget_year0 = 0
        self.investmentCashFlow =[]

    def act(self):
        bestPlant = None
        highestValue = 0
        for candidatepowerplant in self.reps.get_candidate_power_plants_by_owner(self.agent):
            print(F"{self.agent} invests in technology at tick {self.reps.current_tick}")
            agent = self.reps.energy_producers[self.agent]
            projectvalue = getProjectValue(self, candidatepowerplant, agent)
            print("projectvalue", projectvalue)
            if projectvalue > 0 and ((projectvalue / candidatepowerplant.capacity) > highestValue):
                highestValue = projectvalue / candidatepowerplant.capacity
                bestPlant = candidatepowerplant
        print("bestPlant is " , bestPlant )

def getProjectValue(self, candidatepowerplant,agent):
    technology = self.reps.power_generating_technologies[candidatepowerplant.technology]
    totalInvestment = getActualInvestedCapital(self, candidatepowerplant, technology)
    depriacationTime = technology.depreciation_time
    interestRate = technology.interest_rate
    buildingTime = technology.expected_leadtime
    operatingProfit = candidatepowerplant.get_Profit()
    return calculateDiscountedCashFlowForPlant(self, depriacationTime, buildingTime, totalInvestment, operatingProfit, agent)

def calculateDiscountedCashFlowForPlant(self, depriacationTime, buildingTime, totalInvestment, operatingProfit,agent):
    wacc = (1 - agent.debtRatioOfInvestments) * agent.equityInterestRate \
           + agent.debtRatioOfInvestments * agent.loanInterestRate
    equalTotalDownPaymentInstallement = totalInvestment / buildingTime
    investmentCashFlow = [0 for i in range(depriacationTime + buildingTime)]
    for i in range(0, buildingTime):
        investmentCashFlow[i] = - equalTotalDownPaymentInstallement
    for i in range(buildingTime, depriacationTime + buildingTime):
        investmentCashFlow[i] = operatingProfit
    discountedprojectvalue = npf.npv(wacc, investmentCashFlow)
    return discountedprojectvalue


def getActualInvestedCapital(self, candidatepowerplant, technology):
    investmentCostperTechnology = technology.investment_cost
    investmentCostperMW = getinvestmentcosts(investmentCostperTechnology, (technology.expected_permittime + technology.expected_leadtime))
    return  investmentCostperMW * candidatepowerplant.capacity

def getinvestmentcosts(investmentCostperTechnology,time):
    return pow(1.05, time) * investmentCostperTechnology

def isViableInvestment(self):
    return viableInvestment

def setViableInvestment(self, viableInvestment):
    self.viableInvestment = viableInvestment

# def createCashFlow(agent, manufacturer, paymentperyear, CashFlow.DOWNPAYMENT, getCurrentTick(), plant):
#     pass



def checkAllBudget(downPayment, budget, year):

    if year == 1:
        budget_number = budget + budget_year0
        budget_number = budget_number - df_debt.loc[year].sum()
    else:
        budget_number += budget
        tot_debt = sum(df_debt.sum(1))
        if tot_debt > 0:
            budget_number = budget_number - df_debt.loc[year].sum()
    return budget_number

def createSpreadOutDownPayments(agent, downPayment, plant):
    buildingTime = plant.actualLeadtime()
    getReps().createCashFlow(agent,  totalDownPayment / buildingTime, CashFlow.DOWNPAYMENT, getCurrentTick(), plant)
    downpayment = getReps().createLoan(agent, manufacturer, totalDownPayment / buildingTime, buildingTime - 1, getCurrentTick(), plant)
    plant.createOrUpdateDownPayment(downpayment)


    def check(self):
        if (expectedInstalledCapacityOfTechnology + plant.actualNominalCapacity) / (marketInformation.maxExpectedLoad + self.plant.actualNominalCapacity) \
                > self.technology.maximumInstalledCapacityFractionInCountry:
            print(" will not invest in {} technology because there's too much of this type in the market")
    #
            # elif (expectedInstalledCapacityOfTechnologyInNode + plant.getActualNominalCapacity()) > pgtNodeLimit:
            #     pass
            # elif expectedOwnedCapacityInMarketOfThisTechnology > expectedOwnedTotalCapacityInMarket * technology.getMaximumInstalledCapacityFractionPerAgent():
            #     #logger.log(Level.FINER, agent + " will not invest in {} technology because there's too much capacity planned by him", technology)
            # elif capacityInPipelineInMarket > 0.2 * marketInformation.maxExpectedLoad:
            #     #logger.log(Level.FINER, "Not investing because more than 20% of demand in pipeline.")
            # elif (capacityOfTechnologyInPipeline > 2.0 * operationalCapacityOfTechnology) and capacityOfTechnologyInPipeline > 9000:
            #     #logger.log(Level.FINER, agent +" will not invest in {} technology because there's too much capacity in the pipeline", technology)
            # elif plant.getActualInvestedCapital() * (1 - agent.getDebtRatioOfInvestments()) > agent.getDownpaymentFractionOfCash() * agent.getCash():
            #     #logger.log(Level.FINER, agent +" will not invest in {} technology as he does not have enough money for downpayment", technology)
        else:
            print( technology + " passes capacity limit. " + agent + " will now calculate financial viability.")
            self.setViableInvestment(True)
        #         * Return true if the checks in this class have all been passed.
        #         * This means that future capacity expansion is viable.

    # projectValue = calculateProjectValue();
    # projectCost = calculateProjectCost();
    #
    # discountedCapitalCosts = calculateDiscountedCashFlowForPlant(
    #     technology.getDepreciationTime(), plant.getActualInvestedCapital(), 0)
    #
    # calculateDiscountedOperatingProfit
    # operatingProfit = expectedGrossProfit - fixedOMCost
    # discountedOperatingProfit = calculateDiscountedCashFlowForPlant(
#     technology.getDepreciationTime(), 0, operatingProfit)
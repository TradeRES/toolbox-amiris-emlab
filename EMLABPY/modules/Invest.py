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
    #technology = self.reps.power_generating_technologies[candidatepowerplant.technology]
    technology = candidatepowerplant.technology
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


class FutureCapacityExpectation(Investmentdecision):

    def __init__(self, technology, plant):
        super().__init__(technology, plant)
        #instance fields found by Java to Python Converter:
        self.technology = technology
        self.plant = plant
        self.node = "DE"
        self.expectedInstalledCapacityOfTechnology = 0
        self.expectedInstalledCapacityOfTechnologyInNode = 0
        self.expectedOwnedTotalCapacityInMarket = 0
        self.expectedOwnedCapacityInMarketOfThisTechnology = 0
        self.capacityOfTechnologyInPipeline = 0
        self.operationalCapacityOfTechnology = 0
        self.capacityInPipelineInMarket = 0
        self.viableInvestment = False

    def findLimitsByTechnologyAndNode():
        LimitinCountry = self.technology.maximum_installed_capacity_fraction_in_country
        if LimitinCountry:
            return LimitinCountry
        else:
            return None

    def act(self):
        self.findLimitsByTechnologyAndNode()

        self.expectedInstalledCapacityOfTechnology = getReps().calculateCapacityOfExpectedOperationalPowerPlantsInMarketAndTechnology(market, technology, futureTimePoint)

        technologyTarget = getReps().findPowerGeneratingTechnologyTargetByTechnologyAndMarket(technology, market)
        if technologyTarget is not None:
            technologyTargetCapacity = technologyTarget.getTrend().getValue(futureTimePoint)
            self.expectedInstalledCapacityOfTechnology = technologyTargetCapacity if (technologyTargetCapacity > self.expectedInstalledCapacityOfTechnology) else self.expectedInstalledCapacityOfTechnology


        self.expectedInstalledCapacityOfTechnologyInNode = getReps().calculateCapacityOfExpectedOperationalPowerPlantsByNodeAndTechnology(plant.getLocation(),technology, futureTimePoint)

        self.expectedOwnedTotalCapacityInMarket = getReps().calculateCapacityOfExpectedOperationalPowerPlantsInMarketByOwner(market, futureTimePoint, agent)

        self.expectedOwnedCapacityInMarketOfThisTechnology = getReps().calculateCapacityOfExpectedOperationalPowerPlantsInMarketByOwnerAndTechnology(market, technology, futureTimePoint, agent)

        self.capacityOfTechnologyInPipeline = getReps().calculateCapacityOfPowerPlantsByTechnologyInPipeline(technology, getCurrentTick())

        self.operationalCapacityOfTechnology = getReps().calculateCapacityOfOperationalPowerPlantsByTechnology(technology, getCurrentTick())

        self.capacityInPipelineInMarket = getReps().calculateCapacityOfPowerPlantsByMarketInPipeline(market, getCurrentTick())


        self.check()



#Returns the Node Limit by Technology or the max double numer if none was found

    def calculateNodeLimit(self):

        pgtLimit = getReps().findOneByTechnologyAndNode(self.technology, self.node)
        if pgtLimit is not None:
            self.pgtNodeLimit = pgtLimit.getUpperCapacityLimit(futureTimePoint)

    #         * Checks if future capacity expansion is viable.

    def check(self):

        if (self.expectedInstalledCapacityOfTechnology + self.plant.getActualNominalCapacity()) / (marketInformation.maxExpectedLoad + self.plant.getActualNominalCapacity()) > self.technology.getMaximumInstalledCapacityFractionInCountry():
            logger.log(Level.FINER, agent + " will not invest in {} technology because there's too much of this type in the market", self.technology)
        elif (self.expectedInstalledCapacityOfTechnologyInNode + self.plant.getActualNominalCapacity()) > self.pgtNodeLimit:
            pass
        elif self.expectedOwnedCapacityInMarketOfThisTechnology > self.expectedOwnedTotalCapacityInMarket * self.technology.getMaximumInstalledCapacityFractionPerAgent():
            logger.log(Level.FINER, agent + " will not invest in {} technology because there's too much capacity planned by him", self.technology)
        elif self.capacityInPipelineInMarket > 0.2 * marketInformation.maxExpectedLoad:
            logger.log(Level.FINER, "Not investing because more than 20% of demand in pipeline.")

        elif (self.capacityOfTechnologyInPipeline > 2.0 * self.operationalCapacityOfTechnology) and self.capacityOfTechnologyInPipeline > 9000:
            logger.log(Level.FINER, agent +" will not invest in {} technology because there's too much capacity in the pipeline", self.technology)

        elif self.plant.getActualInvestedCapital() * (1 - agent.getDebtRatioOfInvestments()) > agent.getDownpaymentFractionOfCash() * agent.getCash():
            logger.log(Level.FINER, agent +" will not invest in {} technology as he does not have enough money for downpayment", self.technology)

        else:

            logger.log(Level.FINER, self.technology + " passes capacity limit. " + agent + " will now calculate financial viability.")
            self.setViableInvestment(True)





    #        *
    #         * Return true if the checks in this class have all been passed.
    #         * This means that future capacity expansion is viable.
    #         * @return
    #
    def isViableInvestment(self):
        return self.viableInvestment


    def setViableInvestment(self, viableInvestment):
        self.viableInvestment = viableInvestment

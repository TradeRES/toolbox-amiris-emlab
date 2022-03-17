# Determine for which assets there is enough budget to invest in
# budget is the sum of all cash flow
# it is the sum of the revenues minus the debt
# once an investment is done, decrease the amount from the investment budget
from emlabpy.domain.energyproducer import EnergyProducer
from emlabpy.domain.technologies import PowerGeneratingTechnology
from emlabpy.modules.defaultmodule import DefaultModule
from emlabpy.domain.trends import GeometricTrendRegression
from emlabpy.domain.powerplant import *
from emlabpy.domain.CandidatePowerPlant import *
import numpy_financial as npf

from domain.actors import *
from util.repository import Repository
from emlabpy.helpers.helper_functions import get_current_ticks
import sys
import logging

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
        self.investmentCashFlow =[]
        # self.node = None
        # self.pgtNodeLimit = Double.MAX_VALUE
# from AbstractInvestInPowerGenerationTechnologiesRole
        self.useFundamentalCO2Forecast = False
        self.futureTimePoint = 0
        self.futureInvestmentyear = 0
        self.market = None
        self.marketInformation = None
        self.agent = None
        self.budget_year0 = 0

    def act(self):
        self.setAgent( "Producer1")
        self.setTimeHorizon()
        for candidatepowerplant in self.reps.get_candidate_power_plants_by_owner(self.agent.name):
            #TODO finalize
            #self.setPowerPlantExpectations(candidatepowerplant,self.futureTimePoint )
            futurecapacity = FutureCapacityExpectation(self.reps)
            futurecapacity.calculate(candidatepowerplant)

        bestPlant = None
        highestValue = 0
        for candidatepowerplant in self.reps.get_candidate_power_plants_by_owner(self.agent.name):
            print(F"{self.agent} invests in technology at tick {self.reps.current_tick}")
            agent = self.reps.energy_producers[self.agent]
            projectvalue = self.getProjectValue( candidatepowerplant, agent)
            print("projectvalue", projectvalue)
            if projectvalue > 0 and ((projectvalue / candidatepowerplant.capacity) > highestValue):
                highestValue = projectvalue / candidatepowerplant.capacity
                bestPlant = candidatepowerplant
        print("bestPlant is " , bestPlant )

    def setTimeHorizon(self):
        self.futureTimePoint = self.reps.current_tick + self.agent.getInvestmentFutureTimeHorizon()
        self.futureInvestmentyear = self.reps.start_simulation_year + self.futureTimePoint

    def getProjectValue(self, candidatepowerplant,agent):
        #technology = self.reps.power_generating_technologies[candidatepowerplant.technology]
        technology = candidatepowerplant.technology
        totalInvestment = self.getActualInvestedCapital( candidatepowerplant, technology)
        depriacationTime = technology.depreciation_time
        interestRate = technology.interest_rate
        buildingTime = technology.expected_leadtime
        operatingProfit = candidatepowerplant.get_Profit()
        return self.calculateDiscountedCashFlowForPlant( depriacationTime, buildingTime, totalInvestment, operatingProfit, agent)

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
        investmentCostperMW = self.getinvestmentcosts(investmentCostperTechnology, (technology.expected_permittime + technology.expected_leadtime))
        return  investmentCostperMW * candidatepowerplant.capacity

    def getinvestmentcosts(self, investmentCostperTechnology,time):
        return pow(1.05, time) * investmentCostperTechnology

    def checkAllBudget(self, downPayment, budget, year):
        if year == 1:
            budget_number = budget + budget_year0
            budget_number = budget_number - df_debt.loc[year].sum()
        else:
            budget_number += budget
            tot_debt = sum(df_debt.sum(1))
            if tot_debt > 0:
                budget_number = budget_number - df_debt.loc[year].sum()
        return budget_number

    def createSpreadOutDownPayments(self, agent, downPayment, plant):
        buildingTime = plant.actualLeadtime()
        getReps().createCashFlow(agent,  totalDownPayment / buildingTime, CashFlow.DOWNPAYMENT, getCurrentTick(), plant)
        downpayment = getReps().createLoan(agent, manufacturer, totalDownPayment / buildingTime, buildingTime - 1, getCurrentTick(), plant)
        plant.createOrUpdateDownPayment(downpayment)

    def setPowerPlantExpectations(self, powerplant, time):
        powerplant.calculate_marginal_fuel_cost_per_mw_by_tick(self.reps, time)

    def findAllClearingPointsForSubstanceAndTimeRange( self, substance,  timeFrom, timeTo):
        pass

    def getAgent(self):
        return self.agent

    def setAgent(self, agent):
        self.agent = self.reps.energy_producers[agent]

    #	 * Returns the tick for which the investor currently evaluates the technology
    def getFutureTimePoint(self):
        return futureTimePoint

    def setFutureTimePoint(self, futureTimePoint):
        self.futureTimePoint = futureTimePoint

    def isUseFundamentalCO2Forecast(self):
        return useFundamentalCO2Forecast

    def setUseFundamentalCO2Forecast(self, useFundamentalCO2Forecast):
        self.useFundamentalCO2Forecast = useFundamentalCO2Forecast

    def getMarket(self):
        return self.market

    def setMarket(self, market):
        self.market = market

    def getMarketInformation(self):
        return marketInformation

    def setMarketInformation(self, marketInformation):
        self.marketInformation = marketInformation

class FutureCapacityExpectation(Investmentdecision):
    def __init__(self, reps):
        super().__init__(reps)
        # self.technology = technology
        # self.plant = plant
        # self.location = None
        self.expectedInstalledCapacityOfTechnology = 0
        self.expectedInstalledCapacityOfTechnologyInNode = 0
        self.expectedOwnedTotalCapacityInMarket = 0
        self.expectedOwnedCapacityInMarketOfThisTechnology = 0
        self.capacityOfTechnologyInPipeline = 0
        self.operationalCapacityOfTechnology = 0
        self.capacityInPipelineInMarket = 0
        self.reps = reps

    def findLimitsByTechnologyAndNode(self, candidatepowerplant):
        LimitinCountry = candidatepowerplant.technology.maximum_installed_capacity_fraction_in_country
        if LimitinCountry:
            return LimitinCountry
        else:
            return None

    def calculate(self, candidatepowerplant):
            CandidatePowerPlant.specifyTemporaryPowerPlant(candidatepowerplant, self.reps.current_year, self.agent, "DE")
            print(candidatepowerplant)
            self.findLimitsByTechnologyAndNode(candidatepowerplant)
            self.expectedInstalledCapacityOfTechnology = self.reps.calculateCapacityOfExpectedOperationalPowerPlantsperTechnology(candidatepowerplant.technology, self.futureInvestmentyear)

        # technologyTarget = self.reps.findPowerGeneratingTechnologyTargetByTechnologyAndMarket(technology, market)
        # if technologyTarget is not None:
        #     technologyTargetCapacity = technologyTarget.getTrend().getValue(futureTimePoint)
        #     self.expectedInstalledCapacityOfTechnology = technologyTargetCapacity if (technologyTargetCapacity > self.expectedInstalledCapacityOfTechnology) else self.expectedInstalledCapacityOfTechnology
        # #
        # self.expectedInstalledCapacityOfTechnologyInNode = self.reps.calculateCapacityOfExpectedOperationalPowerPlantsByNodeAndTechnology(plant.getLocation(),technology, futureTimePoint)
        #
        # self.expectedOwnedTotalCapacityInMarket = self.reps.calculateCapacityOfExpectedOperationalPowerPlantsInMarketByOwner(market, futureTimePoint, agent)
        #
        # self.expectedOwnedCapacityInMarketOfThisTechnology = self.reps.calculateCapacityOfExpectedOperationalPowerPlantsInMarketByOwnerAndTechnology(market, technology, futureTimePoint, agent)
        #
        # self.capacityOfTechnologyInPipeline = self.reps.calculateCapacityOfPowerPlantsByTechnologyInPipeline(technology, getCurrentTick())
        #
        # self.operationalCapacityOfTechnology = self.reps.calculateCapacityOfOperationalPowerPlantsByTechnology(technology, getCurrentTick())
        #
        # self.capacityInPipelineInMarket = self.reps.calculateCapacityOfPowerPlantsByMarketInPipeline(market, getCurrentTick())

        # self.check()



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

        elif self.getActualInvestedCapital(plant, technology) * (1 - agent.getDebtRatioOfInvestments()) > agent.getDownpaymentFractionOfCash() * agent.getCash():
            logger.log(Level.FINER, agent +" will not invest in {} technology as he does not have enough money for downpayment", self.technology)

        else:

            logger.log(Level.FINER, self.technology + " passes capacity limit. " + agent + " will now calculate financial viability.")
            self.setViableInvestment(True)

    def isViableInvestment(self):
        return self.viableInvestment


    def setViableInvestment(self, viableInvestment):
        self.viableInvestment = viableInvestment

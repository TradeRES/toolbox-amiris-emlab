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
        self.futureInvestmentyear = 0
        self.expectedCO2Price = None
        self.expectedFuelPrices = None
        self.expectedDemand = None
        self.market = None
        self.marketInformation = None
        self.agent = None
        self.budget_year0 = 0

    def prepare(self):
        setAgent(self, "Producer1")
        self.setTimeHorizon()
        self.setExpectations()
        self.createCandidatePowerPlants()

    def act(self):
        setAgent(self, "Producer1")

        for candidatepowerplant in self.reps.get_candidate_power_plants_by_owner(self.agent.name):
            #TODO finalize
            #setPowerPlantExpectations(self, candidatepowerplant,self.futureTimePoint )
            futurecapacity = FutureCapacityExpectation(self.reps)
            futurecapacity.calculate(candidatepowerplant)

        bestPlant = None
        highestValue = 0
        for candidatepowerplant in self.reps.get_candidate_power_plants_by_owner(self.agent.name):
            print(F"{self.agent} invests in technology at tick {self.reps.current_tick}")
            agent = self.reps.energy_producers[self.agent]
            projectvalue = getProjectValue(self, candidatepowerplant, agent)
            print("projectvalue", projectvalue)
            if projectvalue > 0 and ((projectvalue / candidatepowerplant.capacity) > highestValue):
                highestValue = projectvalue / candidatepowerplant.capacity
                bestPlant = candidatepowerplant
        print("bestPlant is " , bestPlant )




    def setTimeHorizon(self):
        self.futureTimePoint = self.reps.current_tick + self.agent.getInvestmentFutureTimeHorizon()
        logging.info(self.agent.name + " is considering investment with horizon "  + self.futureTimePoint)
        self.futureInvestmentyear = self.reps.start_simulation_year + self.futureTimePoint

    def setExpectations(self, substance):
        for substance in self.reps.substances:
            self.predictFuelPrices(substance)
        self.predictDemand()

    def predictFuelPrices(self, future_simulation_tick, substance):
        """
        """
        if self.reps.current_tick >= 2:
            self.expectedFuelPrices = self.predictFuelPrices(self.futureTimePoint)
            substance.expectedFuelPrices = GeometricTrendRegression.predict()
        else:
            xp = [20, 40]
            fp = [substance.initialprice2020, substance.initialprice2040]
            substance.expectedFuelPrices = np.interp(self.futureInvestmentyear - 2000, xp, fp)



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

def setPowerPlantExpectations(self, powerplant, time):
    powerplant.calculate_marginal_fuel_cost_per_mw_by_tick(self.reps, time)

def findAllClearingPointsForSubstanceAndTimeRange( substance,  timeFrom, timeTo):
    pass

def predictFuelPrices(self, agent, futureTimePoint):
    # Fuel Prices
    expectedFuelPrices = {}
    for substance in self.reps.substances:
        #Find Clearing Points for the last 5 years (counting current year as one of the last 5 years).
        cps = self.reps.findAllClearingPointsForSubstanceAndTimeRange(substance, self.reps.current_tick - (agent.getNumberOfYearsBacklookingForForecasting() - 1) , self.reps.current_tick, False)
        #Create regression object
        gtr = GeometricTrendRegression()
        for clearingPoint in cps:
            #logger.warn("CP {}: {} , in" + clearingPoint.getTime(), substance.getName(), clearingPoint.getPrice())
            gtr.addData(clearingPoint.getTime(), clearingPoint.getPrice())
        expectedFuelPrices.update({substance: gtr.predict(futureTimePoint)})
        #logger.warn("Forecast {}: {}, in Step " +  futureTimePoint, substance, expectedFuelPrices.get(substance))
    return expectedFuelPrices





#     if not useFundamentalCO2Forecast:
#         expectedCO2Price = determineExpectedCO2PriceInclTaxAndFundamentalForecast(futureTimePoint, agent.getNumberOfYearsBacklookingForForecasting(), 0, getCurrentTick())
#     else:
#         expectedCO2Price = determineExpectedCO2PriceInclTax(futureTimePoint, agent.getNumberOfYearsBacklookingForForecasting(), getCurrentTick())
#     expectedDemand = {}
#     for elm in getReps().electricitySpotMarkets:
#         gtr = GeometricTrendRegression()
#         time = getCurrentTick()
#         while time > getCurrentTick() - agent.getNumberOfYearsBacklookingForForecasting() and time >= 0:
#             gtr.addData(time, elm.getDemandGrowthTrend().getValue(time))
#             time = time - 1
#         expectedDemand.put(elm, gtr.predict(futureTimePoint))
#     marketInformation = MarketInformation(market, expectedDemand, expectedFuelPrices, expectedCO2Price.get(market).doubleValue(), futureTimePoint)


def getAgent(self):
    return agent

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
    return market

def setMarket(self, market):
    self.market = market

def getMarketInformation(self):
    return marketInformation

def setMarketInformation(self, marketInformation):
    self.marketInformation = marketInformation

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

        elif self.plant.getActualInvestedCapital() * (1 - agent.getDebtRatioOfInvestments()) > agent.getDownpaymentFractionOfCash() * agent.getCash():
            logger.log(Level.FINER, agent +" will not invest in {} technology as he does not have enough money for downpayment", self.technology)

        else:

            logger.log(Level.FINER, self.technology + " passes capacity limit. " + agent + " will now calculate financial viability.")
            self.setViableInvestment(True)

    def isViableInvestment(self):
        return self.viableInvestment


    def setViableInvestment(self, viableInvestment):
        self.viableInvestment = viableInvestment

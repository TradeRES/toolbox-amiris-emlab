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
from emlabpy.domain.cashflow import  CashFlow
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
        #self.expectedInstalledCapacityOfTechnologyInNode = 0
        # self.expectedOwnedCapacityInMarketOfThisTechnology = 0
        self.capacityOfTechnologyInPipeline = 0
        self.operationalCapacityOfTechnology = 0
        self.capacityInPipeline = 0
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
        reps.dbrw.stage_init_future_prices_structure()
        reps.dbrw.stage_init_power_plant_structure()

    def act(self):
        self.setAgent( "Producer1")
        self.setTimeHorizon()
        #TODO if there would be more agents, the future capacity should be analyzed per agent
        #for candidatepowerplant in self.reps.get_candidate_power_plants_by_owner(self.agent.name):
        bestCandidatePowerPlant = None
        highestValue = 0
        # calculate which is the power plant with the highest NPV
        for candidatepowerplant in self.reps.get_candidate_power_plants_by_owner(self.agent.name):
            print(F"{self.agent} invests in technology at tick {self.reps.current_tick}")
            self.calculateFutureCapacityExpectation(candidatepowerplant)

            projectvalue = self.getProjectValue( candidatepowerplant, self.agent)
            print("projectvalue", projectvalue)
            # TODO this is only to test
            bestCandidatePowerPlant = candidatepowerplant
            if projectvalue > 0 and ((projectvalue / candidatepowerplant.capacity) > highestValue):
                highestValue = projectvalue / candidatepowerplant.capacity
                bestCandidatePowerPlant = candidatepowerplant

        print("bestPlant is " , bestCandidatePowerPlant)

        if bestCandidatePowerPlant is not None:
            # investing in best candidate power plant
            newplant = self.invest(bestCandidatePowerPlant)
            self.reps.dbrw.stage_new_power_plant(newplant)

    def invest(self, bestCandidatePowerPlant):
        newplant = PowerPlant(bestCandidatePowerPlant.name) # the name of the candidate power plant was assigned as the next available id from the installed power plants
        newplant.specifyPowerPlant(self.reps.current_tick, self.reps.current_year, self.agent, self.reps.country, bestCandidatePowerPlant.capacity, bestCandidatePowerPlant.technology)
        print("{0} invests in technology {1} at tick {2}".format(self.agent, newplant.name , self.reps.current_tick))
        investmentCostPayedByEquity = newplant.getActualInvestedCapital() * (1 - self.agent.getDebtRatioOfInvestments())
        investmentCostPayedByDebt = newplant.getActualInvestedCapital() * self.agent.getDebtRatioOfInvestments()
        downPayment = investmentCostPayedByEquity
        bigbank = self.reps.bigBank
        manufacturer = self.reps.manufacturer
        self.createSpreadOutDownPayments(self.agent, manufacturer, downPayment, newplant)
        amount = self.determineLoanAnnuities(investmentCostPayedByDebt, newplant.getTechnology().getDepreciationTime(), self.agent.getLoanInterestRate())
        #(self, from_agent, to, amount, numberOfPayments, loanStartTime, plant):
        loan = self.reps.createLoan(self.agent, bigbank, amount, newplant.getTechnology().getDepreciationTime(), self.reps.current_tick, newplant)
        newplant.createOrUpdateLoan(loan)
        return newplant

    def setTimeHorizon(self):
        self.futureTimePoint = self.reps.current_tick + self.agent.getInvestmentFutureTimeHorizon()
        self.futureInvestmentyear = self.reps.start_simulation_year + self.futureTimePoint

    def getProjectValue(self, candidatepowerplant,agent):
        #technology = self.reps.power_generating_technologies[candidatepowerplant.technology]
        technology = candidatepowerplant.technology
        totalInvestment = self.getActualInvestedCapital( candidatepowerplant, technology)
        candidatepowerplant.InvestedCapital = totalInvestment

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

    # from MIDO
    # def checkAllBudget(self, downPayment, budget, year): # TODO check the budget of all power plants
    #     if year == 1:
    #         budget_number = budget + budget_year0
    #         budget_number = budget_number - df_debt.loc[year].sum()
    #     else:
    #         budget_number += budget
    #         tot_debt = sum(df_debt.sum(1))
    #         if tot_debt > 0:
    #             budget_number = budget_number - df_debt.loc[year].sum()
    #     return budget_number

    def createSpreadOutDownPayments(self, agent, manufacturer, totalDownPayment, plant):
        buildingTime = plant.getActualLeadtime()
        # one downpayment is done
        self.reps.createCashFlow(agent,  manufacturer, totalDownPayment / buildingTime, "DOWNPAYMENT", self.reps.current_tick, plant)
        downpayment = self.reps.createLoan(agent, manufacturer, totalDownPayment / buildingTime, buildingTime - 1, self.reps.current_tick, plant)
        # the rest of downpayments are scheduled
        plant.createOrUpdateDownPayment(downpayment)

    def determineLoanAnnuities(self, totalLoan, payBackTime, interestRate):
        annuity = -npf.pmt(interestRate, payBackTime, totalLoan, fv=0, when='end')
        annuitybyhand = (totalLoan * interestRate) / (1 - ((1+interestRate)**(-interestRate)))
        annuity = totalLoan * ((1+interestRate) ** payBackTime * (interestRate)) / ((1+interestRate) ** payBackTime - 1)
        print(annuitybyhand - annuity) # TODO check which one is correct
        return annuity

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
#
# class FutureCapacityExpectation():
#     def __init__(self, reps):
#         #super().__init__(reps)
#         self.expectedInstalledCapacityOfTechnology = 0
#         #self.expectedInstalledCapacityOfTechnologyInNode = 0
#         self.expectedOwnedCapacityInMarketOfThisTechnology = 0
#         self.capacityOfTechnologyInPipeline = 0
#         self.operationalCapacityOfTechnology = 0
#         self.capacityInPipelineInMarket = 0
#         self.reps = reps

    def calculateFutureCapacityExpectation(self, candidatepowerplant):
            # TODO the specification should have happened before
            CandidatePowerPlant.specifyTemporaryPowerPlant(candidatepowerplant, self.reps.current_year, self.agent, self.reps.node)
            print(candidatepowerplant)
            technology = candidatepowerplant.technology

            technologyCapacityLimit = self.findLimitsByTechnology(technology)
            self.expectedInstalledCapacityOfTechnology = \
                self.reps.calculateCapacityOfExpectedOperationalPowerPlantsperTechnology(technology, self.futureInvestmentyear)

            technologyTarget = self.reps.findPowerGeneratingTechnologyTargetByTechnology(technology)
            # TODO:This part considers that if technology is not covered by the subsidies, the government would add subsidies?....

            if technologyTarget is not None:
                technologyTargetCapacity = self.reps.trends[str(technologyTarget)].getValue(self.futureTimePoint)
                if (technologyTargetCapacity > self.expectedInstalledCapacityOfTechnology):
                    self.expectedInstalledCapacityOfTechnology = technologyTargetCapacity

            self.operationalCapacityOfTechnology = self.reps.calculateCapacityOfOperationalPowerPlantsByTechnology(technology)
            self.capacityOfTechnologyInPipeline = self.reps.calculateCapacityOfPowerPlantsByTechnologyInPipeline(technology)
            self.capacityInPipeline = self.reps.calculateCapacityOfPowerPlantsInPipeline()
            self.check(technology.name, candidatepowerplant)

    def check(self, technology, candidatepowerplant):
        if (self.capacityOfTechnologyInPipeline > 2.0 * self.operationalCapacityOfTechnology) and self.capacityOfTechnologyInPipeline > 9000:
            logging.info(" will not invest in {} technology because there's too much capacity in the pipeline", self.technology)
            self.setViableInvestment(False)
            return
            # TODO: add the maxExpected Load amd agent cash
        # elif (self.expectedInstalledCapacityOfTechnology + self.candidatepowerplant.getActualNominalCapacity()) / (marketInformation.maxExpectedLoad + self.plant.getActualNominalCapacity()) >\
        #         self.technology.getMaximumInstalledCapacityFractionInCountry():
        #     logging.info(" will not invest in {} technology because there's too much of this type in the market", technology)
        # if self.capacityInPipeline > 0.2 * marketInformation.maxExpectedLoad:
        #     logging.info( "Not investing because more than 20% of demand in pipeline.")
        # elif self.getActualInvestedCapital(plant, technology) * (1 - agent.getDebtRatioOfInvestments()) > agent.getDownpaymentFractionOfCash() * agent.getCash():
        #     logging.info(Lagent +" will not invest in {} technology as he does not have enough money for downpayment", self.technology)
        else:
            logging.info( technology , " passes capacity limit.  will now calculate financial viability.")
            self.setViableInvestment(True)
            return


    def findLimitsByTechnology(self, technology):
        LimitinCountry = technology.getMaximumCapacityinCountry()
        if LimitinCountry:
            return LimitinCountry
        else:
            return 100000000000 # if there is no declared limit, use a very high number

#Returns the Node Limit by Technology or the max double numer if none was found

    def calculateNodeLimit(self):
        pgtLimit = getReps().findOneByTechnologyAndNode(self.technology, self.node)
        if pgtLimit is not None:
            self.pgtNodeLimit = pgtLimit.getUpperCapacityLimit(futureTimePoint)


    def isViableInvestment(self):
        return self.viableInvestment


    def setViableInvestment(self, viableInvestment):
        self.viableInvestment = viableInvestment

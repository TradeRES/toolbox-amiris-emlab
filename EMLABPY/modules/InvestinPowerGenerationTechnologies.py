# Determine for which assets there is enough budget to invest in
# budget is the sum of all cash flow
# it is the sum of the revenues minus the debt
# once an investment is done, decrease the amount from the investment budget
from emlabpy.domain.actors import EnergyProducer
import numpy_financial as npf
from domain.energy import *
from domain.actors import *
from domain.reps import *
from util.repository import Repository


class AbstractInvestInPowerGenerationTechnologiesRole:
    def __init__(self, reps: Repository):
        #instance fields found by Java to Python Converter:
        self.__useFundamentalCO2Forecast = False
        self.futureTimePoint = 0
        self.__expectedCO2Price = None
        self.__expectedFuelPrices = None
        self.__expectedDemand = None
        self.__market = None
        self.marketInformation = None
        self.agent = None

class FutureCapacityExpectation:
    def _initialize_instance_fields(self, reps: Repository, market, agent):
        #instance fields found by Java to Python Converter:
        self.expectedInstalledCapacityOfTechnology = 0
        self.expectedInstalledCapacityOfTechnologyInNode = 0
        self.expectedOwnedTotalCapacityInMarket = 0
        self.expectedOwnedCapacityInMarketOfThisTechnology = 0
        self.capacityOfTechnologyInPipeline = 0
        self.operationalCapacityOfTechnology = 0
        self.capacityInPipelineInMarket = 0
        self.viableInvestment = False
        self.technology = None
        self.plant = None
        self.node = None
        self.pgtNodeLimit = Double.MAX_VALUE
        self.market = market
        #agent = ENERGY PRODUCER
        self.agent = agent
        self.budget_year0 = 0

    def __setTimeHorizon(self):
        futureTimePoint = getCurrentTick() + agent.getInvestmentFutureTimeHorizon()

    def invest(self, agent, plant):
        print(F"{agent} invests in technology {plant.getTechnology()} at tick {currentTick()}")
       # getReps().createPowerPlantFromPlant(plant)
       # myFuelPrices = {}
       # for fuel in plant.getTechnology().getFuels():
       #     myFuelPrices.update({fuel: expectedFuelPrices.get(fuel)})
       # plant.setFuelMix(calculateFuelMix(plant, myFuelPrices, expectedCO2Price.get(market)))
        investmentCostPayedByEquity = plant.actualInvestedCapital * (1 - agent.debtRatioOfInvestments())
        investmentCostPayedByDebt = plant.actualInvestedCapital() * agent.debtRatioOfInvestments()
        downPayment = investmentCostPayedByEquity
        self.createSpreadOutDownPayments(agent, downPayment, plant)
        # depreciation time = payback time
        amount = plant.determineLoanAnnuities(investmentCostPayedByDebt, plant.technology.depreciationTime, agent.loanInterestRate())
        loan = getReps().createLoan(agent, amount, plant.technology().depreciationTime(), getCurrentTick(), plant)
        plant.createOrUpdateLoan(loan)
        #self.checkAllBudget(downPayment)

    def checkAllBudget(downPayment, budget, year):
        df_debt = pd.DataFrame()
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

    def isViableInvestment(self):
        return viableInvestment


    def setViableInvestment(self, viableInvestment):
        self.viableInvestment = viableInvestment


    def calculateDiscountedValues():
        discountedCapitalCosts = calculateDiscountedCapitalCosts()
        discountedOperatingCost = calculateDiscountedOperatingCost()
        discountedOperatingProfit = calculateDiscountedOperatingProfit()

    def calculateDiscountedCapitalCosts():
        depriacationTime
        totalInvestment
        operatingProfit
        wacc = (1 - agent.getDebtRatioOfInvestments()) * agent.getEquityInterestRate()
        + agent.getDebtRatioOfInvestments() * agent.getLoanInterestRate())


        equalTotalDownPaymentInstallement = totalInvestment / buildingTime
        for i in range(0, buildingTime):
            investmentCashFlow[i] = equalTotalDownPaymentInstallement
        for i in range(0, depriacationTime + buildingTime):
            investmentCashFlow[i] = operatingProfit

        npv = npf.npv(wacc, investmentCashFlow)
        return npv


    def calculateDiscountedOperatingCost():
        pass


    def calculateDiscountedOperatingProfit():
        pass


    def calculateSimplePowerPlantInvestmentCashFlow(self, depriacationTime, buildingTime, totalInvestment, operatingProfit):
        investmentCashFlow = {}
        equalTotalDownPaymentInstallement = totalInvestment / buildingTime
        for i in range(0, buildingTime):
            investmentCashFlow.update({i: -equalTotalDownPaymentInstallement})
        i = buildingTime
        while i < depriacationTime + buildingTime:
            investmentCashFlow.update({i: operatingProfit})
            i += 1
        return investmentCashFlow



    def createCashFlow(agent, manufacturer, paymentperyear, CashFlow.DOWNPAYMENT, getCurrentTick(), plant)




    def getActualInvestedCapital(plant):
        pass



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
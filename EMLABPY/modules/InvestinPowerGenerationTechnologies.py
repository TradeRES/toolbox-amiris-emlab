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
from spinedb import SpineDB
from emlabpy.helpers.helper_functions import get_current_ticks
import sys


class FutureCapacityExpectation:
    def _initialize_instance_fields(self, reps: Repository, market, agent):
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
        wacc = (1 - agent.getDebtRatioOfInvestments()) * agent.getEquityInterestRate() + agent.getDebtRatioOfInvestments() * agent.getLoanInterestRate()


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


    def createCashFlow(agent, manufacturer, paymentperyear, CashFlow.DOWNPAYMENT, getCurrentTick(), plant):
    pass

    def getActualInvestedCapital(plant):
        pass

def query_databases(db_amiris):
    """
    This function queries the databases and retrieves all necessary data.
    :param db_amiris: SpineDB Object of Amiris
    :return: the queried data
    """
    print('Querying databases...')
    ConventionalPlantOperator = db_amiris.query_object_parameter_values_by_object_class('ConventionalPlantOperator')
    VariableRenewableOperator = db_amiris.query_object_parameter_values_by_object_class('VariableRenewableOperator')
    StorageTrader = db_amiris.query_object_parameter_values_by_object_class('StorageTrader')
    # db_emlab_ppdps = db_emlab.query_object_parameter_values_by_object_class('PowerPlantDispatchPlans')
    print('Done')
    return ConventionalPlantOperator, VariableRenewableOperator, StorageTrader


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

def export_investment_decisions_to_emlab_and_competes(db_emlab,
                                                      new_generation_capacity_df,
                                                      db_amiris_technologies):
    """
    This function exports all Investment decisions.
    :param db_emlab: SpineDB
    :param db_competes: SpineDB
    :param new_generation_capacity_df: Dataframe of new generation capacity from COMPETES output
    """
    print('Exporting Investment Decisions to EMLAB ')
    for index, row in new_generation_capacity_df.iterrows():
        row = row.fillna(0)


        technology = next(name for name in db_amiris_technologies)
        expected_permit_time = next(int(i['parameter_value']) for i in db_emlab_technologies if i['object_name'] == technology and i['parameter_name'] == 'expectedPermittime')
        expected_lead_time = next(int(i['parameter_value']) for i in db_emlab_technologies if i['object_name'] == technology and i['parameter_name'] == 'expectedLeadtime')
        build_time = expected_permit_time + expected_lead_time
        online_in_year = build_time + currentyear

        print('Exporting to EM-Lab...')
        db_emlab.import_objects([('PowerPlants', plant_name), ('PowerPlants', plant_name_decom)])
        db_emlab.import_object_parameter_values(
            [('PowerPlants', plant_name, param_index, param_value, str(current_emlab_tick))
             for (param_index, param_value) in param_values_emlab] +
            [('PowerPlants', plant_name_decom, param_index, param_value, str(current_emlab_tick))
             for (param_index, param_value) in param_values_emlab_decom])

        print('Done exporting Investment Decisions to EMLAB and COMPETES')

def invest_BestTechnology():
    """
    This is the main invest function
    """
    print('Establishing Database Connections...')
    db_emlab = SpineDB(sys.argv[1])
    print('Done')
    try:
        print('Current EM-Lab tick: ' )
        ConventionalPlantOperator, VariableRenewableOperator, StorageTrader = query_databases(db_emlab)

        print('Once chose import into alternative new')


        export_investment_decisions_to_emlab_and_competes(db_emlab, db_competes, current_emlab_tick,
                                                          new_generation_capacity_df, current_competes_tick,
                                                          db_emlab_technologies, db_competes_new_technologies)

        export_decommissioning_decisions_to_emlab_and_competes(db_competes, db_emlab, db_competes_powerplants,
                                                               decommissioning_df, current_competes_tick,
                                                               current_emlab_tick, look_ahead)
        export_total_sum_exports_to_emlab(db_emlab, hourly_nl_balance_df, current_emlab_tick)
        export_yearly_emissions_to_emlab(db_emlab, yearly_emissions_df, current_emlab_tick)

        print('Committing...')
        db_emlab.commit('Imported from COMPETES run ' + str(current_competes_tick))
        print('Done')
    except Exception as e:
        print('Exception occurred: ' + str(e))
        raise
    finally:
        print('Closing database connection...')
        db_emlab.close_connection()
        db_competes.close_connection()
        db_config.close_connection()


if __name__ == "__main__":
    print('===== Starting Best investment script =====')
    invest_BestTechnology()
    print('===== End of Best investment script =====')

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
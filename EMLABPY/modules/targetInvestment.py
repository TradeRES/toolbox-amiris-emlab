from emlabpy.domain.powerplant import PowerPlant
from emlabpy.domain.targetinvestor import TargetInvestor
from emlabpy.modules.defaultmodule import DefaultModule
import logging
import time

class TargetInvestmentRole(DefaultModule):

    def __init__(self, reps):
        super().__init__('Investment decisions with target', reps)

    def act(self, targetInvestor):
        for target in targetInvestor.getPowerGenerationTechnologyTargets():
            pgt = target.getPowerGeneratingTechnology()
            futureTimePoint = self.reps.current_tick + pgt.getExpectedLeadtime() + pgt.getExpectedPermittime()
            expectedInstalledCapacity = self.reps.calculateCapacityOfExpectedOperationalPowerPlantsperTechnology( pgt, futureTimePoint)
            pgtNodeLimit = pgt.getMaximumCapacityinCountry()
            targetCapacity = target.getTrend().getValue(futureTimePoint)
            installedCapacityDeviation = 0
            if pgtNodeLimit > targetCapacity:
                installedCapacityDeviation = targetCapacity - expectedInstalledCapacity
            else:
                installedCapacityDeviation = pgtNodeLimit - expectedInstalledCapacity
            #if the target is lower than the physical limits
            if installedCapacityDeviation > 0 and installedCapacityDeviation > pgt.getCapacity():
                logging.info(targetInvestor + " needs to invest " + installedCapacityDeviation + " MW")
                capacity = pgt.getCapacity()
                powerPlantCapacityRatio = installedCapacityDeviation / capacity
                milli_sec = int(round(time.time() * 1000))
                newplant = PowerPlant(milli_sec)

                plant = PowerPlant.specifyPowerPlant(self.reps.current_tick, self.reps.current_year , targetInvestor, "DE", installedCapacityDeviation, pgt)
                #investmentCostPayedByEquity = plant.getActualInvestedCapital() * (1 - targetInvestor.getDebtRatioOfInvestments()) * powerPlantCapacityRatio
                #investmentCostPayedByDebt = plant.getActualInvestedCapital() * targetInvestor.getDebtRatioOfInvestments() * powerPlantCapacityRatio
                #downPayment = investmentCostPayedByEquity
                #self.__createSpreadOutDownPayments(targetInvestor, manufacturer, downPayment, plant)
                #amount = self.determineLoanAnnuities(investmentCostPayedByDebt, plant.getTechnology().getDepreciationTime(), targetInvestor.getLoanInterestRate())
                #loan = getReps().createLoan(targetInvestor, bigbank, amount, plant.getTechnology().getDepreciationTime(), getCurrentTick(), plant)
                #plant.createOrUpdateLoan(loan)


    #
    # def __createSpreadOutDownPayments(self, agent, manufacturer, totalDownPayment, plant):
    #     buildingTime = int(plant.getActualLeadtime())
    #     for i in range(0, buildingTime):
    #         getReps().createCashFlow(agent, manufacturer, totalDownPayment / buildingTime, emlab.gen.domain.contract.CashFlow.DOWNPAYMENT, getCurrentTick() + i, plant)
    #
    # def determineLoanAnnuities(self, totalLoan, payBackTime, interestRate):
    #     q = 1 + interestRate
    #     annuity = totalLoan * (q ** payBackTime * (q - 1)) / (q ** payBackTime - 1)
    #     return annuity

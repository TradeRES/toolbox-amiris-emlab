from domain.powerplant import PowerPlant
from domain.targetinvestor import TargetInvestor
from modules.defaultmodule import DefaultModule
import logging
import time

class TargetInvestmentRole(DefaultModule):

    def __init__(self, reps):
        super().__init__('Investment decisions with target', reps)

    def act(self, targetInvestor):
        for target in targetInvestor.getPowerGenerationTechnologyTargets():
            pgt = target.getPowerGeneratingTechnology()
            futureTimePoint = self.reps.current_tick + pgt.getExpectedLeadtime() + pgt.getExpectedPermittime()
            expectedInstalledCapacity = self.reps.calculateCapacityOfExpectedOperationalPlantsperTechnology(pgt, futureTimePoint)
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
                                                    #(self, tick, year, energyProducer, location, capacity, pgt)
                plant = PowerPlant.specifyPowerPlantforInvest(self.reps.current_tick, self.reps.current_year, targetInvestor, "DE", installedCapacityDeviation, pgt)


from domain.energyproducer import EnergyProducer
from domain.technologies import PowerGeneratingTechnology
from modules.Invest import Investmentdecision
from modules.defaultmodule import DefaultModule
import numpy_financial as npf

from domain.actors import *
from util.repository import Repository
from helpers.helper_functions import get_current_ticks
import sys
import logging
import pandas as pd


class ShortInvestmentdecision(Investmentdecision):
    """
    The class that decides to invest in some technologies according to last year simulation year results
    Short term invest is done to PV or batteries that are very profitable in the last years.
    """

    def __init__(self, reps: Repository):
        super().__init__( reps)
        self.quickInvestabletechnologies = ["PV_utility_systems", "PV_residential", "PV_commercial_systems", "Lithium_ion_battery"]

    def act(self):
        self.setAgent("Producer1")
        print(F"{self.agent} invests in technology at tick {self.reps.current_tick}")
        # TODO if there would be more agents, the future capacity should be analyzed per agent
        operationalInvestablePlants = self.reps.get_operational_power_plants_by_owner_and_technologies(self.agent.name, self.quickInvestabletechnologies)

        PowerPlantstoInvest = []
        technologies = []
        returns = []

        for powerplant in operationalInvestablePlants:
            # checks if the technology can be invested and if not it removes the technology from the investable technology list quick Investabletechnologies
            self.calculateandCheckFutureCapacityExpectation(powerplant.technology)
            # for now the returns calculations are done considering that future years will have the profit of the current year
            # TODO the profit should consider the past year profits?
            returns.append( self.calculatePowerPlantReturns(powerplant, self.agent))
            technologies.append(powerplant.technology.name)

        df = pd.DataFrame( technologies,returns, columns=["Technologies", "Returns"])
        sorted = df.groupby('Technologies').mean().sort_values(by=['Returns'])
        filteredReturns = sorted.drop(sorted[sorted.value < self.reps.short_term_investment_minimal_irr].index)
        technologies = filteredReturns.index.tolist()
        # TODO         newpowerplantname
        PowerPlantstoInvest.append([])

        newpowerplantname = 1
        if len(PowerPlantstoInvest) > 0:
            for planttoInvest in PowerPlantstoInvest:
                newplant = self.invest(planttoInvest, newpowerplantname)
                self.reps.dbrw.stage_new_power_plant(newplant)

    def calculateandCheckFutureCapacityExpectation(self, technology):
        technologyCapacityLimit = self.findLimitsByTechnology(technology)
        # in contrast to long term investment decision, this is calculated for the current year
        self.expectedInstalledCapacityOfTechnology = \
            self.reps.calculateCapacityOfExpectedOperationalCapacityperTechnology(technology,
                                                                                  self.reps.current_tick)
        technologyTarget = self.reps.findPowerGeneratingTechnologyTargetByTechnology(technology)
        # TODO:This part considers that if technology is not covered by the subsidies, the government would add subsidies?....
        # in contrast to long term investment decision, this is calculated for the current year
        if technologyTarget is not None:
            technologyTargetCapacity = self.reps.trends[str(technologyTarget)].getValue(self.reps.current_tick)
            if (technologyTargetCapacity > self.expectedInstalledCapacityOfTechnology):
                self.expectedInstalledCapacityOfTechnology = technologyTargetCapacity

        self.operationalCapacityOfTechnology = self.reps.calculateCapacityOfOperationalPowerPlantsByTechnology(
            technology)
        self.capacityOfTechnologyInPipeline = self.reps.calculateCapacityOfPowerPlantsByTechnologyInPipeline(technology)
        self.capacityInPipeline = self.reps.calculateCapacityOfPowerPlantsInPipeline()

        # the check is not done for candidate power plant, but for installed power plants
        if (self.capacityOfTechnologyInPipeline > 2.0 * self.operationalCapacityOfTechnology) and self.capacityOfTechnologyInPipeline > 9000:
            logging.info(" will not invest in {} technology because there's too much capacity in the pipeline", self.technology)
            # TODO: if the candidate power plants would be parallellized, setting this technology as not investable could that technology simulation
            self.quickInvestabletechnologies.remove(technology)
            return
            # TODO: add the maxExpected Load amd agent cash
        else:
            logging.info(technology, " passes capacity limit.  will now calculate financial viability.")

    def calculatePowerPlantReturns(self, powerplant, agent):
        technology = powerplant.technology
        totalInvestment = self.getActualInvestedCapitalperMW(powerplant, technology) * powerplant.capacity
        powerplant.InvestedCapital = totalInvestment
        depriaciationTime = technology.depreciation_time
        technical_lifetime = technology.expected_lifetime
        # interestRate = technology.interest_rate
        buildingTime = technology.expected_leadtime
        operatingProfit = powerplant.get_Profit() # Todo change this to the last 3 years????
        equalTotalDownPaymentInstallment = (totalInvestment* agent.debtRatioOfInvestments) / buildingTime
        restPayment = totalInvestment* (1-agent.debtRatioOfInvestments)/ technical_lifetime
        investmentCashFlow = [0 for i in range(depriaciationTime + buildingTime)]

        for i in range(0, buildingTime):
            investmentCashFlow[i] = - equalTotalDownPaymentInstallment
        for i in range(buildingTime, technical_lifetime + buildingTime):
            investmentCashFlow[i] = operatingProfit - restPayment

        internalRateReturn = npf.irr(investmentCashFlow, len(investmentCashFlow))
        return internalRateReturn

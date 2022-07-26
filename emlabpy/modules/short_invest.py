from modules.invest import Investmentdecision
import numpy_financial as npf
from util.repository import Repository
import logging

import pandas as pd

class ShortInvestmentdecision(Investmentdecision):
    """
    The class that decides to invest in some technologies according to last year simulation year results
    Short term invest is done to PV or batteries that are very profitable in the last years.
    """

    def __init__(self, reps: Repository):
        super().__init__(reps)
        self.quickInvestabletechnologies = ["PV_utility_systems",
                                            "Lithium_ion_battery"]  # later add  "PV_residential", "PV_commercial_systems",

        reps.dbrw.stage_init_power_plant_structure()
        reps.dbrw.stage_candidate_pp_investment_status_structure()

    def act(self):
        print(F"{self.agent.name} invests in technology at tick {self.reps.current_tick}")
        # TODO if there would be more agents, the future capacity should be analyzed per agent
        # checks if the technology technical limits are passed
        # if not it removes the technology from the list quick Investabletechnologies
        # and dont proceed with the returns calculation

        for quick_technology in self.quickInvestabletechnologies:
            self.calculateandCheckFutureCapacityExpectation(self.reps.power_generating_technologies[quick_technology])

            # the list is updated in the step before!!!!!!!!!!!
        technologies_highreturns =[]
        for quick_technology in self.quickInvestabletechnologies:
            operationalInvestablePlants = self.reps.get_operational_power_plants_by_owner_and_technologies(self.agent.name,
                                                                                                       quick_technology)
            # if the technology can be invested_in_iteration, then calculate the returns
            # TODO the profits should consider the past year profits?
            average_profit = self.reps.get_average_profits(operationalInvestablePlants)
            if pd.isna(average_profit):
                pass
            else:
                cashflow = self.getProjectCashFlow(self.reps.power_generating_technologies[quick_technology], average_profit,  self.agent)
                pp_return_per_tech = self.irr(cashflow)
                if pp_return_per_tech > self.reps.short_term_investment_minimal_irr:
                    technologies_highreturns.append(pp_return_per_tech)

        if len(technologies_highreturns) > 0:
            PowerPlantstoInvest = self.reps.get_candidate_power_plants_of_technologies(technologies_highreturns)
            for planttoInvest in PowerPlantstoInvest:
                new_plant = self.invest(planttoInvest)
                self.reps.dbrw.stage_new_power_plant(new_plant)

        else:
            print("no Investment in quick technologies ")

    def calculateandCheckFutureCapacityExpectation(self, technology):
        technologyCapacityLimit = self.findLimitsByTechnology(technology)
        # in contrast to long term investment decision, this is calculated for the current year
        self.expectedInstalledCapacityOfTechnology = self.reps.calculateCapacityOfExpectedOperationalPlantsperTechnology(
            technology,
            self.reps.current_tick + technology.expected_leadtime + technology.expected_permittime)
        self.operationalCapacityOfTechnology = self.reps.calculateCapacityOfOperationalPowerPlantsByTechnology(
            technology)
        self.capacityOfTechnologyInPipeline = self.reps.calculateCapacityOfPowerPlantsByTechnologyInPipeline(technology)

        # the check is not done for candidate power plant, but for installed power plants
        if (
                self.capacityOfTechnologyInPipeline > 2.0 * self.operationalCapacityOfTechnology) or self.capacityOfTechnologyInPipeline > 9000:
            logging.info(" will not invest in '%s  technology because there's too much capacity in the pipeline",
                         self.technology)
            self.quickInvestabletechnologies.remove(technology.name)
            return False
        elif self.expectedInstalledCapacityOfTechnology > technologyCapacityLimit:
            logging.info(" will not invest in '%s  technology because the capacity limits are achieved", technology)
            self.quickInvestabletechnologies.remove(technology.name)
            return False
        else:
            logging.info( " '%s passes capacity limit.  will now calculate financial viability.", technology)
            return True
            # TODO: add the maxExpected Load amd agent cash

    def irr(self, investmentCashFlow):
        IRR = npf.irr(investmentCashFlow)
        if pd.isna(IRR):
            return -100
        else:
             return round(IRR, 4)


    # Todo change this to the last 3 years profits ????
    def getProjectCashFlow(self, technology ,average_profit, agent):
        totalInvestment = self.getActualInvestedCapitalperMW( technology)
        depreciationTime = technology.depreciation_time
        technical_lifetime = technology.expected_lifetime
        buildingTime = technology.expected_leadtime
        # get average profits per technology
        operatingProfit = average_profit
        equalTotalDownPaymentInstallment = (totalInvestment * agent.debtRatioOfInvestments) / buildingTime
        restPayment = totalInvestment * (1 - agent.debtRatioOfInvestments) / technical_lifetime
        investmentCashFlow = [0 for i in range(technical_lifetime + buildingTime)]

        for i in range(0, buildingTime):
            investmentCashFlow[i] = - equalTotalDownPaymentInstallment
        for i in range(buildingTime, technical_lifetime + buildingTime):
            investmentCashFlow[i] = operatingProfit - restPayment
        return  investmentCashFlow


        # returns.append(pp_returns)
        # technologies.append(powerplant.technology.name)
        # # calculate returns per technology
        # df = pd.DataFrame(technologies, returns, columns=["Technologies", "Returns"])
        # sorted = df.groupby('Technologies').mean().sort_values(by=['Returns'])
        # filteredReturns = sorted.drop(sorted[sorted.value < self.reps.short_term_investment_minimal_irr].index)
        # technologies_highreturns = filteredReturns.index.tolist()
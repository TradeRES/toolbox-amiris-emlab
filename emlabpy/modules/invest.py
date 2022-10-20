from domain.energyproducer import EnergyProducer
from domain.technologies import PowerGeneratingTechnology
from modules.defaultmodule import DefaultModule
from domain.trends import GeometricTrendRegression
from domain.targetinvestor import TargetInvestor
from domain.powerplant import *
from domain.CandidatePowerPlant import *
from domain.cashflow import CashFlow
import numpy_financial as npf
import pandas as pd
from domain.actors import *
from util.repository import Repository
import os
import sys
import logging
import math
import csv
from datetime import datetime


class Investmentdecision(DefaultModule):
    """
    The class that decides to invest according to future dispatch results
    The results are not read from the DB, but from the csv to make faster simulations.
    """

    def __init__(self, reps: Repository):
        super().__init__('EM-Lab Investment decisions', reps)
        self.expectedInstalledCapacityPerTechnology = 0
        self.capacityOfTechnologyInPipeline = 0
        self.operationalCapacityOfTechnology = 0
        self.capacityInPipeline = 0
        self.investmentCashFlow = []
        self.useFundamentalCO2Forecast = False  # from AbstractInvestInPowerGenerationTechnologiesRole
        self.futureTick = 0  # future tick
        self.futureInvestmentyear = 0
        self.market = None
        self.marketInformation = None
        self.budget_year0 = 0
        self.continueInvestment = True
        # Attention!!! leave the order. -> agent> time horizon> init candidate power plants
        now = datetime.now()
        self.now = now.strftime("%H:%M:%S")
        self.setAgent(reps.agent)
        self.ids_of_future_installed_pp = []
        self.setTimeHorizon()
        self.wacc = (
                                1 - self.agent.debtRatioOfInvestments) * self.agent.equityInterestRate + self.agent.debtRatioOfInvestments * self.agent.loanInterestRate
        reps.dbrw.stage_init_candidate_plants_value(self.reps.investmentIteration, self.futureInvestmentyear)
        reps.dbrw.stage_init_investment_decisions(self.reps.investmentIteration, self.futureInvestmentyear)
        # new id = last installed id, plus the iteration
        self.new_id = int(reps.get_id_last_power_plant()) + 1
        self.investable_candidate_plants = []
        reps.dbrw.stage_init_loans_structure()
        reps.dbrw.stage_init_downpayments_structure()
        reps.dbrw.stage_init_alternative(reps.current_tick)
        reps.dbrw.stage_init_future_prices_structure()
        reps.dbrw.stage_init_power_plant_structure()
        reps.dbrw.stage_init_future_operational_profits()
        reps.dbrw.stage_candidate_pp_investment_status_structure()
        # self.expectedOwnedCapacityInMarketOfThisTechnology = 0

    def act(self):
        # this function adds         self.AwardedPowerinMWh = results.PRODUCTION_IN_MWH / self.CostsinEUR = results.VARIABLE_COSTS_IN_EURO /
        # self.ReceivedMoneyinEUR = results.REVENUES_IN_EURO and self.operationalProfit = results.CONTRIBUTION_MARGIN_IN_EURO from csv
        self.read_csv_results_and_filter_candidate_plants()
        pp_numbers = []
        pp_profits = []
        cp_numbers = []
        cp_profits = []
        # saving: operationalprofits from power plants in classname Profits
        # todo: this could be removel once the model is validated
        for pp_id in self.ids_of_future_installed_pp:
            pp = self.reps.get_power_plant_by_id(pp_id)
            pp_numbers.append(pp.name)
            pp_profits.append(pp.operationalProfit)
        self.reps.dbrw.stage_future_operational_profits_installed_plants(self.reps, pp_numbers, pp_profits)
        self.reps.dbrw.stage_iteration(self.reps.investmentIteration + 1)

        # save the iteration
        if self.agent.readytoInvest == True:  # todo this is also for now not active. Activate once the cash flow is not enough
            #  for now there is only one energyproducer
            bestCandidatePowerPlant = None
            highestValue = 0
            # power plants are investable when they havent passed the capacity limits
            self.investable_candidate_plants = self.reps.get_investable_candidate_power_plants()
            if self.investable_candidate_plants:  # check if the are investable power plants
                self.expectedInstalledCapacityPerTechnology = self.reps.calculateCapacityExpectedofListofPlants(
                    self.ids_of_future_installed_pp, self.investable_candidate_plants)

                for candidatepowerplant in self.investable_candidate_plants:
                    cp_numbers.append(candidatepowerplant.name)
                    cp_profits.append(candidatepowerplant.operationalProfit)
                    # calculate which is the power plant (technology) with the highest NPV
                    candidatepowerplant.specifyTemporaryPowerPlant(self.reps.current_year, self.agent,
                                                                   self.reps.country)
                    investable  = self.calculateandCheckFutureCapacityExpectation(candidatepowerplant
                                                                                 )
                    if investable == False:
                        candidatepowerplant.setViableInvestment(False)
                        logging.info("to much in pipeline of this technology%s", candidatepowerplant.technology)
                        # saving if the candidate power plant remains or not as investable
                        self.reps.dbrw.stage_candidate_pp_investment_status(candidatepowerplant)
                        break

                    cashflow = self.getProjectCashFlow(candidatepowerplant, self.agent)
                    projectvalue = self.npv(cashflow)

                    # saving the list of power plants values that have been candidates per investmentIteration.
                    self.reps.dbrw.stage_candidate_power_plants_value(candidatepowerplant.name, projectvalue,
                                                                      self.reps.investmentIteration,
                                                                      self.futureInvestmentyear,
                                                                      )
                    if projectvalue >= 0 and ((projectvalue / candidatepowerplant.capacity) > highestValue):
                        highestValue = projectvalue / candidatepowerplant.capacity  # capacity is anyways 1
                        bestCandidatePowerPlant = candidatepowerplant
                    elif projectvalue < 0:
                        # the power plant should not be investable in next rounds
                        # saving if the candidate power plant remains or not as investable
                        candidatepowerplant.setViableInvestment(False)
                        self.reps.dbrw.stage_candidate_pp_investment_status(candidatepowerplant)
                    else:
                        logging.info("dont invest in this technology%s", candidatepowerplant.technology)

                # saving: operational profits from candidate plants
                # todo?
                self.reps.dbrw.stage_candidate_plant_results(self.reps, cp_numbers, cp_profits)
                # if the power plant is correctly saved
                bestCandidatePowerPlant = None
                if bestCandidatePowerPlant is not None:
                    # investing in best candidate power plant as it passed the checks.
                    newplant = self.invest(bestCandidatePowerPlant)
                    self.reps.dbrw.stage_new_power_plant(newplant)
                    self.reps.dbrw.stage_loans(newplant)
                    self.reps.dbrw.stage_downpayments(newplant)
                    self.reps.dbrw.stage_investment_decisions(bestCandidatePowerPlant.name, newplant.name,
                                                              self.reps.investmentIteration,
                                                              self.futureInvestmentyear, self.reps.current_tick)
                    self.continue_iteration()
                    return
                else:

                    print("no more power plant to invest, saving loans, next iteration")
                    self.stop_iteration()
                    # saving iteration number back to zero for next year
                    self.reps.dbrw.stage_iteration(0)

                    if self.reps.targetinvestment_per_year == True:
                        print("Target investment active")
                        new_target_power_plants = self.investbyTargets()
                        for newplant in new_target_power_plants:
                            self.reps.dbrw.stage_new_power_plant(newplant)
                            self.reps.dbrw.stage_loans(newplant)
                            self.reps.dbrw.stage_downpayments(newplant)
                            # self.reps.dbrw.stage_investment_decisions(100, newplant.name,
                            #                                           self.reps.investmentIteration,
                            #                                           self.futureInvestmentyear, self.reps.current_tick)

                    # self.agent.readytoInvest = False #
            else:
                print("all technologies are unprofitable")

        else:
            print("agent is not longer willing to invest")  # This is not enabled for not

    def invest(self, bestCandidatePowerPlant):
        commissionedYear = self.reps.current_year + bestCandidatePowerPlant.technology.expected_permittime + bestCandidatePowerPlant.technology.expected_leadtime
        newid = (int(str(commissionedYear) +
                     str("{:02d}".format(
                         int(self.reps.dictionaryTechNumbers[bestCandidatePowerPlant.technology.name]))) +
                     str("{:05d}".format(int(self.new_id)))
                     ))
        self.new_id += 1
        newplant = PowerPlant(newid)
        # in Amiris the candidate power plants are tested add a small capacity. The real candidate power plants have a bigger capacity
        newplant.specifyPowerPlantforInvest(self.reps.current_tick, self.reps.current_year, self.agent,
                                            self.reps.country,
                                            bestCandidatePowerPlant.capacityTobeInstalled,
                                            bestCandidatePowerPlant.technology)

        print("{0} invests in technology {1} at tick {2}, with id{3}".format(self.agent.name,
                                                                             bestCandidatePowerPlant.technology.name,
                                                                             self.reps.current_tick, newid))
        # --------------------------------------------------------------------------------------Payments
        investmentCostPayedByEquity = newplant.getActualInvestedCapital() * (1 - self.agent.getDebtRatioOfInvestments())
        investmentCostPayedByDebt = newplant.getActualInvestedCapital() * self.agent.getDebtRatioOfInvestments()
        totalDownPayment = investmentCostPayedByEquity
        bigbank = self.reps.bigBank
        manufacturer = self.reps.manufacturer
        # --------------------------------------------------------------------------------------creating downpayment
        # self.createSpreadOutDownPayments(self.agent, manufacturer, totalDownPayment, newplant)
        buildingTime = newplant.getActualLeadtime()

        #         # make the first downpayment and create the loan
        # self.reps.createCashFlow(self.agent, manufacturer, totalDownPayment / buildingTime, globalNames.CF_DOWNPAYMENT,
        #                          self.reps.current_tick, newplant)
        # todo: check  buildingTime - 1 because one payment is already done
        downpayment = self.reps.createDownpayment(self.agent.name, manufacturer.name, totalDownPayment / buildingTime,
                                                  buildingTime,
                                                  self.reps.current_tick, 0, newplant)
        # the rest of downpayments are scheduled. Are saved to the power plant
        newplant.setDownpayment(downpayment)
        # --------------------------------------------------------------------------------------creating loans
        amount = self.reps.determineLoanAnnuities(investmentCostPayedByDebt,
                                                  newplant.getTechnology().getDepreciationTime(),
                                                  self.agent.getLoanInterestRate())
        loan = self.reps.createLoan(self.agent.name, bigbank.name, amount,
                                    newplant.getTechnology().getDepreciationTime(),
                                    (newplant.commissionedYear - self.reps.start_simulation_year), 0, newplant)
        newplant.setLoan(loan)
        return newplant

    def setTimeHorizon(self):
        self.futureTick = self.reps.current_tick + self.reps.lookAhead  # self.agent.getInvestmentFutureTimeHorizon()
        self.futureInvestmentyear = self.reps.start_simulation_year + self.futureTick

    def getProjectCashFlow(self, candidatepowerplant, agent):
        # technology = self.reps.power_generating_technologies[candidatepowerplant.technology]
        technology = candidatepowerplant.technology
        totalInvestment = self.getActualInvestedCapitalperMW(
            technology) * candidatepowerplant.capacity  # candidate power plants only have 1MW installed
        # candidatepowerplant.InvestedCapital = totalInvestment
        depreciationTime = technology.depreciation_time
        technical_lifetime = technology.expected_lifetime
        interestRate = technology.interest_rate
        buildingTime = technology.expected_leadtime
        operatingProfit = candidatepowerplant.get_Profit()
        fixed_costs = technology.fixed_operating_costs * candidatepowerplant.capacity
        equity = (1 - agent.debtRatioOfInvestments)
        equalTotalDownPaymentInstallment = (totalInvestment * equity) / buildingTime
        debt = totalInvestment * agent.debtRatioOfInvestments
        restPayment = debt / depreciationTime
        annuity = - npf.pmt(self.agent.loanInterestRate, depreciationTime, debt, fv=1, when='end')
        investmentCashFlow = [0 for i in range(depreciationTime + buildingTime)]

        # print("total investment cost in MIll", totalInvestment / 1000000)
        if self.reps.npv_with_annuity == True:
            for i in range(0, buildingTime):
                investmentCashFlow[i] = - equalTotalDownPaymentInstallment
            for i in range(buildingTime, depreciationTime + buildingTime):
                investmentCashFlow[i] = operatingProfit - fixed_costs - annuity
        else:
            for i in range(0, buildingTime):
                investmentCashFlow[i] = - equalTotalDownPaymentInstallment
            for i in range(buildingTime, depreciationTime + buildingTime):
                investmentCashFlow[i] = operatingProfit - fixed_costs - restPayment
        return investmentCashFlow

    def npv(self, investmentCashFlow):
        # print("WACC  ", wacc, " ", [round(x) for x in investmentCashFlow])
        discountedprojectvalue = npf.npv(self.wacc, investmentCashFlow)
        return discountedprojectvalue

    def getActualInvestedCapitalperMW(self, technology):
        investmentCostperTechnology = technology.investment_cost_eur_MW
        investmentCostperMW = self.getinvestmentcosts(investmentCostperTechnology,
                                                      (technology.expected_permittime + technology.expected_leadtime))
        return investmentCostperMW

    def getinvestmentcosts(self, investmentCostperTechnology, time):
        # print("invest", investmentCostperTechnology, "times", pow(1.05, time))
        return investmentCostperTechnology  # TODO check: in emlab it was  pow(1.05, time of permit and construction) * investmentCostperTechnology

    def setPowerPlantExpectations(self, powerplant, time):
        powerplant.calculate_marginal_fuel_cost_per_mw_by_tick(self.reps, time)

    def findAllClearingPointsForSubstanceAndTimeRange(self, substance, timeFrom, timeTo):
        pass

    def calculateandCheckFutureCapacityExpectation(self, candidatepowerplant):
        # checking if the technology can be installed or not
        technology = candidatepowerplant.technology

        expectedInstalledCapacityOfTechnology = self.expectedInstalledCapacityPerTechnology[technology.name]

        # This calculation dont consider that some power plants might not be decommissioned because of positive profits
        # oldExpectedInstalledCapacityOfTechnology = self.reps.calculateCapacityOfExpectedOperationalPlantsperTechnology(
        #     technology, self.futureTick, ids_of_future_installed_pp)
        if self.reps.targetinvestment_per_year == True:
            technologyTargetCapacity = self.reps.findPowerGeneratingTechnologyTargetByTechnologyandyear(technology,
                                                                                                        self.futureInvestmentyear)
            # if there are capacity targets then the targets are the exoected cspaacity

        else:
            technologyTargetCapacity = None
            # TODO: finish the target capacity with trends
            # technologyTarget = self.reps.findPowerGeneratingTechnologyTargetByTechnology(technology, self.future)
            # technologyTargetCapacity = self.reps.trends[technologyTarget.name].get_value(self.futureTick)

        # many technologies dont have capacity targets
        if technologyTargetCapacity != None:
            if (technologyTargetCapacity > expectedInstalledCapacityOfTechnology):
                expectedInstalledCapacityOfTechnology = technologyTargetCapacity

        self.operationalCapacityOfTechnology = self.reps.calculateCapacityOfOperationalPowerPlantsByTechnology(
            technology)
        self.capacityOfTechnologyInPipeline = self.reps.calculateCapacityOfPowerPlantsByTechnologyInPipeline(technology)
        self.capacityInPipeline = self.reps.calculateCapacityOfPowerPlantsInPipeline()
        investable = self.check(technology, candidatepowerplant,expectedInstalledCapacityOfTechnology )
        return investable

    def check(self, technology, candidatepowerplant, expectedInstalledCapacityOfTechnology):
        technologyCapacityLimit = self.findLimitsByTechnology(technology)
        # (self.capacityOfTechnologyInPipeline > 2.0 * self.operationalCapacityOfTechnology)
        if self.capacityOfTechnologyInPipeline >= self.reps.maximum_investment_capacity_per_year:
            logging.info(
                " will not invest in {} technology because there's too much capacity in the pipeline %s",
                technology.name)
            candidatepowerplant.setViableInvestment(False)
            return False
        elif expectedInstalledCapacityOfTechnology > technologyCapacityLimit:
            logging.info(" will not invest in {} technology because the capacity limits are achieved %s",
                         technology.name)
            candidatepowerplant.setViableInvestment(False)
            return False
            # TODO: add if the agent dont have enough cash then change the agent.readytoInvest = False

        # elif (self.expectedInstalledCapacityPerTechnology + self.candidatepowerplant.getActualNominalCapacity()) / (marketInformation.maxExpectedLoad + self.plant.getActualNominalCapacity()) >\
        #         self.technology.getMaximumInstalledCapacityFractionInCountry():
        #     logging.info(" will not invest in {} technology because there's too much of this type in the market" + technology)
        # TODO: add the maxExpected Load
        # if self.capacityInPipeline > 0.2 * marketInformation.maxExpectedLoad:
        #     logging.info( "Not investing because more than 20% of demand in pipeline.")

        #     logging.info(Lagent +" will not invest in {} technology as he does not have enough money for downpayment" + self.technology)
        else:
            logging.info("%s passes capacity limit.  will now calculate financial viability.", technology)
            candidatepowerplant.setViableInvestment(True)
            return True

    def findLimitsByTechnology(self, technology):
        LimitinCountry = technology.getMaximumCapacityinCountry()
        if LimitinCountry:
            return LimitinCountry
        else:
            return 100000000000  # if there is no declared limit, use a very high number

    def investbyTargets(self):
        targetInvestors = self.reps.findTargetInvestorByCountry(self.reps.country)
        new_target_power_plants = []
        for target in targetInvestors:
            target_tech = self.reps.power_generating_technologies[target.targetTechnology]
            # TODO: later the expected installed power plants can be calculated according to profits not only for lookahead but also fot future time:
            #futuretime =self.reps.current_tick + technology.expected_leadtime + technology.expected_permittime)
            expectedInstalledCapacity = self.expectedInstalledCapacityPerTechnology[target_tech.name]
            pgtNodeLimit = target_tech.getMaximumCapacityinCountry() # now is for all technologies the same.
            #futureTimePoint = self.reps.current_tick + pgt.getExpectedLeadtime() + pgt.getExpectedPermittime()
            #targetCapacity = target_tech.getTrend().getValue(futureTimePoint)
            technologyTargetCapacity = self.reps.findPowerGeneratingTechnologyTargetByTechnologyandyear(target_tech,
                                                                                                        self.futureInvestmentyear)
            installedCapacityDeviation = 0
            if pgtNodeLimit > technologyTargetCapacity:
                installedCapacityDeviation = technologyTargetCapacity - expectedInstalledCapacity
            else:
                installedCapacityDeviation = pgtNodeLimit - expectedInstalledCapacity

            # if the target is lower than the physical limits
            if installedCapacityDeviation > 0 and installedCapacityDeviation > target_tech.getCapacity():
                print(target.name + " needs to invest " + str(installedCapacityDeviation) + " MW")

                candidate_name = self.reps.get_candidate_name_by_technology( target_tech.name)
                for investable in self.investable_candidate_plants:
                    if investable.name == candidate_name:
                        bestCandidatePowerPlant = investable

                number_new_powerplants = math.floor(installedCapacityDeviation / bestCandidatePowerPlant.capacity)

                for i in range(number_new_powerplants):
                    print("investing in " + target_tech.name + str(bestCandidatePowerPlant.capacity) )
                    newplant = self.invest(bestCandidatePowerPlant)
                    new_target_power_plants.append(newplant)
        return new_target_power_plants




    # expectedTechnologyCapacity = reps.powerPlantRepository.calculateCapacityOfExpectedOperationalPowerPlantsInMarketAndTechnology(market, pggt.getPowerGeneratingTechnology(), time)
    # targetDifference = pggt.getTrend().getValue(time) - expectedTechnologyCapacity
    # if targetDifference > 0:
    #     plant = PowerPlant()
    #     plant.specifyNotPersist(getCurrentTick(), EnergyProducer(), reps.powerGridNodeRepository.findFirstPowerGridNodeByElectricitySpotMarket(market), pggt.getPowerGeneratingTechnology())
    #     plant.setActualNominalCapacity(targetDifference)
    #     plantMarginalCost = determineExpectedMarginalCost(plant, fuelPrices, co2price)
    #     marginalCostMap.put(plant, plantMarginalCost)
    #     capacitySum += targetDifference

    # Returns the Node Limit by Technology or the max double numer if none was found
    def read_csv_results_and_filter_candidate_plants(self):
        df = pd.read_csv(globalNames.amiris_results_path)
        df['commissionyear'] = df['identifier'].astype(str).str[0:4]
        # the candidate power plants wer given an id of 9999.
        # Only these candidate power plants need to be analyzed
        candidate_pp_results = df[df['commissionyear'] == str(9999)]
        installed_pp_results = df[df['commissionyear'] != str(9999)]
        self.reps.update_candidate_plant_results(candidate_pp_results)
        self.ids_of_future_installed_pp = self.reps.update_installed_pp_results(installed_pp_results)
        print("updated results")

    def continue_iteration(self):
        file = globalNames.continue_path
        print("saving continue to", file)
        f = open(file, "w")
        f.write(str(True))
        f.close()

    def stop_iteration(self):
        print("stop iteration, file in folder ", os.getcwd())
        file = globalNames.continue_path
        f = open(file, "w")
        f.write(str(False))
        f.close()

    def calculateNodeLimit(self):
        pgtLimit = getReps().findOneByTechnologyAndNode(self.technology, self.node)
        if pgtLimit is not None:
            self.pgtNodeLimit = pgtLimit.getUpperCapacityLimit(futureTimePoint)

    def setAgent(self, agent):
        self.agent = self.reps.energy_producers[agent]

    # budget is the sum of all cash flow
    # it is the sum of the revenues minus the debt
    # once an investment is done, decrease the amount from the investment budget
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

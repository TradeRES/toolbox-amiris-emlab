
from modules.defaultmodule import DefaultModule
from domain.CandidatePowerPlant import *
import numpy_financial as npf
import pandas as pd
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

    The investment NPV are made based on technology.
    The loans are made after plant is specified with right capacity

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
        self.ids_of_future_installed_and_dispatched_pp = []
        self.first_run = False

        if self.reps.initialization_investment == True and reps.runningModule != "run_short_investment_module":
            if self.reps.investmentIteration == -1:
                self.first_run = True
                self.setTimeHorizon(reps.lookAhead)
                self.look_ahead_years = reps.lookAhead
            else:
                # Adding the investments as an initialization
                self.setTimeHorizon(reps.investment_initialization_years)
                self.look_ahead_years = reps.investment_initialization_years
        else:
            self.setTimeHorizon(reps.lookAhead)
            self.look_ahead_years = reps.lookAhead

        print("Look ahead year " + str(self.look_ahead_years) + "/ future year" + str(self.futureInvestmentyear))

        self.wacc = (
                                1 - self.agent.debtRatioOfInvestments) * self.agent.equityInterestRate + self.agent.debtRatioOfInvestments * self.agent.loanInterestRate
        reps.dbrw.stage_init_candidate_plants_value(self.reps.investmentIteration, self.futureInvestmentyear)
        # reps.dbrw.stage_init_investment_decisions(self.reps.investmentIteration , self.reps.current_tick)
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

    def act(self):
        self.future_installed_plants_ids = self.reps.get_ids_of_future_installed_plants(self.futureTick)
        # this function adds         self.AwardedPowerinMWh = results.PRODUCTION_IN_MWH / self.CostsinEUR = results.VARIABLE_COSTS_IN_EURO /
        # self.ReceivedMoneyinEUR = results.REVENUES_IN_EURO and self.operationalProfit = results.CONTRIBUTION_MARGIN_IN_EURO from csv
        self.read_csv_results_and_filter_candidate_plants()
        self.pp_dispatched_names = []
        self.pp_profits = pd.DataFrame()
        pp_dispatched_ids = []
        pp_profits = []
        #pp_profits = pd.DataFrame()
        cp_numbers = []
        cp_profits = []
        # saving: operationalprofits from power plants in classname Profits
        for pp_id in self.ids_of_future_installed_and_dispatched_pp:
            pp = self.reps.get_power_plant_by_id(pp_id)
            self.pp_dispatched_names.append(pp.name)
          #  pp_profits.at[0, pp.id] = pp.operationalProfit
            pp_dispatched_ids.append(pp_id)
            pp_profits.append(pp.operationalProfit)
            self.pp_profits.at[0,pp_dispatched_ids] = pp_profits

        if self.first_run == True:
            """
            the first iteration on the first year, no investments are done,
            it is only to check the old power plants profits in a future market
            """
            print(" FIRST RUN ONLY TO TEST THE MARKET")
            self.reps.dbrw.stage_iteration(self.reps.investmentIteration + 1)
            self.reps.dbrw.stage_future_total_profits_installed_plants(self.reps, self.pp_dispatched_names, self.pp_profits,
                                                                       self.future_installed_plants_ids)
            self.continue_iteration()
        elif self.reps.targetinvestment_per_year == True and self.reps.target_investments_done == False:
            # todo: these variables could be removed once the model is validated
           # self.reps.dbrw.stage_future_operational_profits_installed_plants(self.reps, pp_dispatched_names, pp_profits)
            print("Investing according to TARGETS")
            new_target_power_plants = self.investbyTargets()
            for newplant in new_target_power_plants:
                self.reps.dbrw.stage_new_power_plant(newplant)
                self.reps.dbrw.stage_loans(newplant)
                self.reps.dbrw.stage_downpayments(newplant)
            self.reps.dbrw.stage_target_investments_done(True)
            self.continue_iteration()
            self.reps.dbrw.stage_iteration(self.reps.investmentIteration + 1)
        else:
            #todo: these variables could be removed once the model is validated
         #   self.reps.dbrw.stage_future_operational_profits_installed_plants(self.reps, pp_dispatched_names, pp_profits)
            print("Investing according to market results. iteration" + str(self.reps.investmentIteration))
            highestNPVCandidatePP = None
            highestNPV = 0
            # power plants are investable when they havent passed the capacity limits
            self.investable_candidate_plants = self.reps.get_investable_candidate_power_plants()
            if self.investable_candidate_plants:  # check if there are investable power plants
                self.expectedInstalledCapacityPerTechnology = self.reps.calculateCapacityExpectedofListofPlants(
                    self.future_installed_plants_ids, self.investable_candidate_plants, False)

                for candidatepowerplant in self.investable_candidate_plants:
                    cp_numbers.append(candidatepowerplant.name)
                    cp_profits.append(candidatepowerplant.operationalProfit)
                    # calculate which is the power plant (technology) with the highest NPV
                    candidatepowerplant.specifyCandidatePPCapacityLocationOwner(self.reps, self.agent)

                    if self.reps.limit_investments == True:
                        investable = self.calculateandCheckFutureCapacityExpectation(candidatepowerplant
                                                                                     )
                    else:
                        investable = True

                    if investable == False:
                        candidatepowerplant.setViableInvestment(False)
                        print(
                            "set to non investable " + candidatepowerplant.technology.name)
                        # saving if the candidate power plant remains or not as investable
                        self.reps.dbrw.stage_candidate_pp_investment_status(candidatepowerplant)
                    else:
                        cashflow = self.getProjectCashFlow(candidatepowerplant, self.agent)
                        projectvalue = self.npv(cashflow)

                        # saving the list of power plants values that have been candidates per investmentIteration.
                        self.reps.dbrw.stage_candidate_power_plants_value(candidatepowerplant.name, projectvalue / candidatepowerplant.capacity,
                                                                          self.reps.investmentIteration,
                                                                          self.futureInvestmentyear,
                                                                          )
                        if projectvalue >= 0 and ((projectvalue / candidatepowerplant.capacity) > highestNPV):
                            highestNPV = projectvalue / candidatepowerplant.capacity
                            highestNPVCandidatePP = candidatepowerplant

                        elif projectvalue < 0:
                            # the power plant should not be investable in next rounds
                            # saving if the candidate power plant remains or not as investable
                            candidatepowerplant.setViableInvestment(False)
                            self.reps.dbrw.stage_candidate_pp_investment_status(candidatepowerplant)
                        else:
                            logging.info("technology%s negative NPV", candidatepowerplant.technology)

                # saving: operational profits from candidate plant
                # todo: this can be avoid, saving for debugging
                self.reps.dbrw.stage_candidate_plant_results(self.reps, cp_numbers, cp_profits)
                # if the power plant is correctly saved
                if highestNPVCandidatePP is not None:
                    # investing in best candidate power plant as it passed the checks.
                    print("Investing in " + highestNPVCandidatePP.technology.name)
                    newplant = self.invest(highestNPVCandidatePP, False)
                    self.reps.dbrw.stage_new_power_plant(newplant)
                    # self.reps.dbrw.stage_loans(newplant)
                    # self.reps.dbrw.stage_downpayments(newplant)
                    # self.reps.dbrw.stage_investment_decisions(newplant.id,
                    #                                           self.reps.investmentIteration,
                    #                                           self.reps.current_tick)
                    self.reps.dbrw.stage_iteration(self.reps.investmentIteration + 1)
                    self.continue_iteration()
                else:
                    print("no more power plant to invest, saving loans, next iteration")
                    if self.reps.initialization_investment == True:
                        print("increasing testing year by one")
                        if self.reps.investment_initialization_years >= self.reps.lookAhead - 1:
                            # look ahead = 4 should be executed in the workflow
                            self.reps.initialization_investment = False
                            self.reps.dbrw.stage_initialization_investment(self.reps.initialization_investment)
                            self.reps.dbrw.stage_last_testing_technology(False)
                            self.stop_iteration()

                        else:
                            self.reps.investment_initialization_years += 1
                            self.continue_iteration()
                            self.reps.dbrw.stage_testing_future_year(self.reps)

                        # reset all candidate power plants to investable
                        candidates_names = self.reps.get_unique_candidate_names()
                        self.reps.dbrw.stage_candidate_status_to_investable(candidates_names)
                        if self.reps.targetinvestment_per_year == True:
                            self.reps.dbrw.stage_target_investments_done(False)

                    else:
                        # continue to next year in workflow
                        self.reps.dbrw.stage_last_testing_technology(False)
                        self.stop_iteration()
                    # saving iteration number back to zero for next year
                    self.reps.dbrw.stage_iteration(0)

                    if self.reps.groups_plants_per_installed_year == True:
                        self.group_power_plants()
                    else:
                        self.stage_loans_and_downpayments()

                    # saving profits of installed power plants.
                    print("saving future total profits")
                    self.reps.dbrw.stage_future_total_profits_installed_plants(self.reps,self.pp_dispatched_names, self.pp_profits,

                                                                               self.future_installed_plants_ids)
            else:
                print("all technologies are unprofitable")
    def stage_loans_and_downpayments(self):
        for newplant in self.reps.get_power_plants_invested_in_tick(self.reps.current_tick):
            self.reps.dbrw.stage_loans(newplant)
            self.reps.dbrw.stage_downpayments(newplant)


    def invest(self, newplant, target_invest):
        if self.reps.install_at_look_ahead_year == True:
            commissionedYear = self.reps.current_year + self.look_ahead_years
        else:
            print("fix this if needed !!!!!") # todo fix this if needed
            commissionedYear = self.reps.current_year + newplant.technology.expected_permittime + newplant.technology.expected_leadtime

        if target_invest == False:
            newid = (int(str(commissionedYear) +
                         str("{:02d}".format(
                             int(self.reps.dictionaryTechNumbers[newplant.technology.name]))) +
                         str("{:05d}".format(int(self.new_id)))
                         ))
        else:
            newid = (int(str(commissionedYear) +
                         str("{:02d}".format(
                             int(self.reps.dictionaryTechNumbers[newplant.technology.name]))) +
                         str("{:06d}".format(int(self.new_id)))
                         ))

        self.new_id += 1

        newplant.name = newid
        newplant.id = newid
        # in Amiris the candidate power plants are tested add a small capacity. The real candidate power plants have a bigger capacity
        newplant.specifyPowerPlantforInvest(self.reps,  self.look_ahead_years)

        print("{0} invests in technology {1} at tick {2}, with id{3} and million eur:".format(self.agent.name,
                                                                             newplant.technology.name,
                                                                             self.reps.current_tick, newid))
        # --------------------------------------------------------------------------------------Payments
        print(newplant.getActualInvestedCapital() / (1000000*newplant.capacity))
        investmentCostPayedByEquity = newplant.getActualInvestedCapital() * (1 - self.agent.getDebtRatioOfInvestments())
        investmentCostPayedByDebt = newplant.getActualInvestedCapital() * self.agent.getDebtRatioOfInvestments()
        totalDownPayment = investmentCostPayedByEquity
        bigbank = self.reps.bigBank
        manufacturer = self.reps.manufacturer
        # --------------------------------------------------------------------------------------creating downpayment
        # self.createSpreadOutDownPayments(self.agent, manufacturer, totalDownPayment, newplant)
        buildingTime = newplant.getActualLeadtime() # the plant is built after permit time.

        # from_agent: str, to: str, amount, numberOfPayments, loanStartTime, donePayments, plant
        downpayment = self.reps.createDownpayment(self.agent.name, manufacturer.name, totalDownPayment / buildingTime,
                                                  buildingTime,
                                                  self.reps.current_tick, 0, newplant)
        """
        Cash flows are kept only at the financial results module
        Downpayments start from next year
        """
        # the rest of downpayments are scheduled. Are saved to the power plant
        newplant.downpayment = downpayment
        # --------------------------------------------------------------------------------------creating loans
        amount = self.reps.determineLoanAnnuities(investmentCostPayedByDebt,
                                                  newplant.getTechnology().getDepreciationTime(),
                                                  self.agent.getLoanInterestRate())

        loan = self.reps.createLoan(self.agent.name, bigbank.name, amount,
                                    newplant.getTechnology().getDepreciationTime(),
                                    (newplant.commissionedYear - self.reps.start_simulation_year), 0, newplant)
        newplant.setLoan(loan)
        return newplant

    def setTimeHorizon(self, lookAhead):
        self.futureTick = self.reps.current_tick + lookAhead  # self.agent.getInvestmentFutureTimeHorizon()
        self.futureInvestmentyear = self.reps.start_simulation_year + self.futureTick

    def getProjectCashFlow(self, candidatepowerplant, agent):
        technology = candidatepowerplant.technology
        totalInvestment = self.getActualInvestedCapitalperMW(
            technology) * candidatepowerplant.capacity  # candidate power plants only have 1MW installed
        depreciationTime = technology.depreciation_time
        technical_lifetime = technology.expected_lifetime
        buildingTime = technology.expected_leadtime
        operatingProfit = candidatepowerplant.get_Profit()
        fixed_costs = self.getActualFixedCostsperMW(technology) * candidatepowerplant.capacity
        equity = (1 - agent.debtRatioOfInvestments)
        equalTotalDownPaymentInstallment = (totalInvestment * equity) / buildingTime
        debt = totalInvestment * agent.debtRatioOfInvestments
        restPayment = debt / depreciationTime
        annuity = - npf.pmt(self.agent.loanInterestRate, depreciationTime, debt, fv=1, when='end')
        investmentCashFlow = [0 for i in range(depreciationTime + buildingTime)]

        # print("total investment cost in MIll", totalInvestment / 1000000)
        if self.reps.npv_with_annuity == True:
            for i in range(0, buildingTime + depreciationTime):
                if i < buildingTime:
                    investmentCashFlow[i] = - equalTotalDownPaymentInstallment
                else:
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
        investmentCostperTechnology = technology.get_investment_costs_perMW_by_year(self.futureInvestmentyear)
        return investmentCostperTechnology


    def getActualFixedCostsperMW(self, technology):
        fixedCostperTechnology = technology.get_fixed_costs_by_commissioning_year(self.futureInvestmentyear)
        return fixedCostperTechnology

    def getinvestmentcosts(self, investmentCostperTechnology, time):
        # print("invest", investmentCostperTechnology, "times", pow(1.05, time))
        return investmentCostperTechnology  # TODO check: in emlab it was  pow(1.05, time of permit and construction) * investmentCostperTechnology

    def calculateandCheckFutureCapacityExpectation(self,
                                                   candidatepowerplant):  # if there would be more agents, the future capacity should be analyzed per age
        # checking if the technology can be installed or not
        technology = candidatepowerplant.technology
        expectedInstalledCapacityOfTechnology = self.expectedInstalledCapacityPerTechnology[technology.name]
        # This calculation dont consider that some power plants might not be decommissioned because of positive profits
        # oldExpectedInstalledCapacityOfTechnology = self.reps.calculateCapacityOfExpectedOperationalPlantsperTechnology(
        #     technology, self.futureTick, ids_of_future_installed_and_dispatched_pp)
        self.operationalCapacityOfTechnology = self.reps.calculateCapacityOfOperationalPowerPlantsByTechnology(
            technology)
        self.capacityOfTechnologyInPipeline = self.reps.calculateCapacityOfPowerPlantsByTechnologyInPipeline(technology)
        self.capacityInPipeline = self.reps.calculateCapacityOfPowerPlantsInPipeline()

        technologyCapacityLimit = technology.getMaximumCapacityinCountry(self.futureInvestmentyear)

        # (self.capacityOfTechnologyInPipeline > 2.0 * self.operationalCapacityOfTechnology)
        if self.capacityInPipeline >= self.reps.maximum_investment_capacity_per_year:
            print(
                " will not invest in " + technology.name + " because there's too much capacity in the pipeline ")
            candidatepowerplant.setViableInvestment(False)
            return False
        elif expectedInstalledCapacityOfTechnology > technologyCapacityLimit:
            print(" will not invest in " + technology.name + " because the capacity limits are achieved")
            candidatepowerplant.setViableInvestment(False)
            return False
            # TODO: add if the agent dont have enough cash then change the agent.readytoInvest = False

        # elif (self.expectedInstalledCapacityPerTechnology + self.candidatepowerplant.getActualNominalCapacity()) / (marketInformation.maxExpectedLoad + self.plant.getActualNominalCapacity()) >\
        #         self.technology.getMaximumInstalledCapacityFractionInCountry():
        #     logging.info(" will not invest in {} technology because there's too much of this type in the market" + technology)

        else:
            logging.info("%s passes capacity limit.  will now calculate financial viability.", technology)
            candidatepowerplant.setViableInvestment(True)
            return True

    def investbyTargets(self):
        targetInvestors = self.reps.findTargetInvestorByCountry(self.reps.country)
        new_target_power_plants = []
        # adding the target candidate power plants
        already_investable = []
        for i in self.investable_candidate_plants:
            already_investable.append(i.technology.name)
        target_candidate_power_plants = self.reps.get_target_candidate_power_plants(already_investable)
        expectedInstalledCapacityperTechnology = self.reps.calculateCapacityExpectedofListofPlants(
            self.future_installed_plants_ids, target_candidate_power_plants, True)

        for target in targetInvestors:
            target_tech = self.reps.power_generating_technologies[target.targetTechnology]
            # TODO: later the expected installed power plants can be calculated according to profits not only for lookahead but also fot future time:
            expectedInstalledCapacity = expectedInstalledCapacityperTechnology[target_tech.name]
            pgt_country_limit = target_tech.getMaximumCapacityinCountry(self.futureInvestmentyear)

            # targetCapacity = target_tech.getTrend().getValue(futureTimePoint)
            # technologyTargetCapacity = self.reps.findPowerGeneratingTechnologyTargetByTechnologyandyear(target_tech,
            #                                                                                             self.futureInvestmentyear)
            yearlyCapacityTarget = self.reps.find_technology_year_target(target_tech, self.futureInvestmentyear)

            if pgt_country_limit > yearlyCapacityTarget + expectedInstalledCapacity:  # limit is not reached
                pass
            else:
                yearlyCapacityTarget = pgt_country_limit - expectedInstalledCapacity
                print("limit is reached, so install the maximum")

            if yearlyCapacityTarget > 0:  # if the missing capacity is smaller than a unit, then dont install anything
                # print(target.name + " needs to invest " + str(yearlyCapacityTarget) + " MW")
                targetCandidatePowerPlant = self.reps.get_candidate_by_technology(target_tech.name)
                if self.reps.install_missing_capacity_as_one_pp == True:
                    targetCandidatePowerPlant.capacityTobeInstalled = yearlyCapacityTarget
                    print("Target investing in " + target_tech.name + str(
                        targetCandidatePowerPlant.capacityTobeInstalled))
                    newplant = self.invest(targetCandidatePowerPlant, True)
                    newplant.candidate_name = targetCandidatePowerPlant.name  # changing name to be saved in investment decisions
                    new_target_power_plants.append(newplant)
                else:
                    number_new_powerplants = math.floor(
                        yearlyCapacityTarget / targetCandidatePowerPlant.capacityTobeInstalled)
                    remainder = yearlyCapacityTarget % targetCandidatePowerPlant.capacityTobeInstalled
                    for i in range(number_new_powerplants):
                        print("Target investing in " + target_tech.name + str(
                            targetCandidatePowerPlant.capacityTobeInstalled))
                        if i == number_new_powerplants - 1:
                            targetCandidatePowerPlant.capacityTobeInstalled += remainder
                        else:
                            pass
                        newplant = self.invest(targetCandidatePowerPlant, True)
                        newplant.candidate_name = targetCandidatePowerPlant.name  # changing name to be saved in investment decisions
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
    def group_power_plants(self):
        plants_to_delete = []
        for candidate_technology in self.reps.get_unique_candidate_technologies():
            commissionedYear = self.reps.current_year + self.look_ahead_years
            new_plants_per_tech = self.reps.get_power_plants_invested_in_tick_by_technology(commissionedYear, candidate_technology)
            if len(new_plants_per_tech)>1:
                grouped_plant = CandidatePowerPlant("grouped")
                for newplant in new_plants_per_tech:
                    grouped_plant.capacityTobeInstalled += newplant.capacity
                    plants_to_delete.append(str(newplant.id))
                    self.ids_of_future_installed_and_dispatched_pp.remove(newplant.id)
                    print("removing " + str(newplant.id))
                    self.pp_dispatched_names.remove(str(newplant.id))
                    self.pp_profits.drop(columns =newplant.id)
                # self.reps.dbrw.stage_id_plant_to_delete(newplant)
                grouped_plant.setActualEfficiency(newplant.actualEfficiency)
                grouped_plant.setOwner(self.agent)
                grouped_plant.setLocation(self.reps.country)
                grouped_plant.setTechnology(candidate_technology)
                grouped_plant = self.invest(grouped_plant, False)
                self.reps.dbrw.stage_new_power_plant(grouped_plant)
                self.reps.dbrw.stage_loans(grouped_plant)
                self.reps.dbrw.stage_downpayments(grouped_plant)


        # deleting plants that have been grouped
        self.reps.dbrw.delete_rows_DB("Id", plants_to_delete)
        # update power_plants_installed
        self.reps.dbrw.stage_installed_pp_names(self.ids_of_future_installed_and_dispatched_pp, self.futureTick)

    # Returns the Node Limit by Technology or the max double numer if none was found
    def read_csv_results_and_filter_candidate_plants(self):
        df = pd.read_csv(globalNames.amiris_results_path)
        df['commissionyear'] = df['identifier'].astype(str).str[0:4]
        # the candidate power plants wer given an id of 9999.
        # Only these candidate power plants need to be analyzed
        candidate_pp_results = df[df['commissionyear'] == str(9999)]
        installed_pp_results = df[df['commissionyear'] != str(9999)]
        self.reps.update_candidate_plant_results(candidate_pp_results)
        self.ids_of_future_installed_and_dispatched_pp = self.reps.update_installed_pp_results(installed_pp_results)
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

    def setAgent(self, agent):
        self.agent = self.reps.energy_producers[agent]


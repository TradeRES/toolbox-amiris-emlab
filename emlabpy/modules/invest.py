from modules.defaultmodule import DefaultModule
from domain.CandidatePowerPlant import *
import numpy_financial as npf
import pandas as pd
import os
import logging
import math
from modules.capacitymarket import CapacityMarketClearing, calculate_cone
from modules.capacitySubscription import *
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
        self.peak_demand = 0
        self.investmentCashFlow = []
        self.useFundamentalCO2Forecast = False  # from AbstractInvestInPowerGenerationTechnologiesRole
        self.futureTick = 0  # future tick
        self.futureInvestmentyear = 0
        self.spotMarket = reps.get_spot_market_in_country(reps.country)
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
        elif self.reps.round_for_capacity_market == True:
            market = reps.get_capacity_market_in_country(reps.country)
            self.setTimeHorizon(market.forward_years_CM)
            self.look_ahead_years = market.forward_years_CM
        else:
            self.setTimeHorizon(reps.lookAhead)
            self.look_ahead_years = reps.lookAhead

        print("Look ahead year " + str(self.look_ahead_years) + "/ future year" + str(self.futureInvestmentyear))

        # self.wacc = (1 - self.agent.debtRatioOfInvestments) * self.agent.equityInterestRate + self.agent.debtRatioOfInvestments * self.agent.loanInterestRate
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
        self.read_csv_results_and_filter_candidate_plants()  # attention: here are the results for the year saved
        self.pp_dispatched_names = []
        self.pp_profits = pd.DataFrame()
        pp_dispatched_ids = []
        pp_profits = []
        cp_numbers = []
        cp_profits = []
        # saving: operationalprofits from power plants in classname Profits
        profits = []
        names = []
        for pp_id in self.ids_of_future_installed_and_dispatched_pp:
            pp = self.reps.get_power_plant_by_id(pp_id)
            self.pp_dispatched_names.append(pp.name)
            # pp_dispatched_ids.append(pp_id)
            # pp_profits.append(pp.operationalProfit)
            profits.append(pp.operationalProfit)
            names.append(pp_id)

        self.pp_profits = pd.DataFrame([profits], columns=names)
        # self.calculate_capacity_market_price()
        if self.first_run == True:
            """
            the first iteration on the first year, no investments are done, it is only to check the old power plants profits in a future market
            """
            print(" FIRST RUN ONLY TO TEST THE MARKET")
            self.reps.dbrw.stage_iteration(self.reps.investmentIteration + 1)
            self.reps.dbrw.stage_future_profits_withloans_installed_plants(self.reps, self.pp_dispatched_names,
                                                                           self.pp_profits,
                                                                           self.future_installed_plants_ids,
                                                                           self.futureTick, self.look_ahead_years)
            self.continue_iteration()
        elif self.reps.round_for_capacity_market == True:
            """
            no investments are done, it is only to get expected profits for capacity market 
            """
            print("ESTIMATE PROFITS FOR CAPACIY MARKET")
            self.reps.dbrw.stage_future_total_profits_installed_plants(self.reps, self.pp_dispatched_names,
                                                                       self.pp_profits,
                                                                       self.future_installed_plants_ids,
                                                                       self.futureTick)
            self.stop_iteration()
            self.reps.dbrw.stage_iteration_for_CM(False)
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
            # todo: these variables could be removed once the model is validated
            #   self.reps.dbrw.stage_future_operational_profits_installed_plants(self.reps, pp_dispatched_names, pp_profits)
            print("Investing according to market results. iteration" + str(self.reps.investmentIteration))
            highestNPVCandidatePP = None
            highestNPV = 0
            # power plants are investable when they havent passed the capacity limits
            self.investable_candidate_plants = self.reps.get_investable_candidate_power_plants()

            if self.investable_candidate_plants:  # check if there are investable power plants
                # if self.reps.test_first_intermittent_technologies == True and self.reps.testing_intermittent_technologies == True:
                #     # filter out intermittent technologies
                #     self.investable_candidate_plants = self.reps.filter_intermittent_candidate_power_plants(self.investable_candidate_plants)
                self.expectedInstalledCapacityPerTechnology = self.reps.calculateCapacityExpectedofListofPlants(
                    self.future_installed_plants_ids, self.investable_candidate_plants, False)
                self.capacity_calculations()

                if self.reps.capacity_market_cleared_in_investment == False or self.reps.capacity_remuneration_mechanism == None:
                    capacity_market_price = 0
                elif self.reps.capacity_remuneration_mechanism == "capacity_subscription":
                    capacity_market_price = self.calculate_capacity_subscription()
                elif self.reps.capacity_remuneration_mechanism == "capacity_market":
                    capacity_market_price = self.calculate_capacity_market_price_simple()

                print("capacity_market_price " + str(capacity_market_price))
                for candidatepowerplant in self.investable_candidate_plants:
                    # print("..............." + candidatepowerplant.technology.name)
                    cp_numbers.append(candidatepowerplant.name)
                    cp_profits.append(candidatepowerplant.operationalProfit)
                    # calculate which is the power plant (technology) with the highest NPV
                    candidatepowerplant.specifyCandidatePPCapacityLocationOwner(self.reps, self.agent)

                    if self.reps.limit_investments == True:
                        investable = self.calculateandCheckFutureCapacityExpectation(candidatepowerplant)
                    else:
                        investable = True

                    if investable == False:
                        candidatepowerplant.setViableInvestment(False)
                        print(
                            "set to non investable " + candidatepowerplant.technology.name)
                        # saving if the candidate power plant remains or not as investable
                        self.reps.dbrw.stage_candidate_pp_investment_status(candidatepowerplant)
                    else:
                        operatingProfit = candidatepowerplant.get_Profit()  # per installed capacity
                        if self.reps.capacity_market_cleared_in_investment == False:
                            pass
                        else:
                            operatingProfit = operatingProfit + capacity_market_price * candidatepowerplant.capacity * candidatepowerplant.technology.peak_segment_dependent_availability

                        # if self.reps.capacity_remuneration_mechanism == "capacity_market":
                        #     peaksupply,  effectiveExpectedCapacityperTechnology = self.reps.calculateEffectiveCapacityExpectedofListofPlants(
                        #         self.future_installed_plants_ids, self.investable_candidate_plants)
                        #     capacity_market_revenue = self.calculate_capacity_market_revenues(effectiveExpectedCapacityperTechnology, candidatepowerplant)
                        # else:
                        #     capacity_market_revenue = 0
                        # operatingProfit = operatingProfit + capacity_market_revenue

                        cashflow = self.getProjectCashFlow(candidatepowerplant, self.agent, operatingProfit)
                        projectvalue = self.npv(candidatepowerplant.technology, cashflow)

                        # saving the list of power plants values that have been candidates per investmentIteration.
                        self.reps.dbrw.stage_candidate_power_plants_value(candidatepowerplant.name,
                                                                          projectvalue / candidatepowerplant.capacity,
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
                    self.reps.dbrw.stage_iteration(self.reps.investmentIteration + 1)
                    self.continue_iteration()
                else:
                    print("no more power plant to invest, saving loans, next iteration")
                    if (self.reps.capacity_remuneration_mechanism in ["capacity_market", "capacity_subscription"]
                            and self.reps.capacity_market_cleared_in_investment == False):
                        print("************************************* accounting for capacity markets")
                        self.reset_status_candidates_to_investable()
                        self.reps.investment_initialization_years += 1
                        self.continue_iteration()
                        self.reps.dbrw.stage_calculate_future_capacity_market(True)
                        self.reps.dbrw.stage_iteration(0)
                        self.reps.dbrw.stage_last_testing_technology(False)
                    else:
                        if ((self.reps.capacity_remuneration_mechanism in ["capacity_market", "capacity_subscription",
                                                                           "strategic_reserve_ger"])
                                and self.reps.initialization_investment == False
                                and self.reps.capacity_market_cleared_in_investment == True):
                            print("************************************* calculate market for next CM next year")
                            self.reset_status_candidates_to_investable()
                            self.reps.dbrw.stage_calculate_future_capacity_market(False)
                            self.reps.dbrw.stage_iteration_for_CM(True)
                            self.continue_iteration()
                            self.reps.dbrw.stage_iteration(0)
                        else:
                            if self.reps.initialization_investment == True:
                                if (self.reps.capacity_remuneration_mechanism in ["capacity_market",
                                                                                  "capacity_subscription"]
                                        and self.reps.capacity_market_cleared_in_investment == True):
                                    self.reps.dbrw.stage_calculate_future_capacity_market(False)
                                    print(
                                        "************************************* finish capacity markets investment loop")
                                if self.reps.investment_initialization_years >= self.reps.lookAhead - 1:
                                    print("finishing investment loop")
                                    # look ahead = 4 should be executed in the workflow
                                    self.reps.initialization_investment = False
                                    self.reps.dbrw.stage_initialization_investment(False)
                                    self.reps.dbrw.stage_last_testing_technology(False)
                                    self.stop_iteration()  # continue to main workflow
                                else:
                                    print("next initialization year, no capacity market")
                                    self.reps.investment_initialization_years += 1
                                    self.continue_iteration()
                                    self.reps.dbrw.stage_testing_future_year(self.reps)
                                self.reset_status_candidates_to_investable()
                                self.reps.dbrw.stage_iteration(0)

                                if self.reps.targetinvestment_per_year == True:
                                    self.reps.dbrw.stage_target_investments_done(False)
                            else:
                                # continue to next year in workflow
                                # when testing last technolgy, candidate to be installed is tested with real capacity
                                print("no capacity market, finish investments ")
                                self.reps.dbrw.stage_last_testing_technology(False)
                                self.reps.dbrw.stage_iteration(0)
                                self.stop_iteration()

                        if self.reps.groups_plants_per_installed_year == True:
                            self.group_power_plants()
                        else:
                            pass  # not grouping power plants

                        # Ids of grouped power plants were removed, so here are the left ungrouped plants
                        for pp_id in self.future_installed_plants_ids:
                            if self.power_plant_installed_in_this_year(pp_id):
                                newplant = self.reps.get_power_plant_by_id(pp_id)
                                newplant = self.calculate_investments_of_ungrouped(newplant)
                                self.stage_loans_and_downpayments_of_ungrouped(newplant)

                        # saving profits of installed power plants for capacity market
                        print("saving future total profits")
                        self.reps.dbrw.stage_future_profits_withloans_installed_plants(self.reps,
                                                                                       self.pp_dispatched_names,
                                                                                       self.pp_profits,
                                                                                       self.future_installed_plants_ids,
                                                                                       self.futureTick,
                                                                                       self.look_ahead_years)
            else:
                print("all technologies are unprofitable")
                raise Exception

    def power_plant_installed_in_this_year(self, pp_id):
        return str(pp_id)[:4] == str(self.futureInvestmentyear)

    def reset_status_candidates_to_investable(self):
        print("RESET candidates to investable")
        candidates_names = self.reps.get_unique_candidate_names()
        # reset all candidate power plants to investable todo: should this be done also in non initialization
        self.reps.dbrw.stage_candidate_status_to_investable(candidates_names)

    def stage_loans_and_downpayments_of_ungrouped(self, newplant):
        self.reps.dbrw.stage_loans(newplant)
        self.reps.dbrw.stage_downpayments(newplant)

    def invest(self, newplant, target_invest):
        if self.reps.install_at_look_ahead_year == True:
            commissionedYear = self.reps.current_year + self.look_ahead_years
        else:
            # todo fix this if needed
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
        # todo: this might not longer be needed
        newplant.specifyPowerPlantforInvest(self.reps, self.look_ahead_years)
        print("{0} invests in technology {1} at tick {2}, with id{3} :".format(self.agent.name,
                                                                               newplant.technology.name,
                                                                               self.reps.current_tick, newid))
        # --------------------------------------------------------------------------------------Payments
        print(newplant.getActualInvestedCapital() / (1000000 * newplant.capacity))
        print(newplant.capacityTobeInstalled)
        return newplant

    def calculate_investments_of_ungrouped(self, newplant):
        newplant.specify_invested_costs(self.reps)
        investmentCostPayedByEquity = newplant.getActualInvestedCapital() * (1 - self.agent.getDebtRatioOfInvestments())
        investmentCostPayedByDebt = newplant.getActualInvestedCapital() * self.agent.getDebtRatioOfInvestments()
        totalDownPayment = investmentCostPayedByEquity
        # --------------------------------------------------------------------------------------creating downpayment
        # self.createSpreadOutDownPayments(self.agent, manufacturer, totalDownPayment, newplant)
        buildingTime = newplant.getActualLeadtime()  # the plant is built after permit time.
        # from_agent: str, to: str, amount, numberOfPayments, loanStartTime, donePayments, plant
        startick = newplant.commissionedYear - self.reps.start_simulation_year - buildingTime
        downpayment = self.reps.createDownpayment(self.agent.name, self.reps.manufacturer.name,
                                                  totalDownPayment / buildingTime,
                                                  buildingTime, startick, 0, newplant)
        """
        Cash flows are kept only at the financial results module
        Downpayments start from next year
        """
        # the rest of downpayments are scheduled. Are saved to the power plant
        newplant.downpayment = downpayment
        # --------------------------------------------------------------------------------------creating loans
        amount = self.reps.determineLoanAnnuities(investmentCostPayedByDebt,
                                                  newplant.getTechnology().getDepreciationTime(),
                                                  newplant.technology.interestRate)

        loan = self.reps.createLoan(self.agent.name, self.reps.bigBank.name, amount,
                                    newplant.getTechnology().getDepreciationTime(),
                                    (newplant.commissionedYear - self.reps.start_simulation_year), 0, newplant)
        newplant.setLoan(loan)
        return newplant

    def setTimeHorizon(self, lookAhead):
        self.futureTick = self.reps.current_tick + lookAhead  # self.agent.getInvestmentFutureTimeHorizon()
        self.futureInvestmentyear = self.reps.start_simulation_year + self.futureTick

    def getProjectCashFlow(self, candidatepowerplant, agent, operatingProfit):
        technology = candidatepowerplant.technology
        totalInvestment = self.getActualInvestedCapitalperMW(
            technology) * candidatepowerplant.capacity  # candidate power plants only have 1MW installed
        depreciationTime = technology.depreciation_time
        buildingTime = technology.expected_leadtime
        fixed_costs = self.getActualFixedCostsperMW(technology) * candidatepowerplant.capacity
        equity = (1 - agent.debtRatioOfInvestments)
        if equity == 0:
            equalTotalDownPaymentInstallment = 0
        else:
            equalTotalDownPaymentInstallment = (totalInvestment * equity) / buildingTime
        debt = totalInvestment * agent.debtRatioOfInvestments
        restPayment = debt / depreciationTime
        annuity = - npf.pmt(technology.interestRate, depreciationTime, debt, fv=1, when='end')
        investmentCashFlow = [0 for i in range(depreciationTime + buildingTime)]
        #   print(str(candidatepowerplant.name )+ ";"+str(fixed_costs) + ";" +  str(annuity) + technology.name)
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

    def npv(self, technology, investmentCashFlow):
        # print("WACC  ", wacc, " ", [round(x) for x in investmentCashFlow])
        discountedprojectvalue = npf.npv(technology.interestRate, investmentCashFlow)
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

    def capacity_calculations(self):
        self.capacityInPipeline = self.reps.calculateCapacityOfPowerPlantsInPipeline()
        self.peak_demand = self.reps.get_peak_future_demand_by_year(self.futureInvestmentyear)

    def calculateandCheckFutureCapacityExpectation(self,
                                                   candidatepowerplant):  # if there would be more agents, the future capacity should be analyzed per age
        # checking if the technology can be installed or not
        technology = candidatepowerplant.technology
        expectedInstalledCapacityOfTechnology = self.expectedInstalledCapacityPerTechnology[technology.name]
        # This calculation dont consider that some power plants might not be decommissioned because of positive profits
        # oldExpectedInstalledCapacityOfTechnology = self.reps.calculateCapacityOfExpectedOperationalPlantsperTechnology(
        #     technology, self.futureTick, ids_of_future_installed_and_dispatched_pp)
        # self.capacityOfTechnologyInPipeline = self.reps.calculateCapacityOfPowerPlantsByTechnologyInPipeline(technology)
        # self.operationalCapacityOfTechnology = self.reps.calculateCapacityOfOperationalPowerPlantsByTechnology(
        #     technology)
        # (self.capacityOfTechnologyInPipeline > 2.0 * self.operationalCapacityOfTechnology)
        commissionedYear = self.reps.current_year + self.look_ahead_years
        capacityOfTechnologyInvestedAtyear = self.reps.calculateCapacityOfPowerPlantsByTechnologyInstalledinYear(
            commissionedYear, technology)
        technologyCapacityLimit = technology.getMaximumCapacityinCountry(self.futureInvestmentyear)
        if self.capacityInPipeline >= self.reps.maximum_investment_capacity_per_year:
            print(
                " will not invest in " + technology.name + " because there's too much capacity in the pipeline ")
            candidatepowerplant.setViableInvestment(False)
            return False
        elif expectedInstalledCapacityOfTechnology > technologyCapacityLimit:
            print(" will not invest in " + technology.name + " because the capacity limits are achieved")
            candidatepowerplant.setViableInvestment(False)
            return False
        elif capacityOfTechnologyInvestedAtyear > globalNames.maximum_installed_share_initialization * self.peak_demand:
            if self.reps.initialization_investment == True:
                print(capacityOfTechnologyInvestedAtyear)
                print(
                    " will not invest in " + technology.name + " more than 10% of peak demand")
                candidatepowerplant.setViableInvestment(False)
                return False
            else:
                return True
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

    def calculate_capacity_market_price_simple(self):
        capacity_market = self.reps.get_capacity_market_in_country(self.reps.country)
        print(
            "technology" + "name" + ";" + "price_to_bid;capacity" + ";" + " profits" + ";" + "fixed_on_m_cost" + ";" + "pending_loan")

        if self.reps.investmentIteration == 0 and self.reps.current_tick == 0:
            calculate_cone(self.reps, capacity_market, self.investable_candidate_plants)

        for powerplant in self.reps.power_plants.values():
            if powerplant.id in self.future_installed_plants_ids:
                price_to_bid = 0
                operatingProfit = powerplant.get_Profit()  # for installed capacity
                fixed_on_m_cost = self.getActualFixedCostsperMW(powerplant.technology) * powerplant.capacity
                totalInvestment = self.getActualInvestedCapitalperMW(
                    powerplant.technology) * powerplant.capacity  # candidate power plants only have 1MW installed
                pending_loan = - npf.pmt(powerplant.technology.interestRate, powerplant.technology.depreciation_time,
                                         totalInvestment * self.agent.debtRatioOfInvestments, fv=1, when='end')
                net_revenues = operatingProfit - fixed_on_m_cost - pending_loan
                if powerplant.get_actual_nominal_capacity() > 0 and net_revenues <= 0:
                    price_to_bid = -1 * net_revenues / \
                                   (powerplant.capacity * powerplant.technology.peak_segment_dependent_availability)
                else:
                    pass  # if positive revenues price_to_bid remains 0
                capacity_to_bid = powerplant.capacity * powerplant.technology.peak_segment_dependent_availability
                self.reps.create_or_update_power_plant_CapacityMarket_plan(powerplant, self.agent, capacity_market,
                                                                           capacity_to_bid, \
                                                                           price_to_bid, self.futureTick)
                print(powerplant.technology.name +
                      powerplant.name + ";" + str(price_to_bid) + ";" + str(capacity_to_bid) + ";" + str(
                    operatingProfit) + ";" + str(
                    fixed_on_m_cost) + ";" + str(
                    pending_loan))

        sorted_ppdp = self.reps.get_sorted_bids_by_market_and_time(capacity_market, self.futureTick)
        capacity_market_price, total_supply_volume, isTheMarketCleared = CapacityMarketClearing.capacity_market_clearing(
            self, sorted_ppdp, capacity_market, self.futureInvestmentyear)
        capacity_market.name = "capacity_market_future"  # changing name of market to not confuse it with realized market
        self.reps.create_or_update_market_clearing_point(capacity_market, capacity_market_price, total_supply_volume,
                                                         self.futureTick)
        # peaksupply, expected_effective_operationalcapacity = self.reps.calculateEffectiveCapacityExpectedofListofPlants(
        #     self.future_installed_plants_ids, self.investable_candidate_plants)
        # expectedDemandFactor = self.reps.dbrw.get_calculated_simulated_fuel_prices_by_year("electricity",
        #                                                                                    globalNames.future_prices,
        #                                                                                    self.futureInvestmentyear)
        # peakExpectedDemand = self.peak_demand * expectedDemandFactor
        # if peaksupply > peakExpectedDemand:
        #     print("peaksupply " + str(peaksupply) + "peakExpectedDemand " + str(peakExpectedDemand))
        return capacity_market_price


    def calculate_capacity_subscription(self):
        capacity_market = self.reps.get_capacity_market_in_country(self.reps.country)

        for powerplant in self.reps.power_plants.values():
            if powerplant.id in self.future_installed_plants_ids:
                price_to_bid = 0
                operatingProfit = powerplant.get_Profit()  # for installed capacity
                fixed_on_m_cost = self.getActualFixedCostsperMW(powerplant.technology) * powerplant.capacity
                totalInvestment = self.getActualInvestedCapitalperMW(
                    powerplant.technology) * powerplant.capacity  # candidate power plants only have 1MW installed
                pending_loan = - npf.pmt(powerplant.technology.interestRate, powerplant.technology.depreciation_time,
                                         totalInvestment * self.agent.debtRatioOfInvestments, fv=1, when='end')
                net_revenues = operatingProfit - fixed_on_m_cost - pending_loan
                if powerplant.get_actual_nominal_capacity() > 0 and net_revenues <= 0:
                    price_to_bid = -1 * net_revenues / \
                                   (powerplant.capacity * powerplant.technology.peak_segment_dependent_availability)
                else:
                    pass  # if positive revenues price_to_bid remains 0
                capacity_to_bid = powerplant.capacity * powerplant.technology.peak_segment_dependent_availability
                self.reps.create_or_update_power_plant_CapacityMarket_plan(powerplant, self.agent, capacity_market,
                                                                           capacity_to_bid, \
                                                                           price_to_bid, self.futureTick)
                print(powerplant.technology.name +
                      powerplant.name + ";" + str(price_to_bid) + ";" + str(capacity_to_bid) + ";" + str(
                    operatingProfit) + ";" + str(
                    fixed_on_m_cost) + ";" + str(
                    pending_loan))

        sorted_supply = self.reps.get_sorted_bids_by_market_and_time(capacity_market, self.futureTick)

        clearing_price, total_supply_volume = CapacitySubscriptionClearing.capacity_subscription_clearing(
            self, sorted_supply, capacity_market,  self.futureInvestmentyear)
        capacity_market.name = "capacity_market_future"  # changing name of market to not confuse it with realized market
        self.reps.create_or_update_market_clearing_point(capacity_market, clearing_price, total_supply_volume,
                                                         self.futureTick)
        return clearing_price

    def group_power_plants(self):
        plants_to_delete = []
        for candidate_technology in self.reps.get_unique_candidate_technologies():
            commissionedYear = self.reps.current_year + self.look_ahead_years
            new_plants_per_tech = self.reps.get_power_plants_invested_in_tick_by_technology(commissionedYear,
                                                                                            candidate_technology.name)
            if len(new_plants_per_tech) > 1:
                grouped_plant = CandidatePowerPlant("grouped")
                for newplant in new_plants_per_tech:
                    grouped_plant.capacityTobeInstalled += newplant.capacity
                    grouped_plant.operationalProfit += newplant.operationalProfit
                    plants_to_delete.append(str(newplant.id))
                    print("removing " + str(newplant.id))
                    self.future_installed_plants_ids.remove(newplant.id)
                    if newplant.id in self.ids_of_future_installed_and_dispatched_pp:
                        self.ids_of_future_installed_and_dispatched_pp.remove(newplant.id)
                        self.pp_dispatched_names.remove(str(newplant.id))
                        self.pp_profits.drop(columns=newplant.id)

                # self.reps.dbrw.stage_id_plant_to_delete(newplant)
                grouped_plant.setActualEfficiency(newplant.actualEfficiency)
                grouped_plant.setOwner(self.agent)
                grouped_plant.setLocation(self.reps.country)
                grouped_plant.setTechnology(candidate_technology)
                grouped_plant = self.invest(grouped_plant, False)
                grouped_plant = self.calculate_investments_of_ungrouped(grouped_plant)
                self.reps.dbrw.stage_new_power_plant(grouped_plant)
                self.reps.dbrw.stage_loans(grouped_plant)
                self.reps.dbrw.stage_downpayments(grouped_plant)
        #     self.ids_of_future_installed_and_dispatched_pp.append(grouped_plant.id)

        # deleting plants that have been grouped
        self.reps.dbrw.delete_rows_DB("Id", plants_to_delete)
        # update power_plants_installed
        self.reps.dbrw.stage_installed_pp_names(self.ids_of_future_installed_and_dispatched_pp, self.futureTick)

    # Returns the Node Limit by Technology or the max double numer if none was found
    def read_csv_results_and_filter_candidate_plants(self):
        df = pd.read_csv(globalNames.amiris_results_path)
        df = df.dropna(
            subset=['VARIABLE_COSTS_IN_EURO', 'REVENUES_IN_EURO', 'CONTRIBUTION_MARGIN_IN_EURO', 'PRODUCTION_IN_MWH'])
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

    def calculate_capacity_market_from_curve(self, effectiveExpectedCapacityperTechnology, candidatepowerplant):
        capacity_market = self.reps.get_capacity_market_in_country(self.reps.country)
        expectedDemandFactor = self.reps.dbrw.get_calculated_simulated_fuel_prices_by_year("electricity",
                                                                                           globalNames.future_prices,
                                                                                           self.futureInvestmentyear)
        totalPeakDemandAtFuturePoint = self.peak_demand * expectedDemandFactor
        sdc = capacity_market.get_sloping_demand_curve(totalPeakDemandAtFuturePoint)
        clearing_price = 0
        if effectiveExpectedCapacityperTechnology[candidatepowerplant.technology.name] <= sdc.um_volume:
            clearing_price = capacity_market.PriceCap
        elif effectiveExpectedCapacityperTechnology[candidatepowerplant.technology.name] > sdc.lm_volume \
                and effectiveExpectedCapacityperTechnology[candidatepowerplant.technology.name] < sdc.um_volume:
            clearing_price = sdc.get_price_at_volume(
                effectiveExpectedCapacityperTechnology[candidatepowerplant.technology.name])
        elif effectiveExpectedCapacityperTechnology[candidatepowerplant.technology.name] > sdc.lm_volume:
            clearing_price = 0
        else:
            raise Exception
        capacityRevenue = candidatepowerplant.capacity * candidatepowerplant.technology.peak_segment_dependent_availability * clearing_price
        capacity_market.name = "capacity_market_future"  # changing name of market to not confuse it with realized market
        self.reps.create_or_update_market_clearing_point(capacity_market, clearing_price, totalPeakDemandAtFuturePoint,
                                                         self.futureTick)
        return capacityRevenue
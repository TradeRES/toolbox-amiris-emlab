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
        self.ids_of_future_installed_and_dispatched_pp = []
        self.initialization_investments = False

        if reps.current_tick == 0 and reps.testing_future_year < reps.lookAhead and reps.testing_future_year > 0:
            # Adding the investments as an initialization
            self.initialization_investments = True
            self.setTimeHorizon(reps.testing_future_year)
            self.look_ahead_years = reps.testing_future_year
        else:
            self.setTimeHorizon(reps.lookAhead)
            self.look_ahead_years = reps.lookAhead
        print("Look ahead year " + str(self.look_ahead_years))
        self.future_installed_plants_ids = reps.get_ids_of_future_installed_plants(self.futureTick)
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

    def act(self):
        # this function adds         self.AwardedPowerinMWh = results.PRODUCTION_IN_MWH / self.CostsinEUR = results.VARIABLE_COSTS_IN_EURO /
        # self.ReceivedMoneyinEUR = results.REVENUES_IN_EURO and self.operationalProfit = results.CONTRIBUTION_MARGIN_IN_EURO from csv
        self.read_csv_results_and_filter_candidate_plants()
        pp_dispatched_names = []
        pp_dispatched_ids= []
        pp_profits = []
        cp_numbers = []
        cp_profits = []
        # saving: operationalprofits from power plants in classname Profits
        for pp_id in self.ids_of_future_installed_and_dispatched_pp:
            pp = self.reps.get_power_plant_by_id(pp_id)
            pp_dispatched_names.append(pp.name)
            pp_dispatched_ids.append(pp_id)
            pp_profits.append(pp.operationalProfit)
        # todo: these variables could be removed once the model is validated
        self.reps.dbrw.stage_future_operational_profits_installed_plants(self.reps, pp_dispatched_names, pp_profits)

        if self.reps.current_tick == 0 and self.reps.testing_future_year == 0:
            # the first iteration on the first year, no investments are done, it is only to check the old power plants profits in a future market
            print(" FIRST RUN ONLY TO TEST THE MARKET")
            self.reps.dbrw.stage_future_total_profits_installed_plants(self.reps, pp_dispatched_names, pp_dispatched_ids , pp_profits, self.future_installed_plants_ids)
            print("increasing testing year by one")
            self.reps.testing_future_year += 1
            self.reps.dbrw.stage_testing_future_year(self.reps)
            self.continue_iteration()
        elif self.reps.targetinvestment_per_year == True and self.reps.target_investments_done == False:
            print("Investing according to TARGETS")
            self.reps.dbrw.stage_iteration(self.reps.investmentIteration + 1)
            new_target_power_plants = self.investbyTargets()
            for newplant in new_target_power_plants:
                self.reps.dbrw.stage_new_power_plant(newplant)
                self.reps.dbrw.stage_loans(newplant)
                self.reps.dbrw.stage_downpayments(newplant)
                self.reps.dbrw.stage_investment_decisions(newplant.candidate_name, newplant.name,
                                                          self.reps.investmentIteration,
                                                          self.futureInvestmentyear, self.reps.current_tick)
            self.reps.dbrw.stage_target_investments_done(True)
            self.continue_iteration()
            return
        else:
            self.reps.dbrw.stage_iteration(self.reps.investmentIteration + 1)
            print("Investing according to market results")
            highestNPVCandidatePP = None
            highestNPV = 0
            # power plants are investable when they havent passed the capacity limits
            self.investable_candidate_plants = self.reps.get_investable_candidate_power_plants()
            if self.investable_candidate_plants:  # check if the are investable power plants
                self.expectedInstalledCapacityPerTechnology = self.reps.calculateCapacityExpectedofListofPlants(
                    self.future_installed_plants_ids, self.investable_candidate_plants)

                for candidatepowerplant in self.investable_candidate_plants:
                    cp_numbers.append(candidatepowerplant.name)
                    cp_profits.append(candidatepowerplant.operationalProfit)
                    # calculate which is the power plant (technology) with the highest NPV
                    candidatepowerplant.specifyCandidatePPCapacity(self.reps, self.agent)
                    investable = self.calculateandCheckFutureCapacityExpectation(candidatepowerplant
                                                                                 )
                    if investable == False:
                        candidatepowerplant.setViableInvestment(False)
                        print(
                            "set to non investable " + candidatepowerplant.technology.name)
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
                    if projectvalue >= 0 and ((projectvalue / candidatepowerplant.capacity) > highestNPV):
                        highestNPV = projectvalue / candidatepowerplant.capacity  # capacity is anyways 1
                        highestNPVCandidatePP = candidatepowerplant
                    elif projectvalue < 0:
                        # the power plant should not be investable in next rounds
                        # saving if the candidate power plant remains or not as investable
                        candidatepowerplant.setViableInvestment(False)
                        self.reps.dbrw.stage_candidate_pp_investment_status(candidatepowerplant)
                    else:
                        logging.info("dont invest in this technology%s", candidatepowerplant.technology)

                # saving: operational profits from candidate plants
                self.reps.dbrw.stage_candidate_plant_results(self.reps, cp_numbers, cp_profits)
                # if the power plant is correctly saved
                if highestNPVCandidatePP is not None:
                    # investing in best candidate power plant as it passed the checks.
                    print("Investing in " + highestNPVCandidatePP.technology.name)
                    newplant = self.invest(highestNPVCandidatePP, False)
                    self.reps.dbrw.stage_new_power_plant(newplant)
                    self.reps.dbrw.stage_loans(newplant)
                    self.reps.dbrw.stage_downpayments(newplant)
                    self.reps.dbrw.stage_investment_decisions(highestNPVCandidatePP.name, newplant.name,
                                                              self.reps.investmentIteration,
                                                              self.futureInvestmentyear, self.reps.current_tick)
                    self.continue_iteration()
                else:
                    print("no more power plant to invest, saving loans, next iteration")
                    if self.initialization_investments == True:
                        print("increasing testing year by one")
                        self.reps.testing_future_year += 1
                        self.reps.dbrw.stage_testing_future_year(self.reps)
                        self.reps.dbrw.stage_iteration(0)
                        self.continue_iteration()
                        # reset all candidate power plants to investable
                        candidates_names = self.reps.get_unique_candidate_names()
                        self.reps.dbrw.stage_candidate_status_to_investable(candidates_names)
                        if self.reps.targetinvestment_per_year == True:
                            self.reps.dbrw.stage_target_investments_done(False)
                    else:
                        self.stop_iteration()
                        # saving iteration number back to zero for next year
                        self.reps.dbrw.stage_iteration(0)

                    # saving profits of installed power plants.
                    print("saving future total profits")
                    self.reps.dbrw.stage_future_total_profits_installed_plants(self.reps, pp_dispatched_names,pp_dispatched_ids, pp_profits, self.future_installed_plants_ids)
            else:
                print("all technologies are unprofitable")

    def invest(self, bestCandidatePowerPlant, target_invest):
        if self.reps.install_at_look_ahead_year == True:
            commissionedYear = self.reps.current_year + self.look_ahead_years
        else:
            print("fix this!!!!!")
            commissionedYear = self.reps.current_year + bestCandidatePowerPlant.technology.expected_permittime + bestCandidatePowerPlant.technology.expected_leadtime
        if target_invest == False:
            newid = (int(str(commissionedYear) +
                         str("{:02d}".format(
                             int(self.reps.dictionaryTechNumbers[bestCandidatePowerPlant.technology.name]))) +
                         str("{:05d}".format(int(self.new_id)))
                         ))
        else:
            newid = (int(str(commissionedYear) +
                         str("{:02d}".format(
                             int(self.reps.dictionaryTechNumbers[bestCandidatePowerPlant.technology.name]))) +
                         str("{:06d}".format(int(self.new_id)))
                         ))

        self.new_id += 1
        newplant = PowerPlant(newid)
        # in Amiris the candidate power plants are tested add a small capacity. The real candidate power plants have a bigger capacity
        newplant.specifyPowerPlantforInvest(self.reps, self.agent,
                                            bestCandidatePowerPlant.capacityTobeInstalled,
                                            bestCandidatePowerPlant.technology, self.look_ahead_years)

        print("{0} invests in technology {1} at tick {2}, with id{3}".format(self.agent.name,
                                                                             bestCandidatePowerPlant.technology.name,
                                                                             self.reps.current_tick, newid))
        # --------------------------------------------------------------------------------------Payments
        print(newplant.getActualInvestedCapital()/1000000)
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
        investmentCostperTechnology = technology.get_investment_costs_perMW_by_year(self.futureInvestmentyear)
        return investmentCostperTechnology

    def getinvestmentcosts(self, investmentCostperTechnology, time):
        # print("invest", investmentCostperTechnology, "times", pow(1.05, time))
        return investmentCostperTechnology  # TODO check: in emlab it was  pow(1.05, time of permit and construction) * investmentCostperTechnology

    def calculateandCheckFutureCapacityExpectation(self, candidatepowerplant):
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
        investable = self.check(technology, candidatepowerplant, expectedInstalledCapacityOfTechnology)
        return investable

    def check(self, technology, candidatepowerplant, expectedInstalledCapacityOfTechnology):
        technologyCapacityLimit = self.findLimitsByTechnology(technology)
        # (self.capacityOfTechnologyInPipeline > 2.0 * self.operationalCapacityOfTechnology)
        if self.capacityOfTechnologyInPipeline >= self.reps.maximum_investment_capacity_per_year:
            print(
                " will not invest in " +technology.name+" because there's too much capacity in the pipeline ")
            candidatepowerplant.setViableInvestment(False)
            return False
        elif expectedInstalledCapacityOfTechnology > technologyCapacityLimit:
            print(" will not invest in " +technology.name+" because the capacity limits are achieved")
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
        LimitinCountry = technology.getMaximumCapacityinCountry(self.futureInvestmentyear)
        if math.isnan(LimitinCountry):
            return 100000000000  # if there is no declared limit, use a very high number
        else:
            return LimitinCountry

    def investbyTargets(self):
        targetInvestors = self.reps.findTargetInvestorByCountry(self.reps.country)
        new_target_power_plants = []
        # adding the target candidate power plants
        already_investable = []
        for i in self.investable_candidate_plants:
            already_investable.append(i.technology.name)
        target_candidate_power_plants = self.reps.get_target_candidate_power_plants(already_investable)
        expectedInstalledCapacityperTechnology = self.reps.calculateCapacityExpectedofListofPlants(
            self.future_installed_plants_ids, target_candidate_power_plants)

        for target in targetInvestors:
            target_tech = self.reps.power_generating_technologies[target.targetTechnology]
            # TODO: later the expected installed power plants can be calculated according to profits not only for lookahead but also fot future time:
            expectedInstalledCapacity = expectedInstalledCapacityperTechnology[target_tech.name]
            pgt_country_limit =  self.findLimitsByTechnology(target_tech)
            # targetCapacity = target_tech.getTrend().getValue(futureTimePoint)
            # technologyTargetCapacity = self.reps.findPowerGeneratingTechnologyTargetByTechnologyandyear(target_tech,
            #                                                                                             self.futureInvestmentyear)
            yearlyCapacityTarget = self.reps.find_technology_year_target(target_tech, self.futureInvestmentyear)

            if pgt_country_limit > yearlyCapacityTarget + expectedInstalledCapacity : # limit is not reached
                pass
            else:
                yearlyCapacityTarget = pgt_country_limit - expectedInstalledCapacity
                print("limit is reached, so install the maximum")


            if yearlyCapacityTarget > 0: # if the missing capacity is smaller than a unit, then dont install anything
                #print(target.name + " needs to invest " + str(yearlyCapacityTarget) + " MW")
                targetCandidatePowerPlant = self.reps.get_candidate_by_technology(target_tech.name)
                if self.reps.install_missing_capacity_as_one_pp == True:
                    targetCandidatePowerPlant.capacityTobeInstalled = yearlyCapacityTarget
                    print("Target investing in " + target_tech.name + str(targetCandidatePowerPlant.capacityTobeInstalled))
                    newplant = self.invest(targetCandidatePowerPlant, True)
                    newplant.candidate_name = targetCandidatePowerPlant.name # changing name to be saved in investment decisions
                    new_target_power_plants.append(newplant)
                else:
                    number_new_powerplants = math.floor(yearlyCapacityTarget / targetCandidatePowerPlant.capacityTobeInstalled)
                    remainder = yearlyCapacityTarget % targetCandidatePowerPlant.capacityTobeInstalled
                    for i in range(number_new_powerplants):
                        print("Target investing in " + target_tech.name + str(targetCandidatePowerPlant.capacityTobeInstalled))
                        if i == number_new_powerplants - 1:
                            targetCandidatePowerPlant.capacityTobeInstalled += remainder
                        else:
                            pass
                        newplant = self.invest(targetCandidatePowerPlant, True)
                        newplant.candidate_name = targetCandidatePowerPlant.name # changing name to be saved in investment decisions
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

    def calculateNodeLimit(self):
        pgtLimit = getReps().findOneByTechnologyAndNode(self.technology, self.node)
        if pgtLimit is not None:
            self.pgtNodeLimit = pgtLimit.getUpperCapacityLimit(futureTimePoint)

    def setAgent(self, agent):
        self.agent = self.reps.energy_producers[agent]

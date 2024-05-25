"""
The Repository: home of all objects that play a part in the model.
All objects are read through the SpineDBReader and stored in the Repository.
Jim Hommes - 25-3-2021
Ingrid Sanchez 16-2-2022
"""
from datetime import datetime
from typing import Optional, Dict, List

import pandas as pd

from domain.CapacitySubscriptionConsumer import CapacitySubscriptionConsumer
from domain.actors import *
from domain.cashflow import CashFlow
from domain.powerplantDispatchPlan import *
from domain.technologies import *
from domain.markets import *
from domain.powerplant import *
from domain.substances import *
from domain.CandidatePowerPlant import *
from domain.trends import *
from domain.zones import *

from domain.loans import Loan
from util import globalNames
from domain.bids import Bid
from numpy import mean
from domain.StrategicReserveOperator import StrategicReserveOperator
import numpy_financial as npf


class Repository:
    """
    The Repository class reads DB data at initialization and loads all objects and relationships
    Also provides all functions that require e.g. sorting
    """

    def __init__(self):
        """
        Initialize all Repository variables
        """
        # section --------------------------------------------------------------------------------------configuration
        self.simulation_name = "test"
        self.country = ""
        self.available_years_data = False
        self.avoid_alternative = ""
        self.dbrw = None
        self.agent = ""  # TODO if there would be more agents, the future capacity should be analyzed per agent
        self.current_tick = 0
        self.time_step = 1
        self.start_simulation_year = 0
        self.end_simulation_year = 0
        self.short_term_investment_minimal_irr = 0.2
        self.lookAhead = 0
        self.pastTimeHorizon = 0
        self.current_year = 0
        self.simulation_length = 0
        self.start_tick_fuel_trends = 0
        self.start_dismantling_tick = 0
        self.initialization_investment = True
        self.load_shifter = None
        self.minimal_last_years_IRR = "NOTSET"
        self.minimal_last_years_NPV = "NOTSET"
        self.last_investable_technology = False
        self.groups_plants_per_installed_year = True
        self.scenarioWeatheryearsExcel = ""
        self.last_years_IRR_or_NPV = 0
        self.investment_initialization_years = 0  # testing the future market from the next year during initialization investment_initialization_years
        self.typeofProfitforPastHorizon = ""
        self.max_permit_build_time = 0
        self.runningModule = ""
        self.npv_with_annuity = False
        self.fix_fuel_prices_to_year = False
        self.fix_price_year = 2030
        self.writeALLcostsinOPEX = False
        self.fix_profiles_to_representative_year = True
        self.fix_demand_to_representative_year = True
        self.increase_demand = False
        self.iteration_weather = "NOTSET"
        self.Power_plants_from_year = 2019
        self.install_at_look_ahead_year = True
        # section --------------------------------------------------------------------------------------investments
        self.investmentIteration = 0
        self.targetinvestment_per_year = True
        # self.testing_intermittent_technologies = True
        # self.test_first_intermittent_technologies = False
        self.target_investments_done = False
        self.install_missing_capacity_as_one_pp = True
        self.decommission_from_input = False
        self.realistic_candidate_capacities_tobe_installed = False
        self.realistic_candidate_capacities_to_test = False
        self.maximum_investment_capacity_per_year = 0
        self.dummy_capacity_to_be_installed = 1000
        self.dummy_capacity_to_test = 1
        self.run_quick_investments = False
        self.capacity_remuneration_mechanism = None
        self.maximum_installed_share_initialization = 0.1
        self.round_for_capacity_market_y_1 = False
        self.hours_in_year = 8760
        self.change_IRR = False
        self.factor_fromVOLL = 1
        self.reliability_option_strike_price = "NOTSET"

        # section --------------------------------------------------------------------------------------configuration
        self.dictionaryFuelNames = dict()
        self.dictionaryFuelNumbers = dict()
        self.dictionaryTechNumbers = dict()
        self.dictionaryTechSet = dict()
        # -----------------------------------------------------------------------------------------------Objects
        self.newTechnology = dict()
        self.energy_producers = dict()
        self.target_investors = dict()
        self.power_plants = dict()
        self.candidatePowerPlants = dict()
        self.substances = dict()
        self.power_plants_fuel_mix = dict()
        self.electricity_spot_markets = dict()
        self.capacity_markets = dict()
        self.co2_markets = dict()
        self.power_plant_dispatch_plans = dict()
        self.power_plant_dispatch_plans_in_year = dict()
        self.bids = dict()
        self.power_generating_technologies = dict()
        self.loadShifterDemand = dict()
        self.market_clearing_points = dict()
        self.loadShedders = dict()
        self.power_grid_nodes = dict()
        self.trends = dict()
        self.zones = dict()
        self.national_governments = dict()
        self.governments = dict()
        self.candidatesNPV = dict()
        self.weatherYears = dict()
        self.investmentDecisions = dict()
        self.installedCapacity = dict()
        self.installedFuturePowerPlants = dict()
        self.plantsinCM = dict()
        self.bigBank = BigBank("bank")
        self.manufacturer = PowerPlantManufacturer("manufacturer")
        self.decommissioned = dict()
        self.market_stability_reserves = dict()
        self.load = dict()
        self.emissions = dict()
        self.exports = dict()
        self.marketForSubstance = {}
        self.electricitySpotMarketForNationalGovernment = {}
        self.electricitySpotMarketForPowerPlant = {}
        self.loansFromAgent = {}
        self.loansToAgent = {}
        self.powerPlantsForAgent = {}
        self.loanList = dict()
        self.financialPowerPlantReports = dict()
        self.profits = dict()
        # Create list of plants in SR
        self.plants_in_SR = []
        self.bids_sr = dict()
        # Create Strategic Reserve Operator
        self.sr_operator = dict()
        self.cs_consumers = dict()

    """
    Repository functions:
    All functions to get/create/set/update elements and values, possibly under criteria. Sorted on elements.
    """

    # ----------------------------------------------------------------------------section loans
    def createLoan(self, from_agent: str, to: str, amount, numberOfPayments, loanStartTime, donePayments, plant):
        loan = Loan()
        loan.setFrom(from_agent)
        loan.setTo(to)
        loan.setAmountPerPayment(amount)
        loan.setTotalNumberOfPayments(numberOfPayments)
        loan.setLoanStartTime(loanStartTime)
        loan.setNumberOfPaymentsDone(donePayments)
        plant.setLoan(loan)
        return loan

    def createDownpayment(self, from_agent: str, to: str, amount, numberOfPayments, loanStartTime, donePayments, plant):
        loan = Loan()
        loan.setFrom(from_agent)
        loan.setTo(to)
        loan.setAmountPerPayment(amount)
        loan.setTotalNumberOfPayments(numberOfPayments)
        loan.setLoanStartTime(loanStartTime)
        loan.setNumberOfPaymentsDone(donePayments)
        plant.setDownpayment(loan)
        return loan

    def determineLoanAnnuities(self, totalLoan, payBackTime, interestRate):  # same results see npvtest.py
        annuity = npf.pmt(interestRate, payBackTime, totalLoan, fv=0, when='end')
        #        annuity_like_emlab = (totalLoan * interestRate) / (1 - ((1+interestRate)**(-interestRate)))
        # annuitybyhand = (totalLoan * interestRate) / (1 - ((1 + interestRate) ** (-interestRate)))
        # annuity_like_emlab = totalLoan * ((1 + interestRate) ** payBackTime * (interestRate)) / (
        #        (1 + interestRate) ** payBackTime - 1)
        return - annuity

    def findLoansFromAgent(self, agent):
        return self.loansFromAgent.get(agent)

    def findLoansToAgent(self, agent):
        return self.loansToAgent.get(agent)

    # ----------------------------------------------------------------------------section Cashflow
    def createCashFlow(self, from_agent: object, to: object, amount, type, time, plant):
        cashFlow = CashFlow()
        cashFlow.setFrom(from_agent.name)
        cashFlow.setTo(to.name)
        cashFlow.setMoney(amount)
        cashFlow.setType(type)
        cashFlow.setTime(time)
        # cashFlow.setRegardingPowerPlant(plant)
        from_agent.setCash(from_agent.getCash() - amount)
        if to is not None:
            to.setCash(to.getCash() + amount)
        # cashFlows.add(cashFlow)
        return cashFlow

    def get_profits_per_tick(self, tick):  # profits are being saved in the investment step
        try:  # tick is the simulation tick, but the profits are for the future expected years.
            return next(i for i in self.profits.values() if i.name == str(tick))
        except StopIteration:
            return None

    def get_CM_revenues(self, plant_name):
        try:
            return next(
                i.capacityMarketRevenues for i in self.financialPowerPlantReports.values() if i.name == plant_name)
        except StopIteration:
            return pd.Series()

    def get_operational_profits_pp(self, plant_name):
        try:  # this is only to compare with expected value In reality fixed costs are increased each year by eg .001
            return next(
                i.spotMarketRevenue - i.variableCosts for i in
                self.financialPowerPlantReports.values() if i.name == plant_name)
            # + (self.power_generating_technologies[test_tech].fixed_operating_costs * self.power_plants[plant_name].capacity)
        except StopIteration:
            return None

    def get_financial_report_for_plant_KPI(self, plant_name, KPI):
        try:
            return next(getattr(i, KPI) for i in self.financialPowerPlantReports.values() if i.name == plant_name)
        except StopIteration:
            return None

    def get_financial_report_for_plant(self, plant_name):
        try:
            return next(i for i in self.financialPowerPlantReports.values() if i.name == plant_name)
        except StopIteration:
            return None

    def get_totalProfitswLoans_for_plant(self, plant_name):
        try:
            return next(i.totalProfitswLoans for i in self.financialPowerPlantReports.values() if i.name == plant_name)
        except StopIteration:
            return None

    def get_irrs_for_plant(self, plant_name):
        try:
            return next(i.irr for i in self.financialPowerPlantReports.values() if i.name == plant_name)
        except StopIteration:
            return None

    def get_npvs_for_plant(self, plant_name):
        try:
            return next(i.npv for i in self.financialPowerPlantReports.values() if i.name == plant_name)
        except StopIteration:
            return None

    def get_total_profits_for_plant(self, plant_name):
        try:
            return next(i.totalProfits for i in self.financialPowerPlantReports.values() if i.name == plant_name)
        except StopIteration:
            return None

    def getCashFlowsForEnergyProducer(self, energyproducer):
        try:
            return next(i for i in self.energy_producers.values() if i.name == energyproducer)
        except StopIteration:
            return None
        # [cf for cf in self.reps.cashFlows.getRegardingPowerPlant(plant) ][tick]
        #  return cashFlows.stream().filter(lambda p : p.getTime() == tick).filter(lambda p : p.getRegardingPowerPlant() is not None).filter(lambda p : p.getRegardingPowerPlant() is plant).collect(Collectors.toList())

    #
    # def determineLoanAnnuities(self, totalLoan, payBackTime, interestRate):
    #     q = 1 + interestRate
    #     annuity = totalLoan * (q ** payBackTime * (q - 1)) / (q ** payBackTime - 1)
    #     return annuity
    def create_or_update_power_plant_loan(self, plant: PowerPlant,
                                          bidder: EnergyProducer,
                                          bidding_market: Market,
                                          amount: float,
                                          price: float,
                                          time: int) -> PowerPlantDispatchPlan:
        ppdp = next((ppdp for ppdp in self.power_plant_dispatch_plans_in_year.values() if ppdp.plant == plant and
                     ppdp.bidding_market == bidding_market and
                     ppdp.tick == time), None)
        pass

    # Governments
    def get_national_government_by_zone(self, zone: Zone) -> NationalGovernment:
        return next(i for i in self.national_governments.values() if i.governed_zone == zone)

    def get_government(self) -> Government:
        return next(i for i in self.governments.values())

    # PowerGridNode
    def get_power_grid_node_by_zone(self, zone: str):
        try:
            return next(i for i in self.power_grid_nodes.values() if i.parameters['Country'] == zone)
        except StopIteration:
            return None

    def get_realized_peak_demand_by_year(self, year):
        """
        saved in future market preparation,
        """
        try:
            return next(i.realized_demand_peak.loc[year] for i in self.electricity_spot_markets.values() if
                        i.country == self.country)
        except StopIteration:
            return None

    def get_peak_future_demand_by_year(self, year):
        """
        saved in future market preparation, exclude industrial load and electrolyzers (only static demand)
        """
        try:
            # the load was already updated in the clock step
            return next(i.future_demand_peak.loc[year] for i in self.electricity_spot_markets.values() if
                        i.country == self.country)
        except StopIteration:
            return None

    def get_percentage_load_LS(self, name):
        """
        saved in future market preparation, exclude industrial load and electrolyzers (only static demand)
        """
        try:
            # the load was already updated in the clock step
            return next(i.percentageLoad for i in self.loadShedders.values() if
                        i.name == name)
        except StopIteration:
            return None




    def get_peak_future_demand(self):
        try:
            # the load was already updated in the clock step
            return next(
                i.future_demand_peak for i in self.electricity_spot_markets.values() if i.country == self.country)
        except StopIteration:
            return None

    def get_realized_peak_demand(self):
        try:
            # the load was already updated in the clock step
            return next(
                i.realized_demand_peak for i in self.electricity_spot_markets.values() if i.country == self.country)
        except StopIteration:
            return None


    def get_capacity_under_long_term_contract(self, forward_years_CM):
        capacity_under_long_term_market = [i.capacity * i.technology.deratingFactor
                                           for i in self.power_plants.values() if
                                           self.power_plant_still_in_reserve( i, forward_years_CM)
                                          ]
        return sum(capacity_under_long_term_market)

    # ----------------------------------------------------------------------------section technologies
    # PowerGeneratingTechnologies
    def get_power_generating_technology_by_techtype_and_fuel(self, techtype: str, fuel: str):
        try:
            return next(i for i in self.power_generating_technologies.values()
                        if i.techtype == techtype and i.fuel == fuel)
        except StopIteration:
            logging.warning('PowerGeneratingTechnology not found for ' + techtype + ' and ' + fuel)
            return None

    def get_unique_technologies_names(self):
        try:
            return [i.name for i in self.power_generating_technologies.values()]
        except StopIteration:
            return None

    def get_allowed_technology_with_highest_availability(self, allowed_technologies):
        max_number = max(self.candidatePowerPlants,
                         key=lambda x: self.candidatePowerPlants[x].technology.deratingFactor
                         if self.candidatePowerPlants[x].technology.name in allowed_technologies else 0)
        return self.candidatePowerPlants[max_number].technology.name

    def get_unique_substances_names(self):
        try:
            return [i.name for i in self.substances.values()]
        except StopIteration:
            return None

    # SubstanceInFuelMix
    def get_substances_in_fuel_mix_by_plant(self, plant: PowerPlant) -> Optional[SubstanceInFuelMix]:
        if plant.technology.name in self.power_plants_fuel_mix.keys():
            return self.power_plants_fuel_mix[plant.technology.name]
        else:
            return None

    # ----------------------------------------------------------------------------section Candidate
    def get_candidate_power_plants_of_technologies(self, technologies) -> List[CandidatePowerPlant]:
        return [i for i in self.candidatePowerPlants.values() if i.technology in technologies]

    def get_investable_candidate_power_plants_by_owner(self, owner: EnergyProducer) -> List[CandidatePowerPlant]:
        return [i for i in self.candidatePowerPlants.values()
                if i.viableInvestment is True and i.owner == owner]

    def get_candidate_capacity(self, tech):
        return next(i.capacityTobeInstalled for i in self.candidatePowerPlants.values() if i.technology.name == tech)

    def get_candidate_name_by_technology(self, tech):
        return next(i.name for i in self.candidatePowerPlants.values() if i.technology.name == tech)

    def get_candidate_by_technology(self, tech):
        return next(i for i in self.candidatePowerPlants.values() if i.technology.name == tech)

    def get_investable_and_targeted_candidate_power_plants(self) -> List[CandidatePowerPlant]:
        return [i for i in self.candidatePowerPlants.values() if i.viableInvestment is True and
                i.technology.name in globalNames.vRES
                ]

    def get_ids_of_plants(self,list_of_dicts):
        ids = []
        for dictionary in list_of_dicts:
            # Iterate through each dictionary in the list
            if dictionary:  # Check if the dictionary is not empty
                ids.append(dictionary.id)
        return ids

    def get_investable_candidate_power_plants(self) -> List[CandidatePowerPlant]:
        return [i for i in self.candidatePowerPlants.values() if i.viableInvestment is True]

    def get_investable_candidate_power_plants_minimal_irr_or_npv(self) -> List[CandidatePowerPlant]:
        investable_candidates = self.get_investable_candidate_power_plants()
        if self.minimal_last_years_IRR != "NOTSET":
            self.filter_candidates_by_minimal_irr(investable_candidates)
            return self.get_investable_candidate_power_plants()
        elif self.minimal_last_years_NPV != "NOTSET":
            self.filter_candidates_by_minimal_npv(investable_candidates)
            return self.get_investable_candidate_power_plants()
        else:
            return investable_candidates

    def filter_candidates_by_minimal_irr(self, investable_candidates):
        simulation_years = list(range(self.current_tick - self.last_years_IRR_or_NPV, self.current_tick + 1))
        irrs_per_tech_per_year = pd.DataFrame(index=simulation_years).fillna(0)
        for candidate in investable_candidates:
            powerplants_per_tech = self.get_power_plants_by_technology(candidate.technology.name)
            irrs_per_year = pd.DataFrame(index=simulation_years).fillna(0)
            for plant in powerplants_per_tech:
                irr_per_plant = self.get_irrs_for_plant(plant.name)
                if irr_per_plant is None:
                    pass
                else:
                    irrs_per_year[plant.name] = irr_per_plant
            irrs_per_year.replace(to_replace=-100, value=np.nan,
                                  inplace=True)  # the -100 was hard coded in the financial reports
            if irrs_per_year.size != 0:
                irrs_per_tech_per_year[candidate.technology.name] = np.nanmean(irrs_per_year, axis=1)
        meanirr = irrs_per_tech_per_year.mean()

        for candidatepowerplant in investable_candidates:
            if candidatepowerplant.technology.name in meanirr.index.values:
                if meanirr[candidatepowerplant.technology.name] >= self.minimal_last_years_IRR:
                    pass
                else:
                    candidatepowerplant.setViableInvestment(False)
                    self.dbrw.stage_candidate_pp_investment_status(candidatepowerplant)
        return

    def filter_candidates_by_minimal_npv(self, investable_candidates):
        simulation_years = list(range(self.current_tick - self.last_years_IRR_or_NPV, self.current_tick + 1))
        npvs_per_tech_per_MW = pd.DataFrame(index=simulation_years).fillna(0)
        for candidate in investable_candidates:
            powerplants_per_tech = self.get_power_plants_by_technology(candidate.technology.name)
            npvs_per_year_perMW = pd.DataFrame(index=simulation_years).fillna(0)
            for plant in powerplants_per_tech:
                npv_per_plant = self.get_npvs_for_plant(plant.name)
                if npv_per_plant is None:
                    pass
                else:
                    npvs_per_year_perMW[plant.name] = npv_per_plant
            if npvs_per_year_perMW.size != 0:
                npvs_per_tech_per_MW[candidate.technology.name] = np.nanmean(npvs_per_year_perMW, axis=1)
        mean_npv = npvs_per_tech_per_MW.mean()
        for candidatepowerplant in investable_candidates:
            if candidatepowerplant.technology.name in mean_npv.index.values:
                if mean_npv[candidatepowerplant.technology.name] >= self.minimal_last_years_NPV:
                    pass
                else:
                    print("due to last irrs not investable" + candidatepowerplant.technology.name)
                    candidatepowerplant.setViableInvestment(False)
                    self.dbrw.stage_candidate_pp_investment_status(candidatepowerplant)
        return

    def get_target_technologies(self):
        return [i.targetTechnology for i in self.target_investors.values()]

    def get_target_candidate_power_plants(self, already_investable) -> List[CandidatePowerPlant]:
        target_technologies = self.get_target_technologies()
        return [i for i in self.candidatePowerPlants.values() if
                i.technology.name in target_technologies and i.technology.name not in already_investable]

    def update_candidate_plant_results(self, results):
        for index, result in results.iterrows():
            try:
                candidate = next(i for i in self.candidatePowerPlants.values() if i.id == result.identifier)
                if candidate is not None:
                    candidate.add_values_from_df(result)
            except StopIteration:
                logging.warning('candidate technology not found' + str(result.identifier))
        return None

    def get_unique_candidate_technologies_names(self):
        try:
            return [i.technology.name for name, i in self.candidatePowerPlants.items()]
        except StopIteration:
            return None

    def get_intermittent_technologies_names(self):
        try:
            return [i.name for i in self.power_generating_technologies.values() if i.intermittent == True]
        except StopIteration:
            return None

    def get_unique_candidate_technologies(self):
        try:
            return [i.technology for name, i in self.candidatePowerPlants.items()]
        except StopIteration:
            return None

    def get_technologies_except_marginals_for_CM(self, allowed_technologies_capacity_market):
        try:
            return [i.technology for name, i in self.candidatePowerPlants.items() if
                    i.technology.name not in allowed_technologies_capacity_market]
        except StopIteration:
            return None

    def get_unique_candidate_names(self):
        try:
            return [name for name, i in self.candidatePowerPlants.items()]
        except StopIteration:
            return None

    # ----------------------------------------------------------------------------section PowerPlants

    def get_ids_of_future_installed_plants(self, futuretick) -> list:
        # the installed power plants include the ones invested in previous iterations
        return self.installedFuturePowerPlants["All"].installed_ids[futuretick]

    def get_id_last_power_plant(self) -> int:
        # the last 5 numbers are the power plant list
        sorted_ids = sorted([str(i.id)[-4:] for i in self.power_plants.values()])
        return sorted_ids[-1]

    def get_power_plant_by_id(self, id):
        try:
            return next(i for i in self.power_plants.values() if i.id == int(id))
        except StopIteration:
            return None

    def get_power_plant_name_by_id(self, id):
        try:
            return next(i.name for i in self.power_plants.values() if i.id == int(id))
        except StopIteration:
            return None

    def get_power_plant_by_name(self, name):
        try:
            return next(i for i in self.power_plants.values() if i.name == name)
        except StopIteration:
            return None

    def get_power_plants_in_CM(self, tick):
        try:
            return next(i.plantsinCM for i in self.plantsinCM.values() if i.name == str(tick))
        except StopIteration:
            return None

    def get_average_profits(self, powerplants):
        return mean([pp.get_Profit() for pp in powerplants])

    def calculateCapacityExpectedofListofPlants(self, future_installed_plants_ids, investable_candidate_plants,
                                                investbyTarget):
        expectedOperationalcapacity = dict()
        for candidate in investable_candidate_plants:
            capacity = 0
            for plant in self.power_plants.values():
                if plant.id in future_installed_plants_ids:  # this list was kept in the future expected power plants
                    if plant.technology.name == candidate.technology.name:
                        capacity += plant.capacity

            if investbyTarget == True and self.install_missing_capacity_as_one_pp == True:
                pass
            else:
                capacity += candidate.capacityTobeInstalled
            expectedOperationalcapacity[candidate.technology.name] = capacity
        return expectedOperationalcapacity

    def calculateEffectiveCapacityExpectedofListofPlants(self, future_installed_plants_ids,
                                                         investable_candidate_plants):

        peaksupply = 0
        for plant in self.power_plants.values():
            if plant.id in future_installed_plants_ids:  # this list was kept in the future expected power plants
                peaksupply += plant.capacity * plant.technology.deratingFactor
        expected_effective_operationalcapacity = dict()
        for candidate in investable_candidate_plants:
            # capacity from installed power plant
            capacity = 0
            capacity = peaksupply + (
                    candidate.capacityTobeInstalled * candidate.technology.deratingFactor)
            expected_effective_operationalcapacity[candidate.technology.name] = capacity
        return peaksupply, expected_effective_operationalcapacity

    def calculateCapacityOfOperationalPowerPlantsByTechnology(self, technology):
        """ in the market preparation file, the plants that are decommissioned are filtered out,
        so there should not be any left as to be decommissioned"""
        plantsoftechnology = [i.capacity for i in self.power_plants.values() if i.technology.name == technology.name
                              and i.status in [globalNames.power_plant_status_operational,
                                               globalNames.power_plant_status_to_be_decommissioned,
                                               globalNames.power_plant_status_strategic_reserve]]
        return sum(plantsoftechnology)

    def calculateEffecticeCapacityOfOperationalPowerPlants(self):
        plantsoftechnology = [
            i.capacity * self.power_generating_technologies[i.technology.name].deratingFactor
            for i in self.power_plants.values() if i.status in [globalNames.power_plant_status_operational,
                                                                globalNames.power_plant_status_to_be_decommissioned,
                                                                globalNames.power_plant_status_strategic_reserve]]
        return sum(plantsoftechnology)

    def calculate_marginal_costs(self, powerplant, year_ahead):
        simulation_year = year_ahead + self.current_year
        fuel = powerplant.technology.fuel
        variable_costs = powerplant.technology.get_variable_operating_by_time_series(
            powerplant.age + year_ahead)

        fuel_price = fuel.get_price_for_tick(self, simulation_year, True)
        co2_TperMWh = fuel.co2_density
        co2price = self.substances["CO2"].get_price_for_tick(self, simulation_year, True)
        commodities = (powerplant.technology.variable_operating_costs + (fuel_price + co2price * co2_TperMWh) /
                       powerplant.technology.get_efficiency_by_time_series(
                           powerplant.age + year_ahead))
        return variable_costs + commodities

    def calculate_marginal_costs_by_technology(self, technology_name, year_ahead):
        if self.runningModule == "run_future_market":
            run_future_market = True
        else:
            run_future_market = False
        technology = self.power_generating_technologies[technology_name]
        simulation_year = year_ahead + self.current_year
        fuel = technology.fuel
        variable_costs = technology.get_variable_operating_by_time_series(year_ahead)
        fuel_price = self.substances[technology.fuel.name].get_price_for_tick(self, simulation_year, run_future_market)
        co2_TperMWh = fuel.co2_density
        co2price = self.substances["CO2"].get_price_for_tick(self, simulation_year, run_future_market)
        commodities = (technology.variable_operating_costs + (fuel_price + co2price * co2_TperMWh) /
                       technology.get_efficiency_by_time_series(year_ahead))
        return variable_costs + commodities

    def calculateCapacityOfPowerPlantsByTechnologyInPipeline(self, technology):
        return sum([pp.capacity for pp in self.power_plants.values() if pp.technology.name == technology.name
                    and pp.status == globalNames.power_plant_status_inPipeline])  # pp.isInPipeline(tick)

    def calculateCapacityOfPowerPlantsByTechnologyInstalledinYear(self, commissionedYear, technology):
        new_power_plants = self.get_power_plants_invested_in_tick_by_technology(commissionedYear, technology.name)
        return sum([pp.capacity for pp in new_power_plants])

    def calculateCapacityOfPowerPlantsInPipeline(self):
        return sum(
            [i.capacity for i in self.power_plants.values() if i.status == globalNames.power_plant_status_inPipeline])

    def findPowerGeneratingTechnologyTargetByTechnologyandyear(self, technology, year):
        try:
            from_year = self.start_simulation_year
            last_year = self.end_simulation_year
            to_year = year
            return next(
                i.get_cummulative_capacity(from_year, to_year, last_year) for i in self.target_investors.values() if
                i.targetTechnology == technology.name and i.targetCountry == self.country)
        except StopIteration:
            logging.warning('No yearly target for this year.' + str(year))
        return None

    def find_technology_year_target(self, technology, year):
        try:
            return next(i.yearly_increment[year] for i in self.target_investors.values() if
                        i.targetTechnology == technology.name and i.targetCountry == self.country)
        except StopIteration:
            logging.warning('No yearly target for this year.' + str(year))
        return None

    def findTargetInvestorByCountry(self, country):
        return [i for i in self.target_investors.values() if i.targetCountry == country]

    # def findAllPowerPlantsWithConstructionStartTimeInTick(self, tick):
    #     return [i for i in self.power_plants if i.getConstructionStartTick() == tick]

    # def findAllPowerPlantsWhichAreNotDismantledBeforeTick(self, tick):
    #     return [i for i in self.power_plants.values() if i.isWithinTechnicalLifetime(tick)]

    def get_operational_power_plants_by_owner(self, owner: EnergyProducer) -> List[PowerPlant]:
        return [i for i in self.power_plants.values()
                if i.owner == owner and i.status == globalNames.power_plant_status_operational]

    def get_operational_and_to_be_decommissioned_but_no_RES(self) -> List[PowerPlant]:
        return [i for i in self.power_plants.values()
                if i.technology.intermittent == False and (
                        i.status == globalNames.power_plant_status_operational
                        or i.status == globalNames.power_plant_status_to_be_decommissioned)]

    def get_operational_and_to_be_decommissioned(self, forward_years_CM) -> List[PowerPlant]:
        """
        operational plants and plants that could not reach maximum lifetime extension
        """
        return [i for i in self.power_plants.values() if
                (i.status in [globalNames.power_plant_status_operational,
                              globalNames.power_plant_status_to_be_decommissioned] and
                 (i.age + forward_years_CM) <= (i.technology.expected_lifetime + i.technology.maximumLifeExtension)
                 or (i.status == globalNames.power_plant_status_inPipeline and i.age + forward_years_CM >= 0)
                 )]

    def get_plants_that_can_be_operational_not_in_ltcm(self, forward_years_CM) -> List[
        PowerPlant]:
        """
        power plant hasnt passed lifetime or it will not longer be in long term capacity market
        """
        return [i for i in self.power_plants.values() if
             (i.age + forward_years_CM) <= (i.technology.expected_lifetime + i.technology.maximumLifeExtension)
             and self.power_plant_still_in_reserve(i, forward_years_CM ) == False
             ]

    def power_plant_still_in_reserve(self, powerplant, forward_years_CM):
        return powerplant.last_year_in_capacity_market > (forward_years_CM + self.current_year) and powerplant.last_year_in_capacity_market != 0

    def power_plant_in_ltcm(self, powerplant):
        return powerplant.last_year_in_capacity_market != 0


    def get_power_plants_by_status(self, list_of_status: list) -> List[PowerPlant]:
        return [i for i in self.power_plants.values()
                if i.status in list_of_status]
    def get_power_plants_if_target_invested(self) -> List[PowerPlant]:
        return [i for i in self.power_plants.values()
                if len(str(i.id)) == 12]

    def get_operational_power_plants_by_owner_and_technologies(self, owner: EnergyProducer, listofTechnologies) -> List[
        PowerPlant]:
        return [i for i in self.power_plants.values()
                if
                i.owner.name == owner and i.status == globalNames.power_plant_status_operational and i.technology.name in listofTechnologies]

    def get_power_plants_by_technology(self, technology_name):
        return [i for i in self.power_plants.values()
                if i.technology.name == technology_name]

    def get_investments(self) -> List[PowerPlant]:
        return [i for i in self.power_plants.values()
                if i.status == globalNames.power_plant_status_operational]

    def get_load_shedder_by_VOLL(self, VOLL):
        try:
            return next(i.name for i in self.loadShedders.values() if i.VOLL == VOLL)
        except StopIteration:
            return None

    def get_power_plants_invested_in_future_tick(self, futuretick) -> List[PowerPlant]:
        year = futuretick + self.start_simulation_year
        return [i for i in self.power_plants.values()
                if i.name[:4] == str(year)]

    def get_power_plants_invested_in_tick_by_technology(self, commissionedYear, technology_name) -> List[PowerPlant]:
        return [i for i in self.power_plants.values()
                if i.name[:4] == str(commissionedYear) and i.technology.name == technology_name]

    def get_power_plants_by_owner(self, owner: str) -> List[PowerPlant]:
        return [i for i in self.power_plants.values()
                if i.owner.name == owner]

    # def get_power_plants_commissioned_inyear(self, year) -> List[PowerPlant]:
    #     return [i.name for i in self.power_plants.values()
    #             if i.commissionedYear == year]

    def get_power_plants_to_be_decommissioned(self, owner) -> List[PowerPlant]:
        return [i for i in self.power_plants.values()
                if i.owner.name == owner and i.status == globalNames.power_plant_status_to_be_decommissioned]

    def get_plants_to_be_decommissioned_and_inSR(self, forward_years_SR, powerplant) -> List[PowerPlant]:
        # operational power plants should not enter the SR because
        # then the lifetime of the power plant can be reduced, which is undesirable
        # unless they are about to be decommissioned
        if powerplant.technology.intermittent == False and powerplant.technology.name not in globalNames.technologies_not_in_SR and \
            ((powerplant.status == globalNames.power_plant_status_operational \
                     and powerplant.age - powerplant.technology.expected_lifetime >= -forward_years_SR)
             or powerplant.status in [globalNames.power_plant_status_to_be_decommissioned,
                          globalNames.power_plant_status_strategic_reserve]):
            return True
        else:
            return False

    def get_power_plant_operational_profits_by_tick_and_market(self, time: int, market: Market):
        res = 0
        for power_plant in [i for i in self.power_plants.values() if
                            i.status == globalNames.power_plant_status_operational]:
            revenues = self.get_power_plant_electricity_spot_market_revenues_by_tick(power_plant, time)
            mc = power_plant.calculate_marginal_cost_excl_co2_market_cost(self, time)
            total_capacity = self.get_total_accepted_amounts_by_power_plant_and_tick_and_market(power_plant, time,
                                                                                                market)
            res[power_plant.name] = revenues - mc * total_capacity
        return res

    def get_available_power_plant_capacity_at_tick(self, plant: PowerPlant, current_tick: int) -> float:
        ppdps_sum_accepted_amount = sum([float(i.accepted_amount) for i in
                                         self.get_power_plant_dispatch_plans_by_plant(plant)
                                         if i.tick == current_tick])
        return plant.capacity - ppdps_sum_accepted_amount

    def get_power_plant_emissions_by_tick(self, time: int) -> Dict[str, float]:
        if 'YearlyEmissions' in self.emissions.keys():
            res = self.emissions['YearlyEmissions'].emissions[time]
        else:
            res = {}
        for power_plant in [i for i in self.power_plants.values() if
                            i.status == globalNames.power_plant_status_operational and i.name not in res.keys()]:
            # Total Capacity is in MWh
            total_capacity = self.get_total_accepted_amounts_by_power_plant_and_tick_and_market(power_plant, time,
                                                                                                self.electricity_spot_markets[
                                                                                                    'DutchElectricitySpotMarket'])
            # Emission intensity is in ton CO2 / MWh
            emission_intensity = power_plant.calculate_emission_intensity(self)
            res[power_plant.name] = total_capacity * emission_intensity
        return res

    def get_power_plant_electricity_dispatch(self, power_plant_id: str) -> float:
        try:
            return self.power_plant_dispatch_plans_in_year.get(str(power_plant_id))
        except StopIteration:
            logging.warning('No PPDP Price found for plant' + str(power_plant_id))
        return 0

    def get_expected_profits_by_tick(self, power_plant_name: int, tick: int) -> float:
        if hasattr(self.power_plants[power_plant_name], 'expectedTotalProfits'):
            if tick in self.power_plants[power_plant_name].expectedTotalProfits.index:
                return self.power_plants[power_plant_name].expectedTotalProfits.loc[tick]
            else:
                return None
        else:
            return None

    def get_total_accepted_amounts_by_power_plant_and_tick_and_market(self, power_plant: PowerPlant, time: int,
                                                                      market: Market) -> float:
        return sum([i.accepted_amount for i in self.power_plant_dispatch_plans_in_year.values() if i.tick == time and
                    i.plant == power_plant and i.bidding_market == market])

    def get_sorted_bids_by_market_and_time(self, market: Market, time: int) -> \
            List[PowerPlantDispatchPlan]:
        return sorted([i for i in self.bids.values()
                       if i.market == market.name and i.tick == time], key=lambda i: i.price)


    def get_power_plant_dispatch_plans_by_plant(self, plant: PowerPlant) -> List[PowerPlantDispatchPlan]:
        return [i for i in self.power_plant_dispatch_plans_in_year.values() if i.plant == plant]

    def get_all_power_plant_dispatch_plans_by_tick(self, tick: int) -> \
            List[PowerPlantDispatchPlan]:
        try:
            #  return next(i for i in self.power_plant_dispatch_plans.values() if str(int(float(i.name))) == str(tick))
            return next(i for i in self.power_plant_dispatch_plans.values() if str(i.name) == str(tick))
        except StopIteration:
            return None

        # ----------------------------------------------------------------------------section Capacity Mechanisms

    def get_load_shedders_not_hydrogen(self):
        return [i for i in self.loadShedders.values() if i.name != "hydrogen"]

    def get_sorted_load_shedders_by_increasing_VOLL_no_hydrogen(self, reverse) -> \
            List[LoadShedder]:
        return sorted([i for i in self.loadShedders.values() if
                       i.name != "hydrogen"], key=lambda i: i.VOLL, reverse=reverse)

    def get_sorted_load_shedders_by_increasingVOLL(self) -> \
            List[LoadShedder]:
        sorted_load_shedders = sorted([i for i in self.loadShedders.values() if
                                       i.name != "hydrogen"], key=lambda i: i.VOLL, reverse=False)
        sorted_load_shedders.append(self.loadShedders["hydrogen"])
        return sorted_load_shedders

    def get_sorted_load_shedders_by_name(self, name) -> \
            List[LoadShedder]:
        return next(i for i in self.loadShedders.values() if i.name == name)

    def get_strategic_reserve_operator(self, zone) -> Optional[StrategicReserveOperator]:
        try:
            return next(i for i in self.sr_operator.values() if
                        i.zone == zone)
        except StopIteration:
            return None

    def get_CS_consumer_descending_WTP(self):
        try:
            return sorted(self.cs_consumers.values(), key=lambda x: x.WTP, reverse=True)
        except StopIteration:
            return None


    def get_CS_subscribed_consumers_descending_bid(self):
        try:
            # subscribed = [i for i in self.cs_consumers.values() if i.subscribed_yearly > 0]
            # unsubscribed = CapacitySubscriptionConsumer("unsubscribed")
            # unsubscribed.bid = 0
            # unsubscribed.subscribed_yearly = 1 - sum([i.subscribed_yearly for i in self.cs_consumers.values()])
            # subscribed.append(unsubscribed)
            subscribed = [i for i in self.cs_consumers.values()]
            return sorted(subscribed , key=lambda x: x.bid, reverse=True)
        except StopIteration:
            return None

    def get_last_year_bid(self, name):
        try:
            return next(i.bid[self.current_tick - 1] for i in self.cs_consumers.values() if i.name == name)
        except StopIteration:
            return None

    def get_subscribed_yearly(self, name, tick):
        try:
            return next( round(i[tick],3) for i in self.cs_consumers.values() if i.name == name)
        except StopIteration:
            return None


    def get_capacity_market_for_plant(self, plant: PowerPlant) -> Optional[CapacityMarket]:
        try:
            return next(i for i in self.capacity_markets.values() if
                        i.country == plant.location)
        except StopIteration:
            return None

    def get_bid_for_plant_and_tick(self, power_plant_name, tick) -> Optional[CapacityMarket]:
        try:
            return next(i for i in self.bids.values() if
                        i.tick == tick and i.plant == power_plant_name)
        except StopIteration:
            return None

    def get_accepted_CM_bids(self, tick):
        return [i for i in self.bids.values() if i.tick == tick and
                (i.status == globalNames.power_plant_dispatch_plan_status_partly_accepted
                 or i.status == globalNames.power_plant_dispatch_plan_status_accepted)]

    def create_or_update_power_plant_CapacityMarket_plan(self, plant: PowerPlant,
                                                         bidder: EnergyProducer,
                                                         market: Market,
                                                         long_term_contract: bool,
                                                         amount: float,
                                                         price: float,
                                                         time: int) -> Bid:
        bid = next((bid for bid in self.bids.values() if bid.plant == plant.name and \
                    bid.market == market.name and
                    bid.tick == time), None)
        if bid is None:
            # PowerPlantDispatchPlan not found, so create a new one
            bid = Bid(plant.name)

        bid.plant = plant.name
        bid.bidder = bidder.name
        bid.market = market.name
        bid.amount = amount
        bid.price = price
        bid.long_term_contract = long_term_contract
        bid.status = globalNames.power_plant_dispatch_plan_status_awaiting
        bid.accepted_amount = 0
        bid.tick = time
        self.bids[plant.name] = bid
        return bid

    def update_installed_pp_results(self, installed_pp_results):
        try:
            ids = []
            for index, result in installed_pp_results.iterrows():
                ids.append(result.identifier)
                installed_pp = next(i for i in self.power_plants.values() if i.id == result.identifier)
                installed_pp.add_values_from_df(result)  # here are the values added
            return ids
        except StopIteration:
            logging.warning('power plant technology not found' + str(result.identifier))
        return None

    def get_capacity_market_in_country(self, country, long_term):
        try:
            return next(i for i in self.capacity_markets.values() if i.country == country and i.long_term == long_term)
        except StopIteration:
            return None

    def get_spot_market_in_country(self, country):
        try:
            return next(i for i in self.electricity_spot_markets.values() if i.country == country)
        except StopIteration:
            return None

        # MarketClearingPoints

    def get_market_clearing_point_for_market_and_time(self, market: Market, time: int) -> Optional[MarketClearingPoint]:
        try:
            datetime_list = [i.name.split(" ", 1)[1] for i in self.market_clearing_points.values() if
                             i.market.name == market and i.tick == time]
            if datetime_list:
                first = next(
                    i for i in self.market_clearing_points.values() if i.market.name == market and i.tick == time
                    and i.name == 'MarketClearingPoint ' + min(datetime_list))
                last = next(
                    i for i in self.market_clearing_points.values() if i.market.name == market and i.tick == time
                    and i.name == 'MarketClearingPoint ' + max(datetime_list))
                return last
            else:
                return None
        except StopIteration:
            return None

    def get_market_clearing_point_price_for_market_and_time(self, market: Market, time: int) -> float:
        if time >= 0:
            mcp = self.get_market_clearing_point_for_market_and_time(market, time)
            if mcp is None:
                return None
            else:
                return mcp.price
        else:
            return None

    def get_cleared_volume_for_market_and_time(self, market: Market, time: int) -> float:
        if time >= 0:
            mcp = self.get_market_clearing_point_for_market_and_time(market, time)
            if mcp is None:
                return None
            else:
                return mcp.volume
        else:
            return None

    def create_or_update_market_clearing_point(self,
                                               market: Market,
                                               price: float,
                                               volume: float,
                                               time: int) -> MarketClearingPoint:
        mcp = next((mcp for mcp in self.market_clearing_points.values() if mcp.market == market and mcp.tick == time),
                   None)
        if mcp is None:
            # MarketClearingPoint not found, so create a new one
            name = 'MarketClearingPoint ' + str(datetime.now())
            mcp = MarketClearingPoint(name)

        mcp.market = market
        mcp.price = price
        mcp.tick = time
        mcp.volume = volume
        self.market_clearing_points[mcp.name] = mcp
        self.dbrw.stage_market_clearing_point(mcp)
        return mcp

        # Markets

    def get_electricity_spot_market_for_country(self, country: str) -> Optional[ElectricitySpotMarket]:
        try:
            return next(i for i in self.electricity_spot_markets.values() if
                        i.country == country)
        except StopIteration:
            return None

    def get_allowances_in_circulation(self, zone: Zone, time: int) -> int:
        return sum([i.banked_allowances[time] for i in self.power_plants.values()
                    if i.location.parameters['Country'] == zone.name])

    def get_co2_market_for_zone(self, zone: Zone) -> Optional[CO2Market]:
        try:
            return next(i for i in self.co2_markets.values()
                        if i.parameters['zone'] == zone.name)
        except StopIteration:
            return None

    def get_co2_market_for_plant(self, power_plant: PowerPlant) -> Optional[CO2Market]:
        return self.get_co2_market_for_zone(self.zones[power_plant.location.parameters['Country']])

    def get_market_stability_reserve_for_market(self, market: Market) -> Optional[MarketStabilityReserve]:
        try:
            return next(i for i in self.market_stability_reserves.values()
                        if i.zone.name == market.parameters['zone'])
        except StopIteration:
            return None

        # Extra functions for strategic reserve

    def calculateCapacityOfPowerPlantsInMarket(self, market):
        if market == 'DutchCapacityMarket':
            temp_location = 'NL'
        elif market == 'GermanCapacityMarket':
            temp_location = 'DE'
        else:
            temp_location = 'None'
        return sum([i.capacity for i in self.power_plants.values() if i.location == temp_location])

    def get_descending_sorted_power_plant_dispatch_plans_by_SRmarket(self, market: Market, time: int) -> \
            List[PowerPlantDispatchPlan]:
        return sorted([i for i in self.bids.values()
                       if i.market == market.name and i.tick == time], key=lambda i: i.price, reverse=True)

    def get_descending_bids_and_first_in_SR(self, market: Market, time: int, order_status) -> \
            List[PowerPlantDispatchPlan]:
        sortedbids_by_price = sorted([i for i in self.bids.values()
                                      if i.market == market.name and i.tick == time], key=lambda i: i.price,
                                     reverse=True)

        return sorted(sortedbids_by_price,
                      key=lambda item: order_status[self.power_plants[item.plant].status]
                      if self.power_plants[item.plant].status in order_status else 10, reverse=False)

    def get_accepted_SR_bids(self):
        return [i for i in self.bids.values() if
                i.status == globalNames.power_plant_status_strategic_reserve]

    def create_or_update_StrategicReserveOperator(self, name: str,
                                                  zone: str,
                                                  volumeSR: float,
                                                  list_of_plants: list,
                                                  forward_years: int
                                                  ) -> StrategicReserveOperator:
        SRO = next((SRO for SRO in self.sr_operator.values() if SRO.name == name), None)
        if SRO is None:
            name = ("SRO_" + zone)
            SRO = StrategicReserveOperator(name)
        SRO.reserveVolume = volumeSR
        SRO.list_of_plants_inSR_in_current_year = list_of_plants
        self.sr_operator[SRO.name] = SRO
        self.dbrw.stage_sr_operator_results(SRO, self.current_tick + forward_years)
        return SRO

    def update_StrategicReserveOperator(self, SRO) -> StrategicReserveOperator:
        self.dbrw.stage_sr_operator_cash(SRO)
        self.dbrw.stage_sr_operator_revenues_results(SRO, self.current_tick)

    def update_power_plant_status_ger_first_year(self, power_plant):
        power_plant.status = globalNames.power_plant_status_strategic_reserve
        self.dbrw.stage_power_plant_status(power_plant)
        self.dbrw.stage_years_in_SR(power_plant.name, 1)

    def increase_year_in_sr(self, power_plant):
        power_plant.years_in_SR += 1
        self.dbrw.stage_years_in_SR(power_plant.name, power_plant.years_in_SR)

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return str(vars(self))

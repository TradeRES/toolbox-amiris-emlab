"""
This is the Python class responsible for all reads and writes of the SpineDB.
This is a separate file so that all import definitions are centralized.
Ingrid Sanchez 18-2-2022 modified
Jim Hommes - 25-3-2021
"""
import logging
from spinedb_api import Map, DatabaseMapping, export_object_parameter_values
from twine.repository import Repository
import math
from domain.CapacitySubscriptionConsumer import CapacitySubscriptionConsumer
from domain.financialReports import FinancialPowerPlantReport
from domain.investments import CandidatesNPV, InvestmentDecisions, InstalledCapacity, InstalledFuturePowerPlants
from domain.load_shifter_with_cap_demand import LoadShifterwCap
from domain.weatherYears import WeatherYears
from modules.profits import Profits
from domain.newTechnology import NewTechnology
from domain.targetinvestor import TargetInvestor
from util.repository import *
from util.spinedb import SpineDB
from domain.powerplant import Decommissioned
from domain.hydrogen_demand import HydrogenDemand


class SpineDBReaderWriter:
    """
    The class that handles all writing and reading to the SpineDB.
    """

    def __init__(self, open_db, *db_urls: str):
        self.db_urls = db_urls
        self.db = SpineDB(db_urls[0])  # the first url is always emlab
        self.powerplant_installed_classname = 'PowerPlantsInstalled'
        self.load_shedders_classname = 'LoadShedders'
        self.consumer_classname = "CapacitySubscriptionConsumer"
        self.technologies_classname = 'Technologies'
        self.powerplantprofits_classname = 'Profits'
        self.candidate_powerplant_installed_classname = 'CandidatePowerPlants'
        self.powerplant_dispatch_plan_classname = 'PowerPlantDispatchPlans'
        self.bids_classname = 'Bids'
        self.market_clearing_point_object_classname = 'MarketClearingPoints'
        self.financial_reports_object_classname = 'FinancialReports'
        self.loans_object_classname = 'Loans'
        self.downpayments_object_classname = "Downpayments"
        self.candidate_plants_NPV_classname = "CandidatePlantsNPV"
        self.investment_decisions_classname = "InvestmentDecisions"
        self.sro_classname = 'StrategicReserveOperators'
        self.sro_results_classname = 'StrategicReserveResults'
        self.fuel_classname = "node"
        self.configuration_object_classname = "Configuration"
        self.capacity_market_classname = "CapacityMarkets"
        self.cone_classname = "Cone"
        self.energyProducer_classname = "EnergyProducers"
        self.Conventionals_classname = "Conventionals"
        self.VariableRenewable_classname = "Renewables"
        self.Storages_classname = "Storages"
        self.total_capacity_classname = "InstalledDispatchableCapacity"
        self.installed_future_power_plants_classname = "InstalledFuturePowerPlants"
        self.amirisdb = None

        if open_db == "Amiris":
            self.amirisdb = SpineDB(db_urls[1])

    def read_db_and_create_repository(self, module) -> Repository:
        """
        This function add all info from EMLAB DB to REPOSITORY
        """
        logging.info('SpineDBRW: Start Read Repository')
        reps = Repository()
        reps.runningModule = module
        reps.dbrw = self
        self.stage_init_alternative("0")

        for row in self.db.query_object_parameter_values_by_object_class('Configuration'):
            if row['parameter_name'] == 'SimulationTick':
                reps.current_tick = int(row['parameter_value'])
            elif row['parameter_name'] == 'Start Year':
                reps.start_simulation_year = int(row['parameter_value'])
            elif row['parameter_name'] == 'End Year':
                reps.end_simulation_year = int(row['parameter_value'])
                reps.simulation_length = reps.end_simulation_year - reps.start_simulation_year
            elif row['parameter_name'] == 'Look Ahead':
                reps.lookAhead = int(row['parameter_value'])
            elif row['parameter_name'] == 'pastTimeHorizon':
                reps.pastTimeHorizon = int(row['parameter_value'])
            elif row['parameter_name'] == 'CurrentYear':
                reps.current_year = int(row['parameter_value'])
            elif row['parameter_name'] == 'InvestmentIteration':
                reps.investmentIteration = int(row['parameter_value'])
            elif row[
                'parameter_name'] == 'Country':  # changed from node(emlab) to country because in traderes Node is used for fuels
                reps.country = str(row['parameter_value'])
                if reps.country == "NL":
                    reps.avoid_alternative = "DE"
                else:
                    reps.avoid_alternative = "NL"
                reps.agent = "Producer" + reps.country

            elif row['parameter_name'] in ['start_tick_fuel_trends', 'start_year_fuel_trends']:
                reps.start_tick_fuel_trends = int(row['parameter_value'])
            elif row['parameter_name'] == 'start_dismantling_tick':
                reps.start_dismantling_tick = int(row['parameter_value'])
            elif row['parameter_name'] == 'maximum_investment_capacity_per_year':
                reps.maximum_investment_capacity_per_year = int(row['parameter_value'])
            elif row['parameter_name'] == 'typeofProfitforPastHorizon':
                reps.typeofProfitforPastHorizon = str(row['parameter_value'])
            elif row['parameter_name'] == 'max_permit_build_time':
                reps.max_permit_build_time = int(row['parameter_value'])
            elif row['parameter_name'] == 'fix_fuel_prices_to_year':
                reps.fix_fuel_prices_to_year = bool(row['parameter_value'])
            elif row['parameter_name'] == 'fix_price_year':
                reps.fix_price_year = int(row['parameter_value'])
            elif row['parameter_name'] == 'yearly_CO2_prices':
                reps.yearly_CO2_prices = bool(row['parameter_value'])
            elif row['parameter_name'] == 'realistic_candidate_capacities_tobe_installed':
                reps.realistic_candidate_capacities_tobe_installed = bool(row['parameter_value'])
            elif row['parameter_name'] == 'realistic_candidate_capacities_for_future':
                reps.realistic_candidate_capacities_for_future = bool(row['parameter_value'])
            elif row['parameter_name'] == 'dummy_capacity_to_be_installed':
                reps.dummy_capacity_to_be_installed = int(row['parameter_value'])
            elif row['parameter_name'] == 'dummy_capacity_to_test':
                reps.dummy_capacity_to_test = int(row['parameter_value'])
            elif row['parameter_name'] == 'npv_with_annuity':
                reps.npv_with_annuity = bool(row['parameter_value'])
            elif row['parameter_name'] == 'targetinvestment_per_year':
                reps.targetinvestment_per_year = bool(row['parameter_value'])
            elif row['parameter_name'] == 'install_missing_capacity_as_one_pp':
                reps.install_missing_capacity_as_one_pp = bool(row['parameter_value'])
            elif row['parameter_name'] == 'fix_profiles_to_representative_year':
                reps.fix_profiles_to_representative_year = bool(row['parameter_value'])
            elif row['parameter_name'] == 'fix_demand_to_representative_year':
                reps.fix_demand_to_representative_year = bool(row['parameter_value'])
            elif row['parameter_name'] == 'increase_demand':
                reps.increase_demand = bool(row['parameter_value'])
            elif row['parameter_name'] == 'Representative year':
                reps.representative_year = int(row['parameter_value'])
            elif row['parameter_name'] == 'Power plants year':
                reps.Power_plants_from_year = int(row['parameter_value'])
            elif row['parameter_name'] == 'install_at_look_ahead_year':
                reps.install_at_look_ahead_year = bool(row['parameter_value'])
            elif row['parameter_name'] == 'target_investments_done':
                reps.target_investments_done = bool(row['parameter_value'])
            elif row['parameter_name'] == 'investment_initialization_years':
                reps.investment_initialization_years = int(row['parameter_value'])
            elif row['parameter_name'] == 'decommission_from_input':
                reps.decommission_from_input = bool(row['parameter_value'])
            elif row['parameter_name'] == 'initialization_investment':
                reps.initialization_investment = bool(row['parameter_value'])
            elif row['parameter_name'] == 'iteration':
                reps.iteration_weather = str(row['parameter_value'])
            elif row['parameter_name'] == 'available_years_data':
                reps.available_years_data = bool(row['parameter_value'])
            elif row['parameter_name'] == 'load_shifter':
                reps.load_shifter = str(row['parameter_value'])
            elif row['parameter_name'] == 'minimal_last_years_IRR':
                reps.minimal_last_years_IRR = row['parameter_value']
            elif row['parameter_name'] == 'last_years_IRR_or_NPV':
                reps.last_years_IRR_or_NPV = int(row['parameter_value'])
            elif row['parameter_name'] == 'minimal_last_years_NPV':
                reps.minimal_last_years_NPV = row['parameter_value']
            elif row['parameter_name'] == 'last_investable_technology':
                reps.last_investable_technology = row['parameter_value']
            elif row['parameter_name'] == 'groups power plants per installed year':
                reps.groups_plants_per_installed_year = bool(row['parameter_value'])
            elif row['parameter_name'] == 'scenarioWeatheryearsExcel':
                reps.scenarioWeatheryearsExcel = str(row['parameter_value'])
            elif row['parameter_name'] == 'capacity_remuneration_mechanism':
                reps.capacity_remuneration_mechanism = (row['parameter_value'])
            elif row['parameter_name'] == 'maximum_installed_share_initialization':
                reps.maximum_installed_share_initialization = float(row['parameter_value'])
            elif row['parameter_name'] == 'round_for_capacity_market_y_1':
                reps.round_for_capacity_market_y_1 = bool(row['parameter_value'])
            elif row['parameter_name'] == 'change_IRR':
                reps.change_IRR= bool(row['parameter_value'])
            elif row['parameter_name'] == 'reliability_option_SP':
                reps.reliability_option_strike_price = row['parameter_value']
            elif row['parameter_name'] == 'dynamic_derating_factor':
                reps.dynamic_derating_factor = bool(row['parameter_value'])


        # these are the years that need to be added to the power plants on the first simulation tick
        reps.add_initial_age_years = reps.start_simulation_year - reps.Power_plants_from_year

        print("-----------------------------------------------------------" + str(reps.current_tick))
        reps.dictionaryFuelNames = {i['parameter_name']: i['parameter_value'] for i
                                    in
                                    self.db.query_object_parameter_values_by_object_class_and_object_name("Dictionary",
                                                                                                          "AmirisFuelName")}
        reps.dictionaryTechSet = {i['parameter_name']: i['parameter_value'] for i
                                  in self.db.query_object_parameter_values_by_object_class_and_object_name("Dictionary",
                                                                                                           "AmirisSet")}
        reps.dictionaryFuelNumbers = {i['parameter_name']: i[('parameter_value')] for i
                                      in self.db.query_object_parameter_values_by_object_class_and_object_name(
                "Dictionary", "FuelNumber")}
        reps.dictionaryTechNumbers = {i['parameter_name']: i[('parameter_value')] for i
                                      in self.db.query_object_parameter_values_by_object_class_and_object_name(
                "Dictionary", "TechNumber")}
        parameter_priorities = {i['parameter_name']: i['parameter_value'] for i
                                in
                                self.db.query_object_parameter_values_by_object_class_and_object_name("Configuration",
                                                                                                      "priority")}
        db_data = self.db.export_data()
        sorted_parameter_names = sorted(db_data['object_parameters'],
                                        key=lambda item: parameter_priorities[item[0]]
                                        if item[0] in parameter_priorities.keys() else 0, reverse=True)
        object_parameter_values = db_data['object_parameter_values']

        # trying to read DB faster
        # db_map = DatabaseMapping(self.db_urls[0])
        # object_parameter_values = export_object_parameter_values(db_map)

        for (object_class_name, parameter_name, _, _, _) in sorted_parameter_names:
            for (_, object_name, _) in [i for i in db_data['objects'] if i[0] == object_class_name]:
                try:
                    db_line = next(i for i in object_parameter_values
                                   if i[0] == object_class_name and i[1] == object_name and i[2] == parameter_name
                                   and i[4] != reps.avoid_alternative)
                    add_parameter_value_to_repository_based_on_object_class_name(reps, db_line)
                except StopIteration:
                    # logging.warning
                    logging.warning('No value found for class: ' + object_class_name +
                                    ', object: ' + object_name +
                                    ', parameter: ' + parameter_name)

        # the results of AMIRIS dispatch are extracted from the amiris DB
        if self.amirisdb is not None:
            db_amirisdata = self.amirisdb.export_data()
            add_parameter_value_to_repository_based_on_object_class_name_amiris(self, reps, db_amirisdata)
        return reps

    """
    Markets
    """

    def stage_init_bids_structure(self):
        self.stage_object_class(self.bids_classname)
        self.stage_object_parameters(self.bids_classname,
                                     ['plant', 'market', 'price', 'amount', 'bidder', 'accepted_amount',
                                      'status', "tick"])

    def stage_init_market_clearing_point_structure(self):
        self.stage_object_class(self.market_clearing_point_object_classname)
        self.stage_object_parameters(self.market_clearing_point_object_classname, ['Market', 'Price', 'Volume', 'Tick'])

    def stage_market_clearing_point(self, mcp: MarketClearingPoint):
        object_name = mcp.name
        self.stage_object_class(self.market_clearing_point_object_classname)
        self.stage_object_parameters(self.market_clearing_point_object_classname, ['Market', 'Price', 'Volume', 'Tick'])
        self.stage_object(self.market_clearing_point_object_classname, object_name)
        self.stage_object_parameter_values(self.market_clearing_point_object_classname, object_name,
                                           [('Market', mcp.market.name),
                                            ('Price', mcp.price),
                                            ('Tick', mcp.tick),
                                            ('Volume', mcp.volume)], "0")

    def stage_plants_in_CM(self, plantsinCM, tick):
        self.stage_object_class('plantsinCM')
        self.stage_object_parameter('plantsinCM', 'plantsinCM')
        self.stage_object('plantsinCM', str(tick))
        self.stage_object_parameter_values('plantsinCM', str(tick),
                                           [('plantsinCM', plantsinCM)], "0")


    def stage_derating_factor_yearly(self, derating_factors, tick):
        self.stage_object_class("Technologies")
        self.stage_object_parameter('Technologies', "deratingFactor_yearly")
        for tech, derating_factor  in derating_factors.items():
            if derating_factor > 0:
                derating_factor =  round(derating_factor, 3)
            self.stage_object('Technologies', tech)
            self.stage_object_parameter_values('Technologies', tech,
                                               [("deratingFactor_yearly", Map([str(tick)], [derating_factor]))], "0")


    def stage_payment_co2_allowances(self, power_plant, cash, allowances, time):
        self.stage_co2_allowances(power_plant, allowances, time)
        self.stage_object_parameter_values('EnergyProducers', power_plant.owner.name, [('cash', cash)], time)

    def stage_co2_allowances(self, power_plant, allowances, time):
        param_name = 'Allowances'
        self.stage_object_parameter('PowerPlants', param_name)
        self.stage_object_parameter_values('PowerPlants', power_plant.name, [(param_name, allowances)], time)

    def stage_market_stability_reserve(self, msr: MarketStabilityReserve, reserve, time):
        param_name = 'Reserve'
        self.stage_object_parameter('MarketStabilityReserve', param_name)
        self.stage_object_parameter_values('MarketStabilityReserve', msr.name, [(param_name, reserve)], time)


    def stage_power_plant_status(self, power_plant):
        self.stage_object(self.powerplant_installed_classname, power_plant.name)
        self.stage_object_parameter_values(self.powerplant_installed_classname, power_plant.name,
                                           [
                                               ('Status', power_plant.status)], '0')

    """
    Power plants
    """

    # def stage_start_target_capacities(self, targets):
    #     for target in targets:
    #         classname = "Targets"
    #         object_name = target.name
    #         self.stage_object(classname, object_name)
    #         self.stage_object_parameter_values(classname, object_name,
    #                                            [('start_capacity', target.start_capacity)], "0")

    def stage_power_plant_id_and_loans(self, reps, power_plants):
        print("staging id and loans")
        self.stage_object_class(self.powerplant_installed_classname)
        self.stage_object_parameters(self.powerplant_installed_classname, ["Id"])
        self.stage_object_class(self.loans_object_classname)
        self.stage_object_parameters(self.loans_object_classname,
                                     ['amountPerPayment', 'numberOfPaymentsDone', 'loanStartTick',
                                      'totalNumberOfPayments'])

        for power_plant_name, pp in power_plants.items():
            self.stage_object(self.powerplant_installed_classname, power_plant_name)
            self.stage_object(self.loans_object_classname, str(power_plant_name))
            self.stage_object_parameter_values(self.powerplant_installed_classname, str(power_plant_name),
                                               [('Id', pp.id)], '0')

            self.stage_object_parameter_values(self.loans_object_classname, str(power_plant_name),
                                               [('amountPerPayment', pp.loan.amountPerPayment),
                                                ('numberOfPaymentsDone', pp.loan.numberOfPaymentsDone),
                                                ('loanStartTick', pp.loan.loanStartTick),
                                                ('totalNumberOfPayments', pp.loan.totalNumberOfPayments)
                                                ],
                                               '0')

    def stage_candidate_power_plant_id(self, candidate_power_plants):
        self.stage_object_class(self.candidate_powerplant_installed_classname)
        self.stage_object_parameters(self.candidate_powerplant_installed_classname, ["Id"])
        for power_plant_name, values in candidate_power_plants.items():
            self.stage_object(self.candidate_powerplant_installed_classname, power_plant_name)
            self.db.import_object_parameter_values(
                [(self.candidate_powerplant_installed_classname, power_plant_name, 'Id', values.id, '0')])

    def stage_init_power_plant_structure(self):
        self.stage_object_class(self.powerplant_installed_classname)
        self.stage_object_parameters(self.powerplant_installed_classname,
                                     ["Id", "Age", "actualEfficiency", "DischargingEfficiency", "Capacity", "Location",
                                      "Owner", "Status", #"Cash",
                                                         "Technology"])

    def stage_new_power_plant(self, powerplant):
        object_name = str(powerplant.name)
        self.stage_object(self.powerplant_installed_classname, object_name)
        self.stage_object_parameter_values(self.powerplant_installed_classname, object_name,
                                           [("Id", object_name),
                                            ('Age', powerplant.age),
                                            ('actualEfficiency', powerplant.actualEfficiency),
                                            ('Capacity', powerplant.capacity),
                                            ('Location', powerplant.location),
                                            ('Owner', powerplant.owner.name),
                                            ('Status', powerplant.status),
                                           # ('Cash', powerplant.cash),
                                            ('Technology', powerplant.technology.name)], "0")

    def stage_new_irr(self, technology):
        object_name = str(technology.name)
        self.stage_object(self.technologies_classname, object_name)
        self.stage_object_parameter_values(self.technologies_classname, object_name,
                                           [("interest_rate", technology.interestRate)], "0")
    def stage_id_plant_to_delete(self, powerplant):
        object_name = str(powerplant.name)
        self.stage_object_parameter_values(self.powerplant_installed_classname, object_name,
                                           [("Id", "delete")], "0")


    def stage_peak_dispatchable_capacity(self, peak_dispatchable_capacity, year):
        object_name = "All"
        self.stage_object_class(self.total_capacity_classname)
        self.stage_object(self.total_capacity_classname, object_name)
        self.stage_object_parameter(self.total_capacity_classname, str(year))
        self.stage_object_parameter_values(self.total_capacity_classname, object_name,
                                           [(str(year), peak_dispatchable_capacity)], '0')

    def stage_total_demand(self,market , total_demand, year , total_demand_name):
        self.stage_object_class("ElectricitySpotMarkets")
        self.stage_object("ElectricitySpotMarkets", market)
        self.stage_object_parameter("ElectricitySpotMarkets", total_demand_name)
        self.stage_object_parameter_values("ElectricitySpotMarkets", market,
                                           [(total_demand_name, Map([str(year)], [total_demand]))], "0")


    def stage_installed_pp_names(self, list_installed_pp, simulation_tick):
        object_name = "All"
        self.stage_object_class(self.installed_future_power_plants_classname)
        self.stage_object(self.installed_future_power_plants_classname, object_name)
        self.stage_object_parameter(self.installed_future_power_plants_classname, str(simulation_tick))
        self.stage_object_parameter_values(self.installed_future_power_plants_classname, object_name,
                                           [(str(simulation_tick), list_installed_pp)], '0')

    def stage_candidate_pp_investment_status_structure(self):
        self.stage_object_class(self.candidate_powerplant_installed_classname)
        self.stage_object_parameter(self.candidate_powerplant_installed_classname, 'ViableInvestment')

    def stage_candidate_pp_investment_status(self, candidatepowerplant):
        object_name = candidatepowerplant.name
        self.stage_object(self.candidate_powerplant_installed_classname, object_name)
        self.stage_object_parameter_values(self.candidate_powerplant_installed_classname, object_name,
                                           [('ViableInvestment', candidatepowerplant.viableInvestment)], '0')

    def stage_candidate_status_to_investable(self, all_candidates_names):
        for candidate in all_candidates_names:
            self.stage_object(self.candidate_powerplant_installed_classname, candidate)
            self.stage_object_parameter_values(self.candidate_powerplant_installed_classname, candidate,
                                               [('ViableInvestment', True)], '0')

    def stage_last_testing_technology(self, last_investable_technology ):
        # when testing last technolgy, candidate to be installed is tested with real capacity
        self.stage_object_class(self.configuration_object_classname)
        self.stage_object_parameter(self.configuration_object_classname, "last_investable_technology")
        self.stage_object(self.configuration_object_classname, "SimulationYears")
        self.stage_object_parameter_values(self.configuration_object_classname, "SimulationYears",
                                           [('last_investable_technology', last_investable_technology)], "0")
    def stage_price_cap(self, capacity_market_name, price_cap):
        self.stage_object_class(self.capacity_market_classname)
        self.stage_object_parameter(self.capacity_market_classname, "PriceCap")
        self.stage_object(self.capacity_market_classname, capacity_market_name)
        self.stage_object_parameter_values(self.capacity_market_classname, capacity_market_name,
                                           [('PriceCap', price_cap)], "0")


    def stage_net_cone(self, capacity_market_name, net_cone):
        self.stage_object_class(self.capacity_market_classname)
        self.stage_object_parameter(self.capacity_market_classname, "net_cone")
        self.stage_object(self.capacity_market_classname, capacity_market_name)
        self.stage_object_parameter_values(self.capacity_market_classname, capacity_market_name,
                                           [('net_cone', net_cone)], "0")


    def stage_yearly_CONE(self, netcones, cones, current_tick):
        self.stage_object_class(self.cone_classname)
        for technology_name, cone in cones.items():
            self.stage_object_parameter(self.cone_classname, "cone" )
            self.stage_object(self.cone_classname,technology_name)
            self.stage_object_parameter_values(self.cone_classname, technology_name,
            [("cone", Map([str(current_tick)], [float(cone)]))], "0")

        for technology_name, netcone in netcones.items():
            self.stage_object_parameter(self.cone_classname, "netcone" )
            self.stage_object(self.cone_classname,technology_name  )
            self.stage_object_parameter_values(self.cone_classname, technology_name ,
                                               [("netcone" , Map([str(current_tick)], [float(netcone)]))], "0")

    def stage_iteration_for_CM(self, status):
        self.stage_object_class(self.configuration_object_classname)
        self.stage_object_parameter(self.configuration_object_classname, "round_for_capacity_market_y_1")
        self.stage_object(self.configuration_object_classname, "SimulationYears")
        self.stage_object_parameter_values(self.configuration_object_classname, "SimulationYears",
                                           [('round_for_capacity_market_y_1', status)], "0")

    def stage_init_power_plants_status(self):
        self.stage_object_parameters(self.powerplant_installed_classname, ['Status'])

    def stage_power_plant_status_and_age(self, power_plants):
        self.stage_object(self.powerplant_installed_classname, "Status")
        for power_plant_name, values in power_plants.items():
            self.db.import_object_parameter_values(
                [(self.powerplant_installed_classname, power_plant_name, "Status", values.status, '0'),
                 (self.powerplant_installed_classname, power_plant_name, "Age", values.age, '0')])

    def stage_init_years_in_long_term_capacity_market(self):
        self.stage_object_parameter(self.powerplant_installed_classname, 'years_left_in_LCM')
        self.stage_object_parameter(self.powerplant_installed_classname, "last_year_in_capacity_market")
    def stage_power_plant_years_in_long_term_capacity_market(self, power_plant, last_year_in_capacity_market):
        self.db.import_object_parameter_values(
            [(self.powerplant_installed_classname, power_plant, "last_year_in_capacity_market", last_year_in_capacity_market, '0'),
             ])

    def stage_init_power_plants_fixed_costs(self):
        self.stage_object_parameters(self.powerplant_installed_classname, ['actualFixedOperatingCost'])

    def stage_fixed_operating_costs(self, pp):
        self.stage_object_parameter(self.powerplant_installed_classname, 'actualFixedOperatingCost')
        self.stage_object(self.powerplant_installed_classname, pp.name)
        self.stage_object_parameter_values(self.powerplant_installed_classname, pp.name,
                                           [('actualFixedOperatingCost', pp.actualFixedOperatingCost)],
                                           "0")
    def stage_variable_costs_and_efficiency(self, power_plants):
        self.stage_object_parameters(self.powerplant_installed_classname, ['actualVariableCost', 'actualEfficiency'])
        for power_plant_name, pp in power_plants.items():
            self.stage_object(self.powerplant_installed_classname, pp.name)
            self.stage_object_parameter_values(self.powerplant_installed_classname, pp.name,
                                               [('actualVariableCost', pp.actualVariableCost),
                                                ('actualEfficiency', pp.actualEfficiency)],
                                               "0")

    def stage_list_decommissioned_plants(self, decommissioned_list):
        self.stage_object_parameters("Decommissioned", ['Done'])
        self.db.import_object_parameter_values(
            [("Decommissioned",  "Decommissioned", "Done", decommissioned_list, '0')])
        
    def stage_list_decommissioned_expected_plants(self, decommissioned_list, future_year):
        self.stage_object("Decommissioned", "Expectation")
        self.stage_object_parameters("Decommissioned", [str(future_year)])
        self.db.import_object_parameter_values(
            [("Decommissioned", "Expectation" ,  str(future_year), decommissioned_list, "0" )])

    def stage_decommission_year(self, powerplant_name, tick):
        self.stage_object_parameters(self.powerplant_installed_classname, ['DecommissionInYear'])
        self.db.import_object_parameter_values(
            [(self.powerplant_installed_classname, powerplant_name, "DecommissionInYear", tick, '0')])

    def stage_bids(self, bid: Bid):
        self.stage_object(self.bids_classname, bid.name)
        self.stage_object_parameter_values(self.bids_classname, bid.name,
                                           [('plant', bid.plant),
                                            ('market', bid.market),
                                            ('price', bid.price),
                                            ('amount', bid.amount),
                                            ('tick', bid.tick),
                                            ('bidder', bid.bidder),
                                            ('accepted_amount', bid.accepted_amount),
                                            ('status', bid.status)], "0")

    def stage_sr_operator_cash(self, SRO: StrategicReserveOperator):
        self.stage_object(self.sro_classname, SRO.name)
        self.stage_object_parameter_values(self.sro_classname, SRO.name,
                                           [
                                               ('cash', SRO.cash)], "0")

    def stage_init_sr_results_structure(self):
        self.stage_object_class(self.sro_results_classname)
        self.stage_object_parameters(self.sro_results_classname,
                                     ['reserveVolume', 'list_of_plants','revenues_per_year'])

    def stage_sr_operator_results(self, SRO: StrategicReserveOperator, tick):
        self.stage_object(self.sro_results_classname, str(tick))
        self.stage_object_parameter_values(self.sro_results_classname, str(tick),
                                           [('reserveVolume', SRO.reserveVolume),
                                            ('list_of_plants', SRO.list_of_plants_inSR_in_current_year)], "0")

    def stage_sr_operator_revenues_results(self, SRO: StrategicReserveOperator, last_tick):
        self.stage_object(self.sro_results_classname, str(last_tick))
        self.stage_object_parameter_values(self.sro_results_classname, str(last_tick),
                                           [('revenues_per_year', SRO.revenues_per_year)
                                            ], "0")


    def stage_years_in_SR(self, pp_name, years_in_SR):
        self.stage_object(self.powerplant_installed_classname, pp_name)
        self.stage_object_class(self.powerplant_installed_classname)
        self.stage_object_parameter(self.powerplant_installed_classname, "years_in_SR")
        self.stage_object_parameter_values(self.powerplant_installed_classname, pp_name,
                                           [('years_in_SR', years_in_SR)], "0")


    def stage_init_candidate_plants_value(self, iteration, futureYear):
        year_iteration = str(futureYear) + "-" + str(iteration)
        self.stage_object_class(self.candidate_plants_NPV_classname)
        self.stage_object_parameters(self.candidate_plants_NPV_classname,
                                     [year_iteration])
        # ------------------------------------------------ this is only to debug
        # self.stage_init_alternative("costs")
        # self.stage_init_alternative("revenues")

    def stage_candidate_power_plants_value(self, powerplant, powerPlantvalue, iteration, futureYear):
        year_iteration = str(futureYear) + "-" + str(iteration)
        self.stage_object(self.candidate_plants_NPV_classname, powerplant)
        self.stage_object_parameter_values(self.candidate_plants_NPV_classname, powerplant,
                                           [(year_iteration, powerPlantvalue)], "0")
        # ------------------------------------------------ this is only to debug
        # self.stage_object_parameter_values(self.candidate_plants_NPV_classname, powerplant,
        #                                    [(year_iteration, costs)], "costs")
        # self.stage_object_parameter_values(self.candidate_plants_NPV_classname, powerplant,
        #                                    [(year_iteration, revenues)], "revenues")

    # def stage_init_investment_decisions(self, iteration, tick):
    #     self.stage_object_class(self.investment_decisions_classname)
    #     self.stage_object_parameters(self.investment_decisions_classname, [str(iteration)])
    #
    # def stage_investment_decisions(self, power_plant_id, iteration, tick):
    #     self.stage_object(self.investment_decisions_classname, str(tick))
    #     self.stage_object_parameter_values(self.investment_decisions_classname, str(tick),
    #                                        [(str(iteration), power_plant_id)], "0" )

    def stage_init_future_operational_profits(self):
        self.stage_object_class(self.powerplantprofits_classname)
        self.stage_object_parameters(self.powerplantprofits_classname,
                                     ["Profits", "PowerPlants", "ProfitsC", "PowerPlantsC"])

    def stage_future_operational_profits_installed_plants(self, reps, pp_names, pp_profits):
        # object name =  simulation tick  - iteration
        objectname = str(reps.current_tick) + "-" + str(reps.investmentIteration)
        self.stage_object(self.powerplantprofits_classname, objectname)
        self.stage_object_parameter_values(self.powerplantprofits_classname, objectname,
                                           [("Profits", pp_profits)], "0")
        self.stage_object_parameter_values(self.powerplantprofits_classname, objectname,
                                           [("PowerPlants", pp_names)], "0")

    def stage_candidate_plant_results(self, reps, pp_numbers, pp_profits):
        objectname = str(reps.current_tick) + "-" + str(reps.investmentIteration)
        self.stage_object(self.powerplantprofits_classname, objectname)
        self.stage_object_parameter_values(self.powerplantprofits_classname, objectname,
                                           [("ProfitsC", pp_profits)], "0")
        self.stage_object_parameter_values(self.powerplantprofits_classname, objectname,
                                           [("PowerPlantsC", pp_numbers)], "0")

    def stage_future_total_profits_installed_plants(self, reps,  pp_dispatched_names,pp_total_profits, available_plants_ids, tick):
        """
        there are calculdated for capacity markets
        """
        parametername =  "expectedTotalProfits"
        self.stage_object_class(self.powerplant_installed_classname)
        self.stage_object_parameter(self.powerplant_installed_classname, parametername)
        for i, pp_name in enumerate(pp_dispatched_names):
            pp = reps.power_plants[pp_name]
            pp_profit = pp_total_profits.loc[0,pp.id]
            self.stage_object(self.powerplant_installed_classname, str(pp_name))
            self.stage_object_parameter_values(self.powerplant_installed_classname, str(pp_name),
                                               [(parametername, Map([str(tick)], [float(pp_profit)]))], "0")

        if len(available_plants_ids) > len(pp_dispatched_names):
            # if there are less dispatched plants then assign their revenues as 0
            for pp_id in available_plants_ids:
                if pp_id not in pp_total_profits.columns.tolist():
                    pp = reps.get_power_plant_by_id(pp_id)
                    print(pp.name + "was tested but not used - > no operational profits")
                    pp_profit = 0
                    self.stage_object(self.powerplant_installed_classname, str(pp.name))
                    self.stage_object_parameter_values(self.powerplant_installed_classname, str(pp.name),
                                                       [(parametername, Map([str(tick)], [float(pp_profit)]))], "0")

    def stage_future_profits_withloans_installed_plants(self, reps, pp_dispatched_names, pp_total_profits, available_plants_ids, tick, look_ahead_ticks):
        """
        there are calculdated to estimate if power plants will be decommissioned for future market
        """
        parametername = "expectedTotalProfitswFixedCosts"
        self.stage_object_class(self.powerplant_installed_classname)
        self.stage_object_parameter(self.powerplant_installed_classname, parametername)
        for i, pp_name in enumerate(pp_dispatched_names):
            pp = reps.power_plants[pp_name]
            self.update_fixed_costs(pp, look_ahead_ticks)
            pp_profit = pp_total_profits.loc[0,pp.id] - pp.actualFixedOperatingCost
            self.stage_object(self.powerplant_installed_classname, str(pp_name))
            self.stage_object_parameter_values(self.powerplant_installed_classname, str(pp_name),
                                               [(parametername, Map([str(tick)], [float(pp_profit)]))], "0")

        if len(available_plants_ids) > len(pp_dispatched_names):
            # if there are less dispatched plants then assign their revenues as 0
            for pp_id in available_plants_ids:
                if pp_id not in pp_total_profits.columns.tolist():
                    pp = reps.get_power_plant_by_id(pp_id)
                    self.update_fixed_costs(pp , look_ahead_ticks)
                    print(pp.name + "was tested but not used - > no operational profits")
                    pp_profit = - pp.actualFixedOperatingCost
                    self.stage_object(self.powerplant_installed_classname, str(pp.name))
                    self.stage_object_parameter_values(self.powerplant_installed_classname, str(pp.name),
                                                       [(parametername, Map([str(tick)], [float(pp_profit)]))], "0")

    def update_fixed_costs(self, power_plant, lookAhead):
        if power_plant.age >= power_plant.technology.expected_lifetime:
            ModifiedOM = power_plant.getTechnology().get_fixed_operating_by_time_series((power_plant.age + lookAhead) ,
                                                                                        power_plant.commissionedYear) * power_plant.get_actual_nominal_capacity()
            power_plant.setActualFixedOperatingCost(ModifiedOM)
    def stage_testing_future_year(self, reps):
        self.stage_object_class(self.configuration_object_classname)
        self.stage_object_parameter(self.configuration_object_classname, "investment_initialization_years")
        self.stage_object(self.configuration_object_classname, "SimulationYears")
        self.stage_object_parameter_values(self.configuration_object_classname, "SimulationYears",
                                           [("investment_initialization_years", reps.investment_initialization_years)],
                                           "0")

    def stage_initialization_investment(self, initialization_investment):
        self.stage_object_class(self.configuration_object_classname)
        self.stage_object_parameter(self.configuration_object_classname, "initialization_investment")
        self.stage_object(self.configuration_object_classname, "SimulationYears")
        self.stage_object_parameter_values(self.configuration_object_classname, "SimulationYears",
                                           [("initialization_investment", initialization_investment)], "0")

    def get_last_iteration(self):
        return self.db.query_object_parameter_values_by_object_class_name_parameter_and_alternative(
            self.configuration_object_classname, "SimulationYears",
            "InvestmentIteration", "0")

    def stage_iteration(self, nextinvestmentIteration):
        self.stage_object_parameter_values(self.configuration_object_classname, "SimulationYears",
                                           [("InvestmentIteration", nextinvestmentIteration)], "0")

    """
    Financial results
    """

    def stage_init_financial_results_structure(self):
        self.stage_object_class(self.financial_reports_object_classname)
        self.stage_object_parameters(self.financial_reports_object_classname,
                                     ['PowerPlant', 'latestTick', 'spotMarketRevenue', 'overallRevenue', 'production',
                                      'powerPlantStatus', 'totalProfits', 'totalProfitswLoans', 'variableCosts',
                                      'fixedCosts', 'totalCosts', 'irr', 'npv'])

    def stage_financial_results(self, financialreports):
        for fr in financialreports:
            object_name = fr.name
            self.stage_object(self.financial_reports_object_classname, object_name)
            self.stage_object_parameter_values(self.financial_reports_object_classname, object_name,
                                               [('PowerPlant', fr.powerPlant),
                                                ('latestTick', (fr.tick)),
                                                ('spotMarketRevenue',
                                                 Map([str(fr.tick)], [float(fr.spotMarketRevenue)])),
                                                ('powerPlantStatus', Map([str(fr.tick)], [str(fr.powerPlantStatus)])),
                                                ('variableCosts', Map([str(fr.tick)], [float(fr.variableCosts)])),
                                                ('totalCosts', Map([str(fr.tick)], [float(fr.totalCosts)])),
                                                ('totalProfits', Map([str(fr.tick)], [float(fr.totalProfits)])),
                                                ('totalProfitswLoans',
                                                 Map([str(fr.tick)], [float(fr.totalProfitswLoans)])),
                                                ('irr', Map([str(fr.tick)], [float(fr.irr)])),
                                                ('npv', Map([str(fr.tick)], [float(fr.npv)])),
                                                ],
                                               '0')

    def stage_init_loans_structure(self):
        self.stage_object_class(self.loans_object_classname)
        self.stage_object_parameters(self.loans_object_classname,
                                     ['amountPerPayment', 'numberOfPaymentsDone', 'loanStartTick',
                                      'totalNumberOfPayments'])

    def stage_loans(self, pp):
        self.stage_object(self.loans_object_classname, str(pp.name))
        self.stage_object_parameter_values(self.loans_object_classname, str(pp.name),
                                           [('amountPerPayment', pp.loan.amountPerPayment),
                                            ('numberOfPaymentsDone', pp.loan.numberOfPaymentsDone),
                                           # ('loanStartTick', pp.loan.loanStartTick), # loans start tick are determined in the payloans function
                                            ('totalNumberOfPayments', pp.loan.totalNumberOfPayments)
                                            ],
                                           '0')

    def stage_init_downpayments_structure(self):
        self.stage_object_class(self.downpayments_object_classname)
        self.stage_object_parameters(self.downpayments_object_classname,
                                     ['amountPerPayment', 'numberOfPaymentsDone', 'loanStartTick',
                                      'totalNumberOfPayments'])

    def stage_downpayments(self, pp):
        self.stage_object(self.downpayments_object_classname, str(pp.name))
        self.stage_object_parameter_values(self.downpayments_object_classname, str(pp.name),
                                           [('amountPerPayment', pp.downpayment.amountPerPayment),
                                            ('numberOfPaymentsDone', pp.downpayment.numberOfPaymentsDone),
                                           # ('loanStartTick', pp.downpayment.loanStartTick),# loans start tick are determined in the payloans function
                                            ('totalNumberOfPayments', pp.downpayment.totalNumberOfPayments)
                                            ],
                                           '0')

    def set_number_loan_payments(self, pp):
        self.stage_object(self.loans_object_classname, pp.name)
        self.stage_object_parameter_values(self.loans_object_classname, pp.name,
                                           [('numberOfPaymentsDone', pp.loan.numberOfPaymentsDone)
                                            ],
                                           '0')

    def set_number_downpayments_done(self, pp):
        self.stage_object(self.downpayments_object_classname, pp.name)
        self.stage_object_parameter_values(self.downpayments_object_classname, pp.name,
                                           [('numberOfPaymentsDone', pp.downpayment.numberOfPaymentsDone)
                                            ],
                                           '0')

    def stage_cash_plant(self, plant: object):
        self.stage_object(self.powerplant_installed_classname, plant.name)
        self.stage_object_parameter_values(self.powerplant_installed_classname, plant.name,
                                           [('cash', plant.cash)
                                            ],
                                           '0')
    def stage_init_load_shedded(self):
        self.stage_object_class(self.load_shedders_classname)
        self.stage_object_parameters(self.load_shedders_classname, ['realized_LOLE'])

    def stage_load_shedders_realized_lole(self, realized_LOLE, tick):
        # iterate over elements in the series realized_curtailments
        for ls_name, ls in realized_LOLE.iteritems():
            self.stage_object(self.load_shedders_classname, ls_name)
            self.stage_object_parameter_values(self.load_shedders_classname, ls_name,
            [("realized_LOLE", Map([str(tick)], [ls]))], "0")


    def stage_load_shedders_voll_not_hydrogen(self, load_shedders, year):
        for ls_name, ls in load_shedders.items():
            if ls_name == "hydrogen":
                pass
            else:
                self.stage_object(self.load_shedders_classname, ls_name)
                self.stage_object_parameter_values(self.load_shedders_classname, ls_name,
                                                   [("percentage_load", Map([str(year)], [ls.percentageLoad]))], "0")

    def stage_consumers_bids(self , consumer, bid, tick):
        self.stage_object(self.consumer_classname, consumer)
        self.stage_object_parameter_values(self.consumer_classname, consumer,
                                           [("bid", Map([str(tick)], [bid]))], "0")

    def stage_consumer_subscribed_yearly(self , consumer, subscribed_yearly ,  tick):
        self.stage_object(self.consumer_classname, consumer)
        self.stage_object_parameter_values(self.consumer_classname, consumer,
                                           [("subscribed_yearly", Map([str(tick)], [subscribed_yearly]))], "0")

    def stage_subscribed_volume_yearly(self , consumer,subscribed_volume ,  tick):
        self.stage_object(self.consumer_classname, consumer)
        self.stage_object_parameter_values(self.consumer_classname, consumer,
                                           [("subscribed_volume", Map([str(tick)], [subscribed_volume]))], "0")



    def stage_init_cash_agent(self):
        self.stage_object_class(self.energyProducer_classname)
        self.stage_object_parameters(self.energyProducer_classname, ['cash',
                                                                     'CF_ELECTRICITY_SPOT',
                                                                     'CF_LOAN',
                                                                     'CF_DOWNPAYMENT',
                                                                     'CF_LOAN_NEW_PLANTS',
                                                                     'CF_DOWNPAYMENT_NEW_PLANTS',
                                                                     'CF_STRRESPAYMENT',
                                                                     'CF_CAPMARKETPAYMENT',
                                                                     'CF_FIXEDOMCOST',
                                                                     'RETURN_CONSUMERS',
                                                                     'CF_COMMODITY'])

    def stage_cash_agent(self, agent, current_tick):
        self.stage_object(self.energyProducer_classname, agent.name)
        self.stage_object_parameter_values(self.energyProducer_classname, agent.name,
                                           [
                                               ('CF_ELECTRICITY_SPOT',
                                                Map([str(current_tick)], [float(agent.CF_ELECTRICITY_SPOT)])),
                                               ('CF_LOAN', Map([str(current_tick)], [float(agent.CF_LOAN)])),
                                               (
                                                   'CF_LOAN_NEW_PLANTS',
                                                   Map([str(current_tick)], [float(agent.CF_LOAN_NEW_PLANTS)])),
                                               (
                                                   'CF_DOWNPAYMENT',
                                                   Map([str(current_tick)], [float(agent.CF_DOWNPAYMENT)])),

                                               (
                                                   'RETURN_CONSUMERS',
                                                   Map([str(current_tick)], [float(agent.RETURN_CONSUMERS)])),


                                               (
                                                   'CF_DOWNPAYMENT_NEW_PLANTS',
                                                   Map([str(current_tick)], [float(agent.CF_DOWNPAYMENT_NEW_PLANTS)])),

                                               ('CF_STRRESPAYMENT',
                                                Map([str(current_tick)], [float(agent.CF_STRRESPAYMENT)])),
                                               ('CF_CAPMARKETPAYMENT',
                                                Map([str(current_tick)], [float(agent.CF_CAPMARKETPAYMENT)])),
                                               (
                                                   'CF_FIXEDOMCOST',
                                                   Map([str(current_tick)], [float(agent.CF_FIXEDOMCOST)])),
                                               ('CF_COMMODITY', Map([str(current_tick)], [float(agent.CF_COMMODITY)]))
                                           ],
                                           '0')

    # todo this could also be read as all other functions but then it would be read in each step.
    def findFinancialValueForPlant(self, powerplant, value):
        financialresults = self.db.query_object_parameter_values_by_object_class_name_parameter_and_alternative(
            self.financial_reports_object_classname, powerplant.name, value, 0)
        if not financialresults:
            print("NO financial results of plant " + powerplant.name)
            return None
        return financialresults[0]['parameter_value'].to_dict()

    def stage_init_capacitymechanisms_structure(self):
        self.stage_object_class(self.financial_reports_object_classname)
        self.stage_object_parameters(self.financial_reports_object_classname,
                                     ['capacityMechanismRevenues'])

    def stage_CM_revenues(self, power_plant, amount, ticks):
        self.stage_object(self.financial_reports_object_classname, power_plant)
        for tick in ticks:
            self.stage_object_parameter_values(self.financial_reports_object_classname, power_plant,
                                           [('capacityMechanismRevenues', Map([str(tick)], [amount]))],
                                           '0')


    """
    Fuel prices
    """

    def stage_init_next_prices_structure(self):
        self.stage_object_class(self.fuel_classname)
        self.stage_object_parameters(self.fuel_classname, [globalNames.simulated_prices])

    def stage_init_future_prices_structure(self):
        self.stage_object_class(self.fuel_classname)
        self.stage_object_parameters(self.fuel_classname, [globalNames.future_prices])

    def stage_target_investments_done(self, done):
        self.stage_object_class(self.configuration_object_classname)
        self.stage_object_parameter(self.configuration_object_classname, "target_investments_done")
        self.stage_object_parameter_values(self.configuration_object_classname, "SimulationYears",
                                           [("target_investments_done", done)], "0")

    # def stage_testing_intermittent_technologies(self, status_testing):
    #     self.stage_object_class(self.configuration_object_classname)
    #     self.stage_object_parameter(self.configuration_object_classname, "testing_intermittent_technologies")
    #     self.stage_object_parameter_values(self.configuration_object_classname, "SimulationYears",
    #                                        [("testing_intermittent_technologies", status_testing)], "0")

    def stage_simulated_fuel_prices(self, year, price, substance):
        object_name = substance.name
        self.stage_object(self.fuel_classname, object_name)
        self.db.import_object_parameter_values(
            [(self.fuel_classname, substance.name, globalNames.simulated_prices, Map([str(year)], [price]), '0')])

    def stage_future_fuel_prices(self, year, substance, futurePrice):
        object_name = substance.name
        self.stage_object(self.fuel_classname, object_name)
        self.db.import_object_parameter_values(
            [(self.fuel_classname, substance.name, globalNames.future_prices, Map([str(year)], [futurePrice]), '0')])

    def get_calculated_simulated_fuel_prices(self, substance, parametername):
        calculated_fuel_prices = self.db.query_object_parameter_values_by_object_class_name_parameter_and_alternative(
            self.fuel_classname, substance, parametername, 0)
        return calculated_fuel_prices[0]['parameter_value'].to_dict()

    def get_calculated_simulated_fuel_prices_by_year(self, substance, parametername, year):
        calculated_fuel_prices = self.db.query_object_parameter_values_by_object_class_name_parameter_and_alternative(
            self.fuel_classname, substance, parametername, 0)
        cfp = calculated_fuel_prices[0]['parameter_value'].to_dict()
        df = pd.DataFrame(cfp['data'])
        df.set_index(0, inplace=True)
        value = df.loc[str(year)][1]
        return value

    """
    General
    """

    def stage_init_alternative(self, current_tick: int):
        self.db.import_alternatives([str(current_tick)])

    def stage_object_class(self, object_class_name: str):
        self.stage_object_classes([object_class_name])

    def stage_object_classes(self, arr: list):
        self.db.import_object_classes(arr)

    def stage_object_parameter(self, object_class: str, object_parameter: str):
        self.db.import_data({'object_parameters': [[object_class, object_parameter]]})

    def stage_object_parameters(self, object_class: str, object_parameter_arr: list):
        """
        object parameter must be a list!!!
        """
        for object_parameter in object_parameter_arr:
            self.stage_object_parameter(object_class, object_parameter)

    def stage_object(self, object_class: str, object_name: str):
        """"
        object name has to be a string!!!!
        """
        self.stage_objects([(object_class, object_name)])

    def stage_objects(self, arr_of_tuples: list):
        self.db.import_objects(arr_of_tuples)

    def stage_object_parameter_values(self,
                                      object_class_name: str, object_name: str, arr_of_tuples: list, alternative: int):
        import_arr = [(object_class_name, object_name, i[0], i[1], str(alternative)) for i in arr_of_tuples]
        self.db.import_object_parameter_values(import_arr)


    def delete_rows_DB(self, parametername, values):
        self.db.delete_ids(parametername, values)

    # def stage_object_parameter_time_series(self,
    #                                   object_class_name: str, object_name: str, arr_of_tuples: list, alternative: int):
    #     # ('object_class_name', 'object_name', 'parameter_name', '{"type":"time_series", "data": [1,2,3]}', 'alternative')]
    #     import_arr = [(object_class_name, object_name, i[0],  '{"type":"time_series", "data":' + str(i[1]) + '}' , str(alternative)) for i in arr_of_tuples]
    #     self.db.import_object_parameter_values(import_arr)

    def commit(self, commit_message: str):
        self.db.commit(commit_message)

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return str(vars(self))


def add_parameter_value_to_repository(reps: Repository, db_line: list, to_dict: dict, class_to_create):
    object_name = db_line[1]
    parameter_name = db_line[2]
    parameter_value = db_line[3]
    parameter_alt = db_line[4]  #
    if object_name not in to_dict.keys():
        to_dict[object_name] = class_to_create(object_name)
    to_dict[object_name].add_parameter_value(reps, parameter_name, parameter_value, parameter_alt)


def add_type_to_power_plant(reps: Repository, db_line: list, to_dict: dict):
    classname = db_line[0]
    object_name = db_line[1]
    parameter_alt = db_line[4]
    to_dict[object_name].add_parameter_value(reps, "label", classname, parameter_alt)


def add_relationship_to_repository_array(db_data: dict, to_arr: list, relationship_class_name: str):
    """
    Function used to translate SpineDB relationships to an array of tuples

    :param db_data: The exported data from SpineDB
    :param to_arr: The array in which this data should be exported
    :param relationship_class_name: The SpineDB class name of the relationship
    """
    for unit in [i for i in db_data['relationships'] if i[0] == relationship_class_name]:
        if len(unit[1]) == 2:
            to_arr.append((unit[1][0], unit[1][1]))
        else:
            to_arr.append((unit[1][0], unit[1][1], unit[1][2]))



def add_parameter_value_to_repository_based_on_object_class_name(reps, db_line):
    """
    Function used to translate an object_parameter_value from SpineDB to a Repository dict entry.

    :param candidatePowerPlants: candidate power plants dont need to be added if its not investment
    :param reps: Repository
    :param db_line: Line from exported data from spinedb_api
    """
    object_class_name = db_line[0]
    object_name = db_line[1]
    if object_class_name == 'GeometricTrends':
        add_parameter_value_to_repository(reps, db_line, reps.trends, GeometricTrend)
    elif object_class_name == 'FuelPriceTrends':
        add_parameter_value_to_repository(reps, db_line, reps.trends, TriangularTrend)
    elif object_class_name == 'StepTrends':
        add_parameter_value_to_repository(reps, db_line, reps.trends, StepTrend)
    elif object_class_name == 'Decommissioned':  # this decommissioned is to avoid reading the decommissioned plants
        add_parameter_value_to_repository(reps, db_line, reps.decommissioned, Decommissioned)
    elif object_class_name == 'PowerPlantsInstalled':
        if reps.runningModule == "plotting":
            add_parameter_value_to_repository(reps, db_line, reps.power_plants, PowerPlant)
        else:
            if object_name not in (reps.decommissioned["Decommissioned"]).Done:
                add_parameter_value_to_repository(reps, db_line, reps.power_plants, PowerPlant)
    elif object_class_name == "Storage" and reps.runningModule == "run_prepare_next_year_market_clearing":
        if str(object_name)[0: 4] != "9999":  # Read the state of charge of storages, but not of candidate storage.
            pp_name = reps.get_power_plant_name_by_id(object_name)
            db_line = list(db_line)
            db_line[1] = pp_name
            add_parameter_value_to_repository(reps, db_line, reps.power_plants, PowerPlant)
    elif object_class_name in "CandidatePowerPlants":
        add_parameter_value_to_repository(reps, db_line, reps.candidatePowerPlants, CandidatePowerPlant)
    elif object_class_name == 'NewTechnologies':
        add_parameter_value_to_repository(reps, db_line, reps.newTechnology, NewTechnology)
    elif object_class_name == 'CapacityMarkets':
        add_parameter_value_to_repository(reps, db_line, reps.capacity_markets, CapacityMarket)
    elif object_class_name == 'Cone' and reps.runningModule == "plotting":
        add_parameter_value_to_repository(reps, db_line, reps.capacity_markets, Cone)
    elif object_class_name == 'EnergyProducers':
        add_parameter_value_to_repository(reps, db_line, reps.energy_producers, EnergyProducer)
    elif object_class_name == 'Targets':
        add_parameter_value_to_repository(reps, db_line, reps.target_investors, TargetInvestor)
    # elif object_class_name == 'HydrogenfromOptim':
    #     add_parameter_value_to_repository(reps, db_line, reps.hydrogen_demand, HydrogenDemand)
    elif object_class_name == 'LoadShifterCap':
        add_parameter_value_to_repository(reps, db_line, reps.loadShifterDemand, LoadShifterwCap)
    elif object_class_name == 'Technologies':
        # if db_line[1] in globalNames.used_technologies:
        add_parameter_value_to_repository(reps, db_line, reps.power_generating_technologies,
                                          PowerGeneratingTechnology)
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ data from Traderes
    elif object_class_name == 'Fuels':  # Fuels contain CO2 density energy density, quality
        add_parameter_value_to_repository(reps, db_line, reps.substances, Substance)
    elif object_class_name == 'node':  # Substances and CO2 costs
        add_parameter_value_to_repository(reps, db_line, reps.substances, Substance)
    elif object_class_name == 'ElectricitySpotMarkets':
        add_parameter_value_to_repository(reps, db_line, reps.electricity_spot_markets, ElectricitySpotMarket)
    elif object_class_name == 'Bids' and reps.runningModule in globalNames.modules_need_bids:  # only read this when capacity mechanism and when plotting
        add_parameter_value_to_repository(reps, db_line, reps.bids, Bid)
    elif object_class_name == 'MarketClearingPoints':
        add_parameter_value_to_repository(reps, db_line, reps.market_clearing_points, MarketClearingPoint)
    elif object_class_name == 'LoadShedders':
        add_parameter_value_to_repository(reps, db_line, reps.loadShedders, LoadShedder)
    elif object_class_name == 'StrategicReserveOperators':
        add_parameter_value_to_repository(reps, db_line, reps.sr_operator, StrategicReserveOperator)
    elif object_class_name == 'CapacitySubscriptionConsumer':
        add_parameter_value_to_repository(reps, db_line, reps.cs_consumers, CapacitySubscriptionConsumer)
    elif object_class_name == 'StrategicReserveResults':
        new_db_line = list(db_line)
        new_db_line[1] = "SRO_" + reps.country  # object name
        new_db_line[4] = int(db_line[1])  # alternative
        add_parameter_value_to_repository(reps, new_db_line, reps.sr_operator, StrategicReserveOperator)
    elif object_class_name == 'InvestmentDecisions' and reps.runningModule in ["plotting"]:
        add_parameter_value_to_repository(reps, db_line, reps.investmentDecisions, InvestmentDecisions)
    elif object_class_name == "InstalledDispatchableCapacity" and reps.runningModule == "plotting":
        add_parameter_value_to_repository(reps, db_line, reps.installedCapacity, InstalledCapacity)
    elif object_class_name == "InstalledFuturePowerPlants" :
        add_parameter_value_to_repository(reps, db_line, reps.installedFuturePowerPlants, InstalledFuturePowerPlants)
    elif object_class_name in ['Loans', 'Downpayments'] and reps.runningModule in ["run_financial_results", "plotting", "run_CRM",
                                                                                   "run_investment_module"]:
        if db_line[1] in (reps.decommissioned["Decommissioned"].Done) and reps.runningModule != "plotting":
            pass
        else:
            object_name = db_line[1]
            parameter_name = db_line[2]
            parameter_value = db_line[3]
            pp = reps.power_plants[object_name]
            if object_class_name == "Loans":
                setattr(pp.loan, parameter_name, parameter_value)
            else:
                setattr(pp.downpayment, parameter_name, parameter_value)
    elif object_class_name == 'FinancialReports' :
        add_parameter_value_to_repository(reps, db_line, reps.financialPowerPlantReports, FinancialPowerPlantReport)
    elif object_class_name == 'plantsinCM' :
        add_parameter_value_to_repository(reps, db_line, reps.plantsinCM, PlantsinCM)
    elif object_class_name == 'CandidatePlantsNPV' and reps.runningModule == "plotting":
        add_parameter_value_to_repository(reps, db_line, reps.candidatesNPV, CandidatesNPV)
    elif object_class_name == 'weatherYears' and reps.runningModule in ["plotting", "run_CRM", "run_investment_module"]:
        add_parameter_value_to_repository(reps, db_line, reps.weatherYears, WeatherYears) # this data is prepared in clock.py
    elif object_class_name == "Profits" and reps.runningModule == "plotting":
        # db investment with the object name "tick - iteration"
        object_name = db_line[1]
        tick, iteration = object_name.split('-')
        new_db_line = list(db_line)
        new_db_line[1] = tick  # object name
        new_db_line[4] = iteration  # alternative
        add_parameter_value_to_repository(reps, new_db_line, reps.profits, Profits)
    else:
        logging.info('Object Class not defined: ' + object_class_name)


def add_parameter_value_to_repository_based_on_object_class_name_amiris(self, reps, db_amirisdata):
    for db_line_amiris in db_amirisdata['object_parameter_values']:
        object_class_name = db_line_amiris[0]
        object_name = db_line_amiris[1]
        if reps.runningModule == "plotting":
            new_db_line = list(db_line_amiris)
            new_db_line[1] = db_line_amiris[0]  # pass the class name as the object name
            new_db_line[4] = db_line_amiris[1]  # pass the object name (plant id) as the alternative
            add_parameter_value_to_repository(reps, new_db_line, reps.power_plant_dispatch_plans,
                                              PowerPlantDispatchPlansALL)
        elif object_class_name == str(reps.current_year):  # importing only the current power dispatch plans
            add_parameter_value_to_repository(reps, db_line_amiris, reps.power_plant_dispatch_plans_in_year,
                                              PowerPlantDispatchPlan)

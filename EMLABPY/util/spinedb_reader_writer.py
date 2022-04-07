"""
This is the Python class responsible for all reads and writes of the SpineDB.
This is a separate file so that all import definitions are centralized.
Ingrid Sanchez 18-2-2022 modified
Jim Hommes - 25-3-2021
"""
import logging

from spinedb_api import Map
from twine.repository import Repository

from emlabpy.domain.newTechnology import NewTechnology
from emlabpy.util.repository import *
from emlabpy.util.spinedb import SpineDB


class SpineDBReaderWriter:
    """
    The class that handles all writing and reading to the SpineDB.
    """

    def __init__(self, run_module, *db_urls: str):
        self.db_urls = db_urls
        self.db = SpineDB(db_urls[0]) # the first is always emlab
        self.run_module = run_module
        self.powerplant_dispatch_plan_classname = 'PowerPlantDispatchPlans'
        self.market_clearing_point_object_classname = 'MarketClearingPoints'
        self.financial_reports_object_classname = 'financialPowerPlantReports'
        self.fuel_classname = "node"
        self.configuration_object_classname = "Configuration"
        self.energyProducer_classname = "EnergyProducers"
        self.ConventionalOperator_classname = "ConventionalPlantOperator"
        self.VariableRenewableOperator_classname = "VariableRenewableOperator"
        if run_module == "run_investment_module":
            self.amirisdb = SpineDB(db_urls[1])

    def read_db_and_create_repository(self) -> Repository:
        """
        This function add all info from EMLAB DB to REPOSITORY
        """
        logging.info('SpineDBRW: Start Read Repository')
        reps = Repository()
        reps.dbrw = self
        db_data = self.db.export_data()
        self.stage_init_alternative("0")
        # todo: later this should not be hardcoded
        #candidatePowerPlants = [i[0] for i in db_amirisdata["alternatives"]]
        candidatePowerPlants = [503, 49]
        for row in self.db.query_object_parameter_values_by_object_class('Configuration'):
            if row['parameter_name'] == 'SimulationTick':
                reps.current_tick = int(row['parameter_value'])
            elif row['parameter_name'] == 'Time Step':
                reps.time_step = int(row['parameter_value'])
            elif row['parameter_name'] == 'Start Year':
                reps.start_simulation_year = int(row['parameter_value'])
            elif row['parameter_name'] == 'End Year':
                reps.end_simulation_year = int(row['parameter_value'])
                reps.simulation_length = reps.end_simulation_year - reps.start_simulation_year
            elif row['parameter_name'] == 'Look Ahead':
                reps.lookAhead = int(row['parameter_value'])
            elif row['parameter_name'] == 'CurrentYear':
                reps.current_year = int(row['parameter_value'])

        parameter_priorities = {i['parameter_name']: i['parameter_value'] for i
                                in self.db.query_object_parameter_values_by_object_class_and_object_name("Configuration", "priority")}
        sorted_parameter_names = sorted(db_data['object_parameters'],
                                        key=lambda item: parameter_priorities[item[0]]
                                        if item[0] in parameter_priorities.keys() else 0, reverse=True)
        object_parameter_values = db_data['object_parameter_values']

        for (object_class_name, parameter_name, _, _, _) in sorted_parameter_names:
            for (_, object_name, _) in [i for i in db_data['objects'] if i[0] == object_class_name]:
                try:
                    db_line = next(i for i in object_parameter_values
                                   if i[0] == object_class_name and i[1] == object_name and i[2] == parameter_name)
                    add_parameter_value_to_repository_based_on_object_class_name(reps, db_line, candidatePowerPlants)
                except StopIteration:
                    logging.warning('No value found for class: ' + object_class_name +
                                    ', object: ' + object_name +
                                    ', parameter: ' + parameter_name)

        if self.run_module == "run_investment_module":
            db_amirisdata = self.amirisdb.export_data()
            add_parameter_value_to_repository_based_on_object_class_name_amiris(self, reps, db_amirisdata, candidatePowerPlants)

        return reps

    # def stage_cashflow_PowerPlant(self, current_tick: int):
    #     self.stage_init_alternative("0")
    #     self.stage_object(self.powerplant_dispatch_plan_classname, ppdp.name)
    #     self.stage_object_parameter_values(self.powerplant_dispatch_plan_classname, ppdp.name,
    #                                        [('Plant', ppdp.plant.name),
    #                                         ('Market', ppdp.bidding_market.name),
    #                                         ('Price', ppdp.price),
    #                                         ('Capacity', ppdp.amount),
    #                                         ('EnergyProducer', ppdp.bidder.name),
    #                                         ('AcceptedAmount', ppdp.accepted_amount),
    #                                         ('Status', ppdp.status)], current_tick)
    #     for row in self.db.query_object_parameter_values_by_object_class_and_object_name('Configuration', "SimulationYears"):
    #         if row['parameter_name'] == 'Start Year':
    #             reps.start_simulation_year = int(row['parameter_value'])
    #         elif row['parameter_name'] == 'End Year':
    #             reps.end_simulation_year = int(row['parameter_value'])
    #         elif row['parameter_name'] == 'Look Ahead':
    #             reps.lookAhead = int(row['parameter_value'])

    def stage_power_plant_status(self, power_plant_status):
        #self.stage_object_parameter(power_plant_type, 'Status')
        self.db.import_object_parameter_values(power_plant_status)

    """
    Staging functions that are the core for communicating with SpineDB
    
    TO ADD DATA TO DB
    """

    def stage_object_class(self, object_class_name: str):
        self.stage_object_classes([object_class_name])

    def stage_object_classes(self, arr: list):
        self.db.import_object_classes(arr)

    def stage_object_parameter(self, object_class: str, object_parameter: str):
        self.db.import_data({'object_parameters': [[object_class, object_parameter]]})

    def stage_object_parameters(self, object_class: str, object_parameter_arr: list):
        for object_parameter in object_parameter_arr:
            self.stage_object_parameter(object_class, object_parameter)

    def stage_object(self, object_class: str, object_name: str):
        self.stage_objects([(object_class, object_name)])

    def stage_objects(self, arr_of_tuples: list):
        self.db.import_objects(arr_of_tuples)

    def stage_object_parameter_values(self,
                                      object_class_name: str, object_name: str, arr_of_tuples: list, alternative: int):
        import_arr = [(object_class_name, object_name, i[0], i[1], str(alternative)) for i in arr_of_tuples]
        self.db.import_object_parameter_values(import_arr)

    # def stage_object_parameter_time_series(self,
    #                                   object_class_name: str, object_name: str, arr_of_tuples: list, alternative: int):
    #     # ('object_class_name', 'object_name', 'parameter_name', '{"type":"time_series", "data": [1,2,3]}', 'alternative')]
    #     import_arr = [(object_class_name, object_name, i[0],  '{"type":"time_series", "data":' + str(i[1]) + '}' , str(alternative)) for i in arr_of_tuples]
    #     self.db.import_object_parameter_values(import_arr)

    def commit(self, commit_message: str):
        self.db.commit(commit_message)

    """
    Element specific initialization staging functions
    TO ADD SPECIFICALLY TO DB
    """

    def stage_init_market_clearing_point_structure(self):
        self.stage_object_class(self.market_clearing_point_object_classname)
        self.stage_object_parameters(self.market_clearing_point_object_classname, ['Market', 'Price', 'TotalCapacity'])

    def stage_init_power_plant_dispatch_plan_structure(self):
        self.stage_object_class(self.powerplant_dispatch_plan_classname)
        self.stage_object_parameters(self.powerplant_dispatch_plan_classname,
                                     ['Plant', 'Market', 'Price', 'Capacity', 'EnergyProducer', 'AcceptedAmount',
                                      'powerPlantStatus'])

    def stage_init_financial_results_structure(self):
        self.stage_object_class(self.financial_reports_object_classname)
        self.stage_object_parameters(self.financial_reports_object_classname,
                                 ['PowerPlant', 'latestTick','spotMarketRevenue','overallRevenue', 'production', 'powerPlantStatus','profit'])

    def stage_init_next_prices_structure(self):
        self.stage_object_class(self.fuel_classname)
        self.stage_object_parameters(self.fuel_classname, ['simulatedPrice'])

    def stage_init_future_prices_structure(self):
        self.stage_object_class(self.fuel_classname)
        self.stage_object_parameters(self.fuel_classname, ['futurePrice'])

    def stage_init_alternative(self, current_tick: int):
        self.db.import_alternatives([str(current_tick)])

    """
    Element specific staging functions
    """

    def stage_power_plant_dispatch_plan(self, ppdp: PowerPlantDispatchPlan, current_tick: int):
        self.stage_object(self.powerplant_dispatch_plan_classname, ppdp.name)
        self.stage_object_parameter_values(self.powerplant_dispatch_plan_classname, ppdp.name,
                                           [('Plant', ppdp.plant.name),
                                            ('Market', ppdp.bidding_market.name),
                                            ('Price', ppdp.price),
                                            ('Capacity', ppdp.amount),
                                            ('EnergyProducer', ppdp.bidder.name),
                                            ('AcceptedAmount', ppdp.accepted_amount),
                                            ('Status', ppdp.status)], current_tick)

    def stage_financial_results(self, fr):
        object_name = fr.name
        self.stage_object(self.financial_reports_object_classname, object_name)
        self.stage_object_parameter_values(self.financial_reports_object_classname, object_name,
                                           [('PowerPlant', fr.powerPlant),
                                            ('latestTick', (fr.tick)),
                                            ('spotMarketRevenue', (fr.spotMarketRevenue)),
                                            ('overallRevenue',  Map([str(fr.tick)], [fr.overallRevenue])),
                                            ('production', Map([str(fr.tick)], [fr.production])),
                                            ('powerPlantStatus', Map([str(fr.tick)], [fr.powerPlantStatus])),
                                            ('profit', Map([str(fr.tick)], [fr.profit]))],
                                           '0')

    def stage_simulated_fuel_prices(self, tick, price, substance):
        object_name = substance.name
        self.stage_object(self.fuel_classname, object_name)
        #print(self.fuel_classname, substance.name, "simulatedPrice", tick,"-", type(price), price)
        self.db.import_object_parameter_values([(self.fuel_classname, substance.name, "simulatedPrice", Map([str(tick)], [price]) , '0')])


    def stage_future_fuel_prices(self, year, substance, futurePrice):
        object_name = substance.name
        self.stage_object(self.fuel_classname, object_name)
        self.db.import_object_parameter_values([(self.fuel_classname, substance.name, "futurePrice", Map([str(year)], [futurePrice]), '0')])

    def get_calculated_future_fuel_prices(self, substance):
        calculated_future_fuel_prices = self.db.query_object_parameter_values_by_object_class_name_parameter_and_alternative(self.fuel_classname, substance.name, "futurePrice", 0)
        return calculated_future_fuel_prices[0]['parameter_value'].to_dict()

    def get_calculated_simulated_fuel_prices(self, substance):
        calculated_fuel_prices = self.db.query_object_parameter_values_by_object_class_name_parameter_and_alternative(self.fuel_classname, substance.name, "simulatedPrice", 0)
        return calculated_fuel_prices[0]['parameter_value'].to_dict()

    def stage_market_clearing_point(self, mcp: MarketClearingPoint, current_tick: int):
        object_name = mcp.name
        self.stage_object(self.market_clearing_point_object_classname, object_name)
        self.stage_object_parameter_values(self.market_clearing_point_object_classname, object_name,
                                           [('Market', mcp.market.name),
                                            ('Price', mcp.price),
                                            ('TotalCapacity', mcp.capacity)], current_tick)

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

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return str(vars(self))


def add_parameter_value_to_repository(reps: Repository, db_line: list, to_dict: dict, class_to_create):
    object_name = db_line[1]
    parameter_name = db_line[2]
    parameter_value = db_line[3]
    parameter_alt = db_line[4]
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

def add_parameter_value_to_repository_based_on_object_class_name(reps, db_line, candidatePowerPlants):
    """
    Function used to translate an object_parameter_value from SpineDB to a Repository dict entry.

    :param candidatePowerPlants: candidate power plants dont need to be added if its not investment
    :param reps: Repository
    :param db_line: Line from exported data from spinedb_api
    """
    object_class_name = db_line[0]
    object_name = db_line[1]
    if object_class_name == 'trends':
        add_parameter_value_to_repository(reps, db_line, reps.trends, TriangularTrend)
    elif object_class_name == 'StepTrends':
        add_parameter_value_to_repository(reps, db_line, reps.trends, StepTrend)
    elif object_class_name in ['ConventionalPlantOperator', 'VariableRenewableOperator']:# TODO add  'StorageTrader'
        if object_name not in candidatePowerPlants:
            add_parameter_value_to_repository(reps, db_line, reps.power_plants, PowerPlant)
            add_type_to_power_plant(reps, db_line, reps.power_plants)
        else:
            add_parameter_value_to_repository(reps, db_line, reps.candidatePowerPlants, CandidatePowerPlant)
    elif object_class_name == 'NewTechnologies':
        add_parameter_value_to_repository(reps, db_line, reps.newTechnology, NewTechnology)
    elif object_class_name == 'CapacityMarkets':
        add_parameter_value_to_repository(reps, db_line, reps.capacity_markets, CapacityMarket)
    elif object_class_name == 'TechnologiesEmlab':
        add_parameter_value_to_repository(reps, db_line, reps.power_generating_technologies, PowerGeneratingTechnology)
    # data from Traderes
    elif object_class_name == 'unit':
        add_parameter_value_to_repository(reps, db_line, reps.power_generating_technologies, PowerGeneratingTechnology)
    elif object_class_name == 'electricity':
        add_parameter_value_to_repository(reps, db_line, reps.power_generating_technologies, PowerGeneratingTechnology)
    elif object_class_name == 'Fuels': # Fuels contain CO2 density energy density, quality
        add_parameter_value_to_repository(reps, db_line, reps.substances, Substance)
    elif object_class_name == 'node': # node contain the # TODO complete this to the scenario
        add_parameter_value_to_repository(reps, db_line, reps.substances, Substance)
    elif object_class_name == 'EnergyProducers':
        add_parameter_value_to_repository(reps, db_line, reps.energy_producers, EnergyProducer)
    else:
        logging.info('Object Class not defined: ' + object_class_name)
    # elif object_class_name == 'Zones':
    #     add_parameter_value_to_repository(reps, db_line, reps.zones, Zone)
    # elif object_class_name == 'ElectricitySpotMarkets':
    #     add_parameter_value_to_repository(reps, db_line, reps.electricity_spot_markets, ElectricitySpotMarket)
    # elif object_class_name == 'CO2Auction':
    #     add_parameter_value_to_repository(reps, db_line, reps.co2_markets, CO2Market)
    # elif object_class_name == 'Hourly Demand':
    #     add_parameter_value_to_repository(reps, db_line, reps.load, HourlyLoad)
    # elif object_class_name == 'PowerGridNodes':
    #     add_parameter_value_to_repository(reps, db_line, reps.power_grid_nodes, PowerGridNode)
    # elif object_class_name == 'PowerPlants':
    #     add_parameter_value_to_repository(reps, db_line, reps.power_plants, PowerPlant)
    # elif object_class_name == 'PowerPlantDispatchPlans':
    #     add_parameter_value_to_repository(reps, db_line, reps.power_plant_dispatch_plans, PowerPlantDispatchPlan)
    # elif object_class_name == 'MarketClearingPoints':
    #     add_parameter_value_to_repository(reps, db_line, reps.market_clearing_points, MarketClearingPoint)
    # elif object_class_name == 'NationalGovernments':
    #     add_parameter_value_to_repository(reps, db_line, reps.national_governments, NationalGovernment)
    # elif object_class_name == 'Governments':
    #     add_parameter_value_to_repository(reps, db_line, reps.governments, Government)
    # elif object_class_name == 'MarketStabilityReserve':
    #     add_parameter_value_to_repository(reps, db_line, reps.market_stability_reserves, MarketStabilityReserve)
    #elif object_class_name == 'PowerGeneratingTechnologyFuel':
    #     add_parameter_value_to_repository(reps, db_line, reps.power_plants_fuel_mix, SubstanceInFuelMix)
    # elif object_class_name == 'YearlyEmissions':
    #     add_parameter_value_to_repository(reps, db_line, reps.emissions, YearlyEmissions)

def add_parameter_value_to_repository_based_on_object_class_name_amiris(self, reps, db_amirisdata, candidatePowerPlants):
    for db_line_amiris in db_amirisdata['object_parameter_values']:
        object_class_name = db_line_amiris[0]
        object_name = db_line_amiris[1]
        if object_class_name == self.ConventionalOperator_classname:
            if object_name in candidatePowerPlants:
                add_parameter_value_to_repository(reps, db_line_amiris, reps.candidatePowerPlants, CandidatePowerPlant)
            else:
                add_parameter_value_to_repository(reps, db_line_amiris, reps.power_plants, PowerPlant)
        elif object_class_name == self.VariableRenewableOperator_classname:
            if object_name in candidatePowerPlants:
                add_parameter_value_to_repository(reps, db_line_amiris, reps.candidatePowerPlants, CandidatePowerPlant)
            else:
                add_parameter_value_to_repository(reps, db_line_amiris, reps.power_plants, PowerPlant)
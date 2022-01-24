"""
This is the Python class responsible for all reads and writes of the SpineDB.
This is a separate file so that all import definitions are centralized.

Jim Hommes - 25-3-2021
"""
import logging

from util.repository import *
from util.spinedb import SpineDB


class SpineDBReaderWriter:
    """
    The class that handles all writing and reading to the SpineDB.
    """

    def __init__(self, db_url: str, config_url: str):
        self.db_url = db_url
        self.config_db = SpineDB(config_url)
        self.db = SpineDB(db_url)
        self.powerplant_dispatch_plan_classname = 'PowerPlantDispatchPlans'
        self.market_clearing_point_object_classname = 'MarketClearingPoints'

    def read_db_and_create_repository(self) -> Repository:
        logging.info('SpineDBRW: Start Read Repository')
        reps = Repository()
        reps.dbrw = self
        db_data = self.db.export_data()

        # Determine current tick
        reps.current_tick = max(
            [int(i[3]) for i in db_data['object_parameter_values'] if i[0] == i[1] == 'SystemClockTicks' and
             i[2] == 'ticks'])
        logging.info('Current tick: ' + str(reps.current_tick))
        self.stage_init_alternative(reps.current_tick)

        # Load Coupling Parameters and set in repository
        for row in self.config_db.query_object_parameter_values_by_object_class('Coupling Parameters'):
            if row['object_name'] == 'Start Year':
                reps.start_simulation_year = int(row['parameter_value'])
            elif row['object_name'] == 'Time Step':
                reps.time_step = int(row['parameter_value'])

        # Load the parameter priorities from the config db
        parameter_priorities = {i['parameter_name']: i['parameter_value'] for i
                                in self.config_db.query_object_parameter_values_by_object_class('EMLAB Parameters')}

        # Sort the object_parameter_values and object_parameters
        # so that the most recent (highest tick) and highest priority is first selected.
        sorted_object_parameter_values = sorted(db_data['object_parameter_values'], reverse=True,
                                                key=lambda item: int(item[4]))
        sorted_parameter_names = sorted(db_data['object_parameters'],
                                        key=lambda item: parameter_priorities[item[0]]
                                        if item[0] in parameter_priorities.keys() else 0, reverse=True)

        # Import all object parameter values in one go
        for (object_class_name, parameter_name, _, _, _) in sorted_parameter_names:
            for (_, object_name, _) in [i for i in db_data['objects'] if i[0] == object_class_name]:
                try:
                    db_line = next(i for i in sorted_object_parameter_values
                                   if i[0] == object_class_name and i[1] == object_name and i[2] == parameter_name and
                                   int(i[4]) <= reps.current_tick)
                    add_parameter_value_to_repository_based_on_object_class_name(reps, db_line)
                except StopIteration:
                    logging.warning('No value found for class: ' + object_class_name +
                                    ', object: ' + object_name +
                                    ', parameter: ' + parameter_name)

        # Because of COMPETES structure, this is hard to set normally. So separate function:
        set_expected_lifetimes_of_power_generating_technologies(reps, db_data, 'PowerGeneratingTechnologyLifetime')

        logging.info('SpineDBRW: End Read Repository')
        # logging.info('Repository: ' + str(reps))
        return reps

    """
    Staging functions that are the core for communicating with SpineDB
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
                                      object_class_name: str, object_name: str, arr_of_tuples: list, current_tick: int):
        import_arr = [(object_class_name, object_name, i[0], i[1], str(current_tick)) for i in arr_of_tuples]
        self.db.import_object_parameter_values(import_arr)

    def commit(self, commit_message: str):
        self.db.commit(commit_message)

    """
    Element specific initialization staging functions
    """

    def stage_init_market_clearing_point_structure(self):
        self.stage_object_class(self.market_clearing_point_object_classname)
        self.stage_object_parameters(self.market_clearing_point_object_classname, ['Market', 'Price', 'TotalCapacity'])

    def stage_init_power_plant_dispatch_plan_structure(self):
        self.stage_object_class(self.powerplant_dispatch_plan_classname)
        self.stage_object_parameters(self.powerplant_dispatch_plan_classname,
                                     ['Plant', 'Market', 'Price', 'Capacity', 'EnergyProducer', 'AcceptedAmount',
                                      'Status'])

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
    # logging.info('Adding parameter value: {object_name: ' + str(object_name)
    #              + ', parameter_name: ' + str(parameter_name)
    #              + ', parameter_value: ' + str(parameter_value)
    #              + ', parameter_alt: ' + str(parameter_alt) + '}')
    if object_name not in to_dict.keys():
        to_dict[object_name] = class_to_create(object_name)

    to_dict[object_name].add_parameter_value(reps, parameter_name, parameter_value, parameter_alt)


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


def set_expected_lifetimes_of_power_generating_technologies(reps: Repository, db_data: dict, object_class_name: str):
    """
    Separate function to add lifetime to PowerGeneratingTechnology objects. This is due to structure conflict with
    COMPETES.

    :param reps: Repository
    :param db_data: Exported data from spinedb_api
    :param object_class_name: The object_class_name for PowerGeneratingTechnology
    """
    for unit in [i for i in db_data['object_parameter_values'] if i[0] == object_class_name]:
        for [key, value] in unit[3].to_dict()['data']:
            logging.info('PowerGeneratingTechnology found: ' + object_class_name + ', expected lifetime: ' + str(value))
            reps.get_power_generating_technology_by_techtype_and_fuel(unit[1], key).expected_lifetime = float(value)


def add_parameter_value_to_repository_based_on_object_class_name(reps, db_line):
    """
    Function used to translate an object_parameter_value from SpineDB to a Repository dict entry.

    :param reps: Repository
    :param db_line: Line from exported data from spinedb_api
    """

    object_class_name = db_line[0]
    if object_class_name == 'GeometricTrends':
        add_parameter_value_to_repository(reps, db_line, reps.trends, GeometricTrend)
    elif object_class_name == 'TriangularTrends':
        add_parameter_value_to_repository(reps, db_line, reps.trends, TriangularTrend)
    elif object_class_name == 'StepTrends':
        add_parameter_value_to_repository(reps, db_line, reps.trends, StepTrend)
    elif object_class_name == 'Zones':
        add_parameter_value_to_repository(reps, db_line, reps.zones, Zone)
    elif object_class_name == 'EnergyProducers':
        add_parameter_value_to_repository(reps, db_line, reps.energy_producers, EnergyProducer)
    elif object_class_name == 'Substances':
        add_parameter_value_to_repository(reps, db_line, reps.substances, Substance)
    elif object_class_name == 'ElectricitySpotMarkets':
        add_parameter_value_to_repository(reps, db_line, reps.electricity_spot_markets, ElectricitySpotMarket)
    elif object_class_name == 'CO2Auction':
        add_parameter_value_to_repository(reps, db_line, reps.co2_markets, CO2Market)
    elif object_class_name == 'CapacityMarkets':
        add_parameter_value_to_repository(reps, db_line, reps.capacity_markets, CapacityMarket)
    elif object_class_name == 'PowerGeneratingTechnologies':
        add_parameter_value_to_repository(reps, db_line, reps.power_generating_technologies, PowerGeneratingTechnology)
    elif object_class_name == 'Hourly Demand':
        add_parameter_value_to_repository(reps, db_line, reps.load, HourlyLoad)
    elif object_class_name == 'PowerGridNodes':
        add_parameter_value_to_repository(reps, db_line, reps.power_grid_nodes, PowerGridNode)
    elif object_class_name == 'PowerPlants':
        add_parameter_value_to_repository(reps, db_line, reps.power_plants, PowerPlant)
    elif object_class_name == 'PowerPlantDispatchPlans':
        add_parameter_value_to_repository(reps, db_line, reps.power_plant_dispatch_plans, PowerPlantDispatchPlan)
    elif object_class_name == 'MarketClearingPoints':
        add_parameter_value_to_repository(reps, db_line, reps.market_clearing_points, MarketClearingPoint)
    elif object_class_name == 'NationalGovernments':
        add_parameter_value_to_repository(reps, db_line, reps.national_governments, NationalGovernment)
    elif object_class_name == 'Governments':
        add_parameter_value_to_repository(reps, db_line, reps.governments, Government)
    elif object_class_name == 'MarketStabilityReserve':
        add_parameter_value_to_repository(reps, db_line, reps.market_stability_reserves, MarketStabilityReserve)
    elif object_class_name == 'PowerGeneratingTechnologyFuel':
        add_parameter_value_to_repository(reps, db_line, reps.power_plants_fuel_mix, SubstanceInFuelMix)
    elif object_class_name == 'YearlyEmissions':
        add_parameter_value_to_repository(reps, db_line, reps.emissions, YearlyEmissions)
    else:
        logging.info('Object Class not defined: ' + object_class_name)

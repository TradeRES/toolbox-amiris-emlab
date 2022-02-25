"""
This is the Python class responsible for all reads and writes of the SpineDB.
This is a separate file so that all import definitions are centralized.
Ingrid Sanchez 18-2-2022 modified
Jim Hommes - 25-3-2021
"""
import logging

from twine.repository import Repository

from emlabpy.domain.CandidatePowerPlant import CandidatePowerPlant
from emlabpy.util.repository import *
from emlabpy.util.spinedb import SpineDB


class SpineDBReaderWriter:
    """
    The class that handles all writing and reading to the SpineDB.
    """

    def __init__(self, db_url: str, secondURL: str, run_investment_module):
        self.db_url = db_url
        self.db = SpineDB(db_url)
        self.amirisdb = SpineDB(secondURL)
        self.amirisdb = SpineDB(secondURL)
        self.run_investment_module = run_investment_module
        self.powerplant_dispatch_plan_classname = 'PowerPlantDispatchPlans'
        self.market_clearing_point_object_classname = 'MarketClearingPoints'
        self.energyProducer_classname = "EnergyProducers"
        self.ConventionalOperator_classname = "ConventionalPlantOperator"
        self.VariableRenewableOperator_classname = "VariableRenewableOperator"


    def read_db_and_create_repository(self) -> Repository:
        """
        This function add all info from EMLAB DB to REPOSITORY
        """
        logging.info('SpineDBRW: Start Read Repository')
        reps = Repository()
        reps.dbrw = self
        db_data = self.db.export_data()
        self.stage_init_alternative("0")
        for row in self.db.query_object_parameter_values_by_object_class('Configuration'):
            if row['parameter_name'] == 'SimulationTick':
                reps.current_tick = int(row['parameter_value'])
            elif row['parameter_name'] == 'Time Step':
                reps.time_step = int(row['parameter_value'])
            elif row['parameter_name'] == 'Start Year':
                reps.start_simulation_year = int(row['parameter_value'])
            elif row['parameter_name'] == 'End Year':
                reps.end_simulation_year = int(row['parameter_value'])
            elif row['parameter_name'] == 'Look Ahead':
                reps.lookAhead = int(row['parameter_value'])


        try:

            if self.run_investment_module:
                db_amirisdata = self.amirisdb.export_data()
                candidatePowerPlants = [a_tuple[0] for a_tuple in db_amirisdata["alternatives"]]
                add_parameter_value_to_repository_based_on_object_class_name_amiris(self,reps, db_amirisdata, candidatePowerPlants)
                for db_line in db_data['object_parameter_values']:
                    add_trends(reps, db_line)
                    add_parameter_value_to_repository_based_on_object_class_name(reps, db_line, candidatePowerPlants)

            else:
                candidatePowerPlants = []
                for db_line in db_data['object_parameter_values']:
                    add_trends(reps, db_line)
                    add_parameter_value_to_repository_based_on_object_class_name(reps, db_line, candidatePowerPlants)
        except StopIteration:
            logging.warning('No value found for class: ' + object_class_name +
                            ', object: ' + object_name +
                            ', parameter: ' + parameter_name)


        logging.info('SpineDBRW: End Read Repository')
        # logging.info('Repository: ' + str(reps))
        return reps

    def stage_cashflow_PowerPlant(self, current_tick: int):
        self.stage_init_alternative("0")
        self.stage_object(self.powerplant_dispatch_plan_classname, ppdp.name)
        self.stage_object_parameter_values(self.powerplant_dispatch_plan_classname, ppdp.name,
                                           [('Plant', ppdp.plant.name),
                                            ('Market', ppdp.bidding_market.name),
                                            ('Price', ppdp.price),
                                            ('Capacity', ppdp.amount),
                                            ('EnergyProducer', ppdp.bidder.name),
                                            ('AcceptedAmount', ppdp.accepted_amount),
                                            ('Status', ppdp.status)], current_tick)
        for row in self.db.query_object_parameter_values_by_object_class_and_object_name('Configuration',
                                                                                         "SimulationYears"):
            if row['parameter_name'] == 'Start Year':
                reps.start_simulation_year = int(row['parameter_value'])
            elif row['parameter_name'] == 'End Year':
                reps.end_simulation_year = int(row['parameter_value'])
            elif row['parameter_name'] == 'Look Ahead':
                reps.lookAhead = int(row['parameter_value'])



    """
    All functions from here are old
    """
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
                                      object_class_name: str, object_name: str, arr_of_tuples: list, current_tick: int):
        import_arr = [(object_class_name, object_name, i[0], i[1], str(current_tick)) for i in arr_of_tuples]
        self.db.import_object_parameter_values(import_arr)

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
                                      'Status'])

    def stage_init_alternative(self, current_tick: int):
        self.db.import_alternatives([str(current_tick)])

    def stage_init_(self, current_tick: int):
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

def add_trends(reps, db_line):
    object_class_name = db_line[0]
    if object_class_name == 'FuelPriceTrends':
        add_parameter_value_to_repository(reps, db_line, reps.trends, TriangularTrend)
    elif object_class_name == 'StepTrends':
        add_parameter_value_to_repository(reps, db_line, reps.trends, StepTrend)


def add_parameter_value_to_repository_based_on_object_class_name(reps, db_line, candidatePowerPlants):
    """
    Function used to translate an object_parameter_value from SpineDB to a Repository dict entry.

    :param candidatePowerPlants: candidate power plants dont need to be added if its not investment
    :param reps: Repository
    :param db_line: Line from exported data from spinedb_api
    """

    object_class_name = db_line[0]
    object_name = db_line[1]

    if object_class_name in ['ConventionalPlantOperator', 'VariableRenewableOperator']:
        if object_name not in candidatePowerPlants:
            add_parameter_value_to_repository(reps, db_line, reps.power_plants, PowerPlant)
        else:
            add_parameter_value_to_repository(reps, db_line, reps.candidatePowerPlants, CandidatePowerPlant)
# data from old emlab
    elif object_class_name == 'TechnologiesEmlab':
        add_parameter_value_to_repository(reps, db_line, reps.power_generating_technologies, PowerGeneratingTechnology)
# data from Traderes
    elif object_class_name == 'unit':
        add_parameter_value_to_repository(reps, db_line, reps.power_generating_technologies, PowerGeneratingTechnology)
    elif object_class_name == 'electricity':
        add_parameter_value_to_repository(reps, db_line, reps.power_generating_technologies, PowerGeneratingTechnology)
    # elif object_class_name == 'node':
    #     add_parameter_value_to_repository(reps, db_line, reps.substances, Substance)
    elif object_class_name == 'Fuels':
        add_parameter_value_to_repository(reps, db_line, reps.zones, Substance)
    elif object_class_name == 'CapacityMarkets':
        add_parameter_value_to_repository(reps, db_line, reps.capacity_markets, CapacityMarket)
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
    # elif object_class_name == 'PowerGeneratingTechnologyFuel':
    #     add_parameter_value_to_repository(reps, db_line, reps.power_plants_fuel_mix, SubstanceInFuelMix)
    # elif object_class_name == 'YearlyEmissions':
    #     add_parameter_value_to_repository(reps, db_line, reps.emissions, YearlyEmissions)



def add_parameter_value_to_repository_based_on_object_class_name_amiris(self, reps, db_amirisdata, candidatePowerPlants):
    for candidateplant in candidatePowerPlants:
        for db_line_amiris in db_amirisdata['object_parameter_values']:
            object_class_name = db_line_amiris[0]
            object_name = db_line_amiris[1]
            if object_class_name == self.ConventionalOperator_classname and object_name == candidateplant:
                add_parameter_value_to_repository(reps, db_line_amiris, reps.candidatePowerPlants, CandidatePowerPlant)
            if object_class_name == self.VariableRenewableOperator_classname and object_name == candidateplant:
                add_parameter_value_to_repository(reps, db_line_amiris, reps.candidatePowerPlants, CandidatePowerPlant)

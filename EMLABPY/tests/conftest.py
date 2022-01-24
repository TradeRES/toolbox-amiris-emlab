"""
This is the test configuration file.
Most important is the initialization (copy) of the SpineToolbox test SpineDB which is created through the
Spine Project in the /tests folder. This is copied and all operations are tested.

Jim Hommes - 26-4-2021
"""
from util.spinedb_reader_writer import *
from shutil import copyfile
import pytest
import os

dbcounter = 0
path_to_original_emlab_spinedb = '.spinetoolbox\\items\\db_emlab\\DB.sqlite'
path_to_current_emlab_spinedb = 'resources\\current_test_emlab_spineDB.sqlite'
path_to_original_config_spinedb = '.spinetoolbox/items/simulation_configuration_parameters/Simulation Configuration Parameters.sqlite'
path_to_current_config_spinedb = 'resources\\current_test_config_spineDB.sqlite'
path_to_original_competes_spinedb = '.spinetoolbox\\items\\db_competes\\DB COMPETES.sqlite'
path_to_current_competes_spinedb = 'resources\\current_test_competes_spineDB.sqlite'
path_to_original_empty_spinedb = '.spinetoolbox\\items\\empty\\Empty.sqlite'
path_to_current_empty_spinedb = 'resources\\current_empty.sqlite'

# Initialization: copy the DB created by Spine to the tests folder for testing
# This way testing always starts with a fresh database.
dirname = os.path.dirname(__file__)
copyfile(os.path.join(dirname, path_to_original_emlab_spinedb), os.path.join(dirname, path_to_current_emlab_spinedb))
copyfile(os.path.join(dirname, path_to_original_config_spinedb), os.path.join(dirname, path_to_current_config_spinedb))
copyfile(os.path.join(dirname, path_to_original_competes_spinedb), os.path.join(dirname, path_to_current_competes_spinedb))
copyfile(os.path.join(dirname, path_to_original_empty_spinedb), os.path.join(dirname, path_to_current_empty_spinedb))


@pytest.fixture(scope="class")
def dbrw():
    """
    This fixture passes the database itself as a parameter to the test.
    :return: DBRW
    """
    dbrw = SpineDBReaderWriter('sqlite:///' + path_to_current_emlab_spinedb,
                               'sqlite:///' + path_to_current_config_spinedb)
    yield dbrw
    dbrw.db.close_connection()
    dbrw.config_db.close_connection()


@pytest.fixture(scope="class")
def dbrw_fresh():
    dbrw = SpineDBReaderWriter('sqlite:///' + path_to_current_empty_spinedb,
                               'sqlite:///' + path_to_current_config_spinedb)
    yield dbrw
    dbrw.db.close_connection()
    dbrw.config_db.close_connection()


@pytest.fixture(scope="class")
def reps(dbrw):
    return dbrw.read_db_and_create_repository()


@pytest.fixture(scope="function")
def db_competes_powerplants():
    db_competes = SpineDB('sqlite:///' + path_to_current_competes_spinedb)
    yield db_competes.query_object_parameter_values_by_object_classes(
        ['Installed Capacity Abroad', 'Installed Capacity-RES Abroad', 'NL Installed Capacity (+heat)',
         'NL Installed Capacity-RES (+heat)', 'NL Installed Capacity Decentralized (+heat)'])
    db_competes.close_connection()


@pytest.fixture(scope="function")
def db_emlab_technologies():
    db_emlab = SpineDB('sqlite:///' + path_to_current_emlab_spinedb)
    yield db_emlab.query_object_parameter_values_by_object_class('PowerGeneratingTechnologies')
    db_emlab.close_connection()


@pytest.fixture(scope="function")
def db_competes_vre_capacities():
    db_competes = SpineDB('sqlite:///' + path_to_current_competes_spinedb)
    yield db_competes.query_object_parameter_values_by_object_class('VRE Capacities')
    db_competes.close_connection()


@pytest.fixture(scope="function")
def db_competes_vre_technologies():
    db_competes = SpineDB('sqlite:///' + path_to_current_competes_spinedb)
    yield db_competes.query_object_parameter_values_by_object_class('VRE Technologies')
    db_competes.close_connection()


@pytest.fixture(scope="function")
def db_competes_technologies():
    db_competes = SpineDB('sqlite:///' + path_to_current_competes_spinedb)
    yield db_competes.query_object_parameter_values_by_object_class('Technologies')
    db_competes.close_connection()


@pytest.fixture(scope="function")
def db_competes_new_technologies():
    db_competes = SpineDB('sqlite:///' + path_to_current_competes_spinedb)
    yield db_competes.query_object_parameter_values_by_object_class('New Technologies')
    db_competes.close_connection()


@pytest.fixture(scope="function")
def db_emlab_ppdps_and_powerplants():
    db_emlab = SpineDB('sqlite:///' + path_to_current_emlab_spinedb)
    yield db_emlab.query_object_parameter_values_by_object_class('PowerPlantDispatchPlans'), db_emlab.query_object_parameter_values_by_object_class('PowerPlants')
    db_emlab.close_connection()


@pytest.fixture(scope="function")
def db_emlab_mcps():
    db_emlab = SpineDB('sqlite:///' + path_to_current_emlab_spinedb)
    yield db_emlab.query_object_parameter_values_by_object_class('MarketClearingPoints')
    db_emlab.close_connection()


@pytest.fixture(scope="function")
def db_competes_init_and_vre_technologies():
    db_competes = SpineDB('sqlite:///' + path_to_current_competes_spinedb)
    yield db_competes.query_object_parameter_values_by_object_class_and_object_name('INIT VRE Technologies', 'SunPV'), \
          db_competes.query_object_parameter_values_by_object_class_and_object_name('VRE Technologies', 'SunPV')
    db_competes.close_connection()


@pytest.fixture(scope="function")
def db_competes_values_for_cm_non_vre():
    db_competes = SpineDB('sqlite:///' + path_to_current_competes_spinedb)
    db_overnight_cost_map = db_competes.query_object_parameter_values_by_object_class_and_object_name(
        'Overnight Cost (OC)', 'CCGT')
    db_initial_overnight_cost_map = db_competes.query_object_parameter_values_by_object_class_and_object_name(
        'INIT Overnight Cost (OC)', 'CCGT')
    db_technology_combi_map_list = db_competes.query_object_parameter_values_by_object_class_and_object_name(
        'Technologies', 'CCGT')
    db_initial_technology_combi_map = db_competes.query_object_parameter_values_by_object_class_and_object_name(
        'INIT Technologies', 'CCGT')
    yield db_overnight_cost_map, db_initial_overnight_cost_map, db_technology_combi_map_list, \
           db_initial_technology_combi_map
    db_competes.close_connection()


@pytest.fixture(scope="function")
def db_emlab_fuelmap_and_technologies():
    db_emlab = SpineDB('sqlite:///' + path_to_current_emlab_spinedb)
    yield db_emlab.query_object_parameter_values_by_object_class('FuelMap'), \
          db_emlab.query_object_parameter_values_by_object_class('PowerGeneratingTechnologies')
    db_emlab.close_connection()
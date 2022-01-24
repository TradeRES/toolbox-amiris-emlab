"""
This file tests all methods regarding the EMLAB Initialization Pre-processing script.
The more general methods (read Excel sheets, execute all functions) have consciously been skipped.

Jim Hommes 14-8-2021
"""

from conftest import *
from emlab_initialization_preprocessing import *


class TestEmlabInitPreProcessing:

    def test_replace_power_generating_technology_fuel_names(self, mocker, db_emlab_fuelmap_and_technologies):
        db_emlab = mocker.Mock(SpineDB)
        db_emlab_fuelmap, db_emlab_technologies = db_emlab_fuelmap_and_technologies
        replace_power_generating_technology_fuel_names(db_emlab, db_emlab_fuelmap, db_emlab_technologies)

        db_emlab.import_object_parameter_values.assert_has_calls([mocker.call([('PowerGeneratingTechnologyFuel', '1', 'FUELNEW', 'Biomass', '0')]),
                                                                  mocker.call([('PowerGeneratingTechnologyFuel', '6', 'FUELNEW', 'Derived Gas', '0')])], any_order=True)

    def test_import_initial_vre(self, mocker, db_competes_vre_capacities):
        db_emlab = mocker.Mock(SpineDB)
        import_initial_vre(db_emlab, db_competes_vre_capacities, 2020)

        db_emlab.import_object_parameter_values.assert_has_calls([mocker.call([('PowerPlants', 'SunPV', 'MWNL', 10213.0, '0')]),
                                                                  mocker.call([('PowerPlants', 'WindOff', 'MWNL', 2500.0, '0')]),
                                                                  mocker.call([('PowerPlants', 'WindOn', 'MWNL', 4100.0, '0')])])

    def test_import_initial_vre_fixed_oc_start_values(self, mocker, db_competes_vre_technologies, db_emlab_technologies):
        db_emlab = mocker.Mock(SpineDB)

        import_initial_vre_fixed_oc_start_values(db_emlab, db_competes_vre_technologies, db_emlab_technologies, 2020)

        db_emlab.import_object_parameter_values.assert_has_calls([mocker.call([('GeometricTrends', 'sunPVFixedOperatingCostTimeSeries', 'start', 13000.0, '0')]),
                                                                 mocker.call([('GeometricTrends', 'windOFFSHOREFixedOperatingCostTimeSeries', 'start', 85000.0, '0')]),
                                                                 mocker.call([('GeometricTrends', 'windONSHOREFixedOperatingCostTimeSeries', 'start', 40000.0, '0')])])

    def test_import_initial_fixed_oc_start_values(self, mocker, db_competes_technologies, db_emlab_technologies):
        db_emlab = mocker.Mock(SpineDB)
        import_initial_fixed_oc_start_values(db_emlab, db_competes_technologies, db_emlab_technologies)

        db_emlab.import_object_parameter_values.assert_has_calls([mocker.call([('GeometricTrends', 'biomassSTANDALONEFixedOperatingCostTimeSeries', 'start', 69542.57972036711, '0')]),
                                                                  mocker.call([('GeometricTrends', 'gasCHPFixedOperatingCostTimeSeries', 'start', 10473.234339905166, '0')])],
                                                                 any_order=True)




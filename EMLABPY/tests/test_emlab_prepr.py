"""
This file tests all methods regarding the EMLAB Pre-processing script.
The more general methods (read Excel sheets, execute all functions) have consciously been skipped.

Jim Hommes 14-8-2021
"""

from conftest import *
from emlab_preprocessing import *


class TestEmlabPreProcessing:

    def test_set_correct_power_plant_statuses(self, mocker, db_emlab_ppdps_and_powerplants):
        _, db_emlab_powerplants = db_emlab_ppdps_and_powerplants
        db_emlab = mocker.Mock(SpineDB)
        set_correct_power_plant_statuses(db_emlab, db_emlab_powerplants, 2020)

        args_mw, kwargs_mw = db_emlab.import_object_parameter_values.call_args_list[0]
        args_statuses, kwargs_statuses = db_emlab.import_object_parameter_values.call_args_list[1]

        biomass_mw = next(i[3] for i in args_mw[0] if i[1] == 'NED BIOMASS Standalone SUM')
        assert biomass_mw == 15

        plant1 = next(i[3] for i in args_statuses[0] if i[1] == 'PLANT1')
        assert plant1 == 'OPR'
        plant3 = next(i[3] for i in args_statuses[0] if i[1] == 'PLANT3')
        assert plant3 == 'DECOM'

    def test_get_power_plants_by_string_in_object_name(self, db_emlab_ppdps_and_powerplants):
        _, db_emlab_powerplants = db_emlab_ppdps_and_powerplants
        assert get_power_plants_by_string_in_object_name('BIOMASS', db_emlab_powerplants) == {'NED BIOMASS Standalone': 2005.0, 'NED BIOMASS Standalone(D)': 2005.0, 'NED BIOMASS Standalone SUM': 2005.0}

"""
This file tests all methods regarding the EMLAB to COMPETES translation script.
The more general methods (read Excel sheets, execute all functions) have consciously been skipped.

Jim Hommes 14-8-2021
"""

from conftest import *
from emlab_to_competes import *


class TestEmlabToCompetes:

    def test_export_capacity_market_revenues_for_technology_vre_only_fixedom(self, mocker, db_competes_init_and_vre_technologies):
        db_competes = mocker.MagicMock(SpineDB)
        db_competes.query_object_parameter_values_by_object_class_and_object_name = mocker.MagicMock()
        db_competes.query_object_parameter_values_by_object_class_and_object_name.side_effect = \
            [db_competes_init_and_vre_technologies[0], db_competes_init_and_vre_technologies[1]]

        old_value = db_competes_init_and_vre_technologies[1][0]['parameter_value'].get_value('2021')\
            .get_value('Fixed O&M(Euro/kW/yr)')

        export_capacity_market_revenues_for_technology_vre(db_competes, 'SunPV', 2021, 10, 7)

        args, kwargs = db_competes.import_object_parameter_values.call_args
        new_value = args[0][0][3].get_value('2021').get_value('Fixed O&M(Euro/kW/yr)')
        assert new_value == old_value - 10

    def test_export_capacity_market_revenues_for_technology_vre_fixedom_capex(self, mocker, db_competes_init_and_vre_technologies):
        db_competes = mocker.MagicMock(SpineDB)
        db_competes.query_object_parameter_values_by_object_class_and_object_name = mocker.MagicMock()
        db_competes.query_object_parameter_values_by_object_class_and_object_name.side_effect = \
            [db_competes_init_and_vre_technologies[0], db_competes_init_and_vre_technologies[1]]

        old_fixed_om = db_competes_init_and_vre_technologies[1][0]['parameter_value'].get_value('2021') \
            .get_value('Fixed O&M(Euro/kW/yr)')
        old_capex = db_competes_init_and_vre_technologies[1][0]['parameter_value'].get_value('2028') \
            .get_value('Capex(Euro/kW)')

        export_capacity_market_revenues_for_technology_vre(db_competes, 'SunPV', 2021, 20, 7)

        args, kwargs = db_competes.import_object_parameter_values.call_args
        new_fixed_om = args[0][0][3].get_value('2021').get_value('Fixed O&M(Euro/kW/yr)')
        new_capex = args[0][0][3].get_value('2028').get_value('Capex(Euro/kW)')

        assert new_fixed_om == 0
        assert new_capex == (old_capex + old_fixed_om - 20)

    def test_export_capacity_market_revenues_for_technology_nonvre_only_fixedom(self, mocker, db_competes_values_for_cm_non_vre):
        db_competes = mocker.MagicMock(SpineDB)
        db_technology_combi_map_list = db_competes_values_for_cm_non_vre[2]
        db_competes.query_object_parameter_values_by_object_class_and_object_name = mocker.MagicMock()
        db_competes.query_object_parameter_values_by_object_class_and_object_name.side_effect = \
            [db_competes_values_for_cm_non_vre[0], db_competes_values_for_cm_non_vre[1], db_competes_values_for_cm_non_vre[3]]

        old_fixed_om = db_technology_combi_map_list[0]['parameter_value'].get_value('7').get_value('FIXED O&M')

        export_capacity_market_revenues_for_technology_nonvre(db_competes, 'CCGT',
                                                              db_technology_combi_map_list, 'GAS',
                                                              5, 2021, 7)
        args, kwargs = db_competes.import_object_parameter_values.call_args
        new_fixed_om = args[0][0][3].get_value('7').get_value('FIXED O&M')

        assert new_fixed_om == old_fixed_om - 5

    def test_export_capacity_market_revenues_for_technology_nonvre_fixedom_capex(self, mocker, db_competes_values_for_cm_non_vre):
        db_competes = mocker.MagicMock(SpineDB)
        db_technology_combi_map_list = db_competes_values_for_cm_non_vre[2]
        db_competes.query_object_parameter_values_by_object_class_and_object_name = mocker.MagicMock()
        db_competes.query_object_parameter_values_by_object_class_and_object_name.side_effect = \
            [db_competes_values_for_cm_non_vre[0], db_competes_values_for_cm_non_vre[1], db_competes_values_for_cm_non_vre[3]]

        old_fixed_om = db_technology_combi_map_list[0]['parameter_value'].get_value('7').get_value('FIXED O&M')
        old_capex = db_competes_values_for_cm_non_vre[0][0]['parameter_value'].get_value('GAS').get_value('2028')

        export_capacity_market_revenues_for_technology_nonvre(db_competes, 'CCGT',
                                                              db_technology_combi_map_list, 'GAS',
                                                              20, 2021, 7)
        args, kwargs = db_competes.import_object_parameter_values.call_args
        new_fixed_om = args[0][0][3].get_value('7').get_value('FIXED O&M')
        new_capex = args[0][1][3].get_value('GAS').get_value('2028')

        assert new_fixed_om == 0
        assert new_capex == old_capex + old_fixed_om - 20

    def test_get_cm_market_clearing_price(self, db_emlab_mcps):
        assert get_cm_market_clearing_price(50, db_emlab_mcps) == 10 / 1000
        assert get_cm_market_clearing_price(51, db_emlab_mcps) == 50 / 1000

    def test_get_participating_technologies_in_capacity_market(self, db_emlab_ppdps_and_powerplants, ):
        db_emlab_powerplantdispatchplans, db_emlab_powerplants = db_emlab_ppdps_and_powerplants
        assert get_participating_technologies_in_capacity_market(db_emlab_powerplantdispatchplans, 50,
                                                          1, db_emlab_powerplants) == {('GT', 'GAS')}

    def test_get_co2_market_clearing_price(self, db_emlab_mcps):
        assert get_co2_market_clearing_price(db_emlab_mcps, 75) == 100

    def test_export_co2_market_clearing_price(self, mocker, db_emlab_mcps):
        db_competes = mocker.Mock(SpineDB)
        months = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        export_co2_market_clearing_price(db_competes, db_emlab_mcps, 75, 'EU_ETS_CO2price', 2020, months, 7)

        db_competes.import_object_parameter_values.assert_called_with([('EU_ETS_CO2price', '2020', i, 100, '0') for i in months] +
                                                                      [('EU_ETS_CO2price', '2027', i, 100 * pow(1.025, 7), '0') for i in months])

    def test_initialize_co2_spine_structure(self, mocker):
        db_competes = mocker.Mock(SpineDB)
        months = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        initialize_co2_spine_structure(db_competes, 2020, 'EU_ETS_CO2price', months, 7)

        db_competes.import_object_classes.assert_called_with(['EU_ETS_CO2price'])
        db_competes.import_objects.assert_called_with([('EU_ETS_CO2price', str(2020)), ('EU_ETS_CO2price', str(2020 + 7))])
        db_competes.import_data.assert_called_with({'object_parameters': [['EU_ETS_CO2price', i] for i in months]})

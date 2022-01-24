"""
This file tests all methods regarding the COMPETES to EMLAB translation script.
The more general methods (read Excel sheets, execute all functions) have consciously been skipped.

Jim Hommes 14-8-2021
"""

from conftest import *
from competes_to_emlab import *
import pandas

path_and_filename_competes_dummy_output = 'resources/Output_Dynamic_Gen&Trans_tests.xlsx'


class TestCompetesToEmlab:

    def test_export_yearly_emissions_to_emlab(self, mocker):
        db_emlab_mock = mocker.Mock(SpineDB)
        names = ['PLANT1', 'PLANT2', 'PLANT3', 'PLANT4', 'PLANT5', 'PLANT6', 'PLANT7']
        values = [1000, 1100, 1200, 1300, 1400, 1500, 1600]

        # Execute
        export_yearly_emissions_to_emlab(db_emlab_mock, pandas.read_excel(
            path_and_filename_competes_dummy_output, 'Unit Emissions', skiprows=3, header=None), 0)

        # Assert
        db_emlab_mock.import_object_classes.assert_called_with(['YearlyEmissions'])
        db_emlab_mock.import_objects.assert_called_with([('YearlyEmissions', 'YearlyEmissions')])
        db_emlab_mock.import_data.assert_called_with({'object_parameters': [['YearlyEmissions', i] for i in names]})
        db_emlab_mock.import_object_parameter_values.assert_called_with([('YearlyEmissions', 'YearlyEmissions', names[i], values[i], '0') for i in range(len(values))])

    def test_export_decommissioning_decisions_to_emlab_and_competes(self, mocker, db_competes_powerplants):
        decommissioning_df = crop_dataframe_until_first_empty_row(
            pandas.read_excel(path_and_filename_competes_dummy_output, 'Decommissioning', skiprows=2, usecols='A:C'))

        db_competes_mock = mocker.Mock(SpineDB)
        db_emlab_mock = mocker.Mock(SpineDB)

        # Execute
        export_decommissioning_decisions_to_emlab_and_competes(db_competes_mock, db_emlab_mock, db_competes_powerplants,
                                                               decommissioning_df, 2020, 0, 7)

        # Assert
        db_competes_mock.import_object_parameter_values.assert_has_calls([mocker.call([('Installed Capacity Abroad', 'AUS GAS CCGT 2020(D)', 'ON-STREAMEU', 2027, '0')]),
                                                                          mocker.call([('NL Installed Capacity (+heat)', 'PLANT1(D)', 'ON-STREAMNL', 2027, '0')])], any_order=True)
        db_emlab_mock.import_object_parameter_values.assert_called_with([('PowerPlants', 'PLANT1(D)', 'ON-STREAMNL', 2027, '0')])

    def test_export_vre_investment_decisions(self, mocker, db_emlab_technologies, db_competes_vre_capacities):
        db_emlab_mock = mocker.Mock(SpineDB)
        db_competes_mock = mocker.Mock(SpineDB)

        vre_investment_df = crop_dataframe_until_first_empty_row(pandas.read_excel(
            path_and_filename_competes_dummy_output, 'VRE investment', skiprows=2, usecols='A:G'))

        vre_cap_map = next(i['parameter_value'] for i in db_competes_vre_capacities if i['object_name'] == 'WindOn')
        old_value = vre_cap_map.get_value('2024').get_value('ITA').get_value('Initial Capacity(MW)')

        export_vre_investment_decisions(db_emlab_mock, db_competes_mock, 0, 2020, vre_investment_df,
                                        db_emlab_technologies, db_competes_vre_capacities, 1)

        args, kwargs = db_competes_mock.import_object_parameter_values.call_args
        new_value = args[0][0][3].get_value('2024').get_value('ITA').get_value('Initial Capacity(MW)')

        assert new_value == old_value + 100

        db_competes_mock.import_object_parameter_values.assert_called_once()
        db_emlab_mock.import_object_parameter_values.assert_has_calls(
            [mocker.call([('PowerPlants', 'SunPV', 'MWNL', 12291.7, '1')]),
             mocker.call([('PowerPlants', 'WindOff', 'MWNL', 3750.0, '1')]),
             mocker.call([('PowerPlants', 'WindOn', 'MWNL', 4590.0, '1')])], any_order=True)

    def test_get_year_online_by_technology(self, db_emlab_technologies):
        assert get_year_online_by_technology(db_emlab_technologies, 'GAS', 'CHP', 2020) == 2020 + 3
        assert get_year_online_by_technology(db_emlab_technologies, 'NUCLEAR', '-', 2020) == 2020 + 7

    def test_get_plant_efficiency_and_availability_by_fuel_and_tech(self, mocker, db_competes_new_technologies):
        eff, avai = get_plant_efficiency_and_availability_by_fuel_and_tech(db_competes_new_technologies, '-', 2020,
                                                                           'DEN', 'NUCLEAR')
        assert eff == 0.35
        assert avai == 0.8

    def test_export_investment_decisions_to_emlab_and_competes(self, mocker, db_emlab_technologies,
                                                               db_competes_new_technologies):
        db_emlab = mocker.Mock(SpineDB)
        db_competes = mocker.Mock(SpineDB)

        new_generation_capacity_df = crop_dataframe_until_first_empty_row(pandas.read_excel(path_and_filename_competes_dummy_output,
                                                                                            'New Generation Capacity', skiprows=2, usecols='A:D,G:X'))

        export_investment_decisions_to_emlab_and_competes(db_emlab, db_competes, 0,
                                                          new_generation_capacity_df, 2020,
                                                          db_emlab_technologies, db_competes_new_technologies)

        values = [('STATUSNL', 'DECOM'), ('MWNL', 2000), ('ON-STREAMNL', 2023), ('COUNTRYNL', 'The Netherlands'), ('ABBREVNL', 'NL'), ('BUSNL', 'NED'), ('ONEBUSNL', 'NED'), ('GENERATORNL', 'NL GAS'), ('FirmNL', 'NL GAS'), ('FUELNL', 'GAS'), ('TECHTYPENL', 'CCGT'), ('No Load GJ', 984.0), ('CfactorNL', 0), ('MaxCofiring', 0), ('CofiringNL', 0), ('EfficiencyNL', 0.61), ('AvailabilityNL', 0.9)]
        values_decom = values.copy()
        values_decom[1] = ('MWNL', -2000)
        values_decom[2] = ('ON-STREAMNL', 2063)

        db_emlab.import_object_parameter_values.assert_called_with([('PowerPlants', 'NED GAS CCGTinvtick2020', i[0], i[1], '0') for i in values] +
                                                                   [('PowerPlants', 'NED GAS CCGTinvtick2020(D)', i[0], i[1], '0') for i in values_decom])
        values[0] = ('STATUSNL', 'OPR')
        db_competes.import_object_parameter_values.assert_called_with([('NL Installed Capacity (+heat)', 'NED GAS CCGTinvtick2020', i[0], i[1], '0') for i in values] +
                                                                      [('NL Installed Capacity (+heat)', 'NED GAS CCGTinvtick2020(D)', i[0], i[1], '0') for i in values_decom])

    def test_export_power_plant_dispatch_plans_to_emlab(self, mocker, db_emlab_ppdps_and_powerplants):
        db_emlab = mocker.Mock(SpineDB)
        db_emlab_ppdps, db_emlab_powerplants = db_emlab_ppdps_and_powerplants

        hourly_nl_balance_df = pandas.read_excel(path_and_filename_competes_dummy_output,
                                                 'Hourly NL Balance', skiprows=1)
        hourly_nl_balance_df = hourly_nl_balance_df.rename(columns={'Sun': 'SunPV', 'Wind Onshore': 'WindOn',
                                                                    'Wind Offshore': 'WindOff'})
        unit_generation_df = pandas.read_excel(path_and_filename_competes_dummy_output,
                                               'NL Unit Generation', index_col=0, skiprows=1)
        unit_generation_df = unit_generation_df.transpose().join(
            hourly_nl_balance_df[['SunPV', 'WindOn', 'WindOff']]).replace(np.nan, 0)
        hourly_nodal_prices_df = pandas.read_excel(path_and_filename_competes_dummy_output,
                                                   'Hourly Nodal Prices')
        hourly_nodal_prices_nl = get_hourly_nodal_prices(hourly_nodal_prices_df)

        export_power_plant_dispatch_plans_to_emlab(db_emlab, 0, unit_generation_df, db_emlab_ppdps,
                                                   hourly_nodal_prices_nl, db_emlab_powerplants)

        values_gen = [('AcceptedAmount', 17770.320000002506), ('Capacity', 17770.320000002506), ('EnergyProducer', 'FIRM1'), ('Market', 'DutchElectricitySpotMarket'), ('Plant', 'PLANT1'), ('Status', 'Accepted'), ('Price', 77.15761443795816)]
        values_vre1 = [('AcceptedAmount', 10892746.641000018), ('Capacity', 10892746.641000018,), ('EnergyProducer', 'NL PV'), ('Market', 'DutchElectricitySpotMarket'), ('Plant', 'SunPV'), ('Status', 'Accepted'), ('Price', 32.0359153935317)]
        values_vre2 = [('AcceptedAmount', 9342260.00000002), ('Capacity', 9342260.00000002), ('EnergyProducer', 'NL WIND ONSHORE'), ('Market', 'DutchElectricitySpotMarket'), ('Plant', 'WindOn'), ('Status', 'Accepted'), ('Price', 39.17638399868239)]
        values_vre3 = [('AcceptedAmount', 7595888.828257466), ('Capacity', 7595888.828257466), ('EnergyProducer', 'NL WIND OFFSHORE'), ('Market', 'DutchElectricitySpotMarket'), ('Plant', 'WindOff'), ('Status', 'Accepted'), ('Price', 39.60378723210704)]
        db_emlab.import_object_parameter_values.assert_called_with([('PowerPlantDispatchPlans', mocker.ANY, i[0], i[1], '0') for i in values_gen + values_vre1 + values_vre2 + values_vre3])

    def test_get_hourly_nodal_prices(self):
        hourly_nodal_prices_df = pandas.read_excel(path_and_filename_competes_dummy_output,
                                                   'Hourly Nodal Prices')
        assert sum(get_hourly_nodal_prices(hourly_nodal_prices_df)) == 567101.536623265

    def test_export_market_clearing_points_to_emlab(self, mocker, db_emlab_mcps):
        db_emlab = mocker.Mock(SpineDB)
        hourly_nodal_prices_df = pandas.read_excel(path_and_filename_competes_dummy_output,
                                                   'Hourly Nodal Prices')
        hourly_nodal_prices_nl = get_hourly_nodal_prices(hourly_nodal_prices_df)

        export_market_clearing_points_to_emlab(db_emlab, 0, hourly_nodal_prices_nl, db_emlab_mcps)
        db_emlab.import_object_parameter_values.assert_called_with([('MarketClearingPoints', mocker.ANY, 'Market', 'DutchElectricitySpotMarket', '0'),
                                                                    ('MarketClearingPoints', mocker.ANY, 'Price', 64.73761833598915, '0')])

    def test_export_total_sum_exports_to_emlab(self, mocker):
        db_emlab = mocker.Mock(SpineDB)
        hourly_nl_balance_df = pandas.read_excel(path_and_filename_competes_dummy_output,
                                                 'Hourly NL Balance', skiprows=1)
        hourly_nl_balance_df = hourly_nl_balance_df.rename(columns={'Sun': 'SunPV', 'Wind Onshore': 'WindOn',
                                                                    'Wind Offshore': 'WindOff'})

        export_total_sum_exports_to_emlab(db_emlab, hourly_nl_balance_df, 0)

        db_emlab.import_object_parameter_values.assert_called_with([('Exports', 'Exports', 'Exports', 16003023.181560552, '0')])


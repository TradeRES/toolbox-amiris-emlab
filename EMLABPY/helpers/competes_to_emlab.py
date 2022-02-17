"""
This script handles all communication passed from the COMPETES Excel output to the EM-Lab SpineDB.
It handles the MarketClearingPoint from the Hourly Nodal Prices and the unit generation as PowerPlantDispatchPlans.
It also implements the investment and decommissioning decisions into EMLAB and COMPETES.

Arg1: URL of EMLAB SpineDB
Arg2: URL of COMPETES SpineDB
Arg3: Relative path to COMPETES Results folder
Arg4: Filename of COMPETES output Gen&Trans with a "?" as placeholder for the year
Arg5: Filename of COMPETES output UC with a "?" as placeholder for the year

Jim Hommes - 10-6-2021
"""
import sys
import pandas
import numpy as np
from datetime import datetime
from spinedb import SpineDB
from helper_functions import get_current_ticks


def query_databases(db_emlab, db_competes):
    """
    This function queries the databases and retrieves all necessary data.

    :param db_emlab: SpineDB Object of EM-Lab
    :param db_competes: SpineDB Object of COMPETES
    :return: the queried data
    """
    print('Querying databases...')
    db_emlab_powerplants = db_emlab.query_object_parameter_values_by_object_class('PowerPlants')
    db_emlab_ppdps = db_emlab.query_object_parameter_values_by_object_class('PowerPlantDispatchPlans')
    db_competes_powerplants = db_competes.query_object_parameter_values_by_object_classes(
        ['Installed Capacity Abroad', 'Installed Capacity-RES Abroad', 'NL Installed Capacity (+heat)',
         'NL Installed Capacity-RES (+heat)', 'NL Installed Capacity Decentralized (+heat)'])
    db_emlab_mcps = db_emlab.query_object_parameter_values_by_object_class('MarketClearingPoints')
    db_competes_vre_capacities = db_competes.query_object_parameter_values_by_object_class('VRE Capacities')
    db_emlab_technologies = db_emlab.query_object_parameter_values_by_object_class('PowerGeneratingTechnologies')
    db_competes_new_technologies = db_competes.query_object_parameter_values_by_object_class('New Technologies')
    print('Done')
    return db_emlab_powerplants, db_emlab_ppdps, db_competes_powerplants, db_emlab_mcps, db_competes_vre_capacities, \
           db_emlab_technologies, db_competes_new_technologies


def read_excel_sheets(path_to_competes_results, file_name_gentransinv, file_name_gentransdisp):
    """
    This function reads all Excel sheets output by COMPETES. This is done with pandas.

    :param path_to_competes_results: URL
    :param file_name_gentransinv: Filename of the Investment output
    :param file_name_uc: Filename of the Unit Commitment output
    :return: The pandas dataframes of the read Excel sheets
    """
    # Unit Commitment
    hourly_nodal_prices_df = pandas.read_excel(path_to_competes_results + '/' + file_name_gentransdisp,
                                               'Hourly Nodal Prices')
    unit_generation_df = pandas.read_excel(path_to_competes_results + '/' + file_name_gentransdisp,
                                           'NL Unit Generation', index_col=0, skiprows=1)
    hourly_nl_balance_df = pandas.read_excel(path_to_competes_results + '/' + file_name_gentransdisp,
                                             'Hourly NL Balance', skiprows=1)
    yearly_emissions_df = pandas.read_excel(path_to_competes_results + '/' + file_name_gentransdisp,
                                            'Unit Emissions', skiprows=3, header=None)

    # Investment and Decom decisions
    new_generation_capacity_df = pandas.read_excel(path_to_competes_results + '/' + file_name_gentransinv,
                                                   'New Generation Capacity', skiprows=2, usecols='A:D,G:X')
    decommissioning_df = pandas.read_excel(path_to_competes_results + '/' + file_name_gentransinv, 'Decommissioning',
                                           skiprows=2, usecols='A:C')
    vre_investment_df = pandas.read_excel(path_to_competes_results + '/' + file_name_gentransinv, 'VRE investment',
                                          skiprows=2, usecols='A:G')

    return hourly_nodal_prices_df, unit_generation_df, new_generation_capacity_df, decommissioning_df, \
           vre_investment_df, hourly_nl_balance_df, yearly_emissions_df


def export_yearly_emissions_to_emlab(db_emlab, yearly_emissions_df, current_emlab_tick):
    print('Exporting YearlyEmissions object...')
    db_emlab.import_object_classes(['YearlyEmissions'])
    db_emlab.import_objects([('YearlyEmissions', 'YearlyEmissions')])
    param_names = []
    param_values = []
    for index, row in yearly_emissions_df.iterrows():
        param_names.append(['YearlyEmissions', row[0]])
        param_values.append(('YearlyEmissions', 'YearlyEmissions', row[0], row[2], str(current_emlab_tick)))

    db_emlab.import_data({'object_parameters': param_names})
    db_emlab.import_object_parameter_values(param_values)
    print('Done exporting YearlyEmissions')


def export_decommissioning_decisions_to_emlab_and_competes(db_competes, db_emlab, db_competes_powerplants,
                                                           decommissioning_df, current_competes_tick,
                                                           current_emlab_tick, look_ahead):
    """
    This function exports all decommissioning decisions to EMLab and COMPETES.
    This means that the duplicate objects (the ones with (D) in the title) will be changed in their year, or
    ON-STREAMNL. This will be set to the current year.
    The preprocessing EMLab block will make implement the STATUSNL afterwards.

    :param db_competes: SpineDB
    :param db_emlab: SpineDB
    :param db_competes_powerplants: The queried results of the COMPETES powerplants
    :param decommissioning_df: The Decommissioning values from the COMPETES output
    :param current_competes_tick: int
    :param current_emlab_tick: int
    """
    print('Exporting Decommissioning to EMLAB and COMPETES...')
    for index, row in decommissioning_df.iterrows():
        try:
            power_plant_name_decom_version_row = next(
                i for i in db_competes_powerplants if row['unit'] in i['object_name'] and '(D)' in i['object_name'])
            power_plant_name_decom_version = power_plant_name_decom_version_row['object_name']
            onstream_title = 'ON-STREAMNL' if row['node'] == 'NED' else 'ON-STREAMEU'
            db_competes.import_object_parameter_values([(power_plant_name_decom_version_row['object_class_name'],
                                                         power_plant_name_decom_version, onstream_title,
                                                         current_competes_tick + look_ahead, '0')])
            if row['node'] == 'NED':
                # If node is NED, export to EMLAB
                db_emlab.import_object_parameter_values([('PowerPlants', power_plant_name_decom_version, 'ON-STREAMNL',
                                                          current_competes_tick + look_ahead, str(current_emlab_tick))])
        except StopIteration:
            print('No DECOM version found for plant ' + row['unit'])
    print('Done')


def export_vre_investment_decisions(db_emlab, db_competes, current_emlab_tick, current_competes_tick, vre_investment_df,
                                    db_emlab_technologies, db_competes_vre_capacities, step):
    """
    This function exports all VRE Investment decisions.
    Column titles are not printed if they are empty. 'New' is the column title if an investment has been made. If not,
    'Initial' is transported.
    NED investments are fixed, so for EM-Lab the next 'Initial' is taken from COMPETES SpineDB

    :param db_emlab: SpineDB
    :param current_emlab_tick: int
    :param vre_investment_df: Dataframe of VRE Investment decisions from COMPETES output
    :param db_emlab_powerplants: Queried Powerplants from EMLab
    """
    print('Exporting VRE Investment Decisions to EMLAB and COMPETES...')
    for index, vre_row in vre_investment_df.iterrows():
        if 'New' in vre_row.index and not pandas.isnull(vre_row['New']):
            expected_permit_time = next(int(i['parameter_value']) for i in db_emlab_technologies if i['object_name'] ==
                                        vre_row['WindOn'] and i['parameter_name'] == 'expectedPermittime')
            expected_lead_time = next(int(i['parameter_value']) for i in db_emlab_technologies if i['object_name'] ==
                                      vre_row['WindOn'] and i['parameter_name'] == 'expectedLeadtime')
            build_time = expected_permit_time + expected_lead_time

            # There has only been an investment if there is a column New
            vre_capacity_per_year = next(
                i['parameter_value'] for i in db_competes_vre_capacities if i['object_name'] == vre_row['WindOn'])
            vre_capacity_per_bus = vre_capacity_per_year.get_value(str(current_competes_tick + build_time))
            vre_capacity = vre_capacity_per_bus.get_value(vre_row['Bus'])
            old_mw = vre_capacity.get_value('Initial Capacity(MW)')
            vre_capacity.set_value('Initial Capacity(MW)', old_mw + vre_row['New'])
            vre_capacity_per_bus.set_value(vre_row['Bus'], vre_capacity)
            vre_capacity_per_year.set_value(str(current_competes_tick + build_time), vre_capacity_per_bus)
            db_competes.import_object_parameter_values(
                [('VRE Capacities', vre_row['WindOn'], 'VRE Capacities', vre_capacity_per_year, '0')])

        if 'Bus' in vre_row.index and vre_row['Bus'] == 'NED':  # Retrieve Initial from SpineDB COMPETES
            vre_capacity_per_year = next(
                i['parameter_value'] for i in db_competes_vre_capacities if i['object_name'] == vre_row['WindOn'])
            new_mw = vre_capacity_per_year.get_value(str(current_competes_tick + step)).get_value(vre_row['Bus']) \
                .get_value('Initial Capacity(MW)')
            db_emlab.import_object_parameter_values(
                [('PowerPlants', vre_row['WindOn'], 'MWNL', new_mw, str(current_emlab_tick + step))])

    print('Done Exporting VRE Investment Decisions to EMLAB and COMPETES')


def get_year_online_by_technology(db_emlab_technologies, fuel, techtype, current_competes_tick):
    technologies_by_fuel = [i['object_name'] for i in db_emlab_technologies if i['parameter_name'] == 'FUELNEW' and i['parameter_value'] == fuel]
    technologies_by_techtype = [i['object_name'] for i in db_emlab_technologies if i['parameter_name'] == 'FUELTYPENEW' and i['parameter_value'] == techtype]
    technology = next(name for name in technologies_by_fuel if name in technologies_by_techtype)
    expected_permit_time = next(int(i['parameter_value']) for i in db_emlab_technologies if i['object_name'] == technology and i['parameter_name'] == 'expectedPermittime')
    expected_lead_time = next(int(i['parameter_value']) for i in db_emlab_technologies if i['object_name'] == technology and i['parameter_name'] == 'expectedLeadtime')
    build_time = expected_permit_time + expected_lead_time
    return current_competes_tick + build_time


def get_plant_efficiency_and_availability_by_fuel_and_tech(db_competes_new_technologies, tech, year, bus, fuel):
    res_map = next(i['parameter_value'] for i in db_competes_new_technologies if i['object_name'] == tech)
    res_map_per_parameter = res_map.get_value(str(year)).get_value(bus).get_value(fuel)
    return res_map_per_parameter.get_value('Efficiencynew'), res_map_per_parameter.get_value('Availibilitynew')


def export_investment_decisions_to_emlab_and_competes(db_emlab, db_competes, current_emlab_tick,
                                                      new_generation_capacity_df, current_competes_tick,
                                                      db_emlab_technologies, db_competes_new_technologies):
    """
    This function exports all Investment decisions.

    :param db_emlab: SpineDB
    :param db_competes: SpineDB
    :param new_generation_capacity_df: Dataframe of new generation capacity from COMPETES output
    """
    print('Exporting Investment Decisions to EMLAB and COMPETES...')
    for index, row in new_generation_capacity_df.iterrows():
        row = row.fillna(0)
        online_in_year = get_year_online_by_technology(db_emlab_technologies, row['FUELEU'], row['TECHTYPEU'],
                                                       current_competes_tick)

        plant_name = row['UNITEU'] + 'invtick' + str(current_competes_tick)
        plant_name_decom = plant_name + '(D)'
        plant_efficiency, plant_availability = get_plant_efficiency_and_availability_by_fuel_and_tech(
            db_competes_new_technologies, row['TECHTYPEU'], online_in_year, row['BUSEU'], row['FUELEU'])

        if row['Node'] == 'NED':
            print('Node == NED')
            print('Preparing parameters...')
            param_values = [(col.replace("TECHTYPEU", "TECHTYPENL").replace("EU", "NL"), value)
                            for (col, value) in row[4:].items() if not (col == 'STATUSEU'
                                                                        or col == 'MWEU'
                                                                        or col == 'UNITEU'
                                                                        or col == 'ON-STREAMEU'
                                                                        or col == 'EfficiencyEU'
                                                                        or col == 'AvailabilityEU')]
            param_values += [('EfficiencyNL', plant_efficiency),
                             ('AvailabilityNL', plant_availability)]
            param_values_competes = [('STATUSNL', 'OPR'), ('MWNL', row['MWEU']), ('ON-STREAMNL', online_in_year)] + param_values
            param_values_competes_decom = [('STATUSNL', 'DECOM'), ('MWNL', -1 * row['MWEU']), ('ON-STREAMNL', online_in_year + 40)] + param_values
            param_values_emlab = [('STATUSNL', 'DECOM'), ('MWNL', row['MWEU']), ('ON-STREAMNL', online_in_year)] + param_values
            param_values_emlab_decom = [('STATUSNL', 'DECOM'), ('MWNL', -1 * row['MWEU']), ('ON-STREAMNL', online_in_year + 40)] + param_values
            # Always DECOM so CM does not take into account. Will be set to OPR in preprocessing

            competes_table_name = 'NL Installed Capacity (+heat)'

            print('Exporting to EM-Lab...')
            db_emlab.import_objects([('PowerPlants', plant_name), ('PowerPlants', plant_name_decom)])
            db_emlab.import_object_parameter_values(
                [('PowerPlants', plant_name, param_index, param_value, str(current_emlab_tick))
                 for (param_index, param_value) in param_values_emlab] +
                [('PowerPlants', plant_name_decom, param_index, param_value, str(current_emlab_tick))
                 for (param_index, param_value) in param_values_emlab_decom])

        else:
            print('Node != NED')
            param_values = [i for i in row[4:].items() if not (i[0] == 'UNITEU' or
                                                               i[0] == 'MWEU' or
                                                               i[0] == 'ON-STREAMEU' or
                                                               i[0] == 'EfficiencyEU' or
                                                               i[0] == 'AvailabilityEU')]
            param_values_competes = [('ON-STREAMEU', online_in_year),
                                     ('MWEU', row['MWEU']),
                                     ('AvailabilityEU', plant_availability),
                                     ('EfficiencyEU', plant_efficiency)] + param_values
            param_values_competes_decom = [('ON-STREAMEU', online_in_year + 40),
                                           ('MWEU', -1 * row['MWEU']),
                                           ('AvailabilityEU', plant_availability),
                                           ('EfficiencyEU', plant_efficiency)] + param_values
            competes_table_name = 'Installed Capacity Abroad'

        print('Exporting to COMPETES...')
        db_competes.import_objects([(competes_table_name, plant_name), (competes_table_name, plant_name_decom)])
        db_competes.import_object_parameter_values(
            [(competes_table_name, plant_name, param_name, param_value, '0') for (param_name, param_value)
             in param_values_competes] +
            [(competes_table_name, plant_name_decom, param_name, param_value, '0') for (param_name, param_value)
             in param_values_competes_decom])

        print('Exported plant ' + plant_name + ' with parameters ' + str(param_values_competes))
    print('Done exporting Investment Decisions to EMLAB and COMPETES')


def export_power_plant_dispatch_plans_to_emlab(db_emlab, current_emlab_tick, unit_generation_df, db_emlab_ppdps,
                                               hourly_nodal_prices_nl, db_emlab_powerplants):
    """
    This function exports all dispatch and nodal prices from COMPETES output. EMLab interprets this as
    PowerPlantDispatchPlans. In order to achieve the right results, the price of the ppdp is set at the average of
    all the prices the plant operates. Capacity is set to total capacity of the year (sum).

    :param db_emlab: SpineDB
    :param current_emlab_tick: int
    :param unit_generation_df: Dataframe of COMPETES output
    :param db_emlab_ppdps: Queried PowerPlantDispatchPlans from EMLab
    :param hourly_nodal_prices_nl: Hourly nodal prices from COMPETES
    :param db_emlab_powerplants: Queried Powerplants from EMLab
    """
    print('Exporting PowerPlantDispatchPlans into EMLAB')
    ppdp_objects_to_import = []
    ppdp_values_to_import = []
    for power_plant in unit_generation_df.columns:
        print('Staging PPDP for ' + str(power_plant))
        try:
            ppdp_name = next(i['object_name'] for i in db_emlab_ppdps if
                             i['parameter_name'] == 'Plant' and i['parameter_value'] == power_plant and i[
                                 'alternative'] == str(current_emlab_tick))
        except StopIteration:
            ppdp_name = 'PowerPlantDispatchPlan ' + str(datetime.now())
            ppdp_objects_to_import.append(('PowerPlantDispatchPlans', ppdp_name))

        accepted = sum(unit_generation_df[power_plant].values)
        if accepted > 0:
            hourly_nodal_prices_nl_where_plant_generated = [i for i in zip(unit_generation_df[power_plant].values,
                                                                           hourly_nodal_prices_nl) if i[0] > 0]
            ppdp_price = sum([float(i[0]) * float(i[1]) for i in
                              hourly_nodal_prices_nl_where_plant_generated]) / accepted if accepted > 0 else 0
            owner = next(row['parameter_value'] for row in db_emlab_powerplants if
                         row['object_name'] == power_plant and row['parameter_name'] == 'FirmNL')
            status = 'Accepted' if accepted > 0 else 'Failed'
            values = [('AcceptedAmount', accepted), ('Capacity', accepted), ('EnergyProducer', owner),
                      ('Market', 'DutchElectricitySpotMarket'), ('Plant', power_plant), ('Status', status),
                      ('Price', ppdp_price)]
            ppdp_values_to_import = ppdp_values_to_import + [
                ('PowerPlantDispatchPlans', ppdp_name, i[0], i[1], str(current_emlab_tick)) for i in values]
        else:
            print('Accepted amount == 0, not importing')
    db_emlab.import_objects(ppdp_objects_to_import)
    db_emlab.import_object_parameter_values(ppdp_values_to_import)
    print('Done exporting PowerPlantDispatchPlans to EMLAB')


def get_hourly_nodal_prices(hourly_nodal_prices_df):
    """
    This function retrieves the desired data of the dataframe of hourly nodal prices from COMPETES.

    :param hourly_nodal_prices_df:
    :return: Specific values of the Netherlands
    """
    hourly_nodal_prices_df.columns = hourly_nodal_prices_df.iloc[0]
    hourly_nodal_prices_df.drop([0])
    return hourly_nodal_prices_df['NED'][1:].values


def export_market_clearing_points_to_emlab(db_emlab, current_emlab_tick, hourly_nodal_prices_nl, db_emlab_mcps):
    """
    This function exports the MCP of the Electricity Spot Market to EM-Lab. This is the average price of all the hours.

    :param db_emlab_mcps: MCPs as queried of SpineDB EMLab
    :param db_emlab: SpineDB
    :param current_emlab_tick: int
    :param hourly_nodal_prices_nl: Hourly Nodal prices object from get_hourly_nodal_prices
    """
    print('Exporting MarketClearingPoint to EMLAB')
    hourly_nodal_prices_nl_avg = sum(hourly_nodal_prices_nl) / len(hourly_nodal_prices_nl)
    print('Average hourly nodal prices: ' + str(hourly_nodal_prices_nl_avg))

    print('Checking if MCP already exists for this run')
    try:
        newobject_mcp_name = next(i['object_name'] for i in db_emlab_mcps
                                  if i['parameter_name'] == 'Market'
                                  and i['parameter_value'] == 'DutchElectricitySpotMarket')
    except StopIteration:
        newobject_mcp_name = 'MarketClearingPoint ' + str(datetime.now())

    print('Staging...')
    values = [('Market', 'DutchElectricitySpotMarket'), ('Price', hourly_nodal_prices_nl_avg)]
    db_emlab.import_objects([('MarketClearingPoints', newobject_mcp_name)])
    db_emlab.import_object_parameter_values(
        [('MarketClearingPoints', newobject_mcp_name, i[0], i[1], str(current_emlab_tick))
         for i in values])
    print('Done exporting MarketClearingPoint to EMLAB')


def crop_dataframe_until_first_empty_row(df):
    """
    This function is used to crop dataframes that have lots of empty rows (with NaN).
    It returns all data until the first row with all NaN values.

    :param df: Dataframe
    :return: Cropped Dataframe
    """
    if df.isnull().values.any() and df.loc[df.iloc[:, 0].isnull(), :].size > 0:
        first_row_with_all_nan = df.loc[df.iloc[:, 0].isnull(), :].index.tolist()[0]
        return df.loc[0:first_row_with_all_nan - 1]
    else:
        return df


def export_total_sum_exports_to_emlab(db_emlab, hourly_nl_balance_df, current_emlab_tick):
    """
    Export the amount of CO2 tons caused by exports. Estimation: 0.287 is average ton / MWh and 0.47 is average
    efficiency.

    :param db_emlab:
    :param hourly_nl_balance_df:
    :param current_emlab_tick:
    :return:
    """
    db_emlab.import_object_classes(['Exports'])
    db_emlab.import_objects([('Exports', 'Exports')])
    db_emlab.import_data({'object_parameters': [['Exports', 'Exports']]})
    db_emlab.import_object_parameter_values([('Exports', 'Exports', 'Exports',
                                              hourly_nl_balance_df['Exports'].sum() * 0.287 / 0.47,
                                              str(current_emlab_tick))])


def export_all_competes_results():
    """
    This is the main export function
    """

    print('Establishing Database Connections...')
    db_emlab = SpineDB(sys.argv[1])
    db_competes = SpineDB(sys.argv[2])
    db_config = SpineDB(sys.argv[3])
    print('Done')

    try:
        db_config_parameters = db_config.query_object_parameter_values_by_object_class('Coupling Parameters')
        start_simulation_year = next(int(i['parameter_value']) for i in db_config_parameters
                                     if i['object_name'] == 'Start Year')
        look_ahead = next(int(i['parameter_value']) for i in db_config_parameters if i['object_name'] == 'Look Ahead')
        current_emlab_tick, current_competes_tick, current_competes_tick_rounded = get_current_ticks(db_emlab,
                                                                                                     start_simulation_year)
        print('Current EM-Lab tick: ' + str(current_emlab_tick))
        print('Current COMPETES tick: ' + str(current_competes_tick))

        db_emlab_powerplants, db_emlab_ppdps, db_competes_powerplants, db_emlab_mcps, db_competes_vre_capacities, \
        db_emlab_technologies, db_competes_new_technologies = query_databases(db_emlab, db_competes)

        print('Staging next SpineDB alternative...')
        step = next(int(i['parameter_value']) for i in db_config_parameters if i['object_name'] == 'Time Step')
        db_emlab.import_alternatives([str(current_emlab_tick + step)])

        path_to_competes_results = sys.argv[4]
        file_name_gentransinv = sys.argv[5].replace('?', str(current_competes_tick + look_ahead))
        file_name_gentransdisp = sys.argv[6].replace('?', str(current_competes_tick))

        print('Loading sheets...')
        hourly_nodal_prices_df, unit_generation_df, new_generation_capacity_df, decommissioning_df, vre_investment_df, \
        hourly_nl_balance_df, yearly_emissions_df = read_excel_sheets(path_to_competes_results, file_name_gentransinv,
                                                 file_name_gentransdisp)

        new_generation_capacity_df = crop_dataframe_until_first_empty_row(new_generation_capacity_df)
        vre_investment_df = crop_dataframe_until_first_empty_row(vre_investment_df)
        decommissioning_df = crop_dataframe_until_first_empty_row(decommissioning_df)

        # VRE Plants are added to unit_generation sheet
        hourly_nl_balance_df = hourly_nl_balance_df.rename(columns={'Sun': 'SunPV', 'Wind Onshore': 'WindOn',
                                                                    'Wind Offshore': 'WindOff'})
        unit_generation_df = unit_generation_df.transpose().join(
            hourly_nl_balance_df[['SunPV', 'WindOn', 'WindOff']]).replace(np.nan, 0)
        print('Done loading sheets')

        hourly_nodal_prices_nl = get_hourly_nodal_prices(hourly_nodal_prices_df)
        export_vre_investment_decisions(db_emlab, db_competes, current_emlab_tick, current_competes_tick,
                                        vre_investment_df, db_emlab_technologies, db_competes_vre_capacities,
                                        step)
        export_market_clearing_points_to_emlab(db_emlab, current_emlab_tick, hourly_nodal_prices_nl, db_emlab_mcps)
        export_power_plant_dispatch_plans_to_emlab(db_emlab, current_emlab_tick, unit_generation_df, db_emlab_ppdps,
                                                   hourly_nodal_prices_nl, db_emlab_powerplants)
        export_investment_decisions_to_emlab_and_competes(db_emlab, db_competes, current_emlab_tick,
                                                          new_generation_capacity_df, current_competes_tick,
                                                          db_emlab_technologies, db_competes_new_technologies)
        export_decommissioning_decisions_to_emlab_and_competes(db_competes, db_emlab, db_competes_powerplants,
                                                               decommissioning_df, current_competes_tick,
                                                               current_emlab_tick, look_ahead)
        export_total_sum_exports_to_emlab(db_emlab, hourly_nl_balance_df, current_emlab_tick)
        export_yearly_emissions_to_emlab(db_emlab, yearly_emissions_df, current_emlab_tick)

        print('Committing...')
        db_emlab.commit('Imported from COMPETES run ' + str(current_competes_tick))
        db_competes.commit('Imported from COMPETES run ' + str(current_competes_tick))
        print('Done')
    except Exception as e:
        print('Exception occurred: ' + str(e))
        raise
    finally:
        print('Closing database connection...')
        db_emlab.close_connection()
        db_competes.close_connection()
        db_config.close_connection()


if __name__ == "__main__":
    print('===== Starting COMPETES Output Interpretation script =====')
    export_all_competes_results()
    print('===== End of COMPETES Output Interpretation script =====')

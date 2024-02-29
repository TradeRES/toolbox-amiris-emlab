"""
This modules keeps the count of the clock, simulation year.

1. first all candidate power plants are reset to be investable

In the "initializate_clock" mode the excel results from previous simulations are deleted
2a. the current year in DB is set to the year specified in the input
3a. the years file is updated
4a. The load and profile data are prepared

In the "increment_clock" mode
If there are target ivestments, the target investments status is also reset to false
2.b current year and tick are increased (if its not the final year) in DB
3.b years file is updated
4.b The load and profile data are prepared

Ingrid modified 17-2-2022
Jim Hommes - 7-4-2021
"""
import sys
from util.spinedb import SpineDB
from plots.plots import plotting
from util import globalNames
import glob
import os
import pandas as pd
from os.path import dirname, realpath
import spinedb_api.import_functions as im
import socket
import shutil

from spinedb_api import DatabaseMapping, from_database, Map, to_database

db_url = sys.argv[1]
db_emlab = SpineDB(db_url)

grandparentpath = dirname(dirname(realpath(os.getcwd())))
parentpath = os.path.dirname(os.getcwd())

amiris_data_path = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data')
amiris_ouput_path = os.path.join(grandparentpath, 'amiris_workflow\\output\\')
amiris_worfklow_path = os.path.join(grandparentpath, 'amiris_workflow\\')

windon_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\windon.csv')
windoff_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\windoff.csv')
pv_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\pv.csv')

windon_firstyear_file_for_amiris = os.path.join(grandparentpath,
                                                'amiris_workflow\\amiris-config\\data\\first_year_windon.csv')
windoff_firstyear_file_for_amiris = os.path.join(grandparentpath,
                                                 'amiris_workflow\\amiris-config\\data\\first_year_windoff.csv')
pv_firstyear_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\first_year_pv.csv')
future_windon_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\future_windon.csv')
future_windoff_file_for_amiris = os.path.join(grandparentpath,
                                              'amiris_workflow\\amiris-config\\data\\future_windoff.csv')
future_pv_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\future_pv.csv')


def copy_files(source_folder, destination_folder):
    # Ensure the source folder exists
    if not os.path.exists(source_folder):
        print(f"Source folder '{source_folder}' does not exist.")
        return

    # Ensure the destination folder exists, create it if it doesn't
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Get a list of all files in the source folder
    files = os.listdir(source_folder)

    # Iterate over each file and copy it to the destination folder
    for file_name in files:
        source_path = os.path.join(source_folder, file_name)
        destination_path = os.path.join(destination_folder, file_name)

        # Check if it's a file and not a directory
        if os.path.isfile(source_path):
            shutil.copy2(source_path, destination_path)
            print(f"Copied '{file_name}' to '{destination_folder}'.")
        else:
            print(f"Ignored '{file_name}' as it is a directory.")


def reset_candidate_investable_status():
    class_name = "CandidatePowerPlants"
    candidate_powerplants = [i for i in db_emlab.query_object_parameter_values_by_object_class(class_name)]
    for candidate in candidate_powerplants:
        db_emlab.import_object_parameter_values(
            [(class_name, candidate["object_name"], "ViableInvestment", bool(1), '0')])


def reset_target_investments_done():
    class_name = "Configuration"
    db_emlab.import_object_parameter_values(
        [(class_name, "SimulationYears", "target_investments_done", bool(0), '0')])


def update_years_file(current_year, initial, final_year, lookAhead):
    print("updated years file")
    # once the spine bug is fixed. then it can be exported to the output folder.
    # the clock is executed in the util folder. So save the results in the parent folder: emlabpy
    complete_path = os.path.join(os.path.dirname(os.getcwd()), globalNames.years_file)
    f = open(complete_path, "w")
    years_str = str(current_year) + "/" + str(initial) + "/" + str(final_year) + "/" + str(current_year + lookAhead)
    f.write(years_str)
    f.close()


def prepare_AMIRIS_data(year, new_tick, fix_demand_to_representative_year, fix_profiles_to_representative_year,
                        modality):
    print(
        "preparing data for years " + str(year) + " and investment " + str(representative_year_investment) + " for NL")
    """
    load files are updated in market preparation. 
    The VRES profiles have to be prepared in this step
    """
    try:

        # =======================================================================================updating profiles
        excel = pd.read_excel(input_weather_years_excel, index_col=0,
                              sheet_name=["Wind Onshore profiles",
                                          "Wind Offshore profiles",
                                          "Sun PV profiles",
                                          "Load"])

        if modality == "initialize":
            global peak_load
            peak_load = max(excel['Load'][representative_year_investment])
        if fix_demand_to_representative_year == False and fix_profiles_to_representative_year == True:
            print("--------load and profiles should be related")
            raise Exception
        elif fix_demand_to_representative_year == True and fix_profiles_to_representative_year == True:
            # future profiles are upated for representative year
            print("--------fix demand and profiles")
            if modality == "initialize":
                update_profiles_current_year(excel, representative_year_investment)
                prepare_initialization_load_for_future_year(excel, representative_year_investment)
                update_load_shedders_current_year(excel, representative_year_investment)
                prepare_hydrogen_initilization_future(excel)  # todo make this changing for future
                prepare_hydrogen_initilization(excel)


        elif fix_demand_to_representative_year == False and fix_profiles_to_representative_year == False:
            print("---------update demand and update profiles")
            iteration = next(i['parameter_value'] for i in
                             db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name,
                                                                                                    object_name) \
                             if i['parameter_name'] == 'iteration')

            weatherYears_data = next(i['parameter_value'] for i in
                                     db_emlab.query_object_parameter_values_by_object_class_and_object_name(
                                         "weatherYears", "weatherYears") if i['alternative'] == iteration)

            weatherYears = pd.DataFrame(weatherYears_data.values, index=weatherYears_data.indexes)
            sequence_year = weatherYears.values[new_tick]
            print("preparing year profiles to RANDOM year " + str(sequence_year))
            update_load_current_year_by_sequence_year(excel, sequence_year)  # uplad Load

            if modality == "initialize":
                """"
                The investments are done for the same future "representative" year.
                All initialization loop investments are made according to representative year.
                Profiles are prepared for first year, so that these are overwritten in the 
                """
                print("Initializing first year:" + str(sequence_year) + " and future profiles based on " + str(
                    representative_year_investment))
                prepare_initialization_load_for_future_year(excel, representative_year_investment)
                prepare_hydrogen_initilization_future(excel)
                prepare_hydrogen_initilization(excel)
                prepare_initialization_profiles_for_future_year(excel)  # future profiles
                update_profiles_first_year(excel, sequence_year)
            else:
                # current year profile change, but future profiles remain
                wind_onshore = excel['Wind Onshore profiles'][sequence_year]
                wind_onshore.to_csv(windon_file_for_amiris, header=False, sep=';', index=True)
                wind_offshore = excel['Wind Offshore profiles'][sequence_year]
                wind_offshore.to_csv(windoff_file_for_amiris, header=False, sep=';', index=True)
                pv = excel['Sun PV profiles'][sequence_year]
                pv.to_csv(pv_file_for_amiris, header=False, sep=';', index=True)
        else:
            raise Exception

    except Exception as e:
        print("failed updating AMIRIS data")
        raise Exception
    return 0


def update_load_shedders_current_year(excel, current_year):
    for lshedder_name in load_shedders_no_hydrogen:
        load_shedder = excel['Load'][current_year] *  load_shedders.loc[lshedder_name, "percentage_load"]
        load_shedder_file_for_amiris = os.path.join(amiris_worfklow_path, "amiris-config", "data",
                                                    ("LS_" + lshedder_name + ".csv"))
        load_shedder.to_csv(load_shedder_file_for_amiris, header=False, sep=';', index=True)


def update_load_current_year_by_sequence_year(excel, sequence_year):
    """
    Demand is not increasing but the load is changing in every weather year due to heat demand
    """
    for lshedder_name in load_shedders_no_hydrogen:
        load_shedder = excel['Load'][sequence_year] * load_shedders.loc[lshedder_name, "percentage_load"]
        load_shedder_file_for_amiris = os.path.join(amiris_worfklow_path, os.path.normpath(
            load_shedders.loc[lshedder_name, "TimeSeriesFile"]))
        load_shedder.to_csv(load_shedder_file_for_amiris, header=False, sep=';', index=True)


def prepare_initialization_load_for_future_year(excel, representative_year_investment):
    # writing FUTURE load shedders
    for lshedder_name in load_shedders_no_hydrogen:
        load_shedder_file_for_amiris = os.path.join(amiris_worfklow_path, "amiris-config", "data",
                                                    "originalFuture" + lshedder_name + ".csv")
        load_shedder = excel['Load'][representative_year_investment] * load_shedders.loc[
            lshedder_name, "percentage_load"]
        load_shedder.to_csv(load_shedder_file_for_amiris, header=False, sep=';', index=True)


def prepare_hydrogen_initilization_future(excel):
    hydrogen_series = pd.DataFrame([load_shedders.loc["hydrogen", "ShedderCapacityMW"]] * 8760,
                                   index=excel['Load'].index)
    hydrogen_file_for_amiris_future = os.path.join(amiris_worfklow_path, os.path.normpath(
        load_shedders.loc["hydrogen", "TimeSeriesFileFuture"]))
    hydrogen_series.to_csv(hydrogen_file_for_amiris_future, header=False, sep=';', index=True)


def prepare_hydrogen_initilization(excel):
    # TODO: make hydrogen dynamic
    hydrogen_series = pd.DataFrame([load_shedders.loc["hydrogen", "ShedderCapacityMW"]] * 8760,
                                   index=excel['Load'].index)
    hydrogen_file_for_amiris_future = os.path.join(amiris_worfklow_path,
                                                   os.path.normpath(load_shedders.loc["hydrogen", "TimeSeriesFile"]))
    hydrogen_series.to_csv(hydrogen_file_for_amiris_future, header=False, sep=';', index=True)
    # hydrogen demand keeps constant


def prepare_initialization_profiles_for_future_year(excel):
    future_wind_offshore = excel['Wind Offshore profiles'][representative_year_investment]
    future_wind_offshore.to_csv(future_windoff_file_for_amiris, header=False, sep=';', index=True)
    future_wind_onshore = excel['Wind Onshore profiles'][representative_year_investment]
    future_wind_onshore.to_csv(future_windon_file_for_amiris, header=False, sep=';', index=True)
    future_pv = excel['Sun PV profiles'][representative_year_investment]
    future_pv.to_csv(future_pv_file_for_amiris, header=False, sep=';', index=True)


def update_profiles_first_year(excel, current_year):
    wind_onshore = excel['Wind Onshore profiles'][current_year]
    wind_onshore.to_csv(windon_firstyear_file_for_amiris, header=False, sep=';', index=True)
    wind_offshore = excel['Wind Offshore profiles'][current_year]
    wind_offshore.to_csv(windoff_firstyear_file_for_amiris, header=False, sep=';', index=True)
    pv = excel['Sun PV profiles'][current_year]
    pv.to_csv(pv_firstyear_file_for_amiris, header=False, sep=';', index=True)


def update_profiles_current_year(excel, current_year):
    wind_onshore = excel['Wind Onshore profiles'][current_year]
    wind_onshore.to_csv(windon_file_for_amiris, header=False, sep=';', index=True)
    wind_offshore = excel['Wind Offshore profiles'][current_year]
    wind_offshore.to_csv(windoff_file_for_amiris, header=False, sep=';', index=True)
    pv = excel['Sun PV profiles'][current_year]
    pv.to_csv(pv_file_for_amiris, header=False, sep=';', index=True)

def read_load_shedders(updated_year):
    global load_shedders
    load_shedders_parameters = ["TimeSeriesFile", "TimeSeriesFileFuture", "ShedderCapacityMW"]
    load_shedders = pd.DataFrame(columns=load_shedders_parameters)
    load_shedders_names = []

    test = db_emlab.query_object_name_by_class_name_and_alternative("LoadShedders", "0")
    for i in test:
        if i["object_name"] in load_shedders_names:
            pass
        else:
            load_shedders_names.append(i["object_name"])
    global load_shedders_no_hydrogen
    load_shedders_no_hydrogen = load_shedders_names.copy()
    load_shedders_no_hydrogen.remove("hydrogen")
    for load_shedder in load_shedders_names:
        for parameter in load_shedders_parameters:
            load_shedders.at[load_shedder, parameter] = next(i['parameter_value'] for i in
                                                             db_emlab.query_object_parameter_values_by_object_class_and_object_name(
                                                                 "LoadShedders", load_shedder) if
                                                             i['parameter_name'] == parameter)

    for load_shedder in load_shedders_no_hydrogen:
        load_shedder_map = next(i['parameter_value'] for i in
                                db_emlab.query_object_parameter_values_by_object_class_and_object_name(
                                    "LoadShedders", load_shedder) if
                                i['parameter_name'] == "percentage_load")
        array = load_shedder_map.to_dict()
        values = [float(i[1]) for i in array["data"]]
        index = [int(i[0]) for i in array["data"]]
        pd_series = pd.Series(values, index=index)
        load_shedders.at[load_shedder, "percentage_load"] = pd_series[updated_year]
def prepare_AMIRIS_data_for_one_year():
    print("preparing data when there are no more years data available")
    load_path_DE = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\load_DE.csv')
    pv_path_DE = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\pv_DE.csv')
    windon_path_DE = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\windon_DE.csv')
    windoff_path_DE = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\windoff_DE.csv')
    demand = pd.read_csv(load_path_DE, delimiter=";", header=None)
    demand.to_csv(load_file_for_amiris, header=False, sep=';', index=False)
    wind_onshore = pd.read_csv(windon_path_DE, delimiter=";", header=None)
    wind_onshore.to_csv(windon_file_for_amiris, header=False, sep=';', index=False)
    wind_offshore = pd.read_csv(windoff_path_DE, delimiter=";", header=None)
    wind_offshore.to_csv(windoff_file_for_amiris, header=False, sep=';', index=False)
    pv = pd.read_csv(pv_path_DE, delimiter=";", header=None)
    pv.to_csv(pv_file_for_amiris, header=False, sep=';', index=False)


try:
    class_name = "Configuration"
    object_name = 'SimulationYears'
    object_parameter_value_name = 'SimulationTick'
    peak_load = 0
    # print(os.getcwd())
    if len(sys.argv) >= 3:
        lookAhead = next(int(i['parameter_value']) for i
                         in
                         db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name) \
                         if i['parameter_name'] == "Look Ahead")
        final_year = next(int(i['parameter_value']) for i
                          in db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name,
                                                                                                    object_name) \
                          if i['parameter_name'] == "End Year")
        global StartYear
        StartYear = next(int(i['parameter_value']) for i in
                         db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name) \
                         if i['parameter_name'] == 'Start Year')
        global Country
        Country = next(i['parameter_value'] for i in
                       db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name) \
                       if i['parameter_name'] == 'Country')

        targetinvestment_per_year = next(i['parameter_value'] for i in
                                         db_emlab.query_object_parameter_values_by_object_class_and_object_name(
                                             class_name, object_name) \
                                         if i['parameter_name'] == 'targetinvestment_per_year')

        representative_year = next(i['parameter_value'] for i in
                                   db_emlab.query_object_parameter_values_by_object_class_and_object_name(
                                       class_name, object_name) \
                                   if i['parameter_name'] == 'Representative year')

        if representative_year != "NOTSET":
            global representative_year_investment
            representative_year_investment = int(representative_year)
        else:
            raise Exception
        input_weather_years_excel_name = next(i['parameter_value'] for i in
                                              db_emlab.query_object_parameter_values_by_object_class_and_object_name(
                                                  class_name, object_name) \
                                              if i['parameter_name'] == 'scenarioWeatheryearsExcel')

        global input_weather_years_excel
        input_weather_years_excel = os.path.join(grandparentpath, 'data', input_weather_years_excel_name)



        fix_demand_to_representative_year = False
        fix_demand_to_representative_year = next(i['parameter_value'] for i in
                                                 db_emlab.query_object_parameter_values_by_object_class_and_object_name(
                                                     class_name, object_name) \
                                                 if i['parameter_name'] == 'fix_demand_to_representative_year')

        fix_profiles_to_representative_year = next(i['parameter_value'] for i in
                                                   db_emlab.query_object_parameter_values_by_object_class_and_object_name(
                                                       class_name, object_name) \
                                                   if i['parameter_name'] == 'fix_profiles_to_representative_year')
        available_years_data = False
        available_years_data = next(i['parameter_value'] for i in
                                    db_emlab.query_object_parameter_values_by_object_class_and_object_name(
                                        class_name, object_name) \
                                    if i['parameter_name'] == 'available_years_data')
        reset_candidate_investable_status()
        print("reset power plants status ")

        if sys.argv[2] == 'initialize_clock':
            print('delete excels in output')
            start_plot = False
            try:  # removing excels from previous rounds
                for f in glob.iglob(amiris_ouput_path + '/*.xlsx', recursive=True):
                    os.remove(f)

            except Exception as e:
                print(e)

            try:  # removing excels from previous rounds
                files_to_keep = ['otherres.csv', 'biomass.csv', "runofriver.csv"]

                # Get a list of all files in the folder
                all_files = os.listdir(amiris_data_path)

                # Iterate through the files and delete CSV files that are not in the 'files_to_keep' list
                for file_name in all_files:
                    if file_name.endswith('.csv') and file_name not in files_to_keep:
                        file_path = os.path.join(amiris_data_path, file_name)
                        os.remove(file_path)
            except Exception as e:
                print(e)

            print('Initializing clock (tick 0)')
            db_emlab.import_object_classes([class_name])
            db_emlab.import_objects([(class_name, object_name)])
            db_emlab.import_data({'object_parameters': [[class_name, object_parameter_value_name]]})
            db_emlab.import_alternatives([str(0)])
            db_emlab.import_object_parameter_values([(class_name, object_name, object_parameter_value_name, 0, '0')])
            db_emlab.import_object_parameter_values([(class_name, object_name, "CurrentYear", StartYear, '0')])
            read_load_shedders(StartYear)
            update_years_file(StartYear, StartYear, final_year, lookAhead)
            db_emlab.commit('Clock intialization')
            print('Done initializing clock (tick 0)')

            if available_years_data == True:
                prepare_AMIRIS_data(StartYear, 0, fix_demand_to_representative_year,
                                    fix_profiles_to_representative_year,
                                    "initialize")
            else:  # no dynamic data for other cases
                prepare_AMIRIS_data_for_one_year()

        elif sys.argv[2] == 'increment_clock':  # increment clock

            if targetinvestment_per_year == True:
                reset_target_investments_done()
                print(" target investments status")

            # if test_first_intermittent_technologies == True:
            #     reset_testing_intermittent_technologies()
            step = 1  # yearly increment
            previous_tick = next(int(i['parameter_value']) for i
                                 in db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name,
                                                                                                           object_name) \
                                 if i['parameter_name'] == object_parameter_value_name)

            new_tick = step + previous_tick
            print('Incrementing Clock to ' + str(new_tick))
            Current_year = next(int(i['parameter_value']) for i in
                                db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name,
                                                                                                       object_name) \
                                if i['parameter_name'] == 'CurrentYear')

            updated_year = step + Current_year
            read_load_shedders(updated_year)
            if updated_year >= final_year:
                print("final year achieved " + str(final_year))
                start_plot = True
                # updating file to stop simulation.
                update_years_file(updated_year, StartYear, final_year,
                                  lookAhead)
            else:
                start_plot = False
                update_years_file(updated_year, StartYear, final_year, lookAhead)
                db_emlab.import_object_parameter_values(
                    [(class_name, object_name, object_parameter_value_name, new_tick, '0')])
                db_emlab.import_object_parameter_values([(class_name, object_name, "CurrentYear", updated_year, '0')])
                db_emlab.commit('Clock increment')
                print('Done incrementing clock (tick +' + str(step) + '), resetting invest file and years file')

            if available_years_data == True:
                prepare_AMIRIS_data(updated_year, new_tick, fix_demand_to_representative_year,
                                    fix_profiles_to_representative_year,
                                    "increment")
                print("prepared AMIRIS data ")
            else:  # no dynamic data for other cases
                print("no dynamic data for this country")

        else:
            raise Exception
    else:
        print("missing one argument")
        raise Exception
except Exception:
    raise
finally:
    db_emlab.close_connection()

if start_plot == True:
    results_excel = "test.xlsx"
    SCENARIOS = ["NL-temporal"]
    existing_scenario = False
    from_workflow = True

    destination_folder = os.path.join(grandparentpath, 'temporal_results')
    for file_name in os.listdir(destination_folder):
        file_path = os.path.join(destination_folder, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

    copy_files(os.path.join(grandparentpath, '.spinetoolbox\\items\\amiris_db'), destination_folder)
    copy_files(os.path.join(grandparentpath, 'amiris_workflow\\output'), destination_folder)
    copy_files(os.path.join(grandparentpath, '.spinetoolbox\\items\\emlabdb'), destination_folder)
    os.chdir('../..')
    os.chdir('emlabpy')
    plotting(SCENARIOS, results_excel, sys.argv[1], sys.argv[3], existing_scenario)

if sys.argv[2] == 'increment_clock':
    db_map = DatabaseMapping(db_url)
    try:
        subquery = db_map.object_parameter_value_sq
        statuses = {row.object_id: from_database(row.value, row.type) for row in
                    db_map.query(subquery).filter(subquery.c.parameter_name == "status")}
        removable_object_ids = {object_id for object_id, status in statuses.items()}
        db_map.cascade_remove_items(object=removable_object_ids)
        print("removed awaiting bids")
        db_map.commit_session("Removed unacceptable objects.")
    finally:
        db_map.connection.close()

elif sys.argv[2] == 'initialize_clock':
    db_map = DatabaseMapping(db_url)
    print('updating peak load')
    try:
        class_name = "ElectricitySpotMarkets"
        object_name = "ElectricitySpotMarket" + Country
        parameter_name = "peakLoadFixed"
        alternative_name = str(0)
        peak_load_Map = Map([2020.0, StartYear], [20000, peak_load])
        im.import_object_classes(db_map, [class_name])
        im.import_objects(db_map, [(class_name, object_name)])
        im.import_object_parameters(db_map, [(class_name, parameter_name)])
        im.import_alternatives(db_map, [alternative_name])
        im.import_object_parameter_values(
            db_map,
            [(class_name, object_name, parameter_name, peak_load_Map, alternative_name)],
        )
        db_map.commit_session("Add initial data.")
    finally:
        db_map.connection.close()

# print('removing awaiting bids...')
# db_map = DatabaseMapping(db_url)


#
# # Now we have data in the database.
# # Let's find that peak load value and modify it.
#
# # Unfortunately, this is somewhat complicated as we need to do a raw database query.
# sq = db_map.object_parameter_value_sq
# value_record = db_map.query(sq).filter(sq.c.object_class_name == class_name).filter(
#     sq.c.object_name == object_name
# ).filter(sq.c.parameter_name == parameter_name).filter(
#     sq.c.alternative_name == alternative_name
# ).one()
#
# peak_load = from_database(value_record.value, value_record.type)
#
# # Finally we get to modify the value.
# peak_load.set_value(2050.0, 33000.0)
#
# # Store the modified value back to database.
# im.import_object_parameter_values(
#     db_map,
#     [(class_name, object_name, parameter_name, peak_load, alternative_name)],
# )
#     db_map.commit_session("Update peak load value.")
# finally:
#     db_map.connection.close()

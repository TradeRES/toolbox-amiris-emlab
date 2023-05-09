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
from util import globalNames
import glob
import os
import pandas as pd
from os.path import dirname, realpath

db_url = sys.argv[1]
db_emlab = SpineDB(db_url)
from spinedb_api import DatabaseMapping, from_database

grandparentpath = dirname(dirname(realpath(os.getcwd())))
parentpath = os.path.dirname(os.getcwd())

amiris_ouput_path = os.path.join(grandparentpath, 'amiris_workflow\\output\\')
amiris_worfklow_path = os.path.join(grandparentpath, 'amiris_workflow\\')
load_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\load.csv')
future_load_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\future_load.csv')

#
# input_yearly_profiles_demand = os.path.join(grandparentpath,
#                                             'data\\VREprofilesandload2019-2050.xlsx')

windon_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\windon.csv')
windoff_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\windoff.csv')
pv_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\pv.csv')

windon_firstyear_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\first_year_windon.csv')
windoff_firstyear_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\first_year_windoff.csv')
pv_firstyear_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\first_year_pv.csv')

future_windon_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\future_windon.csv')
future_windoff_file_for_amiris = os.path.join(grandparentpath,
                                              'amiris_workflow\\amiris-config\\data\\future_windoff.csv')
future_pv_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\future_pv.csv')


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

# def reset_testing_intermittent_technologies():
#     class_name = "Configuration"
#     db_emlab.import_object_parameter_values(
#         [(class_name, "SimulationYears", "testing_intermittent_technologies", bool(1), '0')])

def update_years_file(current_year, initial, final_year, lookAhead):
    print("updated years file")
    # once the spine bug is fixed. then it can be exported to the output folder.
    # the clock is executed in the util folder. So save the results in the parent folder: emlabpy
    complete_path = os.path.join(os.path.dirname(os.getcwd()), globalNames.years_file)
    f = open(complete_path, "w")
    years_str = str(current_year) + "/" + str(initial) + "/" + str(final_year) + "/" + str(current_year + lookAhead)
    f.write(years_str)
    f.close()


def prepare_AMIRIS_data(year, new_tick, fix_demand_to_initial_year, fix_profiles_to_initial_year,
                        modality):
    print("preparing data for years " + str(year) + " and investment " + str(investment_year) + " for NL")
    try:
        excel = pd.read_excel(input_weather_years_excel, index_col=0,
                                 sheet_name=["Wind Onshore profiles",
                                             "Wind Offshore profiles",
                                             "Sun PV profiles",
                                             "Load"])

        if fix_demand_to_initial_year == False and fix_profiles_to_initial_year == True:
            print("--------preparing demand, fix profiles")
            demand = excel['Load'][year]
            demand.to_csv(load_file_for_amiris, header=False, sep=';', index=True)
            future_demand = excel['Load'][investment_year]
            future_demand.to_csv(future_load_file_for_amiris, header=False, sep=';', index=True)

            if modality == "initialize":
                print("--------preparing profiles NOT random")
                wind_onshore = excel['Wind Onshore profiles'][year]
                wind_onshore.to_csv(windon_file_for_amiris, header=False, sep=';', index=True)
                wind_offshore = excel['Wind Offshore profiles'][year]
                wind_offshore.to_csv(windoff_file_for_amiris, header=False, sep=';', index=True)
                pv = excel['Sun PV profiles'][year]
                pv.to_csv(pv_file_for_amiris, header=False, sep=';', index=True)
            else:
                pass

        elif fix_demand_to_initial_year == True and fix_profiles_to_initial_year == True:
            print("--------fix demand and fix profiles")
            # profiles are same are representative year
            if modality == "initialize":
                demand = excel['Load'][year]
                demand.to_csv(load_file_for_amiris, header=False, sep=';', index=True)
                wind_onshore = excel['Wind Onshore profiles'][year]
                wind_onshore.to_csv(windon_file_for_amiris, header=False, sep=';', index=True)
                wind_offshore = excel['Wind Offshore profiles'][year]
                wind_offshore.to_csv(windoff_file_for_amiris, header=False, sep=';', index=True)
                pv = excel['Sun PV profiles'][year]
                pv.to_csv(pv_file_for_amiris, header=False, sep=';', index=True)
            else:
                pass

        elif fix_demand_to_initial_year == True and fix_profiles_to_initial_year == False:
            print("---------fix demand and update profiles")
            iteration = next(i['parameter_value'] for i in
                             db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name,
                                                                                                    object_name) \
                             if i['parameter_name'] == 'iteration')

            weatherYears_data = next(i['parameter_value'] for i in
                                     db_emlab.query_object_parameter_values_by_object_class_and_object_name(
                                         "weatherYears", "weatherYears") if i['alternative'] == iteration)

            weatherYears = pd.DataFrame(weatherYears_data.values, index=weatherYears_data.indexes)
            current_year = weatherYears.values[new_tick]
            print("preparing year profiles to RANDOM year " + str(current_year))

            #Demand is not increasing but the load is changing in every weather year due to heat demand
            update_initialization_load_current_year(excel, current_year)

            if modality == "initialize":
                """"
                The investments are done for the same future "representative" year.
                All initialization loop investments are made according to representative year.
                Profiles are prepared for first year, so that these are overwritten in the 
                """
                print("Initializing demand to " + str(year) + " and future profiles based on " + str(investment_year))
                update_initialization_load_and_profiles_future_year(excel)
                update_profiles_first_year(excel, current_year)
            else:
                # current year profile change, but future profiles remain
                wind_onshore = excel['Wind Onshore profiles'].iloc[:,current_year]
                wind_onshore.to_csv(windon_file_for_amiris, header=False, sep=';', index=True)
                wind_offshore = excel['Wind Offshore profiles'].iloc[:,current_year]
                wind_offshore.to_csv(windoff_file_for_amiris, header=False, sep=';', index=True)
                pv = excel['Sun PV profiles'].iloc[:,current_year]
                pv.to_csv(pv_file_for_amiris, header=False, sep=';', index=True)

        elif fix_demand_to_initial_year == False and fix_profiles_to_initial_year == False:
            print("demand and profiles change every year")
            raise Exception # profiles would only change year to year but not multiple weather years
        else:
            raise Exception
    except Exception as e:
        print("failed updating AMIRIS data")
        print(e)
    return 0

def update_initialization_load_current_year(excel,current_year):
    load = excel['Load'].iloc[:,current_year] *load_shedders.loc["base", "percentage_load"]
    load.to_csv(load_file_for_amiris, header=False, sep=';', index=True)
    for lshedder in ["low", "mid", "high"]:
        load_shedder = excel['Load'].iloc[:,current_year] *load_shedders.loc[lshedder,"percentage_load"]
        load_shedder_file_for_amiris = os.path.join(amiris_worfklow_path, os.path.normpath(load_shedders.loc[lshedder,"TimeSeriesFile"]))
        load_shedder.to_csv(load_shedder_file_for_amiris, header=False, sep=';', index=True)
    print("total load for current year:")
    print(load.sum())

def update_initialization_load_and_profiles_future_year(excel):
    for lshedder in ["low", "mid", "high"]:
        load_shedder = excel['Load'][investment_year] * load_shedders.loc[lshedder, "percentage_load"]
        load_shedder_file_for_amiris = os.path.join(amiris_worfklow_path, os.path.normpath( load_shedders.loc[lshedder,"TimeSeriesFileFuture"]))
        load_shedder.to_csv(load_shedder_file_for_amiris, header=False, sep=';', index=True)
    future_demand = excel['Load'][investment_year] * load_shedders.loc["base", "percentage_load"]
    future_demand.to_csv(future_load_file_for_amiris, header=False, sep=';', index=True)
    future_wind_offshore = excel['Wind Offshore profiles'][investment_year]
    future_wind_offshore.to_csv(future_windoff_file_for_amiris, header=False, sep=';', index=True)
    future_wind_onshore = excel['Wind Onshore profiles'][investment_year]
    future_wind_onshore.to_csv(future_windon_file_for_amiris, header=False, sep=';', index=True)
    future_pv = excel['Sun PV profiles'][investment_year]
    future_pv.to_csv(future_pv_file_for_amiris, header=False, sep=';', index=True)
    print("total load for investment year")
    print(sum(future_demand))

def update_profiles_first_year(excel, current_year):
    wind_onshore = excel['Wind Onshore profiles'].iloc[:,current_year]
    wind_onshore.to_csv(windon_firstyear_file_for_amiris, header=False, sep=';', index=True)
    wind_offshore = excel['Wind Offshore profiles'].iloc[:,current_year]
    wind_offshore.to_csv(windoff_firstyear_file_for_amiris, header=False, sep=';', index=True)
    pv = excel['Sun PV profiles'].iloc[:,current_year]
    pv.to_csv(pv_firstyear_file_for_amiris, header=False, sep=';', index=True)


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
    # print(os.getcwd())
    if len(sys.argv) >= 2:
        lookAhead = next(int(i['parameter_value']) for i
                         in
                         db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name) \
                         if i['parameter_name'] == "Look Ahead")
        final_year = next(int(i['parameter_value']) for i
                          in db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name,
                                                                                                    object_name) \
                          if i['parameter_name'] == "End Year")
        StartYear = next(int(i['parameter_value']) for i in
                         db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name) \
                         if i['parameter_name'] == 'Start Year')

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
            global investment_year
            investment_year = int(representative_year)
        else:
            raise Exception
        input_weather_years_excel_name = next(i['parameter_value'] for i in
                                         db_emlab.query_object_parameter_values_by_object_class_and_object_name(
                                             class_name, object_name) \
                                         if i['parameter_name'] == 'scenarioWeatheryearsExcel')

        global input_weather_years_excel
        input_weather_years_excel = os.path.join(grandparentpath, 'data', input_weather_years_excel_name)

        global load_shedders
        load_shedders = pd.DataFrame(columns=["TimeSeriesFile", "percentage_load", "TimeSeriesFileFuture"])

        for load_shedder in ["low", "mid", "high", "base"]:
            load_shedders.at[load_shedder, 'TimeSeriesFile']  = next(i['parameter_value'] for i in
                     db_emlab.query_object_parameter_values_by_object_class_and_object_name(
                         "LoadShedders", load_shedder) \
                     if i['parameter_name'] == 'TimeSeriesFile')
            load_shedders.at[load_shedder, 'TimeSeriesFileFuture']  = next(i['parameter_value'] for i in
                                                                     db_emlab.query_object_parameter_values_by_object_class_and_object_name(
                                                                         "LoadShedders", load_shedder) \
                                                                     if i['parameter_name'] == 'TimeSeriesFileFuture')
            load_shedders.at[load_shedder, 'percentage_load']  = next(i['parameter_value'] for i in
                     db_emlab.query_object_parameter_values_by_object_class_and_object_name(
                         "LoadShedders", load_shedder) \
                     if i['parameter_name'] == 'percentage_load')

        fix_demand_to_initial_year = False
        fix_demand_to_initial_year = next(i['parameter_value'] for i in
                                          db_emlab.query_object_parameter_values_by_object_class_and_object_name(
                                              class_name, object_name) \
                                          if i['parameter_name'] == 'fix_demand_to_initial_year')

        fix_profiles_to_initial_year = next(i['parameter_value'] for i in
                                            db_emlab.query_object_parameter_values_by_object_class_and_object_name(
                                                class_name, object_name) \
                                            if i['parameter_name'] == 'fix_profiles_to_initial_year')
        available_years_data = False
        available_years_data = next(i['parameter_value'] for i in
                                            db_emlab.query_object_parameter_values_by_object_class_and_object_name(
                                                class_name, object_name) \
                                            if i['parameter_name'] == 'available_years_data')
        reset_candidate_investable_status()
        print("reset power plants status ")

        if sys.argv[2] == 'initialize_clock':
            print('delete excels in output')
            path = amiris_ouput_path
            try:  # removing excels from previous rounds
                for f in glob.iglob(path + '/*.xlsx', recursive=True):
                    os.remove(f)
            except Exception as e:
                print(e)

            print('Initializing clock (tick 0)')
            db_emlab.import_object_classes([class_name])
            db_emlab.import_objects([(class_name, object_name)])
            db_emlab.import_data({'object_parameters': [[class_name, object_parameter_value_name]]})
            db_emlab.import_alternatives([str(0)])
            db_emlab.import_object_parameter_values([(class_name, object_name, object_parameter_value_name, 0, '0')])
            db_emlab.import_object_parameter_values([(class_name, object_name, "CurrentYear", StartYear, '0')])
            db_emlab.import_object_parameter_values([(class_name, object_name, object_parameter_value_name, 0, '0')])

            update_years_file(StartYear, StartYear, final_year, lookAhead)
            db_emlab.commit('Clock intialization')
            print('Done initializing clock (tick 0)')

            if available_years_data == True:
                prepare_AMIRIS_data(StartYear, 0, fix_demand_to_initial_year, fix_profiles_to_initial_year,
                                    "initialize")
            else:  # no dynamic data for other cases
                prepare_AMIRIS_data_for_one_year()


        if sys.argv[2] == 'increment_clock':  # increment clock

            if targetinvestment_per_year == True:
                reset_target_investments_done()
                print(" target investments status")

            # if test_first_intermittent_technologies == True:
            #     reset_testing_intermittent_technologies()
            step = next(int(i['parameter_value']) for i
                        in
                        db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name) \
                        if i['parameter_name'] == 'Time Step')

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

            if updated_year >= final_year:
                print("final year achieved " + str(final_year))
                # updating file to stop simulation.
                update_years_file(updated_year, StartYear, final_year,
                                  lookAhead)
                # todo need to update the file to make the loop stop. spinetoolbox dont advance for last tick

            else:
                update_years_file(updated_year, StartYear, final_year, lookAhead)
                db_emlab.import_object_parameter_values(
                    [(class_name, object_name, object_parameter_value_name, new_tick, '0')])
                db_emlab.import_object_parameter_values([(class_name, object_name, "CurrentYear", updated_year, '0')])
                db_emlab.commit('Clock increment')
                print('Done incrementing clock (tick +' + str(step) + '), resetting invest file and years file')

            if available_years_data == True:
                prepare_AMIRIS_data(updated_year, new_tick, fix_demand_to_initial_year,
                                    fix_profiles_to_initial_year,
                                    "increment")
                print("prepared AMIRIS data ")
            else:  # no dynamic data for other cases
                print("no dynamic data for this country")

except Exception:
    raise
finally:
    db_emlab.close_connection()

print('removing awaiting bids...')
db_map = DatabaseMapping(db_url)

if sys.argv[2] == 'increment_clock':
    try:
        subquery = db_map.object_parameter_value_sq
        statuses = {row.object_id: from_database(row.value, row.type) for row in
                    db_map.query(subquery).filter(subquery.c.parameter_name == "status")}
        removable_object_ids = {object_id for object_id, status in statuses.items() if status == "Awaiting"}
        db_map.cascade_remove_items(object=removable_object_ids)
        print("removed awaiting bids")
        db_map.commit_session("Removed unacceptable objects.")
    finally:
        db_map.connection.close()

# hasnt worked as function
# def erase_not_accepted_bids(db_url):
#     print("removing awaiting bids")
#     db_map = DatabaseMapping(db_url)
#
#     try:
#         subquery = db_map.object_parameter_value_sq
#         statuses = {row.object_id: from_database(row.value, row.type) for row in
#                     db_map.query(subquery).filter(subquery.c.parameter_name == "status")}
#         removable_object_ids = {object_id for object_id, status in statuses.items() if status == "Awaiting"}
#         db_map.cascade_remove_items(object=removable_object_ids)
#         print("removed awaiting bids")
#         db_map.commit_session("Removed unacceptable objects.")
#     finally:
#         db_map.connection.close()


# todo finish this if bids are being erased then the awarded capapcity of CM should also be saved.
#
# def class_id_for_name(name):
#     return db_map.query(db_map.entity_class_sq).filter(db_map.entity_class_sq.c.name == name).first().id
# try:
#     id_to_remove = class_id_for_name("Bids")
#     db_map.cascade_remove_items(**{"object_class": {id_to_remove}})
#     db_map.commit_session("Removed ")
# finally:
#     db_map.connection.close()

"""
This file contains all interactions with the system clock.
A tick is one year.
For the initialization. make current year the start year and the Simulation tick 0
for the increment clock, add a tick to SimulationTick and a year to current year

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
#dirname(dirname(dirname(realpath(os.getcwd()))))

db_url = sys.argv[1]
db_emlab = SpineDB(db_url)
from spinedb_api import DatabaseMapping, from_database

grandparentpath =  dirname(dirname(realpath(os.getcwd())))
parentpath =  os.path.dirname(os.getcwd())

amiris_ouput_path =  os.path.join(grandparentpath,'amiris_workflow\\output\\')

load_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\load.csv')
future_load_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\future_load.csv' )

input_yearly_profiles_demand = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\NLVREprofilesandload2019-2050.xlsx')
windon_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\windon.csv')
future_windon_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\future_windon.csv' )
windoff_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\windoff.csv')
future_windoff_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\future_windoff.csv' )
pv_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\pv.csv')
future_pv_file_for_amiris = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\future_pv.csv' )

def reset_candidate_investable_status():
    class_name = "CandidatePowerPlants"
    candidate_powerplants = [i for i in db_emlab.query_object_parameter_values_by_object_class(class_name)]
    for candidate in candidate_powerplants:
        db_emlab.import_object_parameter_values(
            [(class_name, candidate["object_name"], "ViableInvestment", bool(1), '0')])


def update_years_file(current_year, initial, final_year, lookAhead):
    print("updated years file")
    # once the spine bug is fixed. then it can be exported to the output folder.
    # the clock is executed in the util folder. So save the results in the parent folder: emlabpy
    complete_path = os.path.join(os.path.dirname(os.getcwd()), globalNames.years_file)
    f = open(complete_path, "w")
    years_str = str(current_year) + "/" + str(initial) + "/" + str(final_year) + "/" + str(current_year + lookAhead)
    f.write(years_str)
    f.close()


def erase_not_accepted_bids(db_url):
    print("removing awaiting bids")
    db_map = DatabaseMapping(db_url)

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


# erase not Accepted bids from capacity mechanisms
# erase_not_accepted_bids(db_url)
def prepare_AMIRIS_data(year, future_year):
    print("preparing data for years " + str(year) + " and " + str(future_year) + " for NL")
    try:
        excel_NL = pd.read_excel(input_yearly_profiles_demand, index_col=0,
                                 sheet_name=["NL Wind Onshore profiles",
                                             "NL Wind Offshore profiles",
                                             "NL Sun PV profiles",
                                             "Load Profile"])

        print("finish reading  excel")
        demand = excel_NL['Load Profile'][year]
        demand.to_csv(load_file_for_amiris, header=False, sep=';', index=True)
        future_demand = excel_NL['Load Profile'][future_year]
        future_demand.to_csv(future_load_file_for_amiris, header=False, sep=';', index=True)

        wind_onshore = excel_NL['NL Wind Onshore profiles'][year]
        future_wind_onshore = excel_NL['NL Wind Onshore profiles'][future_year]
        wind_onshore.to_csv(windon_file_for_amiris, header=False, sep=';', index=True)
        future_wind_onshore.to_csv(future_windon_file_for_amiris, header=False, sep=';', index=True)

        wind_offshore = excel_NL['NL Wind Offshore profiles'][year]
        future_wind_offshore = excel_NL['NL Wind Offshore profiles'][future_year]
        wind_offshore.to_csv(windoff_file_for_amiris, header=False, sep=';', index=True)
        future_wind_offshore.to_csv(future_windoff_file_for_amiris, header=False, sep=';', index=True)

        pv = excel_NL['NL Sun PV profiles'][year]
        future_pv = excel_NL['NL Sun PV profiles'][future_year]
        pv.to_csv(pv_file_for_amiris, header=False, sep=';', index=True)
        future_pv.to_csv(future_pv_file_for_amiris, header=False, sep=';', index=True)
    except Exception as e:
        print("failed updating AMIRIS data")
        print(e)

    return 0

def prepare_AMIRIS_data_fromDE():
    print("preparing DE data")
    load_path_DE = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\load_DE.csv')
    pv_path_DE = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\pv_DE.csv')
    windon_path_DE = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\windon_DE.csv')
    windoff_path_DE = os.path.join(grandparentpath, 'amiris_workflow\\amiris-config\\data\\windoff_DE.csv')
    demand = pd.read_csv(load_path_DE,  delimiter= ";", header=None)
    demand.to_csv(load_file_for_amiris, header=False, sep=';', index=False)
    wind_onshore = pd.read_csv(windon_path_DE,  delimiter= ";", header=None)
    wind_onshore.to_csv(windon_file_for_amiris, header=False, sep=';', index=False)
    wind_offshore = pd.read_csv(windoff_path_DE,  delimiter= ";", header=None)
    wind_offshore.to_csv(windoff_file_for_amiris, header=False, sep=';', index=False)
    pv = pd.read_csv(pv_path_DE,  delimiter= ";", header=None)
    pv.to_csv(pv_file_for_amiris, header=False, sep=';', index=False)

try:
    class_name = "Configuration"
    object_name = 'SimulationYears'
    object_parameter_value_name = 'SimulationTick'
    print(os.getcwd())
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

        reset_candidate_investable_status()
        print("reset power plants status")

        if sys.argv[2] == 'initialize_clock':
            print('delete excels in output')
            path = amiris_ouput_path
            try: # removing excels from previous rounds
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

        if sys.argv[2] == 'increment_clock':
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
                update_years_file(updated_year, StartYear, final_year,
                                  lookAhead)  # need to update the file to make the loop stop
            else:
                db_emlab.import_object_parameter_values(
                    [(class_name, object_name, object_parameter_value_name, new_tick, '0')])
                db_emlab.import_object_parameter_values([(class_name, object_name, "CurrentYear", updated_year, '0')])
                update_years_file(updated_year, StartYear, final_year, lookAhead)
                db_emlab.commit('Clock increment')
                print('Done incrementing clock (tick +' + str(step) + '), resetting invest file and years file')

    else:
        print('No mode specified.')

    if sys.argv[2] == 'initialize_clock':
        future_year = StartYear + lookAhead
        if Country == "NL":
            prepare_AMIRIS_data(StartYear, future_year)
        elif Country == "DE": # no dynamic data for other cases
            prepare_AMIRIS_data_fromDE()
        else:
            raise Exception("no data for this country " + Country)
    else:
        if Country == "NL":
            future_year = updated_year + lookAhead
            prepare_AMIRIS_data(updated_year, future_year)
        elif Country == "DE": # no dynamic data for other cases
            print("no dynamic data for other DE")
        else:
            raise Exception("no data for this country " + Country)

except Exception:
    raise
finally:
    print('Closing DB Connections...')
    db_emlab.close_connection()

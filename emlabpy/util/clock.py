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
import csv
import os
db_url = sys.argv[1]
db_emlab = SpineDB(db_url)

def reset_candidate_investable_status():
    class_name = "CandidatePowerPlants"
    candidate_powerplants = [i for i in db_emlab.query_object_parameter_values_by_object_class(class_name)]
    for candidate in candidate_powerplants:
        db_emlab.import_object_parameter_values([(class_name, candidate["object_name"] , "ViableInvestment",  bool(1) , '0')])

def update_years_file(current_year , lookAhead, final_year):
    fieldnames = ['current', 'future', "final"]
    print("updated years file")
    #TODO dont hard code the path, once the spine bug is fixed. then it can be exported to the output folder.
    # the clock is executed in the util folder. So save the results in the parent folder: emlabpy
    complete_path =  os.path.join(os.path.dirname(os.getcwd()),  globalNames.years_path)
    with open(complete_path, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter ='/')
        csvwriter.writerow([current_year, (current_year + lookAhead), final_year])

try:
    class_name = "Configuration"
    object_name = 'SimulationYears'
    object_parameter_value_name = 'SimulationTick'

    if len(sys.argv) >= 2:
        lookAhead = next(int(i['parameter_value']) for i
                         in db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name ) \
                         if i['parameter_name'] == "Look Ahead")
        final_year = next(int(i['parameter_value']) for i
                          in db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name ) \
                          if i['parameter_name'] == "End Year")
        StartYear = next(int(i['parameter_value']) for i in db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name) \
                         if i['parameter_name'] == 'Start Year')

        reset_candidate_investable_status()
        print("reset power plants status")

        if sys.argv[2] == 'initialize_clock':
            print('Initializing clock (tick 0)')
            db_emlab.import_object_classes([class_name])
            db_emlab.import_objects([(class_name, object_name)])
            db_emlab.import_data({'object_parameters': [[class_name, object_parameter_value_name]]})
            db_emlab.import_alternatives([str(0)])
            db_emlab.import_object_parameter_values([(class_name, object_name, object_parameter_value_name, 0, '0')])

            db_emlab.import_object_parameter_values([(class_name, object_name, "CurrentYear", StartYear, '0')])
            db_emlab.import_object_parameter_values([(class_name, object_name, object_parameter_value_name, 0, '0')])

            update_years_file(StartYear , lookAhead, final_year)
            db_emlab.commit('Clock intialization')
            print('Done initializing clock (tick 0)')

        if sys.argv[2] == 'increment_clock':

            step = next(int(i['parameter_value']) for i
                        in db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name) \
                        if i['parameter_name'] == 'Time Step')

            previous_tick = next(int(i['parameter_value']) for i
                                 in db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name) \
                                 if i['parameter_name'] == object_parameter_value_name)

            new_tick = step + previous_tick
            print('Incrementing Clock to ' + str(new_tick))

            Current_year = next(int(i['parameter_value']) for i in db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name) \
                                if i['parameter_name'] == 'CurrentYear')
            updated_year = step + Current_year
            if updated_year >= final_year:
                print("final year achieved" + str(final_year))
            else:
                db_emlab.import_object_parameter_values([(class_name, object_name, object_parameter_value_name, new_tick, '0')])
                db_emlab.import_object_parameter_values([(class_name, object_name, "CurrentYear", updated_year, '0')])
                update_years_file(updated_year , lookAhead, final_year)
                db_emlab.commit('Clock increment')
                print('Done incrementing clock (tick +' + str(step) + '), resetting invest file and years file')
    else:
        print('No mode specified.')
except Exception:
    raise
finally:
    print('Closing DB Connections...')
    db_emlab.close_connection()

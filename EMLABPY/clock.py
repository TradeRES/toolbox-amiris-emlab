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

db_url = sys.argv[1]
db_emlab = SpineDB(db_url)

try:
    class_name = "Configuration"
    object_name = 'SimulationYears'
    object_parameter_value_name = 'SimulationTick'

    if len(sys.argv) >= 2:
        if sys.argv[2] == 'initialize_clock':
            print('Initializing clock (tick 0)')
            db_emlab.import_object_classes([class_name])
            db_emlab.import_objects([(class_name, object_name)])
            db_emlab.import_data({'object_parameters': [[class_name, object_parameter_value_name]]})
            db_emlab.import_alternatives([str(0)])
            db_emlab.import_object_parameter_values([(class_name, object_name, object_parameter_value_name, 0, '0')])
            StartYear = next(int(i['parameter_value']) for i in db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name) \
                             if i['parameter_name'] == 'Start Year')
            db_emlab.import_object_parameter_values([(class_name, object_name, "CurrentYear", StartYear, '0')])
            db_emlab.import_object_parameter_values([(class_name, object_name, object_parameter_value_name, 0, '0')])
            #todo ERASE this when DB is complete
            db_emlab.import_data({'object_parameters': [["unit",  "efficiency_full_load"]]})
            db_emlab.import_object_parameter_values([("unit", "Hydropower_ROR", "efficiency_full_load", 0.7, '0')])

            db_emlab.commit('Clock intialization')
            print('Done initializing clock (tick 0)')

        if sys.argv[2] == 'increment_clock':

            step = next(int(i['parameter_value']) for i
                        in db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name) \
                        if i['parameter_name'] == 'Time Step')

            print('Incrementing Clock (tick +' + str(step) + ')')
            previous_tick = next(int(i['parameter_value']) for i
                                 in db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name) \
                                 if i['parameter_name'] == object_parameter_value_name)

            new_tick = step + previous_tick
            Current_year = next(int(i['parameter_value']) for i in db_emlab.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name) \
                                if i['parameter_name'] == 'CurrentYear')
            updated_year = step + Current_year
            db_emlab.import_object_parameter_values([(class_name, object_name, object_parameter_value_name, new_tick, '0')])
            db_emlab.import_object_parameter_values([(class_name, object_name, "CurrentYear", updated_year, '0')])
            db_emlab.commit('Clock increment')
            print('Done incrementing clock (tick +' + str(step) + ')')


    else:
        print('No mode specified.')
except Exception:
    raise
finally:
    print('Closing DB Connections...')
    db_emlab.close_connection()

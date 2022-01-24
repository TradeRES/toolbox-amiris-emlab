"""
This file contains all interactions with the system clock.
A tick is one year.

Jim Hommes - 7-4-2021
"""
import sys
from util.spinedb import SpineDB

db_url = sys.argv[1]
db_config_url = sys.argv[2]
db_emlab = SpineDB(db_url)
db_parameters = SpineDB(db_config_url)

try:
    object_name = 'SystemClockTicks'
    object_parameter_value_name = 'ticks'

    if len(sys.argv) >= 3:
        if sys.argv[3] == 'initialize_clock':
            print('Initializing clock (tick 0)')
            db_emlab.import_object_classes([object_name])
            db_emlab.import_objects([(object_name, object_name)])
            db_emlab.import_data({'object_parameters': [[object_name, object_parameter_value_name]]})
            db_emlab.import_alternatives([str(0)])
            db_emlab.import_object_parameter_values([(object_name, object_name, object_parameter_value_name, 0, '0')])
            db_emlab.commit('Clock intialization')
            print('Done initializing clock (tick 0)')

        if sys.argv[3] == 'increment_clock':
            step = next(int(i['parameter_value']) for i
                        in db_parameters.query_object_parameter_values_by_object_class('Coupling Parameters')
                        if i['object_name'] == 'Time Step')
            print('Incrementing Clock (tick +' + str(step) + ')')
            previous_tick = max([int(i['parameter_value']) for i
                                 in db_emlab.query_object_parameter_values_by_object_class('SystemClockTicks')])

            new_tick = step + previous_tick
            db_emlab.import_alternatives([str(new_tick)])
            db_emlab.import_object_parameter_values([(object_name, object_name, object_parameter_value_name, new_tick,
                                                      str(new_tick))])
            db_emlab.commit('Clock increment')
            print('Done incrementing clock (tick +' + str(step) + ')')
    else:
        print('No mode specified.')
except Exception:
    raise
finally:
    print('Closing DB Connections...')
    db_emlab.close_connection()
    db_parameters.close_connection()

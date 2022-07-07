# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 10:37:40 2021

This script is responsible for running COMPETES by connecting through the DataExchange library that AIMMS offers.
In AIMMS, StartHTTPService has to be running. This means AIMMS is ready to receive REST requests.

Arg1: path to EMLAB SpineDB
Arg2: AIMMS Service Name given to Procedure that runs COMPETES

@author: hernandezsernar
@author: Jim Hommes
"""

import requests
import time
import sys
from spinedb import SpineDB
from helper_functions import get_current_ticks

print('===== Starting COMPETES Execution =====')
print('Read current year from SpineDB...')
db_emlab = SpineDB(sys.argv[1])
db_config = SpineDB(sys.argv[2])
try:
    db_config_parameters = db_config.query_object_parameter_values_by_object_class('Coupling Parameters')
    start_simulation_year = next(int(i['parameter_value']) for i in
                                 db_config_parameters if i['object_name'] == 'Start Year')
    look_ahead = next(int(i['parameter_value']) for i in db_config_parameters if i['object_name'] == 'Look Ahead')
    current_emlab_tick, current_competes_tick, current_competes_tick_rounded = get_current_ticks(db_emlab,
                                                                                                 start_simulation_year)
finally:
    db_emlab.close_connection()
    db_config.close_connection()

aimms_service_name = sys.argv[3]
print('Running AIMMS service ' + aimms_service_name)
port = 8080
url = 'http://localhost'

include_look_ahead = sys.argv[4] == 'true'
print('Add Look Ahead to execution year: ' + str(include_look_ahead))
execution_year = current_competes_tick
if include_look_ahead:
    execution_year += look_ahead

print('Sending HTTP Request to AIMMS year ' + str(execution_year))
result = requests.post(url + ':' + str(port) + '/api/v1/tasks/' + aimms_service_name + '?InputYear=' +
                       str(execution_year))
print('Response Code: ' + str(result.status_code))
print('Response Body: ' + result.text)
request_id = result.json()['id']
print('Activity ID: ' + request_id)

status = requests.get(url + ':' + str(port) + '/api/v1/tasks/' + request_id)
print(status.json())
while status.json()['status'] != 'finished' and status.json()['status'] != 'interrupted':
    print('Current status: ' + status.json()['status'] + ', t=' + str(status.json()['runtime']))
    time.sleep(20)
    status = requests.get(url + ':' + str(port) + '/api/v1/tasks/' + request_id)
print('Done')
print('Response Code: ' + str(status.status_code))
print('Response Body: ' + status.text)
print('===== End of COMPETES Execution =====')

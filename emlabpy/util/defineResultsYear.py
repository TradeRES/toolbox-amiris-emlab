import sys
from util.spinedb import SpineDB
import pandas as pd
from util import globalNames
import os

db_url = sys.argv[1]
db_amiris = SpineDB(db_url)
years_file = os.path.join(os.path.dirname(os.getcwd()), globalNames.years_file)
f = open(years_file, "r")
years_str = f.read()
f.close()
years = years_str.split("/")
current_year = years[0]

try:
    class_name = "PowerPlantDispatchPlans"
    db_amiris.import_object_classes([current_year])
    db_amiris.import_alternatives([str(0)])
    db_amiris.import_data({'object_parameters': [[current_year, "REVENUES_IN_EURO"]]})
    db_amiris.import_data({'object_parameters': [[current_year, "VARIABLE_COSTS_IN_EURO"]]})
    db_amiris.import_data({'object_parameters': [[current_year, "PRODUCTION_IN_MWH"]]})
    latest_plants = db_amiris.query_object_parameter_values_by_object_class(class_name)

    for plant in latest_plants:
        db_amiris.import_objects([(current_year, plant["object_name"])])
        db_amiris.import_object_parameter_values([(current_year, plant["object_name"] , plant["parameter_name"],  int(plant["parameter_value"] ),'0' )])
    db_amiris.commit('year changed')
    print('Done Changing year')
except Exception:
    raise
finally:
    print('Closing DB Connections')
    db_amiris.close_connection()

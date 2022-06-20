import sys
from util.spinedb import SpineDB
import pandas as pd
import globalNames

years = pd.read_csv(globalNames.years_path, delimiter ='/')
current_year = years.columns[0]
future_year = years.columns[1]
db_url = sys.argv[1]
db_amiris = SpineDB(db_url)

try:
    class_name = "PowerPlantDispatchPlans"
    db_amiris.import_object_classes([current_year])
    db_amiris.import_alternatives([str(0)])
    db_amiris.import_data({'object_parameters': [[current_year, "REVENUES_IN_EURO"]]})
    db_amiris.import_data({'object_parameters': [[current_year, "VARIABLE_COSTS_IN_EURO"]]})
    db_amiris.import_data({'object_parameters': [[current_year, "PRODUCTION_IN_MWH"]]})
    latest_plants = db_amiris.query_object_name_by_class_name_and_alternative(class_name, "latest")

    for plant in latest_plants:
        db_amiris.import_objects([(current_year, plant["object_name"])])

        db_amiris.import_object_parameter_values([(current_year, plant["object_name"] , "REVENUES_IN_EURO",  plant["parameter_value"] , str(0) ),
                                                  (current_year, plant["object_name"] , "VARIABLE_COSTS_IN_EURO",   plant["parameter_value"], str(0) ),
                                                  (current_year, plant["object_name"], "PRODUCTION_IN_MWH",   plant["parameter_value"] , str(0))
                                                  ])
    db_amiris.commit('year changed')
    print('Done Changing year')
except Exception:
    raise
finally:
    print('Closing DB Connections...')
    db_amiris.close_connection()

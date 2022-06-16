import sys
from util.spinedb import SpineDB
import pandas as pd
filename = "C:\\Users\\isanchezjimene\\Documents\\TraderesCode\\toolbox-amiris-emlab\\data\\years.csv"
years = pd.read_csv(filename, delimiter ='/')
current_year = years.columns[0]
future_year = years.columns[1]
db_url = sys.argv[0]
db_amiris = SpineDB(db_url)

try:
    class_name = "PowerPlantDispatchPlans"
    object_name = 'SimulationYears'
    object_parameter_value_name = 'SimulationTick'
    latest_plants = [i for i in db_amiris.query_object_parameter_values_by_class_name_and_alternative(class_name, "latest")]
    for plant in latest_plants:
        db_amiris.import_object_parameter_values([(class_name, plant["object_name"] , "REVENUES_IN_EURO",   current_year)])
        db_amiris.import_object_parameter_values([(class_name, plant["object_name"] , "VARIABLE_COSTS_IN_EURO",   current_year)])
        db_amiris.import_object_parameter_values([(class_name, plant["object_name"], "PRODUCTION_IN_MWH",  current_year)])

    db_amiris.commit('year changed')
    print('Done Changing year')
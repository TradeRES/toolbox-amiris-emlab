#from emlabpy.util.spinedb import SpineDB
# import sys
#
# db_url = sys.argv[1]
# db_emlab = SpineDB(db_url)
#
# object_parameter_value_name = "Status"
# try:
#     class_name = 'financialPowerPlantReports'
#     object_name = 'SimulationYears'
#     object_parameter_value_name = 'SimulationTick'
#     object_class_name_list = ['ConventionalPlantOperator', 'VariableRenewableOperator']
#     powerPlants = db_emlab.query_object_parameter_values_by_object_classes(object_class_name_list)
#     currentYear = db_emlab.query_object_parameter_values_by_object_class_and_object_name("Configuration", "CurrentYear")
#     commissioned = None
    # for i in powerPlants:
    #     if i["parameter_name"]= 'ComissionedYear':
    #         commissioned = i['parameter_value']
    #         if commissioned < currentYear:
#
# db_emlab.import_data({'object_parameters': [[class_name, object_parameter_value_name]]})
#     db_emlab.import_alternatives([str(0)])
#
#
#     def set_status_of_power_plants(self):
#         pass
#
# except Exception:
#     raise
# finally:
#     print('Closing DB Connections...')
#     db_emlab.close_connection()
data = [1,2,3]
#print("{\"type\":\"time_series\", \"data\": %d ]}" %  )
print('{"type":"time_series", "data":'  + str(data) + '}')
# from spinedb_api import DatabaseMapping, from_database, Map, to_database
# import spinedb_api.import_functions as im
# import math  # Optional
# import numpy as np  # Optional

# Add data to the database
# initial_peak_load = Map([2020.0, 2050.0], [11111, 00000])
# class_name = "ElectricitySpotMarkets"
# object_name = "ElectricitySpotMarketNL"
# parameter_name = "peakLoadFixed"
# alternative_name = str(0)
#
# url = "sqlite:///C:\\toolbox-amiris-emlab\\.spinetoolbox\\items\\emlabdb\\EmlabDB.sqlite" # Use in-memory database
# db_map = DatabaseMapping(url)  # Remove create=True if the database exists
# im.import_object_classes(db_map, [class_name])
# im.import_objects(db_map, [(class_name, object_name)])
# im.import_object_parameters(db_map, [(class_name, parameter_name)])
# im.import_alternatives(db_map, [alternative_name])
# im.import_object_parameter_values(
#     db_map,
#     [(class_name, object_name, parameter_name, initial_peak_load, alternative_name)],
# )
# db_map.commit_session("Add initial data.")
# def make_unique(lst):
#     result = []
#     for item in lst:
#         if item in result:
#             new    = item + 1
#             result.append(new)
#         else:
#             result.append(item)
#     return result
#
# # Example usage:
# my_list = [1, 2, 3, 4, 4, 5, 6, 6, 6]
# unique_list = make_unique(my_list)
# print(unique_list)



import pandas as pd

# create a dataframe
# with 3 rows amd 3  columns
record = {'Math': [10, 20, 30,
                   40, 70],
          'Science': [40, 50, 60,
                      90, 50],
          'English': [70, 80, 66,
                      75, 88]}
df = pd.DataFrame(record)

My_list = [1,2,3,4,5]

for i in My_list:
    print(i)
    df.at[0, "English"] += i
    print(df)


# from domain.import_object import *
# from twine.repository import Repository
#
# reps = Repository()
#
# class I(ImportObject):
#     def __init__(self, name):
#         super().__init__(name)
#         self.invested = {}
#         self.project_value_year =  {}
#
#     def add_parameter_value(self, parameter_name: str, parameter_value, alternative: str):
#         print( parameter_name, parameter_value, alternative)
#         year, iteration = parameter_name.split('-')
#         if alternative == "Invested":
#             # if year not in self.invested.keys():
#             #     self.invested[year] = 1
#             # else:
#             #     self.invested[year] += 1
#             quit()
#         else:
#             if year not in self.project_value_year.keys():
#                 self.project_value_year[year] = [parameter_value]
#             else:
#                 self.project_value_year[year].append(parameter_value)
#
# test = I(1)
# test.add_parameter_value( "2020-1", 213123, "Invested")
# test.add_parameter_value( "2020-1", 213123, 0)
# test.add_parameter_value( "2020-1", 213123, "Invested")
# test.add_parameter_value( "2020-1", 213123, 0)





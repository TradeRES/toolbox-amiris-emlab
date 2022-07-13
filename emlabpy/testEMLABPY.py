import matplotlib.pyplot as plt
import pandas as pd
import pandas as pd
import os
import sys


record1= {'Math': list(range(100))}

record2= {'Math': [0,0,0,0,0],
          'Science': [0,0,0,0,0],
          'English': [0,0,0,0,100000]}


def plot_investments_per_iteration(candidate_plants_project_value, installed_capacity_per_iteration,
                                    ):
    print('project values')
    fig8, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot( candidate_plants_project_value )
    ax2.plot(installed_capacity_per_iteration , 'o')
    ax1.set_xlabel('Iterations', fontsize='medium')
    ax1.set_ylabel('Project value', fontsize='medium')
    ax2.set_ylabel('Investments', fontsize='medium')
    ax1.set_title('Investments and project value per iterations')
    ax1.legend( candidate_plants_project_value.columns.values.tolist())
    print(candidate_plants_project_value.columns)

candidate_plants_project_value = pd.DataFrame(record1)
installed_capacity_per_iteration =  pd.DataFrame(record2)
plot_investments_per_iteration(candidate_plants_project_value, installed_capacity_per_iteration )
print('Showing plots...')
plt.show()


# from domain.import_object import *
# from twine.repository import Repository
#
# reps = Repository()
#
# class I(ImportObject):
#     def __init__(self, name):
#         super().__init__(name)
#         self.invested_in_iteration = {}
#         self.project_value_year =  {}
#
#     def add_parameter_value(self, parameter_name: str, parameter_value, alternative: str):
#         print( parameter_name, parameter_value, alternative)
#         year, iteration = parameter_name.split('-')
#         if alternative == "Invested":
#             # if year not in self.invested_in_iteration.keys():
#             #     self.invested_in_iteration[year] = 1
#             # else:
#             #     self.invested_in_iteration[year] += 1
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





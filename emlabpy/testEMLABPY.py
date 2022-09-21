import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys
from functools import reduce
import pandas as pd
from matplotlib.offsetbox import AnchoredText
# start = 117000 *256
# age = 26
# lifetime =25
# growth_rate = 0.001
# after_life_growth_rate = 0.05
# after_life = pow(1 + growth_rate, lifetime) * start
# print(after_life)
# data = [(1,'sravan'),(2,'ojaswi'),
#         (3,'bobby'),(4,'rohith'),
#         (5,'gnanesh')]
#
# years_to_generate = list(range(1,10))
# hours = np.array(list(range(1,10)))
#
# df = pd.DataFrame(index = hours)
# df.loc[hours <= 4, 'equal_or_lower_than_4?'] = 'True'
#
# np.array(list(range(1,10)))
# dos = np.array(list(range(1,10)))
# for i in range(1, 4):
#     df["dos"+ str(i)] = dos * 3
# df.plot()
# plt.show()
#
#
# df.index.name = "key"
# df = pd.DataFrame({"A": [5, 3, None, 4],
#                    "B": [None, 2, 4, 3],
#                    "C": [4, 3, 8, 5],
#                    "D": [5, 4, 2, None]})
# aaa = pd.Series([3,4], index=[3 ,4 ])
# df["E" ] = aaa
# print(df)
# other = pd.DataFrame({'key': [1, 2, 5],
#                       'B': ['B0', 'B1', 'B2']})
# ssd = pd.DataFrame({'key': [1, 2, 3],
#                       'C': ['B0', 'B1', 'B2']})

# other.set_index('key')
# ssd.set_index('key')
# df = pd.merge(df, other,   on='key', how='inner')
# df = pd.merge(df, ssd,   on='key', how='inner')
# df.join(ssd, how='left')
# print(df)
# merged_df = reduce(lambda df, other: pd.merge(df, other, on='date', how='inner'), dfs)
#
#
record1 = {'Math': list(range(100))}

record2 = {'Math': [0, 0, 0, 0, 0],
           'Science': [0, 0, 0, 0, 0],
           'English': [0, 0, 0, 0, 100000]}
def plot_investments_per_iteration(candidate_plants_project_value, installed_capacity_per_iteration,
                                   ):
    print('project values')
    fig8, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.annotate('figure fraction',
                 xy=(.025, 1), xycoords='figure fraction',
                 horizontalalignment='left', verticalalignment='top',
                 fontsize='medium')

    ax1.plot(candidate_plants_project_value)
    ax2.plot(installed_capacity_per_iteration, 'o')
    ax1.set_xlabel('Iterations', fontsize='medium')
    ax1.set_ylabel('Project value', fontsize='medium')
    ax2.set_ylabel('Investments', fontsize='medium')
    ax2.set_title('Expected future operational (wholesale market) profits \n in year')
    ax1.legend(candidate_plants_project_value.columns.values.tolist(), fontsize='medium', loc='upper left', bbox_to_anchor=(1, 0.9))
    print(candidate_plants_project_value.columns)


candidate_plants_project_value = pd.DataFrame(record1)
installed_capacity_per_iteration = pd.DataFrame(record2)
plot_investments_per_iteration(candidate_plants_project_value, installed_capacity_per_iteration)
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

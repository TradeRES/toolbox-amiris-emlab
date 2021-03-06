import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys
from functools import reduce
import pandas as pd


years_file = os.path.join(os.getcwd(), "years.txt")
f = open(years_file, "r")
years_str = f.read()
years = years_str.split("/")
# exit(1 if continue_str == "False" else 0)
# years = pd.read_csv(years_file, delimiter ='/')
print("current", os.getcwd())
current_year = years[0]
start_year = years[1]
final_year = years[2]

length = int(final_year) - int(start_year)
print(current_year, start_year, final_year, length)
print(1 if int(sys.argv[1]) >= length else 0)


years_to_generate = list(range(1,7))
hours = np.array(list(range(1,10)))

df = pd.DataFrame(index = hours)

np.array(list(range(1,10)))
dos = np.array(list(range(1,10)))
for i in range(1, 4):
    df["dos"+ str(i)] = dos * 3
df.plot()
plt.show()


df.index.name = "key"

other = pd.DataFrame({'key': [1, 2, 5],
                      'B': ['B0', 'B1', 'B2']})
ssd = pd.DataFrame({'key': [1, 2, 3],
                      'C': ['B0', 'B1', 'B2']})
other.set_index('key')
ssd.set_index('key')
df = pd.merge(df, other,   on='key', how='inner')
df = pd.merge(df, ssd,   on='key', how='inner')
df.join(ssd, how='left')
print(df)
merged_df = reduce(lambda df, other: pd.merge(df, other, on='date', how='inner'), dfs)


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





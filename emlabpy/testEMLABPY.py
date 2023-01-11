import matplotlib.pyplot as plt
import numpy as np
from util import globalNames
import pandas as pd
import os
import sys
from functools import reduce
import pandas as pd
import math

# df = pd.DataFrame(np.random.randint(0,10,size=(10,2)), columns=["costs", "size"])
#
# years = [2020,"test",2022]
# test = pd.Series(dtype='float64')

#test.at[0]=132489
# test.at[2020]=0
# test.at[2022]=2
# upsampled = test.resample('Y')
# interpolated = upsampled.interpolate(method='linear')



from pandas import datetime
# def parser(x):
#     return datetime.strptime('190'+x, '%Y-%m')
#new = pd.to_datetime()
# test.to_datetime( unit="A")
#resample = new.resample('A')

# number_new_powerplants = math.floor(installedCapacityDeviation / capacity)
# remainder = installedCapacityDeviation % capacity
# a = []
# for i in range(number_new_powerplants):
#     if i == number_new_powerplants -1 :
#         a.append(capacity+remainder )
#     else:
#         a.append(capacity)
#
# candidate_name = [1,2,3]
# newplant = ["1", "2", "3"]
#
# a = zip(newplant, candidate_name)
#
# for i,j in a:
#     print(i)


# start = 117000 *256
# age = 26
# lifetime =25
# growth_rate = 0.001
# after_life_growth_rate = 0.05
# after_life = pow(1 + growth_rate, lifetime) * start
# print(after_life)
#
# s1 = pd.Series([1, 2], index=[1, 2], name='s1')
# s2 = pd.Series([3, 4], index=[2, 3], name='s2')
# mydict =  {'s1': s1, 's2': s2}
# a = pd.DataFrame.from_dict(mydict)
#
# #a = pd.concat([s1, s2], axis=1)
# print(a)

# data = [1,2,5,4]
# data2 = ["A","B", "C", "D"]
# ser = pd.Series(data2, index=data)
# ser.sort_index(inplace = True)
# print(ser)
# name = "asdasdn-asdasd"
# splitname = name.split("-")
# splitname[1]

# path_to_results = os.path.join(os.getcwd(), "plots", "Scenarios", "Results.xlsx")
# years_to_generate = list(range(2020,2030))
# values = list(range(0,10))
#
# new_scenario = "TEst4"
# df = pd.DataFrame(values, index = years_to_generate)
#
# overview_data = pd.read_excel(path_to_results, sheet_name='ENS', index_col=0)
# overview_data[new_scenario] = df
#
# with pd.ExcelWriter(path_to_results,
#                     mode="a",
#                     engine="openpyxl",
#                     if_sheet_exists="overlay") as writer:
#     overview_data.to_excel(writer, sheet_name="ENS")
#     writer.save()
#
# print("done")

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

# aaa = pd.Series([3,4], index=[3 ,4 ])
# df["E" ] = aaa
#
# other = pd.DataFrame({'key': [1, 2, 5],
#                       'B': ['B0', 'B1', 'B2']})
# ssd = pd.DataFrame({'key': [1, 2, 3],
#                       'C': ['B0', 'B1', 'B2']})
# other["years"] = [2020,2021,2022]
# other.set_index('years', inplace=True)
# other.drop(['key'], axis=1, inplace=True)

# ssd.set_index('key')
# df = pd.merge(df, other,   on='key', how='inner')
# df = pd.merge(df, ssd,   on='key', how='inner')
# df.join(ssd, how='left')
# print(df)
# merged_df = reduce(lambda df, other: pd.merge(df, other, on='date', how='inner'), dfs)
#
#




def plot_investments_per_iteration(
                                   ):
    record1 = {'Math': list(range(100))}
    record0 = {'Math': [0, 0, 0, 0, 0],
               'Science': [0, 0, 0, 0, 0],
               'English': [0, 0, 0, 0, 0]}
    record2 = {'Math': [2, 0, 2, 0, 2],
               'Science': [0, 0, 1, 0, 0],
               'English': [0, 0, 1, 0, 1]}

    two = pd.DataFrame(record2)
    zero = pd.DataFrame(record0)
    print(two)
    c = np.cumsum(two.values,axis=0)

    #two = two.cumsum(axis=1)
    print(c)
    do = zero.sub(c)
    four = pd.DataFrame(do)
    fig8, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.annotate('figure fraction',
                 xy=(.025, 1),xycoords='figure fraction',
                 horizontalalignment='left', verticalalignment='top',
                 fontsize='medium')
    n = len(four.columns)
    colors = plt.cm.rainbow(np.linspace(0, 1, n))
    four.plot.area(color = colors)
    ax2.plot(two, 'o')
    ax1.set_xlabel('Iterations', fontsize='medium')
    ax1.set_ylabel('Project value', fontsize='medium')
    ax2.set_ylabel('Investments', fontsize='medium')
    ax2.set_title('Expected future operational (wholesale market) profits \n in year')
    ax1.legend( fontsize='medium', loc='upper left', bbox_to_anchor=(1, 0.9))

plot_investments_per_iteration()
print('Showing plots...')
plt.show()



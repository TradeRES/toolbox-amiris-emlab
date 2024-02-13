import matplotlib.pyplot as plt
import numpy as np
from util import globalNames
import pandas as pd
import os
import sys
from functools import reduce
import pandas as pd
import math

class CapacityMarket:
    """
    The SlopingDemandCurve as required in the CapacityMarket.
    """
    def __init__(self):
        self.irm = 0
        self.lm = 0.05
        self.d_peak = 40 # GW
        self.um = 0.05
        self.price_cap =50000 # eur/MWh
        self.lm_volume = self.d_peak * (1 +  self.irm  -self.lm )
        self.um_volume = self.d_peak * (1 +  self.irm  + self.um )

        self.m = self.price_cap / (self.um_volume - self.lm_volume)

    def get_price_at_volume(self, volume):
        m = self.price_cap / (self.um_volume - self.lm_volume)
        if volume < self.lm_volume:
            return self.price_cap
        elif self.lm_volume <= volume <= self.um_volume:
            return self.price_cap - m * (volume - self.lm_volume)
        elif self.um_volume < volume:
            return 0
    def get_volume_at_price(self, price):
        m = self.price_cap / (self.um_volume - self.lm_volume)
        if price >= self.price_cap:
            raise Exception
        elif price == 0:
            print("BID PRICE IS ZERO")
            raise Exception
            # return None
        else:
            return ((self.price_cap - price) / m) + self.lm_volume
    def clear_market(self, sorted_ppdp):
        clearing_price = 0
        total_supply_volume = 0
        isMarketUndersuscribed = False
        for ppdp in sorted_ppdp:
            # As long as the market is not cleared
            if ppdp["price"] <= self.get_price_at_volume(total_supply_volume + ppdp["amount"]):
                total_supply_volume +=  ppdp["amount"]
                clearing_price =ppdp["price"]
            elif ppdp["price"]  < self.get_price_at_volume(total_supply_volume):
                clearing_price = ppdp["price"] # oversupply accepted at this price
                total_supply_volume = total_supply_volume + ppdp["amount"] # total supply
                # print(ppdp.plant , " partly ACCEPTED ", total_supply_volume, "", clearing_price)
                isMarketUndersuscribed = False
                break
            else:
                if total_supply_volume > self.lm_volume:
                    isMarketUndersuscribed = False
                else:
                    isMarketUndersuscribed = True
                break
        return clearing_price, total_supply_volume, isMarketUndersuscribed

file = "C:\\toolbox-amiris-emlab\\data\\Analysis\\NPV.xlsx"
df = pd.read_excel(file, sheet_name="Sheet2", usecols="B:C")
market = CapacityMarket()
volume = list(range(len(df)))
bids = list(df.T.to_dict().values())


clearing_price, total_supply_volume, isMarketUndersuscribed = market.clear_market(bids)
print("clearing_price")
print(clearing_price)
print("total_supply_volume")
print(total_supply_volume)
print(isMarketUndersuscribed)









df = pd.read_csv("C:\\toolbox-amiris-emlab\\amiris_workflow\\output\\hourly_generation_per_group.csv")
column = df["unit_25000000"]
max_ENS_in_a_row = pd.DataFrame()
for column_name, column_data in df.iteritems():
    continuous_hours = 0  # Counter for continuous hours
    max_continuous_hours = 0  # Counter for maximum continuous hours
    prev_value = 0  # Variable to store the previous value
    filtered = [column_data>0]
    for value in filtered[0]:
        if value == True:
            continuous_hours += 1
        else:
            continuous_hours = 0
        if continuous_hours > max_continuous_hours:
            max_continuous_hours = continuous_hours

    max_ENS_in_a_row.at[0,column_name] =  max_continuous_hours
print(max_ENS_in_a_row)

    #max_continuous_hours[year] = max_continuous_hours





# fp = [3, 2, 0]
# a = np.interp(5, xp, fp)
# b = np.interp([0, 1, 1.5, 2.72, 3.14], xp, fp)
#
# c = np.polyfit(xp, fp, 1)
# f = np.poly1d(c)
# y_new = f(5).astype(int)
# print(y_new)
#
# df = pd.DataFrame(np.random.randn(1, 4),
#                   index=[1],
#                   columns=list(range(0, 8, 2)))
# df1 = df.transpose()
# df1.reset_index().plot.scatter( x = "index" , y = 1)
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

a = pd.Series([3,8], index=[4, 5])
print(a.loc[3,4])

#
# other = pd.DataFrame({'key': [1, 2, 5],
#                       'B': ['B0', 'B1', 'B2']})



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



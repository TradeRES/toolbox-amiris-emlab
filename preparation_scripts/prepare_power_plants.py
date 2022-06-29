import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
"""
This script groups the power plants per age. 
The capacity is summed and the efficiency is weighted averaged
Plants smaller than X MW are grouped with the power plants of the nearest age
Sanchez 15-06-22
"""
country = "DE"
file = "data/dutchGermanPlants2022_from_emla.xlsx"
dataframe = pd.read_excel(file)
dataframe.loc[dataframe['Location'] == country]
min_capacity_to_group = 50

# Group power plants by age and efficiency
dataframe.rename(columns={"Technology traderes": "Technology"}, inplace=True)
dataframe.sort_values(by=['Age'], ascending=True)
techs = dataframe["Technology"].unique()
weighted_eff = lambda x: np.average(x, weights=dataframe.loc[x.index, "Capacity"])
df = dataframe.groupby(["Technology", 'Age'], as_index=False).agg(total_capacity=("Capacity", "sum"),
                                                                  efficiency_weighted_mean=("Efficiency", weighted_eff))


def weighted_avg(values, weights):
   return np.average(values, weights=weights)


# Group power plants by age and efficiency. Plants smaller than 50 MW are grouped with the power plants of the nearest age
alltechs = []
for t in techs:
    small = df.loc[(df['total_capacity'] < min_capacity_to_group) & (df['Technology'] == t)]
    big = df.loc[(df['total_capacity'] >= min_capacity_to_group) & (df['Technology'] == t)]
    for index, row in small.iterrows():
        idx = big['Age'].sub(row.loc['Age']).abs().idxmin()
        # first calculated the weighted efficiency so that the summed capacity doesnt change the results
        values = [row.loc["efficiency_weighted_mean"], big.loc[idx]["efficiency_weighted_mean"]]
        weights = [row.loc["total_capacity"], big.loc[idx]["total_capacity"]]
        efficiency_weighted_mean = weighted_avg(values, weights)
        big.loc[idx, "efficiency_weighted_mean"] = efficiency_weighted_mean
        big.loc[idx, "total_capacity"] = big.loc[idx]["total_capacity"] + row.loc["total_capacity"]
    alltechs.append(big)

final = pd.concat(alltechs, ignore_index=True)
final.rename(columns={"total_capacity": "Capacity", "efficiency_weighted_mean": "Efficiency"} , inplace=True , errors="raise")
final['Location'] = country
final['Owner'] = "Producer1"
final['DischarginEfficiency'] = 0

boxplot = final.boxplot(column=['Age'], by="Technology", rot=90, fontsize=8)
boxplot_capacity = final.boxplot(column=['Capacity'], by="Technology", rot=90, fontsize=8)

boxplot.plot()
boxplot_capacity.plot()
plt.show()
final.to_excel( "data/" + country  +  "_datapower_plants.xlsx")

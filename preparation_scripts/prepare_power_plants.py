import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
"""
This script groups the power plants per age. 
The capacity is summed and the efficiency is weighted averaged
Plants smaller than X MW are grouped with the power plants of the nearest age
Sanchez 15-06-22

"""
technology_colors = {
    'Biomass_CHP_wood_pellets_DH': "green",
    "Biomass_CHP_wood_pellets_PH": "greenyellow",
    'Coal PSC': "black",
    "Fuel oil PGT": "gray",
    'Lignite PSC': "darkgoldenrod",
    'CCGT': "indianred",
    'OCGT': "darkred",
    'Hydropower_reservoir_medium': "darkcyan",
    'PV_utility_systems': "gold",
    'WTG_onshore': "cornflowerblue",
    "WTG_offshore": "navy",
    "Nuclear": "mediumorchid",
    "Hydropower_ROR": "aquamarine",
    "Lithium_ion_battery": "hotpink",
    "Pumped_hydro": "darkcyan",
    "CCGT_CHP_backpressure_DH": "orange"
}
# file = "../data/Power_plants_Ni.xlsx"
# dataframeoriginal = pd.read_excel(file, sheet_name= "extendedNL_updated")
# dataframe = dataframeoriginal.loc[dataframeoriginal['Location'] == country]
# min_capacity_to_group = 600

excel_path =  'C:\\toolbox-amiris-emlab\\data\\Power_plants_Ni.xlsx'
country = "NL"
year = 2019
dataframeoriginal = pd.read_excel(excel_path, sheet_name= "extendedNL_updated", usecols="A:K" )
dictionary = pd.read_excel(excel_path, sheet_name= "Dict", )
dataframe = dataframeoriginal.loc[dataframeoriginal['Location'] == country]
a = dictionary.set_index('Competes').to_dict()['traderes']
dataframe.replace(a, inplace=True)
dataframe["Age"] = year  - dataframe.Year

min_capacity_to_group = 200
# Group power plants by age and efficiency
dataframe.rename(columns={"Technology traderes": "Technology"}, inplace=True)
dataframe.sort_values(by=['Age'], ascending=True)
techs = dataframe["Technology"].unique()
weighted_eff = lambda x: np.average(x, weights=dataframe.loc[x.index, "Capacity"])
weighted_avail = lambda x: np.average(x, weights=dataframe.loc[x.index, "Availability"])

#group all power plants of same age and technology together
df = dataframe.groupby(["Technology", 'Age'], as_index=False).agg(total_capacity=("Capacity", "sum"),
                                                                  efficiency_weighted_mean=("Efficiency", weighted_eff),
                                                                  availability_weighted_mean=("Availability", weighted_avail))
#drop all power plants after year 2020
df = df[df["Age"]>=0]
#group power plants with negative capacity installed before year !
for t in techs:
    negative = df.loc[(df['total_capacity'] < 0) & (df['Technology'] == t)]
    if negative.size>0:
        plants_tech = df.loc[(df['Technology'] == t)]
        index = (df['Age'] == plants_tech['Age'].max()) &  (df['Technology'] == t)
        df.loc[index, "total_capacity"]  = df.loc[index, "total_capacity"]+ negative.total_capacity.sum()
        index2 = df[(df['total_capacity'] < 0) & (df['Technology'] == t)].index
        df.drop(index2, axis=0, inplace=True)
        print("new capacity of oldest plant")
        print(df.loc[(df['Technology'] == t)].total_capacity)


def weighted_avg(values, weights):
   return np.average(values, weights=weights)


# Group power plants by age and efficiency.
# Plants smaller than 50 MW are grouped with the power plants of the nearest age, Efficiency are weighted averaged, capacity is summed.
#If there are only small capacities power plants, then the efficiency and the age are weighted averaged

alltechs = []
for t in techs:
    print(t)
    small = df.loc[(df['total_capacity'] < min_capacity_to_group) & (df['Technology'] == t)]
    big = df.loc[(df['total_capacity'] >= min_capacity_to_group) & (df['Technology'] == t)]
    print("big ", big.size)
    print("small ",small.size)
    if big.size ==0 and small.size > 0:
        big.at[0, "efficiency_weighted_mean"] = np.average(a = small["efficiency_weighted_mean"] , weights = small["total_capacity"])
        big.at[0, "availability_weighted_mean"] = np.average(a = small["availability_weighted_mean"] , weights = small["total_capacity"])
        big.at[0,"Age"] = round(np.average(a = small["Age"] , weights = small["total_capacity"]),0)
        big.at[0,"total_capacity"] = np.sum(small["total_capacity"])
        big.at[0,"Technology"] = t

    else:

        for index, row in small.iterrows():
            # find the row with the nearest age
            if row.loc['Age'] <= 0:
                idx = big['Age'].sub(0).abs().idxmin()
            else:
                idx = big['Age'].sub(row.loc['Age']).abs().idxmin()

            # first calculated the weighted efficiency so that the summed capacity doesnt change the results
            values = [row.loc["efficiency_weighted_mean"], big.loc[idx]["efficiency_weighted_mean"]]
            availability_values = [row.loc["availability_weighted_mean"], big.loc[idx]["availability_weighted_mean"]]
            weights = [row.loc["total_capacity"], big.loc[idx]["total_capacity"]]

            efficiency_weighted_mean = weighted_avg(values, weights)
            availability_weighted_mean = weighted_avg(availability_values, weights)

            big.loc[idx, "availability_weighted_mean"] = availability_weighted_mean
            big.loc[idx, "efficiency_weighted_mean"] = efficiency_weighted_mean
            big.loc[idx, "total_capacity"] = big.loc[idx]["total_capacity"] + row.loc["total_capacity"]

    alltechs.append(big)

final = pd.concat(alltechs, ignore_index=True)
final.rename(columns={"total_capacity": "Capacity", "efficiency_weighted_mean": "Efficiency"} , inplace=True , errors="raise")
final['Location'] = country
final['Owner'] = "Producer" + country
final['cash'] = 0
final['DischarginEfficiency'] = 0


boxplot = final.boxplot(column=['Age'], by="Technology", rot=90, fontsize=8)
boxplot_capacity = final.boxplot(column=['Capacity'], by="Technology", rot=90, fontsize=8)

boxplot.plot()
boxplot_capacity.plot()
plt.show()


sns.set_theme(style="whitegrid")
print("plotted initial power plants")
sns.set(font_scale=1.2)
colors = [technology_colors[tech] for tech in final["Technology"].unique()]

fig1 = sns.relplot(x="Age", y="Efficiency", hue="Technology", size="Capacity",
                   sizes=(40, 400), alpha=.5, palette=colors,
                   height=6, data=final)
plt.xlabel("Age", fontsize="large")
plt.ylabel("Efficiency", fontsize="large")
fig1.savefig('../data/' + 'Initial_power_plants_NL.png', bbox_inches='tight', dpi=300)
plt.close('all')



final.to_excel( "../data/" + country  +  "_datapower_plants.xlsx")

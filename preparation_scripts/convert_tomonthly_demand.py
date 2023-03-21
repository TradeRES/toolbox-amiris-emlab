import os
import pandas as pd
from os.path import dirname, realpath
"""
Demand from competes results. Electric boiler seem to be a bit inverse correlated with H2. 
The optimization either produce H2 or electric boiler
"""
# amiris requires input raw (not electric)
electrolyzer_efficiency = 0.74
boilerefficiency = 0.99
year = 2019 # all data in amiris has this dataseries

parentpath = dirname(realpath(os.getcwd()))
competes_results_path = os.path.join(parentpath,  "data", "competes_ENTSOE","GA_TradeRES_Output_Dynamic_Gen&Trans_2050.xlsx")
monthly_demand_path = os.path.join(parentpath,  "data", "competes_ENTSOE","monthly_H2_heat_demand.xlsx" )

"""
making hourly electricity demand to monthly
"""

df_raw= pd.read_excel(competes_results_path,  sheet_name = "NL Electricity Balance", usecols = "S:T", skiprows =[0])
#supply= pd.read_excel(competes_results_path,  sheet_name = "NL Electricity Balance", usecols = "B:M", skiprows =[0])

hours = pd.Series(pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31 23:00:00', freq='H'))

df_raw['hours'] = hours
df_raw.set_index('hours', inplace=True)
dfdemand = df_raw.resample('730H').sum()
dfdemand.index = dfdemand.index.strftime('%Y-%m-%d_%H:%M:%S')
dfdemand["H2"] = dfdemand["H2"] * electrolyzer_efficiency
# converting demand to H2 demand (raw)
dfdemand["Industrial heat"] = dfdemand["Industrial heat"] / boilerefficiency * electrolyzer_efficiency
dfdemand["total"] = dfdemand["H2"]+ dfdemand["Industrial heat"]
"""
converting 6 hourly H2 prices to monthly
"""
df_prices = pd.read_excel(competes_results_path,  sheet_name = "Hourly Hydrogen Prices", usecols = "K", skiprows =[0])
hours = pd.Series(pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31 23:00:00', freq='6H'))
df_prices.dropna(inplace=True)
df_prices['hours'] = hours
df_prices.set_index('hours', inplace=True)
dfprices = df_prices.resample('730H').mean()

dfprices.index = dfprices.index.strftime('%Y-%m-%d_%H:%M:%S')

with pd.ExcelWriter(monthly_demand_path) as writer:
    dfdemand.to_excel(writer, sheet_name ="demand")
    dfprices.to_excel(writer, sheet_name = "prices")

print("done")
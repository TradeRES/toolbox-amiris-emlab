import os
import pandas as pd
from os.path import dirname, realpath
"""
Demand from competes results. Electric boiler seem to be a bit inverse correlated with H2. 
The optimization either produce H2 or electric boiler
"""

parentpath = dirname(realpath(os.getcwd()))
competes_results_path = os.path.join(parentpath,  "data", "competes_ENTSOE","separate demand profiles.xlsx")
df_raw= pd.read_excel(competes_results_path,  sheet_name = "NL Electricity Balance", usecols = "S:T", skiprows =[0])
#supply= pd.read_excel(competes_results_path,  sheet_name = "NL Electricity Balance", usecols = "B:M", skiprows =[0])
year = 2019
hours = pd.Series(pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31 23:00:00', freq='H'))

df_raw['hours'] = hours
df_raw.set_index('hours', inplace=True)
df = df_raw.resample('730H').sum()
monthly_demand_path = os.path.join(parentpath,  "data", "competes_ENTSOE","monthly_H2_heat_demand.xlsx")
df.to_excel(monthly_demand_path)
print("done")
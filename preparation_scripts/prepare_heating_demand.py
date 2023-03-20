import os
import pandas as pd
from os.path import dirname, realpath
parentpath = dirname(os.getcwd())
heating_demand_path = os.path.join(parentpath, "data", "weatherpotentialNetherlands", "SH_demand_corr.csv")

demand = pd.DataFrame()

heating_demand = pd.read_csv( heating_demand_path, sep =",", index_col = 'utc_timestamp', parse_dates = True )
heating_demand['Year'] = heating_demand.index.year
for year in heating_demand.index.year.unique():
    x =  heating_demand.loc[heating_demand['Year'] == year, :]
    y  = x["SHD"].reset_index(drop=True)
    demand.at[:,year] = y

result_path= os.path.join(parentpath, "data", "weatherpotentialNetherlands",  "heating_demand.csv")
demand.to_csv(result_path, sep=',')
import os
import pandas as pd
from os.path import dirname, realpath

grandparentpath = dirname(dirname(realpath(os.getcwd())))
parentpath = dirname(os.getcwd())
current_wind_data_path = os.path.join(grandparentpath, "data", "potentialNetherlands","ninja_wind_country_NL_current-merra-2_corrected.csv")
df_wind = pd.read_csv( current_wind_data_path, sep =",", index_col = 'time', parse_dates = True ,skiprows = [0,1])
current_pv_data_path = os.path.join(grandparentpath, "data", "potentialNetherlands", "ninja_pv_country_NL_merra-2_corrected.csv")
df_solar = pd.read_csv( current_pv_data_path, sep =",", index_col = 'time', parse_dates = True ,skiprows = [0,1])
#=================================================================================================== offshore
df_wind['Year'] = df_wind.index.year
offshore = pd.DataFrame()
for year in df_wind.index.year.unique():
    x =  df_wind.loc[df_wind['Year'] == year, :]
    y  = x["offshore"].reset_index(drop=True)
    offshore.at[:,year] = y

futureoffshore  = 1.66*offshore
futureoffshore[futureoffshore  > 1] = 1
futureoffshore.drop(futureoffshore.tail(24).index,inplace=True)# because of leap year

result_path_off = os.path.join(grandparentpath, "data", "potentialNetherlands", "CF_2050_offshore.csv")
futureoffshore.to_csv(result_path_off, sep=',')
#=================================================================================================== onshore
onshore = pd.DataFrame()

for year in df_wind.index.year.unique():
    x =  df_wind.loc[df_wind['Year']  == year, :]
    y  = x["onshore"].reset_index(drop=True)
    onshore.at[:,year] = y
# because of
futureonshore  = 1.42*onshore
futureonshore[futureonshore  > 1] = 1
futureonshore.drop(futureonshore.tail(24).index,inplace=True) # because of leap year

result_path_on = os.path.join(grandparentpath, "data", "potentialNetherlands","CF_2050_onshore.csv")
futureonshore.to_csv(result_path_on, sep=',')
#==================================================================================================== PV
pv = pd.DataFrame()
df_solar['Year'] = df_solar.index.year
for year in df_solar.index.year.unique():
    x =  df_solar.loc[df_solar['Year']  == year, :]
    y  = x["national"].reset_index(drop=True)
    pv.at[:,year] = y

pv.drop(pv.tail(24).index,inplace=True)# because of leap year

result_path_on = os.path.join(grandparentpath, "data","potentialNetherlands", "CF_2050_PV.csv")
pv.to_csv(result_path_on, sep=',')
import os
import pandas as pd
from os.path import dirname, realpath

grandparentpath = dirname(dirname(realpath(os.getcwd())))
parentpath = dirname(os.getcwd())

current_wind_onshore_data_path = os.path.join(parentpath,  "data", "competes","scaled_onshore_ninja_wind_country_NL_current-merra-2_corrected.csv")
df_wind_onshore = pd.read_csv( current_wind_onshore_data_path, sep =",", index_col = 'time', parse_dates = True )

current_wind_offshore_data_path = os.path.join(parentpath,  "data", "competes","scaled_offshore_ninja_wind_country_NL_current-merra-2_corrected.csv")
df_wind_offshore = pd.read_csv( current_wind_offshore_data_path, sep =",", index_col = 'time', parse_dates = True )

current_pv_data_path = os.path.join(parentpath, "data", "competes", "scaled_national_ninja_pv_country_NL_merra-2_corrected.csv")
df_pv = pd.read_csv( current_pv_data_path, sep =",", index_col = 'time', parse_dates = True )

df_wind_onshore['Year'] = df_wind_onshore["year"]
onshore = pd.DataFrame()
for year in df_wind_onshore.index.year.unique():
    x =  df_wind_onshore.loc[df_wind_onshore['Year'] == year, :]
    y  = x["2050"].reset_index(drop=True)
    onshore.at[:,year] = y
onshore.drop(onshore.tail(24).index,inplace=True)# dropping last 24 hours because of leap year
result_path_onshore = os.path.join(parentpath, "data", "competes",  "CF_onshore_matrix.csv")
onshore.to_csv(result_path_onshore, sep=',')

df_wind_offshore['Year'] = df_wind_offshore["year"]
offshore = pd.DataFrame()
for year in df_wind_offshore.index.year.unique():
    x =  df_wind_offshore.loc[df_wind_offshore['Year'] == year, :]
    y  = x["2050"].reset_index(drop=True)
    offshore.at[:,year] = y
offshore.drop(offshore.tail(24).index,inplace=True)# dropping last 24 hours because of leap year
result_path_offshore = os.path.join(parentpath, "data", "competes",  "CF_offshore_matrix.csv")
offshore.to_csv(result_path_offshore, sep=',')


df_pv['Year'] = df_pv["year"]
pv = pd.DataFrame()
for year in df_pv.index.year.unique():
    x =  df_pv.loc[df_pv['Year'] == year, :]
    y  = x["2050"].reset_index(drop=True)
    pv.at[:,year] = y
pv.drop(pv.tail(24).index,inplace=True)# dropping last 24 hours because of leap year
result_path_pv = os.path.join(parentpath, "data", "competes",  "CF_pv_matrix.csv")
pv.to_csv(result_path_pv, sep=',')
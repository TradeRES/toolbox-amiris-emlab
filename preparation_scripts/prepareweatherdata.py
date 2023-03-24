import os
import pandas as pd
from os.path import dirname, realpath
import numpy as np
grandparentpath = dirname(dirname(realpath(os.getcwd())))
parentpath = dirname(os.getcwd())
# competes = os.path.join(parentpath,'data\\competes\\NLVREprofilesandload2019-2050_ricardo.xlsx')
# competesexcel = pd.read_excel(competes, index_col=0,
#                       sheet_name=["NL Wind Onshore profiles",
#                                   "NL Wind Offshore profiles",
#                                   "NL Sun PV profiles"])
# # WindOffshore_increase = competesexcel['NL Wind Offshore profiles'][2050] /competesexcel['NL Wind Offshore profiles'][2019]
# # WindOffshore_increase.replace([np.inf, -np.inf], 1, inplace=True)
# sum_offshore = competesexcel['NL Wind Offshore profiles'].sum()
# offshoreCF_increase = sum_offshore[2050]/sum_offshore[2050]

current_wind_data_path = os.path.join(parentpath,  "data", "renewableninja","ninja_wind_country_NL_current-merra-2_corrected.csv")
df_wind = pd.read_csv( current_wind_data_path, sep =",", index_col = 'time', parse_dates = True ,skiprows = [0,1])
current_pv_data_path = os.path.join(parentpath, "data", "renewableninja", "ninja_pv_country_NL_merra-2_corrected.csv")
df_solar = pd.read_csv( current_pv_data_path, sep =",", index_col = 'time', parse_dates = True ,skiprows = [0,1])
"""
from DNV
 onshore wind from 26% now to 34%, and from 38% to 43% for offshore wind by 2050.
 offshoreCF_increase =  round(43/38,2) in 2018 Renewable Power Generation Costs in 201
 onshoreCF_increase =  round(34/26,2)
IRENA
 with capacity factors in the range of 36% to 58% in 2030 and 43% to 60% in 2050, compared to an average of 43% in 2018.
 
"""

"""
Average from dividing the weather years given by TNO
"""
offshoreCF_increase =  1.66 #increase from
onshoreCF_increase =  1.42
#=================================================================================================== offshore
df_wind['Year'] = df_wind.index.year
offshore = pd.DataFrame()
for year in df_wind.index.year.unique():
    x =  df_wind.loc[df_wind['Year'] == year, :]
    y  = x["offshore"].reset_index(drop=True)
    offshore.at[:,year] = y

futureoffshore  = offshoreCF_increase*offshore
futureoffshore[futureoffshore  > 1] = 1
futureoffshore.drop(futureoffshore.tail(24).index,inplace=True)# dropping last 24 hours because of leap year

result_path_off = os.path.join(grandparentpath, "data", "weatherpotentialNetherlands",  "CF_offshore.csv")
futureoffshore.to_csv(result_path_off, sep=',')
#=================================================================================================== onshore
onshore = pd.DataFrame()

for year in df_wind.index.year.unique():
    x =  df_wind.loc[df_wind['Year']  == year, :]
    y  = x["onshore"].reset_index(drop=True)
    onshore.at[:,year] = y
# because of
futureonshore  = onshoreCF_increase*onshore
futureonshore[futureonshore  > 1] = 1
futureonshore.drop(futureonshore.tail(24).index,inplace=True) # because of leap year

result_path_on = os.path.join(grandparentpath, "data", "weatherpotentialNetherlands","CF_onshore.csv")
futureonshore.to_csv(result_path_on, sep=',')
#==================================================================================================== PV
pv = pd.DataFrame()
df_solar['Year'] = df_solar.index.year
for year in df_solar.index.year.unique():
    x =  df_solar.loc[df_solar['Year']  == year, :]
    y  = x["national"].reset_index(drop=True)
    pv.at[:,year] = y

pv.drop(pv.tail(24).index,inplace=True)# because of leap year

result_path_on = os.path.join(grandparentpath, "data","weatherpotentialNetherlands", "CF_PV.csv")
pv.to_csv(result_path_on, sep=',')
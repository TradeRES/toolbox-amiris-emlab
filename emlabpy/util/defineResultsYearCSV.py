import sys
import pandas as pd
import os
years_file = sys.argv[2]
f = open(years_file, "r")
years_str = f.read()
years = years_str.split("/")
current_year = years[0]
# first_year = years[1]
# tick = int(current_year) - int(first_year)
f.close()

amiris_results_path = sys.argv[1]
df = pd.read_csv( amiris_results_path)
df['year'] = current_year
df.to_csv(amiris_results_path, index=False)

amiris_energy_exchange_path = sys.argv[3]
df_exchange = pd.read_csv( amiris_energy_exchange_path, sep =";")

amiris_residual_load_path = sys.argv[4]
df_residual_raw = pd.read_csv( amiris_residual_load_path, sep =",")

hourly_res_indeed_path = sys.argv[5]
df_hourly_res_infeed_raw = pd.read_csv( hourly_res_indeed_path, sep =",")

hourly_generation_group_path = sys.argv[6]
df_hourly_generation_raw = pd.read_csv( hourly_generation_group_path, sep =",")

grandparentpath =  os.path.join(os.path.dirname(os.path.dirname(os.getcwd())))
storage_level_path = sys.argv[7]
df_storage_levels = pd.read_csv( storage_level_path, sep =",")
df_storage_levels['year'] = current_year
df_storage_levels.to_csv(storage_level_path, index=False)
# new_storage_level_path = os.path.join(grandparentpath,'amiris_workflow\\output\\'+str(tick) +'.csv')
#Renaming the file
#os.rename(storage_level_path, new_storage_level_path)
amiris_results_year = os.path.join(grandparentpath,'amiris_workflow\\output\\'+current_year +'.xlsx')

with pd.ExcelWriter(amiris_results_year) as writer:
    df_exchange.to_excel(writer, sheet_name="energy_exchange" )
    df_residual_raw.to_excel(writer, sheet_name="residual_load", index=False)
    df_hourly_res_infeed_raw.to_excel(writer, sheet_name="res_infeed" )
    df_hourly_generation_raw.to_excel(writer, sheet_name="hourly_generation", index=False)

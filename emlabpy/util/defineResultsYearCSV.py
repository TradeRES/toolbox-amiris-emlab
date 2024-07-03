import sys
import pandas as pd
import os
# import gc
years_file = sys.argv[2]
f = open(years_file, "r")
years_str = f.read()
years = years_str.split("/")
current_year = years[0]

f.close()
amiris_results_path = sys.argv[1]
df = pd.read_csv( amiris_results_path)
# capped_revenues_per_plant_path = sys.argv[7]
# capped_revenues_per_plant = pd.read_csv( capped_revenues_per_plant_path, sep =",")
# capped_revenues_per_plant.drop("Unnamed: 0", axis=1, inplace=True)
# total_capped_revenues = capped_revenues_per_plant.sum().to_frame()
# total_capped_revenues.index = total_capped_revenues.index.astype('int64')
# total_capped_revenues.columns = ['capped_revenues']
# del capped_revenues_per_plant
# gc.collect()
# df_combined = df.merge(total_capped_revenues, left_on='identifier', right_index=True, how='left')
# df_combined['year'] = current_year
# df_combined.to_csv(amiris_results_path, index=False)

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

amiris_results_year = os.path.join(grandparentpath,'amiris_workflow\\output\\'+current_year +'.xlsx')
with pd.ExcelWriter(amiris_results_year) as writer:
    df_exchange.to_excel(writer, sheet_name="energy_exchange" )
    df_residual_raw.to_excel(writer, sheet_name="residual_load", index=False)
    df_hourly_res_infeed_raw.to_excel(writer, sheet_name="res_infeed" )
    df_hourly_generation_raw.to_excel(writer, sheet_name="hourly_generation", index=False)

print("done")
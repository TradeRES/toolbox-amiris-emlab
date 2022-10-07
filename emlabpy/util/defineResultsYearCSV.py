import sys
import pandas as pd
import os
years_file = sys.argv[2]
f = open(years_file, "r")
years_str = f.read()
years = years_str.split("/")
current_year = years[0]
f.close()

amiris_results_path = sys.argv[1]
df = pd.read_csv( amiris_results_path)
df['year'] = current_year
df.to_csv(amiris_results_path, index=False)

amiris_energy_exchange_path = sys.argv[3]
df_exchange = pd.read_csv( amiris_energy_exchange_path, sep =";")

amiris_residual_load_path = sys.argv[4]
df_residual_raw = pd.read_csv( amiris_residual_load_path, sep =",")
#df_residual_raw['year'] = current_year

grandparentpath =  os.path.join(os.path.dirname(os.path.dirname(os.getcwd())))
amiris_results_year = os.path.join(grandparentpath,'amiris_workflow\\output\\'+current_year +'.xlsx')
with pd.ExcelWriter(amiris_results_year) as writer:
    df_exchange.to_excel(writer, sheet_name="energy_exchange" )
    df_residual_raw.to_excel(writer, sheet_name="residual_load", index=False)


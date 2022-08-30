import sys
import pandas as pd

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

amiris_raw_results_path = sys.argv[3]
df_raw = pd.read_csv( amiris_raw_results_path, sep =";")
df_raw['year'] = current_year
df_raw.to_csv(amiris_raw_results_path, index=False, sep =";")
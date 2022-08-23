import sys
import pandas as pd

amiris_results_path = sys.argv[1]
years_file = sys.argv[2]
df = pd.read_csv( amiris_results_path)

f = open(years_file, "r")
years_str = f.read()
f.close()
years = years_str.split("/")
current_year = years[0]
df['year'] = current_year
df.to_csv(amiris_results_path, index=False)


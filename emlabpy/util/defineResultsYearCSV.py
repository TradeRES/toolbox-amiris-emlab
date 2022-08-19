import sys
import pandas as pd
import os
from pathlib import Path


amiris_results_path = sys.argv[1]
years_file = sys.argv[2]
#grandparentpath = Path(__file__).parents[2]
#amiris_results_path =  os.path.join(grandparentpath,'amiris_workflow\\output\\amiris_results.csv')
#years_file = os.path.join(os.path.dirname(os.getcwd()), "years.txt" )

df = pd.read_csv( amiris_results_path)

f = open(years_file, "r")
years_str = f.read()
f.close()
years = years_str.split("/")
current_year = years[0]
df['year'] = current_year
df.to_csv(amiris_results_path, index=False)
#df.at[0,6] = asd

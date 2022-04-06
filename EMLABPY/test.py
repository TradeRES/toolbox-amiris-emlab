import pandas as pd
x = [[2000, 'Job', 'Salary($)'],
          [2001, 'Machine Learning Engineer', 121000]]
df = pd.DataFrame(x)
df.set_index(0, inplace=True)
df.loc[2000]
print("here")

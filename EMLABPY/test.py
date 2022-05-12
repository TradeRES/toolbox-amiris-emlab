# import pandas library
import pandas as pd

# dictionary
x = ['A', 'B', 'A', 'B', 'A', 'B'],
y = [1, 4, 3, 2, 10, 11]

df = pd.DataFrame(powerplantsvalues, columns=['name', 'technology', 'profit'])
groupedplantsbytechnology = df.groupby('technology')
keys = groupedplantsbytechnology.groups.keys()
for i in keys:
    for index, planttoInvest in groupedplantsbytechnology.get_group(i).iterrows():
        if planttoInvest["technology"].isinvestable == False:
            break
    # investing in best candidate power plant as it passed the checks.

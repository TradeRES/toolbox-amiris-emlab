import yaml
import pandas as pd
scenario = "C:\\Users\\isanchezjimene\\Documents\\TraderesCode\\toolbox-amiris-emlab\\amiris\\input\\Austria2019\\scenario_test.yaml"
#scenariojson = "scenario.json"


with open(scenario, "r") as stream:
    try:
        # yaml=YAML(typ='safe')   # default, if not specfied, is 'rt' (round-trip)
        data = yaml.load(stream, Loader=yaml.Loader)
        print(type(data))
    except:
        print("error")


column = []
value = []
position = 0

for agent in data['Agents']:
    if 'Attributes' in agent:
        if (agent['Type'] in ('PredefinedPlantBuilder')):
            column.append("Type")
            value.append(agent['Type'])
            for attribute, v in agent['Attributes'].items():
                if type(v) is dict:
                    for k, valuep in v.items():
                        column.append(k)
                        value.append(valuep)
                else:
                    column.append(attribute)
                    value.append(v)
            d = {'Id':column, agent['Id']:value}
            if position == 0:
                df1 = pd.DataFrame(d)
                df1.set_index('Id')
            else:
                df3 = pd.DataFrame(d)
                df3.set_index('Id')
                df1 = pd.merge(df1, df3, on='Id', how='outer')
            position += 1
            column = []
            value = []

oldheaders = df1.columns.values.tolist()
neaheader = []
for i in oldheaders:
    if i == 'index':
        neaheader.append('index')
    else:
        new = str(5) + str(i)[2:]
        neaheader.append(int(new))
df1.rename(columns=dict(zip(oldheaders, neaheader)), inplace=True)



column = []
value = []
position = 0
for agent in data['Agents']:
    if 'Attributes' in agent:
        if (agent['Type'] in ('VariableRenewableOperator')):
            column.append("Type")
            value.append(agent['Type'])
            for attribute, v in agent['Attributes'].items():
                if type(v) is dict:
                    for k, valuep in v.items():
                        column.append(k)
                        value.append(valuep)
                else:
                    column.append(attribute)
                    value.append(v)
            d = {'Id':column, agent['Id']:value}
            if position == 0:
                df2 = pd.DataFrame(d)
                df2.set_index('Id')
            else:
                df3 = pd.DataFrame(d)
                df3.set_index('Id')
                df2 = pd.merge(df2, df3, on='Id', how='outer')
            position += 1
            column = []
            value = []
with pd.ExcelWriter("C:\\Users\\isanchezjimene\\Documents\\TraderesCode\\toolbox-amiris-emlab\\scripts\\scenario.xlsx") as writer:
    df1.to_excel(writer, sheet_name='PredefinedPlantBuilder')
    df2.to_excel(writer, sheet_name='VariableRenewableOperator')
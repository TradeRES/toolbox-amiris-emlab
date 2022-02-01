# %%
import pandas as pd
df = pd.read_csv("C:\\Users\\isanchezjimene\\Documents\\TraderesCode\\toolbox-amiris-emlab\\scripts\\AMIRIS_combined.csv", sep=',')

# Conventional operator

# %%
filtered = df[df['variable'].isin(["CostsInEUR","ReceivedMoneyInEUR"])]
agents = filtered.AgentId.unique()
filtered.set_index("AgentId", "variable")

# %%
profits = []

# %%
#conventional and renewable profits
for agent in agents:
    revenue = filtered.loc[(filtered['variable'] == 'ReceivedMoneyInEUR') & (filtered['AgentId'] == agent)].value.item()
    costs   = filtered.loc[(filtered['variable'] == 'CostsInEUR') & (filtered['AgentId'] == agent)].value.item()
    profits.append([agent,(revenue - costs)])

# %%
# batteries
profitbatteries  = df.loc[df['variable'] == 'Profit']
agents = profitbatteries.AgentId.unique()
for agent in agents:
    profits.append([agent, profitbatteries.loc[(profitbatteries['AgentId'] == agent)].value.item()])

# %%
#highest profits
dfprofits = pd.DataFrame(profits, columns=["Agent", "profit"])
dfprofits.sort_values(by=['profit'], ascending=False)

# %%
HighestProfitAgent = dfprofits.iloc[0].Agent
BestInvestment = df.loc[(df['AgentId'] == HighestProfitAgent)]
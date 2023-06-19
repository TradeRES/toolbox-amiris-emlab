

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


path_folder_out = "./outputs/"
merit_order = pd.read_csv( "./supply_book.csv", sep=";", header=None)
# Add Headers and remove last technical element
merit_order.columns = ["Power", "Price", "Trader"]
merit_order = merit_order.iloc[:-1]
merit_order
res_traders = [11, 12, 13]
merit_order_no_res = merit_order.loc[~merit_order["Trader"].isin(res_traders)]

merit_order_no_res["CumulatedPower"] = merit_order_no_res["Power"].cumsum()

traders_fuel = {
    1000: "NUCLEAR",
    1001: "LIGNITE",
    1002: "HARD_COAL",
    1003: "NATURAL_GAS_CC",
    1004: "NATURAL_GAS_GT",
    1005: "OIL"
}
merit_order_no_res["Fuel"] = merit_order_no_res["Trader"].apply(
    lambda x: traders_fuel.get(x)
)

colors = {
    'PV': '#fcb001',
    'WindOff': '#0504aa',
    'WindOn': '#82cafc',
    'Biogas': '#15b01a',
    'RunOfRiver': '#c79fef',
    'NUCLEAR': '#e50000',
    'LIGNITE': '#7f2b0a',
    'HARD_COAL': '#000000',
    'NATURAL_GAS_CC': '#a57e52',
    'NATURAL_GAS_GT': '#929591',
    'OIL': '#aaa662'
}

colors = {
    'PV': '#fcb001',
    'WindOff': '#0504aa',
    'WindOn': '#82cafc',
    'Biogas': '#15b01a',
    'RunOfRiver': '#c79fef',
    'NUCLEAR': '#e50000',
    'LIGNITE': '#7f2b0a',
    'HARD_COAL': '#000000',
    'NATURAL_GAS_CC': '#a57e52',
    'NATURAL_GAS_GT': '#929591',
    'OIL': '#aaa662'
}


matrix = merit_order_no_res[['Fuel', 'Price', 'CumulatedPower']].values
MeritOrder = np.zeros((0,3))

for el in range(len(matrix)-1):
    MeritOrder = np.append(MeritOrder, np.reshape(matrix[el,], (1,3)), axis=0)
    if matrix[el,0] != matrix[el+1,0]:
        obj = np.reshape(matrix[el,], (1,3))
        obj[0][0] = matrix[el+1,0]
        MeritOrder = np.append(MeritOrder, obj, axis=0)

MeritOrder = pd.DataFrame(
    data=MeritOrder,
    columns=['Fuel', 'Price', 'CumulatedPower']
)
MeritOrder = MeritOrder.astype({'CumulatedPower': 'float32', 'Price': 'float32'})

plt.rcParams.update({'font.size': 12})

fig, ax = plt.subplots(figsize = (15,8))

for fuel in MeritOrder['Fuel'].unique():
    _ = ax.fill_between(x='CumulatedPower',
                        y1='Price',
                        where = MeritOrder["Fuel"] == fuel,
                        facecolor = colors[fuel],
                        step = "pre",
                        lw = 15,
                        #        interpolate = True,
                        data = MeritOrder,
                        label=fuel)

_ = ax.set(
    xlim=(-1000, MeritOrder['CumulatedPower'].max() + 1000),
    ylim=(MeritOrder['Price'].min() - 10, MeritOrder['Price'].max() + 10)
    #lim=(-200, 300)
)
_ = plt.xlabel('Kumulierte Leistung [MW]')
_ = plt.ylabel('Grenzkosten [€/MWh]')
_ = ax.legend(loc='lower right', ncol=3)

plt.tight_layout()

plt.savefig("merit_order_plot_DLR.png")

plt.show()
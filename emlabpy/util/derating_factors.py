import os
from plots.plots import prepare_pp_status
from util.spinedb_reader_writer import *
import matplotlib.pyplot as plt
type = "sqlite:///"
init_folder = "C:\\toolbox-amiris-emlab\\"
folder = init_folder + "emlabpy\\plots\\Scenarios\\"

first = type + folder
emlab_sql = "\\EmlabDB.sqlite"
amiris_sql = "\\AMIRIS db.sqlite"
energy_exchange_url_sql = "\\energy exchange.sqlite"
scenario_name = "NL-EOM_nolifetimeextension"
emlab_url = first + scenario_name + emlab_sql
amiris_url = first + scenario_name + emlab_sql
spinedb_reader_writer = SpineDBReaderWriter("Amiris", emlab_url, amiris_url)
reps = spinedb_reader_writer.read_db_and_create_repository("plotting")
global years_to_generate
years_to_generate = list(range(reps.start_simulation_year, reps.current_year + 1))  # control the current year

LOLE = 4
global unique_technologies
unique_technologies = reps.get_unique_candidate_technologies_names()
unique_technologies.append("Nuclear")
annual_decommissioned_capacity, annual_in_pipeline_capacity, annual_commissioned, \
    all_techs_capacity, last_year_in_pipeline, last_year_decommissioned, \
    last_year_operational_capacity, last_year_to_be_decommissioned_capacity, \
    last_year_strategic_reserve_capacity, capacity_per_status, number_per_status_last_year = \
    prepare_pp_status(years_to_generate, unique_technologies, reps)

yearly_electricity_prices = pd.DataFrame()
TotalAwardedPowerInMW = pd.DataFrame()
residual_load = pd.DataFrame()
DispatchSystemCostInEUR = pd.DataFrame()
hourly_load_shedded = pd.DataFrame()
hourly_load_shedders_per_year = pd.DataFrame()
hourly_industrial_heat = pd.DataFrame()
hourly_generation_res = pd.DataFrame()
derating_factor = pd.DataFrame()

demand_excel = init_folder + "data\\40weatherYears2050TNO.xlsx"
demand =  pd.read_excel(demand_excel, sheet_name=["Load"])
demand_at_scarcity = pd.DataFrame()

original_demand = pd.DataFrame()
shedded = pd.DataFrame()

for year in years_to_generate:
    print(year)
    year_excel = folder + scenario_name + "\\" + str(year) + ".xlsx"
    df = pd.read_excel(year_excel, sheet_name=["energy_exchange", "hourly_generation"])
    hourly_load_shedders = pd.DataFrame()
    for unit in df['hourly_generation'].columns.values:
        if unit[0:4] == "unit"  and unit[5:] != "8888888":
            hourly_load_shedders[unit[5:]] = df['hourly_generation'][unit]
        elif unit =="PV":
            hourly_generation_res["Solar PV large"] = df['hourly_generation'][unit]
        elif unit =="WindOff":
            hourly_generation_res["Wind Offshore"] = df['hourly_generation'][unit]
        elif unit =="WindOn":
            hourly_generation_res["Wind Onshore"] = df['hourly_generation'][unit]
        elif unit =="storages_discharging":
            hourly_generation_res["Lithium ion battery"] = df['hourly_generation'][unit]
        elif unit =="conventionals":
            hourly_generation_res["hydrogen OCGT"] = df['hourly_generation'][unit]
        else:
            pass

    total_hourly_load_shedders = hourly_load_shedders.sum(axis=1)
    yearly_at_scarcity_hours =  total_hourly_load_shedders[total_hourly_load_shedders > 0 ].index

    demand_at_scarcity.at["prices", year] = df["energy_exchange"]["ElectricityPriceInEURperMWH"].loc[yearly_at_scarcity_hours].mean()
    demand_at_scarcity.at["awarded_power", year] = df["energy_exchange"]["TotalAwardedPowerInMW"].loc[yearly_at_scarcity_hours].mean()

    shedded[year] = total_hourly_load_shedders
    original_demand[year] = demand["Load"][year - 2050 + 1980]

    all_techs_capacity.rename(columns={"Lithium ion battery 4": "Lithium ion battery"}, inplace=True)

    for tech in all_techs_capacity:
        if tech in all_techs_capacity.loc[year] and tech in hourly_generation_res.columns:
            if tech =="Lithium ion battery": # there are 2 types of batteries
                installed_capacity = all_techs_capacity.loc[year, tech].sum()
            else:
                installed_capacity = all_techs_capacity.loc[year, tech]
            average_generation = hourly_generation_res.loc[yearly_at_scarcity_hours, tech].mean()
            derating_factor.at[tech,year] = average_generation / installed_capacity
        else:
            pass

demand_LOLE = pd.DataFrame()
demand_LOLE["shortages"] = shedded.stack().reset_index(drop=True)
demand_LOLE["load"] = original_demand.stack().reset_index(drop=True)
sorted_demand_LOLE = demand_LOLE.sort_values(by='shortages', ascending=False, ignore_index=True)


selected_rows = sorted_demand_LOLE[sorted_demand_LOLE['shortages'] > 0].head(LOLE*len(years_to_generate))
selected_rows_1_5 = sorted_demand_LOLE[sorted_demand_LOLE['shortages'] > 0].head(int(LOLE*len(years_to_generate)*1.5))
demand_near_scarcity = pd.DataFrame({LOLE: [selected_rows["load"].mean()], LOLE*1.5: [selected_rows_1_5["load"].mean()]})


with pd.ExcelWriter("near_scarcity.xlsx") as writer:
    derating_factor.to_excel(writer, sheet_name="derating_factors")
    demand_at_scarcity.to_excel(writer, sheet_name="demand_at_scarcity")
    demand_near_scarcity.to_excel(writer, sheet_name="demand_near_scarcity")

axs21 = derating_factor.T.plot() #color=colors_unique_techs
axs21.set_axisbelow(True)
plt.xlabel('Years', fontsize='medium')
plt.ylabel('Derating factors (€/MWh)', fontsize='medium')
plt.legend(fontsize='medium', loc='upper left', bbox_to_anchor=(1, 1.1))
plt.grid()
axs21.set_title(scenario_name + ' \n Derating factors')
plt.show()



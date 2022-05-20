"""
This code prepares the information for next years market clearing:
-fuel prices and demand. the demand is as the node "electricity"
For the first 2 years the fuel prices are considering interpolating.
For the next years the fuel prices are considered with a geometric trend

"""
from modules.defaultmodule import DefaultModule
import pandas as pd
from datetime import datetime, timedelta


class PrepareMarket(DefaultModule):

    def __init__(self, reps):
        super().__init__("Next year prices", reps)
        self.tick = 0
        self.simulation_year = 0
        self.empty = None
        self.Years = []
        self.writer = None
        self.path = '../data/amiris/amiris_data_structure.xlsx'
        self.power_plants_list = self.reps.power_plants
        reps.dbrw.stage_init_next_prices_structure()

    def act(self):
        self.setTimeHorizon()
        self.setExpectations()
        self.openwriter()
        self.write_conventionals()
        self.write_renewables()
        self.write_storage()
        self.write_scenario_data_emlab("simulatedPrices")
        self.write_times()
        self.writer.save()
        self.writer.close()

    def setTimeHorizon(self):
        self.tick = self.reps.current_tick
        self.simulation_year = self.reps.current_year
        self.Years = (list(range(self.reps.start_simulation_year, self.simulation_year + 1, 1)))

    def setExpectations(self):
        for k, substance in self.reps.substances.items():
            fuel_price = substance.get_price_for_next_tick(self.reps, self.tick, self.simulation_year, substance)
            self.reps.dbrw.stage_simulated_fuel_prices(self.simulation_year, fuel_price, substance)

    def write_times(self):
        startime = datetime(self.simulation_year, 1, 1) - timedelta(minutes=2)
        stoptime = datetime(self.simulation_year, 12, 31) - timedelta(minutes=2)
        d = {'StartTime': startime, 'StopTime': stoptime}
        df = pd.DataFrame.from_dict(d, orient='index')
        df.to_excel(self.writer, sheet_name="times")

    def write_scenario_data_emlab(self, calculatedprices):
        Co2Prices = []
        FuelPrice_NUCLEAR = []
        FuelPrice_LIGNITE = []
        FuelPrice_HARD_COAL = []
        FuelPrice_NATURAL_GAS = []
        FuelPrice_OIL = []

        demand = ["./timeseries/demand/load.csv"] * len(self.Years)

        for k, substance in self.reps.substances.items():
            for year in self.Years:
                simulatedPrices = self.reps.dbrw.get_calculated_simulated_fuel_prices(substance, calculatedprices)
                df_prices = pd.DataFrame(simulatedPrices['data'])
                df_prices.set_index(0, inplace=True)
                fuel_price = df_prices.loc[str(year)][1]
                if substance.name == "nuclear":
                    FuelPrice_NUCLEAR.append(fuel_price)
                elif substance.name == "lignite":
                    FuelPrice_LIGNITE.append(fuel_price)
                elif substance.name == "hard_coal":
                    FuelPrice_HARD_COAL.append(fuel_price)
                elif substance.name == "natural_gas":
                    FuelPrice_NATURAL_GAS.append(fuel_price)
                elif substance.name == "light_oil":
                    FuelPrice_OIL.append(fuel_price)
                elif substance.name == "CO2":
                    Co2Prices.append(fuel_price)

        d = {'Co2Prices': Co2Prices,
             'FuelPrice_NUCLEAR': FuelPrice_NUCLEAR, 'FuelPrice_LIGNITE': FuelPrice_LIGNITE,
             'FuelPrice_HARD_COAL': FuelPrice_HARD_COAL, 'FuelPrice_NATURAL_GAS': FuelPrice_NATURAL_GAS,
             'FuelPrice_OIL': FuelPrice_OIL,
             'DemandSeries': demand}
        df = pd.DataFrame.from_dict(d, orient='index', columns=self.Years)
        df.to_excel(self.writer, sheet_name="scenario_data_emlab")

    def write_conventionals(self):
        identifier = []
        FuelType = []
        OpexVarInEURperMWH = []
        Efficiency = []
        BlockSizeInMW = []
        InstalledPowerInMW = []

        for name, pp in self.power_plants_list.items():
            if pp.technology.type == "ConventionalPlantOperator":
                identifier.append(pp.id)
                FuelType.append(self.reps.dictionaryFuelNames[pp.technology.fuel.name])
                OpexVarInEURperMWH.append(pp.technology.variable_operating_costs)
                Efficiency.append(pp.actualEfficiency)
                BlockSizeInMW.append(pp.capacity)
                InstalledPowerInMW.append(pp.capacity)

        d = {'identifier': identifier, 'FuelType': FuelType, 'OpexVarInEURperMWH': OpexVarInEURperMWH,
             'Efficiency': Efficiency, 'BlockSizeInMW': BlockSizeInMW,
             'InstalledPowerInMW': InstalledPowerInMW}

        df = pd.DataFrame(data=d)
        df.to_excel(self.writer, sheet_name="conventionals")

    def write_renewables(self):
        identifier = []
        InstalledPowerInMW = []
        OpexVarInEURperMWH = []
        Set = []
        SupportInstrument = []
        FIT = []
        Premium = []
        Lcoe = []

        for id, pp in self.power_plants_list.items():
            if pp.technology.type == "VariableRenewableOperator":
                identifier.append(pp.id)
                InstalledPowerInMW.append(pp.capacity)
                OpexVarInEURperMWH.append(pp.technology.variable_operating_costs)
                Set.append(self.reps.dictionaryTechSet[pp.technology.name])
                SupportInstrument.append("-")
                FIT.append("-")
                Premium.append("-")
                Lcoe.append("-")

        d = {'identifier': identifier, 'InstalledPowerInMW': InstalledPowerInMW,
             'OpexVarInEURperMWH': OpexVarInEURperMWH,
             'Set': Set, 'SupportInstrument': SupportInstrument, 'FIT': FIT, 'Premium': Premium, 'Lcoe': Lcoe}

        df = pd.DataFrame(data=d)
        df.to_excel(self.writer, sheet_name="renewables")

    def write_storage(self):
        identifier = []
        EnergyToPowerRatio = []
        ChargingEfficiency = []
        DischargingEfficiency = []
        InitialEnergyLevelInMWH = []
        InstalledPowerInMW = []
        StorageType = []
        for id, pp in self.power_plants_list.items():
            if pp.technology.type == "StorageTrader":
                identifier.append(pp.id)
                ChargingEfficiency.append(pp.actualEfficiency)  # todo this should be charging efficiency specifically
                DischargingEfficiency.append(pp.actualDischargingEfficiency)
                InitialEnergyLevelInMWH.append(0)  # todo this should be charging efficiency specifically
                EnergyToPowerRatio.append(pp.technology.energyToPowerRatio)
                InstalledPowerInMW.append(pp.capacity)
                StorageType.append("STORAGE")

        d = {'identifier': identifier, 'StorageType': StorageType, 'EnergyToPowerRatio': EnergyToPowerRatio,
             'ChargingEfficiency': ChargingEfficiency,
             'DischargingEfficiency': DischargingEfficiency, 'InitialEnergyLevelInMWH': InitialEnergyLevelInMWH,
             'InstalledPowerInMW': InstalledPowerInMW}

        df = pd.DataFrame(data=d)
        df.to_excel(self.writer, sheet_name="storages")

    def openwriter(self):

        self.writer = pd.ExcelWriter(self.path, mode="a", engine='openpyxl', if_sheet_exists='replace')

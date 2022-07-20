from modules.defaultmodule import DefaultModule
import pandas as pd
from datetime import datetime, timedelta
from util import globalNames


class PrepareMarket(DefaultModule):
    """
    This function prepares the information for next years market clearing:
    -fuel prices and demand. the demand is as the node "electricity".
    The fuel prices are stochastically simulated with a triangular trend

    """

    def __init__(self, reps):
        super().__init__("Next year prices", reps)
        self.tick = 0
        self.simulation_year = 0
        self.empty = None
        self.Years = []
        self.writer = None
        self.path = globalNames.amiris_data_path
        self.power_plants_list = []
        reps.dbrw.stage_init_bids_structure()
        reps.dbrw.stage_init_next_prices_structure()

    def act(self):
        totallist = []
        for energy_producer in self.reps.energy_producers.values():
            totallist.append(
                self.reps.get_operational_and_to_be_decommissioned_power_plants_by_owner(energy_producer.name))
        self.power_plants_list = totallist[0]
        self.setTimeHorizon()
        self.setExpectations()
        self.openwriter()
        self.write_conventionals()
        self.write_renewables()
        self.write_storage()
        self.write_biogas()
        self.write_scenario_data_emlab("next_year_price")
        self.write_times()
        self.writer.save()
        self.writer.close()
        print("saved to ", self.path)

    def setTimeHorizon(self):
        self.tick = self.reps.current_tick
        self.simulation_year = self.reps.current_year
        self.Years = (list(range(self.reps.start_simulation_year, self.simulation_year + 1, 1)))

    def setExpectations(self):
        for k, substance in self.reps.substances.items():
            fuel_price = substance.get_price_for_next_tick(self.reps, self.tick, self.simulation_year, substance)
            substance.simulatedPrice_inYear = fuel_price
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
            if calculatedprices == "next_year_price":
                fuel_price = substance.simulatedPrice_inYear
            else:
                fuel_price = substance.futurePrice_inYear

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

        for pp in self.power_plants_list:
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

        for pp in self.power_plants_list:
            if pp.technology.type == "VariableRenewableOperator" and self.reps.dictionaryTechSet[
                pp.technology.name] != "Biogas":
                identifier.append(pp.id)
                InstalledPowerInMW.append(pp.capacity)
                OpexVarInEURperMWH.append(pp.technology.variable_operating_costs)
                Set.append(self.reps.dictionaryTechSet[pp.technology.name])
                SupportInstrument.append("-")
                FIT.append("-")
                Premium.append("-")
                Lcoe.append("-")
            if self.reps.dictionaryTechSet[
                pp.technology.name] == "Hydropower_reservoir_medium":
                print("siiii")
        d = {'identifier': identifier, 'InstalledPowerInMW': InstalledPowerInMW,
             'OpexVarInEURperMWH': OpexVarInEURperMWH,
             'Set': Set, 'SupportInstrument': SupportInstrument, 'FIT': FIT, 'Premium': Premium, 'Lcoe': Lcoe}

        df = pd.DataFrame(data=d)
        df.to_excel(self.writer, sheet_name="renewables")

    def write_biogas(self):
        identifier = []
        InstalledPowerInMW = []
        OpexVarInEURperMWH = []
        Set = []
        SupportInstrument = []
        FIT = []
        Premium = []
        Lcoe = []

        for pp in self.power_plants_list:
            if pp.technology.type == "VariableRenewableOperator" and self.reps.dictionaryTechSet[
                pp.technology.name] == "Biogas":
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
        df.to_excel(self.writer, sheet_name="biogas")

    def write_storage(self):
        identifier = []
        EnergyToPowerRatio = []
        ChargingEfficiency = []
        DischargingEfficiency = []
        InitialEnergyLevelInMWH = []
        InstalledPowerInMW = []
        StorageType = []
        for pp in self.power_plants_list:
            if pp.technology.type == "StorageTrader":
                identifier.append(pp.id)
                ChargingEfficiency.append(pp.technology.chargingEfficiency)
                DischargingEfficiency.append(pp.technology.dischargingEfficiency)
                InitialEnergyLevelInMWH.append(pp.initialEnergyLevelInMWH)
                EnergyToPowerRatio.append(pp.technology.energyToPowerRatio)
                InstalledPowerInMW.append(pp.capacity)
                StorageType.append("STORAGE")

        d = {'identifier': identifier, 'StorageType': StorageType, 'EnergyToPowerRatio': EnergyToPowerRatio,
             'ChargingEfficiency': ChargingEfficiency,
             'DischargingEfficiency': DischargingEfficiency, 'InitialEnergyLevelInMWH': InitialEnergyLevelInMWH,
             'InstalledPowerInMW': InstalledPowerInMW, }
        # @DLR: missing SelfDischargeRatePerHour in excel

        df = pd.DataFrame(data=d)
        print(self.path)
        df.to_excel(self.writer, sheet_name="storages")

    def openwriter(self):
        self.writer = pd.ExcelWriter(self.path, mode="a", engine='openpyxl', if_sheet_exists='replace')

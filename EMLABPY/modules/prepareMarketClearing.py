"""
This code prepares the information for next years market clearing:
-fuel prices and demand. the demand is as the node "electricity"
For the first 2 years the fuel prices are considering interpolating.

"""
from emlabpy.modules.defaultmodule import DefaultModule
import pandas as pd


class PrepareMarket(DefaultModule):

    def __init__(self, reps):
        super().__init__("Next year prices", reps)
        self.tick = 0
        self.year = 0
        self.fuel_price = 0
        self.empty = None
        reps.dbrw.stage_init_next_prices_structure()

    def act(self):
        # self.setTimeHorizon()
        # self.setExpectations()
        # self.openexcel()

        self.write_conventionals()
        # self.write_scenario_data_emlab()
        # self.write_renewables()
        # self.write_storage()

    def openexcel(self):
        self.empty = pd.read_excel("../data/amiris/amiris_data_structure_template_empty.xlsx")
        # self.empty = pd.read_excel("./../data/amiris/amiris_data_structure_template_empty.xlsx", sheet_name= "conventionals", index_col=1,header=None)

    def setTimeHorizon(self):
        self.tick = self.reps.current_tick
        self.year = self.reps.current_year

    def setExpectations(self):
        for k, substance in self.reps.substances.items():
            self.fuel_price = substance.get_price_for_next_tick(self.reps, self.tick, self.year, substance)
            self.reps.dbrw.stage_simulated_fuel_prices(self.year, self.fuel_price, substance)

    def write_conventionals(self):
        temporalid = []
        FuelType = []
        OpexVarInEURperMWH = []
        Efficiency = []
        BlockSizeInMW = []
        InstalledPowerInMW = []
        for id, pp in self.reps.power_plants.items():
            if pp.technology.type == "ConventionalPlantOperator":
                temporalid.append(int(str(pp.commissionedYear) +
                                      str("{:02d}".format(int(self.reps.dictionaryFuelNumbers[pp.technology.fuel.name])))
                                  ))
                FuelType.append(self.reps.dictionaryFuelNames[pp.technology.fuel.name])
                OpexVarInEURperMWH.append(pp.technology.variable_operating_costs)
                Efficiency.append(pp.actualEfficiency)
                BlockSizeInMW.append(pp.capacity)
                InstalledPowerInMW.append(pp.capacity)

        d = {'temporalid': temporalid, 'FuelType': FuelType, 'OpexVarInEURperMWH': OpexVarInEURperMWH,
             'Efficiency': Efficiency, 'BlockSizeInMW': BlockSizeInMW,
             'InstalledPowerInMW': InstalledPowerInMW}

        df = pd.DataFrame(data=d)
        df['C'] = df.groupby(['temporalid']).cumcount()+1
        df['C'] = df['C'].apply(lambda x: '{0:0>3}'.format(x))
        df['identifier'] = df['temporalid'].map(str) + df['C'].map(str)
        df.drop(['C', 'temporalid'], axis=1, inplace=True)
        df.to_excel("../data/amiris/amiris_data_structure.xlsx", sheet_name="conventionals")

    def write_renewables(self):
        identifier = []
        InstalledPowerInMW = []
        OpexVarInEURperMWH = []
        Set = []
        SupportInstrument = []
        FIT = []
        Premium = []
        Lcoe = []

        for id, pp in self.reps.power_plants.items():
            identifier.append(id)
            OpexVarInEURperMWH.append(pp.technology.variable_operating_costs)
            InstalledPowerInMW.append(pp.capacity)
            Set.append(pp.capacity)
            SupportInstrument.append(pp.technology.fuel)
            FIT.append(pp.actualEfficiency)
            Premium.append(pp.actualEfficiency)
            Lcoe.append(pp.capacity)

        d = {'identifier': identifier, 'InstalledPowerInMW': InstalledPowerInMW,
             'OpexVarInEURperMWH': OpexVarInEURperMWH,
             'Set': Set, 'SupportInstrument': SupportInstrument, 'FIT': FIT, 'Premium': Premium, 'Lcoe': Lcoe}

        df = pd.DataFrame(data=d).T
        df.to_excel("../data/amiris/amiris_data_structure.xlsx", sheet_name="renewables")

    def write_storage(self):
        identifier = []
        EnergyToPowerRatio = []
        ChargingEfficiency = []
        DischargingEfficiency = []
        InitialEnergyLevelInMWH = []
        PowerInMW = []

        for id, pp in self.reps.power_plants.items():
            identifier.append(id)
            EnergyToPowerRatio.append(pp)
            ChargingEfficiency.append(pp.capacity)
            DischargingEfficiency.append(pp.capacity)
            InitialEnergyLevelInMWH.append(pp.technology.fuel)
            PowerInMW.append(pp.actualEfficiency)

        d = {'identifier': identifier, 'EnergyToPowerRatio': EnergyToPowerRatio,
             'ChargingEfficiency': ChargingEfficiency,
             'DischargingEfficiency': DischargingEfficiency, 'InitialEnergyLevelInMWH': InitialEnergyLevelInMWH,
             'PowerInMW': PowerInMW}

        df = pd.DataFrame(data=d).T
        df.to_excel("../data/amiris/amiris_data_structure.xlsx", sheet_name="storages")

    def write_scenario_data_emlab(self):
        pass
        # Co2Prices = []
        # FuelPrice_NUCLEAR =
        # for id, substance in self.reps.substances.items():
        # d = {'identifier': identifier, 'EnergyToPowerRatio': EnergyToPowerRatio, 'ChargingEfficiency': ChargingEfficiency,
        #      'DischargingEfficiency': DischargingEfficiency, 'InitialEnergyLevelInMWH': InitialEnergyLevelInMWH, 'PowerInMW': PowerInMW}
        #
        # df = pd.DataFrame(data=d).T
        # df.to_excel("../data/amiris/amiris_data_structure.xlsx", sheet_name = "scenario_data_emlab")

import shutil
from modules.defaultmodule import DefaultModule
import pandas as pd
from datetime import datetime, timedelta
from util import globalNames


class PrepareMarket(DefaultModule):
    """
    This module prepares the information for the current simulation year
    1. operational, to be decommissioned and in strategic reserve power plants are chosen
    2. the fuel prices is calculated by interpolation and
        after a year X (specified by the user), fuel prices are stochastically simulated with a triangular trend
        the demand is as the node "electricity" for DE
    3. demand and yield profiles are saved to files to be read by amiris
    4. power plants are saved in excel to be read by amiris. as well as the fuel and CO2 prices.
    """

    def __init__(self, reps):
        super().__init__("Next year prices", reps)
        self.tick = 0
        self.simulation_year = 0
        self.empty = None
        self.writer = None
        self.path = globalNames.amiris_data_path
        self.power_plants_list = []
        reps.dbrw.stage_init_bids_structure()
        reps.dbrw.stage_init_next_prices_structure()

    def act(self):
        # look for all power plants, except for decommissioned and in pipeline
        self.setTimeHorizon()
        self.setFuelPrices()
        self.power_plants_list = self.reps.get_power_plants_by_status([globalNames.power_plant_status_operational,
                                                                       globalNames.power_plant_status_to_be_decommissioned,
                                                                       globalNames.power_plant_status_strategic_reserve,
                                                                       ])
        self.calculate_save_peak_dispatchable_capacity()
        self.sort_power_plants_by_age()
        self.openwriter()
        self.write_renewables()
        self.write_storage()
        self.write_conventionals()
        self.write_electrolysers()
        self.write_load_shedders()
        self.write_biogas()
        self.write_scenario_data_emlab("next_year_price")
        self.write_times()
        self.writer.close()
        print("saved to ", self.path)

    def calculate_save_peak_dispatchable_capacity(self):
        # saving the available capacity to calculate the supply ratio
        sumcapacity = []
        for pp in self.power_plants_list:
            if pp.technology.intermittent == False:
                # include hydropower, batteries, biogas,
                sumcapacity.append(pp.capacity)
        peak_dispatchable_capacity = sum(sumcapacity)
        self.reps.dbrw.stage_peak_dispatchable_capacity(peak_dispatchable_capacity, self.reps.current_year)

    def sort_power_plants_by_age(self):  # AMIRIS seem to give dispatch priority according to the order in the excel.
        self.power_plants_list.sort(key=lambda x: x.age)

    def setTimeHorizon(self):
        self.tick = self.reps.current_tick
        self.simulation_year = self.reps.current_year

    def setFuelPrices(self):
        for k, substance in self.reps.substances.items():
            fuel_price = substance.get_price_for_tick(self.reps, self.simulation_year, False)
            substance.simulatedPrice_inYear = fuel_price
            self.reps.dbrw.stage_simulated_fuel_prices(self.simulation_year, fuel_price, substance)

    def write_times(self):
        """"
        These are not read by AMIRIS
        """
        startime = datetime(self.simulation_year, 1, 1) - timedelta(minutes=2)
        stoptime = datetime(self.simulation_year, 12, 31) - timedelta(minutes=2)
        d = {'StartTime': startime, 'StopTime': stoptime}
        df = pd.DataFrame.from_dict(d, orient='index')
        df.to_excel(self.writer, sheet_name="times")

    def write_scenario_data_emlab(self, calculatedprices):
        wholesale_market = self.reps.get_electricity_spot_market_for_country(self.reps.country)
        demand = wholesale_market.hourlyDemand
        dict_fuels = {}
        for k, substance in self.reps.substances.items():
            if calculatedprices == "next_year_price":  # choose the prices depending if nexy year or future year is calculated
                fuel_price = substance.simulatedPrice_inYear
            else:
                fuel_price = substance.futurePrice_inYear
            # --------------------------------------------------------------------- preparing demand and yield profiles
            if substance.name == "electricity":
                if self.reps.available_years_data == False: # for germany the load is calculated with a trend.
                    new_demand = demand.copy()
                    new_demand[1] = new_demand[1].apply(lambda x: x * fuel_price)
                    new_demand.to_csv(globalNames.load_file_for_amiris, header=False, sep=';', index=False)
                else:  # for now, only have dynamic data for NL case
                    if self.reps.runningModule == "run_prepare_next_year_market_clearing" and self.reps.current_tick > 0:
                        # the load was already updated in the clock step
                        pass
                    elif self.reps.runningModule == "run_prepare_next_year_market_clearing" and self.reps.current_tick == 0:
                        pass
                        # self.update_demand_file() todo # in the first tick all needs to be updated??
                        # self.update_profiles_files()

                    elif self.reps.runningModule == "run_future_market":
                        if self.reps.investmentIteration == 0:
                            # only update data in first iteration of each year or during the initialization loop

                            if self.reps.fix_demand_to_initial_year == True and self.reps.fix_profiles_to_initial_year == True:
                                print("dont update demand, nor profiles")
                            else:
                                # ========================================================= Updating demand for investment
                                if self.reps.fix_demand_to_initial_year == True:
                                    print("dont update demand ")
                                else:
                                    if self.reps.initialization_investment == True:
                                        # update demand during initialization investment
                                        print("updating demand file data of year" + str(self.simulation_year))
                                        self.update_demand_file()
                                    else:
                                        print("updated demand for year " + str(self.simulation_year))
                                        # copying future demand (prepared in clock) file to be current demand
                                        wholesale_market.future_demand.to_csv(globalNames.load_file_for_amiris,
                                                                              header=False, sep=';', index=False)

                                # ========================================================
                                # Profiles are never updated for investment,but the profile files were changed
                                # during the market preparation for the current year
                                if self.reps.initialization_investment == True:
                                    print("dont update profiles, the representative year was saved in the initialization")
                                    # self.update_profiles_files(self.reps.current_year + \
                                    #                            self.reps.investment_initialization_years)
                                else:
                                    print("copy profiles prepared in clock")
                                    shutil.copy(globalNames.future_windoff_file_for_amiris,
                                                globalNames.windoff_file_for_amiris)
                                    shutil.copy(globalNames.future_windon_file_for_amiris,
                                                globalNames.windon_file_for_amiris)
                                    shutil.copy(globalNames.future_pv_file_for_amiris,
                                                globalNames.pv_file_for_amiris)

                        else:
                            # next iterations have same market conditions, no need to update the demand or profile
                            print("next iteration, dont update data")
                            pass
            # ----------------------------------------------------------------------------preparing CO2 price
            elif substance.name == "CO2":
                Co2Prices = fuel_price
            # ----------------------------------------------------------------------------preparing  other fuel prices
            else:
                try:
                    if self.reps.dictionaryFuelNames[k] in ["NUCLEAR", "LIGNITE", "HARD_COAL", "NATURAL_GAS", "OIL",
                                                            "HYDROGEN", "BIOMASS", "WASTE"]:
                        dict_fuels[self.reps.dictionaryFuelNames[k]] = fuel_price
                    else:
                        pass
                        # "Fuel not considered in AMIRIS"
                except KeyError:
                    print(k + "not amiris name")

        d2 = {'AgentType': "CarbonMarket", 'CO2': Co2Prices}

        dict_fuels['AgentType'] = "FuelsMarket"
        fuels = pd.DataFrame.from_dict(dict_fuels, orient='index', columns=[1])
        fuels.loc["OTHER"] = 0
        co2 = pd.DataFrame.from_dict(d2, orient='index')

        result = pd.concat(
            [co2, fuels],
            axis=1,
            join="outer",
        )
        df1_transposed = result.T
        df1_transposed.to_excel(self.writer, sheet_name="scenario_data_emlab")

    def update_demand_file(self):
        print("updated demand file" + str(self.reps.current_year + self.reps.investment_initialization_years))
        excel = pd.read_excel(globalNames.input_data, index_col=0,
                                 sheet_name=["Load"])
        demand = excel['Load'][self.reps.current_year + self.reps.investment_initialization_years]
        demand.to_csv(globalNames.load_file_for_amiris, header=False, sep=';', index=True)
    def write_electrolysers(self):
        if self.reps.monthly_hydrogen_demand ==True:
            hydrogen_demand = "amiris-config/data/hydrogen_demand.csv"
        else:
            hydrogen_demand = self.reps.hydrogen_demand["Hydrogen"].averagemonthlyConsumptionMWh

        d = {'identifier': 99999999999,
             'ElectrolyserType': "ELECTROLYSIS",
             'PeakConsumptionInMW': self.reps.hydrogen_demand["Hydrogen"].peakConsumptionInMW,
             'ConversionFactor': 1,
            # 'ConversionFactor': self.reps.power_generating_technologies['electrolyzer'].efficiency,
             'HydrogenProductionTargetInMWH': hydrogen_demand
             }
        df = pd.DataFrame(data=d, index=[0])
        df.to_excel(self.writer, sheet_name="electrolysers")
    def write_load_shedders(self):
        VOLLs = []
        TimeSeries = []
        Type_ls = []
        for name, loadshedder in self.reps.loadShedders.items():
            Type_ls.append("SHEDDING")
            VOLLs.append(loadshedder.VOLL)
            TimeSeries.append(loadshedder.TimeSeriesFile)

        d = {'Type': Type_ls,
             'VOLL': VOLLs,
             'TimeSeries': TimeSeries
             }
        df = pd.DataFrame(data=d)
        df.to_excel(self.writer, sheet_name="load_shedding",index=False)

    def update_profiles_files(self, year):
        print("Update profiles to year" + str(year))
        excel = pd.read_excel(globalNames.input_data, index_col=0,
                                 sheet_name=["Wind Onshore profiles",
                                             "Wind Offshore profiles",
                                             "Sun PV profiles"])
        wind_onshore = excel['Wind Onshore profiles'][year]
        wind_onshore.to_csv(globalNames.windon_file_for_amiris, header=False, sep=';', index=True)
        wind_offshore = excel['Wind Offshore profiles'][year]
        wind_offshore.to_csv(globalNames.windoff_file_for_amiris, header=False, sep=';', index=True)
        pv = excel['Sun PV profiles'][year]
        pv.to_csv(globalNames.pv_file_for_amiris, header=False, sep=';', index=True)

    def write_conventionals(self):
        identifier = []
        FuelType = []
        OpexVarInEURperMWH = []
        Efficiency = []
        BlockSizeInMW = []
        InstalledPowerInMW = []
        operator = self.reps.get_strategic_reserve_operator(self.reps.country)
        for pp in self.power_plants_list:
            if pp.technology.type == "ConventionalPlantOperator":
                identifier.append(pp.id)
                FuelType.append(self.reps.dictionaryFuelNames[pp.technology.fuel.name])
                if pp.name in operator.list_of_plants:
                    OpexVarInEURperMWH.append(operator.reservePriceSR)
                else:
                    OpexVarInEURperMWH.append(pp.actualVariableCost)
                Efficiency.append(pp.actualEfficiency)
                BlockSizeInMW.append(pp.capacity)
                InstalledPowerInMW.append(pp.capacity)

        d = {'identifier': identifier, 'FuelType': FuelType, 'OpexVarInEURperMWH': OpexVarInEURperMWH,
             'Efficiency': Efficiency, 'BlockSizeInMW': BlockSizeInMW,
             'InstalledPowerInMW': InstalledPowerInMW}

        df = pd.DataFrame(data=d)
        df.sort_values(by=['InstalledPowerInMW'], inplace=True)
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
        operator = self.reps.get_strategic_reserve_operator(self.reps.country)

        for pp in self.power_plants_list:
            if pp.technology.type == "VariableRenewableOperator" and self.reps.dictionaryTechSet[
                pp.technology.name] != "Biogas":
                identifier.append(pp.id)
                InstalledPowerInMW.append(pp.capacity)
                # todo: make exception for forward Capacity market.
                if pp.name in operator.list_of_plants:
                    OpexVarInEURperMWH.append(operator.reservePriceSR)
                else:
                    OpexVarInEURperMWH.append(pp.actualVariableCost)
                Set.append(self.reps.dictionaryTechSet[pp.technology.name])
                SupportInstrument.append("NONE")
                FIT.append("-")
                Premium.append("-")
                Lcoe.append("-")

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
        operator = self.reps.get_strategic_reserve_operator(self.reps.country)

        for pp in self.power_plants_list:
            if pp.technology.type == "VariableRenewableOperator" and self.reps.dictionaryTechSet[
                pp.technology.name] == "Biogas":
                identifier.append(pp.id)
                InstalledPowerInMW.append(pp.capacity)
                if pp.name in operator.list_of_plants:
                    OpexVarInEURperMWH.append(operator.reservePriceSR)
                else:
                    OpexVarInEURperMWH.append(pp.actualVariableCost)
                Set.append(self.reps.dictionaryTechSet[pp.technology.name])
                SupportInstrument.append("-")
                FIT.append("-")
                Premium.append("-")
                Lcoe.append("-")

        d = {'identifier': identifier, 'InstalledPowerInMW': InstalledPowerInMW,
             'OpexVarInEURperMWH': OpexVarInEURperMWH,
             'Set': Set, 'SupportInstrument': SupportInstrument, 'FIT': FIT, 'Premium': Premium, 'Lcoe': Lcoe}

        df = pd.DataFrame(data=d)
        df.sort_values(by=['InstalledPowerInMW'], inplace=True)
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
                ChargingEfficiency.append(pp.actualEfficiency)
                DischargingEfficiency.append(pp.technology.dischargingEfficiency) # todo modify also discarhging capacity
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

    # def write_conventionals_and_biogas_with_prices(self, calculatedprices):
    #     identifier = []
    #     FuelType = []
    #     OpexVarInEURperMWH = []
    #     BlockSizeInMW = []
    #     InstalledPowerInMW = []
    #     operator = self.reps.get_strategic_reserve_operator(self.reps.country)
    #     for pp in self.power_plants_list:
    #         if pp.technology.type == "ConventionalPlantOperator":
    #             identifier.append(pp.id)
    #             FuelType.append(self.reps.dictionaryFuelNames[pp.technology.fuel.name])
    #
    #             if calculatedprices == "next_year_price":
    #                 fuel_price = self.reps.substances[pp.technology.fuel.name].simulatedPrice_inYear
    #                 CO2_price = self.reps.substances["CO2"].simulatedPrice_inYear * pp.technology.fuel.co2_density
    #             else:
    #                 fuel_price = self.reps.substances[pp.technology.fuel.name].futurePrice_inYear
    #                 CO2_price = self.reps.substances["CO2"].futurePrice_inYear * pp.technology.fuel.co2_density
    #
    #             if pp.name in operator.list_of_plants:
    #                 OpexVarInEURperMWH.append(operator.reservePriceSR + (fuel_price + CO2_price)/pp.actualEfficiency  )
    #             else:
    #                 OpexVarInEURperMWH.append(pp.technology.variable_operating_costs + (fuel_price + CO2_price)/pp.actualEfficiency )
    #
    #             BlockSizeInMW.append(pp.capacity)
    #             InstalledPowerInMW.append(pp.capacity)
    #
    #     d = {'identifier': identifier, 'FuelType': FuelType, 'OpexVarInEURperMWH': OpexVarInEURperMWH,
    #          'BlockSizeInMW': BlockSizeInMW,
    #          'InstalledPowerInMW': InstalledPowerInMW}
    #     df = pd.DataFrame(data=d)
    #     df.sort_values(by=['BlockSizeInMW'], inplace=True)
    #     df.sort_values(by=['OpexVarInEURperMWH'], inplace=True)
    #
    #     min = 0.1
    #     max = 0.4
    #     myrange = max - min
    #     length = df.index.size
    #     efficiency = []
    #     for t in list(range(0,length)):
    #         efficiency.append(min + myrange*t/length)
    #     efficiency.reverse()
    #     df["Efficiency"] = efficiency
    #     df.to_excel(self.writer, sheet_name="conventionals")
    #
    #     identifier = []
    #     InstalledPowerInMW = []
    #     OpexVarInEURperMWH = []
    #     Set = []
    #     SupportInstrument = []
    #     FIT = []
    #     Premium = []
    #     Lcoe = []
    #     operator = self.reps.get_strategic_reserve_operator(self.reps.country)
    #
    #     for pp in self.power_plants_list:
    #         if pp.technology.type == "VariableRenewableOperator" and self.reps.dictionaryTechSet[
    #             pp.technology.name] == "Biogas":
    #             identifier.append(pp.id)
    #             InstalledPowerInMW.append(pp.capacity)
    #             if calculatedprices == "next_year_price":
    #                 fuel_price = self.reps.substances[pp.technology.fuel.name].simulatedPrice_inYear
    #             else:
    #                 fuel_price = self.reps.substances[pp.technology.fuel.name].futurePrice_inYear
    #
    #             if pp.name in operator.list_of_plants:
    #                 OpexVarInEURperMWH.append(operator.reservePriceSR + (fuel_price)/pp.actualEfficiency  )
    #             else:
    #                 OpexVarInEURperMWH.append(pp.technology.variable_operating_costs + (fuel_price)/pp.actualEfficiency )
    #
    #             Set.append(self.reps.dictionaryTechSet[pp.technology.name])
    #             SupportInstrument.append("-")
    #             FIT.append("-")
    #             Premium.append("-")
    #             Lcoe.append("-")
    #
    #     d = {'identifier': identifier, 'InstalledPowerInMW': InstalledPowerInMW,
    #          'OpexVarInEURperMWH': OpexVarInEURperMWH,
    #          'Set': Set, 'SupportInstrument': SupportInstrument, 'FIT': FIT, 'Premium': Premium, 'Lcoe': Lcoe}
    #
    #     df = pd.DataFrame(data=d)
    #     df.sort_values(by=['InstalledPowerInMW'], inplace=True)
    #     df.to_excel(self.writer, sheet_name="biogas")

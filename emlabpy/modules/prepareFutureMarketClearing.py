from domain.CandidatePowerPlant import *
from modules.prepareMarketClearing import PrepareMarket


class PrepareFutureMarketClearing(PrepareMarket):
    """
    This module prepares the information for the future market.
    In the first simulation year,
        In the first iteration the market is prepared for user-defined look-ahead years without candidate power plants
        In the next iteration, the initialization investment is prepared. The market prices and laod is prepared for next year,
        then 2 years ahead and so on until the user-defined look-ahead year is reached.
        Investable Candidate power plants are added to the market.
    1. the fuel prices are calculated by interpolation and
        after a year X (specified by the user), fuel prices are stochastically simulated with a geometric trend regression
    2. if the simulation year has reached the user-defined pastTimeHorizon, then
        power plants that have passed their lifetime and that presented negative operational profits in the
        last pastTimeHorizon years are then set to de decommissioned, otherwise they are set to be operational
    2. demand and yield profiles are saved to files to be read by dispatch-model(AMIRIS)
    3. power plants are saved in excel to be read by dispatch-model(AMIRIS), as well as the fuel and CO2 prices.
    """

    def __init__(self, reps):
        super().__init__(reps)
        self.simulation_year = 0  # future investment year
        self.powerPlantsinFutureToBeOperational = []
        self.RESLabel = "VariableRenewableOperator"
        self.conventionalLabel = "ConventionalPlantOperator"
        self.storageLabel = "StorageTrader"
        reps.dbrw.stage_init_future_prices_structure()

        if reps.current_tick == 0 and reps.initialization_investment == True:
            if reps.investmentIteration >= 0:
                print("initialization investments for year  " + str(reps.investment_initialization_years))
                # in the initialization round there are not past NPVs (calculated in financial results)
                self.power_plants_list = reps.get_investable_candidate_power_plants()
                self.look_ahead_years = reps.investment_initialization_years
            else:
                print("first run")
                self.power_plants_list = []
                self.look_ahead_years = reps.lookAhead

        elif reps.round_for_capacity_market_y_1 ==True:
            print("for CAPACITY MARKET Y-1")
            if self.reps.capacity_remuneration_mechanism in ["capacity_market", "capacity_subscription", "forward_capacity_market"]:
                market = reps.get_capacity_market_in_country(reps.country, long_term=False)
                self.look_ahead_years = market.forward_years_CM
            elif self.reps.capacity_remuneration_mechanism == "strategic_reserve_ger":
                SR_operator = self.reps.get_strategic_reserve_operator(self.reps.country)
                self.look_ahead_years = SR_operator.forward_years_SR
            self.setTimeHorizon()
            self.power_plants_list = []
        else:
            if reps.targetinvestment_per_year == True and reps.target_investments_done == False:
                # investing in target technologies
                self.power_plants_list = []
                self.look_ahead_years = reps.lookAhead
            else:  # no target investments, test as normal
                if reps.investmentIteration == 0:
                    self.power_plants_list = reps.get_investable_candidate_power_plants_minimal_irr_or_npv()
                else:
                    self.power_plants_list = reps.get_investable_candidate_power_plants()
                self.look_ahead_years = reps.lookAhead


        # changing efficency and variable costs of candidate power plants
        for pp in self.power_plants_list: # candidate technologues get variable costs from the technology
            pp.actualVariableCost = pp.technology.variable_operating_costs

        if len(self.power_plants_list) == 1: # if it is zero, then it is because of target investment or investment iteration 0
            uniquepp = self.power_plants_list[0]
            if reps.investmentIteration == 0:
                # in the first iteration: test realitist capacity if there is only one power plant
                uniquepp.capacity = uniquepp.capacityRealistic
                self.reps.dbrw.stage_last_testing_technology(True)
            else:
                year_iteration = str(reps.current_year + self.look_ahead_years) + "-" + str(reps.investmentIteration -1)
                NPV_last_investment_decision = next((i['parameter_value'] for i in reps.dbrw.db.query_object_parameter_values_by_object_class_and_object_name(
                                                        "CandidatePlantsNPV", uniquepp.name) if i['parameter_name'] == year_iteration), 0)
                print(NPV_last_investment_decision)
                if NPV_last_investment_decision< 10000:
                    print("last investment decision")
                    uniquepp.capacity = uniquepp.capacityRealistic
                    self.reps.dbrw.stage_last_testing_technology(True)
                else:
                    if reps.investmentIteration == 1:
                        # if in the first iteration the NPV was very high, then change back to larger installation volumes
                        self.reps.dbrw.stage_last_testing_technology(False)


    def act(self):
        print("investment iteration " + str(self.reps.investmentIteration))

        self.setTimeHorizon()
        self.setFuelPrices()
        self.filter_power_plants_to_be_operational()
        self.save_future_plants_to_be_operational()
        self.sort_power_plants_by_age()
        # ----------------------------------------------------functions to save the power plants
        self.openwriter()
        self.write_renewables()
        self.write_storage()
        self.write_load_shedders()
        self.write_conventionals()
        self.write_biogas()
        self.write_scenario_data_emlab("futurePrice")
        self.write_load_shifter_with_price_cap()
        self.write_times()
        self.writer.close()


    def filter_power_plants_to_be_operational(self):
        """
        This function assign a fictional future status to power plants by adding the look ahead years to the age of the power plants
        For plants that have passed their lifetime
            If the decommission year is specified in input file, these plants are decommissioned.
        :return:
        """
        powerPlantsfromAgent = self.reps.get_power_plants_by_owner(self.reps.agent)
        powerPlantsinSR = []

        requiredProfit = self.reps.energy_producers[self.reps.agent].getDismantlingRequiredOperatingProfit()
        horizon = self.reps.pastTimeHorizon

        SR_operator = self.reps.get_strategic_reserve_operator(self.reps.country)

        global decommissioned_list
        decommissioned_list = []

        for powerplant in powerPlantsfromAgent:
            fictional_age = powerplant.age + self.look_ahead_years
            # for plants that have passed their lifetime, assume that these will be decommissioned
            if self.reps.decommission_from_input == True and powerplant.decommissionInYear is not None:
                if self.simulation_tick >= powerplant.endOfLife:
                    # decommissioned as specified by input
                    powerplant.fictional_status = globalNames.power_plant_status_decommissioned
                    decommissioned_list.append(powerplant.name)
                else:
                    self.set_power_plant_as_operational_calculateEff_and_Var(powerplant, fictional_age)
            elif fictional_age > powerplant.technology.expected_lifetime + powerplant.technology.maximumLifeExtension:
                if self.reps.current_tick >= (self.reps.start_dismantling_tick - self.reps.lookAhead):
                    powerplant.fictional_status = globalNames.power_plant_status_decommissioned
                    decommissioned_list.append(powerplant.name)
                else:
                    self.set_power_plant_as_operational_calculateEff_and_Var(powerplant, fictional_age)

            elif powerplant.status ==  globalNames.power_plant_status_strategic_reserve:
                powerplant.technology.variable_operating_costs = SR_operator.reservePriceSR
                self.power_plants_list.append(powerplant)

            elif fictional_age >= powerplant.technology.expected_lifetime:
                if self.reps.current_tick == 0 and self.reps.initialization_investment == True and self.reps.investmentIteration == -1:
                    """
                    In the first iteration test the future market with all power plants,
                      except the ones that should be decommissioned by then
                    """
                    self.set_power_plant_as_operational_calculateEff_and_Var(powerplant, fictional_age)
                elif  self.reps.round_for_capacity_market_y_1 ==True:
                    """
                    for the capacity market y-1 all power plants that might be decommissioned should participate in the market
                    """
                    if fictional_age < powerplant.technology.expected_lifetime + powerplant.technology.maximumLifeExtension:
                        self.set_power_plant_as_operational_calculateEff_and_Var(powerplant, fictional_age)
                    else:
                        powerplant.fictional_status = globalNames.power_plant_status_decommissioned
                        decommissioned_list.append(powerplant.name)

                elif self.reps.current_tick >= (self.reps.start_dismantling_tick - self.reps.lookAhead): # there are enough past simulations fictional_age <= powerplant.technology.expected_lifetime + powerplant.technology.maximumLifeExtension:
                    self.check_profitability( powerplant,requiredProfit , horizon,  fictional_age)
                else:
                    self.set_power_plant_as_operational_calculateEff_and_Var(powerplant, fictional_age)
                    print("passed lifetime, decommission starting in year " + str(self.reps.start_dismantling_tick))

            elif fictional_age < 0:
                powerplant.fictional_status = globalNames.power_plant_status_inPipeline
            else:  # powerplant.commissionedYear > self.simulation_year
                # planned power plants further in the future should not be considered.
                # all plants that  have not passed their lifetime are expected to be operational
                self.set_power_plant_as_operational_calculateEff_and_Var(powerplant, fictional_age)

        self.save_decommissioned_expected_list(decommissioned_list)


    def check_profitability(self, powerplant, requiredProfit , horizon,  fictional_age):
        profits = self.reps.get_financial_report_for_plant_KPI(powerplant.name, self.reps.typeofProfitforPastHorizon)
        if isinstance(profits, pd.Series):
            profit = profits[-horizon:].mean() # takes the last horizon forecasts
            if profit <= requiredProfit:
                powerplant.fictional_status = globalNames.power_plant_status_decommissioned
                print("{} expected operating loss {} : was {} which is less than required:  {} " \
                      .format(powerplant.name, horizon, profit, requiredProfit))
                decommissioned_list.append(powerplant.name)
            else:
                print("past profit positive, dont dismantle " , powerplant.name)
                self.set_power_plant_as_operational_calculateEff_and_Var(powerplant, fictional_age)
        else:
            print("no past profits for plant, dismantle", powerplant.name)
            powerplant.fictional_status = globalNames.power_plant_status_decommissioned
            decommissioned_list.append(powerplant.name)
           # self.set_power_plant_as_operational_calculateEff_and_Var(powerplant, fictional_age)

    def save_decommissioned_expected_list(self, decommissioned_list):
        self.reps.dbrw.stage_list_decommissioned_expected_plants(decommissioned_list, self.simulation_year)

    def set_power_plant_as_operational_calculateEff_and_Var(self, powerplant, fictional_age):
        new_variable_costs = powerplant.getTechnology().get_variable_operating_by_time_series(fictional_age)
        ModifiedEfficiency = powerplant.getTechnology().get_efficiency_by_time_series(fictional_age) # same as geometric trend
        powerplant.setActualEfficiency(ModifiedEfficiency)
        powerplant.setActualVariableCosts(new_variable_costs)
        powerplant.fictional_status = globalNames.power_plant_status_operational
        self.power_plants_list.append(powerplant)

    def save_future_plants_to_be_operational(self):
        # saving for investment algorithm
        list_installed_pp = [i.id for i in self.power_plants_list if i.is_not_candidate_power_plant()]
        self.reps.dbrw.stage_installed_pp_names(list_installed_pp, self.simulation_tick)

    def setTimeHorizon(self):
        """
        The years are defined to store installed future power plants
        :return:
        """
        self.simulation_year = self.reps.current_year + self.look_ahead_years
        self.simulation_tick = self.reps.current_tick + self.look_ahead_years

    def setFuelPrices(self):
        """
        The demand is also predicted as a substance
        :return:
        """
        for k, substance in self.reps.substances.items():
            future_price = substance.get_price_for_tick(self.reps, self.simulation_year, True)  # True = simulating future prices
            substance.futurePrice_inYear = future_price
            self.reps.dbrw.stage_future_fuel_prices(self.simulation_year, substance,
                                                    future_price)


    def calculateExpectedOperatingProfitfrompastIterations(self, plant, horizon):
        # "totalProfits" or "irr"
        indices = list(range(self.reps.current_tick + self.look_ahead_years - horizon,
                             self.reps.current_tick + self.look_ahead_years))
        try:
            past_operating_profit = plant.expectedTotalProfitswFixedCosts.loc[indices].values
            averagePastOperatingProfit = sum(list(map(float, past_operating_profit))) / len(indices)
        except: # there are not enough information
            averagePastOperatingProfit = -1
        return averagePastOperatingProfit

    # this function is to pass the renewables grouped. Amiris_Results would then have to be reassigned to each id.
    # the profits of the installed power plants are saved to account for expected future profits.
    # if no futur
    # def write_renewables_together(self):
    #     identifier = []
    #     InstalledPowerInMW = []
    #     OpexVarInEURperMWH = []
    #     Set = []
    #     SupportInstrument = []
    #     FIT = []
    #     Premium = []
    #     Lcoe = []
    #     operator = self.reps.get_strategic_reserve_operator(self.reps.country)
    #     for pp in self.power_plants_list:
    #         if pp.technology.type == "VariableRenewableOperator" and self.reps.dictionaryTechSet[
    #             pp.technology.name] != "Biogas":
    #             identifier.append(pp.id)
    #             InstalledPowerInMW.append(pp.capacity)
    #             if pp.name in operator.list_of_plants_inSR_in_current_year:
    #                 OpexVarInEURperMWH.append(operator.reservePriceSR)
    #             else:
    #                 OpexVarInEURperMWH.append(pp.technology.variable_operating_costs)
    #             Set.append(self.reps.dictionaryTechSet[pp.technology.name])
    #             SupportInstrument.append("NONE")
    #             FIT.append("-")
    #             Premium.append("-")
    #             Lcoe.append("-")
    #
    #     d = {'identifier': identifier, 'InstalledPowerInMW': InstalledPowerInMW,
    #          'OpexVarInEURperMWH': OpexVarInEURperMWH,
    #          'Set': Set, 'SupportInstrument': SupportInstrument, 'FIT': FIT, 'Premium': Premium, 'Lcoe': Lcoe}
    #
    #     df = pd.DataFrame(data=d)
    #     chosenset = [self.reps.dictionaryTechSet[ren] for ren in globalNames.vRES]
    #     # grouping installed  renewables for amiris faster dispatch
    #     renewables = df[df['Set'].isin(chosenset)]
    #     df.drop(df['Set'].isin(chosenset).index, inplace=True)
    #     renewables = renewables.groupby('Set').agg({'identifier': 'first', 'InstalledPowerInMW':'sum', 'SupportInstrument': 'first',
    #                                                 'FIT': 'first', 'Premium': 'first','Lcoe': 'first',
    #                                                 'OpexVarInEURperMWH':'mean'})
    #     renewables = renewables.reset_index()
    #     groupedres = pd.concat([df, renewables])
    #     groupedres.to_excel(self.writer, sheet_name="renewables")


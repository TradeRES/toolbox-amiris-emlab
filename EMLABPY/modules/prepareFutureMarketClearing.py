
from domain.CandidatePowerPlant import *
from modules.prepareMarketClearing import PrepareMarket
from domain.StrategicReserveOperator import StrategicReserveOperator


class PrepareFutureMarketClearing(PrepareMarket):

    """ This function creates the power plants that will be analyzed as possible investments. It
        creates the Candidate Power Plants and these are assigned a capacity of 1 MW not to modify the
        For the first 2 years the fuel prices are considering interpolating.
        For the next years the fuel prices are considered with a geometric trend.
    """

    def __init__(self, reps):
        super().__init__(reps)
        self.newPowerPlant = None
        self.newTechnologies = None
        self.lastrenewableId = 0
        self.lastconventionalId = 0
        self.laststorageId = 0
        self.simulation_year = 0  # future investment year
        self.powerPlantsinFutureToBeOperational = []
        self.RESLabel = "VariableRenewableOperator"
        self.conventionalLabel = "ConventionalPlantOperator"
        self.storageLabel = "StorageTrader"
        reps.dbrw.stage_init_future_prices_structure()
        self.agent = "Producer1"
        self.power_plants_list =self.reps.get_investable_candidate_power_plants()
        # self.power_plants_ids_list = list(range(1, len(reps.candidatePowerPlants) + 1, 1))
        self.iteration = 0  # the number of times that the future clearing has been done per year.


    def act(self):
        self.setTimeHorizon()
        self.setExpectations()
      #  self.specifyIdsandCapacityCandidatePowerPlants()
        self.filter_power_plants_to_be_operational()
        # functions to save the power plants
        self.openwriter()
        self.write_scenario_data_emlab("futurePrice")
        self.write_conventionals()
        self.write_renewables()
        self.write_storage()
        self.write_times()
        self.writer.save()

    def filter_power_plants_to_be_operational(self):  # TODO should ooperational costs be raised?

        """
        This function assign a fictional future status to power plants
        If the plants have passed their expected lifetime then these are in theory decommissioned and not added to the list of power plants.

        :return:
        """

        powerPlantsfromAgent = self.reps.get_power_plants_by_owner(self.agent)
        powerPlantsinSR = self.reps.get_power_plants_in_SR_by_name()
        for powerplant in powerPlantsfromAgent:
            fictional_age = powerplant.age + self.reps.energy_producers[self.agent].getInvestmentFutureTimeHorizon()
            if fictional_age > powerplant.technology.expected_lifetime:
                powerplant.fictional_status = globalNames.power_plant_status_to_be_decommissioned
                # print("to be decommisioned", powerplant.name, "age", fictional_age,
                #       "technology", powerplant.technology.name, "lifetime", powerplant.technology.expected_lifetime)
                # todo add some exception for plants under startegic reserve
            elif powerplant.commissionedYear <= self.simulation_year and powerplant.name in powerPlantsinSR:
                powerplant.fictional_status = globalNames.power_plant_status_strategic_reserve
                # set the power plant costs to the strategic reserve price
                powerplant.technology.variable_operating_costs = self.reps.get_strategic_reserve_price(StrategicReserveOperator)
                powerplant.owner = 'StrategicReserveOperator'
                self.power_plants_list[powerplant.name] = powerplant
            elif powerplant.commissionedYear <= self.simulation_year:
                powerplant.fictional_status = globalNames.power_plant_status_operational
                self.power_plants_list[powerplant.name] = powerplant
            elif powerplant.commissionedYear > self.simulation_year:
                powerplant.fictional_status = globalNames.power_plant_status_inPipeline
                print("--------------------- in pipeline", powerplant.name)
            else:
                print("status not set", powerplant.name)


    def setTimeHorizon(self):
        """
        The years are defined to export all the CO2 prices
        :return:
        """
        startfutureyear = self.reps.start_simulation_year + self.reps.energy_producers[
            self.agent].getInvestmentFutureTimeHorizon()
        self.simulation_year = self.reps.current_year + self.reps.energy_producers[
            self.agent].getInvestmentFutureTimeHorizon()
        self.Years = (list(range(startfutureyear, self.simulation_year + 1, 1)))


    def setExpectations(self):
        """
        The demand is also predicted as a substance
        :return:
        """
        for k, substance in self.reps.substances.items():
            futureprice = substance.get_price_for_future_tick(self.reps, self.simulation_year, substance)
            self.reps.dbrw.stage_future_fuel_prices(self.simulation_year, substance,
                                                    futureprice)  # todo: save this as a map in DB
    #
    # def createCandidatePowerPlants(self):
    #     self.getlastIds()  # from installed power plants
    #     self.iteration = self.reps.dbrw.get_last_iteration(self.simulation_year)
    #     if self.iteration > 0:  # if there was no iteration before leave it as zero
    #         self.iteration += 1
    #         # TODO for higher iterations dont consider the power plants that are not investable
    #     self.reps.dbrw.stage_init_power_plants_list(self.iteration)
    #
    #     for key, candidateTechnology in self.reps.newTechnology.items():
    #         if candidateTechnology.type == self.RESLabel:
    #             self.lastrenewableId += 1
    #             object_name = self.lastrenewableId
    #         elif candidateTechnology.type == self.conventionalLabel:
    #             self.lastconventionalId += 1
    #             object_name = self.lastconventionalId
    #         elif candidateTechnology.type == self.storageLabel:
    #             self.laststorageId += 1
    #             object_name = self.laststorageId
    #         self.reps.candidatePowerPlants[object_name] = CandidatePowerPlant(object_name)
    #         self.reps.candidatePowerPlants[object_name].add_parameter_value(self.reps, "type", candidateTechnology.type,
    #                                                                         0)
    #         self.reps.candidatePowerPlants[object_name].add_parameter_value(self.reps, "technology",
    #                                                                         candidateTechnology.name, 0)
    #         self.reps.candidatePowerPlants[object_name].add_parameter_value(self.reps, "Capacity",
    #                                                                         candidateTechnology.Capacity, 0)
    #         print("New technology ", object_name, candidateTechnology.type, candidateTechnology.name,
    #               candidateTechnology.Capacity)
    #
    #         self.power_plants_ids_list.append(object_name)
    #     # df = pd.DataFrame.from_dict(candidateTechnology.__dict__, orient='index')
    #     # df.to_excel('forYaml.xlsx')
    #     print(self.power_plants_ids_list, self.iteration, self.simulation_year)
    #
    #     # save the list of power plants that have been candidates per iteration.
    #     self.reps.dbrw.stage_new_power_plants_ids(self.power_plants_ids_list, self.iteration, self.simulation_year)
    #
    #     # parameternames = [Technology, Status, CommissionedYear, Capacity, FuelType, Label]
    #
    # def getlastIds(self):
    #     # get maximum number of power plan
    #     lastbuiltrenewable = []
    #     lastbuiltconventional = []
    #     lastbuiltstorage = []
    #     for id, pp in self.reps.power_plants.items():
    #         if pp.label == self.RESLabel:
    #             lastbuiltrenewable.append(int(id))
    #         elif pp.label == self.conventionalLabel:
    #             lastbuiltconventional.append(int(id))
    #         elif pp.label == self.storageLabel:
    #             lastbuiltstorage.append(int(id))
    #     lastbuiltrenewable.sort()
    #     lastbuiltconventional.sort()
    #     lastbuiltstorage.sort()
    #     self.lastrenewableId = lastbuiltrenewable[-1]
    #     self.lastconventionalId = lastbuiltconventional[-1]
    #     if len(lastbuiltstorage) > 0:  # TODO: give numeration to storage so that it doesnt overlap with renewables
    #         self.laststorageId = lastbuiltstorage[-1]


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
        self.filter_power_plants_to_be_operational()
        # functions to save the power plants
        self.openwriter()
        self.write_scenario_data_emlab("futurePrice")
        self.write_conventionals()
        self.write_renewables()
        self.write_storage()
        self.write_biogas()
        self.write_times()
        self.writer.save()
        self.writer.close()

    def filter_power_plants_to_be_operational(self):  # TODO should operational costs be raised?

        """
        This function assign a fictional future status to power plants
        If the plants have passed their expected lifetime then these are in theory decommissioned and not added to the list of power plants.

        :return:
        """

        powerPlantsfromAgent = self.reps.get_power_plants_by_owner(self.agent)

        powerPlantsinSR = []
        SR_price = 0
        for i in self.reps.sr_operator.values():
            if len(i.list_of_plants) != 0 and i.zone == self.reps.country:
                powerPlantsinSR = i.list_of_plants
                SR_price = i.strategic_reserve_price

        for powerplant in powerPlantsfromAgent:
            fictional_age = powerplant.age + self.reps.energy_producers[self.agent].getInvestmentFutureTimeHorizon()
            if fictional_age > powerplant.technology.expected_lifetime:
                powerplant.fictional_status = globalNames.power_plant_status_to_be_decommissioned
                # print("to be decommisioned", powerplant.name, "age", fictional_age,
                #       "technology", powerplant.technology.name, "lifetime", powerplant.technology.expected_lifetime)
                # todo better to make decisions according to age
            elif powerplant.commissionedYear <= self.simulation_year and powerplant.name in powerPlantsinSR:
                powerplant.fictional_status = globalNames.power_plant_status_strategic_reserve
                # set the power plant costs to the strategic reserve price
                powerplant.technology.variable_operating_costs = SR_price
                powerplant.owner = 'StrategicReserveOperator'
                #self.power_plants_list[powerplant.name] = powerplant
                self.power_plants_list.append(powerplant)
            elif powerplant.commissionedYear <= self.simulation_year:
                powerplant.fictional_status = globalNames.power_plant_status_operational
                #self.power_plants_list[powerplant.name] = powerplant
                self.power_plants_list.append(powerplant)
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
            future_price = substance.get_price_for_future_tick(self.reps, self.simulation_year, substance)
            substance.futurePrice_inYear = future_price
            self.reps.dbrw.stage_future_fuel_prices(self.simulation_year, substance,
                                                    future_price)  # todo: save this as a map in DB
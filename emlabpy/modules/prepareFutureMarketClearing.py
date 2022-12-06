import os
import shutil

from domain.CandidatePowerPlant import *
from modules.prepareMarketClearing import PrepareMarket
import pandas as pd


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

        self.power_plants_list =self.reps.get_investable_candidate_power_plants()
        # self.power_plants_ids_list = list(range(1, len(reps.candidatePowerPlants) + 1, 1))
        self.iteration = 0  # the number of times that the future clearing has been done per year.


    def act(self):
        self.setTimeHorizon()
        self.setExpectations()
        self.filter_power_plants_to_be_operational()
        # from here functions are from prepare market clearing

        self.sort_power_plants_by_age()
        # functions to save the power plants
        self.openwriter()
        self.write_scenario_data_emlab("futurePrice")
        self.write_renewables()
        self.write_storage()

        if self.reps.writeALLcostsinOPEX ==True:
            self.write_conventionals_and_biogas_with_prices("futurePrice")
        else:
            self.write_conventionals()
            self.write_biogas()

        # todo: erase this
        path = os.path.join(os.path.dirname(os.getcwd()), str(self.reps.current_year) + ".xlsx"  )
        shutil.copy(globalNames.amiris_data_path, path)

        self.write_times()
        self.writer.save()
        self.writer.close()

    def filter_power_plants_to_be_operational(self):
        """
        This function assign a fictional future status to power plants
        If the plants have passed their expected lifetime then these are
        in theory decommissioned and not added to the list of power plants.

        :return:
        """
        powerPlantsfromAgent = self.reps.get_power_plants_by_owner(self.reps.agent)
        powerPlantsinSR = []
        SR_price = 0
        requiredProfit = self.reps.energy_producers[self.reps.agent].getDismantlingRequiredOperatingProfit()
        horizon = self.reps.pastTimeHorizon
        for i in self.reps.sr_operator.values():
            if len(i.list_of_plants) != 0 and i.zone == self.reps.country:
                powerPlantsinSR = i.list_of_plants
                SR_price = i.reservePriceSR

        for powerplant in powerPlantsfromAgent:
            fictional_age = powerplant.age + self.reps.lookAhead
            # for plants that have passed their lifetime, assume that these will be decommissioned
            if fictional_age > powerplant.technology.expected_lifetime:
                if self.reps.current_tick >= self.reps.start_tick_dismantling :
                    # calculate the past operating profit
                    profit = self.calculateAveragePastOperatingProfit(powerplant, horizon)

                    if profit <= requiredProfit:
                        # dont add this plant to future scenario
                        powerplant.status = globalNames.power_plant_status_decommissioned
                    else:
                        powerplant.fictional_status = globalNames.power_plant_status_operational
                        self.power_plants_list.append(powerplant)
                else:
                    powerplant.fictional_status = globalNames.power_plant_status_operational
                    self.power_plants_list.append(powerplant)
                # todo better to make decisions according to expected profit and expected participation in capacity market/strategic reserve
            elif powerplant.commissionedYear <= self.simulation_year and powerplant.name in powerPlantsinSR:
                powerplant.fictional_status = globalNames.power_plant_status_strategic_reserve
                # set the power plant costs to the strategic reserve price
                #powerplant.technology.variable_operating_costs = self.reps.get_strategic_reserve_price(StrategicReserveOperator)
                # todo: if plant is in strategic reserve , it should be decommissioned after 4 years so make an
                # exception for the power plants that were contracted earlier
                powerplant.owner = 'StrategicReserveOperator'
                powerplant.technology.variable_operating_costs = SR_price
                #  If there is SR, the power plants are considered to be in the SR also in the future with high MC prices
                # # todo: but if they are in the german SR, the generators should consider that they will be decommmsisioned after 4 years!!!
                self.power_plants_list.append(powerplant)
            elif powerplant.commissionedYear <= self.simulation_year:
                powerplant.fictional_status = globalNames.power_plant_status_operational
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
        startfutureyear = self.reps.start_simulation_year +   self.reps.lookAhead
                        #  self.reps.energy_producers[self.agent].getInvestmentFutureTimeHorizon()
        self.simulation_year = self.reps.current_year + self.reps.lookAhead
        #self.Years = (list(range(startfutureyear, self.simulation_year + 1, 1)))
        self.Years =  [self.simulation_year]

    def setExpectations(self):
        """
        The demand is also predicted as a substance
        :return:
        """
        for k, substance in self.reps.substances.items():
            future_price = substance.get_price_for_future_tick(self.reps, self.simulation_year, substance)
            substance.futurePrice_inYear = future_price
            self.reps.dbrw.stage_future_fuel_prices(self.simulation_year, substance,
                                                    future_price)

    def calculateAveragePastOperatingProfit(self, plant, horizon ):
        # "totalProfits" or "irr"
        averagePastOperatingProfit = 0
        # typeofProfitforPastHorizon are the total Profits which exclude the loans
        rep = self.reps.dbrw.findFinancialValueForPlant(plant, self.reps.typeofProfitforPastHorizon)
        if rep is not None:
            # if there is data than the one needed for the horizon then an average of those years are taken
            if self.reps.current_tick >= horizon:
                past_operating_profit_all_years = pd.Series(dict(rep["data"]))
                # before year 4 there is no dismantling considered.
                # in year 4 it looks for profits from tick  1 to tick 4
                # but the dismantling in tick 8 (when the plants should be installed) there are more plants installed
                # also it looks for the profits from tick 5 to tick 8. So the profits are different
                indices = list(range(self.reps.current_tick - horizon, self.reps.current_tick))
                past_operating_profit = past_operating_profit_all_years.loc[ list(map(str,indices))].values
                averagePastOperatingProfit =  sum(list(map(float,past_operating_profit))) / len(indices)
            else:  # Attention for now, for the first years the availble past data is taken
                print("no past profits for plant", plant.name)
                pass
        return averagePastOperatingProfit
from util import globalNames
from modules.defaultmodule import DefaultModule
from util.repository import Repository
import logging
import csv
import pandas as pd

class Dismantle(DefaultModule):
    """
    The class that decides to decomission some technologies
    """

    def __init__(self, reps: Repository):
        super().__init__('Dismantle decisions', reps)
        self.decommissioned_list = (self.reps.decommissioned["Decommissioned"]).Decommissioned
        reps.dbrw.stage_init_power_plants_status()

    def act(self):
        self.add_one_year_to_age()
        self.set_powerplants_status()  # set status according to operational time
        self.decommision_by_age_and_profit()
        self.save_powerplants_status_and_age()
        self.save_decommissioned_list()

    def decommision_by_age_and_profit(self):
        for producer, producer_specs in self.reps.energy_producers.items():
            for plant in self.reps.get_power_plants_to_be_decommissioned(producer):
                # TODO is the power plant subsidized ? then dismantle
                horizon = self.reps.pastTimeHorizon
                requiredProfit = producer_specs.getDismantlingRequiredOperatingProfit()
                if self.reps.current_tick >= self.reps.start_year_dismantling:
                    profit = self.calculateAveragePastOperatingProfit(plant, horizon) #attention change this to IRR
                    if profit <= requiredProfit:
                        logging.info("Dismantling power plant because it has an operating loss (incl O&M cost) on average in the last %s years: %s was %s which is less than required: "
                                .format(horizon, plant.name, profit, requiredProfit))
                        plant.dismantlePowerPlant(self.reps.current_tick)
                        self.reps.dbrw.stage_decommission_time(plant.name, self.reps.current_tick)
                        plant.status = globalNames.power_plant_status_decommissioned
                        self.decommissioned_list.append(plant.name)
                    else:
                        logging.info("dont dismantle but increase OPEX of %s ".format(plant.name))
                        ModifiedOM = plant.getActualFixedOperatingCost() * (
                                1 + (plant.getTechnology().getFixedOperatingCostModifierAfterLifetime())) ** (
                                             float(plant.age) - (
                                         (float(plant.getTechnology().getExpectedLifetime()))))
                        plant.setActualFixedOperatingCost(ModifiedOM)
                else:
                    logging.info("dont dismantle but increase OPEX of %s ".format(plant.name))
                    if plant.age < plant.technology.getExpectedLifetime():
                        print("Age is less than expected life time")
                    else:
                        ModifiedOM = plant.getActualFixedOperatingCost() * (
                                1 + (plant.technology.getFixedOperatingCostModifierAfterLifetime())) ** (
                                plant.age - plant.technology.getExpectedLifetime() )
                        plant.setActualFixedOperatingCost(ModifiedOM)
                        # TODO save the new fixed operating costs in DB!!!!!!!!!!!!!!!

    def add_one_year_to_age(self):
        for powerplantname, powerplant in self.reps.power_plants.items():
            powerplant.age += 1

    def calculateAveragePastOperatingProfit(self, plant, horizon):
        # "totalProfits" or "irr"
        averagePastOperatingProfit = 0

        rep = self.reps.dbrw.findFinancialValueForPlant(plant, self.reps.typeofProfitforPastHorizon)
        if rep is not None:
            # if there is data than the one needed for the horizon then an average of those years are taken
            if self.reps.current_tick >= horizon:
                past_operating_profit_all_years = pd.Series(dict(rep["data"]))
                indices = list(range(self.reps.current_tick-horizon, self.reps.current_tick))
                past_operating_profit = past_operating_profit_all_years.loc[ list(map(str,indices))].values
                averagePastOperatingProfit =  sum(list(map(float,past_operating_profit))) / len(indices)
            else:  # Attention for now, for the first years the availble past data is taken
                print("no past profits for plant", plant.name)
                pass
        return averagePastOperatingProfit

    def set_powerplants_status(self):
        for powerplantname, powerplant in self.reps.power_plants.items():
            technology = self.reps.power_generating_technologies[powerplant.technology.name]
            if powerplant.age > technology.expected_lifetime:
                powerplant.status = globalNames.power_plant_status_to_be_decommissioned
            elif powerplant.commissionedYear <= self.reps.current_year:
                powerplant.status = globalNames.power_plant_status_operational
            elif powerplant.commissionedYear > self.reps.current_year:
                powerplant.status = globalNames.power_plant_status_inPipeline
            else:
                print("status not set", powerplant.name)

    def save_powerplants_status_and_age(self):
        self.reps.dbrw.stage_power_plant_status_and_age(self.reps.power_plants)

    def save_decommissioned_list(self):
        self.reps.dbrw.stage_list_decommissioned_plants(self.decommissioned_list )

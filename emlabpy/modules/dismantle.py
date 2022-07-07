from util import globalNames
from modules.defaultmodule import DefaultModule
from util.repository import Repository
import logging
import csv


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
       # self.decommision_by_age_and_profit()
        self.save_powerplants_status_and_age()
        self.save_decommissioned_list()

    def decommision_by_age_and_profit(self):
        for producer, producer_specs in self.reps.energy_producers.items():
            for plant in self.reps.get_power_plants_to_be_decommissioned(producer):
                # TODO is the power plant subsidized ? then dismantle
                horizon = producer_specs.getPastTimeHorizon()
                requiredProfit = producer_specs.getDismantlingRequiredOperatingProfit()
                # todo: for the first 3 years dont dismantle
                profit = self.calculateAveragePastOperatingProfit(plant, horizon)
                if profit <= requiredProfit:
                    logging.info(
                        "Dismantling power plant because it has an operating loss (incl O&M cost) on average in the last %s years: %s was %s which is less than required: "
                            .format(horizon, plant, profit, requiredProfit))
                    plant.dismantlePowerPlant(self.reps.current_tick)
                    self.reps.dbrw.stage_decommission_time(plant.name, self.reps.current_tick)
                    plant.status = globalNames.power_plant_status_decommissioned
                    self.decommissioned_list.append(plant.name)
                else:
                    print("dont dismantle but increase OPEX, because lifetime is over")
                    ModifiedOM = plant.getActualFixedOperatingCost() * (
                            1 + (plant.getTechnology().getFixedOperatingCostModifierAfterLifetime())) ** (
                                         float(plant.getActualLifetime()) - (
                                     (float(plant.getTechnology().getExpectedLifetime()))))
                    plant.setActualFixedOperatingCost(ModifiedOM)

    def add_one_year_to_age(self):
        for powerplantname, powerplant in self.reps.power_plants.items():
            powerplant.age += 1

    def calculateAveragePastOperatingProfit(self, plant, horizon):
        averagePastOperatingProfit = 0
        rep = self.reps.dbrw.findFinancialPowerPlantProfitsForPlant(plant)

        if rep is not None:
            # if there is data than the one needed for the horizon then an average of those years are taken
            if self.reps.current_tick >= horizon:
                pastOperatingProfit = sum(int(x[1]) for x in rep['data'] if x[0] in range(-horizon, 1))
                # TODO add revenues from capacity mechanisms
                averagePastOperatingProfit = pastOperatingProfit / horizon
            else:  # TODO for now, for the first years the availble past data is taken
                averagePastOperatingProfit = sum(
                    int(x[1]) for x in rep['data'] if int(x[0]) < self.reps.current_tick) / horizon
        return averagePastOperatingProfit

    def set_powerplants_status(self):
        for powerplantname, powerplant in self.reps.power_plants.items():
            technology = self.reps.power_generating_technologies[powerplant.technology.name]
            if powerplant.age > technology.expected_lifetime:
                powerplant.status = globalNames.power_plant_status_to_be_decommissioned
            elif powerplant.commissionedYear <= self.reps.current_year:
                powerplant.status = globalNames.power_plant_status_operational
                if powerplant.commissionedYear == self.reps.current_year:
                    powerplant.age = 0
            elif powerplant.commissionedYear > self.reps.current_year:
                powerplant.status = globalNames.power_plant_status_inPipeline
            else:
                print("status not set", powerplant.name)

    def save_powerplants_status_and_age(self):
        print("     saving power plants status ...   ")
        self.reps.dbrw.stage_power_plant_status_and_age(self.reps.power_plants)

    def save_decommissioned_list(self):
        self.reps.dbrw.stage_list_decommissioned_plants(self.decommissioned_list )


from modules.defaultmodule import DefaultModule
from util.repository import Repository
import logging

class Dismantle(DefaultModule):
    """
    The class that decides to decomission some technologies
    """
    def __init__(self, reps: Repository):
        super().__init__('Dismantle decisions', reps)
        reps.dbrw.stage_init_power_plants_status()

    def act(self):
        self.set_powerplants_status() # set status according to operational time
        #producer = "Producer1" # TODO change

        for producer, producer_specs in self.reps.energy_producers.items():
            for plant in self.reps.get_power_plants_to_be_decommisioned(producer):
                # TODO is the power plant subsidized ? then dismantle
                print(plant.name)
                horizon = producer_specs.getPastTimeHorizon()
                requiredProfit = producer_specs.getDismantlingRequiredOperatingProfit()
                profit = self.calculateAveragePastOperatingProfit(plant, horizon)
                if profit <= requiredProfit:
                    logging.info("Dismantling power plant because it has an operating loss (incl O&M cost) on average in the last ",
                                 horizon," years: ", plant," was ", profit ," which is less than required: " , requiredProfit)
                    plant.dismantlePowerPlant(self.reps.current_tick)
                    self.reps.dbrw.stage_decommission_time(plant.name, self.reps.current_tick)
                    plant.status = self.reps.power_plant_status_decommissioned
                else:
                    print("dont dismantle but increase OPEX, because lifetime is over")
                    # TODO increase opex
        self.save_powerplants_status()


    def calculateAveragePastOperatingProfit(self, plant, horizon):
        averagePastOperatingProfit = 0
        rep = self.reps.dbrw.findFinancialPowerPlantProfitsForPlant(plant)
        if rep is not None:
            # if there is data than the one needed for the horizon then an average of those years are taken
            if self.reps.current_tick >= horizon:
                pastOperatingProfit = sum(int(x[1]) for x in rep['data'] if x[0] in range(-horizon, 1))
                averagePastOperatingProfit = pastOperatingProfit /  horizon
            else: # TODO for now, for the first years the availble past data is taken
                averagePastOperatingProfit = sum(int(x[1]) for x in rep['data'] if int(x[0])  < self.reps.current_tick )/ horizon
        return averagePastOperatingProfit

    def set_powerplants_status(self):
        for powerplantname, powerplant in self.reps.power_plants.items():
            technology = self.reps.power_generating_technologies[powerplant.technology.name]
            if powerplant.age > technology.expected_lifetime:
                print("plant to be decommisioned age", powerplant.age , "lifetime ",  technology.expected_lifetime)
                powerplant.status = self.reps.power_plant_status_to_be_decommissioned
            elif powerplant.commissionedYear <= self.reps.current_year:
                powerplant.status = self.reps.power_plant_status_operational
                if powerplant.commissionedYear == self.reps.current_year:
                    powerplant.age = 0
            elif powerplant.commissionedYear > self.reps.current_year:
                powerplant.status = self.reps.power_plant_status_inPipeline
            else:
                print("status not set", powerplant.name)

    def save_powerplants_status(self):
        print("     saving power plants status ...   ")
        self.reps.dbrw.stage_power_plant_status(self.reps.power_plants)




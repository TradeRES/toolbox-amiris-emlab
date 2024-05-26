from util import globalNames
from modules.defaultmodule import DefaultModule
from util.repository import Repository
import logging
from domain.CandidatePowerPlant import *
import pandas as pd

class Dismantle(DefaultModule):
    """
    1. one year is added to the age of the power plants if it is not the first simulation year (current tick == 0 )
    2. the status of the power plants is updated simply by commission year
    3. for plants that have passed their lifetime and if the simulation year , specified by user, is reached
        then the power plants aare decommissioned by profit
    4. If plants are not decommissioned but have passed their lifetime, their fixed costs is increased
    """

    def __init__(self, reps: Repository):
        super().__init__('Dismantle decisions', reps)
        self.decommissioned_list = (self.reps.decommissioned["Decommissioned"]).Done
        reps.dbrw.stage_init_power_plants_status()
       # reps.dbrw.stage_init_power_plants_fixed_costs()
        self.check_ids(reps)

    def act(self):

        if self.reps.current_tick > 0: # on the first year the age shouldnt be increased
            # add one year to the age of power plants
            self.add_one_year_to_age()
            self.decrease_variable_costs_and_efficiency()
        self.set_powerplants_status()  # set status according to operational time
        self.decommision_by_profit() # this should go after setting the status
        self.save_powerplants_status_and_age()
        self.save_decommissioned_list()

    def check_ids(self, reps):
        # this was added for debugging. The ids were different possibly because of not cleaning the DB at start
        for pp in reps.power_plants.values():
            if pp.is_new_installed():
                if pp.id != int(pp.name):
                    raise Exception("there is something wrong here Id " + str(pp.id) + " Name " + str(pp.name))

        # try:
        #     subquery = db_map.object_parameter_value_sq
        #     for row in db_map.query(subquery).filter(subquery.c.parameter_name == "status"):
        #         print(row.type)
        #
        #     statuses = dict()
        #     removable_object_ids = {object_id for object_id, status in statuses.items() if status != "Accepted"}
        #     db_map.cascade_remove_items(object=removable_object_ids)
        #     db_map.commit_session("Removed unacceptable objects.")
        # finally:
        #     db_map.connection.close()

    def decommision_by_profit(self):
        producer = self.reps.energy_producers[self.reps.agent]
        horizon = self.reps.pastTimeHorizon
        requiredProfit = producer.getDismantlingRequiredOperatingProfit()
        for plant in self.reps.get_power_plants_to_be_decommissioned(producer.name):   # TODO is the power plant subsidized ? then dismantle
            profit = self.calculateAveragePastOperatingProfit(plant, horizon, requiredProfit)
            if self.reps.current_tick < self.reps.pastTimeHorizon:
                print(str(plant.name) + "for initialization")
                self.set_plant_dismantled(plant)
            else:
                if profit <= requiredProfit:
                    print("{}  operating loss on average in the last {} years: was {} which is less than required:  {} " \
                          .format(plant.name, horizon, profit, requiredProfit))
                    self.set_plant_dismantled(plant)
                else:
                    pass

    def increase_fixed_cost(self, plant):
        print("dont dismantle but increase FOM of  {} ".format(plant.name))
        ModifiedOM = plant.getTechnology().get_fixed_operating_by_time_series(plant.age, plant.commissionedYear) * plant.get_actual_nominal_capacity()
        plant.setActualFixedOperatingCost(ModifiedOM)
        self.reps.dbrw.stage_fixed_operating_costs(plant)

    def decrease_variable_costs_and_efficiency(self):
        for powerplantname, plant in self.reps.power_plants.items():
            if plant.age < 0:
                pass # dont change data of power plants in pipeline.
            else:
                new_variable_costs = plant.getTechnology().get_variable_operating_by_time_series(plant.age)
                ModifiedEfficiency = plant.getTechnology().get_efficiency_by_time_series(plant.age) # same as geometric trend
                plant.setActualEfficiency(ModifiedEfficiency)
                plant.setActualVariableCosts(new_variable_costs)
            # saving new variable and efficiency costs
        self.reps.dbrw.stage_variable_costs_and_efficiency(self.reps.power_plants)

    def add_one_year_to_age(self):
        for powerplantname, powerplant in self.reps.power_plants.items():
            powerplant.age += 1
            powerplant.commissionedYear = self.reps.current_year - powerplant.age


    def calculateAveragePastOperatingProfit(self, plant, horizon, requiredProfit):
        profits = self.reps.get_financial_report_for_plant_KPI(plant.name, self.reps.typeofProfitforPastHorizon)
        if isinstance(profits, pd.Series):
            averagePastOperatingProfit = profits[-horizon:].mean() # takes the last horizon forecasts
        else:
            averagePastOperatingProfit = requiredProfit - 1
            print("no past profits for plant, dismantle", plant.name)
            raise Exception
        return averagePastOperatingProfit


    def set_powerplants_status(self):
        operator = self.reps.get_strategic_reserve_operator(self.reps.country)
        for powerplantname, powerplant in self.reps.power_plants.items():
            technology = self.reps.power_generating_technologies[powerplant.technology.name]
            if self.reps.decommission_from_input == True and powerplant.decommissionInYear is not None:
                if  self.reps.current_tick >= powerplant.endOfLife:
                    self.set_plant_dismantled(powerplant)
                    print(powerplant.name + "decommissioned from input")
            elif  powerplant.status == globalNames.power_plant_status_decommissioned_from_SR:
                self.set_plant_dismantled(powerplant)
                print(powerplant.name + "decommission from strategic reserve") # dont change status (set in SR algorithm) otherwise the status changes to operational
            elif  powerplant.status == globalNames.power_plant_status_strategic_reserve:
                print(powerplant.name + " in strategic reserve")
            elif powerplant.age > technology.expected_lifetime + technology.maximumLifeExtension:
                if self.reps.current_tick >= self.reps.start_dismantling_tick:
                    self.set_plant_dismantled(powerplant)
                else:
                    powerplant.status = globalNames.power_plant_status_operational
                    self.increase_fixed_cost(powerplant)
            elif  powerplant.age >= technology.expected_lifetime: # hasnt passed maximum lifetime extension
                if self.reps.current_tick >= self.reps.start_dismantling_tick:
                    # dont decommission yet but increase costs
                    powerplant.status = globalNames.power_plant_status_to_be_decommissioned
                    self.increase_fixed_cost(powerplant)
                else:
                    powerplant.status = globalNames.power_plant_status_operational
                    self.increase_fixed_cost(powerplant)
            elif powerplant.age >= 0:
                powerplant.status = globalNames.power_plant_status_operational
            elif powerplant.age < 0:
                powerplant.status = globalNames.power_plant_status_inPipeline
            else:
                print("status not set", powerplant.name)

    def set_plant_dismantled(self, plant):
        """
        Decommissioned power plants are saved in a list, and this list is read in every module.
        Power plants in this list are then not read.
        """
        plant.status = globalNames.power_plant_status_decommissioned
        plant.setdismantleYear(self.reps.current_year)
        self.reps.dbrw.stage_decommission_year(plant.name, self.reps.current_year)
        self.decommissioned_list.append(plant.name)

    def save_powerplants_status_and_age(self):
        self.reps.dbrw.stage_power_plant_status_and_age(self.reps.power_plants)

    def save_decommissioned_list(self):
        self.reps.dbrw.stage_list_decommissioned_plants(self.decommissioned_list)


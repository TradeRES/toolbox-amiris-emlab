from util import globalNames
from modules.defaultmodule import DefaultModule
from util.repository import Repository
import logging
from spinedb_api import DatabaseMapping
import pandas as pd

class Dismantle(DefaultModule):
    """
    The class that decides to decomission some technologies
    """

    def __init__(self, reps: Repository):
        super().__init__('Dismantle decisions', reps)
        self.decommissioned_list = (self.reps.decommissioned["Decommissioned"]).Decommissioned
        reps.dbrw.stage_init_power_plants_status()
        reps.dbrw.stage_init_power_plants_fixed_costs()

    def act(self):
        self.add_one_year_to_age() # add one year to the age of power plants
        self.set_powerplants_status()  # set status according to operational time
        self.decommision_by_age_and_profit()
        self.save_powerplants_status_and_age()
        self.save_decommissioned_list()

       # self.erase_bids_class()

    def erase_bids_class(self):
        # todo finish this if bids are being erased then the awarded capapcity of CM should also be saved.
        db_map = DatabaseMapping(self.reps.dbrw.db_urls[0])
        def class_id_for_name(name):
            return db_map.query(db_map.entity_class_sq).filter(db_map.entity_class_sq.c.name == name).first().id
        try:
            id_to_remove = class_id_for_name("Bids")
            db_map.cascade_remove_items(**{"object_class": {id_to_remove}})
            db_map.commit_session("Removed ")
        finally:
            db_map.connection.close()
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

    def decommision_by_age_and_profit(self):
        for producer, producer_specs in self.reps.energy_producers.items():
            for plant in self.reps.get_power_plants_to_be_decommissioned(producer):
                # TODO is the power plant subsidized ? then dismantle
                horizon = self.reps.pastTimeHorizon
                requiredProfit = producer_specs.getDismantlingRequiredOperatingProfit()
                if self.reps.current_tick >= self.reps.start_year_dismantling:
                    profit = self.calculateAveragePastOperatingProfit(plant, horizon)
                    if profit <= requiredProfit:
                        logging.info("Dismantling power plant because it has an operating loss (incl O&M cost) on average in the last %s years: %s was %s which is less than required: "
                                .format(horizon, plant.name, profit, requiredProfit))
                        plant.dismantlePowerPlant(self.reps.current_tick)
                        self.reps.dbrw.stage_decommission_time(plant.name, self.reps.current_tick)
                        plant.status = globalNames.power_plant_status_decommissioned
                        self.decommissioned_list.append(plant.name)
                    else:
                        logging.info("dont dismantle ( enough profits) but increase fixed OPEX of %s ".format(plant.name))
                        ModifiedOM = plant.getActualFixedOperatingCost() * (
                                1 + plant.technology.getFixedOperatingCostModifierAfterLifetime())
                        plant.setActualFixedOperatingCost(ModifiedOM)
                        # saving
                        self.reps.dbrw.stage_fixed_operating_costs(plant)
                else:
                    logging.info(" for the first years dont dismantle (initialization) but increase fixed OPEXof %s ".format(plant.name))
                    if plant.age < plant.technology.getExpectedLifetime():
                        print("Age is less than expected life time")
                    else:
                        ModifiedOM = plant.getActualFixedOperatingCost() * (
                                1 + plant.technology.getFixedOperatingCostModifierAfterLifetime())
                        plant.setActualFixedOperatingCost(ModifiedOM)
                        self.reps.dbrw.stage_fixed_operating_costs(plant)


    def add_one_year_to_age(self):
        for powerplantname, powerplant in self.reps.power_plants.items():
            powerplant.age += 1

    def calculateAveragePastOperatingProfit(self, plant, horizon):
        averagePastOperatingProfit = 0
        rep = self.reps.dbrw.findFinancialValueForPlant(plant, self.reps.typeofProfitforPastHorizon)
        # self.reps.typeofProfitforPastHorizon is defined in the config exce and can be "totalProfits" or "irr"
        if rep is not None:
            # if there is data than the one needed for the horizon then an average of those years are taken
            if self.reps.current_tick >= horizon:
                past_operating_profit_all_years = pd.Series(dict(rep["data"]))
                indices = list(range(self.reps.current_tick-horizon, self.reps.current_tick))
                past_operating_profit = past_operating_profit_all_years.loc[ list(map(str,indices))].values
                averagePastOperatingProfit =  sum(list(map(float,past_operating_profit))) / len(indices)
            else:  # Attention for now, for the first years the available past data is taken
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

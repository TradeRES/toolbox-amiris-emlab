# update the price of fuel, capex, opex, to the look ahead year
# update e demand
# assets age + look ahead
# dismantle plants that are too old or too unprofitable
# any plants that are supposed to be built at that time?
from emlabpy.modules.defaultmodule import DefaultModule
from emlabpy.util.repository import Repository


class Dismantle(DefaultModule):
    """
    The class that decides to invest in some technologies
    """

    def __init__(self, reps: Repository):
        super().__init__('Dismantle decisions', reps)
        # self.current_tick = current_tick
        # self.power_plants = power_plants
        #reps.dbrw.stage_init_power_plant_status()

    def act(self):
        set_powerplants_status(self)



def set_powerplants_status(self):
    powerplants_status=[]
    for powerplantname, powerplant in self.reps.power_plants.items():
        technology = self.reps.power_generating_technologies[powerplant.technology]
        if powerplant.age > technology.expected_lifetime:
            powerplant.status = self.reps.power_plant_status_decommissioned
        elif powerplant.commissionedYear <= self.reps.current_year:
            powerplant.status = self.reps.power_plant_status_operational
        elif powerplant.commissionedYear > self.reps.current_year:
            powerplant.status = self.reps.power_plant_status_inPipeline
        else:
            print("status not set")

        if technology.intermittent:
            powerplanttype = "VariableRenewableOperator"
        else:
            powerplanttype = "ConventionalPlantOperator"

        powerplants_status.append([powerplanttype, powerplantname,"Status", powerplant.status, "0"])
    self.reps.dbrw.stage_power_plant_status(powerplants_status)


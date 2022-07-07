"""
This file handles all (temporary) payments and allocations.
COMPETES will be doing this, but for the development of the MarketStabilityReserve an allocation of EUAs was
necessary.

Jim Hommes - 13-5-2021
"""
from modules.defaultmodule import DefaultModule
from util.repository import Repository


class PayAndBankCO2Allowances(DefaultModule):
    """
    This class describes the actor behaviour in buying CO2 Allowances.
    If possible, the actor will buy 150% of necessary credits.
    Otherwise, the actor will buy 100% of necessary credits.
    If that's not possible, the actor will try to buy the difference required for the actor to have sufficient credits.
    """
    def __init__(self, reps: Repository):
        super().__init__("Payment Module: CO2 Payments and Banking", reps)

    def act(self):
        for power_plant in self.reps.power_plants.values():
            market = self.reps.get_co2_market_for_plant(power_plant)
            mcp = self.reps.get_market_clearing_point_for_market_and_time(market, self.reps.current_tick)

            total_capacity = self.reps.get_total_accepted_amounts_by_power_plant_and_tick_and_market(power_plant,
                                                                                                     self.reps.current_tick)
            emission_intensity = power_plant.calculate_emission_intensity(self.reps)
            emissions = total_capacity * emission_intensity

            if 1.5 * emissions * mcp.price <= int(power_plant.owner.parameters['cash']):
                power_plant.owner.parameters['cash'] = int(power_plant.owner.parameters['cash']) - 1.5 * emissions * mcp.price
                power_plant.banked_allowances[self.reps.current_tick] = 1.5 * emissions
            elif emissions * mcp.price <= int(power_plant.owner.parameters['cash']):
                power_plant.owner.parameters['cash'] = int(power_plant.owner.parameters['cash']) - emissions * mcp.price
                power_plant.banked_allowances[self.reps.current_tick] += emissions
            elif power_plant.banked_allowances[self.reps.current_tick] < emissions and \
                    (power_plant.banked_allowances[self.reps.current_tick] - emissions) * mcp.price <= int(power_plant.owner.parameters['cash']):
                power_plant.parameters['cash'] = int(power_plant.parameters['cash']) - (power_plant.banked_allowances - emissions) * mcp.price
                power_plant.banked_allowances[self.reps.current_tick] += (power_plant.banked_allowances[self.reps.current_tick] - emissions)
            self.reps.dbrw.stage_payment_co2_allowances(power_plant, int(power_plant.owner.parameters['cash']),
                                                        power_plant.banked_allowances[self.reps.current_tick], self.reps.current_tick)


class UseCO2Allowances(DefaultModule):
    """
    This class handles the actual usage of credits and their return to the market.
    """
    def __init__(self, reps: Repository):
        super().__init__("Payment Module: Use CO2 Allowances and Subtract From Banked", reps)

    def act(self):
        for power_plant in self.reps.power_plants.values():
            total_capacity = self.reps.get_total_accepted_amounts_by_power_plant_and_tick_and_market(power_plant,
                                                                                                     self.reps.current_tick)
            emission_intensity = power_plant.calculate_emission_intensity(self.reps)
            power_plant.banked_allowances[self.reps.current_tick] -= total_capacity * emission_intensity
            self.reps.dbrw.stage_co2_allowances(power_plant, power_plant.banked_allowances[self.reps.current_tick],
                                                self.reps.current_tick)

        # Surplus of EAUs gets added to MSR
        for msr in self.reps.market_stability_reserves.values():
            euas_in_circulation = self.reps.get_allowances_in_circulation(msr.zone, self.reps.current_tick)
            cap = self.reps.get_government().co2_cap_trend.get_value(self.reps.current_tick)
            if euas_in_circulation < cap:
                msr.reserve[self.reps.current_tick] += (cap - euas_in_circulation)


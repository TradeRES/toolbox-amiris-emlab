"""
The file responsible for all CO2 Market classes.

Jim Hommes - 13-4-2021
"""
from modules.marketmodule import MarketModule
from util.repository import Repository
import math


class CO2MarketDetermineCO2Price(MarketModule):
    """
    This class determines the CO2 Price based on the Willingness To Pay of the PowerPlants.
    It does so by evaluating the profits and emissions of last year.
    """

    def __init__(self, reps: Repository):
        super().__init__('CO2 Market: Determine CO2 Price', reps)
        reps.dbrw.stage_init_market_clearing_point_structure()

    def act(self):
        # For every CO2Market
        for market in self.reps.co2_markets.values():
            co2price = 0
            if self.reps.current_tick == 0:
                # If first tick, COMPETES has not run yet. Set to CO2 substance cost
                # co2price = self.reps.substances['co2'].get_price_for_tick(0)
                co2price = 21.165   # Value from COMPETES run
            else:
                # If not first tick, base CO2 Price of profits/emissions last year
                amount_of_years_to_look_back = self.reps.time_step

                # If implemented, take MarketStabilityReserve into account
                msr = self.reps.get_market_stability_reserve_for_market(market)
                # CO2Cap is in EU ETS - 1 for 1 ton CO2
                if msr is not None:
                    co2_cap = self.reps.get_government().co2_cap_trend.get_value(self.reps.current_tick - amount_of_years_to_look_back) - \
                              self.reps.get_allowances_in_circulation(self.reps.zones[market.parameters['zone']], self.reps.current_tick)\
                              + msr.flow
                else:
                    co2_cap = self.reps.get_government().co2_cap_trend.get_value(self.reps.current_tick - amount_of_years_to_look_back) - \
                              self.reps.get_allowances_in_circulation(self.reps.zones[market.parameters['zone']], self.reps.current_tick)

                # Get profits, emissions and calculate WTP
                profits_per_plant = self.reps.get_power_plant_operational_profits_by_tick_and_market(
                    self.reps.current_tick - amount_of_years_to_look_back, self.reps.electricity_spot_markets['DutchElectricitySpotMarket'])
                emissions_per_plant = self.reps.get_power_plant_emissions_by_tick(self.reps.current_tick - amount_of_years_to_look_back)
                willingness_to_pay_per_plant = {
                    key: value / emissions_per_plant[key] for (key, value)
                    in profits_per_plant.items() if emissions_per_plant[key] != 0
                }

                emission_hedging_correction = 1

                co2_from_exports = 0
                if 'Exports' in self.reps.exports.keys():
                    co2_from_exports = self.reps.exports['Exports'].amount_of_co2 * emission_hedging_correction

                # Determine CO2 Price based on the WTP merit order
                co2price = max(willingness_to_pay_per_plant.values())
                total_emissions = 0
                sorted_wtp = sorted(willingness_to_pay_per_plant.items(),
                                    key=lambda item: item[1], reverse=True)

                for (power_plant_name, wtp) in sorted_wtp:
                    emissions_per_plant_rounded = math.ceil(emissions_per_plant[power_plant_name])
                    if co2_cap >= total_emissions + emissions_per_plant_rounded * emission_hedging_correction:
                        total_emissions += emissions_per_plant_rounded * emission_hedging_correction
                        co2price = wtp
                    else:
                        break

            # Check if CO2Price is below the Government's min CO2 price
            print(co2price)
            co2price = self.floor_co2price(co2price)
            self.reps.create_or_update_market_clearing_point(market, co2price, 0, self.reps.current_tick)

    def floor_co2price(self, co2price):
        """Check if CO2Price is below the Government's min CO2 price"""
        return max(co2price, self.reps.get_government().co2_min_price_trend.get_value(self.reps.current_tick))

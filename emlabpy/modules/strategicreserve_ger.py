"""
The file responsible for all German strategic reserve operations.

Bart van Nobelen - 26-05-2022
"""

from util import globalNames
from modules.marketmodule import MarketModule
from util.repository import Repository
from domain.StrategicReserveOperator import StrategicReserveOperator


class StrategicReserveSubmitBids_ger(MarketModule):
    """
    The class that submits all bids to the Strategic Reserve Market
    """

    def __init__(self, reps: Repository):
        super().__init__('EM-Lab Strategic Reserve: Submit Bids', reps)
        reps.dbrw.stage_init_bids_structure()
        reps.dbrw.stage_init_sr_results_structure()
        self.agent = reps.energy_producers[reps.agent]
        self.operator = self.reps.get_strategic_reserve_operator(self.reps.country)

    def act(self):
        # Retrieve every power plant in the active energy producer for the defined country
        for powerplant in self.reps.get_power_plants_to_participate_inSR():
            # Retrieve the active capacity market and power plant capacity
            market = self.reps.get_capacity_market_for_plant(powerplant)
            power_plant_capacity = powerplant.get_actual_nominal_capacity()
            Bid = powerplant.technology.get_variable_operating_by_time_series(
                powerplant.age + self.operator.forward_years_SR)
            Bid = Bid + powerplant.technology.fuel.futurePrice[
                self.operator.forward_years_SR + self.reps.current_year] / powerplant.technology.get_efficiency_by_time_series(
                powerplant.age + self.operator.forward_years_SR)

            # Bid = powerplant.getActualFixedOperatingCost()
            # if powerplant.age < powerplant.technology.expected_lifetime:
            #     Bid += powerplant.getLoan().getAmountPerPayment()  # if power plant is reaches its lifetime it should not have anymore payments left
            # Bid = Bid/powerplant.capacity
            # variable_costs = powerplant.technology.get_variable_operating_by_time_series(powerplant.age + self.operator.forward_years_SR) # actually this could be raised to one year more
            # Place bids on market only if plant is conventional (full capacity at cost price per MW)
            if powerplant.technology.type == 'ConventionalPlantOperator':
                self.reps.create_or_update_power_plant_CapacityMarket_plan(powerplant, self.agent,
                                                                           market, power_plant_capacity,
                                                                           Bid, self.reps.current_tick)


class StrategicReserveAssignment_ger(MarketModule):
    """
    The class clearing the Strategic Reserve Market and assigning them to the Strategic Reserve Operator
    """

    def __init__(self, reps: Repository):
        super().__init__('EM-Lab Strategic Reserve: Assign Plants', reps)
        reps.dbrw.stage_init_sr_results_structure()
        reps.dbrw.stage_init_capacitymechanisms_structure()
        self.operator = None
        self.reserveFull = False

    def act(self):
        # Retrieve the active capacity market
        market = self.reps.get_capacity_market_in_country(self.reps.country)

        # Retrieve the active strategic reserve operator in the country
        self.operator = self.reps.get_strategic_reserve_operator(self.reps.country)

        # Retrieve peak load volume of market
        # peak_load =self.reps.get_realized_peak_demand_by_year(self.reps.current_year) this was making volatile reserve
        spot_market = self.reps.get_spot_market_in_country(self.reps.country)
        peak_load = spot_market.get_peak_load_per_year(self.reps.current_year)

        # get peak load from weather
        expectedDemandFactor = self.reps.dbrw.get_calculated_simulated_fuel_prices_by_year("electricity",
                                                                                           globalNames.future_prices,
                                                                                           (self.reps.current_year + self.operator.forward_years_SR))
        # The expected peak load volume is defined as the base peak load with a demand factor for the defined year
        peakExpectedDemand = peak_load * (expectedDemandFactor)

        # Calculate needed strategic reserve capacity
        strategic_reserve_capacity = peakExpectedDemand * self.operator.getReserveVolumePercentSR()

        # Retrieve the bids on the capacity market, sorted in descending order on price
        sorted_ppdp = self.reps.get_descending_sorted_power_plant_dispatch_plans_by_SRmarket(market,
                                                                                             self.reps.current_tick)
        list_of_plants = []
        # Contract plants to Strategic Reserve Operator
        contracted_strategic_reserve_capacity = 0

        for ppdp in sorted_ppdp:
            if self.reserveFull == True:
                break
            else:
            # If plants are already in strategic reserve they have to be until end of life
            # todo: owner to 'StrategicReserveOperator' and price to SR price?

                power_plant = self.reps.get_power_plant_by_name(ppdp.plant)
                if power_plant.status == globalNames.power_plant_status_strategic_reserve: # last year in Strategic reserve
                    if self.reserveFull == False:
                        if power_plant.years_in_SR >= self.operator.max_years_in_reserve:  # Has already been in reserve for 4 years
                            power_plant.status = globalNames.power_plant_status_decommissioned_from_SR
                            self.reps.dbrw.stage_power_plant_status(power_plant)
                            print("to be decommissioned because of >" + str(self.operator.max_years_in_reserve) + " years in SR "  +  power_plant.name)
                        else:  # Has been less than 4 years. Keep contracting
                            ppdp.status = globalNames.power_plant_status_strategic_reserve
                            ppdp.accepted_amount = ppdp.amount
                            self.reps.increase_year_in_sr(power_plant)
                            contracted_strategic_reserve_capacity += ppdp.amount
                            list_of_plants.append(ppdp.plant)
                            print("years in reserve " + str(power_plant.years_in_SR))

                            if (contracted_strategic_reserve_capacity) > strategic_reserve_capacity:
                                self.reserveFull = True
                                break
                            else:
                                pass
                    else:
                        raise Exception("should have stopped earlier")


                # If strategic reserve is not filled yet contract additional new plants
                elif self.reserveFull == False:
                    print("new in Reserve")
                    ppdp.status = globalNames.power_plant_status_strategic_reserve
                    ppdp.accepted_amount = ppdp.amount
                    # Add plant to the list of the StrategicReserveOperator so that next year they are also accepted
                    list_of_plants.append(ppdp.plant)
                    # Change plant status and increase age
                    power_plant = self.reps.get_power_plant_by_name(ppdp.plant)
                    self.reps.update_power_plant_status_ger_first_year(power_plant)
                    contracted_strategic_reserve_capacity += ppdp.amount
                    if (contracted_strategic_reserve_capacity) > strategic_reserve_capacity:
                        self.reserveFull = True
                        break
                else:
                    print(self.isReservedCleared )
                    raise Exception("Sorry, no numbers below zero")

        # Pass the contracted plants to the strategic reserve operator
        self.operator.setPlants(list_of_plants)

        # Pass the total contracted volume to the strategic reserve operator
        self.operator.setReserveVolume(contracted_strategic_reserve_capacity)

        # Pay the contracted plants in the strategic reserve and save the revenues to the power plants
        self.createCashFlowforSR(market)

        # Save the SR operator variables to the SR operator of the country
        self.reps.create_or_update_StrategicReserveOperator(self.operator.name,
                                                            self.operator.getZone(),
                                                            self.operator.getReserveVolume(),
                                                            self.operator.getCash(),
                                                            self.operator.revenues_per_year,
                                                            self.operator.getPlants())

    # Cashflow function for the operation of the strategic reserve
    def createCashFlowforSR(self, market):
        accepted_ppdp = self.reps.get_accepted_SR_bids()
        for accepted in accepted_ppdp:
            plant = self.reps.power_plants[accepted.plant]
            # Fixed operating costs of plants
            fixed_operating_costs = plant.actualFixedOperatingCost
            # Retrieve dispatch data of plants for variable costs and revenues
            dispatch = self.reps.get_power_plant_electricity_dispatch(plant.id)
            # Costs to be paid by Strategic Reserve Operator and to be received
            if dispatch is None:
                SR_payment_to_plant = fixed_operating_costs
                SR_payment_to_operator = 0
                print("fixed_operating_costs " + str(fixed_operating_costs))
            else:
                SR_payment_to_plant = fixed_operating_costs + dispatch.variable_costs
                SR_payment_to_operator = dispatch.revenues
                print("variable costs " + str(dispatch.variable_costs))
                print("fixed_operating_costs " + str(fixed_operating_costs))

            if plant.age < plant.technology.expected_lifetime:
                # if power plant is reaches its lifetime it should not have anymore payments left
                print("SR_payment_to_plant " + plant.name)
                SR_payment_to_plant += plant.getLoan().getAmountPerPayment()
            # Payment (fixed costs and variable costs ) from operator to plant
            self.reps.createCashFlow(self.operator, plant,
                                     SR_payment_to_plant, globalNames.CF_STRRESPAYMENT, self.reps.current_tick,
                                     self.reps.power_plants[accepted.plant])
            # saving the revenues to the power plants
            self.reps.dbrw.stage_CM_revenues(accepted.plant, SR_payment_to_plant, self.reps.current_tick)

            # Payment (market revenues) from market to operator
            self.reps.createCashFlow(market, self.operator,
                                     SR_payment_to_operator, globalNames.CF_STRRESPAYMENT, self.reps.current_tick,
                                     self.reps.power_plants[accepted.plant])

            self.operator.revenues_per_year += SR_payment_to_operator

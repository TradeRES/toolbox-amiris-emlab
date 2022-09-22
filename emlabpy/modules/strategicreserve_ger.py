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

    def act(self):
        # Retrieve every power plant in the active energy producer for the defined country
        for powerplant in self.reps.get_operational_and_to_be_decommissioned_power_plants_by_owner(
                self.reps.agent):
            # Retrieve the active capacity market and power plant capacity
            market = self.reps.get_capacity_market_for_plant(powerplant)
            power_plant_capacity = powerplant.get_actual_nominal_capacity()

            # Get Variable and Fixed Operating Costs
            fixed_operating_costs = powerplant.getActualFixedOperatingCost()
            variable_costs = powerplant.calculate_marginal_cost_excl_co2_market_cost(self.reps, self.reps.current_tick)

            # Calculate normalised costs
            normalised_costs = variable_costs + (fixed_operating_costs/power_plant_capacity)

            # Place bids on market only if plant is conventional (full capacity at cost price per MW)
            if powerplant.technology.type == 'ConventionalPlantOperator':
                self.reps.create_or_update_power_plant_CapacityMarket_plan(powerplant, self.agent,
                                                                           market, power_plant_capacity,
                                                                           normalised_costs, self.reps.current_tick)

class StrategicReserveAssignment_ger(MarketModule):
    """
    The class clearing the Strategic Reserve Market and assigning them to the Strategic Reserve Operator
    """

    def __init__(self, reps: Repository):
        super().__init__('EM-Lab Strategic Reserve: Assign Plants', reps)
        reps.dbrw.stage_init_sr_results_structure()
        reps.dbrw.stage_init_capacitymechanisms_structure()
        self.operator = None

    def act(self):
        # Retrieve the active capacity market
        market = self.reps.get_capacity_market_in_country(self.reps.country)

        # Retrieve the active strategic reserve operator in the country
        self.operator = self.reps.get_strategic_reserve_operator(self.reps.country)

        # Retrieve peak load volume of market
        peak_load = max(self.reps.get_hourly_demand_by_country(market.country)[1])
        expectedDemandFactor = self.reps.dbrw.get_calculated_simulated_fuel_prices_by_year("electricity",
                                                                                           globalNames.simulated_prices,
                                                                                           self.reps.current_year)
        # The expected peak load volume is defined as the base peak load with a demand factor for the defined year
        peakExpectedDemand = peak_load * (expectedDemandFactor)

        # Calculate needed strategic reserve capacity
        strategic_reserve_capacity = peakExpectedDemand * self.operator.getReserveVolumePercentSR()

        # Retrieve SR price
        SR_price = self.operator.getReservePriceSR()

        # Retrieve the bids on the capacity market, sorted in descending order on price
        sorted_ppdp = self.reps.get_descending_sorted_power_plant_dispatch_plans_by_SRmarket(market, self.reps.current_tick)

        # Retrieve plants already contracted in reserve
        list_of_plants = self.operator.list_of_plants
        # Remove decommissioned plants from reserve
        for plant in (self.reps.decommissioned["Decommissioned"]).Decommissioned:
            if plant in list_of_plants:
                list_of_plants.remove(plant)

        # Contract plants to Strategic Reserve Operator
        contracted_strategic_reserve_capacity = 0

        for ppdp in sorted_ppdp:
            # If plants are already in strategic reserve they have to be until end of life
            if ppdp.plant in list_of_plants:
                contracted_strategic_reserve_capacity += ppdp.amount
                ppdp.status = globalNames.power_plant_status_strategic_reserve
                ppdp.accepted_amount = ppdp.amount
                # Change plant status to 'InStrategicReserve', owner to 'StrategicReserveOperator' and price to SR price
                self.reps.update_power_plant_status(ppdp.plant, SR_price)
            # If strategic reserve is not filled yet contract additional new plants
            elif (contracted_strategic_reserve_capacity + ppdp.amount) <= strategic_reserve_capacity:
                contracted_strategic_reserve_capacity += ppdp.amount
                ppdp.status = globalNames.power_plant_status_strategic_reserve
                ppdp.accepted_amount = ppdp.amount
                # Add plant to the list of the StrategicReserveOperator
                list_of_plants.append(ppdp.plant)
                # Change plant status and increase age
                self.reps.update_power_plant_status_ger_first_year(ppdp.plant, SR_price)
            else:
                # When strategic reserve is full nothing actually changes for the power plant
                ppdp.accepted_amount = 0

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
            else:
                SR_payment_to_plant = fixed_operating_costs + dispatch.variable_costs
                SR_payment_to_operator = dispatch.revenues

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

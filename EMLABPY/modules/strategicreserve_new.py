"""
The file responsible for all strategic reserve operations.

Bart van Nobelen - 26-05-2022
"""

from util import globalNames
from modules.marketmodule import MarketModule
from util.repository import Repository
from domain.StrategicReserveOperator import StrategicReserveOperator

class StrategicReserveSubmitBids(MarketModule):
    """
    The class that submits all bids to the Strategic Reserve Market
    """

    def __init__(self, reps: Repository):
        super().__init__('EM-Lab Strategic Reserve: Submit Bids', reps)
        # reps.dbrw.stage_init_plant_status()

    def act(self):
        # For every EnergyProducer
        for energy_producer in self.reps.energy_producers.values():

            # For every PowerPlant owned by energyProducer
            for powerplant in self.reps.get_operational_and_to_be_decommissioned_power_plants_by_owner(
                    energy_producer.name):
                # Retrieve vars
                market = self.reps.get_capacity_market_for_plant(powerplant)
                capacity = powerplant.get_actual_nominal_capacity()

                # Get Marginal Cost and Fixed Operating Costs
                dispatch = self.reps.get_power_plant_electricity_dispatch(powerplant.id)
                fixed_operating_costs = powerplant.get_actual_fixed_operating_cost()
                # variable_costs = powerplant.calculate_marginal_cost_excl_co2_market_cost(self.reps, self.reps.current_tick)
                # variable_costs = dispatch.variable_costs

                # Calculate normalised costs
                if dispatch is None:
                    normalised_costs = fixed_operating_costs/capacity
                else:
                    normalised_costs = (dispatch.variable_costs + fixed_operating_costs)/capacity

                # If only conventional plants are able to participate, add the following line
                # if powerplant.technology.type == 'ConventionalPlantOperator':

                # Place bids on market (full capacity at cost price per MW)
                # Remove this if statement when everything works
                if market != None:
                    self.reps.create_or_update_power_plant_StrategicReserve_plan(powerplant, energy_producer,
                                                                               market, capacity, normalised_costs,
                                                                               self.reps.current_tick)

class StrategicReserveAssignment(MarketModule):
    """
    The class clearing the Strategic Reserve Market and assigning them to the Strategic Reserve Operator
    """

    def __init__(self, reps: Repository, operator: StrategicReserveOperator):
        super().__init__('EM-Lab Strategic Reserve: Assign Plants', reps)
        self.operator = operator
        # reps.dbrw.stage_init_bids_structure()

    def act(self):
        # Assign plants to Strategic Reserve per region
        for market in self.reps.capacity_markets.values():
            # Retrieve vars
            market_capacity = self.reps.calculateCapacityOfPowerPlantsInMarket(market.name)
            strategic_reserve_capacity = market_capacity * self.operator.getReserveVolumePercentSR()
            SR_price = self.operator.getReservePriceSR()

            # Sort the bids in descending order
            sorted_ppdp = self.reps.get_descending_sorted_power_plant_dispatch_plans_by_SRmarket(market)

            # Set the strategic reserve zone to the same as the market
            self.operator.setZone(market.parameters['zone'])

            # Contract plants to Strategic Reserve
            contracted_strategic_reserve_volume = 0

            for ppdp in sorted_ppdp:
                if (contracted_strategic_reserve_volume + ppdp.amount) <= strategic_reserve_capacity:
                    contracted_strategic_reserve_volume += ppdp.amount
                    ppdp.status = globalNames.power_plant_status_strategic_reserve
                    ppdp.accepted_amount = ppdp.amount
                    # Add plant to the list of the StrategicReserveOperator
                    self.operator.setPlants(ppdp.plant)
                    self.reps.set_power_plants_in_SR(ppdp.plant)
                    # Change plant status to 'InStrategicReserve', owner to 'StrategicReserveOperator' and price to SR price
                    self.reps.update_power_plant_status(ppdp.plant, SR_price)
                else:
                    # When strategic reserve is full nothing actually changes for the power plant
                    ppdp.accepted_amount = 0

            # Pass the total contracted volume to the strategic reserve operator
            self.operator.setReserveVolume(contracted_strategic_reserve_volume)

            # Pay the contracted plants in the strategic reserve
            self.createCashFlowforSR(self.operator, market)

    # Cashflow function for the operation of the strategic reserve
    def createCashFlowforSR(self, operator, market):
        accepted_ppdp = self.reps.get_accepted_SR_bids()
        for accepted in accepted_ppdp:
            # Fixed operating costs of plants
            # fixed_operating_cost_1 = self.reps.get_fixed_costs_of_SR_plant(accepted.plant)
            fixed_operating_costs = accepted.plant.get_actual_fixed_operating_cost()
            # Variable operating costs of plants
            dispatch = self.reps.get_power_plant_electricity_dispatch(accepted.plant.id)
            # Costs to be paid by Strategic Reserve Operator
            if dispatch is None:
                SR_payment_to_plant = fixed_operating_costs
                SR_payment_to_operator = 0
            else:
                SR_payment_to_plant = fixed_operating_costs + dispatch.variable_costs
                SR_payment_to_operator = dispatch.revenues

            # from_agent, to, amount, type, time, plant
            # Payment from operator to plant
            self.reps.createCashFlow(operator, self.reps.energy_producers[accepted.bidder.name],
                                     SR_payment_to_plant, "CAPMARKETPAYMENT", self.reps.current_tick,
                                     self.reps.power_plants[accepted.plant.name])
            # Payment from market to operator
            self.reps.createCashFlow(market, operator,
                                     SR_payment_to_operator, "CAPMARKETPAYMENT", self.reps.current_tick,
                                     self.reps.power_plants[accepted.plant.name])
            # Update cash of Strategic Reserve Operator
            # self.operator.setCash(-SR_payment)
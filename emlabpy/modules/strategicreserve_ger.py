"""
The file responsible for all strategic reserve operations.

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
        self.agent = reps.energy_producers[reps.agent]

    def act(self):
        # For every PowerPlant owned by energyProducer
        for powerplant in self.reps.get_operational_and_to_be_decommissioned_power_plants_by_owner(
                self.reps.agent):
            # Retrieve vars
            market = self.reps.get_capacity_market_for_plant(powerplant)
            power_plant_capacity = powerplant.get_actual_nominal_capacity()

            # Get Variable and Fixed Operating Costs
            fixed_operating_costs = powerplant.getActualFixedOperatingCost()
            variable_costs = powerplant.calculate_marginal_cost_excl_co2_market_cost(self.reps, self.reps.current_tick)

            # Calculate normalised costs
            normalised_costs = variable_costs + (fixed_operating_costs/power_plant_capacity)

            # Place bids on market only if plant is conventional (full capacity at cost price per MW)
            if market != None and powerplant.technology.type == 'ConventionalPlantOperator':
                self.reps.create_or_update_power_plant_CapacityMarket_plan(powerplant, self.agent,
                                                                           market, power_plant_capacity,
                                                                           normalised_costs, self.reps.current_tick)

class StrategicReserveAssignment_ger(MarketModule):
    """
    The class clearing the Strategic Reserve Market and assigning them to the Strategic Reserve Operator
    """

    def __init__(self, reps: Repository, operator: StrategicReserveOperator):
        super().__init__('EM-Lab Strategic Reserve: Assign Plants', reps)
        reps.dbrw.stage_init_sr_operator_structure()
        self.operator = operator

    def act(self):
        # Assign plants to Strategic Reserve per region
        for market in self.reps.capacity_markets.values():
            # Set the strategic reserve zone to the same as the market
            self.operator.setZone(market.country)

            # Retrieve peak load volume of market
            peak_load_volume = max(self.reps.get_hourly_demand_by_country(market.country)[1])

            # Calculate needed strategic reserve capacity
            strategic_reserve_capacity = peak_load_volume * self.operator.getReserveVolumePercentSR()

            # Retrieve SR price
            SR_price = self.operator.getReservePriceSR()

            # Sort the bids in descending order
            sorted_ppdp = self.reps.get_descending_sorted_power_plant_dispatch_plans_by_SRmarket(market, self.reps.current_tick)

            # Contract plants to Strategic Reserve Operator
            contracted_strategic_reserve_capacity = 0
            SRO_name = "SRO_" + market.country
            try:
                SR_operator = self.reps.sr_operator[SRO_name]
            except:
                SR_operator = self.operator

            for ppdp in sorted_ppdp:
                # If plants are already in strategic reserve they have to be until end of life
                if ppdp.name in SR_operator.list_of_plants:
                    contracted_strategic_reserve_capacity += ppdp.amount
                    ppdp.status = globalNames.power_plant_status_strategic_reserve
                    ppdp.accepted_amount = ppdp.amount
                    self.operator.setPlants(ppdp.plant)
                    # Change plant status
                    self.reps.update_power_plant_status(ppdp.plant, SR_price)
                # If strategic reserve is not filled yet contract additional new plants
                elif (contracted_strategic_reserve_capacity + ppdp.amount) <= strategic_reserve_capacity:
                    contracted_strategic_reserve_capacity += ppdp.amount
                    ppdp.status = globalNames.power_plant_status_strategic_reserve
                    ppdp.accepted_amount = ppdp.amount
                    # Add plant to the list of the StrategicReserveOperator
                    self.operator.setPlants(ppdp.plant)
                    # Change plant status and increase age
                    self.reps.update_power_plant_status_ger_first_year(ppdp.plant, SR_price)
                else:
                    # When strategic reserve is full nothing actually changes for the power plant
                    ppdp.accepted_amount = 0

            # Pass the total contracted volume to the strategic reserve operator
            self.operator.setReserveVolume(contracted_strategic_reserve_capacity)

            # Pay the contracted plants in the strategic reserve
            self.createCashFlowforSR(self.operator, market)

            # Write operator to DB
            self.reps.create_or_update_StrategicReserveOperator(SRO_name, self.operator.getZone(),
                                                                self.operator.getReservePriceSR(),
                                                                self.operator.getReserveVolumePercentSR(),
                                                                self.operator.getReserveVolume(),
                                                                self.operator.getCash(),
                                                                self.operator.getPlants())

    # Cashflow function for the operation of the strategic reserve
    def createCashFlowforSR(self, operator, market):
        accepted_ppdp = self.reps.get_accepted_SR_bids()
        for accepted in accepted_ppdp:
            plant = self.reps.power_plants[accepted.plant]
            # Fixed operating costs of plants
            fixed_operating_costs = plant.actualFixedOperatingCost
            # fixed_operating_costs = accepted.plant.get_actual_fixed_operating_cost()
            # Retrieve dispatch data of plants for variable costs and revenues
            dispatch = self.reps.get_power_plant_electricity_dispatch(plant.id)
            # Costs to be paid by Strategic Reserve Operator and to be received
            if dispatch is None:
                SR_payment_to_plant = fixed_operating_costs
                SR_payment_to_operator = 0
            else:
                SR_payment_to_plant = fixed_operating_costs + dispatch.variable_costs
                SR_payment_to_operator = dispatch.revenues

            # from_agent, to, amount, type, time, plant
            # Payment from operator to energy producer, self.reps.energy_producers[accepted.bidder]
            # for now only the power plant cash is being saved
            self.reps.createCashFlow(operator, plant,
                                     SR_payment_to_plant, globalNames.CF_STRRESPAYMENT, self.reps.current_tick,
                                     self.reps.power_plants[accepted.plant])
            self.reps.dbrw.stage_cash_plant(plant)
            # Payment from market to operator
            self.reps.createCashFlow(market, operator,
                                     SR_payment_to_operator, globalNames.CF_STRRESPAYMENT, self.reps.current_tick,
                                     self.reps.power_plants[accepted.plant])

            self.reps.dbrw.stage_CM_revenues(accepted.plant, SR_payment_to_plant, self.reps.current_tick)
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
        reps.dbrw.stage_init_bids_structure()
        reps.dbrw.stage_init_sr_results_structure()
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

            # Place bids on market (full capacity at cost price per MW)
            # Remove this if statement when everything works
            if market != None:
                # self.reps.create_or_update_power_plant_StrategicReserve_plan(powerplant, energy_producer,
                #                                                              market, power_plant_capacity,
                #                                                              normalised_costs, self.reps.current_tick)
                self.reps.create_or_update_power_plant_CapacityMarket_plan(powerplant, self.agent,
                                                                           market, power_plant_capacity,
                                                                           normalised_costs, self.reps.current_tick)

class StrategicReserveAssignment(MarketModule):
    """
    The class clearing the Strategic Reserve Market and assigning them to the Strategic Reserve Operator
    """

    def __init__(self, reps: Repository ):
        super().__init__('EM-Lab Strategic Reserve: Assign Plants', reps)
        reps.dbrw.stage_init_capacitymechanisms_structure()
        self.operator = None


    def act(self):
        # Assign plants to Strategic Reserve per region
        market = self.reps.get_capacity_market_in_country(self.reps.country)
        
        # Set the strategic reserve zone to the same as the market
        self.operator = self.reps.get_strategic_reserve_operator(self.reps.country)
        # Retrieve peak load volume of market
        peak_load = max(self.reps.get_hourly_demand_by_country(market.country)[1])
        expectedDemandFactor = self.reps.dbrw.get_calculated_simulated_fuel_prices_by_year("electricity",
                                                                                           globalNames.simulated_prices,
                                                                                           self.reps.current_year)
        peakExpectedDemand = peak_load * (expectedDemandFactor)

        # Calculate needed strategic reserve capacity
        strategic_reserve_capacity = peakExpectedDemand * self.operator.getReserveVolumePercentSR()

        # Retrieve SR price
        SR_price = self.operator.getReservePriceSR()

        # Sort the bids in descending order
        sorted_ppdp = self.reps.get_descending_sorted_power_plant_dispatch_plans_by_SRmarket(market, self.reps.current_tick)

        # Contract plants to Strategic Reserve Operator
        list_of_plants = []
        contracted_strategic_reserve_capacity = 0

        for ppdp in sorted_ppdp:
            # If plant capacity fits in strategic reserve than contract it
            if (contracted_strategic_reserve_capacity + ppdp.amount) <= strategic_reserve_capacity:
                contracted_strategic_reserve_capacity += ppdp.amount
                ppdp.status = globalNames.power_plant_status_strategic_reserve
                ppdp.accepted_amount = ppdp.amount
                # Add plant to the list of the StrategicReserveOperator
                list_of_plants.append(ppdp.plant)
                # Change plant status to 'InStrategicReserve', owner to 'StrategicReserveOperator' and price to SR price
                self.reps.update_power_plant_status(ppdp.plant, SR_price)
            else:
                # When strategic reserve is full nothing actually changes for the power plant
                ppdp.accepted_amount = 0

        # setting the plants to be saved in the strategic reserve
        self.operator.setPlants(list_of_plants)
        # Pass the total contracted volume to the strategic reserve operator
        self.operator.setReserveVolume(contracted_strategic_reserve_capacity)

        #saving the revenues to the power plants
        # Pay the contracted plants in the strategic reserve
        self.createCashFlowforSR( market)

        #saving the cash to the operator and the volume and list of power plants to SRResults
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
            #
            # # saving the bids status # todo: the bids could be erased later on
            # self.reps.dbrw.stage_bids_status(accepted)
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


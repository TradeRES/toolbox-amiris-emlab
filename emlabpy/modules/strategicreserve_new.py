"""
The file simulates a simple strategic reserve operations.

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
        self.operator = self.reps.get_strategic_reserve_operator(self.reps.country)


    def act(self):
        # Retrieve every power plant in the active energy producer for the defined country
        for powerplant in self.reps.get_plants_to_be_decommissioned_and_inSR(self.operator.years_accepted_inSR_before_decommissioned):
            # Retrieve the active capacity market and power plant capacity
            market = self.reps.get_capacity_market_for_plant(powerplant)
            power_plant_capacity = powerplant.get_actual_nominal_capacity()

            variable_costs = powerplant.technology.get_variable_operating_by_time_series(
                powerplant.age + self.operator.forward_years_SR)

            Bid = variable_costs + powerplant.technology.fuel.futurePrice[
                self.operator.forward_years_SR + self.reps.current_year] / powerplant.technology.get_efficiency_by_time_series(
                powerplant.age + self.operator.forward_years_SR)
            # Place bids on market (full capacity at cost price per MW)
            self.reps.create_or_update_power_plant_CapacityMarket_plan(powerplant, self.agent,
                                                                       market, power_plant_capacity,
                                                                       Bid, self.reps.current_tick)

class StrategicReserveAssignment(MarketModule):
    """
    The class clearing the Strategic Reserve Market and assigning them to the Strategic Reserve Operator
    """

    def __init__(self, reps: Repository ):
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
        spot_market = self.reps.get_spot_market_in_country(self.reps.country)
        peak_load = self.reps.get_peak_future_demand_by_year(self.reps.current_year)
      #  peak_load = spot_market.get_peak_load_per_year(self.reps.current_year)
        expectedDemandFactor = self.reps.dbrw.get_calculated_simulated_fuel_prices_by_year("electricity",
                                                                                           globalNames.simulated_prices,
                                                                                           self.reps.current_year)
        # The expected peak load volume is defined as the base peak load with a demand factor for the defined year
        peakExpectedDemand = peak_load * (expectedDemandFactor)

        # Calculate needed strategic reserve capacity
        strategic_reserve_capacity = peakExpectedDemand * self.operator.getReserveVolumePercentSR()

        # Retrieve the bids on the capacity market, sorted in descending order on price
        sorted_ppdp = self.reps.get_descending_sorted_power_plant_dispatch_plans_by_SRmarket(market, self.reps.current_tick)

        # Contract plants to Strategic Reserve Operator
        list_of_plants = []
        contracted_strategic_reserve_capacity = 0

        for ppdp in sorted_ppdp:
            power_plant = self.reps.get_power_plant_by_name(ppdp.plant)
            ppdp.status = globalNames.power_plant_status_strategic_reserve
            ppdp.accepted_amount = ppdp.amount
            contracted_strategic_reserve_capacity += ppdp.amount
            list_of_plants.append(ppdp.plant)
            if power_plant.status == globalNames.power_plant_status_strategic_reserve: # last year in Strategic reserve
                self.reps.increase_year_in_sr(power_plant)
                print("years in reserve " + str(power_plant.years_in_SR))
            else:
                self.reps.update_power_plant_status_ger_first_year(power_plant)
                print("new in Reserve"  + power_plant.name)

            if (contracted_strategic_reserve_capacity) > strategic_reserve_capacity:
                self.reserveFull = True
                break

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
            print(plant.name)
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
            if plant.loan.getNumberOfPaymentsDone() < plant.loan.getTotalNumberOfPayments(): # that year the plant should still pay the loans
                print("plus loans " + str(plant.loan.getAmountPerPayment()))
                SR_payment_to_plant = SR_payment_to_plant +  plant.loan.getAmountPerPayment()
            print("SR_payment_to_plant " + str(SR_payment_to_plant))
            # Payment (fixed costs and variable costs ) from operator to plant
            self.reps.createCashFlow(self.operator, plant,
                                     SR_payment_to_plant, globalNames.CF_STRRESPAYMENT, self.reps.current_tick,
                                     self.reps.power_plants[accepted.plant])
            # saving the revenues to the power plants
            self.reps.dbrw.stage_CM_revenues(accepted.plant, SR_payment_to_plant, self.reps.current_tick)
            plant.crm_payments_in_year += SR_payment_to_plant # adding to variable so that it is available in
            # Payment (market revenues) from market to operator
            self.reps.createCashFlow(market, self.operator,
                                     SR_payment_to_operator, globalNames.CF_STRRESPAYMENT, self.reps.current_tick,
                                     self.reps.power_plants[accepted.plant])

            self.operator.revenues_per_year += SR_payment_to_operator

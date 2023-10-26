"""
The file simulates the German strategic reserve operations.
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
        for powerplant in self.reps.get_plants_to_be_decommissioned_and_inSR(self.operator .years_accepted_inSR_before_decommissioned ):
            # Retrieve the active capacity market and power plant capacity
            market = self.reps.get_capacity_market_for_plant(powerplant)
            power_plant_capacity = powerplant.get_actual_nominal_capacity()
            Bid  = self.reps.calculate_marginal_costs( powerplant, self.operator.forward_years_SR)
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

        # order_status =  {         # Retrieve the bids on the capacity market, sorted in descending order on price and first the ones in SR
        #     globalNames.power_plant_status_strategic_reserve: 0,
        # }
        # sorted_ppdp = self.reps.get_descending_bids_and_first_in_SR(market,self.reps.current_tick, order_status)
        # Retrieve the bids on the capacity market, sorted in descending order on price

        sorted_ppdp = self.reps.get_descending_sorted_power_plant_dispatch_plans_by_SRmarket(market, self.reps.current_tick)

        list_of_plants = []
        # Contract plants to Strategic Reserve Operator
        contracted_strategic_reserve_capacity = 0

        for count, ppdp in enumerate(sorted_ppdp):
            if self.reserveFull == True:
                break
            else:
            # If plants are already in strategic reserve they have to be until max years in reserve
                power_plant = self.reps.get_power_plant_by_name(ppdp.plant)


                if power_plant.status == globalNames.power_plant_status_strategic_reserve: # last year in Strategic reserve
                    if self.reserveFull == False:
                        if power_plant.years_in_SR >= self.operator.max_years_in_reserve:  # Has already been in reserve for 4 years
                            power_plant.status = globalNames.power_plant_status_decommissioned_from_SR
                            self.reps.dbrw.stage_power_plant_status(power_plant)
                            print("to be decommissioned because of >" + str(self.operator.max_years_in_reserve) + " years in SR "  +  power_plant.name)
                        elif count < len(sorted_ppdp) -1:
                            second = sorted_ppdp[count+1]
                            if (second.price - ppdp.price <= 5):
                                if (power_plant.technology.expected_lifetime + power_plant.technology.maximumLifeExtension - power_plant.age)<0:
                                    power_plant.status = globalNames.power_plant_status_decommissioned_from_SR
                                    self.reps.dbrw.stage_power_plant_status(power_plant)
                                    print("plant is very old and next plant has similar bid" + str(self.operator.max_years_in_reserve) + " years in SR "  +  power_plant.name)
                            else:
                                print("keep with first bid")

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
                    ppdp.status = globalNames.power_plant_status_strategic_reserve
                    ppdp.accepted_amount = ppdp.amount
                    # Add plant to the list of the StrategicReserveOperator so that next year they are also accepted
                    list_of_plants.append(ppdp.plant)
                    # Change plant status and increase age
                    power_plant = self.reps.get_power_plant_by_name(ppdp.plant)
                    print("new in Reserve "  + power_plant.name)
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

        self.reps.create_or_update_StrategicReserveOperator(self.operator.name,
                                                            self.operator.getZone(),
                                                            self.operator.getReserveVolume(),
                                                            self.operator.getPlants())

        for ppdp in sorted_ppdp:
            power_plant = self.reps.get_power_plant_by_name(ppdp.plant)
            if ppdp.plant not in list_of_plants and power_plant.status == globalNames.power_plant_status_strategic_reserve:
                print("power plant in SR, didnt enter the reserve this time")
                power_plant.status = globalNames.power_plant_status_decommissioned_from_SR
                self.reps.dbrw.stage_power_plant_status(power_plant)

    # Cashflow function for the operation of the strategic reserve
    def createCashFlowforSR(self, plant, operator):
        """ Pay the contracted plants in the strategic reserve and save the revenues to the power plants
        """
        print("-----------------SR plant" + str(plant.name))
        # Fixed operating costs of plants
        fixed_operating_costs = plant.actualFixedOperatingCost
        # Retrieve dispatch data of plants for variable costs and revenues
        dispatch = self.reps.get_power_plant_electricity_dispatch(plant.id)
        # Costs to be paid by Strategic Reserve Operator and to be received
        if dispatch is None:
            SR_payment_to_plant = fixed_operating_costs
            SR_payment_to_operator = 0
            real_commodity_costs = 0
        else:
            marginal_costs =  self.reps.calculate_marginal_costs( plant, 0)
            real_commodity_costs =  dispatch.accepted_amount * marginal_costs
            SR_payment_to_plant = fixed_operating_costs + real_commodity_costs
            SR_payment_to_operator = dispatch.revenues - real_commodity_costs

        if (plant.loan_payments_in_year + plant.downpayment_in_year) > 0: # that year the plant should still pay the loans
            print("plus loans" + str(plant.loan.getAmountPerPayment()))
            SR_payment_to_plant = SR_payment_to_plant +  plant.loan.getAmountPerPayment()

        print("SR_payment_to_plant" + str(SR_payment_to_plant))

        # saving the revenues to the power plants
        self.reps.dbrw.stage_CM_revenues(plant.name, SR_payment_to_plant, self.reps.current_tick)
        plant.crm_payments_in_year += SR_payment_to_plant


        #Payment (fixed costs and variable costs ) from operator to plant
        self.reps.createCashFlow(operator, plant,
                                 SR_payment_to_plant, globalNames.CF_STRRESPAYMENT, self.reps.current_tick, plant)
        #Payment (market revenues) from wholesale market to operator
        market = self.reps.get_spot_market_in_country(self.reps.country)

        operator.revenues_per_year += SR_payment_to_operator
        self.reps.createCashFlow(market, operator,
                                 SR_payment_to_operator, globalNames.CF_STRRESPAYMENT, self.reps.current_tick, plant)
        return real_commodity_costs
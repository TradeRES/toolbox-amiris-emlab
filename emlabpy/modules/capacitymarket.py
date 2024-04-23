"""
The file responsible for all capacity market operations.

Jim Hommes - 25-3-2021
Sanchez 31-05-2022
"""
import json
import logging

from util import globalNames
import numpy_financial as npf
from modules.marketmodule import MarketModule
from util.repository import Repository
from domain.markets import SlopingDemandCurve


class CapacityMarketSubmitBids(MarketModule):
    """
    The class that submits all bids to the Capacity Market
    """

    def __init__(self, reps: Repository, long_term: bool):
        super().__init__('EM-Lab Capacity Market: Submit Bids', reps)
        reps.dbrw.stage_init_bids_structure()
        self.agent = reps.energy_producers[reps.agent]
        reps.dbrw.stage_init_market_clearing_point_structure()
        self.long_term = long_term

    def act(self):
        # in the future : do for every EnergyProducer
        # Retrieve every power plant in the active energy producer for the defined country
        market = self.reps.get_capacity_market_in_country(self.reps.country, self.long_term)
        # self.future_installed_plants_ids = self.reps.get_ids_of_future_installed_plants(market.forward_years_CM + self.reps.current_tick )
        print(
            "technologyname;price_to_bid;capacity;profits;fixed_on_m_cost;pending_loan")
        power_plants = []
        if self.long_term == False:
            # power_plants = self.reps.get_operational_and_to_be_decommissioned(
            #     market.forward_years_CM)
            for pp_id in self.reps.get_ids_of_future_installed_plants(market.forward_years_CM + self.reps.current_tick): # the installed power plants are filtered in the prepare futur market clearing file
                power_plants.append( self.reps.get_power_plant_by_id(pp_id))
        else:
            power_plants = self.reps.get_plants_that_can_be_operational_not_in_ltcm(
                market.forward_years_CM)  # retrieve plants that will be operational in 1 -4 years
        total_offered_capacity = 0

        for powerplant in power_plants:
            fixed_on_m_cost = powerplant.actualFixedOperatingCost
            capacity = powerplant.get_actual_nominal_capacity()
            profits = self.reps.get_expected_profits_by_tick(powerplant.name,
                                                             self.reps.current_tick + market.forward_years_CM)
            self.reps.dbrw.update_fixed_costs(powerplant, market.forward_years_CM)
            # Bid price is zero, unless net revenues are negative
            price_to_bid = 0
            loan = powerplant.getLoan()
            """
            for the capacity market runs, there are no downpayments
            """
            pending_loan = 0
            if powerplant.age <= - market.forward_years_CM:
                if loan is not None:
                    if loan.getNumberOfPaymentsDone() < loan.getTotalNumberOfPayments():
                        pending_loan = loan.getAmountPerPayment()
            else:
                pending_loan = 0
            # if power plant is not dispatched, the net revenues are minus the fixed operating costs
            if profits is None:
                net_revenues = - fixed_on_m_cost - pending_loan
                profits = 0
            else: # if power plant is dispatched, the net revenues are the revenues minus the total costs
                net_revenues = profits - fixed_on_m_cost - pending_loan

        # if net revenues are negative, the bid price is the net revenues per mw of capacity
            if powerplant.get_actual_nominal_capacity() > 0 and net_revenues <= 0:
                price_to_bid = -1 * net_revenues / \
                               (capacity * powerplant.technology.deratingFactor)
            else:
                pass  # if positive revenues price_to_bid remains 0
            """
            if the power plant is in the long term and will continue to be in the long term, the bid price is limited
            """
            long_term_contract = False
            if self.reps.capacity_remuneration_mechanism == "forward_capacity_market":
                if powerplant.status == globalNames.power_plant_status_inPipeline:
                    long_term_contract = True
                else:
                    price_to_bid = min(market.PriceCap / 2, price_to_bid)
            print(powerplant.technology.name +
                  powerplant.name + ";" + str(price_to_bid) + ";" + str(
                capacity * powerplant.technology.deratingFactor) + ";" + str(profits) + ";" + str(
                fixed_on_m_cost) + ";" + str(
                pending_loan))

            # all power plants place a bid pair of price and capacity on the market
            capacity_to_bid = capacity * powerplant.technology.deratingFactor
            self.reps.create_or_update_power_plant_CapacityMarket_plan(powerplant, self.agent, market,
                                                                       long_term_contract, capacity_to_bid, \
                                                                       price_to_bid, self.reps.current_tick)
            total_offered_capacity += capacity_to_bid
            # todo: delete this later
        # expected_capacity = self.reps.get_cleared_volume_for_market_and_time("capacity_market_future", self.reps.current_tick + market.forward_years_CM)
        # if expected_capacity != int(total_offered_capacity):
        #     raise ValueError("Total volume of bids is not equal to total offered capacity")
        # else:
        #     pass


class CapacityMarketClearing(MarketModule):
    """
    The class that clears the Capacity Market based on the Sloping Demand curve
    """

    def __init__(self, reps: Repository, long_term):
        super().__init__('EM-Lab Capacity Market: Clear Market', reps)
        reps.dbrw.stage_init_capacitymechanisms_structure()
        self.long_term = long_term

    def act(self):
        print("capacity market clearing")
        # Retireve variables: active capacity market, peak load volume and expected demand factor in defined year
        capacity_market = self.reps.get_capacity_market_in_country(self.reps.country, self.long_term)
        # Retrieve the bids on the capacity market, sorted in ascending order on price
        sorted_supply = self.reps.get_sorted_bids_by_market_and_time(capacity_market, self.reps.current_tick)

        capacity_market_year = self.reps.current_year + capacity_market.forward_years_CM
        clearing_price, total_supply_volume, is_the_market_undersubscribed, upperVolume = self.capacity_market_clearing(
            sorted_supply,
            capacity_market,
            capacity_market_year)

        if clearing_price <0:
            raise ValueError("Clearing price is negative")

        # saving yearly CM revenues to the power plants and update bids
        self.stageCapacityMechanismRevenues(capacity_market, clearing_price)
        # saving market clearing point
        self.reps.create_or_update_market_clearing_point(capacity_market, clearing_price, total_supply_volume,
                                                         self.reps.current_tick + capacity_market.forward_years_CM)  # saved according to effective year

    def capacity_market_clearing(self, sorted_supply, capacity_market, capacity_market_year):
        def check_if_market_under_subscribed(total_supply_volume, targetVolume):
            if total_supply_volume > targetVolume:
                return False
            else:
                return True

        # spot_market = self.reps.get_spot_market_in_country(self.reps.country)
        # expectedDemandFactor = self.reps.substances["electricity"].get_price_for_tick(self.reps, capacity_market_year,
        #                                                                               True)
        # # changed to fix number because peak load can change per weather year.
        # # changing peak load according to higher than median year.
        # peak_load = self.reps.get_peak_future_demand_by_year(capacity_market_year)
        # # The expected peak load volume is defined as the base peak load with a demand factor for the defined year
        # peakExpectedDemand = peak_load * (expectedDemandFactor)
        effective_capacity_long_term_CM = self.reps.get_capacity_under_long_term_contract(
            capacity_market.forward_years_CM)
        targetVolume = capacity_market.TargetCapacity
        targetVolume -= effective_capacity_long_term_CM
        # uppertargetVolume = capacity_market.UpperTargetCapacity
        # uppertargetVolume -= effective_capacity_long_term_CM
        # Retrieve the sloping demand curve for the expected peak load volume
        sdc = capacity_market.get_sloping_demand_curve(targetVolume)

        clearing_price = 0
        total_supply_volume = 0
        isMarketUndersuscribed = True
        for supply in sorted_supply:
            if isMarketUndersuscribed == True:
                # As long as the market is not cleared
                if supply.price <= sdc.get_price_at_volume(total_supply_volume + supply.amount):
                    total_supply_volume += supply.amount
                    clearing_price = sdc.get_price_at_volume(total_supply_volume + supply.amount)
                    supply.status = globalNames.power_plant_dispatch_plan_status_accepted
                    supply.accepted_amount = supply.amount

                elif supply.price < sdc.get_price_at_volume(total_supply_volume) and supply.price < sdc.price_cap:
                    """
                    the price of the next bid is higher than the price cap.
                    accepting the power plant, but giving lower price, otherwise the price dont decrease!!!
                    """
                    total_supply_volume = total_supply_volume + supply.amount

                    if total_supply_volume >= sdc.lm_volume:
                        # cost_for_extra_reliabilty =  supply.amount * supply.price # todo finish according to elia rules.
                        # willingness_to_pay_for_extra_reliability = (
                        #     sdc.get_price_at_volume(total_supply_volume))
                        # y1 =  sdc.get_price_at_volume(total_supply_volume )
                        # y2 =  sdc.get_price_at_volume(total_supply_volume -  supply.amount)
                        clearing_price = supply.price
                    else:
                        clearing_price = sdc.get_price_at_volume(total_supply_volume)

                    supply.status = globalNames.power_plant_dispatch_plan_status_accepted
                    supply.accepted_amount = supply.amount
                    print(supply.plant, " last ACCEPTED ", total_supply_volume, "", clearing_price)
                    break
                else:
                    supply.status = globalNames.power_plant_dispatch_plan_status_failed
                    break
            else:
                supply.status = globalNames.power_plant_dispatch_plan_status_failed
                break
            isMarketUndersuscribed = check_if_market_under_subscribed(total_supply_volume, targetVolume)
        isMarketUndersuscribed = check_if_market_under_subscribed(total_supply_volume, targetVolume)
        print("clearing price ", clearing_price)
        print("total_supply", total_supply_volume)
        print("isMarketUndersuscribed ", isMarketUndersuscribed)
        return clearing_price, total_supply_volume, isMarketUndersuscribed, sdc.um_volume

    def stageCapacityMechanismRevenues(self, market, clearing_price):
        print("staging capacity market")
        accepted_ppdp = self.reps.get_accepted_CM_bids(self.reps.current_tick)
        self.reps.dbrw.stage_init_years_in_long_term_capacity_market()
        for accepted in accepted_ppdp:
            amount = accepted.accepted_amount * clearing_price
            ticks_awarded = list(range(self.reps.current_tick + market.forward_years_CM, \
                                       self.reps.current_tick + market.forward_years_CM + int(
                                           market.years_long_term_market)))
            if accepted.long_term_contract:
                self.reps.dbrw.stage_CM_revenues(accepted.plant, amount, ticks_awarded)
                self.reps.dbrw.stage_power_plant_years_in_long_term_capacity_market(accepted.plant,
                                                                                     self.reps.current_year + market.years_long_term_market)
            else:
                self.reps.dbrw.stage_CM_revenues(accepted.plant, amount, [self.reps.current_tick + market.forward_years_CM])


def calculate_cone(reps, capacity_market, candidatepowerplants):
    """CONE is calculated  for every technology and the minimum is chosen as the price cap"""
    cones = {}
    netcones = {}
    for candidatepowerplant in candidatepowerplants:
        if candidatepowerplant.technology.name not in capacity_market.allowed_technologies_capacity_market:
            continue
        else:
            technology = candidatepowerplant.technology
            totalInvestment = technology.get_investment_costs_perMW_by_year(
                reps.current_year + capacity_market.forward_years_CM)

            depreciationTime = technology.depreciation_time
            buildingTime = technology.expected_leadtime
            fixed_costs = technology.get_fixed_costs_by_commissioning_year(
                reps.current_year + capacity_market.forward_years_CM)
            equalTotalDownPaymentInstallment = (totalInvestment) / buildingTime
            # agent = reps.energy_producers[reps.agent]
            # equalTotalDownPaymentInstallment = (totalInvestment * (1 - agent.debtRatioOfInvestments)) / buildingTime
            # debt = totalInvestment * agent.debtRatioOfInvestments
            # annuity = - npf.pmt(technology.interestRate, depreciationTime, debt, fv=1, when='end')
            investmentCashFlow = [0 for i in range(depreciationTime + buildingTime)]
            investmentCashFlowNETCONE = [0 for i in range(depreciationTime + buildingTime)]
            wacc = technology.interestRate
            for i in range(0, buildingTime + depreciationTime):
                if i < buildingTime:
                    investmentCashFlow[i] = equalTotalDownPaymentInstallment
                    investmentCashFlowNETCONE[i] =  equalTotalDownPaymentInstallment
                else:
                    investmentCashFlow[i] = fixed_costs
                    investmentCashFlowNETCONE[
                        i] = fixed_costs - candidatepowerplant.get_Profit() / candidatepowerplant.capacity  # per MW

            discountedprojectvalue = npf.npv(wacc, investmentCashFlow)
            discountedprojectvalueNETCONE = npf.npv(wacc, investmentCashFlowNETCONE) # it is equivalent as summing up the discounted cash flows

            factor = (wacc * (1 + wacc) ** (buildingTime + depreciationTime)) / (((1 + wacc) ** depreciationTime) - 1)

            CONE = discountedprojectvalue * factor/ technology.deratingFactor
            NETCONE = discountedprojectvalueNETCONE * factor/ technology.deratingFactor
            cones[technology.name] = CONE
            netcones[technology.name] = NETCONE
    if not cones:
        print("cones is empty")
    else:
        reps.dbrw.stage_yearly_CONE(netcones, cones, reps.current_tick)
        technology_highest_availability = reps.get_allowed_technology_with_highest_availability(
            capacity_market.allowed_technologies_capacity_market)
        netCONE = netcones[technology_highest_availability]
        cone = cones[technology_highest_availability]
       # according to the belgian authorities the price cap should range between 80000 and 100000
        price_cap = max(int(netCONE * capacity_market.PriceCapTimesCONE),cone)
        print("price_cap")
        print(price_cap)

        if reps.current_tick == 0:
            if price_cap < 0:
                raise ValueError("Price cap is negative")
            else:
                capacity_market.PriceCap = price_cap
                reps.dbrw.stage_price_cap(capacity_market.name, price_cap)

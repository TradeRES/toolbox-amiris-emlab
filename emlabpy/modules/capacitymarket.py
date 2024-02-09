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

def calculate_cone(reps, market):
    cones = {}
    for candidatepowerplant in reps.candidatePowerPlants.values():
        technology = candidatepowerplant.technology
        totalInvestment = technology.get_investment_costs_perMW_by_year(
            reps.current_year + market.forward_years_CM)
        depreciationTime = technology.depreciation_time
        buildingTime = technology.expected_leadtime
        fixed_costs = technology.get_fixed_costs_by_commissioning_year(
            reps.current_year + market.forward_years_CM)
        equalTotalDownPaymentInstallment = (totalInvestment ) / buildingTime
        investmentCashFlow = [0 for i in range(depreciationTime + buildingTime)]
        for i in range(0, buildingTime + depreciationTime):
            if i < buildingTime:
                investmentCashFlow[i] =  equalTotalDownPaymentInstallment
            else:
                investmentCashFlow[i] =  fixed_costs
        wacc = technology.interestRate
        discountedprojectvalue = npf.npv(wacc, investmentCashFlow)
        factor = (wacc * (1 + wacc) ** (buildingTime + depreciationTime)) / (((1 + wacc) ** depreciationTime) - 1)
        CONE = discountedprojectvalue * factor
        cones[technology.name ] = CONE
    minCONE = min(cones.values())
    reps.dbrw.stage_CONE( market.name, int(minCONE))

class CapacityMarketSubmitBids(MarketModule):
    """
    The class that submits all bids to the Capacity Market
    """

    def __init__(self, reps: Repository):
        super().__init__('EM-Lab Capacity Market: Submit Bids', reps)
        reps.dbrw.stage_init_bids_structure()
        self.agent = reps.energy_producers[reps.agent]
        reps.dbrw.stage_init_market_clearing_point_structure()

    def act(self):
        # in the future : do for every EnergyProducer
        # Retrieve every power plant in the active energy producer for the defined country

        market = self.reps.get_capacity_market_in_country(self.reps.country)
        print(
            "technology" + "name" + ";" + "price_to_bid" + ";" + " profits" + ";" + "fixed_on_m_cost" + ";" + "pending_loan")
        for powerplant in self.reps.get_operational_almost_operational_and_to_be_decommissioned(
                market.forward_years_CM):
            # Retrieve variables: the active capacity market, fixed operating costs, power plant capacity and dispatch
            # market = self.reps.get_capacity_market_for_plant(powerplant) for now only one market
            fixed_on_m_cost = powerplant.actualFixedOperatingCost
            capacity = powerplant.get_actual_nominal_capacity()  # TODO check if this has to be changed
            profits = self.reps.get_expected_profits_by_tick(powerplant.name,
                                                             self.reps.current_tick + market.forward_years_CM)
            self.reps.dbrw.update_fixed_costs(powerplant, market.forward_years_CM)
            # Bid price is zero, unless net revenues are negative
            price_to_bid = 0
            loan = powerplant.getLoan()
            pending_loan = 0
            if loan is not None:
                if loan.getNumberOfPaymentsDone() < loan.getTotalNumberOfPayments():
                    pending_loan = loan.getAmountPerPayment()

            # if power plant is not dispatched, the net revenues are minus the fixed operating costs
            if profits is None:
                # print("no dispatch found for " + str(powerplant.id)+  " with name "+str(powerplant.name))
                net_revenues = - fixed_on_m_cost - pending_loan
                profits = 0
            # if power plant is dispatched, the net revenues are the revenues minus the total costs
            else:
                net_revenues = profits - fixed_on_m_cost - pending_loan
            # if net revenues are negative, the bid price is the net revenues per mw of capacity
            if powerplant.get_actual_nominal_capacity() > 0 and net_revenues <= 0:
                price_to_bid = -1 * net_revenues / \
                               (capacity * powerplant.technology.peak_segment_dependent_availability)
            else:
                pass  # if positive revenues price_to_bid remains 0
            print(powerplant.technology.name +
                  powerplant.name + ";" + str(price_to_bid) + ";" + str(profits) + ";" + str(
                fixed_on_m_cost) + ";" + str(
                pending_loan))
            # all power plants place a bid pair of price and capacity on the market
            capacity_to_bid = capacity * powerplant.technology.peak_segment_dependent_availability
            self.reps.create_or_update_power_plant_CapacityMarket_plan(powerplant, self.agent, market, capacity_to_bid, \
                                                                       price_to_bid, self.reps.current_tick)



class CapacityMarketClearing(MarketModule):
    """
    The class that clears the Capacity Market based on the Sloping Demand curve
    """

    def __init__(self, reps: Repository):
        super().__init__('EM-Lab Capacity Market: Clear Market', reps)
        reps.dbrw.stage_init_capacitymechanisms_structure()

    def act(self):
        print("capacity market clearing")
        # Retireve variables: active capacity market, peak load volume and expected demand factor in defined year
        market = self.reps.get_capacity_market_in_country(self.reps.country)
        # Retrieve the bids on the capacity market, sorted in ascending order on price
        sorted_ppdp = self.reps.get_sorted_bids_by_market_and_time(market, self.reps.current_tick)
        capacity_market_year = self.reps.current_year + market.forward_years_CM
        clearing_price, total_supply_volume, is_the_market_undersubscribed = self.capacity_market_clearing(sorted_ppdp,
                                                                                                           market,
                                                                                                           capacity_market_year)

        # saving yearly CM revenues to the power plants and update bids
        self.stageCapacityMechanismRevenues(market, clearing_price)

        # saving market clearing point
        if is_the_market_undersubscribed == True:
            self.reps.create_or_update_market_clearing_point(market, clearing_price, total_supply_volume,
                                                             self.reps.current_tick)
            print("Cleared market", market.name, "at ", str(clearing_price))
        else:
            self.reps.create_or_update_market_clearing_point(market, clearing_price, total_supply_volume,
                                                             self.reps.current_tick)
            print("Market is not cleared", market.name, "at ", str(clearing_price))

    def capacity_market_clearing(self, sorted_ppdp, market, capacity_market_year):
        isMarketUndersuscribed = False  # isTheMarketCleared means ther capacity us slightly oversubscribed
        spot_market = self.reps.get_spot_market_in_country(self.reps.country)
        expectedDemandFactor = self.reps.substances["electricity"].get_price_for_tick(self.reps, capacity_market_year,
                                                                                      True)
        # peak_load = self.reps.get_realized_peak_demand_by_year(self.reps.current_year) - >
        # changed to fix number because peak load can change per weather year.
        # changing peak load according to higher than median year.
        peak_load = self.reps.get_peak_future_demand_by_year(capacity_market_year)
        # The expected peak load volume is defined as the base peak load with a demand factor for the defined year
        peakExpectedDemand = peak_load * (expectedDemandFactor)

        print("peak load " + str(peakExpectedDemand))
        # Retrieve the sloping demand curve for the expected peak load volume
        sdc = market.get_sloping_demand_curve(peakExpectedDemand)

        clearing_price = 0
        total_supply_volume = 0
        # peaksupply = 0   # capacity market should be able to have more capacity than peak
        for ppdp in sorted_ppdp:
            # As long as the market is not cleared
            if ppdp.price <= sdc.get_price_at_volume(total_supply_volume + ppdp.amount):
                total_supply_volume += ppdp.amount
                clearing_price = ppdp.price
                ppdp.status = globalNames.power_plant_dispatch_plan_status_accepted
                ppdp.accepted_amount = ppdp.amount
            #   print(ppdp.plant , " ACCEPTED ", total_supply_volume, "", clearing_price)

            elif ppdp.price < sdc.get_price_at_volume(total_supply_volume):
                """
                should be partly accepted but currently accepting only complete plants, if partly is out, then it is not accepted
                """
                clearing_price = sdc.get_price_at_volume(total_supply_volume)
                total_supply_volume = total_supply_volume# total supply sdc.get_volume_at_price(clearing_price)
                ppdp.status = globalNames.power_plant_dispatch_plan_status_partly_accepted
                ppdp.accepted_amount = 0
                # print(ppdp.plant , " partly ACCEPTED ", total_supply_volume, "", clearing_price)
                isMarketUndersuscribed = False
                break
            else:
                ppdp.status = globalNames.power_plant_dispatch_plan_status_failed
                if total_supply_volume > sdc.lm_volume:
                    isMarketUndersuscribed = False
                else:
                    isMarketUndersuscribed = True
                break

        print("clearing price ", clearing_price)
        print("total_supply", total_supply_volume)
        print("market mninimum volume? ", isMarketUndersuscribed)

        return clearing_price, total_supply_volume, isMarketUndersuscribed

    def stageCapacityMechanismRevenues(self, market, clearing_price):
        print("staging capacity market")
        accepted_ppdp = self.reps.get_accepted_CM_bids(self.reps.current_tick)
        for accepted in accepted_ppdp:
            amount = accepted.accepted_amount * clearing_price
            # saving yearly CM revenues to the power plants # todo: the bids could be erased later on if all the values can be read from clearing point
            self.reps.dbrw.stage_CM_revenues(accepted.plant, amount, self.reps.current_tick + market.forward_years_CM)
            # saving capacity market accepted bids amount and status
            self.reps.dbrw.stage_bids_status(accepted)

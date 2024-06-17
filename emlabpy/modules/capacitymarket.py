"""
The file responsible for all capacity market operations.

Jim Hommes - 25-3-2021
Sanchez 31-05-2022
"""
import json
import pandas as pd
import os
from os.path import dirname, realpath
import matplotlib.pyplot as plt
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

        # the installed power plants are filtered in the prepare futur market clearing file
        for pp_id in self.reps.get_ids_of_future_installed_plants(market.forward_years_CM + self.reps.current_tick):
            powerplant = self.reps.get_power_plant_by_id(pp_id)
            if self.long_term == True and self.reps.power_plant_still_in_reserve(powerplant, market.forward_years_CM):
                pass
            elif powerplant.technology.deratingFactor ==0:
                pass
            else:
                power_plants.append(powerplant)

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

            print(powerplant.technology.name +
                  powerplant.name + ";" + str(price_to_bid) + ";" + str(
                capacity * powerplant.technology.deratingFactor) + ";" + str(profits) + ";" + str(
                fixed_on_m_cost) + ";" + str(
                pending_loan))

            #all power plants place a bid pair of price and capacity on the market tech
            if self.reps.dynamic_derating_factor == True and self.reps.capacity_remuneration_mechanism != "capacity_subscription" and \
                powerplant.technology.name in globalNames.vres_and_batteries:
                capacity_to_bid = capacity * self.reps.get_current_derating_factor(powerplant.technology.name)
            else:
                capacity_to_bid = capacity * powerplant.technology.deratingFactor
            self.reps.create_or_update_power_plant_CapacityMarket_plan(powerplant, self.agent, market,
                                                                       long_term_contract, capacity_to_bid, \
                                                                       price_to_bid, self.reps.current_tick)
            capacity_to_bid = capacity * powerplant.technology.deratingFactor
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
        if self.reps.current_tick >=4:
            self.calculate_derating_factor()
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
        def check_if_market_under_subscribed(total_supply_volume, volume):
            if total_supply_volume > volume:
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
                # As long as the supply are not above the upper margin, the supply is accepted
                if supply.price <= sdc.get_price_at_volume(total_supply_volume + supply.amount):
                    total_supply_volume += supply.amount
                    clearing_price = sdc.get_price_at_volume(total_supply_volume)
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
                    print("price higher than price cap")
                    supply.status = globalNames.power_plant_dispatch_plan_status_failed
                    break
            else:
                print("market oversubscribed")
                supply.status = globalNames.power_plant_dispatch_plan_status_failed
                break
            isMarketUndersuscribed = check_if_market_under_subscribed(total_supply_volume, sdc.um_volume)

        # final check if the market is undersubscribed
        isMarketUndersuscribed = check_if_market_under_subscribed(total_supply_volume, sdc.um_volume)

        print("clearing price ", clearing_price)
        print("total_supply", total_supply_volume)
        print("isMarketUndersuscribed ", isMarketUndersuscribed)

        if self.reps.runningModule =="run_CRM":
            total = 0
            for i, supply in enumerate(sorted_supply):
                total += supply.amount
                supply.cummulative_quantity = total
            x = [sdc.um_volume , targetVolume, sdc.lm_volume]
            y = [0, sdc.net_cone, sdc.price_cap]

            supply_prices = []
            supply_quantities = []
            cummulative_quantity = 0

            for bid in sorted_supply:
                supply_prices.append(bid.price)
                cummulative_quantity += bid.amount
                supply_quantities.append(cummulative_quantity)
            fig1 = plt.figure()
            plt.step(supply_quantities, supply_prices, 'o-', label='supply', color='b')
            plt.plot(x, y, marker='o')
            plt.grid(visible=None, which='minor', axis='both', linestyle='--')
            plt.axhline(y=clearing_price, color='g', linestyle='--', label='P ' + str(clearing_price))
            plt.axvline(x=total_supply_volume, color='g', linestyle='--', label='Q ' + str(total_supply_volume))
            plt.title(self.reps.runningModule + " " + str(self.reps.investmentIteration))
            plt.xlabel('Quantity')
            plt.ylabel('Price')
            path = os.path.join(dirname(realpath(os.getcwd())), 'temporal_results')
            plt.savefig(os.path.join( path , str(self.reps.current_year)+ '.png') ,bbox_inches='tight', dpi=300)

        return clearing_price, total_supply_volume, isMarketUndersuscribed, sdc.um_volume

    def stageCapacityMechanismRevenues(self, market, clearing_price):
        print("staging capacity market")
        accepted_ppdp = self.reps.get_accepted_CM_bids(self.reps.current_tick)
        self.reps.dbrw.stage_init_years_in_long_term_capacity_market()
        accepted_plant_names = []
        for accepted in accepted_ppdp:
            accepted_plant_names.append(accepted.name)
            amount = accepted.accepted_amount * clearing_price
            ticks_awarded = list(range(self.reps.current_tick + market.forward_years_CM, \
                                       self.reps.current_tick + market.forward_years_CM + int(
                                           market.years_long_term_market)))

            if accepted.long_term_contract:
                self.reps.dbrw.stage_CM_revenues(accepted.plant, amount, ticks_awarded)
                self.reps.dbrw.stage_power_plant_years_in_long_term_capacity_market(accepted.plant,
                                         self.reps.current_year + market.forward_years_CM + market.years_long_term_market)
            else:
                self.reps.dbrw.stage_CM_revenues(accepted.plant, amount, [self.reps.current_tick + market.forward_years_CM])

        if self.reps.reliability_option_strike_price == "NOTSET" or self.reps.capacity_remuneration_mechanism == "forward_capacity_market":
            pass
        else:
            self.reps.dbrw.stage_plants_in_CM(accepted_plant_names, self.reps.current_tick + market.forward_years_CM)

    def calculate_derating_factor(self):
        power_plants_list = self.reps.get_power_plants_by_status([globalNames.power_plant_status_operational,
                                                                  globalNames.power_plant_status_to_be_decommissioned,
                                                                  globalNames.power_plant_status_strategic_reserve,
                                                                  ])
        all_techs_capacity = {}
        for pp in power_plants_list:
            tech = pp.technology.name
            capacity = pp.capacity
            if tech in globalNames.vres_and_batteries:
                if tech in all_techs_capacity:
                    all_techs_capacity[tech] += capacity
                else:
                    all_techs_capacity[tech] = capacity

        hourly_generation_res = pd.DataFrame()
        year_excel = os.path.join(os.path.dirname(os.getcwd()), 'amiris_workflow','output',  (str(self.reps.current_year) + ".xlsx"))
        df = pd.read_excel(year_excel, sheet_name=["energy_exchange", "hourly_generation"])
        hourly_load_shedders = pd.DataFrame()
        for unit in df['hourly_generation'].columns.values:
            if unit[0:4] == "unit"  and unit[5:] != "8888888": # excluding electrolyzers shedding
                hourly_load_shedders[unit[5:]] = df['hourly_generation'][unit]
            elif unit =="PV":
                hourly_generation_res["Solar PV large"] = df['hourly_generation'][unit]
            elif unit =="WindOff":
                hourly_generation_res["Wind Offshore"] = df['hourly_generation'][unit]
            elif unit =="WindOn":
                hourly_generation_res["Wind Onshore"] = df['hourly_generation'][unit]
            elif unit =="storages_discharging":
                hourly_generation_res["Lithium ion battery 4"] = df['hourly_generation'][unit]
            # elif unit =="conventionals": # this has all the time 1 derating factor
            #     hourly_generation_res["hydrogen OCGT"] = df['hourly_generation'][unit]
            else:
                pass
        total_hourly_load_shedders = hourly_load_shedders.sum(axis=1)
        yearly_at_scarcity_hours = total_hourly_load_shedders[total_hourly_load_shedders > 0 ].index
        derating_factors = pd.DataFrame()
        # df['Sum'] = df['Lithium ion battery 4'] + df['Lithium ion battery']

        for tech in all_techs_capacity:
            if tech in all_techs_capacity and tech in hourly_generation_res.columns:
                installed_capacity = all_techs_capacity[tech]
                average_generation = hourly_generation_res.loc[yearly_at_scarcity_hours, tech].mean()
                derating_factors[tech] = average_generation / installed_capacity
            else:
                pass

        self.reps.dbrw.stage_derating_factor(derating_factors, self.reps.current_tick)

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
            agent = reps.energy_producers[reps.agent]
            # equalTotalDownPaymentInstallment = (totalInvestment * (1 - agent.debtRatioOfInvestments)) / buildingTime
            #debt = totalInvestment * agent.debtRatioOfInvestments
            # annuity = - npf.pmt(technology.interestRate, depreciationTime, debt, fv=1, when='end')
            investmentCashFlow = [0 for i in range(depreciationTime + buildingTime)]
            investmentCashFlowNETCONE = [0 for i in range(depreciationTime + buildingTime)]

            wacc = (1 - agent.debtRatioOfInvestments) * agent.equityInterestRate + agent.debtRatioOfInvestments * technology.interestRate
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
        price_cap = max(int(netCONE * capacity_market.PriceCapTimesCONE), cone)
        print("price_cap")
        print(price_cap)

        if reps.current_tick == 0:
            if price_cap < 0:
                raise ValueError("Price cap is negative")
            else:
                capacity_market.PriceCap = price_cap
                reps.dbrw.stage_price_cap(capacity_market.name, price_cap)
                reps.dbrw.stage_net_cone(capacity_market.name, netCONE)




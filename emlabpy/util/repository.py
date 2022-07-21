"""
The Repository: home of all objects that play a part in the model.
All objects are read through the SpineDBReader and stored in the Repository.

Jim Hommes - 25-3-2021
Ingrid Sanchez 16-2-2022
"""
from datetime import datetime
from typing import Optional, Dict, List
from domain.actors import *
from domain.cashflow import CashFlow
from domain.powerplantDispatchPlan import *
from domain.technologies import *
from domain.markets import *
from domain.powerplant import *
from domain.substances import *
from domain.CandidatePowerPlant import *
from domain.trends import *
from domain.zones import *
from domain.contract import *
from domain.loans import Loan
from util import globalNames
from domain.bids import Bid
from numpy import mean
from domain.StrategicReserveOperator import StrategicReserveOperator

class Repository:
    """
    The Repository class reads DB data at initialization and loads all objects and relationships
    Also provides all functions that require e.g. sorting
    """

    def __init__(self):
        """
        Initialize all Repository variables
        """
        #self.node = ""
        self.country = ""
        self.dbrw = None
        self.agent = "Producer1"      # TODO if there would be more agents, the future capacity should be analyzed per agent
        self.current_tick = 0
        self.time_step = 0
        self.start_simulation_year = 0
        self.end_simulation_year = 0
        self.short_term_investment_minimal_irr = 0
        self.lookAhead = 0
        self.current_year = 0
        self.simulation_length = 0
        self.start_year_fuel_trends = 0
        self.investmentIteration = 0
        self.dictionaryFuelNames = dict()
        self.dictionaryFuelNumbers = dict()
        self.dictionaryTechNumbers = dict()
        self.dictionaryTechSet = dict()
        self.newTechnology = dict()
        self.energy_producers = dict()
        self.target_investors = dict()
        self.power_plants = dict()
        self.candidatePowerPlants = dict()
        self.substances = dict()
        self.power_plants_fuel_mix = dict()
        self.electricity_spot_markets = dict()
        self.capacity_markets = dict()
        self.co2_markets = dict()
        self.power_plant_dispatch_plans = dict()
        self.bids = dict()
        self.power_generating_technologies = dict()
        self.used_technologies = ["Coal PSC", "CCGT", "OCGT", "Hydropower_reservoir_medium", "Nuclear", "WTG_onshore",
                                  "WTG_offshore", "PV_utility_systems", "Lignite PSC", "Fuel oil PGT",
                                  "Hydropower_ROR", "Lithium_ion_battery", "Biomass_CHP_wood_pellets_DH"]
        self.market_clearing_points = dict()
        self.power_grid_nodes = dict()
        self.trends = dict()
        self.zones = dict()
        self.national_governments = dict()
        self.governments = dict()
        self.investments = dict()
        self.bigBank = BigBank("0")
        self.manufacturer = PowerPlantManufacturer("0")
        self.decommissioned = dict()
        self.market_stability_reserves = dict()
        self.load = dict()
        self.emissions = dict()
        self.exports = dict()

        self.marketForSubstance = {}
        self.electricitySpotMarketForNationalGovernment = {}
        self.electricitySpotMarketForPowerPlant = {}
        self.loansFromAgent = {}
        self.loansToAgent = {}
        self.powerPlantsForAgent = {}
        self.loanList = []
        self.financialPowerPlantReports = dict()

        # Create Strategic Reserve Operator
        self.sr_operator = dict()

    """
    Repository functions:
    All functions to get/create/set/update elements and values, possibly under criteria. Sorted on elements.
    """

    # ----------------------------------------------------------------------------section loans
    def createLoan(self, from_agent, to, amount, numberOfPayments, loanStartTime, plant):
        loan = Loan()
        loan.setFrom(from_agent)
        loan.setTo(to)
        loan.setAmountPerPayment(amount)
        loan.setTotalNumberOfPayments(numberOfPayments)
        loan.setRegardingPowerPlant(plant)
        loan.setLoanStartTime(loanStartTime)
        loan.setNumberOfPaymentsDone(0)
        plant.setLoan(loan)
        self.loanList.append(loan)
        if from_agent not in self.loansFromAgent.keys():
            self.loansFromAgent['from_agent'] = []
        self.loansFromAgent['from_agent'] = loan
        if to not in self.loansToAgent.keys():
            self.loansToAgent['to'] = []
        self.loansToAgent['to'] = loan
        return loan

    def findLoansFromAgent(self, agent):
        return self.loansFromAgent.get(agent)

    def findLoansToAgent(self, agent):
        return self.loansToAgent.get(agent)

    # ----------------------------------------------------------------------------section Cashflow
    def createCashFlow(self, from_agent, to, amount, type, time, plant):
        cashFlow = CashFlow()
        cashFlow.setFrom(from_agent)
        cashFlow.setTo(to)
        cashFlow.setMoney(amount)
        cashFlow.setType(type)
        cashFlow.setTime(time)
        cashFlow.setRegardingPowerPlant(plant)
        from_agent.setCash(from_agent.getCash() - amount)
        if to is not None:
            to.setCash(to.getCash() + amount)
        # cashFlows.add(cashFlow)
        return cashFlow

    def getCashFlowsForPowerPlant(self, plant, tick):

        pass
        # [cf for cf in self.reps.cashFlows.getRegardingPowerPlant(plant) ][tick]
        #  return cashFlows.stream().filter(lambda p : p.getTime() == tick).filter(lambda p : p.getRegardingPowerPlant() is not None).filter(lambda p : p.getRegardingPowerPlant() is plant).collect(Collectors.toList())
    #
    # def determineLoanAnnuities(self, totalLoan, payBackTime, interestRate):
    #     q = 1 + interestRate
    #     annuity = totalLoan * (q ** payBackTime * (q - 1)) / (q ** payBackTime - 1)
    #     return annuity
    def create_or_update_power_plant_loan(self, plant: PowerPlant,
                                          bidder: EnergyProducer,
                                          bidding_market: Market,
                                          amount: float,
                                          price: float,
                                          time: int) -> PowerPlantDispatchPlan:
        ppdp = next((ppdp for ppdp in self.power_plant_dispatch_plans.values() if ppdp.plant == plant and
                     ppdp.bidding_market == bidding_market and
                     ppdp.tick == time), None)
        pass



    # ----------------------------------------------------------------------------section PowerPlants


    # ----------------------------------------------------------------------------section Candidate

    def get_id_last_power_plant(self) -> int:
        # the last 5 numbers are the power plant list
        return sorted([str(i.id)[-4:] for i in self.power_plants.values()])[-1]

    def get_average_profits(self, powerplants):
        return mean([pp.get_Profit()for pp in powerplants])

    def get_candidate_power_plants_of_technologies(self, technologies) -> List[CandidatePowerPlant]:
        return [i for i in self.candidatePowerPlants.values() if i.technology in technologies]

    def get_investable_candidate_power_plants_by_owner(self, owner: EnergyProducer) -> List[CandidatePowerPlant]:
        return [i for i in self.candidatePowerPlants.values()
                if i.viableInvestment is True and i.owner == owner]

    def get_investable_candidate_power_plants(self) -> List[CandidatePowerPlant]:
        return [i for i in self.candidatePowerPlants.values() if i.viableInvestment is True]

    def calculateCapacityOfExpectedOperationalPlantsperTechnology(self, technology, tick):
        expectedOperationalcapacity = 0
        plantsoftechnology = [i for i in self.power_plants.values() if i.technology.name == technology.name]
        for plant in plantsoftechnology:
            if PowerPlant.isExpectedToBeOperational(plant, tick, (self.current_year + tick)):
                expectedOperationalcapacity += plant.capacity
        return expectedOperationalcapacity

    def calculateCapacityOfOperationalPowerPlantsByTechnology(self, technology):
        plantsoftechnology = [i.capacity for i in self.power_plants.values() if i.technology.name == technology.name
                              and i.status == globalNames.power_plant_status_operational]
        return sum(plantsoftechnology)

    def calculateCapacityOfPowerPlantsByTechnologyInPipeline(self, technology):
        return sum([pp.capacity for pp in self.power_plants.values() if pp.technology.name == technology.name
                    and pp.status == globalNames.power_plant_status_inPipeline])  # pp.isInPipeline(tick)

    def calculateCapacityOfPowerPlantsInPipeline(self):
        return sum(
            [i.capacity for i in self.power_plants.values() if i.status == globalNames.power_plant_status_inPipeline])

    def findPowerGeneratingTechnologyTargetByTechnology(self, technology):
        for i in self.target_investors.values():
            if i.targetTechnology == technology.name and i.targetNode == self.country:
                return i

    def findAllPowerPlantsWithConstructionStartTimeInTick(self, tick):
        return [i for i in self.power_plants if i.getConstructionStartTime() == tick]

    def findAllPowerPlantsWhichAreNotDismantledBeforeTick(self, tick):
        return [i for i in self.power_plants.values() if i.isWithinTechnicalLifetime(tick)]

    def get_operational_power_plants_by_owner(self, owner: EnergyProducer) -> List[PowerPlant]:
        return [i for i in self.power_plants.values()
                if i.owner == owner and i.status == globalNames.power_plant_status_operational]

    def get_operational_and_to_be_decommissioned_power_plants_by_owner(self, owner: EnergyProducer) -> List[PowerPlant]:
        return [i for i in self.power_plants.values()
                if i.owner.name == owner and (
                        i.status == globalNames.power_plant_status_operational or i.status == globalNames.power_plant_status_to_be_decommissioned)]

    def get_operational_power_plants_by_owner_and_technologies(self, owner: EnergyProducer, listofTechnologies) -> List[
        PowerPlant]:
        return [i for i in self.power_plants.values()
                if
                i.owner.name == owner and i.status == globalNames.power_plant_status_operational and i.technology.name in listofTechnologies]

    def get_power_plants_by_status(self, status) -> List[ PowerPlant]:
        return [i for i in self.power_plants.values()
                if  i.status == status]

    def get_investments(self) -> List[ PowerPlant]:
        return [i for i in self.power_plants.values()
                if  i.status == globalNames.power_plant_status_operational]

    def get_power_plants_by_owner(self, owner: str) -> List[PowerPlant]:
        return [i for i in self.power_plants.values()
                if i.owner.name == owner]

    def get_power_plants_to_be_decommissioned(self, owner) -> List[PowerPlant]:
        return [i for i in self.power_plants.values()
                if i.owner.name == owner and i.status == globalNames.power_plant_status_to_be_decommissioned]

    def get_power_plant_operational_profits_by_tick_and_market(self, time: int, market: Market):
        res = 0
        for power_plant in [i for i in self.power_plants.values() if
                            i.status == globalNames.power_plant_status_operational]:
            revenues = self.get_power_plant_electricity_spot_market_revenues_by_tick(power_plant, time)
            mc = power_plant.calculate_marginal_cost_excl_co2_market_cost(self, time)
            total_capacity = self.get_total_accepted_amounts_by_power_plant_and_tick_and_market(power_plant, time,
                                                                                                market)
            res[power_plant.name] = revenues - mc * total_capacity
        return res

    def get_available_power_plant_capacity_at_tick(self, plant: PowerPlant, current_tick: int) -> float:
        ppdps_sum_accepted_amount = sum([float(i.accepted_amount) for i in
                                         self.get_power_plant_dispatch_plans_by_plant(plant)
                                         if i.tick == current_tick])
        return plant.capacity - ppdps_sum_accepted_amount

    def get_power_plant_costs_by_tick_and_market(self, power_plant: PowerPlant, time: int, market: Market) -> float:
        # MC is Euro / MW
        mc = power_plant.calculate_marginal_cost_excl_co2_market_cost(self, time)
        # FOC is Euro
        foc = power_plant.get_actual_fixed_operating_cost()
        # total capacity is in MWh
        total_capacity = self.get_total_accepted_amounts_by_power_plant_and_tick_and_market(power_plant, time, market)
        return foc + mc * total_capacity

    def get_power_plant_emissions_by_tick(self, time: int) -> Dict[str, float]:
        if 'YearlyEmissions' in self.emissions.keys():
            res = self.emissions['YearlyEmissions'].emissions[time]
        else:
            res = {}
        for power_plant in [i for i in self.power_plants.values() if
                            i.status == globalNames.power_plant_status_operational and i.name not in res.keys()]:
            # Total Capacity is in MWh
            total_capacity = self.get_total_accepted_amounts_by_power_plant_and_tick_and_market(power_plant, time,
                                                                                                self.electricity_spot_markets[
                                                                                                    'DutchElectricitySpotMarket'])
            # Emission intensity is in ton CO2 / MWh
            emission_intensity = power_plant.calculate_emission_intensity(self)
            res[power_plant.name] = total_capacity * emission_intensity
        return res

    def get_power_plant_electricity_dispatch(self, power_plant_id: str) -> float:
        try:
            return self.power_plant_dispatch_plans.get(str(power_plant_id))
        except StopIteration:
            logging.warning('No PPDP Price found for plant' + str(power_plant_id))
        return 0

    def get_power_plant_electricity_spot_market_revenues_by_tick(self, power_plant_id: str, time: int) -> float:
        try:  # TODO fix this
            return next(i.revenues for i in self.power_plant_dispatch_plans.values() if
                        i.power_plant_id == power_plant_id and i.tick == time)
        except StopIteration:
            logging.warning('No PPDP Price found for plant  and at time ' + str(time))
        return 0

    def get_total_accepted_amounts_by_power_plant_and_tick_and_market(self, power_plant: PowerPlant, time: int,
                                                                      market: Market) -> float:
        return sum([i.accepted_amount for i in self.power_plant_dispatch_plans.values() if i.tick == time and
                    i.plant == power_plant and i.bidding_market == market])

    # PowerPlantDispatchPlans
    # def get_power_plant_dispatch_plan_price_by_plant_and_time_and_market(self, plant: PowerPlant, time: int,
    #                                                                      market: Market) -> float:
    #     try:
    #         return next(i.price for i in self.power_plant_dispatch_plans.values() if i.plant == plant and i.tick == time
    #                     and i.bidding_market == market)
    #     except StopIteration:
    #         logging.warning('No PPDP Price found for plant ' + plant.name + ' and at time ' + str(time))
    #         return 0

    def get_sorted_bids_by_market_and_time(self, market: Market, time: int) -> \
            List[PowerPlantDispatchPlan]:
        return sorted([i for i in self.bids.values()
                       if i.market == market.name and i.tick == time], key=lambda i: i.price)

    def get_power_plant_dispatch_plans_by_plant(self, plant: PowerPlant) -> List[PowerPlantDispatchPlan]:
        return [i for i in self.power_plant_dispatch_plans.values() if i.plant == plant]

    def get_power_plant_dispatch_plans_by_plant_and_tick(self, plant: PowerPlant, time: int) -> \
            List[PowerPlantDispatchPlan]:
        return [i for i in self.power_plant_dispatch_plans.values() if i.name == plant and i.tick == time]

    def get_accepted_CM_bids(self):
        return [i for i in self.bids.values() if
                i.status == globalNames.power_plant_dispatch_plan_status_partly_accepted or i.status == globalNames.power_plant_dispatch_plan_status_accepted]

    def create_or_update_power_plant_CapacityMarket_plan(self, plant: PowerPlant,
                                                         bidder: EnergyProducer,
                                                         market: Market,
                                                         amount: float,
                                                         price: float,
                                                         time: int) -> Bid:
        bid = next((bid for bid in self.bids.values() if bid.plant == plant.name and \
                    bid.market == market.name and
                    bid.tick == time), None)
        if bid is None:
            # PowerPlantDispatchPlan not found, so create a new one
            name = str(datetime.now())
            bid = Bid(name)

        bid.plant = plant.name
        bid.bidder = bidder.name
        bid.market = market.name
        bid.amount = amount
        bid.price = price
        bid.status = globalNames.power_plant_dispatch_plan_status_awaiting
        bid.accepted_amount = 0
        bid.tick = time
        self.bids[bid.name] = bid
        self.dbrw.stage_bids(bid, time)
        return bid

    def update_installed_pp_results(self, installed_pp_results):
        try:
            for index, result in installed_pp_results.iterrows():
                installed_pp = next(i for i in self.power_plants.values() if i.id == result.identifier)
                installed_pp.add_values_from_df(result)
        except StopIteration:
            logging.warning('power plant technology not found' + str(result.identifier) )
        return None

    def update_candidate_plant_results(self, results):
        try:
            for index, result in results.iterrows():
                candidate = next(i for i in self.candidatePowerPlants.values() if i.id == result.identifier)
                candidate.add_values_from_df(result)
        except StopIteration:
            logging.warning('candidate technology not found' + str(result.identifier)  )
        return None

    def get_unique_candidate_technologies(self):
        try:
            return [i.technology.name for name, i in self.candidatePowerPlants.items()]
        except StopIteration:
            return None

    # def get_project_value(self):
    #     try:
    #         return [name for name, i in self.candidatePowerPlants.items()]
    #     except StopIteration:
    #         return None

    # MarketClearingPoints
    def get_market_clearing_point_for_market_and_time(self, market: Market, time: int) -> Optional[MarketClearingPoint]:
        try:
            return next(i for i in self.market_clearing_points.values() if i.market == market and i.tick == time)
        except StopIteration:
            return None

    def get_market_clearing_point_price_for_market_and_time(self, market: Market, time: int) -> float:
        if time >= 0:
            mcp = self.get_market_clearing_point_for_market_and_time(market, time)
            return mcp.price
        else:
            return 0

    def create_or_update_market_clearing_point(self,
                                               market: Market,
                                               price: float,
                                               volume: float,
                                               time: int) -> MarketClearingPoint:
        mcp = next((mcp for mcp in self.market_clearing_points.values() if mcp.market == market and mcp.tick == time),
                   None)
        if mcp is None:
            # MarketClearingPoint not found, so create a new one
            name = 'MarketClearingPoint ' + str(datetime.now())
            mcp = MarketClearingPoint(name)

        mcp.market = market
        mcp.price = price
        mcp.tick = time
        mcp.volume = volume
        self.market_clearing_points[mcp.name] = mcp
        self.dbrw.stage_market_clearing_point(mcp, time)
        return mcp

    # Markets
    def get_electricity_spot_market_for_plant(self, plant: PowerPlant) -> Optional[ElectricitySpotMarket]:
        try:
            return next(i for i in self.electricity_spot_markets.values() if
                        i.parameters['zone'] == plant.location)
        except StopIteration:
            return None

    def get_capacity_market_for_plant(self, plant: PowerPlant) -> Optional[CapacityMarket]:
        try:
            return next(i for i in self.capacity_markets.values() if
                        i.parameters['zone'] == plant.location)
        except StopIteration:
            return None

    def get_allowances_in_circulation(self, zone: Zone, time: int) -> int:
        return sum([i.banked_allowances[time] for i in self.power_plants.values()
                    if i.location.parameters['Country'] == zone.name])

    def get_co2_market_for_zone(self, zone: Zone) -> Optional[CO2Market]:
        try:
            return next(i for i in self.co2_markets.values()
                        if i.parameters['zone'] == zone.name)
        except StopIteration:
            return None

    def get_co2_market_for_plant(self, power_plant: PowerPlant) -> Optional[CO2Market]:
        return self.get_co2_market_for_zone(self.zones[power_plant.location.parameters['Country']])

    def get_market_stability_reserve_for_market(self, market: Market) -> Optional[MarketStabilityReserve]:
        try:
            return next(i for i in self.market_stability_reserves.values()
                        if i.zone.name == market.parameters['zone'])
        except StopIteration:
            return None

    # SubstanceInFuelMix
    def get_substances_in_fuel_mix_by_plant(self, plant: PowerPlant) -> Optional[SubstanceInFuelMix]:
        if plant.technology.name in self.power_plants_fuel_mix.keys():
            return self.power_plants_fuel_mix[plant.technology.name]
        else:
            return None

    def findAllClearingPointsForSubstanceAndTimeRange(self, substance, timeFrom, timeTo, forecast):

        # return clearingPoints.stream().filter(lambda p : p.getTime() >= timeFrom).filter(lambda p : p.getTime() <= timeTo).
        # filter(lambda p : p.getAbstractMarket().getSubstance() is substance).filter(p -(> p.isForecast()) == forecast).collect(Collectors.toList())
        return

    # Governments
    def get_national_government_by_zone(self, zone: Zone) -> NationalGovernment:
        return next(i for i in self.national_governments.values() if i.governed_zone == zone)

    def get_government(self) -> Government:
        return next(i for i in self.governments.values())

    # PowerGeneratingTechnologies
    def get_power_generating_technology_by_techtype_and_fuel(self, techtype: str, fuel: str):
        try:
            return next(i for i in self.power_generating_technologies.values()
                        if i.techtype == techtype and i.fuel == fuel)
        except StopIteration:
            logging.warning('PowerGeneratingTechnology not found for ' + techtype + ' and ' + fuel)
            return None


    def get_unique_technologies_names(self):
        try:
            return [i.name for i in self.power_generating_technologies.values()]
        except StopIteration:
            return None

    def get_unique_substances_names(self):
        try:
            return [i.name for i in self.substances.values()]
        except StopIteration:
            return None
    # PowerGridNode
    def get_power_grid_node_by_zone(self, zone: str):
        try:
            return next(i for i in self.power_grid_nodes.values() if i.parameters['Country'] == zone)
        except StopIteration:
            return None

    # Hourly Demand
    def get_hourly_demand_by_power_grid_node_and_year(self, zone):
        try:
            return next(i.hourlyDemand for i in self.electricity_spot_markets.values() if i.zone == zone)
        except StopIteration:
            return None

        return

    # Extra functions for strategic reserve
    def calculateCapacityOfPowerPlantsInMarket(self, market):
        if market == 'DutchCapacityMarket':
            temp_location = 'NL'
        elif market == 'GermanCapacityMarket':
            temp_location = 'DE'
        else:
            temp_location = 'None'
        return sum([i.capacity for i in self.power_plants.values() if i.location == temp_location])

    def get_descending_sorted_power_plant_dispatch_plans_by_SRmarket(self, market: Market, time: int) -> \
            List[PowerPlantDispatchPlan]:
        return sorted([i for i in self.bids.values()
                       if i.market == market.name and i.tick == time], key=lambda i: i.price, reverse=True)

    def get_accepted_SR_bids(self):
        return [i for i in self.bids.values() if
                i.status == globalNames.power_plant_status_strategic_reserve]

    def update_power_plant_status(self, plant: PowerPlant, price):
        new_status = globalNames.power_plant_status_strategic_reserve
        new_owner = 'StrategicReserveOperator'
        new_price = price
        for i in self.power_plants.values():
            if i.name == plant:
                i.status = new_status
                i.owner = new_owner
                i.technology.variable_operating_costs = new_price
                self.power_plants[i.name] = i
                self.dbrw.stage_power_plant_status(i)

    # def get_power_plants_in_SR(self) -> List[StrategicReserveOperator]:
    #     return [i for i in self.power_plants.values() if
    #             i.status == globalNames.power_plant_status_strategic_reserve]
    # i.name in self.StrategicReserveOperator.getPlants()]
    #



    def create_or_update_StrategicReserveOperator(self, name: str,
                                                  zone: str,
                                                  priceSR: float,
                                                  percentSR: float,
                                                  volumeSR: float,
                                                  cash: float,
                                                  list_of_plants: list) -> StrategicReserveOperator:
        SRO = next((SRO for SRO in self.sr_operator.values() if SRO.name == name), None)
        if SRO is None:
            name = ("SRO_" + zone)
            SRO = StrategicReserveOperator(name)

        SRO.zone = zone
        SRO.reservePriceSR = priceSR
        SRO.reserveVolumePercentSR = percentSR
        SRO.reserveVolume = volumeSR
        SRO.cash = cash
        SRO.list_of_plants = list_of_plants
        self.sr_operator[SRO.name] = SRO
        self.dbrw.stage_sr_operator(SRO)
        return SRO

    def update_power_plant_status_ger_first_year(self, plant: PowerPlant, price):
        new_status = globalNames.power_plant_status_strategic_reserve
        new_owner = 'StrategicReserveOperator'
        new_price = price
        for i in self.power_plants.values():
            if i.name == plant:
                new_age = i.technology.expected_lifetime - 4
                i.age = new_age
                i.status = new_status
                i.owner = new_owner
                i.technology.variable_operating_costs = new_price
                self.power_plants[i.name] = i
                self.dbrw.stage_power_plant_status(i)


    # def set_power_plants_in_SR(self, plant):
    #     self.plants_in_SR.append(plant)
    #
    # def get_power_plants_in_SR(self):
    #     return self.plants_in_SR
    #
    # def get_power_plants_in_SR_by_name(self):
    #     return [i.name for i in self.plants_in_SR]

    # def get_fixed_costs_of_SR_plant(self, plant):
    #     for i in self.power_plants.values():
    #         if i.name == plant.name:
    #             cost = i.actualFixedOperatingCost
    #             return cost
    #
    #     # return [i.actualFixedOperatingCost for i in self.power_plants.values() if i.name == plant.name]
    #
    # def get_strategic_reserve_price(self, operator: StrategicReserveOperator):
    #     return operator.getReservePriceSR()


    # def create_or_update_power_plant_StrategicReserve_plan(self, plant: PowerPlant,
    #                                                      bidder: EnergyProducer,
    #                                                      market: Market,
    #                                                      amount: float,
    #                                                      price: float,
    #                                                      time: int) -> Bid:
    #     bid = next((bid for bid in self.bids_sr.values() if bid.plant == plant.name and \
    #                 bid.market == market.name and
    #                 bid.tick == time), None)
    #     if bid is None:
    #         # PowerPlantDispatchPlan not found, so create a new one
    #         name = str(datetime.now())
    #         bid = Bid(name)
    #
    #     bid.plant = plant
    #     bid.bidder = bidder
    #     bid.market = market
    #     bid.amount = amount
    #     bid.price = price
    #     bid.status = globalNames.power_plant_dispatch_plan_status_awaiting
    #     bid.accepted_amount = 0
    #     bid.tick = time
    #     self.bids_sr[bid.name] = bid
    #     self.dbrw.stage_bids(bid, time)
    #     return bid



    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return str(vars(self))

from modules.marketmodule import MarketModule
from util.repository import Repository
from domain.markets import ElectricitySpotMarket
import globalNames
from domain.cashflow import *


class StrategicReserve(MarketModule):
    """
    The class that solves the strategic reserve
    """

    def __init__(self, reps: Repository):
        super().__init__('Strategic reserve', reps)

    def act(self, strategicReserveOperator):
        for market in self.reps.capacity_markets.values():
            node = self.reps.get_power_grid_node_by_zone(market.parameters['zone'])
            peak_load = max(
                self.reps.get_hourly_demand_by_power_grid_node_and_year(node, self.reps.current_tick +
                                                                        self.reps.start_simulation_year))
            trend = ElectricitySpotMarket.getDemandGrowthTrend().getValue(self.reps.current_tick)
            # trend is calculated in substances
            peakLoadforMarket = trend * peakLoadforMarket

            # Set volume to be contracted
            strategicReserveOperator.setReserveVolume(
                peakLoadforMarket * strategicReserveOperator.getReserveVolumePercentSR())

            volumetobeContracted = strategicReserveOperator.getReserveVolume()
            dispatchPrice = strategicReserveOperator.getReservePriceSR()
            # Find difference between peak load and peak capacity
            clearingEpsilon = 0.001
            sumofContractedBids = 0

            for currentPPDP in self.reps.findDescendingSortedPowerPlantDispatchPlansForSegmentForTime(
                    self.reps.current_tick, False):
                if (currentPPDP.getPowerPlant().getAgeFraction() < 1.2):
                    if volumetobeContracted == 0:
                        isORMarketCleared = True
                    elif isORMarketCleared == False:
                        # check if already not contracted
                        # logger.warn("volume of current PPDP " + currentPPDP.getAmount())
                        if volumetobeContracted - (sumofContractedBids + currentPPDP.getAmount()) >= clearingEpsilon:
                            currentPPDP.setSRstatus(globalNames.capacity_mechanism_contracted)
                            sumofContractedBids += currentPPDP.getAmount()
                            currentPPDP.setOldPrice(currentPPDP.getPrice())
                            currentPPDP.setPrice(dispatchPrice)
                            # Pays O&M costs to the generated for the contracted capacity
                            Loan = 0
                            # if there are left loan payments
                            if (currentPPDP.getPowerPlant().getLoan().getTotalNumberOfPayments() - currentPPDP.getPowerPlant().getLoan().getNumberOfPaymentsDone()) > 0:
                                loan = (currentPPDP.getPowerPlant().getLoan().getAmountPerPayment())
                                money = (currentPPDP.getPowerPlant().getActualFixedOperatingCost()) + loan
                            else:
                                money = (currentPPDP.getPowerPlant().getActualFixedOperatingCost())
                            self.reps.createCashFlow(strategicReserveOperator, currentPPDP.getBidder(), money,
                                                     CashFlow.STRRESPAYMENT, self.reps.current_tick,
                                                     currentPPDP.getPowerPlant())

                        elif volumetobeContracted - (sumofContractedBids + currentPPDP.getAmount()) < clearingEpsilon:
                            currentPPDP.setSRstatus(globalNames.power_plant_dispatch_plan_status_partly_accepted)
                            sumofContractedBids += currentPPDP.getAmount()
                            currentPPDP.setOldPrice(currentPPDP.getPrice())
                            currentPPDP.setPrice(dispatchPrice)

                            isORMarketCleared = True
                            # Pays O&M costs and outstanding loans to the
                            # generated for the contracted capacity
                            Loan = 0
                            if (
                                    currentPPDP.getPowerPlant().getLoan().getTotalNumberOfPayments() - currentPPDP.getPowerPlant().getLoan().getNumberOfPaymentsDone()) > 0:
                                Loan = (currentPPDP.getPowerPlant().getLoan().getAmountPerPayment())
                            money = ((currentPPDP.getPowerPlant().getActualFixedOperatingCost()) + Loan)
                            self.reps.createCashFlow(strategicReserveOperator, currentPPDP.getBidder(), money,
                                                     CashFlow.STRRESPAYMENT, self.reps.current_tick,
                                                     currentPPDP.getPowerPlant())

                        else:
                            currentPPDP.setSRstatus(globalNames.capacity_mechanism_not_contracted)

                    if volumetobeContracted - sumofContractedBids < clearingEpsilon:
                        isORMarketCleared = True

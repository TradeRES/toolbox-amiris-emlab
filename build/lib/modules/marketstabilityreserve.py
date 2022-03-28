"""
This file contains all classes towards the MarketStabilityReserve.

Jim Hommes - 13-5-2021
"""
from modules.defaultmodule import DefaultModule
from util.repository import Repository


class DetermineMarketStabilityReserveFlow(DefaultModule):
    """
    This class determines the action of the MarketStabilityReserve.
    In the CO2Auction, when calculating the CO2 Cap the MSR is taken into consideration.

    This class checks whether the amount of EUAs in circulation triggers the upper or lower trigger.
    If it triggers the upper trigger, 12% of the EUAs are withdrawn.
    If it triggers the lower trigger, the MSR releases a fixed number (according to a trend) of EUAs.
    """
    def __init__(self, reps: Repository):
        super().__init__("Market Stability Reserve: Determine Flows", reps)

    def act(self):
        if self.reps.current_tick > 1:
            for msr in self.reps.market_stability_reserves.values():
                time = self.reps.current_tick - 2
                euas_in_circulation = self.reps.get_allowances_in_circulation(msr.zone, time)
                if euas_in_circulation > msr.upper_trigger_trend.get_value(time):
                    msr.flow = 0.12 * euas_in_circulation
                elif euas_in_circulation < msr.lower_trigger_trend.get_value(time):
                    msr.flow = -1 * min(msr.release_trend.get_value(self.reps.current_tick),
                                        msr.reserve[self.reps.current_tick])
                msr.reserve[self.reps.current_tick] += msr.flow
                self.reps.dbrw.stage_market_stability_reserve(msr, msr.reserve[self.reps.current_tick],
                                                              self.reps.current_tick)




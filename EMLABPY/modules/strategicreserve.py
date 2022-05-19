from modules.marketmodule import MarketModule
from util.repository import Repository


# class StrategicReserveOperatorRole(MarketModule):
#
#     def act(self, strategicReserveOperator):
#
#         peakLoadforMarketNOtrend = getReps().peakLoadbyZoneMarketandTime(curZone, market)
#
#         trend = market.getDemandGrowthTrend().getValue(getCurrentTick())
#
#         peakLoadforMarket = trend * peakLoadforMarketNOtrend
#
#         #multiply by whatever factor
#         segmentCounter = 0
#         # Set volume to be contracted
#
#         strategicReserveOperator.setReserveVolume(peakLoadforMarket * strategicReserveOperator.getReserveVolumePercentSR())
#         #logger.warn(strategicReserveOperator.setReserveVolume(peakLoadforMarket*strategicReserveOperator.getReserveVolumePercent()))
#
#         #Find peak supply in the market
#         # double peakCapacityforMarket = getReps().powerPlantRepository.calculatePeakCapacityOfOperationalPowerPlantsInMarket(market,
#         #         getCurrentTick())
#         # Find difference between peakload and peak capacity
#         # Sets Dispatch price set by operator
#         strategicReserveOperator.getReservePriceSR()
#         #logger.warn(" Reserve Price " + strategicReserveOperator.getReservePriceSR())
#         # Contract Powers Power Plants
#
#         # Iterable<Bid> sortedListofBidPairs = bidRepository.findOffersDescendingForMarketForTime(currentMarket, getCurrentTick())
#         #finds List of all segments
#         #List<Segment> segments = Utils.asList(getReps().segmentRepository.findAll())
#         #for(Segment currentSegment: getReps().segmentRepository.findAll()){
#         #segmentCounter += 1
#         #}
#         # Count all segments in the given market
#         segmentCounter = getReps().segments.size()
#         # find all segments for the given market
#         for currentSegment in getReps().segments:
#             #logger.warn("Current segment is" + currentSegment)
#             #find query for specific market
#
#             isORMarketCleared = False
#             sumofContractedBids = 0
#             volumetobeContracted = strategicReserveOperator.getReserveVolume()
#             #logger.warn("volumetobeContracted " + volumetobeContracted)
#             clearingEpsilon = 0.001
#             dispatchPrice = strategicReserveOperator.getReservePriceSR()
#             #logger.warn("dispatchPrice " + dispatchPrice)
#             #double reserveMargin = peakCapacityforMarket-peakLoadforMarket
#
#
#
#             for currentPPDP in getReps().findDescendingSortedPowerPlantDispatchPlansForSegmentForTime(currentSegment, getCurrentTick(), False):
#
#                 #logger.warn("Bidding Market " + currentPPDP.getBiddingMarket().getNodeId().intValue())
#                 #logger.warn("Bidding Volume" + (currentPPDP.getAmount()))
#                 #logger.warn("current Market" + market.getNodeId().intValue())
#                 # **use querying for market**
#                 if currentPPDP.getBiddingMarket() is market:
#                     #logger.warn("isOR market cleared" + isORMarketCleared)
#
#                     # Check the size of margin
#
#                     #                     if (strategicReserveOperator.getReserveVolume()>reserveMargin){
#                     #                        if (reserveMargin-currentPPDP.getAmount()>strategicReserveOperator.getReserveVolume()){
#                     #                            currentPPDP.setSRstatus(PowerPlantDispatchPlan.NOT_CONTRACTED)
#                     #                            reserveMargin -= currentPPDP.getAmount()
#                     #                        }
#                     #
#                     #                    }
#                     if volumetobeContracted == 0:
#                         isORMarketCleared = True
#                     elif isORMarketCleared == False:
#                         #logger.warn("volume of current PPDP " + currentPPDP.getAmount())
#                         if volumetobeContracted - (sumofContractedBids + currentPPDP.getAmount()) >= clearingEpsilon:
#
#                             # check if already not contracted
#                             #if(currentPPDP.getSRstatus()!=PowerPlantDispatchPlan.NOT_CONTRACTED){
#                             #logger.warn("RemainingVolume" + (volumetobeContracted-(sumofContractedBids + currentPPDP.getAmount())))
#                             currentPPDP.setSRstatus(emlab.gen.domain.market.electricity.PowerPlantDispatchPlan.CONTRACTED)
#                             #logger.warn("SRSTATUS " +currentPPDP.getSRstatus())
#                             sumofContractedBids += currentPPDP.getAmount()
#                             currentPPDP.setOldPrice(currentPPDP.getPrice())
#                             #logger.warn("Old Price" + currentPPDP.getOldPrice())
#                             currentPPDP.setPrice(dispatchPrice)
#
#                             #logger.warn("New Price" + currentPPDP.getPrice())
#                             # Pays O&M costs to the generated for the contracted capacity
#                             Loan = 0
#                             if (currentPPDP.getPowerPlant().getLoan().getTotalNumberOfPayments() - currentPPDP.getPowerPlant().getLoan().getNumberOfPaymentsDone()) > 0:
#                                 Loan = (currentPPDP.getPowerPlant().getLoan().getAmountPerPayment())
#
#                             #JAVA TO PYTHON CONVERTER TODO TASK: Java to Python Converter cannot determine whether both operands of this division are integer types - if they are then you should change 'lhs / rhs' to 'math.trunc(lhs / float(rhs))':
#                             money = ((currentPPDP.getPowerPlant().getActualFixedOperatingCost()) + Loan) / segmentCounter
#                             #logger.warn("Annual FOC "+ currentPPDP.getPowerPlant().getTechnology().getFixedOperatingCost())
#                             #logger.warn("No of Segments " +segmentCounter)
#                             #logger.warn("Money Paid " +money)
#
#                             #logger.warn("SRO "+ strategicReserveOperator.getName() +" CASH Before" +strategicReserveOperator.getCash())
#                             #logger.warn("Owner " + currentPPDP.getBidder().getName() + "money Before" +currentPPDP.getBidder().getCash())
#                             getReps().createCashFlow(strategicReserveOperator, currentPPDP.getBidder(), money, emlab.gen.domain.contract.CashFlow.STRRESPAYMENT, getCurrentTick(), currentPPDP.getPowerPlant())
#
#                             #logger.warn("SRO's CASH After" +strategicReserveOperator.getCash())
#                             #logger.warn("Owner " + currentPPDP.getBidder().getName() + " money After" +currentPPDP.getBidder().getCash())
#                             # }
#                         elif volumetobeContracted - (sumofContractedBids + currentPPDP.getAmount()) < clearingEpsilon:
#
#                             # if(currentPPDP.getSRstatus()!=PowerPlantDispatchPlan.NOT_CONTRACTED){
#                             currentPPDP.setSRstatus(emlab.gen.domain.market.electricity.PowerPlantDispatchPlan.PARTLY_CONTRACTED)
#                             #logger.warn("SRSTATUS " +currentPPDP.getSRstatus())
#                             sumofContractedBids += currentPPDP.getAmount()
#                             currentPPDP.setOldPrice(currentPPDP.getPrice())
#                             #logger.warn("Old Price" + currentPPDP.getOldPrice())
#                             currentPPDP.setPrice(dispatchPrice)
#
#                             #logger.warn("New Price" + currentPPDP.getPrice())
#                             isORMarketCleared = True
#                             # Pays O&M costs and outstanding loans to the
#                             # generated for the contracted capacity
#                             Loan = 0
#                             if (currentPPDP.getPowerPlant().getLoan().getTotalNumberOfPayments() - currentPPDP.getPowerPlant().getLoan().getNumberOfPaymentsDone()) > 0:
#                                 Loan = (currentPPDP.getPowerPlant().getLoan().getAmountPerPayment())
#
#                             #JAVA TO PYTHON CONVERTER TODO TASK: Java to Python Converter cannot determine whether both operands of this division are integer types - if they are then you should change 'lhs / rhs' to 'math.trunc(lhs / float(rhs))':
#                             money = ((currentPPDP.getPowerPlant().getActualFixedOperatingCost()) + Loan) / segmentCounter
#                             #logger.warn("Annual FOC "+ currentPPDP.getPowerPlant().getTechnology().getFixedOperatingCost())
#                             #logger.warn("No of Segments " +segmentCounter)
#                             #logger.warn("Money Paid " +money)
#
#                             #logger.warn("SRO "+ strategicReserveOperator.getName() +" CASH Before" +strategicReserveOperator.getCash())
#                             #logger.warn("Owner " + currentPPDP.getBidder().getName() + "money Before" +currentPPDP.getBidder().getCash())
#                             getReps().createCashFlow(strategicReserveOperator, currentPPDP.getBidder(), money, emlab.gen.domain.contract.CashFlow.STRRESPAYMENT, getCurrentTick(), currentPPDP.getPowerPlant())
#
#                             #logger.warn("SRO's CASH After" +strategicReserveOperator.getCash())
#                             #logger.warn("Owner " + currentPPDP.getBidder().getName() + " money After" +currentPPDP.getBidder().getCash())
#                             #}
#
#                     else:
#                         currentPPDP.setSRstatus(emlab.gen.domain.market.electricity.PowerPlantDispatchPlan.NOT_CONTRACTED)
#
#                     #logger.warn(volumetobeContracted-sumofContractedBids)
#                     if volumetobeContracted - sumofContractedBids < clearingEpsilon:
#                         #logger.warn("is market clear" + isORMarketCleared)
#                         isORMarketCleared = True
#                     #logger.warn(" iS OR CLEARED "+isORMarketCleared)
#                     #logger.warn("Price is "+currentPPDP.getPrice())
#                     #                    currentPPDP.persist()
#         #logger.warn("cash of SR " +strategicReserveOperator.getCash())

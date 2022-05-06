class MarketInformation:

    def __init__(self, market, expectedDemand, fuelPrices, co2price, time):
        #instance fields found by Java to Python Converter:
        self.expectedElectricityPricesPerSegment = None
        self.maxExpectedLoad = 0
        self.meritOrder = None
        self.capacitySum = 0
        # determine expected power prices
        self.expectedElectricityPricesPerSegment = {}
        marginalCostMap = {}
        self.capacitySum = 0


        # # get merit order for this market

        # for plant in getReps().findExpectedOperationalPowerPlantsInMarket(market, time):
        #     #double plantMarginalCost = determineExpectedMarginalCost(plant, fuelPrices, co2price)
        #     plantMarginalCost = determineExpectedMarginalCost(plant)
        #     marginalCostMap.update({plant: plantMarginalCost})
        #     self.capacitySum += plant.getActualNominalCapacity()
        #
        # #get difference between technology target and expected operational capacity
        # for pggt in getReps().findAllPowerGeneratingTechnologyTargetsByMarket(market):
        #     expectedTechnologyCapacity = getReps().calculateCapacityOfExpectedOperationalPowerPlantsInMarketAndTechnology(market, pggt.getPowerGeneratingTechnology(), time)
        #     targetDifference = pggt.getTrend().getValue(time) - expectedTechnologyCapacity
        #     if targetDifference > 0:
        #         plant = getReps().createAndSpecifyTemporaryPowerPlant(getCurrentTick(), EnergyProducer(), getReps().findFirstPowerGridNodeByElectricitySpotMarket(market), pggt.getPowerGeneratingTechnology())
        #         plant.setActualNominalCapacity(targetDifference)
        #         myFuelPrices = {}
        #         for fuel in plant.getTechnology().getFuels():
        #             myFuelPrices.update({fuel: fuelPrices[fuel]})
        #         plant.setFuelMix(calculateFuelMix(plant, myFuelPrices, co2price))
        #         plantMarginalCost = determineExpectedMarginalCost(plant)
        #         #double plantMarginalCost = determineExpectedMarginalCost(plant, fuelPrices, co2price)
        #         marginalCostMap.update({plant: plantMarginalCost})
        #         self.capacitySum += targetDifference
        #
        # comp = MapValueComparator(marginalCostMap)
        # self.meritOrder = dict(comp)
        # self.meritOrder.putAll(marginalCostMap)
        #
        # numberOfSegments = getReps().segments.size()
        #
        # demandFactor = float(expectedDemand[market])
        #
        # # find expected prices per segment given merit order
        # for segmentLoad in market.getLoadDurationCurve():
        #
        #     expectedSegmentLoad = segmentLoad.getBaseLoad() * demandFactor
        #
        #     if expectedSegmentLoad > self.maxExpectedLoad:
        #         self.maxExpectedLoad = expectedSegmentLoad
        #
        #     segmentSupply = 0
        #     segmentPrice = 0
        #     totalCapacityAvailable = 0
        #
        #     for plantCost in self.meritOrder.entrySet():
        #         plant = plantCost.getKey()
        #         plantCapacity = 0
        #         # Determine available capacity in the future in this segment
        #         plantCapacity = plant.getExpectedAvailableCapacity(time, segmentLoad.getSegment(), numberOfSegments)
        #         totalCapacityAvailable += plantCapacity
        #         # logger.warn("Capacity of plant " + plant.toString() +
        #         # " is " +
        #         # plantCapacity/plant.getActualNominalCapacity())
        #         if segmentSupply < expectedSegmentLoad:
        #             segmentSupply += plantCapacity
        #             segmentPrice = plantCost.getValue()
        #     # logger.warn("Segment " +
        #     # segmentLoad.getSegment().getSegmentID() + " supply equals " +
        #     # segmentSupply + " and segment demand equals " +
        #     # expectedSegmentLoad)
        #     # Find strategic reserve operator for the market.
        #     reservePrice = 0
        #     reserveVolume = 0
        #     for operator in getReps().strategicReserveOperators:
        #         market1 = getReps().findElectricitySpotMarketForZone(operator.getZone())
        #         if market is market1:
        #             reservePrice = operator.getReservePriceSR()
        #             reserveVolume = operator.getReserveVolume()
        #
        #
        #     report = getReps().findMarketInformationReport(segmentLoad.getSegment(), agent, time)
        #     report.schedule = schedule
        #     report.setMarket(market)
        #     report.setExpectedSegmentLoad(expectedSegmentLoad)
        #     report.setSegmentSupply(segmentSupply)
        #     report.setTotalCapacityAvailable(totalCapacityAvailable)
        #
        #     report.setCO2price(co2price)
        #     report.setFuelPrices(fuelPrices)
        #
        #
        #     expectedElectricityPrice = None
        #
        #
        #     if segmentSupply >= expectedSegmentLoad and ((totalCapacityAvailable - expectedSegmentLoad) <= (reserveVolume)):
        #
        #         expectedElectricityPrice = reservePrice
        #         report.setResult(1)
        #
        #     elif segmentSupply >= expectedSegmentLoad and ((totalCapacityAvailable - expectedSegmentLoad) > (reserveVolume)):
        #
        #         expectedElectricityPrice = segmentPrice
        #         report.setResult(2)
        #
        #     else:
        #         expectedElectricityPrice = market.getValueOfLostLoad()
        #         report.setResult(3)
        #
        #     self.expectedElectricityPricesPerSegment.update({segmentLoad.getSegment(): expectedElectricityPrice})
        #
        #     report.setExpectedElectricityPrice(expectedElectricityPrice)

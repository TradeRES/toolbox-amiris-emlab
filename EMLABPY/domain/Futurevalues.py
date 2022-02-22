# Set future values to AMIRIS


from emlabpy.domain.import_object import *
class UpdatefutureValues():
    def __init__(self, reps: Repository):
        self.__useFundamentalCO2Forecast = False
        self.futureTimePoint = 5
        self.__expectedCO2Price = None
        self.__expectedFuelPrices = None
        self.__expectedDemand = None
        self.__market = None
        self.marketInformation = None
        self.agent = None

    def initEvaluationForEnergyProducer(, ):
        setAgent()
        setMarket()
        setTimeHorizon()
        setExpectations()

    def setAgent(EnergyProducer):
        pass

    def setMarket(ElectricitySpotMarket):
        pass

    def setExpectations():
        expectedFuelPrices = predictFuelPrices(EnergyProducer, futureTimePoint)
        if useFundamentalCO2Forecast==False:
            expectedCO2Price = determineExpectedCO2PriceInclTaxAndFundamentalForecast(
                futureTimePoint, agent.getNumberOfYearsBacklookingForForecasting(), 0, getCurrentTick())
        else:
            expectedCO2Price = determineExpectedCO2PriceInclTax(futureTimePoint,
                                                                agent.getNumberOfYearsBacklookingForForecasting(), getCurrentTick())

        return expectedFuelPrices

    def setTimeHorizon():
        return futureTimePoint = getCurrentTick() + agent.InvestmentFutureTimeHorizon()



    def predictFuelPrices(EnergyProducer, futureTimePoint):
        for substance in substances:
            GeometricTrendRegression

    def createPowerPlant():
        # creats technology, size, fuelmix

        #for fuel in technology.getFuels:


        pass



from emlabpy.domain.CandidatePowerPlant import *
from emlabpy.modules.defaultmodule import DefaultModule
import pandas as pd


class FuturePowerPlants(DefaultModule):
    """Ths function creates the power plants that will be analyzed as possible investments
        creates the Candidate Power Plants
    """

    def __init__(self, reps):
        super().__init__("Define Future Power Plants", reps)
        self.newPowerPlant = None
        self.newTechnologies = None
        self.lastrenewableId = 0
        self.lastconventionalId = 0
        self.laststorageId = 0
        self.futureDemand = None
        self.futureYear = 0
        self.futureInvestmentyear = 0
        self.futureDemand = None
        self.RESLabel = "VariableRenewableOperator"
        self.conventionalLabel = "ConventionalPlantOperator"
        self.storageLabel = "StorageTrader"
        reps.dbrw.stage_init_future_prices_structure()
        self.agent = "Producer1"
        self.powerPlantsList = []
        self.iteration = 0

    def act(self):
        self.setTimeHorizon()
        self.setExpectations()
        self.createCandidatePowerPlants()

    def setTimeHorizon(self):
        self.futureYear = self.reps.current_year + self.reps.energy_producers[
            self.agent].getInvestmentFutureTimeHorizon()

    def setExpectations(self):
        for k, substance in self.reps.substances.items():
            futureprice = substance.get_price_for_future_tick(self.reps, self.futureYear, substance)
            self.reps.dbrw.stage_future_fuel_prices(self.futureYear, substance, futureprice)  # todo: save this as a map in DB
        # self.predictDemand()
        # self.nextDemand()

    def createCandidatePowerPlants(self):
        self.getlastIds()
        self.iteration = self.reps.dbrw.get_last_iteration( self.futureYear)
        if self.iteration > 0: # if there was no iteration before leave it as zero
            self.iteration += 1

        #
        self.reps.dbrw.stage_init_power_plants_list(self.iteration)

        for key, candidateTechnology in self.reps.newTechnology.items():
            if candidateTechnology.type == self.RESLabel:
                self.lastrenewableId += 1
                object_name = self.lastrenewableId
            elif candidateTechnology.type == self.conventionalLabel:
                self.lastconventionalId += 1
                object_name = self.lastconventionalId
            elif candidateTechnology.type == self.storageLabel:
                self.laststorageId += 1
                object_name = self.laststorageId
            self.reps.candidatePowerPlants[object_name] = CandidatePowerPlant(object_name)
            self.reps.candidatePowerPlants[object_name].add_parameter_value(self.reps, "type", candidateTechnology.type,
                                                                            0)
            self.reps.candidatePowerPlants[object_name].add_parameter_value(self.reps, "technology",
                                                                            candidateTechnology.name, 0)
            self.reps.candidatePowerPlants[object_name].add_parameter_value(self.reps, "InstalledPowerInMW",
                                                                            candidateTechnology.InstalledPowerInMW, 0)
            print("New technology ", object_name, candidateTechnology.type, candidateTechnology.name, candidateTechnology.InstalledPowerInMW)

            self.powerPlantsList.append(object_name)
        #df = pd.DataFrame.from_dict(candidateTechnology.__dict__, orient='index')
        #df.to_excel('forYaml.xlsx')
        print(self.powerPlantsList, self.iteration, self.futureYear)
        self.reps.dbrw.stage_new_power_plants_ids( self.powerPlantsList, self.iteration, self.futureYear)

            # parameternames = [Technology, Status, CommissionedYear, InstalledPowerInMW, FuelType, Label]

    def getlastIds(self):
        # get maximum number of power plan
        lastbuiltrenewable = []
        lastbuiltconventional = []
        lastbuiltstorage = []
        for id, pp in self.reps.power_plants.items():
            if pp.label == self.RESLabel:
                lastbuiltrenewable.append(int(id))
            elif pp.label == self.conventionalLabel:
                lastbuiltconventional.append(int(id))
            elif pp.label == self.storageLabel:
                lastbuiltstorage.append(int(id))
        lastbuiltrenewable.sort()
        lastbuiltconventional.sort()
        lastbuiltstorage.sort()
        self.lastrenewableId = lastbuiltrenewable[-1]
        self.lastconventionalId = lastbuiltconventional[-1]
        if len(lastbuiltstorage) > 0:  # TODO: give numeration to storage so that it doesnt overlap with renewables
            self.laststorageId = lastbuiltstorage[-1]

# def predictFuelPrices(self, agent, futureTimePoint):
#     # Fuel Prices
#     expectedFuelPrices = {}
#     for substance in self.reps.substances:
#         #Find Clearing Points for the last 5 years (counting current year as one of the last 5 years).
#         cps = self.reps.findAllClearingPointsForSubstanceAndTimeRange(substance, self.reps.current_tick - (agent.getNumberOfYearsBacklookingForForecasting() - 1) , self.reps.current_tick, False)
#         #Create regression object
#         gtr = GeometricTrendRegression()
#         for clearingPoint in cps:
#             #logger.warn("CP {}: {} , in" + clearingPoint.getTime(), substance.getName(), clearingPoint.getPrice())
#             gtr.addData(clearingPoint.getTime(), clearingPoint.getPrice())
#         expectedFuelPrices.update({substance: gtr.predict(futureTimePoint)})
#         #logger.warn("Forecast {}: {}, in Step " +  futureTimePoint, substance, expectedFuelPrices.get(substance))
#     return expectedFuelPrices

#     if not useFundamentalCO2Forecast:
#         expectedCO2Price = determineExpectedCO2PriceInclTaxAndFundamentalForecast(futureTimePoint, agent.getNumberOfYearsBacklookingForForecasting(), 0, getCurrentTick())
#     else:
#         expectedCO2Price = determineExpectedCO2PriceInclTax(futureTimePoint, agent.getNumberOfYearsBacklookingForForecasting(), getCurrentTick())
#     expectedDemand = {}
#     for elm in getReps().electricitySpotMarkets:
#         gtr = GeometricTrendRegression()
#         time = getCurrentTick()
#         while time > getCurrentTick() - agent.getNumberOfYearsBacklookingForForecasting() and time >= 0:
#             gtr.addData(time, elm.getDemandGrowthTrend().getValue(time))
#             time = time - 1
#         expectedDemand.put(elm, gtr.predict(futureTimePoint))
#     marketInformation = MarketInformation(market, expectedDemand, expectedFuelPrices, expectedCO2Price.get(market).doubleValue(), futureTimePoint)

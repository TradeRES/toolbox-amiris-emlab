from domain.energyproducer import EnergyProducer

class TargetInvestor(EnergyProducer):
    def __init__(self, name):
        super().__init__(name)
        self.powerGeneratingTechnologyTargets = None
        self.specificPowerGridNode = None


    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'targetTechnology':
            self.powerGeneratingTechnologyTargets = parameter_value
        elif parameter_name == 'targetNode':
            self.specificPowerGridNode = parameter_value

    def getPowerGenerationTechnologyTargets(self):
        return self.powerGeneratingTechnologyTargets

    def setPowerGenerationTechnologyTargets(self, powerGeneratingTechnologyTargets):
        self.powerGeneratingTechnologyTargets = powerGeneratingTechnologyTargets

    def getSpecificPowerGridNode(self):
        return self.specificPowerGridNode

    def setSpecificPowerGridNode(self, specificPowerGridNode):
        self.specificPowerGridNode = specificPowerGridNode

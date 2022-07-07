from domain.energyproducer import EnergyProducer

class TargetInvestor(EnergyProducer):
    def __init__(self, name):
        super().__init__(name)
        self.targetTechnology = None
        self.targetNode = None


    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'targetTechnology':
            self.targetTechnology = parameter_value
        elif parameter_name == 'targetNode':
            self.targetNode = parameter_value

    def getPowerGenerationTechnologyTargets(self):
        return self.targetTechnology

    def setPowerGenerationTechnologyTargets(self, targetTechnology):
        self.targetTechnology = targetTechnology

    def getSpecificPowerGridNode(self):
        return self.targetNode

    def setSpecificPowerGridNode(self, targetNode):
        self.targetNode = targetNode

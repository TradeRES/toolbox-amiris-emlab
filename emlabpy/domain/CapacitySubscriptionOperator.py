from domain.actors import EMLabAgent
class CapacitySubscriptionOperator(EMLabAgent):

    def __init__(self, name):
        super().__init__(name)
        self.VOLL_CS = None


    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative):
        # for list of plants and reserve volume, pass the tick as alternative
        setattr(self, parameter_name, parameter_value)


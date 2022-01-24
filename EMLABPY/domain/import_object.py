

class ImportObject:
    """
    Parent Class for all objects imported from Spine
    Will probably become redundant in the future as it's neater to translate parameters to Python parameters
    instead of a dict like this
    """

    def __init__(self, name: str):
        self.name = name
        self.parameters = {}

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative: str):
        self.parameters[parameter_name] = parameter_value

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return str(vars(self))

from domain.import_object import *

class I(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.invested = {}
        self.project_value_year =  {}

    def add_parameter_value(self, parameter_name: str, parameter_value, alternative: str):
        print( parameter_name, parameter_value, alternative)
        year, iteration = parameter_name.split('-')
        if alternative == "Invested":
            if year not in self.invested.keys():
                self.invested[year] = 1
            else:
                self.invested[year] += 1
        else:
            if year not in self.project_value_year.keys():
                self.project_value_year[year] = [parameter_value]
            else:
                self.project_value_year[year].append(parameter_value)

test = I(1)
test.add_parameter_value( "2020-1", 213123, "Invested")
test.add_parameter_value( "2020-1", 213123, 0)
test.add_parameter_value( "2020-1", 213123, "Invested")
test.add_parameter_value( "2020-1", 213123, 0)

print(test)



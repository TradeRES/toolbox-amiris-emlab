from domain.actors import EMLabAgent
import pandas as pd

class CapacitySubscriptionConsumer(EMLabAgent):

    def __init__(self, name):
        super().__init__(name)
        self.WTP = None
        self.max_subscribed_percentage = None
        self.subscribed_yearly = None
        self.subscribed_volume = None
        self.cummulative_quantity = 0
        self.bid = 0

    def add_parameter_value(self, reps, parameter_name: str, parameter_value, alternative):
        # for list of plants and reserve volume, pass the tick as alternative
        if parameter_name == 'WTP':
            self.WTP = float(parameter_value)
        elif parameter_name == 'max_subscribed_percentage':
            self.max_subscribed_percentage = float(parameter_value)
        elif parameter_name == 'subscribed_yearly':
            if reps.capacity_remuneration_mechanism == "capacity_subscription" and reps.runningModule in ["run_CRM", "run_investment_module" , "run_financial_results", "plotting"]:
                array = parameter_value.to_dict()
                values = [float(i[1]) for i in array["data"]]
                index = [int(i[0]) for i in array["data"]]
                pd_series = pd.Series(values, index=index)
                self.subscribed_yearly = pd_series
        # elif parameter_name == 'bid':
        #     array = parameter_value.to_dict()
        #     values = [float(i[1]) for i in array["data"]]
        #     index = [int(i[0]) for i in array["data"]]
        #     pd_series = pd.Series(values, index=index)
        #     if reps.runningModule == "plotting":
        #         self.bid = pd_series
        #     elif reps.capacity_remuneration_mechanism == "capacity_subscription" and reps.runningModule in ["run_CRM", "run_investment_module"]:
        #         self.bid = round(pd_series[reps.current_tick],3)
        #     elif reps.capacity_remuneration_mechanism == "capacity_subscription" and reps.runningModule == "run_financial_results" :
        #         self.bid = pd_series
        elif parameter_name == 'subscribed_volume':
            array = parameter_value.to_dict()
            values = [float(i[1]) for i in array["data"]]
            index = [int(i[0]) for i in array["data"]]
            pd_series = pd.Series(values, index=index)
            self.subscribed_volume = pd_series
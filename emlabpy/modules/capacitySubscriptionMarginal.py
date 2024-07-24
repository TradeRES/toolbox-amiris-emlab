from modules.marketmodule import MarketModule
from util.repository import Repository
import pandas as pd
from util import globalNames
import matplotlib.pyplot as plt
import os
import numpy as np
from os.path import dirname, realpath
class DemandCurve:
    """
    The SlopingDemandCurve as required in the CapacityMarket.
    """

    def __init__(self,  sorted_demand):
        self.sorted_demand = sorted_demand

    def get_demand_price_at_volume(self, supply_volume):
        demand_price = self.sorted_demand["bid"][0] # the demand price cao
        last_demand = False
        cummulative_quantity = 0
        for numero, demand in self.sorted_demand.iterrows():
            cummulative_quantity += demand.volume
            if numero == (len(self.sorted_demand) - 1):
                last_demand = True

            demand_price = demand.bid
            if cummulative_quantity >= supply_volume:
                break
        return demand_price, last_demand


class CapacitySubscriptionMarginal(MarketModule):
    """
    After a capacity market has been cleared, the accepted bids are cleared and the revenues are staged.
    """

    def __init__(self, reps: Repository):
        super().__init__('EM-Lab Capacity Subscription: Clear Market', reps)
        reps.dbrw.stage_init_capacitymechanisms_structure()
        self.agent = reps.energy_producers[reps.agent]

    def act(self):
        print("capacity subscription clearing")
        capacity_market = self.reps.get_capacity_market_in_country(self.reps.country, False)
        capacity_market_year = self.reps.current_year + capacity_market.forward_years_CM
        sorted_ppdp = self.reps.get_sorted_bids_by_market_and_time(capacity_market, self.reps.current_tick)
        clearing_price, total_supply_volume = self.capacity_subscription_clearing(sorted_ppdp, capacity_market)
        accepted_supply_bid = self.reps.get_accepted_CM_bids(self.reps.current_tick)
        print("--------------------accepted_supply_bid-------------------")
        plantsinCM = []
        for accepted in accepted_supply_bid:
            amount = accepted.accepted_amount * clearing_price
            self.reps.dbrw.stage_CM_revenues(accepted.plant, amount,
                                             [self.reps.current_tick + capacity_market.forward_years_CM])
            plantsinCM.append(accepted.plant)
        self.reps.create_or_update_market_clearing_point(capacity_market, clearing_price, total_supply_volume,
                                                         self.reps.current_tick + capacity_market.forward_years_CM)
        self.reps.dbrw.stage_plants_in_CM(plantsinCM, self.reps.current_tick + capacity_market.forward_years_CM)
        print("Cleared market", capacity_market.name, "at ", str(clearing_price))


    def capacity_subscription_clearing(self, sorted_supply, capacity_market):
        """
        reading ENS for the current year
        """
        # if self.reps.runningModule =="run_investment_module" and self.reps.investmentIteration > 0:
        #     bid_per_consumer_group = pd.read_csv("bid_per_consumer_group.csv")
        # else:
        bid_per_consumer_group = CapacitySubscriptionMarginal.preparing_demand_curve(self)
        bid_per_consumer_group["cummulative_quantity"] = bid_per_consumer_group["volume"].cumsum()
        # print(bid_per_consumer_group[["cummulative_quantity","bid"]])
        total_volume = 0
        # print("cummulativesupply;price")

        for i, supply in enumerate(sorted_supply):
            total_volume += supply.amount
            supply.cummulative_quantity = total_volume
            # print(str(total_volume) + ";" + str(supply.price))

        clearing_price = 0
        total_supply_volume = 0

        dc = DemandCurve(bid_per_consumer_group) # price cap is set as the WTP of the most expensive consumer
        cummulative_supply = 0
        supply_volumes = []
        supply_prices = []
        for num, supply_bid  in enumerate(sorted_supply):
            # As long as the market is not cleared
            cummulative_supply = supply_bid.amount + cummulative_supply
            supply_volumes.append(cummulative_supply)
            supply_prices.append(supply_bid.price)
            demand_price , isnotlast = dc.get_demand_price_at_volume(cummulative_supply)
            last_demand_price , is_last_demand = dc.get_demand_price_at_volume( supply_volumes[num-1])
            if supply_bid.price <= demand_price: # not crossed line, price set by demand
                total_supply_volume += supply_bid.amount
                clearing_price =  demand_price
                supply_bid.accepted_amount = supply_bid.amount
                supply_bid.status = globalNames.power_plant_dispatch_plan_status_accepted
                if is_last_demand == True and total_supply_volume > bid_per_consumer_group["cummulative_quantity"].iloc[-1]: # last demand, price set by supply
                    clearing_price = supply_bid.price
                    print("last demand and not crossed line, clearing price is last supply price")
                    break
            elif supply_bid.price < last_demand_price: # crossed line, price set by supply
                clearing_price = supply_bid.price
                total_supply_volume += supply_bid.amount
                supply_bid.accepted_amount = supply_bid.amount
                supply_bid.status = globalNames.power_plant_dispatch_plan_status_accepted
                break
            else: # crossed line from the beginning, clearing price is zero
                supply_bid.status = globalNames.power_plant_dispatch_plan_status_failed
                supply_bid.accepted_amount = 0
                break
        print("clearing_price", clearing_price)
        print("total_supply_volume",total_supply_volume )

        colorplot = 'g'
        if clearing_price <= self.reps.CS_minimum_price:
            clearing_price = self.reps.CS_minimum_price
            colorplot = 'k'

        # for i, row in bid_per_consumer_group.iterrows():
        #     cumsum+= row["volume"]
        #     if cumsum < total_supply_volume:
        #         bid_per_consumer_group.loc[i, 'accepted_volume'] = bid_per_consumer_group.loc[i, 'volume']
        #     else:
        #         bid_per_consumer_group.loc[i, 'accepted_volume'] = bid_per_consumer_group.loc[i, 'volume'] - (cumsum - total_supply_volume)
        """
        subscribed consumers are those who are willing to pay less than the clearing price
        """
        cumsum = 0
        for i, row in bid_per_consumer_group.iterrows():
            cumsum+=  row.volume
            if row.bid > clearing_price:
                bid_per_consumer_group.loc[i, 'accepted_volume'] = row.volume
            elif row.bid == clearing_price and cumsum < total_supply_volume:
                bid_per_consumer_group.loc[i, 'accepted_volume'] = row.volume
            elif row.bid == clearing_price and cumsum >= total_supply_volume:
                bid_per_consumer_group.loc[i, 'accepted_volume'] = row.volume - (cumsum - total_supply_volume)
                break
            else:
                bid_per_consumer_group.loc[i, 'accepted_volume'] = 0

        bid_per_consumer_group['accepted_volume'] = bid_per_consumer_group['accepted_volume'].apply(lambda x: 0 if x < 0 else x)
        grouped_accepted_bids = bid_per_consumer_group.groupby('consumer_name').agg({'accepted_volume': 'sum'}).reset_index()

        for i, consumer in grouped_accepted_bids.iterrows():
            self.reps.dbrw.stage_subscribed_volume_yearly(consumer.consumer_name, consumer.accepted_volume,  self.reps.current_tick + capacity_market.forward_years_CM)

        total = 0
        for i, supply in enumerate(sorted_supply):
            total += supply.amount
            supply.cummulative_quantity = total

        supply_prices = []
        supply_quantities = []
        cummulative_quantity = 0
        if self.reps.runningModule =="run_CRM":
            for bid in sorted_supply:
                supply_prices.append(bid.price)
                cummulative_quantity += bid.amount
                supply_quantities.append(cummulative_quantity)
            plt.step(supply_quantities, supply_prices, 'o-', label='supply', color='b')
            plt.step(bid_per_consumer_group["cummulative_quantity"].to_list(), bid_per_consumer_group["bid"].to_list(), 'o-', label='demand', color='r')
            plt.grid(visible=None, which='major', axis='both', linestyle='--')
            plt.axhline(y=clearing_price, color=colorplot, linestyle='--', label='P ' + str(clearing_price))
            plt.axvline(x=total_supply_volume, color='g', linestyle='--', label='Q ' + str(total_supply_volume))
            plt.title(self.reps.runningModule + " " + str(self.reps.current_year))
            plt.xlabel('Quantity')
            plt.ylabel('Price')
            # plt.show()
            # plt.ylim(0, 4000)
            path  = os.path.join(dirname(realpath(os.getcwd())), 'temporal_results')
            plt.savefig(os.path.join( path , str(self.reps.current_year)+ '.png') ,bbox_inches='tight', dpi=300)

        return clearing_price, total_supply_volume

    def preparing_demand_curve(self):
        year_excel = os.path.join(os.path.dirname(os.getcwd()), 'amiris_workflow','output',  (str(self.reps.current_year) + ".xlsx"))
        input_weather_years_excel =  os.path.join(os.path.dirname(os.getcwd()), 'data', self.reps.scenarioWeatheryearsExcel)
        df = pd.read_excel(year_excel, sheet_name=["hourly_generation"])
        hourly_load_shedders = pd.DataFrame()
        for unit in df['hourly_generation'].columns.values:
            if unit[0:4] == "unit" and unit[5:] != str(8888888): # the 8888888 unit corresponed to the electrolyzer
                hourly_load_shedders[int(int(unit[5:])/100000)] = df['hourly_generation'][unit]
        # ---------------------------------ENS calculation per consumer group  -----------------------------------
        realized_ENS_consumers = hourly_load_shedders[[1]].sum(axis=1) # these is the load disptached at 4000
        demand_all = pd.read_excel(input_weather_years_excel, index_col=0, sheet_name=["Load"])
        orginal_load = self.reps.weatherYears["weatherYears"].sequence[self.reps.current_tick]
        demand = demand_all["Load"][orginal_load].reset_index(drop=True)

        consumer_possible_ENS = pd.DataFrame()
        for consumer in self.reps.get_CS_consumer_descending_WTP():
            subscription_per_consumer = consumer.subscribed_volume[self.reps.current_tick] # MW
            demand_per_consumer_group = demand* consumer.max_subscribed_percentage #
            possibleENS = (demand_per_consumer_group- subscription_per_consumer)
            possibleENS = possibleENS.apply(lambda x: 0 if x < 0 else x)
            consumer_possible_ENS[consumer.name] = possibleENS # ignore negative values
            # print(consumer.name)
            # print(subscription_per_consumer)

        total_potential_ENS = consumer_possible_ENS.sum(axis=1)
        probability_curtailment = pd.DataFrame()
        for consumer in self.reps.get_CS_consumer_descending_WTP():
            probability_curtailment[consumer.name] = consumer_possible_ENS[consumer.name] / total_potential_ENS

        ENS_proportion = pd.DataFrame()
        for consumer in self.reps.get_CS_consumer_descending_WTP():
            ENS_proportion[consumer.name] = realized_ENS_consumers*probability_curtailment[consumer.name]
        # probability_curtailment.plot()
        # plt.show()
        # --------------------------------- marginal bids  -----------------------------------
        marginal_value_per_consumer_group = pd.DataFrame()
        subscribed_consumers = dict()
        def calculate_marginal_value_per_consumer_group(hourly_shedded, WTP, consumer_name):
            df = pd.DataFrame()
            ENS_one_MW = 0
            for column, value in hourly_shedded[hourly_shedded>0].iteritems():
                # Determine the number of rows based on the value in the first row
                if value >= 1:
                    ENS_one_MW += 1
                quotient = value // self.reps.consumer_marginal_volume
                remainder = value % self.reps.consumer_marginal_volume
                column_data = [self.reps.consumer_marginal_volume] * int(quotient) + [remainder]
                df =  pd.concat([df, pd.Series(column_data)], ignore_index=True, axis=1)
            one_MW = ENS_one_MW*WTP
            prices = df.sum(axis=1)*WTP/ self.reps.consumer_marginal_volume
            marginal_value_per_consumer_group[consumer_name] = prices
            subscribed_consumers[consumer_name] = one_MW
        # do for the first MW

        calculate_marginal_value_per_consumer_group(hourly_load_shedders[2], self.reps.loadShedders['2'].VOLL, "DSR")
        for consumer_name, data in ENS_proportion.iteritems():
            calculate_marginal_value_per_consumer_group(data, self.reps.cs_consumers[consumer_name].WTP, consumer_name )

        bid_per_consumer_group = pd.melt(marginal_value_per_consumer_group.T, ignore_index=False)
        bid_per_consumer_group.reset_index(inplace=True)
        bid_per_consumer_group.dropna(inplace=True)
        bid_per_consumer_group.drop(columns=["variable"], inplace=True)
        bid_per_consumer_group.rename(columns={"value": "bid","index": "consumer_name" }, inplace=True)
        bid_per_consumer_group['volume'] = self.reps.consumer_marginal_volume # new MW

        # largestbid = bid_per_consumer_group["bid"].max()
        capacity_market = self.reps.get_capacity_market_in_country(self.reps.country, False)
        if self.reps.current_tick <= self.reps.CS_look_back_years:
            ticks = range(capacity_market.forward_years_CM, self.reps.current_tick + capacity_market.forward_years_CM)
        else:
            ticks = range(self.reps.current_tick + capacity_market.forward_years_CM - self.reps.CS_look_back_years, self.reps.current_tick+ capacity_market.forward_years_CM)

        # lastCM = []
        # for tick in ticks:
        #     lastCM.append(self.reps.get_market_clearing_point_price_for_market_and_time(capacity_market.name,
        #                                                                                 tick + capacity_market.forward_years_CM))
        # average_CS = np.mean(lastCM)

        """
        adding the marginal value (1 MW of more capacity) per consumer to subscribed consumers, that conserve volume
        """
        for i, consumer in enumerate(self.reps.get_CS_consumer_descending_WTP()):
            bid = subscribed_consumers[consumer.name]
            if bid <= self.reps.CS_minimum_price:
                bid = self.reps.CS_minimum_price
            new_row = {"consumer_name":consumer.name, 'volume': consumer.subscribed_volume[self.reps.current_tick], "bid":bid }
            bid_per_consumer_group = bid_per_consumer_group.append(new_row, ignore_index=True)
        bid_per_consumer_group.sort_values("bid", inplace=True, ascending=False)
        path  = os.path.join(dirname(realpath(os.getcwd())), 'temporal_results', (str(self.reps.current_tick+ capacity_market.forward_years_CM) +"bid_per_consumer_group.csv"))
        bid_per_consumer_group.to_csv(path)

        if self.reps.CS_look_back_years > 0:
            bid_per_consumer_group = self.mean_demand_values(ticks, bid_per_consumer_group, self.reps.current_tick + capacity_market.forward_years_CM)
            bid_per_consumer_group.sort_values("bid", inplace=True, ascending=False)
        else:
            pass
        return bid_per_consumer_group

    def mean_demand_values(self, ticks, bid_per_consumer_group, CS_tick):
        past_consumer_bids = dict()
        for tick in ticks:
            path  = os.path.join(dirname(realpath(os.getcwd())), 'temporal_results', str(tick) +"bid_per_consumer_group.csv")
            if os.path.exists(path):
                past_consumer_bids[tick] = pd.read_csv(path )
            else:
                raise Exception("File not found")
        interpolated_bids = pd.DataFrame()
        consumers_names = self.reps.get_CS_consumer_names()

        for consumer in consumers_names:
            bids= pd.DataFrame()
            volumes= pd.DataFrame()
            y1_interp = pd.DataFrame()

            current_year_df  = bid_per_consumer_group[bid_per_consumer_group["consumer_name"] == consumer]
            current_year_df.sort_values(by="bid", inplace=True, ascending=False)
            current_year_df['cumulative_vol'] = current_year_df['volume'].cumsum()
            bids[CS_tick] = current_year_df["bid"].reset_index(drop=True)
            volumes[CS_tick] = current_year_df["cumulative_vol"].reset_index(drop=True)

            for tick in ticks:
                df_year = past_consumer_bids[tick]
                df = df_year[df_year["consumer_name"] == consumer]
                df.sort_values(by="bid", inplace=True, ascending=False)
                df['cumulative_vol'] = df['volume'].cumsum()
                df["bid"].reset_index(drop=True, inplace=True)
                df["cumulative_vol"].reset_index(drop=True, inplace=True)
                bids = pd.concat([bids,df["bid"]],axis=1)
                bids = bids.rename(columns={'bid': tick})
                volumes =pd.concat([volumes,df["cumulative_vol"]],axis=1)
                volumes = volumes.rename(columns={'cumulative_vol': tick})

            bids.fillna(0, inplace=True)
            volumes.fillna(0, inplace=True)
            unique_volume = pd.Series(volumes.values.flatten()).drop_duplicates()
            unique_volume_sorted = unique_volume.sort_values(ascending=True)
            unique_volume_sorted.reset_index(drop=True, inplace=True)
            # print("next consumer " + consumer)
            # print(bids)
            # print(volumes)
            for tick in volumes.columns.values:
                if  len(unique_volume_sorted) ==0:
                    new_rows = {'consumer_name': [consumer], 'bid': 0, "volume":0}
                else:
                    y1_interp[tick] = np.interp(unique_volume_sorted.values, volumes[tick]  ,  bids[tick], right=0)
                    # plt.step(unique_volume_sorted.values, y1_interp[tick], where='post',  label=tick)
            volume = np.diff(unique_volume_sorted, prepend=0)
            new_rows = {'consumer_name': [consumer]*len(unique_volume_sorted), 'bid': y1_interp.mean(axis=1), "volume":volume}
            new_df = pd.DataFrame(new_rows)
            interpolated_bids = interpolated_bids.append(new_df, ignore_index=True)
            # plt.step(unique_volume_sorted.values, y1_interp.mean(axis=1), where='post', linestyle='--', label='Average Line')
            # plt.title(consumer)
            # plt.legend()
            # plt.show()
        return interpolated_bids




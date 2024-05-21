import matplotlib.pyplot as plt

"""
testing capacity subsciption market
"""


def plot_CS_market(sorted_supply, sorted_demand, equilibrium_price, equilibrium_quantity ):
    total = 0
    for i, supply in enumerate(sorted_supply):
        total += supply.amount
        supply.cummulative_quantity = total

    print(f"Equilibrium Price: {equilibrium_price}, Equilibrium Quantity: {equilibrium_quantity}")
    supply_prices = []
    supply_quantities = []
    demand_prices = []
    demand_quantities = []

    cummulative_quantity = 0

    for bid in sorted_supply:
        supply_prices.append(bid.price)
        cummulative_quantity += bid.amount
        supply_quantities.append(cummulative_quantity)

    for bid in sorted_demand:
        demand_prices.append(bid.price)
        demand_quantities.append(bid.cummulative_quantity)

    plt.step(supply_quantities, supply_prices, 'o-', label='supply', color='b')
    plt.step(demand_quantities, demand_prices, 'o-', label='demand', color='r')
    plt.grid(visible=None, which='major', axis='both', linestyle='--')
    plt.axhline(y=equilibrium_price, color='g', linestyle='--', label='Equilibrium Price')
    plt.axvline(x=equilibrium_quantity, color='g', linestyle='--', label='Equilibrium Quantity')
    plt.xlabel('Quantity')
    plt.ylabel('Price')
  #  plt.ylim(40000, 50000)
    plt.legend()
    plt.show()


class Market:
    def __init__(self, price_cap, sorted_demand):
        self.price_cap = price_cap
        self.sorted_demand = sorted_demand

    def get_demand_price_at_volume_test(self, supply):
        demand_price = self.price_cap
        last_demand = False
        for numero, demand in enumerate(self.sorted_demand):
            if numero == (len(self.sorted_demand) - 1):
                last_demand = True

            demand_price = demand.price
            if demand.cummulative_quantity >= supply.cummulative_quantity:
                print("Q"+ str(demand.cummulative_quantity) )
                break
        return demand_price, last_demand


class Bid:
    def __init__(self, price, amount):
        self.price = price
        self.amount = amount
        self.cummulative_quantity = amount


def clear_market(sorted_supply, sorted_demand):
    clearing_price = 0

    market = Market(60000, sorted_demand)
    total_supply_volume = 0
    supply_volumes = []
    equilibriumprices = []
    for numero, supply  in enumerate(sorted_supply):
        # As long as the market is not cleared
        print("--------------------------------------------------------------------")
        print("suuply_price " + str(supply.price) + "      supply volume" + str(supply.cummulative_quantity) )

        demand_price ,  is_last_demand = market.get_demand_price_at_volume_test(supply)
        last_demand_price ,  is_not = market.get_demand_price_at_volume_test(sorted_supply[numero - 1])
        if supply.price <= demand_price:
            print("not crossed the line")
            total_supply_volume += supply.amount
            clearing_price = demand_price

            equilibriumprices.append(clearing_price)
            if is_last_demand == True:
                clearing_price = supply.price
                print("last demand and not crossed line, clearing price is last supply price")
                break

        elif supply.price < last_demand_price:
            print("crossed line," + str(demand_price) )
            clearing_price = supply.price
            equilibriumprices.append(clearing_price)
            total_supply_volume = total_supply_volume + supply.amount
            break
        else: # supply price is higher than last demand price
            print("supply price is higher than last demand price  ")
            equilibriumprices.append(clearing_price)
            break

    print("equilibrium_price: ", str(clearing_price))
    print("total_supply_volume", str(total_supply_volume))
    return clearing_price, total_supply_volume


def example():
    # Example usage
    supply = [
        Bid(price=5000, amount=3000),
        Bid(price=8000, amount=3000),
        Bid(price=10000, amount=2000),
        Bid(price=27000, amount=2000),
        Bid(price=23000, amount=2000),
        Bid(price=24000, amount=1000)
    ]

    # demand = [
    #     Bid(price=51000, amount=5000),
    #     Bid(price=46000, amount=5100),
    #     Bid(price=36000, amount=4100),
    #     Bid(price=26000, amount=2000),
    #     Bid(price=22000, amount=2000),
    #     Bid(price=18000, amount=2000),
    #     Bid(price=17000, amount=2100),
    # ]


    demand = [
        Bid(price=0, amount=5000),
        Bid(price=0, amount=5100),
        Bid(price=0, amount=4100),

    ]

    sorted_supply = sorted(supply, key=lambda x: x.price, reverse=False)
    sorted_demand = sorted(demand, key=lambda x: x.price, reverse=True)

    total = 0
    for i, supply in enumerate(sorted_supply):
        total += supply.amount
        supply.cummulative_quantity = total
    total = 0
    for i, demand in enumerate(sorted_demand):
        total += demand.amount
        demand.cummulative_quantity = total

    equilibrium_price, equilibrium_quantity = clear_market(sorted_supply, sorted_demand)
    plot_CS_market(sorted_supply, sorted_demand, equilibrium_price, equilibrium_quantity)


example()

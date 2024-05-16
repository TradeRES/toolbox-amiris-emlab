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
        for numero, demand in enumerate(self.sorted_demand):
            last_capacity = supply.cummulative_quantity - supply.amount
            last_demand_price = self.sorted_demand[numero - 1].price
            print("price " + str(demand.price) +" q " + str(demand.cummulative_quantity) )
            demand_volume = demand.cummulative_quantity
            demand_price = demand.price
            # if  demand.price < supply.price and demand.cummulative_quantity >= last_capacity:
            if demand.cummulative_quantity >= supply.cummulative_quantity:
                break

            if demand.price < supply.price:
                print("***")
                break
        return demand_price, demand_volume, last_demand_price


class Bid:
    def __init__(self, price, amount):
        self.price = price
        self.amount = amount
        self.cummulative_quantity = amount


def clear_market(sorted_supply, sorted_demand):
    clearing_price = None

    market = Market(60000, sorted_demand)
    total_supply_volume = 0

    for numero, supply  in enumerate(sorted_supply):

        # As long as the market is not cleared
        print("--------------------------------------------------------------------")
        print("suuply_price " + str(supply.price) + "      supply volume" + str(supply.cummulative_quantity) )
        demand_price , demand_volume, last_demand_price = market.get_demand_price_at_volume_test(supply)
        print("demand price ************" + str(demand_price) + " demandvolume " + str(demand_volume))
        clearing_price = demand_price
        last_supply_price = sorted_supply[numero - 1].price
        last_supply_volume = sorted_supply[numero - 1].cummulative_quantity
        if supply.cummulative_quantity > demand_volume:
            print("supply volume > demand volume")
            print("cummulative_supply", supply.cummulative_quantity,  "> demand_at_price", demand_volume)
            total_supply_volume = last_supply_volume
            clearing_price = last_supply_price


            break

        if supply.price <= demand_price:
            total_supply_volume += supply.amount

        elif supply.price > demand_price:
            print("supply price > demand price")
            total_supply_volume = last_supply_volume
            clearing_price = last_supply_price
            break

    print("equilibrium_price: ", str(clearing_price))
    print("total_supply_volume", str(total_supply_volume))
    return clearing_price, total_supply_volume


def example():
    # Example usage
    supply = [
        Bid(price=5000, amount=3000),
        Bid(price=8000, amount=6000),
        Bid(price=10000, amount=3000),
        Bid(price=20000, amount=3000),
        Bid(price=22000, amount=500),
        Bid(price=23000, amount=3000),
        Bid(price=25000, amount=3000)
    ]

    demand = [
        Bid(price=51000, amount=1000),
        Bid(price=46000, amount=5100),
        Bid(price=36000, amount=4100),
        Bid(price=26000, amount=2000),
        Bid(price=22000, amount=2000),
        Bid(price=18000, amount=2000),
        Bid(price=17000, amount=2100),
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

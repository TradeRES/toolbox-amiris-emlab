import matplotlib.pyplot as plt
"""
testing capacity subsciption market
"""

def plot_CS_market(sorted_supply, sorted_demand, equilibrium_price, equilibrium_quantity):
    total = 0
    for i , supply in enumerate(sorted_supply):
        total += supply.amount
        supply.cummulative_quantity = total
    total = 0

    print(f"Equilibrium Price: {equilibrium_price}, Equilibrium Quantity: {equilibrium_quantity}")
    supply_prices = []
    supply_quantities = []
    demand_prices = []
    demand_quantities = []

    cummulative_quantity=0

    for bid in sorted_supply:
        supply_prices.append(bid.price)
        cummulative_quantity += bid.amount
        supply_quantities.append(cummulative_quantity)

    for bid in sorted_demand:
        demand_prices.append(bid.price)
        demand_quantities.append(bid.cummulative_quantity)

    plt.step(supply_quantities, supply_prices, 'o-', label='supply', color='b')
    plt.step(demand_quantities, demand_prices, 'o-', label='demand',color='r')
    plt.grid(visible=None, which='major', axis='both', linestyle='--')
    plt.axhline(y=equilibrium_price, color='g', linestyle='--', label='Equilibrium Price')
    plt.xlabel('Quantity')
    plt.ylabel('Price')
    plt.legend()
    plt.show()



class Market:
    def __init__(self, price_cap, sorted_demand ):
        self.price_cap = price_cap
        self.sorted_demand = sorted_demand

    def get_demand_price_at_volume_test(self, supply):
        price = self.price_cap
        for numero, demand in enumerate(self.sorted_demand):
            last_capacity = supply.cummulative_quantity - supply.amount
            print("deamand " + str(demand.cummulative_quantity) + "_" +  str(demand.price))
            if demand.cummulative_quantity >= supply.cummulative_quantity or \
                    demand.price < supply.price and demand.cummulative_quantity >= last_capacity:
                print("demand_q" + str(demand.cummulative_quantity))
                price = demand.price
                break
            # else:
            #     if demand.price < supply.price and demand.cummulative_quantity >= last_capacity:
            #         print("price" + str(demand.price) )
            #         price = demand.price
            #         break
                #if there is no demand, take the last price
             #   price = demand.price
        return price

class Bid:
    def __init__(self, price, amount):
        self.price = price
        self.amount = amount
        self.cummulative_quantity = amount


def clear_market(sorted_supply, sorted_demand):
    equilibrium_price = None
    equilibrium_quantity = 0
    market = Market(60000, sorted_demand)
    total_supply_volume = 0

    for supply in sorted_supply:
        # As long as the market is not cleared
        print("supply -----------" + str(supply.cummulative_quantity) + "_" + str(supply.price))
        demand_price = market.get_demand_price_at_volume_test(supply)
        print( "demand price ************" +str(demand_price))
        if supply.price < demand_price:
            total_supply_volume += supply.amount
            equilibrium_price = demand_price
        else:
            equilibrium_price = demand_price
            total_supply_volume += supply.amount
            print("last price: ", str(demand_price))
            break
    return equilibrium_price, equilibrium_quantity

def example():
# Example usage
    supply = [
        Bid(price=5000, amount=5000),
        Bid(price=5000, amount=6000),
        Bid(price=6000, amount=3000),
        Bid(price=10000, amount=5000),
  #      Bid(price=30000, amount=10000),
  #      Bid(price=60000, amount=10000)

    ]

    demand = [
        Bid(price=49000, amount=5000),
        Bid(price=45000, amount=5000),
        Bid(price=35000, amount=4000),
        Bid(price=30000, amount=4000),
        Bid(price=25000, amount=6000),
        Bid(price=20000, amount=5050),

    ]

    sorted_supply = sorted(supply, key=lambda x: x.price, reverse=False)
    sorted_demand = sorted(demand, key=lambda x: x.price, reverse=True)

    total = 0
    for i , supply in enumerate(sorted_supply):
        total += supply.amount
        supply.cummulative_quantity = total
    total = 0
    for i , demand in enumerate(sorted_demand):
        total += demand.amount
        demand.cummulative_quantity = total

    equilibrium_price, equilibrium_quantity = clear_market(sorted_supply, sorted_demand)
    plot_CS_market(sorted_supply, sorted_demand, equilibrium_price, equilibrium_quantity)

example()
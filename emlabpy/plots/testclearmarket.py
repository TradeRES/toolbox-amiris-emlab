import matplotlib.pyplot as plt
"""
testing capacity subsciption market
"""
class Market:
    def __init__(self, price_cap, sorted_demand ):
        self.price_cap = price_cap
        self.sorted_demand = sorted_demand

    def cleared_market(self, volume):
        price = self.price_cap
        for demand in self.sorted_demand:
            print("lastdemand " + str(demand.cummulative_quantity))
            if volume  >= demand.cummulative_quantity:
                price = demand.price
                print("demand price " + str(price))
            else:
                break
        return price

class Bid:
    def __init__(self, price, quantity):
        self.price = price
        self.quantity = quantity
        self.cummulative_quantity = quantity

def clear_market(sorted_supply, sorted_demand):
    equilibrium_price = None
    equilibrium_quantity = 0
    market = Market(1000, sorted_demand)
    total_supply_volume = 0

    for ppdp in sorted_supply:
        # As long as the market is not cleared
        print("supply quantity -----------" + str(ppdp.cummulative_quantity))
        if ppdp.price <= market.cleared_market(ppdp.cummulative_quantity):
            total_supply_volume += ppdp.quantity
            equilibrium_price = ppdp.price
            print("equilibrium_price: ", ppdp.price)
        else:
            break
    return equilibrium_price, equilibrium_quantity

# Example usage
supply = [
    Bid(price=1, quantity=4),
    Bid(price=2, quantity=4),
    Bid(price=3, quantity=4),
    Bid(price=7, quantity=4),
    Bid(price=15.4, quantity=4),
    Bid(price=6.5, quantity=4)
]

demand = [
    Bid(price=10, quantity=5),
    Bid(price=8, quantity=7),
    Bid(price=6, quantity=3),
    Bid(price=5, quantity=8)
]

sorted_supply = sorted(supply, key=lambda x: x.price, reverse=False)
sorted_demand = sorted(demand, key=lambda x: x.price, reverse=True)

total = 0
for i , supply in enumerate(sorted_supply):
    total += supply.quantity
    supply.cummulative_quantity = total
total = 0
for i , demand in enumerate(sorted_demand):
    total += demand.quantity
    demand.cummulative_quantity = total

equilibrium_price, equilibrium_quantity = clear_market(sorted_supply, sorted_demand)

print(f"Equilibrium Price: {equilibrium_price}, Equilibrium Quantity: {equilibrium_quantity}")
supply_prices = []
supply_quantities = []
demand_prices = []
demand_quantities = []
total_quantity_supplied=0
total_quantity_demanded = 0
for bid in sorted_supply:
    supply_prices.append(bid.price)
    supply_quantities.append(bid.cummulative_quantity)

for bid in sorted_demand:
    demand_prices.append(bid.price)
    demand_quantities.append(bid.cummulative_quantity)

plt.step(supply_quantities, supply_prices, 'o-', label='supply', color='b')
plt.step(demand_quantities, demand_prices, 'o-', label='demand',color='r')

plt.axhline(y=equilibrium_price, color='g', linestyle='--', label='Equilibrium Price')
plt.xlabel('Quantity')
plt.ylabel('Price')
plt.legend()
plt.show()
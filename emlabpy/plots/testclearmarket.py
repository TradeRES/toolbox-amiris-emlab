import matplotlib.pyplot as plt
"""
testing capacity subsciption market
"""
class Market:
    def __init__(self, price_cap, sorted_demand ):
        self.price_cap = price_cap
        self.sorted_demand = sorted_demand

    def get_demand_price_at_volume(self, supply):
        price = self.price_cap
        for demand in self.sorted_demand:
            price = demand.price
            print(price)
            if demand.cummulative_quantity >= supply.cummulative_quantity:
                print("cummulative_quantity")
                print(demand.cummulative_quantity)
                break
            if demand.price <= supply.price:
                print("demand price")
                print(demand.price)
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
    market = Market(60000, sorted_demand)
    total_supply_volume = 0

    for supply in sorted_supply:
        # As long as the market is not cleared
        print("supply quantity -----------" + str(supply.cummulative_quantity))
        price_at_volume = market.get_demand_price_at_volume(supply)
        print( "price at volume -----------" +str(price_at_volume))
        if supply.price <= price_at_volume:
            total_supply_volume += supply.quantity
            equilibrium_price = price_at_volume
        else:
            equilibrium_price = supply.price
            print("last price: ", str(price_at_volume))
            break
    return equilibrium_price, equilibrium_quantity

# Example usage
supply = [
    Bid(price=0, quantity=0),
    Bid(price=5000, quantity=18000),
    Bid(price=6000, quantity=17000),
    Bid(price=25000, quantity=18000),
 #   Bid(price=32000, quantity=10000),
 #   Bid(price=46000, quantity=20000)

]

demand = [
    Bid(price=50000, quantity=1305),
    Bid(price=39000, quantity=26000),
    Bid(price=35000, quantity=10000),
    Bid(price=30000, quantity=4000),
    Bid(price=27000, quantity=6000),
    Bid(price=20000, quantity=4000)
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
plt.grid(visible=None, which='major', axis='both', linestyle='--')
plt.axhline(y=equilibrium_price, color='g', linestyle='--', label='Equilibrium Price')
plt.xlabel('Quantity')
plt.ylabel('Price')
plt.legend()
plt.show()
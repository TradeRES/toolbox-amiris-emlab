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
        for numero, demand in enumerate(self.sorted_demand):
            last_capacity = supply.cummulative_quantity - supply.quantity
            print("deamand " + str(demand.cummulative_quantity) + "_" +  str(demand.price))
            if demand.cummulative_quantity >= supply.cummulative_quantity:
                print("demand_q" + str(demand.cummulative_quantity))
                price = demand.price
                break
            else:
                if demand.price < supply.price and demand.cummulative_quantity >= last_capacity:
                    print("price" + str(demand.price) )
                    price = demand.price
                    break
                #if there is no demand, take the last price
                price = demand.price
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
        print("supply -----------" + str(supply.cummulative_quantity) + "_" + str(supply.price))
        demand_price = market.get_demand_price_at_volume(supply)
        print( "demand price ************" +str(demand_price))
        if supply.price < demand_price:
            total_supply_volume += supply.quantity
        else:
            equilibrium_price = demand_price
            total_supply_volume += supply.quantity
            print("last price: ", str(demand_price))
            break
    return equilibrium_price, equilibrium_quantity

# Example usage
supply = [
    Bid(price=5000, quantity=5000),
    Bid(price=5000, quantity=6000),
    Bid(price=6000, quantity=3000),
    Bid(price=10000, quantity=5000),
    Bid(price=30000, quantity=10000),
    Bid(price=60000, quantity=10000)

]

demand = [
    Bid(price=49000, quantity=5000),
    Bid(price=45000, quantity=5000),
    Bid(price=35000, quantity=4000),
    Bid(price=30000, quantity=4000),
    Bid(price=25000, quantity=6000),
    Bid(price=20000, quantity=5050),



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
import numpy as np
import matplotlib.pyplot as plt


class Bid:
    def __init__(self, price, amount):
        self.price = price
        self.amount = amount
        self.cummulative_quantity = amount

demand = [
    Bid(price=39000, amount=6000),
    Bid(price=38000, amount=7000),
    Bid(price=35000, amount=5000),
    Bid(price=34000, amount=5000),
    # Bid(price=33000, amount=5000),
    # Bid(price=32000, amount=5000),
    # Bid(price=40000, amount=5000),
]

x_values = []
y_values = []
sorted_demand = sorted(demand, key=lambda x: x.price, reverse=True)
total = 0
for i, demand in enumerate(sorted_demand):
    total += demand.amount
    demand.cummulative_quantity = total
    y_values.append(demand.price)
    x_values.append(total)
# Define a function to return the y value from a segmented line given an x value
def get_demand_price( x):
    # Find the index of the nearest x value to the left of the given x
    left_index = np.searchsorted(x_values, x, side='right') - 1
    # If x is smaller than the smallest x value, return the corresponding y value
    if left_index == -1:
        return y_values[0], False
    # If x is larger than the largest x value, return the corresponding y value
    if left_index == len(x_values) - 1:
        return y_values[-1], True
    # Interpolate between the nearest x values
    x_left, x_right = x_values[left_index], x_values[left_index + 1]
    y_left, y_right = y_values[left_index], y_values[left_index + 1]
    slope = (y_right - y_left) / (x_right - x_left)
    return y_left + slope * (x - x_left), False




def linearmarket():
    supply = [
        Bid(price=5000, amount=5000),
        Bid(price=10000, amount=6000),
        Bid(price=15000, amount=5000),
        Bid(price=23000, amount=3000),
        Bid(price=25000, amount=15000),
     #   Bid(price=39000, amount=5000)
    ]

    sorted_supply = sorted(supply, key=lambda x: x.price, reverse=False)
    total = 0
    for i, supply in enumerate(sorted_supply):
        total += supply.amount
        supply.cummulative_quantity = total


    total_supply_volume = 0
    clearing_price = 0

    equilibriumprices = []

    # Example usage
    price_cap = sorted_demand[0].price
    notacceptedy = 0
    notacceptedx = 0
    for num, supply in enumerate(sorted_supply):
        # As long as the market is not cleared
        print("--------------------------------------------------------------------")
        print("suuply_price " + str(supply.price) + "      supply volume" + str(supply.cummulative_quantity) )
        demand_price , is_last_demand = get_demand_price( supply.cummulative_quantity)
        last_demand_price , isnotlast = get_demand_price(sorted_supply[num -1].cummulative_quantity) # last accepted volume

        if supply.price <= demand_price:
            print("not crossed the line")
            total_supply_volume += supply.amount
            clearing_price = demand_price
            print(clearing_price)
            equilibriumprices.append(clearing_price)
            if is_last_demand == True:
                clearing_price = supply.price
          #      total_supply_volume += supply.amount
                print("last demand and not crossed line, clearing price is last supply price")
                break

        elif supply.price < last_demand_price:
            print("crossed line," + str(demand_price) )
            notacceptedy = demand_price
            notacceptedx = supply.cummulative_quantity
            clearing_price = supply.price
            equilibriumprices.append(clearing_price)
            total_supply_volume = total_supply_volume + supply.amount
            break
        else:
            print("crossed  line ")
            equilibriumprices.append(clearing_price)
            break

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

    plot_CS_linear( supply_quantities, supply_prices, demand_quantities, demand_prices, clearing_price, total_supply_volume, equilibriumprices )



    # print(f"Equilibrium Price: {clearing_price}, Equilibrium Quantity: {total_supply_volume}")
def plot_CS_linear( supply_quantities, supply_prices, demand_quantities, demand_prices, clearing_price, total_supply_volume , equilibriumprices):
    cummulative_quantity = 0
 #   plt.scatter(notacceptedx, notacceptedy, color = "y")
    plt.step(supply_quantities, supply_prices, 'o-', label='supply', color='b')
    plt.step(demand_quantities, demand_prices, 'o-', label='demand', color='r')
    plt.grid(visible=None, which='major', axis='both', linestyle='--')
    plt.scatter(supply_quantities[:len(equilibriumprices)], equilibriumprices, color='g', label='Equilibrium Prices')
    plt.axhline(y=clearing_price, color='g', linestyle='--', label='Equilibrium Price')
    plt.axvline(x=total_supply_volume, color='g', linestyle='--', label='Equilibrium Quantity')
    plt.xlabel('Quantity')
    plt.ylabel('Price')
    #  plt.ylim(40000, 50000)
    plt.legend()
    plt.show()


linearmarket()

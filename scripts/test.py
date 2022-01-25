import math

def roundup(x):
    return (round(x/100.0) * 100)

original = 10189
test = roundup(original)

print(test)
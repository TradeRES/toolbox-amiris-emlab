import math
import numpy as np


X = []
Y = []
def addData(x, y):
    logy = [math.log(y2)for y2 in y]
    X = np.array(x).reshape(-1, 1)
    Y = np.array(logy).reshape(-1, 1)
    print(X)
    print(Y)
l =  [['0', 69], ['1', 70], ['2', 71]]

x = []
y = []
for i in l:
    x.append(int(i[0]))
    y.append(i[1])
addData(x,y)
import matplotlib.pyplot as plt
import numpy as np
from sklearn import linear_model

regr2 = linear_model.LinearRegression()
y = np.array([0, 1, 2])

Y = y.reshape(-1,1)
X = np.array([0, 1, 2]).reshape(-1,1)

regr2.fit(X, Y)
print(X)
print(Y)
print(regr2.coef_)

# Plot outputs
#plt.plt(diabetes_X_test, diabetes_y_test, color="black")
plt.scatter(X,Y, color="blue", linewidth=3)
plt.show()


def estimate_coef(x, y):
    # number of observations/points
    n = np.size(x)

    # mean of x and y vector
    m_x = np.mean(x)
    m_y = np.mean(y)

    # calculating cross-deviation and deviation about x
    SS_xy = np.sum(y*x) - n*m_y*m_x
    SS_xx = np.sum(x*x) - n*m_x*m_x

    # calculating regression coefficients
    b_1 = SS_xy / SS_xx
    b_0 = m_y - b_1*m_x

    return (b_0, b_1)

def plot_regression_line(x, y, b):
    # plotting the actual points as scatter plot
    plt.scatter(x, y, color = "m",
                marker = "o", s = 30)

    # predicted response vector
    y_pred = b[0] + b[1]*x

    # plotting the regression line
    plt.plot(x, y_pred, color = "g")

    # putting labels
    plt.xlabel('x')
    plt.ylabel('y')

    # function to show plot
    plt.show()

def main():
    # observations / data
    x = np.array([0, 1, 2, 3])
    y = np.array([1, 3, 2, 5])

    # estimating coefficients
    b = estimate_coef(x, y)
    print("Estimated coefficients:\nb_0 = {}  \
          \nb_1 = {}".format(b[0], b[1]))

    # plotting regression line
    plot_regression_line(x, y, b)

if __name__ == "__main__":
    main()
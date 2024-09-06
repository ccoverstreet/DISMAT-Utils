import numpy as np
import matplotlib.pyplot as plt
from scipy.odr import Model, RealData, ODR
from scipy.optimize import curve_fit

x = np.linspace(0, 10, 100)
y = x + np.random.rand(np.size(x)) - 0.5

x_err = np.random.rand(np.size(x)) * 0.4
y_err = np.random.rand(np.size(x)) * 0.4

def linear(params, x):
    return params[0] + params[1] * x

# General flow:
# 1. Make Model from your selected function
# 2. Make RealData using your uncertainties
# 3. Run ODR on the Model and provide some starting values
# 4. Print fit output and use refined parameters to plot your fit
linear_model = Model(linear)
data = RealData(x, y, sx=x_err, sy=y_err)
odr = ODR(data, linear_model, beta0=[0, 1])
res = odr.run()
res.pprint()

# Plot raw data
plt.errorbar(x, y, xerr=x_err, yerr=y_err, ls="", marker=".")

# plot fit
x_fit = x # Using same x since I'm lazy
y_fit = linear(res.beta, x_fit)
plt.plot(x_fit, y_fit, color="k")

# Plot curve fit for comparison
def linear_curve(x, m , b):
    return m * x + b

popt, pcov = curve_fit(linear_curve, x, y, sigma=y_err)
y_fit_curve = linear_curve(x, *popt)

plt.plot(x_fit, y_fit_curve)

plt.show()

import numpy as np
import matplotlib.pyplot as plt

# y = mx + b
def linear(x, m, b):
    return m*x + b

# y = 1 - exp(-phi * sigma)
# Returns values between 0 and 1
def direct_impact(phi, sigma):
    return 1 - np.exp(-1 * phi * sigma)

# y = f_sat * (1 - exp(-phi * sigma)) + offset
def direct_impact_scaled(phi, sigma, f_sat):
    return f_sat * (1 - np.exp(-1 * phi * sigma))

# y = f_sat * (1 - exp(-phi * sigma)) + offset
def direct_impact_arb(phi, sigma, f_sat, offset):
    return offset + f_set * (1 - np.exp(-1 * phi * sigma))




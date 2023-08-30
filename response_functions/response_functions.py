import numpy as np
import matplotlib.pyplot as plt

# y = mx + b
def linear(x, m, b):
    return m*x + b

# y = 1 - exp(-phi * sigma)
# Returns values between 0 and 1
def single_impact(phi, sigma):
    return 1 - np.exp(-1 * phi * sigma)

# y = f_sat * (1 - exp(-phi * sigma)) + offset
def single_impact_scaled(phi, sigma, f_sat):
    return f_sat * single_impact(phi, sigma)

# y = f_sat * (1 - exp(-phi * sigma)) + offset
def single_impact_arb(phi, sigma, f_sat, offset):
    return offset + single_impact_scaled(phi, sigma, f_sat)

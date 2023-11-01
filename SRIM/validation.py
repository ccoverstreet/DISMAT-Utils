import numpy as np
import matplotlib.pyplot as plt

rho_3114 = np.genfromtxt("3p114.dat")
rho_568 = np.genfromtxt("5p68.dat")
rho_3114_conv = np.genfromtxt("3p114_conv.dat")

# Scaling energy loss and depth using density
plt.plot(rho_3114[:, 0] / 5.68 * 3.114, rho_3114[:, 3] / 3.114 * 5.68, label="3.114 adj.")
plt.plot(rho_3114_conv[:, 0], rho_3114_conv[:, 3], label="3.114 conv.")
plt.plot(rho_568[:, 0], rho_568[:, 3], label="5.68")

plt.legend()
plt.savefig("validation.png")
plt.show()

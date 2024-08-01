import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simps
from scipy.interpolate import interp1d
file_path = '/Users/georgeadamson/Desktop/UTK python programs for reaserch/946mevAU_Ho2Ti2O7.csv'
df = pd.read_csv(file_path,skiprows=1, header=None)
title= ''
# Display the first few rows of the dataframe to understand its structure
print(df.head())
print(df[0])

x_value = 25  # Replace with the x-coordinate where you want the vertical line
interpolated_y = np.interp(x_value, df[0], df[1])
new_point = pd.DataFrame({0: [x_value], 1: [interpolated_y]})
df = pd.concat([df, new_point]).sort_values(by=0).reset_index(drop=True)

###
filtered_df = df[df[0] <= x_value].copy()

# Interpolating function for the entire dataset
f = interp1d(filtered_df[0], filtered_df[1], kind='linear')
# Integrate the area under the curve up to fill_to_x
x_values = filtered_df[0]
y_values = filtered_df[1]
area_under_curve = simps(y_values, x_values)
# Calculate the length of the curve up to fill_to_x
length_of_curve = np.sqrt(np.diff(x_values)**2 + np.diff(y_values)**2).sum()
# Calculate the desired value
desired_value = area_under_curve / length_of_curve
std_deviation = np.std(y_values)

###
print(desired_value)
print(std_deviation)
plt.figure(figsize=(10, 6))
plt.tight_layout()
plt.plot(df.iloc[:,0], df.iloc[:,1],color='red',linewidth=2.5)
plt.axvline(x=x_value, color='black', linestyle='--', label='Vertical Line',linewidth=2.5)
plt.fill_between(df[0], df[1], where=(df[0] <= x_value ), color='skyblue', alpha=0.4)
###
# Adding a double-sided arrow and text "thickness"
plt.annotate('', xy=(x_value , max(y_values)/2), xytext=(0, max(y_values)/2),
             arrowprops=dict(arrowstyle='<->', color='black', lw=2.5))
plt.text(x_value / 2, (max(y_values)/2)*1.015, 'Sample Thickness', verticalalignment='bottom', horizontalalignment='center',
         color='black', fontsize=16)
###
plt.text(1,1,f" {round(desired_value,2)} ± {round(std_deviation,2)} Kev/nm",ha='left', fontsize=20, color='black')

plt.xlabel(r"Depth ($\mu m$)", fontsize=20)
plt.ylabel("Energy loss (keV/nm)", fontsize=20)
plt.xlim(left=0)
plt.ylim(bottom=0)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
#plt.grid(False)
#plt.savefig("Variance_withlegend_normed_w_shamblin_wbox.svg")
plt.show()
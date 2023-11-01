#!/usr/bin/env python3
# Utility Library and Script for SRIM output analysis
# Cale Overstreet
# Comes with a CLI tool (use `python3 thisscript.py --help` to see options)

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

# These mults are use to convert all length units to micrometers
MULTS = {
    "A": 1E-4,
    "um": 1,
    "mm": 1E3,
    "keV": 1,
    "MeV": 1E3,
    "GeV": 1e6
}

@dataclass
class SrimData:
    rho: float
    data: np.array

# Convert all to keV and micron
def read_file(filename):
    with open(filename) as f:
        collect = False
        collect_count = 0
        out = []
        conversion = 1.0
        rho = 1.0

        for line in f:
            stripped = line.strip()


            if stripped.startswith("-----"):
                collect = not collect
                collect_count += 1
                continue

            if not collect: 
                if "Density" in stripped:
                    rho = float(stripped.split()[3])

            if collect and collect_count < 2:
                split_line = line.split()
                row = []
                row.append(float(split_line[0]) * MULTS[split_line[1]])
                row.append(float(split_line[2]))
                row.append(float(split_line[3]))
                row.append(float(split_line[4]) * MULTS[split_line[5]])
                row.append(float(split_line[6]) * MULTS[split_line[7]])
                row.append(float(split_line[8]) * MULTS[split_line[9]])

                out.append(row)
            elif collect and collect_count >= 2:
                # We only care about this line
                if "keV" in line and "micron" in line:
                    conversion = float(line.split()[0])

        # Use conversion to change energy loss to keV / micron
        print(f"Conversion = {conversion}")
        out = np.array(out)
        out[:, 1] = out[:, 1] * conversion
        out[:, 2] = out[:, 2] * conversion

        return SrimData(rho, out)

def range_to_depth(range_data):
    return range_data[-1] - range_data

# Convert keV / micron to keV / nm
# Make sure to pass in rho adjusted by packing fraction
def dedx_to_kev_nm(eloss):
    return eloss / 1000


if __name__ == "__main__":
    import sys 
    import os
    import argparse

    parser = argparse.ArgumentParser(
        prog="CCO SRIM Utils",
        description="Use to convert SRIM stopping tables output to a energy loss plot",
    )

    parser.add_argument("datafiles", nargs="+")
    parser.add_argument("-s", "--save", type=str,
                        help="Save the converted depth and energy loss data to a file")
    parser.add_argument("-r", "--rho", type=float, required=True,
                        help="theoretical density of material (ex. 3.43 g/cm^3)")
    parser.add_argument("-p", "--packing", type=float, required=True,
                        help="estimated packing fraction of material (ex. 0.8)")

    args = parser.parse_args()

    # Try to read and plot every provided data file
    # All plots are shown at the end
    # Useful if multiple ions/energies are used for a single compound
    for filename in args.datafiles:
        print(f"Processing {filename}")

        rho = args.rho
        packing_frac = args.packing

        srim_data = read_file(filename)
        data = srim_data.data

        print(f"Using density of {rho} g/cm^3")
        print(f"SRIM was run using density of {srim_data.rho} g/cm^3")
        print(f"Using packing fraction of {packing_frac}")

        print("\n*********\nIMPORTANT: The 'normalized' plot and dataset apply the packing fraction to the energy loss values as well to preserve the integral. \n!!!DO NOT USE WHEN REPORTING VALUES IN PAPERS.!!!\n*********\n")

        # Perform all conversions to usable output format
        # We use the SRIM density and user provided density to properly scale 
        # the data.
        # Density correction rho_corr = user_rho / SRIM_rho
        rho_corr = rho / srim_data.rho

        depth = range_to_depth(data[:, 3]) / packing_frac / rho_corr
        elec_dedx = dedx_to_kev_nm(data[:,1]) * rho_corr
        nuclear_dedx = dedx_to_kev_nm(data[:, 2]) * rho_corr
        
        # Normalized is just used for keeping the integral of the table data the same.
        # Normalized should not be reported in paper
        norm_elec_dedx = dedx_to_kev_nm(data[:,1]) * packing_frac * rho_corr
        norm_nuclear_dedx = dedx_to_kev_nm(data[:, 2]) * packing_frac * rho_corr

        if args.save:
            combined_array = np.vstack((depth,
                                        elec_dedx, nuclear_dedx, elec_dedx + nuclear_dedx,
                                        norm_elec_dedx, norm_nuclear_dedx, norm_nuclear_dedx + norm_elec_dedx)).T
            with open(args.save, "w") as f:
                np.savetxt(f, np.flip(combined_array, axis=0), header="Depth (um), Electronic Energy Loss (keV/nm), Nuclear Energy Loss (keV/nm), Total Energy Loss (keV/nm), Normalized Electronic Energy Loss (keV/nm), Normalized Nuclear Energy Loss (keV/nm), Normalized Total Energy Loss (keV/nm)")


        # Create figures using the generated data
        plt.figure()
        plt.plot(depth, elec_dedx + nuclear_dedx,
                 label="total", linewidth=1, color="k")
        plt.plot(depth, elec_dedx,
                 label="electronic", linewidth=1, color="r", ls="--")
        plt.plot(depth, nuclear_dedx,
                 label="nuclear", linewidth=1, color="b", ls="--")
        plt.title(f"{filename}", fontsize=16)
        plt.xlabel(r"Depth ($\mu m$)", fontsize=14)
        plt.ylabel("Energy loss (keV/nm)", fontsize=14)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.legend(fontsize=14)

        plt.figure()
        plt.plot(depth, norm_elec_dedx + norm_nuclear_dedx,
                 label="total", linewidth=1, color="k")
        plt.plot(depth, norm_elec_dedx,
                 label="electronic", linewidth=1, color="r", ls="--")
        plt.plot(depth, norm_nuclear_dedx,
                 label="nuclear", linewidth=1, color="b", ls="--")
        plt.title(f"{filename} normalized", fontsize=16)
        plt.xlabel(r"Depth ($\mu m$)", fontsize=14)
        plt.ylabel("Energy loss (keV/nm)", fontsize=14)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.legend(fontsize=14)

        plt.tight_layout()

    plt.show()

#!/usr/bin/env python3
# Utility Library and Script for SRIM output analysis
# Cale Overstreet
# Comes with a CLI tool (use `python3 thisscript.py --help` to see options)

import numpy as np
import matplotlib.pyplot as plt

# These mults are use to convert all length units to micrometers
MULTS = {
    "A": 1E-4,
    "um": 1,
    "keV": 1,
    "MeV": 1E3,
    "GeV": 1e6
}

# Convert all to keV and micron
def read_file(filename):
    with open(filename) as f:
        collect = False
        out = []
        for line in f:
            if line.startswith("-"):
                collect = collect != True
                continue
            if not collect: continue

            split_line = line.split()
            row = []
            row.append(float(split_line[0]) * MULTS[split_line[1]])
            row.append(float(split_line[2]))
            row.append(float(split_line[3]))
            row.append(float(split_line[4]) * MULTS[split_line[5]])
            row.append(float(split_line[6]) * MULTS[split_line[7]])
            row.append(float(split_line[8]) * MULTS[split_line[9]])

            out.append(row)

        return np.array(out)

def range_to_depth(range_data):
    return range_data[-1] - range_data

# Convert MeV/(mg/cm^2) to keV/nm
# Make sure to pass in rho adjusted by packing fraction
def dedx_to_kev_nm(eloss, rho):
    rho_adj = rho * 1000
    eloss_mev_cm = rho_adj * eloss
    eloss_kev_nm = eloss_mev_cm * 1E3 / 1E7
    return eloss_kev_nm


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

        print(f"Using density of {rho} g/cm^3")
        print(f"Using packing fraction of {packing_frac}")

        print("\n*********\nIMPORTANT: The 'normalized' plot and dataset apply the packing fraction to the energy loss values as well to preserve the integral\n*********\n")

        data = read_file(filename)
        depth = range_to_depth(data[:, 3]) / packing_frac
        elec_dedx = dedx_to_kev_nm(data[:,1], rho)
        nuclear_dedx = dedx_to_kev_nm(data[:, 2], rho)

        norm_elec_dedx = dedx_to_kev_nm(data[:,1], rho * packing_frac)
        norm_nuclear_dedx = dedx_to_kev_nm(data[:, 2], rho * packing_frac)

        if args.save:
            combined_array = np.vstack((depth,
                                        elec_dedx, nuclear_dedx, elec_dedx + nuclear_dedx,
                                        norm_elec_dedx, norm_nuclear_dedx, norm_nuclear_dedx + norm_elec_dedx)).T
            with open(args.save, "w") as f:
                np.savetxt(f, np.flip(combined_array, axis=0), header="Depth (um), Electronic Energy Loss (keV/nm), Nuclear Energy Loss (keV/nm), Total Energy Loss (keV/nm), Normalized Electronic Energy Loss (keV/nm), Normalized Nuclear Energy Loss (keV/nm), Normalized Total Energy Loss (keV/nm)")


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

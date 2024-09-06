from io import SEEK_SET
import struct
import sys
import matplotlib.pyplot as plt
from dataclasses import dataclass
import numpy as np
from os import path

# Header information starts at 0xBB8 offset
# Data stream appears to start at 0xC02 offset

def main():
    if len(sys.argv) < 2:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        files = tk.filedialog.askopenfiles(mode="r")
        print(files)

        for filename in files:
            data = read_file(filename.name)

            data.write_file(f"{path.splitext(path.basename(filename.name))[0]}_conv.xy")

            plt.plot(data.two_theta, data.intensities)
            plt.show()

    else:
        # Run in CLI mode
        for filename in sys.argv[1:]:
            data = read_file(filename)

            data.write_file(f"{path.splitext(path.basename(filename))[0]}_conv.xy")

            plt.plot(data.two_theta, data.intensities)
            plt.show()

@dataclass
class XRDData:
    scan_speed: float
    theta_min: float
    theta_max: float
    spacing: float
    two_theta: np.array
    intensities: np.array

    def write_file(self, filename):
        file = open(filename, "w")
        file.write(f"# scan speed: {self.scan_speed}\n# theta min: {self.theta_min}\n# theta_max: {self.theta_max}\n# spacing: {self.spacing}\n# two theta, intensity\n")
        for i in range(0, len(self.two_theta)):
            file.write(f"{self.two_theta[i]} {self.intensities[i]} \n")

        file.close()


def read_file(filename):
    f = open(filename, "rb")

    # Get header info
    f.seek(0xbb8)
    scan_speed = struct.unpack("f", f.read(4))[0]
    theta_min = struct.unpack("f", f.read(4))[0]
    theta_max = struct.unpack("f", f.read(4))[0]
    spacing = struct.unpack("f", f.read(4))[0]

    print(scan_speed, theta_min, theta_max, spacing)


    theta = []
    intensities = []

    f.seek(0xc02)
    cur_loop = 0
    while True:
        block = f.read(4)
        if len(block) < 4:
            break

        val = struct.unpack("f", block)[0]
        intensities.append(val)
        theta.append(theta_min + cur_loop * spacing)
        cur_loop += 1


    return XRDData(
        scan_speed,
        theta_min,
        theta_max,
        spacing,
        np.array(theta),
        np.array(intensities)
    )

if __name__ == "__main__":
    main()

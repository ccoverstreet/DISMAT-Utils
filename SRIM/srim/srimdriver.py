import subprocess
import os
from dataclasses import dataclass
from enum import Enum
import sys

PROGRAM_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

@dataclass()
class ElementData():
    atomic_number: int
    symbol: str
    name: str
    MAI_mass: int
    MAI_weight: float
    natural_weight: float


# Preload Elemental Data
def load_element_data(filename):
    data = []
    elem_dict = {}
    with open(filename) as f:
        for i, line in enumerate(f):
            if i < 2 or line.startswith("(c)"): 
                continue

            split = line.replace("\"", "").split()

            elem_dict[split[1]] = ElementData(
                int(split[0]),
                split[1],
                split[2],
                int(split[3]),
                float(split[4]),
                float(split[5])
            )

    return elem_dict


ELEM_DICT = load_element_data(f"{PROGRAM_DIR}/data/ATOMDATA")


class TargetType(Enum):
    SOLID = 0
    GAS = 1

@dataclass()
class SRIMConfig:
    output_name: str
    ion: ElementData
    target_type: TargetType
    density: float
    compound_corr: float
    stoich: [float]
    elements: [ElementData]
    min_energy: float
    max_energy: float

    def to_input_file_str(self):
        buffer = "---Stopping/Range Input Data (Number-format: Period = Decimal Point)\r\n"
        buffer += "---Output File Name\r\n"
        buffer += f"\"{self.output_name}\"" + "\r\n"
        buffer += "---Ion(Z), Ion Mass(u)\r\n"
        buffer += f"{self.ion.atomic_number}   {self.ion.MAI_weight}\r\n"
        buffer += "---Target Data: (Solid=0,Gas=1), Density(g/cm3), Compound Corr.\r\n"
        buffer += f"{self.target_type.value} {self.density} {self.compound_corr}\r\n"
        buffer += "---Number of Target Elements\r\n"
        buffer += f"{len(self.stoich)}\r\n"
        buffer += "---Target Elements: (Z), Target name, Stoich, Target Mass(u)\r\n"
        for i in range(0, len(self.stoich)):
            elem = self.elements[i]
            buffer += f"{elem.atomic_number} \"{elem.name}\" {self.stoich[i]} {elem.natural_weight}\r\n"

        buffer += "---Output Stopping Units (1-8)\r\n"
        buffer += "5\r\n"
        buffer += "---Ion Energy : E-Min(keV), E-Max(keV)\r\n"
        buffer += f"{self.min_energy} {self.max_energy}\r\n"

        return buffer


def run_srim_config(srim_config):
    sr_in = f"{PROGRAM_DIR}/srim/SR.IN"
    with open(sr_in, "w") as f:
        f.write(srim_config.to_input_file_str())

    subprocess.run(PROGRAM_DIR + "/srim/" + "SRModule.exe", cwd=PROGRAM_DIR + "/srim")


if __name__ == "__main__":
    #subprocess.run()
    conf = SRIMConfig(
        "testfile",
        ELEM_DICT["Au"],
        TargetType.SOLID,
        5.68,
        1,
        [1, 2],
        [ELEM_DICT["Zr"], ELEM_DICT["O"]],
        10,
        1470000
    )

    with open("SR.IN", "w") as f:
        f.write(conf.to_input_file_str())

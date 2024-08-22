from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal as Signal
from PyQt6.QtCore import Qt,QSize 
from PyQt6.QtGui import QFont
import sys
import matplotlib.pyplot as plt
import ccosrimutil_v5 as csu
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import numpy as np
import srim as srim

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        central = QtWidgets.QWidget()

        self.setWindowTitle("CCO Srim Utility")

        master = QtWidgets.QHBoxLayout()

        self.input_box = QtWidgets.QVBoxLayout()

        self.srim_form = SRIMInputForm()
        self.material_form = MaterialForm()
        self.plotting_frame = PlottingFrame()
        self.divider = QtWidgets.QLabel("")
        self.divider.setStyleSheet("border-top: 1px solid black")
        #self.divider.setLineWidth(5)
        #self.divider.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        #self.divider.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

        self.srim_form.new_srim_table.connect(self.material_form.open_file)
        self.material_form.new_data.connect(self.plotting_frame.plot_table)

        self.input_box.addWidget(self.srim_form)
        self.input_box.addWidget(self.divider)
        self.input_box.addWidget(self.material_form)

        master.addLayout(self.input_box)
        master.addWidget(self.plotting_frame)

        central.setLayout(master)
        self.setCentralWidget(central)
        self.show()


class ElementComboBox(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QtWidgets.QVBoxLayout()

        self.combobox = QtWidgets.QComboBox()
        self.combobox.setFont(QFont("Monospace"))
        self.combobox.setMinimumHeight(30)
        for sym in srim.ELEM_DICT:
            elem = srim.ELEM_DICT[sym]
            self.combobox.addItem(f"{elem.atomic_number:2} {sym:2} {elem.name:20}", sym)

        self.layout.addWidget(self.combobox)

        self.setLayout(self.layout)

    def getSymbol(self):
        return self.combobox.currentData()

class SRIMInputForm(QtWidgets.QWidget):
    new_srim_table = Signal(str)

    def __init__(self):
        super().__init__()

        self.input_layout = QtWidgets.QVBoxLayout()


        self.setMaximumWidth(500)

        self.ion_row = QtWidgets.QHBoxLayout()
        self.combo_label = QtWidgets.QLabel("Ion:")
        self.ionbox = ElementComboBox()
        #self.combobox = QtWidgets.QComboBox()
        #self.combobox.setFont(QFont("Monospace"))
        #for sym in srim.ELEM_DICT:
        #    elem = srim.ELEM_DICT[sym]
        #    self.combobox.addItem(f"{elem.atomic_number:2} {sym:2} {elem.name:20}", sym)

        self.ion_row.addWidget(self.combo_label)
        self.ion_row.addWidget(self.ionbox)

        self.min_energy_row = QtWidgets.QHBoxLayout()
        self.min_energy_label = QtWidgets.QLabel("Min. energy (keV)")
        self.min_energy_input = QtWidgets.QDoubleSpinBox()
        self.min_energy_input.setMinimum(10)
        self.min_energy_input.setMaximum(1E9)
        self.min_energy_row.addWidget(self.min_energy_label)
        self.min_energy_row.addWidget(self.min_energy_input)

        self.max_energy_row = QtWidgets.QHBoxLayout()
        self.max_energy_label = QtWidgets.QLabel("Max. energy (keV)")
        self.max_energy_input = QtWidgets.QDoubleSpinBox()
        self.max_energy_input.setMinimum(10)
        self.max_energy_input.setMaximum(1E9)
        self.max_energy_row.addWidget(self.max_energy_label)
        self.max_energy_row.addWidget(self.max_energy_input)

        self.list_control_row = QtWidgets.QHBoxLayout()
        self.add_elem_button = QtWidgets.QPushButton("Add element")
        self.add_elem_button.clicked.connect(self.add_element)
        self.delete_elem_button = QtWidgets.QPushButton("Delete sel.")
        self.delete_elem_button.clicked.connect(self.delete_element)
        self.list_control_row.addWidget(self.add_elem_button)
        self.list_control_row.addWidget(self.delete_elem_button)

        self.elem_list = QtWidgets.QListWidget()
        self.add_element()
        #item = QtWidgets.QListWidgetItem()
        #self.elem_list.addItem(item)
        #self.elem_list.setItemWidget(item, TargetElementRow())

        self.density_row = QtWidgets.QHBoxLayout()
        self.density_label = QtWidgets.QLabel("Density (g/cm<sup>3</sup>):")
        self.density_input = QtWidgets.QDoubleSpinBox()
        self.density_row.addWidget(self.density_label)
        self.density_row.addWidget(self.density_input)

        #self.ion_line = QtWidgets.QLineEdit()
        #self.ion_completer = QtWidgets.QCompleter([srim.ELEM_DICT[x].name for x in srim.ELEM_DICT.keys()])
        #self.ion_completer = QtWidgets.QCompleter(list(srim.ELEM_DICT.keys()))
        #self.ion_completer.setCaseSensitivity(Qt.CaseSensitivity(0))
        #self.ion_line.setCompleter(self.ion_completer)
        #self.input_layout.addWidget(self.ion_line)

        self.run_srim_button = QtWidgets.QPushButton("Run SRIM table")
        self.run_srim_button.clicked.connect(self.run_srim_module)

        self.input_layout.addLayout(self.ion_row)
        self.input_layout.addLayout(self.min_energy_row)
        self.input_layout.addLayout(self.max_energy_row)
        self.input_layout.addLayout(self.list_control_row)
        self.input_layout.addWidget(self.elem_list)
        self.input_layout.addLayout(self.density_row)
        self.input_layout.addWidget(self.run_srim_button)

        self.setLayout(self.input_layout)

    def add_element(self):
        new_item = QtWidgets.QListWidgetItem()
        new_item.setSizeHint(QSize(30, 60))
        self.elem_list.addItem(new_item)
        self.elem_list.setItemWidget(new_item, TargetElementRow())

    def delete_element(self):
        items = self.elem_list.selectedItems()
        for x in items:
            row = self.elem_list.indexFromItem(x)
            wid = self.elem_list.takeItem(row.row())
            del wid
        print(items)

    def run_srim_module(self):
        ion_data = srim.ELEM_DICT[self.ionbox.getSymbol()]
        min_energy = self.min_energy_input.value()
        max_energy = self.max_energy_input.value()

        stoich = []
        target = []
        for i in range(0, self.elem_list.count()):
            item = self.elem_list.item(i)
            widget = self.elem_list.itemWidget(item)
            data = widget.data()

            target.append(data[0])
            stoich.append(data[1])

        density = self.density_input.value()

        srim_filename_parts = QtWidgets.QFileDialog.getSaveFileName(self, 'Save table', "", "SRIM Table File (*.srim);;")

        if srim_filename_parts[0] == "": 
            return

        srim_filename = srim_filename_parts[0] if srim_filename_parts[0].endswith(".srim") else srim_filename_parts[0] + ".srim"


        conf = srim.SRIMConfig(
            srim_filename,
            ion_data,
            srim.TargetType.SOLID,
            density,
            1,
            stoich,
            target,
            min_energy,
            max_energy
        )

        print("Running SRIM config:", conf)
        srim.run_srim_config(conf)
        print("Finished running SRIM config")

        self.new_srim_table.emit(srim_filename)



class TargetElementRow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.elembox = ElementComboBox()
        self.stoich_input = QtWidgets.QDoubleSpinBox()
        self.stoich_input.setMaximumWidth(80)
        self.stoich_input.setMaximum(1000)

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.elembox)
        self.layout.addWidget(self.stoich_input)

        self.setLayout(self.layout)

        #self.setMinimumHeight(60)

    def data(self):
        stoich = self.stoich_input.value()
        return (srim.ELEM_DICT[self.elembox.getSymbol()], stoich)




class MaterialForm(QtWidgets.QWidget):
    new_data = Signal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.setMaximumWidth(500)

        input_layout = QtWidgets.QVBoxLayout()

        file_row = QtWidgets.QHBoxLayout()
        self.file_label = QtWidgets.QLabel("Current file: none")
        self.file_label.setMaximumWidth(200)
        self.file_label.setWordWrap(True)
        file_button = QtWidgets.QPushButton("Open")
        file_button.clicked.connect(self.open_file_dialog)
        file_button.setMaximumWidth(39)

        file_row.addWidget(self.file_label)
        file_row.addWidget(file_button)

        density_row = QtWidgets.QHBoxLayout()
        rho_label = QtWidgets.QLabel("Density (g/cm<sup>3</sup>):")
        self.rho_input = QtWidgets.QDoubleSpinBox()
        self.rho_input.setMaximumWidth(100)
        self.rho_input.setDecimals(6)
        self.rho_input.setValue(1.00)
        self.rho_input.setSingleStep(0.01)
        self.rho_input.setMinimum(0.01)
        self.rho_input.textChanged.connect(self.process_data)
        density_row.addWidget(rho_label)
        density_row.addWidget(self.rho_input)

        packing_row = QtWidgets.QHBoxLayout()
        packing_label = QtWidgets.QLabel("Packing fraction:")
        self.packing_input = QtWidgets.QDoubleSpinBox()
        self.packing_input.setMaximumWidth(100)
        self.packing_input.setDecimals(6)
        self.packing_input.setValue(1.0)
        self.packing_input.setSingleStep(0.05)
        self.packing_input.setMinimum(0.05)
        self.packing_input.textChanged.connect(self.process_data)
        packing_row.addWidget(packing_label)
        packing_row.addWidget(self.packing_input)

        input_layout.addLayout(file_row)
        input_layout.addLayout(density_row)
        input_layout.addLayout(packing_row)

        process_button = QtWidgets.QPushButton("Process")
        process_button.clicked.connect(self.process_data)
        input_layout.addWidget(process_button)

        save_button = QtWidgets.QPushButton("Save")
        save_button.clicked.connect(self.open_save_dialog)
        input_layout.addWidget(save_button)


        input_layout.addStretch()


        self.setLayout(input_layout)

    def open_file_dialog(self):
        self.input_filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open SRIM output file')
        if self.input_filename[0] == "":
            return

        self.open_file(self.input_filename[0])

    def open_file(self, filename):
        print(filename)
        self.file_label.setText(f"Current file: {filename}")
        try:
            self.srim_data = csu.read_file(filename)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "CCO SRIM Utility Error", f"The selected file is not a valid SRIM output file.\n{e}")
            return

        self.rho_input.setValue(self.srim_data.rho)
        self.process_data()

    def process_data(self):
        config = csu.ConversionConfig(self.rho_input.value(), self.packing_input.value())
        if not hasattr(self, "srim_data"):
            QtWidgets.QMessageBox.warning(self, "CCO SRIM Utility Error", "Please select a SRIM file to process.")
            return

        self.table = csu.convert_srim_to_table(self.srim_data, config)
        self.new_data.emit(self.table)

    def open_save_dialog(self):
        if not hasattr(self, "table"):
            QtWidgets.QMessageBox.warning(self, "CCO SRIM Utility Error", "There is no data to save. Please process a file first before saving.")
            return

        savename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save table', "", "Comma-separated values (*.csv);;")
        print(savename)
        if savename[0] == "": 
            return

        name = savename[0] if savename[0].endswith(".csv") else savename[0] + ".csv"


        np.savetxt(name, np.flip(self.table, axis=0),
                   header="Depth (um), Electronic Energy Loss (keV/nm), Nuclear Energy Loss (keV/nm), Total Energy Loss (keV/nm), Energy (keV)",
                   delimiter=",")



class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        layout = QtWidgets.QVBoxLayout()
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.fig = fig
        super(MplCanvas, self).__init__(fig)

    def update_plot(self):
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


class PlotTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.canvas = MplCanvas()
        self.fig = self.canvas.fig
        self.axes = self.canvas.axes
        self.toolbar = NavigationToolbar2QT(self.canvas)

        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_plot(self):
        self.canvas.update_plot()


class PlottingFrame(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()

        self.tab_widget = QtWidgets.QTabWidget()

        self.dEdx_x = PlotTab()
        self.dEdx_E = PlotTab()
        self.annotated = PlotTab()
        self.deriv = PlotTab()

        #layout.addWidget(demo)
        self.tab_widget.addTab(self.dEdx_x, "dE/dx(x)")
        self.tab_widget.addTab(self.dEdx_E, "dE/dx(E)")
        self.tab_widget.addTab(self.annotated, "dE/dx(x) annotated")
        self.tab_widget.addTab(self.deriv, "(dE/dx(x))'")
        self.tab_widget.currentChanged.connect(self.refresh_tab)
        layout.addWidget(self.tab_widget)

        self.setLayout(layout)

    def refresh_tab(self, index):
        page = self.tab_widget.widget(index)
        page.fig.tight_layout()
        page.update_plot()

    def plot_table(self, data):
        # dEdx(x) plot
        self.dEdx_x.axes.clear()
        self.dEdx_x.axes.plot(data[:, 0], data[:, 1], color="tab:red", label="Electronic dE/dx")
        self.dEdx_x.axes.plot(data[:, 0], data[:, 2], color="tab:blue", label="Nuclear dE/dx")
        self.dEdx_x.axes.plot(data[:, 0], data[:, 3], color="k", label="Total dE/dx")
        self.dEdx_x.axes.set_xlabel(r"Depth [$\mu$m]", fontsize=16)
        self.dEdx_x.axes.set_ylabel(r"dE/dx [keV/nm]", fontsize=16)
        self.dEdx_x.axes.tick_params(axis="both", which="major", labelsize=12)
        self.dEdx_x.axes.set_xlim(0, np.max(data[:, 0]) * 1.05)
        self.dEdx_x.axes.set_ylim(0, np.max(data[:, 1]) * 1.05)
        self.dEdx_x.axes.legend(fontsize=12)
        #self.dEdx_x.fig.tight_layout()
        self.dEdx_x.fig.tight_layout()
        self.dEdx_x.update_plot()

        # dEdx(E) plot
        self.dEdx_E.axes.clear()
        self.dEdx_E.axes.plot(data[:, 4], data[:, 1], color="tab:red", label="Electronic dE/dx")
        self.dEdx_E.axes.plot(data[:, 4], data[:, 2], color="tab:blue", label="Nuclear dE/dx")
        self.dEdx_E.axes.plot(data[:, 4], data[:, 3], color="k", label="Total dE/dx")
        self.dEdx_E.axes.set_xlabel(r"Energy [keV]", fontsize=16)
        self.dEdx_E.axes.set_ylabel(r"dE/dx [keV/nm]", fontsize=16)
        self.dEdx_E.axes.tick_params(axis="both", which="major", labelsize=12)
        #self.dEdx_E.axes.set_xlim(0, np.max(data[:, 4]) * 1.05)
        self.dEdx_E.axes.set_ylim(0, np.max(data[:, 3]) * 1.05)
        self.dEdx_E.axes.set_xscale("log")
        self.dEdx_E.axes.legend(fontsize=12)
        #self.dEdx_E.fig.tight_layout()
        self.dEdx_E.fig.tight_layout()
        self.dEdx_E.update_plot()


        # Annotated plot
        self.annotated.axes.clear()

        # find 10% dev
        flipped = np.flip(data, axis=0)
        dEdx_0 = flipped[0, 1]

        # Find depth where stopping is more than 10%
        # We linearly interpolate to find the exact point
        for i, val in enumerate(flipped[:, 1]):
            print(val, dEdx_0)
            delta = np.abs(val - dEdx_0) / dEdx_0
            print(delta)
            if delta > 0.1:
                before = flipped[i - 1, 1]
                after = flipped[i, 1]

                before_x = flipped[i - 1, 0]
                after_x = flipped[i, 0]

                print()
                print(before_x, after_x)
                print(before, after)

                target = dEdx_0 * 0.9

                print(target)

                if before > after:
                    dev_depth = np.interp(target, [after, before], [after_x, before_x])
                else:
                    dev_depth = np.interp(target, [before, after], [before_x, after_x])

                print(dev_depth)
                break


        self.annotated.axes.plot(data[:, 0], data[:, 1], color="k", label="Total dE/dx")
        self.annotated.axes.axvline(dev_depth, color="k", ls="--", label=f"10% dEdx(x) deviation ({round(dev_depth, 2)} " + r"$\mu m$)")
        self.annotated.axes.set_xlabel(r"Energy [keV]", fontsize=16)
        self.annotated.axes.set_ylabel(r"dE/dx [keV/nm]", fontsize=16)
        self.annotated.axes.tick_params(axis="both", which="major", labelsize=12)
        self.annotated.axes.set_xlim(0, np.max(data[:, 0]) * 1.05)
        self.annotated.axes.set_ylim(0, np.max(data[:, 1]) * 1.05)
        self.annotated.axes.legend(fontsize=12)
        self.annotated.fig.tight_layout()
        self.annotated.update_plot()


        # (dE/dx)'
        self.deriv.axes.clear()
        dEdxp = np.diff(flipped[:, 3]) / np.diff(flipped[:, 0])
        dEdxp_x = np.diff(flipped[:, 0]) / 2 + flipped[:-1, 0]

        self.deriv.axes.plot(dEdxp_x, dEdxp)
        self.deriv.update_plot()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec()

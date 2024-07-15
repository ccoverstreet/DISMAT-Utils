from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal as Signal
import sys
import matplotlib.pyplot as plt
import ccosrimutil_v5 as csu
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import numpy as np

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        central = QtWidgets.QWidget()

        self.setWindowTitle("CCO Srim Utility")

        master = QtWidgets.QHBoxLayout()

        self.material_form = MaterialForm()
        self.plotting_frame = PlottingFrame()

        self.material_form.new_data.connect(self.plotting_frame.plot_table)

        master.addWidget(self.material_form)
        master.addWidget(self.plotting_frame)

        central.setLayout(master)
        self.setCentralWidget(central)
        self.show()


class MaterialForm(QtWidgets.QWidget):
    new_data = Signal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.setMaximumWidth(500)

        input_layout = QtWidgets.QVBoxLayout()

        
        file_row = QtWidgets.QHBoxLayout()
        self.file_label = QtWidgets.QLabel("Current file: none")
        self.file_label.setMaximumWidth(100)
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

        self.open_file(self.input_filename)

    def open_file(self, filename):
        print(filename)
        self.file_label.setText(f"Current file: {filename}")
        try:
            self.srim_data = csu.read_file(filename[0])
        except:
            QtWidgets.QMessageBox.warning(self, "CCO SRIM Utility Error", "The selected file is not a valid SRIM output file.")
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


        np.savetxt(savename[0], np.flip(self.table, axis=0),
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

        tab_widget = QtWidgets.QTabWidget()

        self.dEdx_x = PlotTab()
        self.dEdx_E = PlotTab()
        self.annotated = PlotTab()

        #layout.addWidget(demo)
        tab_widget.addTab(self.dEdx_x, "dE/dx(x)")
        tab_widget.addTab(self.dEdx_E, "dE/dx(E)")
        tab_widget.addTab(self.annotated, "dE/dx(x) annotated")
        layout.addWidget(tab_widget)

        self.setLayout(layout)

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
        self.dEdx_E.update_plot()


        # Annotated plot
        self.annotated.axes.clear()

        # find 10% dev
        flipped = np.flip(data, axis=0)
        dEdx_0 = flipped[0, 1]

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
            
        self.annotated.update_plot()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec()

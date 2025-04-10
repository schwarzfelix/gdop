import matplotlib as mpl
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import numpy as np
from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
import matplotlib.pyplot as plt

from plot import Plot
from simulation import Simulation
from window import MainWindow

mpl.use('macosx')

if __name__ == "__main__":
    #simulation = Simulation()
    #p = Plot(simulation)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
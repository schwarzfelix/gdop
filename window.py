from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTextEdit
import numpy as np
from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)

from plot import GdopPlot
from simulation import Simulation


class MainWindow(QMainWindow):
    def __init__(self, gdop_sim: Simulation, gdop_plt: GdopPlot):
        super().__init__()

        self.simulation = gdop_sim
        self.plot = gdop_plt

        self.setWindowTitle("PyQt with Matplotlib and Slider")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.figure = self.plot.fig
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(5)
        self.slider.setValue(0)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self.update_plot)
        layout.addWidget(self.slider)

        self.angle_text = QTextEdit()
        self.angle_text.setReadOnly(True)
        self.angle_text.setText("Angles will be displayed here.")
        layout.addWidget(self.angle_text)

    def update_plot(self):
        self.simulation.sigma = self.slider.value()
        self.plot.update_plot()
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
import numpy as np
from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
import matplotlib.pyplot as plt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt with Matplotlib and Slider")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(20)
        self.slider.setValue(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self.update_plot)

        layout.addWidget(self.slider)

        self.plot_data()

    def plot_data(self, frequency=1):
        x = np.linspace(0, 2 * np.pi, 100)
        y = np.sin(frequency * x)
        self.ax.clear()
        self.ax.plot(x, y, label=f"Sine Wave (Freq: {frequency})")
        self.ax.legend()
        self.canvas.draw()

    def update_plot(self):
        frequency = self.slider.value()
        self.plot_data(frequency)
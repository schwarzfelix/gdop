from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import Qt

import presentation
from simulation import Scenario, geometry

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)

class MainWindow(QMainWindow):
    def __init__(self, gdop_scenario):
        super().__init__()

        self.scenario = gdop_scenario
        self.plot = presentation.TrilatPlot(self.scenario, self, show=False)

        self.setWindowTitle("Trilateration & GDOP")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.figure = self.plot.fig
        self.figure.set_dpi(100)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)

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
        self.scenario.sigma = self.slider.value()
        self.plot.update_plot()

    def update_angles(self):
        angles_text = ""
        for i in range(len(self.scenario.anchor_positions())):
            for j in range(i + 1, len(self.scenario.anchor_positions())):
                angle = geometry.angle_vectors(
                    self.scenario.anchor_positions()[i] - self.scenario.tag_truth.position(),
                    self.scenario.anchor_positions()[j] - self.scenario.tag_truth.position())
                angles_text += f"Angle between {self.scenario.anchors[i].name()} and {self.scenario.anchors[j].name()}: {angle:.2f}°\n"

        self.angle_text.setText(angles_text)

    def update_all(self):
        self.update_plot()
        self.update_angles()

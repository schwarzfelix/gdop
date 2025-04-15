from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTextEdit, QDoubleSpinBox, QTabWidget
from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import Qt

import presentation
from simulation import geometry

from itertools import combinations

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)

class MainWindow(QMainWindow):
    def __init__(self, gdop_scenario):
        super().__init__()

        self.scenario = gdop_scenario
        self.plot = presentation.TrilatPlot(self)

        self.setWindowTitle("Trilateration & GDOP")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.figure = self.plot.fig
        self.figure.set_dpi(100)
        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.slider = QSlider(Qt.Horizontal)
        self.sigma_input = QDoubleSpinBox()

        self.tab_widget = QTabWidget()
        self.create_plot_tab()
        self.create_sigma_tab()
        self.create_angles_tab()
        layout.addWidget(self.tab_widget)

    def create_plot_tab(self):
        self.tab_widget.addTab(self.toolbar, "Plot")

    def create_sigma_tab(self):

        inside_tab_widget = QWidget()
        inside_tab_layout = QVBoxLayout()
        inside_tab_widget.setLayout(inside_tab_layout)

        self.slider.setMinimum(0)
        self.slider.setMaximum(500)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.slider_changed)
        inside_tab_layout.addWidget(self.slider)

        self.sigma_input.setMinimum(0.0)
        self.sigma_input.setSingleStep(0.1)
        self.sigma_input.setValue(0.0)
        self.sigma_input.valueChanged.connect(self.sigma_input_changed)
        inside_tab_layout.addWidget(self.sigma_input)

        self.tab_widget.addTab(inside_tab_widget, "Sigma")

    def create_angles_tab(self):
        self.angle_text = QTextEdit()
        self.angle_text.setReadOnly(True)
        self.angle_text.setText("Angles will be displayed here.")
        self.tab_widget.addTab(self.angle_text, "Angles")

    def slider_changed(self):
        self.scenario.sigma = 0.0 + self.slider.value() * 0.01
        self.update_all()

    def sigma_input_changed(self):
        self.scenario.sigma = self.sigma_input.value()
        self.update_all()

    def update_angles(self):
        angles_text = ""
        anchor_positions = self.scenario.anchor_positions()
        for (i, j) in combinations(range(len(anchor_positions)), 2):
            angle = geometry.angle_vectors(
                anchor_positions[i] - self.scenario.tag_truth.position(),
                anchor_positions[j] - self.scenario.tag_truth.position()
            )
            angles_text += f"Angle between {self.scenario.anchors[i].name()} and {self.scenario.anchors[j].name()}: {angle:.2f}°\n"
        self.angle_text.setText(angles_text)

    def update_sigma(self):
        self.slider.setValue(int(self.scenario.sigma * 100))
        self.sigma_input.setValue(self.scenario.sigma)

    def update_all(self):
        self.plot.update_plot()
        self.update_angles()
        self.update_sigma()

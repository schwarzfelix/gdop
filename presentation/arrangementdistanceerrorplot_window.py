"""Window for displaying the arrangement distance error plot.

This module provides a standalone window for displaying the arrangement distance error plot
showing average distance errors grouped by arrangement with PD vs FW variants.
"""

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from presentation.arrangementdistanceerrorplot import ArrangementDistanceErrorPlot


class ArrangementDistanceErrorPlotWindow(QMainWindow):
    """Window for displaying the arrangement distance error plot."""

    def __init__(self, scenarios, parent=None):
        super().__init__(parent)
        self.scenarios = scenarios
        self.setWindowTitle("Arrangement Distance Error Plot - PD vs FW")
        self.resize(1000, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create the plot
        self.plot = ArrangementDistanceErrorPlot(self, self.scenarios)
        
        # Create canvas and add to layout
        self.canvas = FigureCanvasQTAgg(self.plot.fig)
        layout.addWidget(self.canvas)

        # Initial update
        self.plot.update_data()
        self.plot.redraw()

"""Window for displaying the arrangement anchor count position error plot.

This module provides a standalone window for displaying the arrangement position error plot
showing position errors grouped by arrangement with 3A vs 4A variants.
"""

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from presentation.arrangementanchorcountpositionerrorplot import ArrangementAnchorCountPositionErrorPlot


class ArrangementAnchorCountPositionErrorPlotWindow(QMainWindow):
    """Window for displaying the arrangement anchor count position error plot."""

    def __init__(self, scenarios, parent=None):
        super().__init__(parent)
        self.scenarios = scenarios
        self.setWindowTitle("Arrangement Position Error Plot - 3A vs 4A")
        self.resize(1000, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create the plot
        self.plot = ArrangementAnchorCountPositionErrorPlot(self, self.scenarios)
        
        # Create canvas and toolbar
        self.canvas = FigureCanvasQTAgg(self.plot.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Initial update
        self.plot.update_data()
        self.plot.redraw()

"""Window wrapper for AccessPointMetricsPlot.

This file provides a QMainWindow that embeds the Access Point metrics plot
and can be opened from the analysis tab.
"""

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from .accesspointmetricsplot import AccessPointMetricsPlot


class AccessPointMetricsPlotWindow(QMainWindow):
    """Window displaying Access Point quality metrics (avg error & std dev)."""

    def __init__(self, scenarios, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Access Point Quality Metrics")
        self.resize(1000, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create plot
        self.plot = AccessPointMetricsPlot(self, scenarios)
        
        # Create canvas and toolbar
        self.canvas = FigureCanvasQTAgg(self.plot.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Update and draw
        self.plot.update_data()
        self.plot.redraw()

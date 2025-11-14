"""Window wrapper for AccessPointMetricsPlotRaw.

This file provides a QMainWindow that embeds the Access Point metrics plot (raw data)
and can be opened from the analysis tab.
"""

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from .accesspointmetricsplot_raw import AccessPointMetricsPlotRaw


class AccessPointMetricsPlotRawWindow(QMainWindow):
    """Window displaying Access Point quality metrics using raw CSV data (all entries, no aggregation)."""

    def __init__(self, scenarios, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Access Point Quality Metrics - RAW DATA (All CSV Entries)")
        self.resize(1200, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create plot
        self.plot = AccessPointMetricsPlotRaw(self, scenarios)
        
        # Create canvas and toolbar
        self.canvas = FigureCanvasQTAgg(self.plot.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Update and draw
        self.plot.update_data()
        self.plot.redraw()

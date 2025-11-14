"""Window wrapper for AggregationMethodComparisonPlot.

This file provides a QMainWindow that embeds the aggregation method comparison plot
and can be opened from the analysis tab.
"""

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from .aggregationmethodcomparisonplot import AggregationMethodComparisonPlot


class AggregationMethodComparisonPlotWindow(QMainWindow):
    """Window displaying aggregation method comparison plot."""

    def __init__(self, scenarios, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aggregation Method Comparison - Position Error Analysis")
        self.resize(1200, 700)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create plot
        self.plot = AggregationMethodComparisonPlot(self, scenarios)
        
        # Create canvas and toolbar
        self.canvas = FigureCanvasQTAgg(self.plot.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Update and draw
        self.plot.update_data()
        self.plot.redraw()

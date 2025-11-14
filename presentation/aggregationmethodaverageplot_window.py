"""
Window for Aggregation Method Average Plot.
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from .aggregationmethodaverageplot import AggregationMethodAveragePlot


class AggregationMethodAveragePlotWindow(QDialog):
    """Window displaying the aggregation method average plot."""
    
    def __init__(self, parent, scenarios):
        """Initialize the window.
        
        Args:
            parent: Parent widget
            scenarios: List of scenarios to analyze
        """
        super().__init__(parent)
        self.setWindowTitle("Average Position Error by Aggregation Method")
        self.resize(800, 600)
        
        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create plot
        self.plot = AggregationMethodAveragePlot(self, scenarios)
        self.canvas = FigureCanvas(self.plot.fig)
        
        # Add toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        
        # Add canvas
        layout.addWidget(self.canvas)
        
        # Update plot
        self.plot.update_data()
        self.plot.redraw()

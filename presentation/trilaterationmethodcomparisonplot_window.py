"""Window wrapper for TrilaterationMethodComparisonPlot.

This file provides a QMainWindow that embeds the trilateration method comparison plot
and can be opened from the analysis tab.
"""

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from .trilaterationmethodcomparisonplot import TrilaterationMethodComparisonPlot


class TrilaterationMethodComparisonPlotWindow(QMainWindow):
    """Window displaying trilateration method comparison plot."""

    def __init__(self, scenarios, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Trilateration Method Comparison - Position Error Analysis")
        self.resize(1200, 700)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create plot
        self.plot = TrilaterationMethodComparisonPlot(self, scenarios)
        
        # Create canvas and toolbar
        self.canvas = FigureCanvasQTAgg(self.plot.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Update and draw
        self.plot.update_data()
        self.plot.redraw()

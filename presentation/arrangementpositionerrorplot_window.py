"""Window wrapper for ArrangementPositionErrorPlot.

This file provides a QMainWindow that embeds the arrangement position error plot
and can be opened from the analysis tab.
"""

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from .arrangementpositionerrorplot import ArrangementPositionErrorPlot


class ArrangementPositionErrorPlotWindow(QMainWindow):
    """Window displaying arrangement position error plot (PD vs FW)."""

    def __init__(self, scenarios, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Arrangement Position Error Plot (PD vs FW)")
        self.resize(1000, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create plot
        self.plot = ArrangementPositionErrorPlot(self, scenarios)
        
        # Create canvas and toolbar
        self.canvas = FigureCanvasQTAgg(self.plot.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Update and draw
        self.plot.update_data()
        self.plot.redraw()

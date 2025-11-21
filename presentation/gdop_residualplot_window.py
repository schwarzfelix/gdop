"""Window wrapper for GDOP Residual Plot."""

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from presentation.gdop_residualplot import GDOPResidualPlot


class GDOPResidualPlotWindow(QMainWindow):
    """Window to display residual plot for GDOP vs Position Error regression."""

    def __init__(self, scenarios, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GDOP vs Position Error - Residual Plot")
        self.resize(1000, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create the plot
        self.plot = GDOPResidualPlot(self, scenarios)

        # Create matplotlib canvas
        self.canvas = FigureCanvasQTAgg(self.plot.fig)
        layout.addWidget(self.canvas)

        # Add navigation toolbar
        toolbar = NavigationToolbar2QT(self.canvas, self)
        layout.addWidget(toolbar)

        # Initial plot update
        self.plot.update_data()
        self.plot.redraw()

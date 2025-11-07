from PyQt5.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from presentation.comparisonplot import ComparisonPlot

class ComparisonPlotWindow(QDialog):
    def __init__(self, app_scenarios, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Comparison Plot - GDOP per Scenario")
        self.resize(800, 600)

        # Create the ComparisonPlot instance
        self.comparison_plot = ComparisonPlot(self, app_scenarios)

        # Set up the layout
        layout = QVBoxLayout()

        # Create canvas and toolbar
        self.canvas = FigureCanvas(self.comparison_plot.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        # Initial update
        self.comparison_plot.update_data()
        self.comparison_plot.redraw()
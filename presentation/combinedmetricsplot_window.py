from PyQt5.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from presentation.combinedmetricsplot import CombinedMetricsPlot

class CombinedMetricsPlotWindow(QDialog):
    def __init__(self, app_scenarios, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Combined Metrics Plot - Position Error and Tag Truth GDOP per Scenario")
        self.resize(1000, 600)

        # Create the CombinedMetricsPlot instance
        self.combined_metrics_plot = CombinedMetricsPlot(self, app_scenarios)

        # Set up the layout
        layout = QVBoxLayout()

        # Create canvas and toolbar
        self.canvas = FigureCanvas(self.combined_metrics_plot.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        # Initial update
        self.combined_metrics_plot.update_data()
        self.combined_metrics_plot.redraw()
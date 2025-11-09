from PyQt5.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from presentation.combinedmetricslineplot import CombinedMetricsLinePlot

class CombinedMetricsLinePlotWindow(QDialog):
    def __init__(self, app_scenarios, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Combined Metrics Line Plot - Position Error and Tag Truth GDOP Trends")
        self.resize(1200, 700)

        # Create the CombinedMetricsLinePlot instance
        self.combined_metrics_line_plot = CombinedMetricsLinePlot(self, app_scenarios)

        # Set up the layout
        layout = QVBoxLayout()

        # Create canvas and toolbar
        self.canvas = FigureCanvas(self.combined_metrics_line_plot.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        # Initial update
        self.combined_metrics_line_plot.update_data()
        self.combined_metrics_line_plot.redraw()
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from presentation.combinedmetricslineplot_sorted import CombinedMetricsLinePlotSorted

class CombinedMetricsLinePlotSortedWindow(QDialog):
    def __init__(self, app_scenarios, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Combined Metrics Line Plot (Sorted) - Position Error and Tag Truth GDOP Trends")
        self.resize(1200, 700)
        
        # Get display_config from parent if available
        if parent and hasattr(parent, 'display_config'):
            self.display_config = parent.display_config

        # Create the CombinedMetricsLinePlotSorted instance
        self.combined_metrics_line_plot_sorted = CombinedMetricsLinePlotSorted(self, app_scenarios)

        # Set up the layout
        layout = QVBoxLayout()

        # Create canvas and toolbar
        self.canvas = FigureCanvas(self.combined_metrics_line_plot_sorted.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        # Initial update
        self.combined_metrics_line_plot_sorted.update_data()
        self.combined_metrics_line_plot_sorted.redraw()
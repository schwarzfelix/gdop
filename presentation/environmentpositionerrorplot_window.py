from PyQt5.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from presentation.environmentpositionerrorplot import EnvironmentPositionErrorPlot

class EnvironmentPositionErrorPlotWindow(QDialog):
    def __init__(self, app_scenarios, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Environment Position Error Plot - Position Error per Scenario (Grouped by Environment)")
        self.resize(800, 600)

        # Create the EnvironmentPositionErrorPlot instance
        self.environment_position_error_plot = EnvironmentPositionErrorPlot(self, app_scenarios)

        # Set up the layout
        layout = QVBoxLayout()

        # Create canvas and toolbar
        self.canvas = FigureCanvas(self.environment_position_error_plot.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        # Initial update
        self.environment_position_error_plot.update_data()
        self.environment_position_error_plot.redraw()
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from presentation.multi_trilatplot import MultiTrilatPlot

class MultiTrilatPlotWindow(QDialog):
    def __init__(self, scenarios, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Multi-Scenario Trilateration Plot")
        self.resize(1200, 800)

        # Copy display_config from parent (MainWindow)
        self.display_config = parent.display_config if parent else None

        # Create the MultiTrilatPlot instance
        self.multi_trilat_plot = MultiTrilatPlot(self, scenarios)

        # Set up the layout
        layout = QVBoxLayout()

        # Create canvas and toolbar
        self.canvas = FigureCanvas(self.multi_trilat_plot.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        # Initial update
        self.multi_trilat_plot.update_data()
        self.multi_trilat_plot.redraw()
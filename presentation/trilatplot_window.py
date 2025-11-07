from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from presentation.trilatplot import TrilatPlot

class TrilatPlotWindow(QDialog):
    def __init__(self, scenario, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Trilat Plot - {scenario.name}")
        self.resize(800, 600)

        # Copy display_config from parent (MainWindow)
        self.display_config = parent.display_config if parent else None

        # Create the TrilatPlot instance
        self.trilat_plot = TrilatPlot(self, scenario)

        # Set up the layout
        layout = QVBoxLayout()

        # Create canvas and toolbar
        self.canvas = FigureCanvas(self.trilat_plot.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        # Initial update
        self.trilat_plot.update_data()
        self.trilat_plot.redraw()
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import presentation
from presentation.tabs import (
    PlotTab,
    SigmaTab,
    StationsTab,
    DisplayTab,
    DataTab,
    MeasurementsTab
)


class MainWindow(QMainWindow):

    FIGURE_DPI = 100
    SIGMA_SLIDER_MAX = 5
    SIGMA_SLIDER_RESOLUTION = 100
    SIGMA_INPUT_STEP = 0.1

    def __init__(self, gdop_scenario):
        super().__init__()

        self.scenario = gdop_scenario
        self.display_config = presentation.DisplayConfig()
        self.plot = presentation.TrilatPlot(self)

        self.setWindowTitle("Trilateration & GDOP")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.figure = self.plot.fig
        self.figure.set_dpi(self.FIGURE_DPI)
        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(self.canvas)

        # Create tab widget and all tabs
        self.tab_widget = QTabWidget()
        self.create_tabs()
        layout.addWidget(self.tab_widget)

        self.start_periodic_update()
        self.update_all()

    def create_tabs(self):
        """Create all tabs using the new tab classes."""
        # Create tab instances
        self.plot_tab = PlotTab(self)
        self.sigma_tab = SigmaTab(self)
        self.stations_tab = StationsTab(self)
        self.display_tab = DisplayTab(self)
        self.data_tab = DataTab(self)
        self.measurements_tab = MeasurementsTab(self)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.plot_tab.get_widget(), self.plot_tab.tab_name)
        self.tab_widget.addTab(self.sigma_tab.get_widget(), self.sigma_tab.tab_name)
        self.tab_widget.addTab(self.stations_tab.get_widget(), self.stations_tab.tab_name)
        self.tab_widget.addTab(self.display_tab.get_widget(), self.display_tab.tab_name)
        self.tab_widget.addTab(self.data_tab.get_widget(), self.data_tab.tab_name)
        self.tab_widget.addTab(self.measurements_tab.get_widget(), self.measurements_tab.tab_name)

    def update_sigma(self):
        """Update sigma controls with current scenario values."""
        if hasattr(self, 'sigma_tab') and self.sigma_tab:
            self.sigma_tab.update_sigma()

    def update_all(self):
        """Update all UI components."""
        if hasattr(self, "plot") and self.plot is not None:
            self.plot.update_anchors()
            self.plot.update_plot()
        
        # Update individual tabs
        if hasattr(self, 'stations_tab'):
            self.stations_tab.update()
        if hasattr(self, 'measurements_tab'):
            self.measurements_tab.update()
        
        self.update_sigma()

    def start_periodic_update(self):
        """Start the periodic update timer."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_all)
        #TODO instead of periodically, update when new SSE data received
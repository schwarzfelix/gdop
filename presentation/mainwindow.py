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
    SandboxTab,
    StationsTab,
    DisplayTab,
    DataTab,
    MeasurementsTab
)


class MainWindow(QMainWindow):

    WINDOW_TITLE = "GDOP App"
    FIGURE_DPI = 100
    SIGMA_SLIDER_MAX = 5
    SIGMA_SLIDER_RESOLUTION = 100
    SIGMA_INPUT_STEP = 0.1
    PERIODIC_UPDATE_INTERVAL_MS = 1000

    def __init__(self, gdop_scenario):
        super().__init__()

        self.scenario = gdop_scenario
        self.display_config = presentation.DisplayConfig()
        self.plot = presentation.TrilatPlot(self)

        self.setWindowTitle(MainWindow.WINDOW_TITLE)

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
        self.sandbox_tab = SandboxTab(self)
        self.stations_tab = StationsTab(self)
        self.display_tab = DisplayTab(self)
        self.data_tab = DataTab(self)
        self.measurements_tab = MeasurementsTab(self)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.plot_tab.get_widget(), self.plot_tab.tab_name)
        self.tab_widget.addTab(self.sandbox_tab.get_widget(), self.sandbox_tab.tab_name)
        self.tab_widget.addTab(self.stations_tab.get_widget(), self.stations_tab.tab_name)
        self.tab_widget.addTab(self.display_tab.get_widget(), self.display_tab.tab_name)
        self.tab_widget.addTab(self.data_tab.get_widget(), self.data_tab.tab_name)
        self.tab_widget.addTab(self.measurements_tab.get_widget(), self.measurements_tab.tab_name)

    def update_sandbox(self):
        """Update sandbox controls with current scenario values."""
        # Prefer the new attribute name `sandbox_tab`, but accept the old `sigma_tab` as well
        tab = None
        if hasattr(self, 'sandbox_tab') and self.sandbox_tab:
            tab = self.sandbox_tab
        elif hasattr(self, 'sigma_tab') and self.sigma_tab:
            tab = self.sigma_tab

        if tab:
            if hasattr(tab, 'update_sandbox'):
                tab.update_sandbox()
            elif hasattr(tab, 'update_sigma'):
                tab.update_sigma()
        #TODO remove old sigma_tab support later

    def update_all(self):
        """Update UI components.

        Args:
            anchors (bool): anchor list/positions changed.
            tags (bool): tag positions/estimates changed.
            measurements (bool): measurement relations changed.

        If called without args, a full update is performed (backwards compatible).
        """
        # Backwards compatible signature: allow being called with no args.
        # Consumers may pass named flags when available.
        anchors = True
        tags = True
        measurements = True

        # If caller used the new API, they'll have set temporary attributes
        # on the plot (we use these when called by TrilatPlot._on_refresh_timer).
        if hasattr(self, '_requested_update_flags'):
            flags = self._requested_update_flags
            anchors = flags.get('anchors', True)
            tags = flags.get('tags', True)
            measurements = flags.get('measurements', True)
            # reset after use
            delattr(self, '_requested_update_flags')

        # Plot updates: anchors may require updating artist lists. Prefer
        # the lighter-weight update_data/redraw API when available.
        if hasattr(self, "plot") and self.plot is not None:
            if hasattr(self.plot, 'update_data') and hasattr(self.plot, 'redraw'):
                # Use the newer API
                self.plot.update_data(anchors=anchors, tags=tags, measurements=measurements)
                self.plot.redraw()
            else:
                # Fallback to original API
                if anchors:
                    self.plot.update_anchors()
                if tags or measurements:
                    self.plot.update_plot()

        # Update individual tabs selectively
        if anchors and hasattr(self, 'stations_tab'):
            self.stations_tab.update()
        if measurements and hasattr(self, 'measurements_tab'):
            self.measurements_tab.update()

        # Sandbox (tags controls) depends on tags/measurements
        if (tags or measurements):
            self.update_sandbox()

    def start_periodic_update(self):
        """Start the periodic update timer."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_all)
        # Start the periodic update timer with a conservative default interval.
        # The codebase prefers event-driven updates for streaming, but having
        # a running timer keeps the UI responsive in absence of events.
        self.update_timer.setInterval(MainWindow.PERIODIC_UPDATE_INTERVAL_MS)
        self.update_timer.start()
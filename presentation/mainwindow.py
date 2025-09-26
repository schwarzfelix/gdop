from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from PyQt5.QtWidgets import QSplitter
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy

import presentation
from presentation.tabs import (
    SandboxTab,
    StationsTab,
    DisplayTab,
    DataTab,
    MeasurementsTab,
    ScenariosTab
)


class MainWindow(QMainWindow):

    WINDOW_TITLE = "GDOP App"
    FIGURE_DPI = 100
    SIGMA_SLIDER_MAX = 5
    SIGMA_SLIDER_RESOLUTION = 100
    SIGMA_INPUT_STEP = 0.1

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.scenario = app.scenarios[0] if app.scenarios else None
        self.display_config = presentation.DisplayConfig()
        self.plot = presentation.TrilatPlot(self, self.scenario)
        self.comparison_plot = presentation.ComparisonPlot(self, self.app.scenarios)

        self.plot.anchors_changed.connect(lambda: self.update_all(anchors=True, tags=False, measurements=False))
        self.plot.tags_changed.connect(lambda: self.update_all(anchors=False, tags=True, measurements=False))
        self.plot.measurements_changed.connect(lambda: self.update_all(anchors=False, tags=False, measurements=True))
        self.comparison_plot.anchors_changed.connect(lambda: self.update_all(anchors=True, tags=False, measurements=False))
        self.comparison_plot.tags_changed.connect(lambda: self.update_all(anchors=False, tags=True, measurements=False))
        self.comparison_plot.measurements_changed.connect(lambda: self.update_all(anchors=False, tags=False, measurements=True))

        self.setWindowTitle(MainWindow.WINDOW_TITLE)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        plots_layout = QVBoxLayout()
        left_widget = QWidget()
        left_widget.setLayout(plots_layout)


        # Trilateration plot setup -------------------
        self.figure = self.plot.fig
        self.figure.set_dpi(self.FIGURE_DPI)
        self.canvas = FigureCanvas(self.figure)

        top_widget = QWidget()
        top_layout = QVBoxLayout()
        top_widget.setLayout(top_layout)
        top_layout.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        top_layout.addWidget(self.toolbar)
        # --------------------------------------------

        # Comparison plot setup ----------------------
        self.comp_figure = self.comparison_plot.fig
        self.comp_figure.set_dpi(self.FIGURE_DPI)
        self.comp_canvas = FigureCanvas(self.comp_figure)

        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout()
        bottom_widget.setLayout(bottom_layout)
        bottom_layout.addWidget(self.comp_canvas)

        self.comp_toolbar = NavigationToolbar(self.comp_canvas, self)
        bottom_layout.addWidget(self.comp_toolbar)
        # --------------------------------------------


        self.tab_widget = QTabWidget()
        self.create_tabs()
        self.tab_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        vertical_splitter = QSplitter(Qt.Vertical)
        vertical_splitter.addWidget(top_widget)
        vertical_splitter.addWidget(bottom_widget)
        vertical_splitter.setStretchFactor(0, 3)
        vertical_splitter.setStretchFactor(1, 1)
        plots_layout.addWidget(vertical_splitter)

        horizontal_splitter = QSplitter(Qt.Horizontal)
        horizontal_splitter.addWidget(left_widget)
        horizontal_splitter.addWidget(self.tab_widget)
        horizontal_splitter.setStretchFactor(0, 3)
        horizontal_splitter.setStretchFactor(1, 1)
        main_layout.addWidget(horizontal_splitter)

        sb = self.statusBar()
        sb.showMessage("")

        self.update_all()

    def create_tabs(self):
        """Create all tabs using the new tab classes."""
        # Create tab instances
        self.sandbox_tab = SandboxTab(self)
        self.stations_tab = StationsTab(self)
        self.scenarios_tab = ScenariosTab(self)
        self.display_tab = DisplayTab(self)
        self.data_tab = DataTab(self)
        self.measurements_tab = MeasurementsTab(self)

        # Add tabs to tab widget (no Plot tab — toolbars are shown under each plot)
        self.tab_widget.addTab(self.sandbox_tab.get_widget(), self.sandbox_tab.tab_name)
        self.tab_widget.addTab(self.stations_tab.get_widget(), self.stations_tab.tab_name)
        self.tab_widget.addTab(self.scenarios_tab.get_widget(), self.scenarios_tab.tab_name)
        self.tab_widget.addTab(self.display_tab.get_widget(), self.display_tab.tab_name)
        self.tab_widget.addTab(self.data_tab.get_widget(), self.data_tab.tab_name)
        self.tab_widget.addTab(self.measurements_tab.get_widget(), self.measurements_tab.tab_name)

    def replace_scenario(self, new_scenario):
        self.scenario = new_scenario
        self.update_all()
        self.scenarios_tab.update_scenarios()

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

    def update_all(self, anchors=True, tags=True, measurements=True):
        """Update UI components selectively based on change flags."""
        # Plot updates: anchors may require updating artist lists. Prefer
        # the lighter-weight update_data/redraw API when available.
        if hasattr(self, "plot") and self.plot is not None:
            if hasattr(self.plot, 'update_data') and hasattr(self.plot, 'redraw'):
                # ensure anchor artists (circle_pairs) are created/updated before update_data
                if anchors and hasattr(self.plot, 'update_anchors'):
                    self.plot.update_anchors()
                self.plot.update_data(anchors=anchors, tags=tags, measurements=measurements)
                self.plot.redraw()
            else:
                if anchors:
                    self.plot.update_anchors()
                if tags or measurements:
                    self.plot.update_plot()

        # Update comparison plot (multi-scenario) as well
        if hasattr(self, 'comparison_plot') and self.comparison_plot is not None:
            if hasattr(self.comparison_plot, 'update_data') and hasattr(self.comparison_plot, 'redraw'):
                # comparison plot doesn't need anchors pre-setup but keep API consistent
                self.comparison_plot.update_data(anchors=anchors, tags=tags, measurements=measurements)
                self.comparison_plot.redraw()
            else:
                # best-effort request refresh
                if anchors or tags or measurements:
                    try:
                        self.comparison_plot.request_refresh(anchors=anchors, tags=tags, measurements=measurements)
                    except Exception:
                        pass

        # Update individual tabs selectively
        if anchors and hasattr(self, 'stations_tab'):
            self.stations_tab.update()
        if measurements and hasattr(self, 'measurements_tab'):
            self.measurements_tab.update()

        # Sandbox (tags controls) depends on tags/measurements
        if (tags or measurements):
            self.update_sandbox()

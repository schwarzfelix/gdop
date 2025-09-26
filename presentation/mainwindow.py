from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QSplitter,
    QSizePolicy
)

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)

import presentation
from presentation.tabs import (
    SandboxTab,
    DisplayTab,
    DataTab,
    TreeTab
)


class MainWindow(QMainWindow):

    WINDOW_TITLE = "GDOP App"
    FIGURE_DPI = 100
    SIGMA_SLIDER_MAX = 5
    SIGMA_SLIDER_RESOLUTION = 100
    SIGMA_INPUT_STEP = 0.1

    def __init__(self, gdop_app):
        super().__init__()
        self._gdop_app = gdop_app
        self._scenario = gdop_app.scenarios[0] if gdop_app.scenarios else None
        self._display_config = presentation.DisplayConfig()
        self._trilat_plot = presentation.TrilatPlot(self, self._scenario)
        self._comparison_plot = presentation.ComparisonPlot(self, self._gdop_app.scenarios)

        self.trilat_plot.anchors_changed.connect(lambda: self.update_all(anchors=True, tags=False, measurements=False))
        self.trilat_plot.tags_changed.connect(lambda: self.update_all(anchors=False, tags=True, measurements=False))
        self.trilat_plot.measurements_changed.connect(lambda: self.update_all(anchors=False, tags=False, measurements=True))
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
        self.trilat_figure = self.trilat_plot.fig
        self.trilat_figure.set_dpi(self.FIGURE_DPI)
        self.trilat_canvas = FigureCanvas(self.trilat_figure)

        top_widget = QWidget()
        top_layout = QVBoxLayout()
        top_widget.setLayout(top_layout)
        top_layout.addWidget(self.trilat_canvas)

        self.trilat_toolbar = NavigationToolbar(self.trilat_canvas, self)
        top_layout.addWidget(self.trilat_toolbar)
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
        vertical_splitter.setStretchFactor(0, 1)
        vertical_splitter.setStretchFactor(1, 1)
        plots_layout.addWidget(vertical_splitter)

        horizontal_splitter = QSplitter(Qt.Horizontal)
        horizontal_splitter.addWidget(left_widget)
        horizontal_splitter.addWidget(self.tab_widget)
        horizontal_splitter.setStretchFactor(0, 1)
        horizontal_splitter.setStretchFactor(1, 1)
        main_layout.addWidget(horizontal_splitter)

        status_bar = self.statusBar()
        status_bar.showMessage("")

        self.update_all()

    def create_tabs(self):
        self.tree_tab = TreeTab(self)
        self.display_tab = DisplayTab(self)
        self.data_tab = DataTab(self)
        self.sandbox_tab = SandboxTab(self)

        self.tab_widget.addTab(self.tree_tab.get_widget(), self.tree_tab.tab_name)
        self.tab_widget.addTab(self.display_tab.get_widget(), self.display_tab.tab_name)
        self.tab_widget.addTab(self.data_tab.get_widget(), self.data_tab.tab_name)
        self.tab_widget.addTab(self.sandbox_tab.get_widget(), self.sandbox_tab.tab_name)

    def update_all(self, anchors=True, tags=True, measurements=True):
        if anchors:
            self.trilat_plot.update_anchors()
            self.tree_tab.update()
        
        if (tags or measurements):
            self.sandbox_tab.update_sandbox()
            self.tree_tab.update()

        self.trilat_plot.update_data(anchors=anchors, tags=tags, measurements=measurements)
        self.trilat_plot.redraw()

        self.comparison_plot.update_data(anchors=anchors, tags=tags, measurements=measurements)
        self.comparison_plot.redraw()


    @property
    #TODO rename to trilat_plot after streamlining all references
    def app(self):
        return self._gdop_app

    @property
    def scenario(self):
        return self._scenario

    @property
    def display_config(self):
        return self._display_config

    @property
    def trilat_plot(self):
        return self._trilat_plot

    @property
    def comparison_plot(self):
        return self._comparison_plot

from itertools import combinations

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QLineEdit,
    QMainWindow,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
)
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)

import presentation
from simulation import geometry


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

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.slider = QSlider(Qt.Horizontal)
        self.sigma_input = QDoubleSpinBox()

        self.tab_widget = QTabWidget()
        self.create_plot_tab()
        self.create_sigma_tab()
        self.create_stations_tab()
        self.create_display_tab()
        self.create_streaming_tab()
        self.create_measurements_tab()
        layout.addWidget(self.tab_widget)

        self.start_periodic_update()
        self.update_all()

    def create_plot_tab(self):
        self.tab_widget.addTab(self.toolbar, "Plot")

    def create_sigma_tab(self):

        inside_tab_widget = QWidget()
        inside_tab_layout = QVBoxLayout()
        inside_tab_widget.setLayout(inside_tab_layout)

        self.slider.setMinimum(0)
        self.slider.setMaximum(self.SIGMA_SLIDER_MAX * self.SIGMA_SLIDER_RESOLUTION)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.slider_changed)
        inside_tab_layout.addWidget(self.slider)

        self.sigma_input.setMinimum(0.0)
        self.sigma_input.setSingleStep(0.1)
        self.sigma_input.setValue(0.0)
        self.sigma_input.valueChanged.connect(self.sigma_input_changed)
        inside_tab_layout.addWidget(self.sigma_input)

        self.tab_widget.addTab(inside_tab_widget, "Sigma")

    def create_stations_tab(self):
        self.stations_tree = QTreeWidget()
        self.stations_tree.setHeaderHidden(True)
        self.update_stations_tree()
        self.tab_widget.addTab(self.stations_tree, "Stations")

    def create_display_tab(self):
        self.display_tree = QTreeWidget()
        self.display_tree.setHeaderHidden(True)

        anchor_node = QTreeWidgetItem(self.display_tree, ["Anchor"])
        self.anchor_circles_checkbox = QCheckBox("Show Anchor Circles")
        self.anchor_circles_checkbox.setChecked(self.display_config.showAnchorCircles)
        self.anchor_circles_checkbox.stateChanged.connect(self.update_display_config)
        self.anchor_circles_item = QTreeWidgetItem(anchor_node)
        self.display_tree.setItemWidget(self.anchor_circles_item, 0, self.anchor_circles_checkbox)

        self.anchor_labels_checkbox = QCheckBox("Show Anchor Labels")
        self.anchor_labels_checkbox.setChecked(self.display_config.showAnchorLabels)
        self.anchor_labels_checkbox.stateChanged.connect(self.update_display_config)
        anchor_labels_item = QTreeWidgetItem(anchor_node)
        self.display_tree.setItemWidget(anchor_labels_item, 0, self.anchor_labels_checkbox)

        between_anchors_node = QTreeWidgetItem(self.display_tree, ["Between Anchors"])
        self.between_anchors_lines_checkbox = QCheckBox("Show Lines Between Anchors")
        self.between_anchors_lines_checkbox.setChecked(self.display_config.showBetweenAnchorsLines)
        self.between_anchors_lines_checkbox.stateChanged.connect(self.update_display_config)
        between_anchors_lines_item = QTreeWidgetItem(between_anchors_node)
        self.display_tree.setItemWidget(between_anchors_lines_item, 0, self.between_anchors_lines_checkbox)

        self.between_anchors_labels_checkbox = QCheckBox("Show Labels Between Anchors")
        self.between_anchors_labels_checkbox.setChecked(self.display_config.showBetweenAnchorsLabels)
        self.between_anchors_labels_checkbox.stateChanged.connect(self.update_display_config)
        between_anchors_labels_item = QTreeWidgetItem(between_anchors_node)
        self.display_tree.setItemWidget(between_anchors_labels_item, 0, self.between_anchors_labels_checkbox)

        tag_anchor_node = QTreeWidgetItem(self.display_tree, ["Tag and Anchors"])
        self.tag_anchor_lines_checkbox = QCheckBox("Show Lines Between Tag and Anchors")
        self.tag_anchor_lines_checkbox.setChecked(self.display_config.showTagAnchorLines)
        self.tag_anchor_lines_checkbox.stateChanged.connect(self.update_display_config)
        tag_anchor_lines_item = QTreeWidgetItem(tag_anchor_node)
        self.display_tree.setItemWidget(tag_anchor_lines_item, 0, self.tag_anchor_lines_checkbox)

        self.tag_anchor_labels_checkbox = QCheckBox("Show Labels Between Tag and Anchors")
        self.tag_anchor_labels_checkbox.setChecked(self.display_config.showTagAnchorLabels)
        self.tag_anchor_labels_checkbox.stateChanged.connect(self.update_display_config)
        tag_anchor_labels_item = QTreeWidgetItem(tag_anchor_node)
        self.display_tree.setItemWidget(tag_anchor_labels_item, 0, self.tag_anchor_labels_checkbox)

        interaction_node = QTreeWidgetItem(self.display_tree, ["Interaction"])
        self.right_click_anchors_checkbox = QCheckBox("Enable Right-Click Anchor Control")
        self.right_click_anchors_checkbox.setChecked(self.display_config.rightClickAnchors)
        self.right_click_anchors_checkbox.stateChanged.connect(self.update_display_config)
        right_click_anchors_item = QTreeWidgetItem(interaction_node)
        self.display_tree.setItemWidget(right_click_anchors_item, 0, self.right_click_anchors_checkbox)

        self.gdop_checkbox = QCheckBox("Show GDOP Calculation")
        self.gdop_checkbox.setChecked(self.display_config.showGDOP)
        self.gdop_checkbox.stateChanged.connect(self.update_display_config)
        gdop_checkbox_item = QTreeWidgetItem(interaction_node)
        self.display_tree.setItemWidget(gdop_checkbox_item, 0, self.gdop_checkbox)

        tag_labels_checkbox = QCheckBox("Show Tag Labels")
        tag_labels_checkbox.setChecked(self.display_config.showTagLabels)
        tag_labels_checkbox.stateChanged.connect(self.update_display_config)
        tag_labels_item = QTreeWidgetItem(tag_anchor_node)
        self.display_tree.setItemWidget(tag_labels_item, 0, tag_labels_checkbox)
        self.tag_labels_checkbox = tag_labels_checkbox  # Save reference

        self.tab_widget.addTab(self.display_tree, "Display")

    def create_streaming_tab(self):
        self.streaming_tree = QTreeWidget()
        self.streaming_tree.setHeaderHidden(True)

        root_node = QTreeWidgetItem(self.streaming_tree)
        self.stream_enabled_checkbox = QCheckBox("Stream Measurements")
        self.stream_enabled_checkbox.setChecked(False)
        self.stream_enabled_checkbox.stateChanged.connect(self.update_streaming_config)
        self.streaming_tree.setItemWidget(root_node, 0, self.stream_enabled_checkbox)

        url_node = QTreeWidgetItem(self.streaming_tree)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter SSE URL")
        self.streaming_tree.setItemWidget(url_node, 0, self.url_input)

        periodic_node = QTreeWidgetItem(self.streaming_tree)
        self.periodic_update_checkbox = QCheckBox("Enable Periodic Update")
        self.periodic_update_checkbox.setChecked(False)
        self.periodic_update_checkbox.stateChanged.connect(self.update_periodic_config)
        self.streaming_tree.setItemWidget(periodic_node, 0, self.periodic_update_checkbox)

        interval_node = QTreeWidgetItem(self.streaming_tree)
        self.interval_input = QSpinBox()
        self.interval_input.setRange(100, 10000)
        self.interval_input.setValue(2000)
        self.interval_input.setSuffix(" ms")
        self.interval_input.valueChanged.connect(self.update_periodic_interval)
        self.streaming_tree.setItemWidget(interval_node, 0, self.interval_input)

        self.tab_widget.addTab(self.streaming_tree, "Streaming")

    def create_measurements_tab(self):
        self.measurements_tree = QTreeWidget()
        self.measurements_tree.setHeaderHidden(True)
        self.update_measurements_tree()
        self.tab_widget.addTab(self.measurements_tree, "Measurements")

    def update_measurements_tree(self):
        self.measurements_tree.clear()

        for pair, distance in self.scenario.measurements.relation.items():
            station1, station2 = pair
            measurement_item = QTreeWidgetItem(
                self.measurements_tree,
                [f"{station1.name()} ↔ {station2.name()}: {distance:.2f}"]
            )

    def update_streaming_config(self):
        is_enabled = self.stream_enabled_checkbox.isChecked()
        if is_enabled:
            url = self.url_input.text().strip()
            if url:
                self.scenario.start_streaming(url)
            else:
                self.stream_enabled_checkbox.setChecked(False)
                print("Please enter a valid SSE URL.")
        else:
            self.scenario.stop_streaming()
            print("Streaming stopped.")

    def update_display_config(self):
        self.display_config.showAnchorCircles = self.anchor_circles_checkbox.isChecked()
        self.display_config.showAnchorLabels = self.anchor_labels_checkbox.isChecked()
        self.display_config.showBetweenAnchorsLines = self.between_anchors_lines_checkbox.isChecked()
        self.display_config.showBetweenAnchorsLabels = self.between_anchors_labels_checkbox.isChecked()
        self.display_config.showTagAnchorLines = self.tag_anchor_lines_checkbox.isChecked()
        self.display_config.showTagAnchorLabels = self.tag_anchor_labels_checkbox.isChecked()

        self.display_config.rightClickAnchors = self.right_click_anchors_checkbox.isChecked()
        self.display_config.showGDOP = self.gdop_checkbox.isChecked()
        self.display_config.showTagLabels = self.tag_labels_checkbox.isChecked()

        self.update_all()

    def slider_changed(self):
        self.scenario.sigma = self.slider.value() / self.SIGMA_SLIDER_RESOLUTION
        self.update_all()

    def sigma_input_changed(self):
        self.scenario.sigma = self.sigma_input.value()
        self.update_all()

    def update_stations_tree(self):
        self.stations_tree.clear()

        all_stations = self.scenario.stations
        station_positions = {station: station.position() for station in all_stations}

        for station in all_stations:
            station_node = QTreeWidgetItem(self.stations_tree)

            station_widget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)

            name_label = QLabel(station.name())
            rename_button = QPushButton("✎")
            rename_button.setToolTip("Rename station")
            rename_button.clicked.connect(lambda checked, s=station: self.rename_station_dialog(s))

            delete_button = QPushButton("␡")
            delete_button.setToolTip("Delete station")
            delete_button.clicked.connect(lambda checked, s=station: self.delete_station(s))

            layout.addWidget(delete_button)
            layout.addWidget(rename_button)
            layout.addWidget(name_label)
            layout.addStretch()
            station_widget.setLayout(layout)

            self.stations_tree.setItemWidget(station_node, 0, station_widget)

            other_stations = [
                (other_station.name(), station_positions[other_station])
                for other_station in all_stations if other_station != station
            ]

            #TODO fix angle calculation, (list/vecor operations not supported)
            #for (name1, pos1), (name2, pos2) in combinations(other_stations, 2):
            #    angle = geometry.angle_vectors(
            #        pos1 - station_positions[station],
            #        pos2 - station_positions[station]
            #    )
            #    QTreeWidgetItem(
            #        station_node,
            #        [f"Angle between {name1} and {name2}: {angle:.2f}°"]
            #    )

    def rename_station_dialog(self, station):
        from PyQt5.QtWidgets import QInputDialog
        current_name = station.name()
        new_name, ok = QInputDialog.getText(self, "Rename Station", f"Enter new name for station '{current_name}':", text=current_name)
        if ok and new_name and new_name != current_name:
            self.rename_station(station, new_name)

    def rename_station(self, station, new_name):
        # Try to set the name attribute if possible
        if hasattr(station, '_name'):
            station._name = new_name
        elif hasattr(station, 'name') and callable(getattr(station, 'name', None)):
            try:
                station.name = lambda: new_name
            except Exception:
                pass
        self.update_all()

    def delete_station(self, station):
        self.scenario.remove_station(station)
        self.update_all()

    def update_sigma(self):
        self.slider.setValue(int(self.scenario.sigma * self.SIGMA_SLIDER_RESOLUTION))
        self.sigma_input.setValue(self.scenario.sigma)

    def update_all(self):
        if hasattr(self, "plot") and self.plot is not None:
            self.plot.update_anchors()
            self.plot.update_plot()
        self.update_stations_tree()
        self.update_measurements_tree()
        self.update_sigma()

    def start_periodic_update(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_all)
        #TODO instead of periodically, update when new SSE data received

    def update_periodic_config(self):
        is_enabled = self.periodic_update_checkbox.isChecked()
        if is_enabled:
            self.update_timer.start(self.interval_input.value())
        else:
            self.update_timer.stop()

    def update_periodic_interval(self):
        if self.periodic_update_checkbox.isChecked():
            self.update_timer.setInterval(self.interval_input.value())
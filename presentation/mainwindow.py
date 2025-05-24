from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTextEdit, QDoubleSpinBox, QTabWidget
from PyQt5.QtWidgets import QSlider, QCheckBox, QTreeWidgetItem, QTreeWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLineEdit, QDoubleSpinBox, QTabWidget

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)

import presentation
from simulation import geometry
from itertools import combinations

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
        self.create_angles_tab()
        self.create_display_tab()
        self.create_streaming_tab()
        layout.addWidget(self.tab_widget)

        self.start_periodic_update()

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

    def create_angles_tab(self):
        self.angles_tree = QTreeWidget()
        self.angles_tree.setHeaderHidden(True)
        self.update_angles_tree()
        self.tab_widget.addTab(self.angles_tree, "Angles")

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

        self.tab_widget.addTab(self.streaming_tree, "Streaming")

        self.tab_widget.addTab(self.streaming_tree, "Streaming")

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

        self.update_all()

    def slider_changed(self):
        self.scenario.sigma = self.slider.value() / self.SIGMA_SLIDER_RESOLUTION
        self.update_all()

    def sigma_input_changed(self):
        self.scenario.sigma = self.sigma_input.value()
        self.update_all()

    def update_angles_tree(self):
        self.angles_tree.clear()

        anchor_positions = self.scenario.anchor_positions()
        tag_position = self.scenario.tag_truth.position()

        for i, anchor in enumerate(self.scenario.get_anchor_list()):
            anchor_node = QTreeWidgetItem(self.angles_tree, [anchor.name()])
            other_stations = [
                (self.scenario.get_anchor_list()[j].name(), anchor_positions[j])
                for j in range(len(self.scenario.get_anchor_list())) if j != i
            ]
            other_stations.append(("Tag", tag_position))

            for (name1, pos1), (name2, pos2) in combinations(other_stations, 2):
                angle = geometry.angle_vectors(pos1 - anchor_positions[i], pos2 - anchor_positions[i])
                QTreeWidgetItem(anchor_node, [f"Angle between {name1} and {name2}: {angle:.2f}°"])

        tag_node = QTreeWidgetItem(self.angles_tree, ["Tag"])
        other_stations = [
            (anchor.name(), anchor_positions[i])
            for i, anchor in enumerate(self.scenario.get_anchor_list())
        ]

        for (name1, pos1), (name2, pos2) in combinations(other_stations, 2):
            angle = geometry.angle_vectors(pos1 - tag_position, pos2 - tag_position)
            QTreeWidgetItem(tag_node, [f"Angle between {name1} and {name2}: {angle:.2f}°"])

    def update_sigma(self):
        self.slider.setValue(int(self.scenario.sigma * self.SIGMA_SLIDER_RESOLUTION))
        self.sigma_input.setValue(self.scenario.sigma)

    def update_all(self):
        self.plot.update_plot()
        self.update_angles_tree()
        self.update_sigma()

    def start_periodic_update(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_all)
        self.update_timer.start(2000)
        #TODO add switch to turn on/off periodic update

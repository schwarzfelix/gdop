from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTextEdit, QDoubleSpinBox, QTabWidget
from PyQt5.QtWidgets import QSlider, QCheckBox, QTreeWidgetItem, QTreeWidget
from PyQt5.QtCore import Qt

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
        layout.addWidget(self.tab_widget)

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
        self.angle_text = QTextEdit()
        self.angle_text.setReadOnly(True)
        self.angle_text.setText("Angles will be displayed here.")
        self.tab_widget.addTab(self.angle_text, "Angles")

    def create_display_tab(self):
        display_tab_widget = QWidget()
        display_tab_layout = QVBoxLayout()
        display_tab_widget.setLayout(display_tab_layout)

        display_tab_widget = QWidget()
        display_tab_layout = QVBoxLayout()
        display_tab_widget.setLayout(display_tab_layout)

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

        display_tab_layout.addWidget(self.display_tree)
        self.tab_widget.addTab(display_tab_widget, "Display")

    def update_display_config(self):
        self.display_config.showAnchorCircles = self.anchor_circles_checkbox.isChecked()
        self.display_config.showAnchorLabels = self.anchor_labels_checkbox.isChecked()
        self.display_config.showBetweenAnchorsLines = self.between_anchors_lines_checkbox.isChecked()
        self.display_config.showBetweenAnchorsLabels = self.between_anchors_labels_checkbox.isChecked()
        self.display_config.showTagAnchorLines = self.tag_anchor_lines_checkbox.isChecked()
        self.display_config.showTagAnchorLabels = self.tag_anchor_labels_checkbox.isChecked()

        self.update_all()

    def slider_changed(self):
        self.scenario.sigma = self.slider.value() / self.SIGMA_SLIDER_RESOLUTION
        self.update_all()

    def sigma_input_changed(self):
        self.scenario.sigma = self.sigma_input.value()
        self.update_all()

    def update_angles(self):
        angles_text = ""
        anchor_positions = self.scenario.anchor_positions()
        for (i, j) in combinations(range(len(anchor_positions)), 2):
            angle = geometry.angle_vectors(
                anchor_positions[i] - self.scenario.tag_truth.position(),
                anchor_positions[j] - self.scenario.tag_truth.position()
            )
            angles_text += f"Angle between {self.scenario.anchors[i].name()} and {self.scenario.anchors[j].name()}: {angle:.2f}°\n"
        self.angle_text.setText(angles_text)

    def update_sigma(self):
        self.slider.setValue(int(self.scenario.sigma * self.SIGMA_SLIDER_RESOLUTION))
        self.sigma_input.setValue(self.scenario.sigma)

    def update_all(self):
        self.plot.update_plot()
        self.update_angles()
        self.update_sigma()

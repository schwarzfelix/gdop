"""
Display tab for the GDOP application.
"""

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QCheckBox, QComboBox, QLabel, QHBoxLayout, QWidget
from .base_tab import BaseTab


class DisplayTab(BaseTab):
    """Tab for display configuration options."""
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.display_tree = None
        # Store references to checkboxes for later access
        self.anchor_circles_checkbox = None
        self.anchor_names_checkbox = None
        self.anchor_coordinates_checkbox = None
        self.between_anchors_lines_checkbox = None
        self.between_anchors_labels_checkbox = None
        self.tag_anchor_lines_checkbox = None
        self.tag_anchor_labels_checkbox = None
        self.right_click_anchors_checkbox = None
        self.tag_names_checkbox = None
        self.tag_coordinates_checkbox = None
        self.drag_anchors_checkbox = None
        self.show_anchors_checkbox = None
        self.show_tag_truth_checkbox = None
        self.show_tag_truth_labels_checkbox = None
        self.show_tags_checkbox = None
        self.show_trilat_plot_checkbox = None
        self.show_comparison_plot_checkbox = None
        self.show_border_rectangle_checkbox = None
        self.use_border_rectangle_for_viewport_checkbox = None
        self.show_position_error_lines_checkbox = None
        self.show_legend_anchors_checkbox = None
        self.show_legend_tags_checkbox = None
        self.show_legend_tag_truth_checkbox = None
        self.show_legend_border_checkbox = None
        self.show_line_point_values_checkbox = None
        self.aggregation_method_combo = None
        self.trilateration_method_combo = None
    
    @property
    def tab_name(self):
        return "Display"
        
    def create_widget(self):
        """Create and return the display tab widget."""
        self.display_tree = QTreeWidget()
        self.display_tree.setHeaderHidden(True)

        # Anchors section
        anchors_node = QTreeWidgetItem(self.display_tree, ["Anchors"])
        self.show_anchors_checkbox = QCheckBox("Show Anchors")
        self.show_anchors_checkbox.setChecked(self.display_config.showAnchors)
        self.show_anchors_checkbox.stateChanged.connect(self.update_display_config)
        show_anchors_item = QTreeWidgetItem(anchors_node)
        self.display_tree.setItemWidget(show_anchors_item, 0, self.show_anchors_checkbox)
        anchors_node.setExpanded(True)

        self.anchor_circles_checkbox = QCheckBox("Show Anchor Circles")
        self.anchor_circles_checkbox.setChecked(self.display_config.showAnchorCircles)
        self.anchor_circles_checkbox.stateChanged.connect(self.update_display_config)
        anchor_circles_item = QTreeWidgetItem(anchors_node)
        self.display_tree.setItemWidget(anchor_circles_item, 0, self.anchor_circles_checkbox)

        self.anchor_names_checkbox = QCheckBox("Show Anchor Names")
        self.anchor_names_checkbox.setChecked(self.display_config.showAnchorNames)
        self.anchor_names_checkbox.stateChanged.connect(self.update_display_config)
        anchor_names_item = QTreeWidgetItem(anchors_node)
        self.display_tree.setItemWidget(anchor_names_item, 0, self.anchor_names_checkbox)

        self.anchor_coordinates_checkbox = QCheckBox("Show Anchor Coordinates")
        self.anchor_coordinates_checkbox.setChecked(self.display_config.showAnchorCoordinates)
        self.anchor_coordinates_checkbox.stateChanged.connect(self.update_display_config)
        anchor_coordinates_item = QTreeWidgetItem(anchors_node)
        self.display_tree.setItemWidget(anchor_coordinates_item, 0, self.anchor_coordinates_checkbox)

        # Tags section
        tags_node = QTreeWidgetItem(self.display_tree, ["Tags"])
        self.show_tag_truth_checkbox = QCheckBox("Show Tag Truth")
        self.show_tag_truth_checkbox.setChecked(self.display_config.showTagTruth)
        self.show_tag_truth_checkbox.stateChanged.connect(self.update_display_config)
        show_tag_truth_item = QTreeWidgetItem(tags_node)
        self.display_tree.setItemWidget(show_tag_truth_item, 0, self.show_tag_truth_checkbox)
        tags_node.setExpanded(True)

        self.show_tag_truth_labels_checkbox = QCheckBox("Show Tag Truth Labels")
        self.show_tag_truth_labels_checkbox.setChecked(self.display_config.showTagTruthLabels)
        self.show_tag_truth_labels_checkbox.stateChanged.connect(self.update_display_config)
        show_tag_truth_labels_item = QTreeWidgetItem(tags_node)
        self.display_tree.setItemWidget(show_tag_truth_labels_item, 0, self.show_tag_truth_labels_checkbox)

        self.show_tags_checkbox = QCheckBox("Show Tags")
        self.show_tags_checkbox.setChecked(self.display_config.showTags)
        self.show_tags_checkbox.stateChanged.connect(self.update_display_config)
        show_tags_item = QTreeWidgetItem(tags_node)
        self.display_tree.setItemWidget(show_tags_item, 0, self.show_tags_checkbox)

        self.tag_names_checkbox = QCheckBox("Show Tag Names")
        self.tag_names_checkbox.setChecked(self.display_config.showTagNames)
        self.tag_names_checkbox.stateChanged.connect(self.update_display_config)
        tag_names_item = QTreeWidgetItem(tags_node)
        self.display_tree.setItemWidget(tag_names_item, 0, self.tag_names_checkbox)

        self.tag_coordinates_checkbox = QCheckBox("Show Tag Coordinates")
        self.tag_coordinates_checkbox.setChecked(self.display_config.showTagCoordinates)
        self.tag_coordinates_checkbox.stateChanged.connect(self.update_display_config)
        tag_coordinates_item = QTreeWidgetItem(tags_node)
        self.display_tree.setItemWidget(tag_coordinates_item, 0, self.tag_coordinates_checkbox)

        self.show_position_error_lines_checkbox = QCheckBox("Show Position Error Lines")
        self.show_position_error_lines_checkbox.setChecked(self.display_config.showPositionErrorLines)
        self.show_position_error_lines_checkbox.stateChanged.connect(self.update_display_config)
        show_position_error_lines_item = QTreeWidgetItem(tags_node)
        self.display_tree.setItemWidget(show_position_error_lines_item, 0, self.show_position_error_lines_checkbox)

        # Between Anchors and Tags section
        between_anchors_tags_node = QTreeWidgetItem(self.display_tree, ["Between Anchors and Tags"])
        self.tag_anchor_lines_checkbox = QCheckBox("Show Lines Between Tag and Anchors")
        self.tag_anchor_lines_checkbox.setChecked(self.display_config.showTagAnchorLines)
        self.tag_anchor_lines_checkbox.stateChanged.connect(self.update_display_config)
        tag_anchor_lines_item = QTreeWidgetItem(between_anchors_tags_node)
        self.display_tree.setItemWidget(tag_anchor_lines_item, 0, self.tag_anchor_lines_checkbox)
        between_anchors_tags_node.setExpanded(True)

        self.tag_anchor_labels_checkbox = QCheckBox("Show Labels Between Tag and Anchors")
        self.tag_anchor_labels_checkbox.setChecked(self.display_config.showTagAnchorLabels)
        self.tag_anchor_labels_checkbox.stateChanged.connect(self.update_display_config)
        tag_anchor_labels_item = QTreeWidgetItem(between_anchors_tags_node)
        self.display_tree.setItemWidget(tag_anchor_labels_item, 0, self.tag_anchor_labels_checkbox)

        # Between Anchors section
        between_anchors_node = QTreeWidgetItem(self.display_tree, ["Between Anchors"])
        self.between_anchors_lines_checkbox = QCheckBox("Show Lines Between Anchors")
        self.between_anchors_lines_checkbox.setChecked(self.display_config.showBetweenAnchorsLines)
        self.between_anchors_lines_checkbox.stateChanged.connect(self.update_display_config)
        between_anchors_lines_item = QTreeWidgetItem(between_anchors_node)
        self.display_tree.setItemWidget(between_anchors_lines_item, 0, self.between_anchors_lines_checkbox)
        between_anchors_node.setExpanded(True)

        self.between_anchors_labels_checkbox = QCheckBox("Show Labels Between Anchors")
        self.between_anchors_labels_checkbox.setChecked(self.display_config.showBetweenAnchorsLabels)
        self.between_anchors_labels_checkbox.stateChanged.connect(self.update_display_config)
        between_anchors_labels_item = QTreeWidgetItem(between_anchors_node)
        self.display_tree.setItemWidget(between_anchors_labels_item, 0, self.between_anchors_labels_checkbox)

        # Interaction section
        interaction_node = QTreeWidgetItem(self.display_tree, ["Interaction"])
        self.right_click_anchors_checkbox = QCheckBox("Enable Right-Click Anchor Control")
        self.right_click_anchors_checkbox.setChecked(self.display_config.rightClickAnchors)
        self.right_click_anchors_checkbox.stateChanged.connect(self.update_display_config)
        right_click_anchors_item = QTreeWidgetItem(interaction_node)
        self.display_tree.setItemWidget(right_click_anchors_item, 0, self.right_click_anchors_checkbox)
        interaction_node.setExpanded(True)

        self.drag_anchors_checkbox = QCheckBox("Enable Dragging Anchors")
        self.drag_anchors_checkbox.setChecked(self.display_config.dragAnchors)
        self.drag_anchors_checkbox.stateChanged.connect(self.update_display_config)
        drag_anchors_item = QTreeWidgetItem(interaction_node)
        self.display_tree.setItemWidget(drag_anchors_item, 0, self.drag_anchors_checkbox)

        # Plots section
        plots_node = QTreeWidgetItem(self.display_tree, ["Plots"])
        self.show_trilat_plot_checkbox = QCheckBox("Show Trilateration Plot")
        self.show_trilat_plot_checkbox.setChecked(self.display_config.showTrilatPlot)
        self.show_trilat_plot_checkbox.stateChanged.connect(self.update_display_config)
        show_trilat_plot_item = QTreeWidgetItem(plots_node)
        self.display_tree.setItemWidget(show_trilat_plot_item, 0, self.show_trilat_plot_checkbox)
        plots_node.setExpanded(True)

        self.show_comparison_plot_checkbox = QCheckBox("Show Comparison Plot")
        self.show_comparison_plot_checkbox.setChecked(self.display_config.showComparisonPlot)
        self.show_comparison_plot_checkbox.stateChanged.connect(self.update_display_config)
        show_comparison_plot_item = QTreeWidgetItem(plots_node)
        self.display_tree.setItemWidget(show_comparison_plot_item, 0, self.show_comparison_plot_checkbox)

        self.show_border_rectangle_checkbox = QCheckBox("Show Border Rectangle")
        self.show_border_rectangle_checkbox.setChecked(self.display_config.showBorderRectangle)
        self.show_border_rectangle_checkbox.stateChanged.connect(self.update_display_config)
        show_border_rectangle_item = QTreeWidgetItem(plots_node)
        self.display_tree.setItemWidget(show_border_rectangle_item, 0, self.show_border_rectangle_checkbox)

        self.use_border_rectangle_for_viewport_checkbox = QCheckBox("Use Border Rectangle for Viewport")
        self.use_border_rectangle_for_viewport_checkbox.setChecked(self.display_config.useBorderRectangleForViewport)
        self.use_border_rectangle_for_viewport_checkbox.stateChanged.connect(self.update_display_config)
        use_border_rectangle_for_viewport_item = QTreeWidgetItem(plots_node)
        self.display_tree.setItemWidget(use_border_rectangle_for_viewport_item, 0, self.use_border_rectangle_for_viewport_checkbox)

        # Legend Elements section
        legend_elements_node = QTreeWidgetItem(self.display_tree, ["Legend Elements"])
        self.show_legend_anchors_checkbox = QCheckBox("Show Anchors in Legend")
        self.show_legend_anchors_checkbox.setChecked(self.display_config.showLegendAnchors)
        self.show_legend_anchors_checkbox.stateChanged.connect(self.update_display_config)
        show_legend_anchors_item = QTreeWidgetItem(legend_elements_node)
        self.display_tree.setItemWidget(show_legend_anchors_item, 0, self.show_legend_anchors_checkbox)
        legend_elements_node.setExpanded(True)

        self.show_legend_tags_checkbox = QCheckBox("Show Tags in Legend")
        self.show_legend_tags_checkbox.setChecked(self.display_config.showLegendTags)
        self.show_legend_tags_checkbox.stateChanged.connect(self.update_display_config)
        show_legend_tags_item = QTreeWidgetItem(legend_elements_node)
        self.display_tree.setItemWidget(show_legend_tags_item, 0, self.show_legend_tags_checkbox)

        self.show_legend_tag_truth_checkbox = QCheckBox("Show Tag Truth in Legend")
        self.show_legend_tag_truth_checkbox.setChecked(self.display_config.showLegendTagTruth)
        self.show_legend_tag_truth_checkbox.stateChanged.connect(self.update_display_config)
        show_legend_tag_truth_item = QTreeWidgetItem(legend_elements_node)
        self.display_tree.setItemWidget(show_legend_tag_truth_item, 0, self.show_legend_tag_truth_checkbox)

        self.show_legend_border_checkbox = QCheckBox("Show Border in Legend")
        self.show_legend_border_checkbox.setChecked(self.display_config.showLegendBorder)
        self.show_legend_border_checkbox.stateChanged.connect(self.update_display_config)
        show_legend_border_item = QTreeWidgetItem(legend_elements_node)
        self.display_tree.setItemWidget(show_legend_border_item, 0, self.show_legend_border_checkbox)

        # Line Plot Options section
        line_plot_options_node = QTreeWidgetItem(self.display_tree, ["Line Plot Options"])
        self.show_line_point_values_checkbox = QCheckBox("Show Values at Points")
        self.show_line_point_values_checkbox.setChecked(self.display_config.showLinePointValues)
        self.show_line_point_values_checkbox.stateChanged.connect(self.update_display_config)
        show_line_point_values_item = QTreeWidgetItem(line_plot_options_node)
        self.display_tree.setItemWidget(show_line_point_values_item, 0, self.show_line_point_values_checkbox)
        line_plot_options_node.setExpanded(True)

        # Import Options section
        import_options_node = QTreeWidgetItem(self.display_tree, ["Import Options"])
        import_options_node.setExpanded(True)
        
        # Create a widget with label and combo box for aggregation method
        aggregation_method_widget = QWidget()
        aggregation_method_layout = QHBoxLayout(aggregation_method_widget)
        aggregation_method_layout.setContentsMargins(0, 0, 0, 0)
        
        aggregation_method_label = QLabel("Aggregation Method:")
        aggregation_method_layout.addWidget(aggregation_method_label)
        
        self.aggregation_method_combo = QComboBox()
        self.aggregation_method_combo.addItems(["ask", "newest", "lowest", "mean", "median"])
        # Set current selection
        current_method = self.display_config.aggregationMethod
        index = self.aggregation_method_combo.findText(current_method)
        if index >= 0:
            self.aggregation_method_combo.setCurrentIndex(index)
        self.aggregation_method_combo.currentTextChanged.connect(self.update_aggregation_method)
        aggregation_method_layout.addWidget(self.aggregation_method_combo)
        
        aggregation_method_item = QTreeWidgetItem(import_options_node)
        self.display_tree.setItemWidget(aggregation_method_item, 0, aggregation_method_widget)

        # Trilateration Options section
        trilateration_options_node = QTreeWidgetItem(self.display_tree, ["Trilateration Options"])
        trilateration_options_node.setExpanded(True)
        
        # Create a widget with label and combo box
        trilateration_method_widget = QWidget()
        trilateration_method_layout = QHBoxLayout(trilateration_method_widget)
        trilateration_method_layout.setContentsMargins(0, 0, 0, 0)
        
        trilateration_method_label = QLabel("Method:")
        trilateration_method_layout.addWidget(trilateration_method_label)
        
        self.trilateration_method_combo = QComboBox()
        self.trilateration_method_combo.addItems(["ask", "classical", "best_subset", "nonlinear"])
        # Set current selection
        current_method = self.display_config.trilaterationMethod
        index = self.trilateration_method_combo.findText(current_method)
        if index >= 0:
            self.trilateration_method_combo.setCurrentIndex(index)
        self.trilateration_method_combo.currentTextChanged.connect(self.update_trilateration_method)
        trilateration_method_layout.addWidget(self.trilateration_method_combo)
        
        trilateration_method_item = QTreeWidgetItem(trilateration_options_node)
        self.display_tree.setItemWidget(trilateration_method_item, 0, trilateration_method_widget)

        return self.display_tree

    def update_display_config(self):
        """Update display configuration based on checkbox states."""
        # Anchors
        self.display_config.showAnchors = self.show_anchors_checkbox.isChecked()
        self.display_config.showAnchorCircles = self.anchor_circles_checkbox.isChecked()
        self.display_config.showAnchorNames = self.anchor_names_checkbox.isChecked()
        self.display_config.showAnchorCoordinates = self.anchor_coordinates_checkbox.isChecked()

        # Tags
        self.display_config.showTagTruth = self.show_tag_truth_checkbox.isChecked()
        self.display_config.showTagTruthLabels = self.show_tag_truth_labels_checkbox.isChecked()
        self.display_config.showTags = self.show_tags_checkbox.isChecked()
        self.display_config.showPositionErrorLines = self.show_position_error_lines_checkbox.isChecked()
        self.display_config.showTagNames = self.tag_names_checkbox.isChecked()
        self.display_config.showTagCoordinates = self.tag_coordinates_checkbox.isChecked()

        # Between Anchors and Tags
        self.display_config.showTagAnchorLabels = self.tag_anchor_labels_checkbox.isChecked()
        self.display_config.showTagAnchorLines = self.tag_anchor_lines_checkbox.isChecked()

        # Between Anchors
        self.display_config.showBetweenAnchorsLabels = self.between_anchors_labels_checkbox.isChecked()
        self.display_config.showBetweenAnchorsLines = self.between_anchors_lines_checkbox.isChecked()

        # Interaction
        self.display_config.rightClickAnchors = self.right_click_anchors_checkbox.isChecked()
        self.display_config.dragAnchors = self.drag_anchors_checkbox.isChecked()

        # Plots
        self.display_config.showTrilatPlot = self.show_trilat_plot_checkbox.isChecked()
        self.display_config.showComparisonPlot = self.show_comparison_plot_checkbox.isChecked()
        self.display_config.showBorderRectangle = self.show_border_rectangle_checkbox.isChecked()
        self.display_config.useBorderRectangleForViewport = self.use_border_rectangle_for_viewport_checkbox.isChecked()

        # Legend Elements
        self.display_config.showLegendAnchors = self.show_legend_anchors_checkbox.isChecked()
        self.display_config.showLegendTags = self.show_legend_tags_checkbox.isChecked()
        self.display_config.showLegendTagTruth = self.show_legend_tag_truth_checkbox.isChecked()
        self.display_config.showLegendBorder = self.show_legend_border_checkbox.isChecked()

        # Line Plot Options
        self.display_config.showLinePointValues = self.show_line_point_values_checkbox.isChecked()

        # Note: Import Options (aggregation method) are updated via update_aggregation_method()

        self.main_window.update_all()

    def update_aggregation_method(self, method):
        """Update aggregation method when combo box selection changes."""
        self.display_config.aggregationMethod = method

    def update_trilateration_method(self, method):
        """Update trilateration method default when combo box selection changes.
        
        Note: This only updates the default method used for new imports.
        Existing scenarios retain their configured methods.
        """
        self.display_config.trilaterationMethod = method
        # Don't update existing scenarios - each scenario keeps its own method

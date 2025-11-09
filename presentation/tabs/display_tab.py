"""
Display tab for the GDOP application.
"""

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QCheckBox
from .base_tab import BaseTab


class DisplayTab(BaseTab):
    """Tab for display configuration options."""
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.display_tree = None
        # Store references to checkboxes for later access
        self.anchor_circles_checkbox = None
        self.anchor_labels_checkbox = None
        self.between_anchors_lines_checkbox = None
        self.between_anchors_labels_checkbox = None
        self.tag_anchor_lines_checkbox = None
        self.tag_anchor_labels_checkbox = None
        self.right_click_anchors_checkbox = None
        self.tag_labels_checkbox = None
        self.drag_anchors_checkbox = None
        self.show_anchors_checkbox = None
        self.show_tag_truth_checkbox = None
        self.show_tags_checkbox = None
        self.show_trilat_plot_checkbox = None
        self.show_comparison_plot_checkbox = None
        self.show_border_rectangle_checkbox = None
        self.use_border_rectangle_for_viewport_checkbox = None
        self.show_position_error_lines_checkbox = None
        self.show_legend_anchors_checkbox = None
        self.show_legend_tags_checkbox = None
        self.show_legend_tag_truth_checkbox = None
    
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

        self.anchor_labels_checkbox = QCheckBox("Show Anchor Labels")
        self.anchor_labels_checkbox.setChecked(self.display_config.showAnchorLabels)
        self.anchor_labels_checkbox.stateChanged.connect(self.update_display_config)
        anchor_labels_item = QTreeWidgetItem(anchors_node)
        self.display_tree.setItemWidget(anchor_labels_item, 0, self.anchor_labels_checkbox)

        # Tags section
        tags_node = QTreeWidgetItem(self.display_tree, ["Tags"])
        self.show_tag_truth_checkbox = QCheckBox("Show Tag Truth")
        self.show_tag_truth_checkbox.setChecked(self.display_config.showTagTruth)
        self.show_tag_truth_checkbox.stateChanged.connect(self.update_display_config)
        show_tag_truth_item = QTreeWidgetItem(tags_node)
        self.display_tree.setItemWidget(show_tag_truth_item, 0, self.show_tag_truth_checkbox)
        tags_node.setExpanded(True)

        self.show_tags_checkbox = QCheckBox("Show Tags")
        self.show_tags_checkbox.setChecked(self.display_config.showTags)
        self.show_tags_checkbox.stateChanged.connect(self.update_display_config)
        show_tags_item = QTreeWidgetItem(tags_node)
        self.display_tree.setItemWidget(show_tags_item, 0, self.show_tags_checkbox)

        self.tag_labels_checkbox = QCheckBox("Show Tag Labels")
        self.tag_labels_checkbox.setChecked(self.display_config.showTagLabels)
        self.tag_labels_checkbox.stateChanged.connect(self.update_display_config)
        tag_labels_item = QTreeWidgetItem(tags_node)
        self.display_tree.setItemWidget(tag_labels_item, 0, self.tag_labels_checkbox)

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

        return self.display_tree

    def update_display_config(self):
        """Update display configuration based on checkbox states."""
        # Anchors
        self.display_config.showAnchors = self.show_anchors_checkbox.isChecked()
        self.display_config.showAnchorCircles = self.anchor_circles_checkbox.isChecked()
        self.display_config.showAnchorLabels = self.anchor_labels_checkbox.isChecked()

        # Tags
        self.display_config.showTagTruth = self.show_tag_truth_checkbox.isChecked()
        self.display_config.showTags = self.show_tags_checkbox.isChecked()
        self.display_config.showTagLabels = self.tag_labels_checkbox.isChecked()
        self.display_config.showPositionErrorLines = self.show_position_error_lines_checkbox.isChecked()

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

        self.main_window.update_all()

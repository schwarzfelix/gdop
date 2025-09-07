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
        self.gdop_checkbox = None
        self.tag_labels_checkbox = None
    
    @property
    def tab_name(self):
        return "Display"
        
    def create_widget(self):
        """Create and return the display tab widget."""
        self.display_tree = QTreeWidget()
        self.display_tree.setHeaderHidden(True)

        # Anchor section
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

        # Between Anchors section
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

        # Tag and Anchors section
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

        # Tag labels checkbox
        tag_labels_checkbox = QCheckBox("Show Tag Labels")
        tag_labels_checkbox.setChecked(self.display_config.showTagLabels)
        tag_labels_checkbox.stateChanged.connect(self.update_display_config)
        tag_labels_item = QTreeWidgetItem(tag_anchor_node)
        self.display_tree.setItemWidget(tag_labels_item, 0, tag_labels_checkbox)
        self.tag_labels_checkbox = tag_labels_checkbox  # Save reference

        # Interaction section
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

        return self.display_tree

    def update_display_config(self):
        """Update display configuration based on checkbox states."""
        self.display_config.showAnchorCircles = self.anchor_circles_checkbox.isChecked()
        self.display_config.showAnchorLabels = self.anchor_labels_checkbox.isChecked()
        self.display_config.showBetweenAnchorsLines = self.between_anchors_lines_checkbox.isChecked()
        self.display_config.showBetweenAnchorsLabels = self.between_anchors_labels_checkbox.isChecked()
        self.display_config.showTagAnchorLines = self.tag_anchor_lines_checkbox.isChecked()
        self.display_config.showTagAnchorLabels = self.tag_anchor_labels_checkbox.isChecked()

        self.display_config.rightClickAnchors = self.right_click_anchors_checkbox.isChecked()
        self.display_config.showGDOP = self.gdop_checkbox.isChecked()
        self.display_config.showTagLabels = self.tag_labels_checkbox.isChecked()

        self.main_window.update_all()

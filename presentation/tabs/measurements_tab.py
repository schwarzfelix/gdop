"""
Measurements tab for the GDOP application.
"""

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from .base_tab import BaseTab


class MeasurementsTab(BaseTab):
    """Tab for displaying measurements."""
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.measurements_tree = None
    
    @property
    def tab_name(self):
        return "Measurements"
        
    def create_widget(self):
        """Create and return the measurements tab widget."""
        self.measurements_tree = QTreeWidget()
        self.measurements_tree.setHeaderHidden(True)
        self.update_measurements_tree()
        return self.measurements_tree

    def update_measurements_tree(self):
        """Update the measurements tree with current measurement data."""
        if not self.measurements_tree:
            return

        self.measurements_tree.clear()

        for pair, distance in self.scenario.measurements.relation.items():
            station1, station2 = pair
            measurement_item = QTreeWidgetItem(
                self.measurements_tree,
                [f"{station1.name()} ↔ {station2.name()}: {distance:.2f}"]
            )
            # Group measurements by tag
            measurement_item.setExpanded(True)
            
    def update(self):
        """Update the measurements tree."""
        self.update_measurements_tree()

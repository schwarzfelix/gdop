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
        # Aggregate measurement relations from all scenarios
        app = getattr(self, 'app', None) or getattr(self.main_window, 'app', None)
        scenarios = app.scenarios if app and getattr(app, 'scenarios', None) else [self.scenario]

        for scen in scenarios:
            try:
                for pair, distance in scen.measurements.relation.items():
                    station1, station2 = pair
                    measurement_item = QTreeWidgetItem(
                        self.measurements_tree,
                        [f"{station1.name()} ↔ {station2.name()}: {distance:.2f}"]
                    )
                    measurement_item.setExpanded(True)
            except Exception:
                # best-effort per scenario
                continue
            
    def update(self):
        """Update the measurements tree."""
        self.update_measurements_tree()

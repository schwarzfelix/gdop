
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from .base_tab import BaseTab


class TreeTab(BaseTab):

    def __init__(self, main_window):
        super().__init__(main_window)
        self.tree = None

    @property
    def tab_name(self):
        return "Tree"

    def create_widget(self):
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.update_tree()
        return self.tree

    def update_tree(self):
        if not self.tree:
            return

        self.tree.clear()

        app = self.main_window.app
        scenarios = app.scenarios

        for scen in scenarios:
            scen_node = QTreeWidgetItem(self.tree, [scen.name])
            scen_node.setExpanded(True)

            stations_node = QTreeWidgetItem(scen_node, ["Stations"]) 
            stations_node.setExpanded(True)
            for station in scen.stations:
                QTreeWidgetItem(stations_node, [station.name()])

            measurements_node = QTreeWidgetItem(scen_node, ["Measurements"]) 
            measurements_node.setExpanded(True)
            for pair, distance in scen.measurements.relation.items():
                station1, station2 = pair
                label = f"{station1.name()} ↔ {station2.name()}: {distance:.2f}"
                QTreeWidgetItem(measurements_node, [label])

    def update(self):
        self.update_tree()

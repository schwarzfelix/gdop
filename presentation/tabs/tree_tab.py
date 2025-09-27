
from PyQt5.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from .base_tab import BaseTab
from PyQt5.QtWidgets import QInputDialog
from simulation.station import Anchor
from data.importer import get_available_scenarios, validate_scenario_for_import


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

        active = self.main_window.trilat_plot.scenario

        for scen in scenarios:
            scen_node = QTreeWidgetItem(self.tree)
            scen_node.setExpanded(True)

            row_widget = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)

            name_label = QLabel(scen.name)
            activate_button = QPushButton("⏿")
            activate_button.setToolTip("Activate this scenario in the main plot")
            activate_button.clicked.connect(lambda checked, s=scen: self._activate_scenario(s))

            row_layout.addWidget(activate_button)
            row_layout.addWidget(name_label)
            row_layout.addStretch()
            row_widget.setLayout(row_layout)

            self.tree.setItemWidget(scen_node, 0, row_widget)

            if active is scen:
                self.tree.setCurrentItem(scen_node)

            stations_node = QTreeWidgetItem(scen_node, ["Stations"]) 
            stations_node.setExpanded(True)
            for station in scen.stations:
                station_node = QTreeWidgetItem(stations_node)

                station_widget = QWidget()
                layout = QHBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)

                name_label = QLabel(station.name)
                rename_button = QPushButton("✎")
                rename_button.setToolTip("Edit station (name and coordinates)")
                rename_button.clicked.connect(lambda checked, s=station: self.rename_station_dialog(s))

                delete_button = QPushButton("␡")
                delete_button.setToolTip("Delete station")
                delete_button.clicked.connect(lambda checked, s=station: self._delete_station(s))

                layout.addWidget(delete_button)
                layout.addWidget(rename_button)
                layout.addWidget(name_label)
                layout.addStretch()
                station_widget.setLayout(layout)

                self.tree.setItemWidget(station_node, 0, station_widget)

            measurements_node = QTreeWidgetItem(scen_node, ["Measurements"]) 
            measurements_node.setExpanded(True)
            for pair, distance in scen.measurements.relation.items():
                station1, station2 = pair

                label = f"{station1.name} ↔ {station2.name}: {distance:.2f}"
                QTreeWidgetItem(measurements_node, [label])

        scenario_names, error_message = get_available_scenarios()
        for scen_name in scenario_names:
           if scen_name not in [scen.name for scen in scenarios]:
               QTreeWidgetItem(self.tree, [scen_name])

    def update(self):
        self.update_tree()

    def rename_station_dialog(self, station):
        new_name, ok = QInputDialog.getText(self.main_window, "Rename Station", "New name:", text=station.name)
        if ok and new_name and new_name != station.name:
            self.rename_station(station, new_name)

    def rename_station(self, station, new_name):
        station.name = new_name
        self.main_window.update_all()

    def _delete_station(self, station):
        try:
            self.scenario.remove_station(station)
        except Exception:
            app = self.main_window.app
            for scen in app.scenarios:
                scen.remove_station(station)
        self.main_window.update_all()
        # TODO implement station removal function in station (stations need to know their scenario)

    def _activate_scenario(self, scen):
        plot = self.main_window.trilat_plot
        plot.scenario = scen
        try:
            plot.sandbox_tag = next((tag for tag in plot.scenario.get_tag_list() if tag.name == "SANDBOX_TAG"), None)
        except Exception:
            plot.sandbox_tag = None
        # TODO fix SandboxTag handling
        plot.init_artists()
        self.main_window.update_all()

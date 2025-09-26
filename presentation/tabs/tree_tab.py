
from PyQt5.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
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

        scenarios_node = QTreeWidgetItem(self.tree, ["Scenarios"])
        scenarios_node.setExpanded(True)

        active = self.main_window.trilat_plot.scenario

        for scen in scenarios:
            scen_node = QTreeWidgetItem(scenarios_node)
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
                QTreeWidgetItem(stations_node, [station.name()])

            measurements_node = QTreeWidgetItem(scen_node, ["Measurements"]) 
            measurements_node.setExpanded(True)
            for pair, distance in scen.measurements.relation.items():
                station1, station2 = pair

                label = f"{station1.name()} ↔ {station2.name()}: {distance:.2f}"
                QTreeWidgetItem(measurements_node, [label])

    def update(self):
        self.update_tree()

    def _activate_scenario(self, scen):
        plot = self.main_window.trilat_plot
        plot.scenario = scen
        try:
            plot.sandbox_tag = next((tag for tag in plot.scenario.get_tag_list() if tag.name() == "SANDBOX_TAG"), None)
        except Exception:
            plot.sandbox_tag = None
        # TODO fix SandboxTag handling
        plot.init_artists()
        self.main_window.update_all()

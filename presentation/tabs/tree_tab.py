
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
        # active scenario to mark selection
        try:
            active = getattr(self.main_window.trilat_plot, 'scenario', None)
        except Exception:
            active = None

        for scen in scenarios:
            scen_node = QTreeWidgetItem(scenarios_node)

            # create a row widget with label and activate button (like StationsTab)
            row_widget = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)

            name_label = QLabel(getattr(scen, 'name', str(scen)))
            activate_button = QPushButton("Activate")
            activate_button.setToolTip("Activate this scenario in the main plot")
            activate_button.clicked.connect(lambda checked, s=scen: self.activate_scenario(s))

            row_layout.addWidget(activate_button)
            row_layout.addWidget(name_label)
            row_layout.addStretch()
            row_widget.setLayout(row_layout)

            self.tree.setItemWidget(scen_node, 0, row_widget)

            # if this is the active scenario, select it
            try:
                if active is scen or (active and getattr(active, 'name', None) == getattr(scen, 'name', None)):
                    self.tree.setCurrentItem(scen_node)
            except Exception:
                pass

            scen_node.setExpanded(True)

            stations_node = QTreeWidgetItem(scen_node, ["Stations"]) 
            stations_node.setExpanded(True)
            try:
                for station in getattr(scen, 'stations', []):
                    QTreeWidgetItem(stations_node, [station.name()])
            except Exception:
                pass

            measurements_node = QTreeWidgetItem(scen_node, ["Measurements"]) 
            measurements_node.setExpanded(True)
            try:
                for pair, distance in getattr(scen, 'measurements', {}).relation.items():
                    try:
                        station1, station2 = pair
                    except Exception:
                        items = list(pair)
                        if len(items) >= 2:
                            station1, station2 = items[0], items[1]
                        else:
                            continue

                    label = f"{station1.name()} ↔ {station2.name()}: {distance:.2f}"
                    QTreeWidgetItem(measurements_node, [label])
            except Exception:
                pass

    def update(self):
        self.update_tree()

    def activate_scenario(self, scen):
        """Activate the given scenario in the main trilat plot (mirrors ScenariosTab)."""
        plot = self.main_window.trilat_plot
        if plot is not None:
            plot.scenario = scen
            try:
                plot.sandbox_tag = next((tag for tag in plot.scenario.get_tag_list() if tag.name() == "SANDBOX_TAG"), None)
            except Exception:
                plot.sandbox_tag = None
            try:
                plot.init_artists()
            except Exception:
                pass
        # refresh all (this will also refresh the tree selection)
        try:
            self.main_window.update_all()
        except Exception:
            pass

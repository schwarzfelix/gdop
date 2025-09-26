"""
Scenarios management tab - lists available scenarios.
"""

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QWidget, QHBoxLayout, QLabel
from .base_tab import BaseTab


class ScenariosTab(BaseTab):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.scenarios_tree = None

    @property
    def tab_name(self):
        return "Scenarios"

    def create_widget(self):
        self.scenarios_tree = QTreeWidget()
        self.scenarios_tree.setHeaderHidden(True)
        self.scenarios_tree.itemClicked.connect(self._on_item_clicked)
        self.update_scenarios()
        return self.scenarios_tree

    def update_scenarios(self):
        if not self.scenarios_tree:
            return
        self.scenarios_tree.clear()
        app = getattr(self.main_window, 'app', None)
        if not app:
            return
        # active scenario is stored in the plot
        plot = self.main_window.plot
        active = getattr(plot, 'scenario', None)

        for scen in app.scenarios:
            node = QTreeWidgetItem(self.scenarios_tree)


            row_widget = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)

            name_label = QLabel(scen.name)
            row_layout.addWidget(name_label)
            row_layout.addStretch()
            row_widget.setLayout(row_layout)

            self.scenarios_tree.setItemWidget(node, 0, row_widget)

            if active is scen or (active and getattr(active, 'name', None) == getattr(scen, 'name', None)):
                # select the active scenario
                self.scenarios_tree.setCurrentItem(node)

    def _on_item_clicked(self, item, col):
        
        app = self.main_window.app

        try:
            widget = self.scenarios_tree.itemWidget(item, 0)
            if widget is not None:
                label = widget.findChild(QLabel)
                if label:
                    name = label.text()
                else:
                    name = item.text(0)
            else:
                name = item.text(0)
        except Exception:
            name = item.text(0)

        for scen in app.scenarios:
            if scen.name == name:

                plot = self.main_window.plot
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
                self.main_window.update_all()
                break

    def update(self):
        self.update_scenarios()

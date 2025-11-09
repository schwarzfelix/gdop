
from PyQt5.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
)
from .base_tab import BaseTab
from PyQt5.QtWidgets import QInputDialog
from simulation.station import Anchor
from data.importer import get_available_scenarios, validate_scenario_for_import, get_scenario_data
from data import importer as importer_module
from PyQt5.QtWidgets import QComboBox, QFormLayout, QDialog, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QDialogButtonBox
import pandas as pd
try:
    import pandasgui as pg
except ImportError:
    pg = None
import os
from PyQt5.QtWidgets import QTableView, QAbstractItemView, QHeaderView
from PyQt5.QtCore import QAbstractTableModel, Qt
from presentation.trilatplot_window import TrilatPlotWindow
from simulation import station as station_module
import numpy as np


class DataFrameModel(QAbstractTableModel):
    def __init__(self, df):
        super().__init__()
        self.df = df

    def rowCount(self, parent=None):
        return len(self.df)

    def columnCount(self, parent=None):
        return len(self.df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            value = self.df.iloc[index.row(), index.column()]
            return str(value)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.df.columns[section])
            elif orientation == Qt.Vertical:
                return str(self.df.index[section])
        return None


class DataFrameViewer(QDialog):
    def __init__(self, df, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 600)

        layout = QVBoxLayout()

        self.table = QTableView()
        self.model = DataFrameModel(df)
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)


class AggregationMethodDialog(QDialog):
    """Dialog to choose aggregation method for imported measurements.

    Moved here from `data_tab.py` so TreeTab can reuse it without circular imports.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Aggregation Method")
        self.setModal(True)
        self.resize(300, 120)

        # Build UI inside constructor only (no widgets at import time)
        layout = QVBoxLayout()

        info_label = QLabel("Choose how to aggregate measurements per AP:")
        layout.addWidget(info_label)

        form = QFormLayout()
        self.combo = QComboBox()
        # default 'lowest' first
        self.combo.addItems(["lowest", "newest", "mean", "median"])
        self.combo.setCurrentIndex(0)
        form.addRow("Method:", self.combo)
        layout.addLayout(form)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_method(self):
        return self.combo.currentText()


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

        scenario_names, error_message = get_available_scenarios()
        loaded_scenario_names = {s.name for s in scenarios}
        all_scenario_names = set(scenario_names) | loaded_scenario_names

        for scen_name in sorted(all_scenario_names):
            scen_node = QTreeWidgetItem(self.tree)
            #scen_node.setExpanded(True)

            row_widget = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)

            checkbox = QCheckBox()
            is_imported = scen_name in loaded_scenario_names
            is_from_workspace = scen_name in scenario_names
            checkbox.setChecked(is_imported)
            checkbox.setEnabled(True)
            checkbox.stateChanged.connect(lambda state, name=scen_name: self._toggle_scenario(name, state))

            name_label = QLabel(scen_name)

            row_layout.addWidget(checkbox)
            row_layout.addWidget(name_label)
            row_layout.addStretch()

            if is_imported:
                scen = next(s for s in scenarios if s.name == scen_name)

                if active is not scen:
                    activate_button = QPushButton("⏿")
                    activate_button.setToolTip("Activate this scenario in the main plot")
                    activate_button.clicked.connect(lambda checked, s=scen: self._activate_scenario(s))

                    row_layout.addWidget(activate_button)

                # Add PandasGUI and Viewer buttons only if from workspace and not SandboxScenario
                if is_from_workspace and scen.name != "SandboxScenario":
                    pandas_button = QPushButton("📊")
                    pandas_button.setToolTip("Open DataFrame in PandasGUI")
                    pandas_button.clicked.connect(lambda checked, name=scen_name: self._open_pandasgui(name))

                    row_layout.addWidget(pandas_button)

                    viewer_button = QPushButton("📋")
                    viewer_button.setToolTip("Open DataFrame in Table Viewer")
                    viewer_button.clicked.connect(lambda checked, name=scen_name: self._open_dataframe_viewer(name))

                    row_layout.addWidget(viewer_button)

                # Add TrilatPlot popup button for all imported scenarios
                popup_button = QPushButton("📈")
                popup_button.setToolTip("Open TrilatPlot in new window")
                popup_button.clicked.connect(lambda checked, s=scen: self._open_trilat_popup(s))

                row_layout.addWidget(popup_button)

                if active is scen:
                    self.tree.setCurrentItem(scen_node)
                    checkbox.setEnabled(False)  # Prevent unchecking the active scenario

                stations_node = QTreeWidgetItem(scen_node, ["Stations"]) 
                #stations_node.setExpanded(True)
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

                    layout.addWidget(name_label)
                    layout.addStretch()
                    layout.addWidget(rename_button)
                    layout.addWidget(delete_button)
                    station_widget.setLayout(layout)

                    self.tree.setItemWidget(station_node, 0, station_widget)

                    # Add GDOP for Tags
                    if isinstance(station, station_module.Tag):
                        try:
                            gdop = station.dilution_of_precision()
                            gdop_text = f"GDOP: {gdop:.2f}" if np.isfinite(gdop) else "GDOP: ∞"
                            QTreeWidgetItem(station_node, [gdop_text])
                        except Exception as e:
                            QTreeWidgetItem(station_node, ["GDOP: N/A"])

                        # Add Position Error
                        try:
                            error = station.position_error()
                            if error is not None:
                                error_text = f"Position Error: {error:.2f}"
                                QTreeWidgetItem(station_node, [error_text])
                            else:
                                QTreeWidgetItem(station_node, ["Position Error: N/A"])
                        except Exception as e:
                            QTreeWidgetItem(station_node, ["Position Error: N/A"])

                measurements_node = QTreeWidgetItem(scen_node, ["Measurements"]) 
                #measurements_node.setExpanded(True)
                for pair, distance in scen.measurements.relation.items():
                    station1, station2 = pair

                    label = f"{station1.name} ↔ {station2.name}: {distance:.2f}"
                    QTreeWidgetItem(measurements_node, [label])

                # Add Tag Truth GDOP if exists
                tag_truth_node = QTreeWidgetItem(scen_node, ["Tag Truth"])
                try:
                    gdop = scen.get_tag_truth_gdop()
                    gdop_text = f"GDOP: {gdop:.2f}" if np.isfinite(gdop) else "GDOP: ∞"
                    QTreeWidgetItem(tag_truth_node, [gdop_text])
                except Exception as e:
                    QTreeWidgetItem(tag_truth_node, ["GDOP: N/A"])
            row_widget.setLayout(row_layout)

            self.tree.setItemWidget(scen_node, 0, row_widget)

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

    def _open_pandasgui(self, scen_name):
        if pg is None:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self.main_window, "PandasGUI not available", "PandasGUI is not installed. Please install it with 'pip install pandasgui'.")
            return
        try:
            workspace_dir = os.path.abspath("workspace")
            df, error = get_scenario_data(scen_name, workspace_dir=workspace_dir)
            if error:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self.main_window, "Data Load Error", f"Could not load data for scenario '{scen_name}': {error}")
                return
            if df is not None and not df.empty:
                # Open in PandasGUI
                try:
                    pg.show(df, title=f"DataFrame for Scenario: {scen_name}")
                except Exception as e:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.critical(self.main_window, "Error opening PandasGUI", f"Failed to open PandasGUI: {str(e)}")
            else:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self.main_window, "No Data", f"No data available for scenario '{scen_name}'.")
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to open PandasGUI: {str(e)}")

    def _open_dataframe_viewer(self, scen_name):
        try:
            workspace_dir = os.path.abspath("workspace")
            df, error = get_scenario_data(scen_name, workspace_dir=workspace_dir)
            if error:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self.main_window, "Data Load Error", f"Could not load data for scenario '{scen_name}': {error}")
                return
            if df is not None and not df.empty:
                # Open in DataFrameViewer
                viewer = DataFrameViewer(df, f"DataFrame for Scenario: {scen_name}", self.main_window)
                viewer.exec_()
            else:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self.main_window, "No Data", f"No data available for scenario '{scen_name}'.")
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to open DataFrame viewer: {str(e)}")

    def _open_trilat_popup(self, scen):
        try:
            # Create and show the TrilatPlotWindow
            window = TrilatPlotWindow(scen, self.main_window)
            window.show()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Error", f"Failed to open TrilatPlot popup: {str(e)}")

    def _remove_scenario(self, scen):
        app = self.main_window.app
        app.scenarios.remove(scen)
        plot = self.main_window.trilat_plot
        if plot.scenario == scen:
            plot.scenario = None
            plot.sandbox_tag = None
            plot.init_artists()
        self.main_window.update_all()

    def _toggle_scenario(self, scen_name, state):
        from PyQt5.QtCore import Qt
        if state == Qt.Checked:
            # Import if not already imported
            app = self.main_window.app
            if scen_name not in [s.name for s in app.scenarios]:
                self._import_scenario_from_workspace(scen_name)
        else:
            # Remove if imported
            app = self.main_window.app
            scen = next((s for s in app.scenarios if s.name == scen_name), None)
            if scen:
                self._remove_scenario(scen)

    def _import_scenario_from_workspace(self, scen_name: str):
        """Import a scenario by name from the workspace directory.

        Shows an aggregation method dialog (reuse from DataTab) and calls the importer.
        On success appends the scenario to app.scenarios and activates it in the plot.
        """
        # Check if standard aggregation method should be used
        if self.main_window.display_config.useStandardAggregationMethod:
            agg_method = "lowest"
        else:
            # Ask for aggregation method
            try:
                agg_dialog = AggregationMethodDialog(self.main_window)
            except Exception:
                # fallback: simple selection
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self.main_window, "Import", "Unable to open aggregation dialog.")
                return

            if agg_dialog.exec_() != agg_dialog.Accepted:
                return

            agg_method = agg_dialog.get_method()

        try:
            success, message, imported_scenario = importer_module.import_scenario(scen_name, workspace_dir="workspace", agg_method=agg_method)
        except Exception as e:
            success = False
            message = f"Import raised exception: {e}"
            imported_scenario = None

        if success and imported_scenario is not None:
            # Append to app scenarios
            app = getattr(self.main_window, 'app', None)
            if app is not None:
                app.scenarios.append(imported_scenario)

            # Activate in plot
            try:
                plot = self.main_window.trilat_plot
                if plot is not None:
                    plot.scenario = imported_scenario
                    try:
                        plot.sandbox_tag = next((tag for tag in plot.scenario.get_tag_list() if tag.name == "SANDBOX_TAG"), None)
                    except Exception:
                        plot.sandbox_tag = None
                    try:
                        plot.init_artists()
                    except Exception:
                        pass
            except Exception:
                pass

            # Refresh UI
            try:
                if hasattr(self.main_window, 'scenarios_tab') and self.main_window.scenarios_tab:
                    self.main_window.scenarios_tab.update()
            except Exception:
                pass
            self.main_window.update_all()
            try:
                self.main_window.statusBar().showMessage(f"Imported scenario '{scen_name}' ({agg_method})", 5000)
            except Exception:
                pass
        else:
            try:
                self.main_window.statusBar().showMessage(f"Import Error: {message}", 0)
            except Exception:
                pass

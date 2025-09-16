"""
Stations tab for the GDOP application.
"""

from PyQt5.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QWidget, QHBoxLayout, 
    QLabel, QPushButton, QDialog, QFormLayout,
    QLineEdit, QVBoxLayout, QDialogButtonBox
)
from .base_tab import BaseTab
from simulation.station import Anchor


class StationEditDialog(QDialog):
    """Dialog for editing station name and coordinates."""
    
    def __init__(self, station, parent=None):
        super().__init__(parent)
        self.station = station
        self.setWindowTitle(f"Edit Station: {station.name()}")
        self.setModal(True)
        self.resize(300, 200)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit(station.name())
        form_layout.addRow("Name:", self.name_edit)
        
        # Coordinate fields (only for Anchor stations)
        self.x_edit = None
        self.y_edit = None
        if isinstance(station, Anchor):
            position = station.position()
            self.x_edit = QLineEdit(str(position[0]))
            self.y_edit = QLineEdit(str(position[1]))
            form_layout.addRow("X Coordinate:", self.x_edit)
            form_layout.addRow("Y Coordinate:", self.y_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_values(self):
        """Get the edited values from the dialog."""
        values = {'name': self.name_edit.text().strip()}
        
        if self.x_edit and self.y_edit:
            try:
                values['x'] = float(self.x_edit.text())
                values['y'] = float(self.y_edit.text())
            except ValueError:
                return None  # Invalid coordinate values
        
        return values


class StationsTab(BaseTab):
    """Tab for managing stations."""
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.stations_tree = None
    
    @property
    def tab_name(self):
        return "Stations"
        
    def create_widget(self):
        """Create and return the stations tab widget."""
        self.stations_tree = QTreeWidget()
        self.stations_tree.setHeaderHidden(True)
        self.update_stations_tree()
        return self.stations_tree
        
    def update_stations_tree(self):
        """Update the stations tree with current station data."""
        if not self.stations_tree:
            return
            
        self.stations_tree.clear()
        # Aggregate stations from all scenarios if an app container is available
        app = getattr(self, 'app', None) or getattr(self.main_window, 'app', None)
        if app and getattr(app, 'scenarios', None):
            # merge stations from all scenarios (keep duplicates if separate objects)
            all_stations = []
            for scen in app.scenarios:
                all_stations.extend(getattr(scen, 'stations', []))
        else:
            all_stations = self.scenario.stations

        station_positions = {station: station.position() for station in all_stations}

        for station in all_stations:
            station_node = QTreeWidgetItem(self.stations_tree)

            station_widget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)

            name_label = QLabel(station.name())
            rename_button = QPushButton("✎")
            rename_button.setToolTip("Edit station (name and coordinates)")
            rename_button.clicked.connect(lambda checked, s=station: self.rename_station_dialog(s))

            delete_button = QPushButton("␡")
            delete_button.setToolTip("Delete station")
            delete_button.clicked.connect(lambda checked, s=station: self.delete_station(s))

            layout.addWidget(delete_button)
            layout.addWidget(rename_button)
            layout.addWidget(name_label)
            layout.addStretch()
            station_widget.setLayout(layout)

            self.stations_tree.setItemWidget(station_node, 0, station_widget)

            other_stations = [
                (other_station.name(), station_positions[other_station])
                for other_station in all_stations if other_station != station
            ]

            #TODO fix angle calculation, (list/vecor operations not supported)
            #for (name1, pos1), (name2, pos2) in combinations(other_stations, 2):
            #    angle = geometry.angle_vectors(
            #        pos1 - station_positions[station],
            #        pos2 - station_positions[station]
            #    )
            #    QTreeWidgetItem(
            #        station_node,
            #        [f"Angle between {name1} and {name2}: {angle:.2f}°"]
            #    )

    def rename_station_dialog(self, station):
        """Show dialog to edit station name and coordinates."""
        dialog = StationEditDialog(station, self.main_window)
        
        if dialog.exec_() == QDialog.Accepted:
            values = dialog.get_values()
            if values is None:
                # Invalid input (e.g., non-numeric coordinates)
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self.main_window,
                    "Invalid Input",
                    "Please enter valid numeric values for coordinates."
                )
                return
            
            # Update name
            if values['name'] and values['name'] != station.name():
                self.rename_station(station, values['name'])
            
            # Update coordinates for Anchor stations
            if isinstance(station, Anchor) and 'x' in values and 'y' in values:
                current_pos = station.position()
                if current_pos[0] != values['x'] or current_pos[1] != values['y']:
                    station.update_position([values['x'], values['y']])
                    self.main_window.update_all()

    def rename_station(self, station, new_name):
        """Rename a station."""
        # Try to set the name attribute if possible
        if hasattr(station, '_name'):
            station._name = new_name
        elif hasattr(station, 'name') and callable(getattr(station, 'name', None)):
            try:
                station.name = lambda: new_name
            except Exception:
                pass
        self.main_window.update_all()

    def delete_station(self, station):
        """Delete a station."""
        self.scenario.remove_station(station)
        self.main_window.update_all()
        
    def update(self):
        """Update the stations tree."""
        self.update_stations_tree()

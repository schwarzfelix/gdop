"""
Data tab for the GDOP application.
"""

from PyQt5.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QCheckBox, 
    QLineEdit, QSpinBox, QPushButton, QVBoxLayout, QWidget,
    QDialog, QListWidget, QListWidgetItem, QMessageBox, QDialogButtonBox,
    QLabel
)
from .base_tab import BaseTab
from data.importer import get_available_scenarios, import_scenario_data, validate_scenario_for_import


class ScenarioSelectionDialog(QDialog):
    """Dialog for selecting which scenario to import from available CSV data."""
    
    def __init__(self, scenarios: list, parent=None):
        super().__init__(parent)
        self.scenarios = scenarios
        
        self.setWindowTitle("Select Scenario to Import")
        self.setModal(True)
        self.resize(400, 300)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the dialog UI components."""
        layout = QVBoxLayout()
        
        # Instructions
        info_label = QLabel("Select a scenario to import measurement data:")
        layout.addWidget(info_label)
        
        # Scenario list
        self.scenario_list = QListWidget()
        for scenario in self.scenarios:
            item = QListWidgetItem(scenario)
            self.scenario_list.addItem(item)
        
        # Select first item by default
        if self.scenarios:
            self.scenario_list.setCurrentRow(0)
            
        layout.addWidget(self.scenario_list)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_selected_scenario(self):
        """Get the selected scenario name."""
        current_item = self.scenario_list.currentItem()
        return current_item.text() if current_item else None


class DataTab(BaseTab):
    """Tab for data import and streaming configuration options."""
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.streaming_tree = None
        self.stream_enabled_checkbox = None
        self.url_input = None
        self.periodic_update_checkbox = None
        self.interval_input = None
        self.csv_import_button = None
    
    @property
    def tab_name(self):
        return "Data"
        
    def create_widget(self):
        """Create and return the data tab widget."""
        # Create main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # CSV Import section
        self.csv_import_button = QPushButton("Import CSV Measurements")
        self.csv_import_button.clicked.connect(self.import_csv_measurements)
        layout.addWidget(self.csv_import_button)
        
        # Streaming section
        self.streaming_tree = QTreeWidget()
        self.streaming_tree.setHeaderHidden(True)

        # Stream enabled checkbox
        root_node = QTreeWidgetItem(self.streaming_tree)
        self.stream_enabled_checkbox = QCheckBox("Stream Measurements")
        self.stream_enabled_checkbox.setChecked(False)
        self.stream_enabled_checkbox.stateChanged.connect(self.update_streaming_config)
        self.streaming_tree.setItemWidget(root_node, 0, self.stream_enabled_checkbox)

        # URL input
        url_node = QTreeWidgetItem(self.streaming_tree)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter Streaming URL")
        self.streaming_tree.setItemWidget(url_node, 0, self.url_input)

        # Periodic update checkbox
        periodic_node = QTreeWidgetItem(self.streaming_tree)
        self.periodic_update_checkbox = QCheckBox("Enable Periodic Update")
        self.periodic_update_checkbox.setChecked(False)
        self.periodic_update_checkbox.stateChanged.connect(self.update_periodic_config)
        self.streaming_tree.setItemWidget(periodic_node, 0, self.periodic_update_checkbox)

        # Interval input
        interval_node = QTreeWidgetItem(self.streaming_tree)
        self.interval_input = QSpinBox()
        self.interval_input.setRange(100, 10000)
        self.interval_input.setValue(2000)
        self.interval_input.setSuffix(" ms")
        self.interval_input.valueChanged.connect(self.update_periodic_interval)
        self.streaming_tree.setItemWidget(interval_node, 0, self.interval_input)

        layout.addWidget(self.streaming_tree)
        return main_widget

    def import_csv_measurements(self):
        """Import measurements from CSV files with scenario selection."""
        # Validate scenario first
        is_valid, validation_error = validate_scenario_for_import(self.scenario)
        if not is_valid:
            QMessageBox.warning(
                self.main_window,
                "Validation Error",
                validation_error
            )
            return
        
        # Get available scenarios
        scenarios, error_message = get_available_scenarios("workspace")
        
        if error_message:
            if "No CSV measurement files found" in error_message:
                QMessageBox.information(
                    self.main_window,
                    "No Data Found",
                    f"No CSV measurement files found in 'workspace' directory."
                )
            elif "No scenario data found" in error_message:
                QMessageBox.warning(
                    self.main_window,
                    "No Scenarios Found",
                    "No scenario data found in CSV files."
                )
            else:
                QMessageBox.critical(
                    self.main_window,
                    "Error",
                    error_message
                )
            return
        
        # Show scenario selection dialog
        dialog = ScenarioSelectionDialog(scenarios, self.main_window)
        
        if dialog.exec_() != QDialog.Accepted:
            return  # User cancelled
        
        selected_scenario = dialog.get_selected_scenario()
        if not selected_scenario:
            return
        
        # Import the selected scenario
        success, message = import_scenario_data(self.scenario, selected_scenario, "workspace")
        
        if success:
            QMessageBox.information(
                self.main_window,
                "Import Successful",
                message
            )
            # Update the UI to reflect the imported data
            self.main_window.update_all()
        else:
            QMessageBox.critical(
                self.main_window,
                "Import Error",
                message
            )

    def update_streaming_config(self):
        """Update streaming configuration based on checkbox state."""
        is_enabled = self.stream_enabled_checkbox.isChecked()
        if is_enabled:
            url = self.url_input.text().strip()
            if url:
                self.scenario.start_streaming(url)
            else:
                self.stream_enabled_checkbox.setChecked(False)
                print("Please enter a valid Streaming URL.")
        else:
            self.scenario.stop_streaming()
            print("Streaming stopped.")

    def update_periodic_config(self):
        """Update periodic update configuration."""
        is_enabled = self.periodic_update_checkbox.isChecked()
        if is_enabled:
            self.main_window.update_timer.start(self.interval_input.value())
        else:
            self.main_window.update_timer.stop()

    def update_periodic_interval(self):
        """Update periodic update interval."""
        if self.periodic_update_checkbox.isChecked():
            self.main_window.update_timer.setInterval(self.interval_input.value())

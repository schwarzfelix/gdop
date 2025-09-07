"""
Data tab for the GDOP application.
"""

from PyQt5.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QCheckBox, 
    QLineEdit, QSpinBox, QPushButton, QVBoxLayout, QWidget
)
from .base_tab import BaseTab
import data.csv as csvio


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
        self.url_input.setPlaceholderText("Enter SSE URL")
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
        """Import measurements from CSV file."""
        df = csvio.read_workspace_csvs("workspace")
        print(df.head())

    def update_streaming_config(self):
        """Update streaming configuration based on checkbox state."""
        is_enabled = self.stream_enabled_checkbox.isChecked()
        if is_enabled:
            url = self.url_input.text().strip()
            if url:
                self.scenario.start_streaming(url)
            else:
                self.stream_enabled_checkbox.setChecked(False)
                print("Please enter a valid SSE URL.")
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

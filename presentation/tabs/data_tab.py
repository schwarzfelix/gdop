"""
Data tab for the GDOP application.
"""

from PyQt5.QtWidgets import (
    QLineEdit, QPushButton, QVBoxLayout, QWidget,
    QDialog, QListWidget, QListWidgetItem, QDialogButtonBox,
    QLabel, QRadioButton, QButtonGroup
)
from .base_tab import BaseTab
from data.importer import get_available_scenarios, validate_scenario_for_import
from PyQt5.QtWidgets import QComboBox, QFormLayout
from data.mqtt_streamer import MQTTStreamer
from typing import Optional
import logging

_LOG = logging.getLogger(__name__)


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


class AggregationMethodDialog(QDialog):
    """Dialog to choose aggregation method for imported measurements."""

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


class DataTab(BaseTab):
    """Tab for data import and streaming configuration options."""
    
    def __init__(self, main_window):
        super().__init__(main_window)
        # container widget for streaming controls (replaces previous QTreeWidget)
        self.streaming_container = None
        # radio buttons for streaming mode: off, mqtt, sse
        self.stream_mode_group = None
        self.stream_mode_off = None
        self.stream_mode_mqtt = None
        self.stream_mode_sse = None
        self.url_input = None
        # MQTT streamer instance (optional, created lazily)
        self._mqtt_streamer: Optional[MQTTStreamer] = None
        # periodic update controls removed - updates come from streamer signals
        self.csv_import_button = None
    
    @property
    def tab_name(self):
        return "Import"
        
    def create_widget(self):
        """Create and return the data tab widget."""
        # Create main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # CSV Import section
        self.csv_import_button = QPushButton("Import scenario from workspace")
        self.csv_import_button.clicked.connect(self.import_csv_measurements)
        layout.addWidget(self.csv_import_button)
        
        # Streaming section (direct widgets, no list container)
        self.streaming_container = QWidget()
        streaming_layout = QVBoxLayout(self.streaming_container)

        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter streaming URL")
        streaming_layout.addWidget(self.url_input)

        # container widget is just the radio buttons; we use a button group to manage them
        self.stream_mode_off = QRadioButton("Turn off streaming")
        self.stream_mode_mqtt = QRadioButton("Stream from MQTT")
        self.stream_mode_sse = QRadioButton("Stream from SSE")
        # default to off
        self.stream_mode_off.setChecked(True)

        self.stream_mode_group = QButtonGroup(self.streaming_container)
        self.stream_mode_group.addButton(self.stream_mode_off, 0)
        self.stream_mode_group.addButton(self.stream_mode_mqtt, 1)
        self.stream_mode_group.addButton(self.stream_mode_sse, 2)
        # connect change
        self.stream_mode_group.buttonClicked.connect(self.update_streaming_config)

        streaming_layout.addWidget(self.stream_mode_off)
        streaming_layout.addWidget(self.stream_mode_mqtt)
        streaming_layout.addWidget(self.stream_mode_sse)

        # Periodic update checkbox
    # Periodic update controls removed (streaming signals handle updates)

        layout.addWidget(self.streaming_container)
        return main_widget

    def import_csv_measurements(self):
        """Import measurements from CSV files with scenario selection."""
        # Validate scenario first
        is_valid, validation_error = validate_scenario_for_import(self.scenario)
        if not is_valid:
            try:
                self.main_window.statusBar().showMessage(f"Validation Error: {validation_error}", 5000)
            except Exception:
                pass
            return
        
        # Get available scenarios
        scenarios, error_message = get_available_scenarios("workspace")
        
        if error_message:
            try:
                if "No CSV measurement files found" in error_message:
                    self.main_window.statusBar().showMessage("No CSV measurement files found in 'workspace' directory.", 5000)
                elif "No scenario data found" in error_message:
                    self.main_window.statusBar().showMessage("No scenario data found in CSV files.", 5000)
                else:
                    # critical/errors stay until next message (timeout=0)
                    self.main_window.statusBar().showMessage(f"Error: {error_message}", 0)
            except Exception:
                pass
            return
        
        # Show scenario selection dialog
        dialog = ScenarioSelectionDialog(scenarios, self.main_window)
        
        if dialog.exec_() != QDialog.Accepted:
            return  # User cancelled
        
        selected_scenario = dialog.get_selected_scenario()
        if not selected_scenario:
            return
        # Ask for aggregation method
        agg_dialog = AggregationMethodDialog(self.main_window)
        if agg_dialog.exec_() != QDialog.Accepted:
            return  # User cancelled

        agg_method = agg_dialog.get_method()

        # Ask the importer to create and return a populated Scenario
        try:
            from data import importer as importer_module
            success, message, imported_scenario = importer_module.import_scenario(selected_scenario, workspace_dir="workspace", agg_method=agg_method)
        except Exception as e:
            success = False
            message = f"Import raised exception: {e}"
            imported_scenario = None

        if success and imported_scenario is not None:
            # Append the newly imported scenario to the application-level list
            app = getattr(self.main_window, 'app', None)
            if app is not None:
                app.scenarios.append(imported_scenario)
            # Set the plot to show the new scenario
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

            # Refresh UI to reflect the additional scenario
            # Refresh the scenarios tab list if present
            try:
                if hasattr(self.main_window, 'scenarios_tab') and self.main_window.scenarios_tab:
                    self.main_window.scenarios_tab.update()
            except Exception:
                pass
            self.main_window.update_all()
            try:
                self.main_window.statusBar().showMessage(f"Imported scenario '{selected_scenario}' ({agg_method})", 5000)
            except Exception:
                pass
        else:
            try:
                self.main_window.statusBar().showMessage(f"Import Error: {message}", 0)
            except Exception:
                pass

    def update_streaming_config(self):
        """Update streaming configuration based on checkbox state."""
        # Determine which radio is selected: 0=off,1=mqtt,2=sse
        selected_id = self.stream_mode_group.checkedId()
        if selected_id == 0:
            # Turn off streaming
            # stop SSE streamer if running
            try:
                self.scenario.stop_streaming()
            except Exception:
                pass
            # stop MQTT streamer if running
            try:
                if getattr(self, '_mqtt_streamer', None):
                    self._mqtt_streamer.stop()
                    self._mqtt_streamer = None
            except Exception:
                pass
            _LOG.info("Streaming turned off.")
            try:
                self.main_window.statusBar().showMessage("Streaming turned off.", 3000)
            except Exception:
                pass
        elif selected_id == 1:
            # MQTT selected - not implemented yet
            # Try to start a minimal MQTT streamer using the URL as broker/topic
            # URL format expected: mqtt://host:port[/topic] or host[:port][/topic]
            broker_spec = self.url_input.text().strip()
            if not broker_spec:
                try:
                    self.main_window.statusBar().showMessage("Please enter an MQTT broker URL/topic.", 5000)
                except Exception:
                    pass
                self.stream_mode_off.setChecked(True)
                return

            # parse broker_spec
            host = broker_spec
            port = 1883
            topic = '#'
            try:
                if host.startswith('mqtt://'):
                    host = host[len('mqtt://'):]
                if '/' in host:
                    host, topic = host.split('/', 1)
                if ':' in host:
                    host, port_s = host.split(':', 1)
                    port = int(port_s)
            except Exception:
                # fall back to treating whole string as host
                host = broker_spec

            # create streamer and start
            try:
                def _on_mqtt_message(topic_in, payload):
                    # minimal handler: attempt to decode payload as utf-8 text and log
                    try:
                        text = payload.decode('utf-8')
                    except Exception:
                        text = str(payload)
                    # TODO: parse payload and call scenario.update_relation as needed
                    _LOG.info("MQTT message on %s: %s", topic_in, text)
                    try:
                        # briefly notify user a message arrived
                        self.main_window.statusBar().showMessage(f"MQTT msg on {topic_in}", 2000)
                    except Exception:
                        pass

                # stop existing streamer first
                if getattr(self, '_mqtt_streamer', None):
                    self._mqtt_streamer.stop()

                self._mqtt_streamer = MQTTStreamer(_on_mqtt_message)
                self._mqtt_streamer.start(host, port=port, topic=topic)
                try:
                    self.main_window.statusBar().showMessage(f"Connected to MQTT {host}:{port} topic={topic}", 5000)
                except Exception:
                    pass
            except Exception:
                try:
                    self.main_window.statusBar().showMessage("Failed to start MQTT streamer.", 0)
                except Exception:
                    pass
                # revert to off
                self.stream_mode_off.setChecked(True)
        elif selected_id == 2:
            # SSE selected - use current behavior
            url = self.url_input.text().strip()
            if url:
                self.scenario.start_streaming(url)
            else:
                # revert to off and notify
                self.stream_mode_off.setChecked(True)
                try:
                    self.main_window.statusBar().showMessage("Please enter a valid Streaming URL for SSE.", 5000)
                except Exception:
                    pass
        else:
            # No selection or unknown id - treat as off
            self.scenario.stop_streaming()
            _LOG.info("Streaming turned off (unknown selection).")
            try:
                self.main_window.statusBar().showMessage("Streaming turned off.", 3000)
            except Exception:
                pass


"""
Data tab for the GDOP application.
"""

from PyQt5.QtWidgets import (
    QLineEdit, QPushButton, QVBoxLayout, QWidget,
    QDialog, QListWidget, QListWidgetItem, QDialogButtonBox,
    QLabel, QRadioButton, QButtonGroup
)
from .base_tab import BaseTab
from PyQt5.QtWidgets import QComboBox, QFormLayout
from data.mqtt_streamer import MQTTStreamer
from typing import Optional
import logging

_LOG = logging.getLogger(__name__)


# Scenario import moved to TreeTab; DataTab no longer provides CSV import UI.


# AggregationMethodDialog moved to `presentation/tabs/tree_tab.py`


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
    # CSV import moved to TreeTab; no csv_import_button here anymore
    
    @property
    def tab_name(self):
        return "Streaming"
        
    def create_widget(self):
        """Create and return the data tab widget."""
        # Create main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        # CSV import UI removed (handled in Tree tab)
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


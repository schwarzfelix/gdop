import threading
import logging

import requests
from sseclient import SSEClient
import json


_LOG = logging.getLogger(__name__)


class SSEUpdate:
    def __init__(self, id, source_id, destination_id, raw_distance):
        self.id = id
        self.source_id = source_id
        self.destination_id = destination_id
        self.raw_distance = raw_distance

    def __repr__(self):
        return f"SSEUpdate(id={self.id}, source_id={self.source_id}, destination_id={self.destination_id}, raw_distance={self.raw_distance})"


class SSEStreamingData:
    def __init__(self):
        self.status = None
        self.updates = []

    def update_status(self, status):
        self.status = status

    def add_update(self, update_data):
        update = SSEUpdate(
            id=update_data["id"],
            source_id=update_data["source_id"],
            destination_id=update_data["destination_id"],
            raw_distance=update_data["raw_distance"]
        )
        self.updates.append(update)


def process_sse_data(data, scenario):
    source_station = scenario.get_station_by_name(str(data["source_id"]))
    destination_station = scenario.get_station_by_name(str(data["destination_id"]))
    raw_distance = data["raw_distance"]
    scenario.measurements.update_relation(frozenset([source_station, destination_station]), raw_distance)
    # Emit measurements_changed signal if available
    if hasattr(scenario, 'window') and hasattr(scenario.window, 'plot'):
        scenario.window.plot.measurements_changed.emit()


def fetch_sse_streaming_data(url, scenario):
    streaming_data = SSEStreamingData()

    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        client = SSEClient(response)

        for event in client.events():
            if event.event == "connected":
                try:
                    status_data = json.loads(event.data)
                    streaming_data.update_status(status_data["status"])
                    _LOG.info("SSE status updated: %s", streaming_data.status)
                except json.JSONDecodeError as e:
                    _LOG.warning("Error decoding 'connected' event data: %s", e)
            elif event.event in ["update", "message"]:
                try:
                    update_data = json.loads(event.data)
                    streaming_data.add_update(update_data)
                    process_sse_data(update_data, scenario)
                except json.JSONDecodeError as e:
                    _LOG.warning("Error decoding event data: %s", e)
    except requests.RequestException as e:
        _LOG.error("Error fetching streaming data: %s", e)
    except Exception as e:
        _LOG.exception("Unexpected error while fetching SSE data: %s", e)


class SSEStreamer:
    def __init__(self, url, scenario):
        self.url = url
        self.scenario = scenario
        self.streaming_thread = threading.Thread(target=fetch_sse_streaming_data, args=(self.url, self.scenario,), daemon=True)
        self.streaming_thread.start()

    def stop_streaming(self):
        if self.streaming_thread.is_alive():
            self.streaming_thread.join(timeout=1)
            if self.streaming_thread.is_alive():
                _LOG.warning("SSEStreamer thread did not stop gracefully.")
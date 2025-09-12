"""
Compatibility shim for streaming API.

Historically this package provided `Streamer`, `StreamingData`, and related
functions in `data.streaming`. Streaming was SSE-specific. Now that we have
both SSE and MQTT streamers, the SSE implementation lives in
`data.sse_streamer`. This module keeps the old import path working by
re-exporting the SSE-specific names and including a deprecation note.
"""

from data.sse_streamer import SSEStreamer, fetch_sse_streaming_data, SSEStreamingData, SSEUpdate


# Backwards-compatible names
Streamer = SSEStreamer
fetch_streaming_data = fetch_sse_streaming_data
StreamingData = SSEStreamingData
Update = SSEUpdate


def _deprecated_note():
    # Intended for debugging; no-op in normal operation.
    try:
        import warnings
        warnings.warn("data.streaming is deprecated; use data.sse_streamer or data.mqtt_streamer instead", DeprecationWarning)
    except Exception:
        pass
import threading

import requests
from sseclient import SSEClient
import json


class Update:
    def __init__(self, id, source_id, destination_id, raw_distance):
        self.id = id
        self.source_id = source_id
        self.destination_id = destination_id
        self.raw_distance = raw_distance

    def __repr__(self):
        return f"Update(id={self.id}, source_id={self.source_id}, destination_id={self.destination_id}, raw_distance={self.raw_distance})"

class StreamingData:
    def __init__(self):
        self.status = None
        self.updates = []

    def update_status(self, status):
        self.status = status

    def add_update(self, update_data):
        update = Update(
            id=update_data["id"],
            source_id=update_data["source_id"],
            destination_id=update_data["destination_id"],
            raw_distance=update_data["raw_distance"]
        )
        self.updates.append(update)

def process_data(data, scenario):
    source_station = scenario.get_station_by_name(str(data["source_id"]))
    destination_station = scenario.get_station_by_name(str(data["destination_id"]))
    raw_distance = data["raw_distance"]
    scenario.measurements.update_relation(frozenset([source_station, destination_station]), raw_distance)
    # Emit measurements_changed signal if available
    if hasattr(scenario, 'window') and hasattr(scenario.window, 'plot'):
        scenario.window.plot.measurements_changed.emit()

def fetch_streaming_data(url, scenario):
    streaming_data = StreamingData()

    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        client = SSEClient(response)

        for event in client.events():
            if event.event == "connected":
                try:
                    status_data = json.loads(event.data)
                    streaming_data.update_status(status_data["status"])
                    print(f"Status updated: {streaming_data.status}")
                except json.JSONDecodeError as e:
                    print(f"Error decoding 'connected' event data: {e}")
            elif event.event in ["update", "message"]:
                try:
                    update_data = json.loads(event.data)
                    streaming_data.add_update(update_data)
                    process_data(update_data, scenario)
                except json.JSONDecodeError as e:
                    print(f"Error decoding event data: {e}")
    except requests.RequestException as e:
        print(f"Error fetching streaming data: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

class Streamer:
    def __init__(self, url, scenario):
        self.url = url
        self.scenario = scenario
        self.streaming_thread = threading.Thread(target=fetch_streaming_data, args=(self.url, self.scenario,), daemon=True)
        self.streaming_thread.start()

    def stop_streaming(self):
        if self.streaming_thread.is_alive():
            self.streaming_thread.join(timeout=1)
            if self.streaming_thread.is_alive():
                print("Streamer thread did not stop gracefully.")

"""
Refering to simulation/station/Tag/distances

Handle case of empty anchor list to avoid broadcasting errors.
If no anchors are defined, return an empty array.
I ran into a crash after entering a streaming URL before defining anchors

Status updated: connected
Traceback (most recent call last):
File "/home/bastian/Workspace/gdop/presentation/mainwindow.py", line 239, in update_display_config
    self.update_all()
File "/home/bastian/Workspace/gdop/presentation/mainwindow.py", line 300, in update_all
    self.plot.update_plot()
File "/home/bastian/Workspace/gdop/presentation/trilatplot.py", line 158, in update_plot
    gdop_values = [tag.dilution_of_precision() for tag in tags]
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/bastian/Workspace/gdop/simulation/station.py", line 132, in dilution_of_precision
    return geometry.dilution_of_precision(self.scenario.anchor_positions(), self.position(), self.distances())
                                                                                            ^^^^^^^^^^^^^^^^
File "/home/bastian/Workspace/gdop/simulation/station.py", line 129, in distances
    return geometry.euclidean_distances(self.scenario.anchor_positions(), self.position())
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/bastian/Workspace/gdop/simulation/geometry.py", line 4, in euclidean_distances
    distances = np.linalg.norm(anchor_positions - tag_position, axis=1)
                            ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~
ValueError: operands could not be broadcast together with shapes (0,) (2,)
[1]    8420 IOT instruction (core dumped)  python3 app.py


basti - br0sinski@github
"""
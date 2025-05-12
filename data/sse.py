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

class SSEData:
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

def process_data(data):
    print(f"Processing data: {data}")

def fetch_sse_data(url):
    sse_data = SSEData()

    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        client = SSEClient(response)

        for event in client.events():
            print(f"Raw Event: {event}")
            if event.event == "connected":
                try:
                    status_data = json.loads(event.data)
                    sse_data.update_status(status_data["status"])
                    print(f"Status updated: {sse_data.status}")
                except json.JSONDecodeError as e:
                    print(f"Error decoding 'connected' event data: {e}")
            elif event.event in ["update", "message"]:
                try:
                    update_data = json.loads(event.data)
                    sse_data.add_update(update_data)
                    process_data(update_data)
                except json.JSONDecodeError as e:
                    print(f"Error decoding event data: {e}")
    except requests.RequestException as e:
        print(f"Error fetching SSE data: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def test_function():
    url = "https://gps-no.legincy.de/api/v1/rangings/stream"
    fetch_sse_data(url)
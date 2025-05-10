import requests
from sseclient import SSEClient

def fetch_sse_data(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        client = SSEClient(response)

        for event in client.events():
            print(f"Event: {event.event}, Data: {event.data}")
    except requests.RequestException as e:
        print(f"Error fetching SSE data: {e}")

def test_function():
    url = "https://stream.wikimedia.org/v2/stream/recentchange"
    fetch_sse_data(url)
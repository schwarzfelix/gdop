"""
Minimal MQTT streamer helper for GDOP.
This module provides a small, optional wrapper around paho-mqtt to connect to
an MQTT broker, subscribe to a topic, and deliver incoming messages to a
callback function. It's intentionally minimal and non-blocking: the paho
client runs its network loop in a background thread.

Usage:
    streamer = MQTTStreamer(on_message_cb)
    streamer.start(broker_url, port=1883, topic="/gdop/measurements")
    streamer.stop()

The on_message_cb will be called with the (topic, payload_bytes) for each
incoming message. This module does not parse payloads - the caller should
implement parsing and updating the Scenario.
"""

from typing import Callable, Optional
import threading

try:
    import paho.mqtt.client as mqtt
except Exception:
    mqtt = None


class MQTTStreamer:
    def __init__(self, on_message: Callable[[str, bytes], None]):
        self.on_message = on_message
        # avoid forward-ref type annotation to keep linting simple
        self.client: Optional[object] = None
        self._thread = None
        self._connected = False

    def _ensure_mqtt_available(self):
        if mqtt is None:
            raise RuntimeError("paho-mqtt is not installed")

    def start(self, broker_url: str, port: int = 1883, topic: str = "#"):
        """Start the MQTT client and subscribe to topic.

        broker_url may be a hostname or include a scheme (we pass host to paho).
        """
        self._ensure_mqtt_available()

        if self.client is not None:
            # already started
            return

        def _on_connect(client, userdata, flags, rc):
            self._connected = True
            try:
                client.subscribe(topic)
            except Exception:
                pass

        def _on_message(client, userdata, msg):
            try:
                self.on_message(msg.topic, msg.payload)
            except Exception:
                # swallow exceptions from callback to keep loop alive
                pass

        self.client = mqtt.Client()
        self.client.on_connect = _on_connect
        self.client.on_message = _on_message

        # Start the client loop in a background thread
        def _run():
            try:
                # if broker_url includes scheme, strip it
                host = broker_url
                if host.startswith("mqtt://"):
                    host = host[len("mqtt://"):]
                self.client.connect(host, port)
                self.client.loop_forever()
            except Exception:
                # failed to connect or loop; mark disconnected
                self._connected = False

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def stop(self):
        try:
            if self.client is not None:
                try:
                    self.client.disconnect()
                except Exception:
                    pass
                try:
                    self.client.loop_stop()
                except Exception:
                    pass
                self.client = None
            self._connected = False
        except Exception:
            pass

 
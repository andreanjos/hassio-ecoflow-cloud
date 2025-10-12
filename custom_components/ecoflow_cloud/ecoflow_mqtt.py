from __future__ import annotations

import base64
import logging
import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict, Optional

import paho.mqtt.client as mqtt

from .const import MQTT_KEEPALIVE_SECONDS, MQTT_IDLE_FORCE_RECONNECT_SECONDS


LOG = logging.getLogger(__name__)


MessageHandler = Callable[[str, dict], None]


@dataclass
class Subscription:
    topic: str
    qos: int = 0


class EcoflowMqttClient:
    def __init__(self, broker_host: str, broker_port: int, client_id: str, username: str, password: str) -> None:
        self._client = mqtt.Client(client_id=client_id, clean_session=True)
        self._client.username_pw_set(username=username, password=password)
        self._client.reconnect_delay_set(min_delay=1, max_delay=60)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect

        self._broker_host = broker_host
        self._broker_port = broker_port

        self._subscriptions: Dict[str, Subscription] = {}
        self._message_handler: Optional[MessageHandler] = None

        self._last_packet_time = time.monotonic()
        self._watchdog_stop = threading.Event()
        self._watchdog_thread: Optional[threading.Thread] = None
        # metrics
        self._reconnects = 0
        self._published = 0

    def set_message_handler(self, handler: MessageHandler) -> None:
        self._message_handler = handler

    def connect_and_start(self) -> None:
        self._client.connect(self._broker_host, self._broker_port, keepalive=MQTT_KEEPALIVE_SECONDS)
        self._client.loop_start()
        self._start_watchdog()

    def stop(self) -> None:
        self._watchdog_stop.set()
        if self._watchdog_thread is not None:
            self._watchdog_thread.join(timeout=5)
        self._client.loop_stop()
        self._client.disconnect()

    def subscribe(self, topic: str, qos: int = 0) -> None:
        self._subscriptions[topic] = Subscription(topic=topic, qos=qos)
        self._client.subscribe(topic, qos=qos)

    def publish_base64(self, topic: str, payload_bytes: bytes, qos: int = 0, retain: bool = False) -> None:
        if not self._client.is_connected():
            LOG.debug("skip publish while disconnected: %s", topic)
            return
        b64 = base64.b64encode(payload_bytes).decode("ascii")
        self._client.publish(topic, b64, qos=qos, retain=retain)
        self._published += 1

    # Callbacks
    def _on_connect(self, client: mqtt.Client, userdata, flags, rc):
        LOG.info("MQTT connected rc=%s", rc)
        # Idempotent resubscribe
        for sub in self._subscriptions.values():
            self._client.subscribe(sub.topic, qos=sub.qos)

    def _on_disconnect(self, client: mqtt.Client, userdata, rc):
        LOG.warning("MQTT disconnected rc=%s", rc)
        self._reconnects += 1

    def _on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        self._last_packet_time = time.monotonic()
        if self._message_handler is None:
            return
        try:
            # The integration wraps protobuf inside JSON; caller should parse JSON then pass dict
            # Here we only pass raw topic + payload bytes for higher layer to parse.
            self._message_handler(msg.topic, {"raw": msg.payload})
        except Exception:  # meaningful handling at higher layers
            LOG.exception("message handler failed for topic=%s", msg.topic)

    # Watchdog forces reconnect if idle too long
    def _start_watchdog(self) -> None:
        def run():
            while not self._watchdog_stop.is_set():
                now = time.monotonic()
                if now - self._last_packet_time > MQTT_IDLE_FORCE_RECONNECT_SECONDS:
                    LOG.warning("MQTT idle > %ss; forcing reconnect", MQTT_IDLE_FORCE_RECONNECT_SECONDS)
                    try:
                        self._client.reconnect()
                        self._last_packet_time = now
                    except Exception:
                        LOG.exception("forced reconnect failed")
                self._watchdog_stop.wait(timeout=5)

        self._watchdog_thread = threading.Thread(target=run, name="ecoflow-mqtt-watchdog", daemon=True)
        self._watchdog_thread.start()

    # Diagnostics/metrics
    def get_metrics(self) -> dict:
        return {
            "reconnects": self._reconnects,
            "published": self._published,
            "seconds_since_last_packet": max(0, int(time.monotonic() - self._last_packet_time)),
        }


"""Define MQTT publishers."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, cast

from aiomqtt import Client, MqttError

from ecowitt2mqtt.config import Config
from ecowitt2mqtt.const import LOGGER
from ecowitt2mqtt.data import ProcessedData
from ecowitt2mqtt.helpers.publisher import Publisher
from ecowitt2mqtt.helpers.typing import CalculatedValueType

# Track sensors purged this session to prevent repeated execution
PURGED_SENSORS: set[str] = set()


def generate_mqtt_payload(data: CalculatedValueType) -> bytes:
    """Generate a binary MQTT payload from input data."""
    if isinstance(data, dict):
        converted_data = json.dumps(data, default=json_serializer)
    elif not isinstance(data, str):
        converted_data = str(data)
    else:
        converted_data = data
    return converted_data.encode("utf-8")


def json_serializer(obj: Any) -> float | int | str:
    """Define a custom JSON serializer."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


class MqttPublisher(Publisher):
    """Define a base MQTT publisher."""

    def __init__(self, config: Config, client: Client) -> None:
        """Initialize."""
        super().__init__(config)
        self._client = client

    async def async_check_and_delete(self, processed_data: ProcessedData) -> None:
        """Clear all topics for a specific sensor if requested in config."""
        sensor_to_delete = self._config.delete_sensor
        if not sensor_to_delete or sensor_to_delete in PURGED_SENSORS:
            return

        prefix = self._config.hass_discovery_prefix
        device_id = processed_data.device.unique_id
        
        # Sub-topics to wipe based on your discovery payload
        sub_topics = ["config", "state", "availability", "attributes"]
        
        LOGGER.info("Full purge triggered for sensor: %s", sensor_to_delete)

        for sub in sub_topics:
            topic = f"{prefix}/sensor/{device_id}/{sensor_to_delete}/{sub}"
            LOGGER.debug("Purging topic: %s", topic)
            try:
                # Empty payload with retain=True deletes the message from the broker
                await self._client.publish(topic, payload="", retain=True)
            except MqttError as err:
                LOGGER.error("Failed to purge topic %s: %s", topic, err)

        PURGED_SENSORS.add(sensor_to_delete)
        LOGGER.info("Successfully requested removal of %s from MQTT broker", sensor_to_delete)


class TopicPublisher(MqttPublisher):
    """Define an MQTT publisher that publishes to a topic."""

    async def async_publish(self, data: dict[str, CalculatedValueType]) -> None:
        """Publish to MQTT and handle deletions."""
        processed_data = ProcessedData(self._config, data)

        # Check for deletion flag before publishing new data
        await self.async_check_and_delete(processed_data)

        if not self._config.raw_data:
            data = {key: value.value for key, value in processed_data.output.items()}

        topic = cast(str, self._config.mqtt_topic)
        await self._client.publish(
            topic, payload=generate_mqtt_payload(data), retain=self._config.mqtt_retain
        )

        LOGGER.info("Published to %s", self._config.mqtt_topic)
import logging
import re

from .mqtt import mqtt
from ..helpers import get_kwargs
from ..helpers import key_wanted

log = logging.getLogger("domoticz_autodiscover")


class domoticz_autodiscover(mqtt):
    def __str__(self):
        return """outputs the to the supplied mqtt broker in hass format: eg "homeassistant/sensor/mpp_{tag}_{key}/state" """

    def __init__(self, *args, **kwargs) -> None:
        log.debug(f"__init__: kwargs {kwargs}")

    def build_msgs(self, *args, **kwargs):
        data = get_kwargs(kwargs, "data")
        tag = get_kwargs(kwargs, "tag")
        keep_case = get_kwargs(kwargs, "keep_case")

        filter = get_kwargs(kwargs, "filter")
        if filter is not None:
            filter = re.compile(filter)
        excl_filter = get_kwargs(kwargs, "excl_filter")
        if excl_filter is not None:
            excl_filter = re.compile(excl_filter)

        # Build array of mqtt messages with hass update format
        # assumes hass_config has been run
        # or hass updated manually
        msgs = []
        # Remove command and _command_description
        data.pop("_command", None)
        data.pop("_command_description", None)
        data.pop("raw_response", None)

        # Loop through responses
        for _key, values in data.items():
            unit = values[1]
            # remove spaces
            key = _key.replace(" ", "_")
            if not keep_case:
                # make lowercase
                key = key.lower()
            if key_wanted(key, filter, excl_filter):
                #
                # CONFIG / AUTODISCOVER
                #
                # <discovery_prefix>/<component>/[<node_id>/]<object_id>/config
                # topic "homeassistant/binary_sensor/garden/config"
                # msg '{"name": "garden", "device_class": "motion", "state_topic": "homeassistant/binary_sensor/garden/state", "unit_of_measurement": "°C"}'
                topic = f"homeassistant/sensor/mpp_{tag}_{key}/config"
                topic = topic.replace(" ", "_")
                state_topic = f"domoticz/sensor/mpp_{tag}_{key}/state"
                state_topic = state_topic.replace(" ", "_")

                name = f"{tag} {_key}"
                if unit == "W":
                    payload = f'{{"name": "{name}", "stat_t": "{state_topic}", "unit_of_meas": "{unit}", "uniq_id": "mpp_{tag}_{key}", "stat_cla": "measurement", "device_class": "power"  }}'
                else:
                    payload = f'{{"name": "{name}", "stat_t": "{state_topic}", "unit_of_meas": "{unit}", "uniq_id": "mpp_{tag}_{key}"  }}'
                # msg = {"topic": topic, "payload": payload, "retain": True}
                msg = {"topic": topic, "payload": payload}
                msgs.append(msg)
                #
                # VALUE SETTING
                #
                # payload = value
                # msg = {"topic": state_topic, "payload": payload}
                # msgs.append(msg)
        return msgs

    def output(self, *args, **kwargs):
        log.info("Using output processor: domoticz_autodiscover")
        log.debug(f"kwargs {kwargs}")
        data = get_kwargs(kwargs, "data")
        # exit if no data
        if data is None:
            return

        # get the broker instance
        mqtt_broker = get_kwargs(kwargs, "mqtt_broker")
        # exit if no broker
        if mqtt_broker is None:
            return

        # Get device name for routing
        device_name = get_kwargs(kwargs, "name", "mppsolar")

        # build the messages...
        msgs = self.build_msgs(**kwargs)
        log.debug(f"domoticz_autodiscover.output msgs {msgs}")

        # publish
        mqtt_broker.publishMultiple(msgs, device_name=device_name)

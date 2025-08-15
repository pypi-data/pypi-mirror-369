import logging
import re

from .mqtt import mqtt
from ..helpers import get_kwargs
from ..helpers import key_wanted

log = logging.getLogger("tag_mqtt")


class tag_mqtt(mqtt):
    def __str__(self):
        return "outputs the to the supplied mqtt broker using the supplied tag as the topic: eg {tag}/max_charger_range 120.0"

    def __init__(self, *args, **kwargs) -> None:
        log.debug(f"__init__: kwargs {kwargs}")

    def build_msgs(self, *args, **kwargs):
        data = get_kwargs(kwargs, "data")
        tag = get_kwargs(kwargs, "tag")
        keep_case = get_kwargs(kwargs, "keep_case")
        _topic = get_kwargs(kwargs, "topic", default="mpp-solar")
        if tag is None:
            tag = _topic
        filter = get_kwargs(kwargs, "filter")
        if filter is not None:
            filter = re.compile(filter)
        excl_filter = get_kwargs(kwargs, "excl_filter")
        if excl_filter is not None:
            excl_filter = re.compile(excl_filter)

        # Build array of Influx Line Protocol II messages
        # Message format is: mpp-solar,command=QPGS0 max_charger_range=120.0
        #                    mpp-solar,command=inverter2 parallel_instance_number="valid"
        #                    measurement,tag_set field_set
        msgs = []
        # Remove command and _command_description
        cmd = data.pop("_command", None)
        data.pop("_command_description", None)
        data.pop("raw_response", None)
        if tag is None:
            tag = cmd
        # Loop through responses
        for key, values in data.items():
            value = values[0]
            # remove spaces
            key = key.replace(" ", "_")
            if not keep_case:
                # make lowercase
                key = key.lower()
            if key_wanted(key, filter, excl_filter):
                msg = {
                    "topic": f"{tag}/{key}",
                    "payload": value,
                }
                msgs.append(msg)
        return msgs

    def output(self, *args, **kwargs):
        log.info("Using output processor: tag_mqtt")
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
        log.debug(f"tag_mqtt.output msgs {msgs}")

        # publish
        mqtt_broker.publishMultiple(msgs, device_name=device_name)

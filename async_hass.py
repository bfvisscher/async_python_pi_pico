# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT


#  Class and methods used to connect to Home Assistant via hass_mqtt
#
#  Compatible with MQTT discovery!!
#
#  Most of the standard setup is being taken care off.
#  Different entities are defined in hass_entities
#
# Any publish are queued and processed in order of arrival. This allows easy use of the methods
# without delays to the running coroutine

import binascii
import json
import os

import machine
import uasyncio
import ucollections

# from copy import deepcopy

hass_device = {
    "identifiers": os.uname()[0] + binascii.hexlify(machine.unique_id()).decode("utf-8"),
    "suggested_area": "Lab",
    "model": os.uname()[-1],
    "name": os.uname()[0] + ' [' + binascii.hexlify(machine.unique_id()).decode("utf-8") + ']',
    "manufacturer": "Raspberry Pi Ltd",
    "sw_version": os.uname()[3]
}


class HomeAssistantEntity:
    def __init__(self, name, entity_type, ha: "HomeAssistantMQTT", config, initial_state=None, callback=None,
                 device=hass_device, qos=1):
        if isinstance(config, (dict, list)):
            config = config.copy()
        if isinstance(initial_state, (dict, list)):
            initial_state = initial_state.copy()

        self.name = name
        self.entity_type = entity_type

        self._ha = ha
        self.callback = callback
        self.state = initial_state

        self.qos = qos
        config['name'] = name
        if device is not None:
            config['device'] = device.copy()

        if "unique_id" not in config:
            config['unique_id'] = self.name.lower().replace(' ', '_') + '_' + binascii.hexlify(
                machine.unique_id()).decode(
                "utf-8")

        self.entity_topic = "%s/%s/%s" % (ha.topic_prefix, entity_type, config['unique_id'])
        if '~' not in config:
            config['~'] = self.entity_topic

        self.state_topic = None
        if initial_state is not None:
            self.state = initial_state
            if 'stat_t' in config:
                state_topic = config['stat_t']
            elif 'state_topic' in config:
                state_topic = config['state_topic']
            else:
                config['stat_t'] = '~/state'
                state_topic = '~/state'
            self.state_topic = state_topic.replace('~', config['~'])
            self.publish_state()

        self.command_topic = None
        if self.callback is not None:
            if 'cmd_t' in config:
                command_topic = config['cmd_t']
            elif 'command_topic' in config:
                command_topic = config['command_topic']
            else:
                config['cmd_t'] = '~/cmd'
                command_topic = '~/cmd'
            self.command_topic = command_topic.replace('~', config['~'])
            self._ha.subscribe(self.command_topic, qos=1, callback=self)

        # remove any None entries
        keys_to_delete = []
        for k, v in config.items():
            if v is None:
                keys_to_delete.append(k)
        for k in keys_to_delete:
            del config[k]

        # make configuration available for HA hass_mqtt discovery
        self._ha.publish(self.entity_topic + '/config', json.dumps(config), qos=1, retain=True)
        self.config = config

    def publish_state(self):
        self._ha.publish(self.state_topic, json.dumps(self.state), qos=self.qos, retain=True)

    def __call__(self, message, retain):  # command topic messages
        try:
            message = json.loads(message)
        except:
            message = message.decode('utf-8')  # convert to string

        new_state = self.callback(self, message)

        if new_state and self.state_topic:
            self.publish_state()


class HomeAssistantMQTT:
    topic_prefix = 'homeassistant'

    def __init__(self, url, user, password, wifi_ssid, wifi_password, quick=False):
        self.publish_queue = []
        self.publish_qos0 = ucollections.OrderedDict()
        self.subscribe_queue = []
        self.callbacks = {}
        self._mqtt_client = None
        self._mqtt_connect = {'url': url, 'user': user, 'password': password, 'wifi_ssid': wifi_ssid,
                              'wifi_password': wifi_password, 'quick': quick}
        self.anything_todo = uasyncio.Event()
        self.connected = False
        self.task = uasyncio.create_task(self.update())

    def is_connected(self):
        return self.connected and self._mqtt_client.isconnected()

    async def connect(self, url, user, password, wifi_ssid, wifi_password, quick=False):
        from async_mqtt import MQTTClient, mqtt_config
        url_split = url.split(':')
        config = mqtt_config.copy()

        config['ssid'] = wifi_ssid
        config['wifi_pw'] = wifi_password
        config['subs_cb'] = self.mqtt_callback
        config['server'] = url_split[0]
        config['port'] = int(url_split[1]) if len(url_split) == 2 else 1883  # default hass_mqtt port
        config['user'] = user
        config['password'] = bytearray(password)

        self._mqtt_client = MQTTClient(config)
        await self._mqtt_client.connect(quick=quick)

    def publish(self, topic, message, qos=0, retain=False):
        if qos == 0:
            self.publish_qos0[topic] = (message, retain)
        else:
            self.publish_queue.append((topic, message, qos, retain))
        self.anything_todo.set()

    def mqtt_callback(self, topic, msg, retained):
        topic = topic.decode("utf-8")
        if topic in self.callbacks:
            self.callbacks[topic](msg, retained)

    def subscribe(self, topic, callback, qos=1):
        self.subscribe_queue.append((topic, qos))
        self.callbacks[topic] = callback
        self.anything_todo.set()

    async def update(self):
        print('HASS MQTT Connecting...')
        await self.connect(**self._mqtt_connect)
        self.connected = True
        print('HASS MQTT connected!')
        while True:
            while len(self.publish_queue) > 0 or len(self.subscribe_queue) > 0 or len(self.publish_qos0) > 0:
                if len(self.subscribe_queue) > 0:
                    msg = self.subscribe_queue.pop(0)
                    await self._mqtt_client.subscribe(*msg)
                elif len(self.publish_queue) > 0:
                    msg = self.publish_queue.pop(0)
                    await self._mqtt_client.publish(*msg)
                elif len(self.publish_qos0) > 0:
                    (topic, (msg, retain)) = self.publish_qos0.popitem()
                    await self._mqtt_client.publish(topic, msg, 0, retain)

            self.anything_todo.clear()
            await self.anything_todo.wait()

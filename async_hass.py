#  Class and methods used to connect to Home Assistant via mqtt
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

hass_device = {
    "identifiers": binascii.hexlify(machine.unique_id()),
    "suggested_area": "Lab",
    "model": os.uname()[-1],
    "manufacturer": "Raspberry Pi Ltd",
    "sw_version": os.uname()[3]
}


class HomeAssistantEntity:

    def __init__(self, name, entity_type, ha: "HomeAssistantMQTT", config, initial_state=None, cmd_callback=None,
                 device=hass_device, qos=1):
        self.name = name
        self.entity_type = entity_type

        self._ha = ha
        self.cmd_callback = cmd_callback
        self.state = initial_state

        self.qos = qos
        config['name'] = name
        # if device is not None:
        #    config['device'] = device

        if "unique_id" not in config:
            config['unique_id'] = binascii.hexlify(machine.unique_id()).decode(
                "utf-8") + '_' + self.name.lower().replace(' ', '_')

        self.entity_topic = "%s/%s/%s" % (ha.topic_prefix, entity_type, config['unique_id'])
        if '~' not in config:
            config['~'] = self.entity_topic

        if initial_state is not None:
            self.state = initial_state
            if 'stat_t' in config:
                state_topic = config['stat_t']
            elif 'state_topic' in config:
                state_topic = config['state_topic']
            else:
                config['stat_t'] = '~/state'
                state_topic = config['~'] + '/state'
            self.state_topic = state_topic.replace('~', config['~'])
            if len(initial_state) != 0:
                self.publish_state()

        if cmd_callback is not None:
            if 'cmd_t' in config:
                command_topic = config['cmd_t']
            elif 'command_topic' in config:
                command_topic = config['command_topic']
            else:
                config['cmd_t'] = '~/cmd'
                command_topic = config['~'] + '/cmd'
            command_topic.replace('~', config['~'])
            self._ha.subscribe(command_topic, qos=1, callback=self)

        # make configuration available for HA mqtt discovery
        self._ha.publish(self.entity_topic + '/config', json.dumps(config), qos=1, retain=True)
        self.config = config.copy()

    def publish_state(self):
        self._ha.publish(self.state_topic, json.dumps(self.state), qos=self.qos, retain=True)

    def __call__(self, message, retain):  # command topic messages
        new_state = self.cmd_callback(self, json.loads(message))
        if new_state:
            self.state = new_state
            self.publish_state()


class HomeAssistantMQTT:
    topic_prefix = 'homeassistant'

    def __init__(self, url, user, password, wifi_ssid, wifi_password, quick=False):
        self.publish_queue = []
        self.subscribe_queue = []
        self.callbacks = {}
        self._mqtt_client = None
        self._mqtt_connect = {'url': url, 'user': user, 'password': password, 'wifi_ssid': wifi_ssid,
                              'wifi_password': wifi_password, 'quick': quick}
        self.anything_todo = uasyncio.Event()

        self.task = uasyncio.create_task(self.update())

    async def connect(self, url, user, password, wifi_ssid, wifi_password, quick=False):
        from async_mqtt import MQTTClient, mqtt_config
        url_split = url.split(':')
        config = mqtt_config.copy()

        config['ssid'] = wifi_ssid
        config['wifi_pw'] = wifi_password
        config['subs_cb'] = self.mqtt_callback
        config['server'] = url_split[0]
        config['port'] = int(url_split[1]) if len(url_split) == 2 else 1883  # default mqtt port
        config['user'] = user
        config['password'] = bytearray(password)

        self._mqtt_client = MQTTClient(config)
        await self._mqtt_client.connect(quick=quick)

    def publish(self, topic, message, qos=0, retain=False):
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
        await self.connect(**self._mqtt_connect)
        while True:
            await self.anything_todo.wait()
            while len(self.publish_queue) > 0 or len(self.subscribe_queue) > 0:
                if len(self.publish_queue) > 0:
                    msg = self.publish_queue.pop(0)
                    await self._mqtt_client.publish(*msg)
                elif len(self.subscribe_queue) > 0:
                    msg = self.subscribe_queue.pop(0)
                    await self._mqtt_client.subscribe(*msg)
                # await uasyncio.sleep_ms(10) # small pause to let messages be processed

            self.anything_todo.clear()

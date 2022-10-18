# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT


import json

import async_hass
from async_runner import add_task, start_tasks
from async_tasks import heartbeat, cpu_load
from hass_entities import HassButton, HassNumber, HassLight, HassSensor

with open('secrets.json', 'rt') as f:
    secrets = json.load(f)

hass_mqtt = async_hass.HomeAssistantMQTT('192.168.68.11:1883', secrets['mqtt.username'],
                                         secrets['mqtt.password'],
                                         secrets['wifi.ssid'], secrets['wifi.password'])


def test_callback(entity, state):
    print(entity.name, state)
    return state


button_1 = HassButton(hass_mqtt, 'button1', test_callback)
button_2 = HassButton(hass_mqtt, 'button2', test_callback)
button_3 = HassButton(hass_mqtt, 'button3', test_callback)
button_4 = HassButton(hass_mqtt, 'button4', test_callback)

entity_1 = HassNumber(hass_mqtt, 'Number 1', test_callback, initial_value=0, min_value=-50,
                      max_value=50, use_box=True)

entity_2 = HassNumber(hass_mqtt, 'Number 2', test_callback, initial_value=0, min_value=-50,
                      max_value=50, use_box=False)

light1 = HassLight(hass_mqtt, 'Light_1', test_callback, color_mode='rgb')
light2 = HassLight(hass_mqtt, 'Light_2', test_callback, color_mode='rgbw')


def test(name, poll_ms=1000):
    entity = HassSensor(hass_mqtt, name, 0)
    while True:
        entity.state = (entity.state + 1) % 20
        entity.publish_state()
        yield poll_ms


add_task(heartbeat)
add_task(cpu_load, mqtt=hass_mqtt, time_between_report_ms=5000)
add_task(test, 'sensor_1', poll_ms=500)
add_task(test, 'sensor_2', poll_ms=2500)

start_tasks()

import json
import time
from machine import Pin

import async_hass
from angular_servo import AngularServo
from async_hcsr04 import HCSR04, SignalTimer
from async_ky040 import KY040
from async_runner import add_task, start_tasks
from async_tasks import heartbeat, cpu_load
from dc_motor import DCMotor
from hass_entities import HassNumber, HassSensor, HassButton

with open('secrets.json', 'rt') as f:
    secrets = json.load(f)

hass_mqtt = async_hass.HomeAssistantMQTT('192.168.68.11:1883', secrets['mqtt.username'],
                                         secrets['mqtt.password'],
                                         secrets['wifi.ssid'], secrets['wifi.password'])


class OmniPlatform:
    def __init__(self, stall_zone=.3, freq=1000, hass_mqtt = None):

        
        self.hs_speed = HassNumber(hass_mqtt, 'Speed', self.speed, initial_value=0, min_value=-1,
                              max_value=1, step=.05, use_box=False)
        self.hs_strafe = HassNumber(hass_mqtt, 'Strafe', self.strafe, initial_value=0, min_value=-1,
                               max_value=1, step=.05, use_box=False)
        self.hs_rotation = HassNumber(hass_mqtt, 'Rotation', self.rotation, initial_value=0, min_value=-1,
                                 max_value=1, step=.05, use_box=False)

        self.power_limiter = HassNumber(hass_mqtt, 'Power Limit', self.power_limit, initial_value=.30, min_value=.3,
                                   max_value=1, step=.05, use_box=False)
        self.stall_zone = HassNumber(hass_mqtt, 'Stall Zone', self.stall_zone, initial_value=.3, min_value=0,
                                max_value=.9, step=.05, use_box=False)

        stop_button = HassButton(hass_mqtt, 'Stop', self.stop)

        self.wheel_lb = DCMotor(13, 12, 11, stall_zone=stall_zone, pwm_freq=freq)
        self.wheel_rb = DCMotor(8, 9, 7, stall_zone=stall_zone, pwm_freq=freq)
        self.wheel_lf = DCMotor(2, 3, 14, stall_zone=stall_zone, pwm_freq=freq)
        self.wheel_rf = DCMotor(5, 6, 4, stall_zone=stall_zone, pwm_freq=freq)

        self.wheels = [self.wheel_rf, self.wheel_lf, self.wheel_rb, self.wheel_lb]
        self._power_limit = 1


    def test_wheels(self):
        for wh in self.wheels:
            print("Clockwise")
            wh.throttle(.5)
            time.sleep(2)
            print("Counter Clockwise")
            wh.throttle(-.5)
            time.sleep(2)
            print('Stop')
            wh.throttle(0)
            time.sleep(2)
    

    def set_throttle(self, values):
        for w, v in zip(self.wheels, values):
            w.throttle(v)

    def strafe(self, entity, command):
        print("strafe : %s" % command)
        command *= self._power_limit
        self.set_throttle([-command, -command, command, command])
        self.hs_speed.state = 0
        self.hs_speed.publish_state()
        self.hs_rotation.state = 0
        self.hs_rotation.publish_state()
        return command

    def speed(self, entity, command):
        print("speed : %s" % command)
        command *= self._power_limit
        self.set_throttle([command, -command, command, -command])
        self.hs_rotation.state = 0
        self.hs_rotation.publish_state()
        self.hs_strafe.state = 0
        self.hs_strafe.publish_state()
        return command

    def rotation(self, entity, command):
        print("rotation : %s" % command)
        command *= self._power_limit
        self.set_throttle([command, command, command, command])
        self.hs_speed.state = 0
        self.hs_speed.publish_state()
        self.hs_strafe.state = 0
        self.hs_strafe.publish_state()
        
        return command

    def rotary_knob(self, event):
        print('event   %i' % event)

    def power_limit(self, entity, command):
        self._power_limit = command
        return command

    def stall_zone(self, entity, command):
        print("stall_zone : %s" % command)
        for whl in self.wheels:
            whl.stall_zone = command
        return command

    def stop(self, entity, command):
        for w in self.wheels:
            w.stop()
        self.hs_speed.state = 0
        self.hs_speed.publish_state()
        self.hs_rotation.state = 0
        self.hs_rotation.publish_state()
        self.hs_strafe.state = 0
        self.hs_strafe.publish_state()
            

def mobile_platform(hass_mqtt, stall_zone=.4, freq=5000):
    op = OmniPlatform(hass_mqtt=hass_mqtt)


    range_sensor = HassSensor(hass_mqtt, 'Range', unit_of_measurement='cm')    


    def ranging_cb(measure):
        range_sensor.state = measure
        range_sensor.publish_state()

    rot = KY040(clk_pin=20, dt_pin=19, sw_pin=18, callback=op.rotary_knob)

    trigger_pin = Pin(26, Pin.OUT, 0)
    echo_feedback = HCSR04(signal_pin=27, callback=ranging_cb, measure=SignalTimer.TIME_HIGH, hard=True)
    servo = AngularServo(10)
    step = 45
    delay_ms = 125
    yield 1000
    while True:
        for angle in range(0, 90, step):
            servo.angle = angle
            yield delay_ms - 10
            trigger_pin.value(1)
            yield 10
            trigger_pin.value(0)
            yield delay_ms
        for angle in range(90, -90, -step):
            servo.angle = angle
            yield delay_ms - 10
            trigger_pin.value(1)
            yield 10
            trigger_pin.value(0)
            yield delay_ms
        for angle in range(-90, 0, step):
            servo.angle = angle
            yield delay_ms - 10
            trigger_pin.value(1)
            yield 10
            trigger_pin.value(0)
            yield delay_ms


add_task(mobile_platform, hass_mqtt)
add_task(cpu_load)
add_task(heartbeat)
start_tasks()

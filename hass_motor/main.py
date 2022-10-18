import math
import json

from async_runner import *
from async_tasks import cpu_load, heartbeat
from machine import ADC, Pin, PWM
import async_hass
import hass_entities

with open('secrets.json', 'rt') as f:
    secrets = json.load(f)

hass_mqtt = async_hass.HomeAssistantMQTT('192.168.68.11:1883', secrets['mqtt.username'],
                                         secrets['mqtt.password'],
                                         secrets['wifi.ssid'], secrets['wifi.password'])


def motor_control():
    


    in1Pin = Pin(15, Pin.OUT)
    in2Pin = Pin(16, Pin.OUT)
    pwm = PWM(Pin(17))  # enable(GP17)
    pwm.freq(1000)
    pwm.duty_u16(512)
    adc = ADC(26)

    def driveMotor(dr, spd):
        if dr:
            in1Pin.value(1)
            in2Pin.value(0)
        else:
            in1Pin.value(0)
            in2Pin.value(1)
        pwm.duty_u16(spd)


        
    def speed_cb(entity, msg):
        
        new_speed = min(65536, int(math.fabs(msg) * 655.36))
        print(msg, new_speed)
        driveMotor(msg > 0, new_speed)
        return msg

    speed = hass_entities.HassNumber(hass_mqtt, 'Speed', speed_cb, initial_value=0, min_value=-100,
                      max_value=100, use_box=False)

    def stop_cb(entity, msg):
        print('stop')
        speed.state = 0
        speed.publish_state()        
        
        driveMotor(0,0)
        
    stop_button = hass_entities.HassButton(hass_mqtt, 'Stop', stop_cb)

    try:
        while True:
            yield 50000
    except:
        pwm.deinit()



add_task(motor_control)
add_task(cpu_load, mqtt=hass_mqtt, time_between_report_ms=5000)
add_task(heartbeat)

# start all the tasks ***********************************************************
start_tasks()


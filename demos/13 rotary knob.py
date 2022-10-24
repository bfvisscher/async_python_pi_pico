# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT


from async_ky040 import KY040
from async_runner import add_task, start_tasks
from async_tasks import heartbeat, cpu_load


# HARDWARE SETUP:
# Materials:
#            one KY040 rotary knob
#       KY040:
#            connect the GND and v3.3
#            connect SW  to pin 18
#            connect DT  to pin 19
#            connect CLK to pin 20


def rotary_change_handler(event):
    print("Rotary Event : {0:04b}".format(event))
    if event & KY040.PRESS:
        print('Button has been PRESSED')
    if event & KY040.RELEASE:
        print('Button has been RELEASED')
    if event & KY040.CLOCKWISE:
        print('CLOCKWISE step detected')
    if event & KY040.COUNTER_CLOCKWISE:
        print('COUNTER CLOCKWISE  step detected')


ky40 = KY040(clk_pin=20, dt_pin=19, sw_pin=18, callback=rotary_change_handler)

add_task(heartbeat)
add_task(cpu_load)
start_tasks()

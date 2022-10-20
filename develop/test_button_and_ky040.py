# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT



from async_ky040 import Button, KY040
from async_runner import add_task, start_tasks
from async_tasks import heartbeat, cpu_load, reset_if_unresponsive
from async_pb_drivers import neo_driver_dma
from patterns import kit

def b1_change_handler(delta):
    print("B1:", delta) 


def b2_change_handler(delta):
    print("B2:", delta)


def b3_change_handler(delta):
    print("B3:", delta)
    while True: # force system to become unresponsive
        pass






b1 = Button(19, b1_change_handler)
b2 = Button(20, b2_change_handler)
b3 = Button(21, b3_change_handler)


def change_handler(delta):
    print("RO:",delta)


ky40 = KY040(clk_pin=4, dt_pin=3, sw_pin=2, callback=change_handler)


add_task(neo_driver_dma, pin=6, n=7, bpp=3, pattern=kit, pixel=[127,0,0])
# add_task(reset_if_unresponsive)
add_task(heartbeat)
add_task(cpu_load)

start_tasks()

# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT


from async_button import Button
from async_runner import add_task, start_tasks
from async_tasks import heartbeat, cpu_load


# HARDWARE SETUP:
# Materials:
#            one button 
#       button:
#            connect the button to GND and pin 18 (uses pi pico pin pull-up so no other resistors required)


def button_change_handler(event):
    print("Button Event : {0:04b}".format(event))
    if event & Button.PRESS:
        print('Button has been PRESSED')
    if event & Button.RELEASE:
        print('Button has been RELEASED')


# The Button class automatically de-bounces (events only occur after 4 identical measurements at 5ms intervals)
# and calls the button_change_handler in the async loop
b1 = Button(pin=18, callback=button_change_handler)

add_task(heartbeat)
add_task(cpu_load)

start_tasks()

from machine import Pin

from async_runner import add_task, start_tasks
from gbl import ON_BOARD_LED_PIN


# seeing some code duplication so lets simplify

# HARDWARE SETUP:
#   2 x red LED + 2x 220ohm resistor
#   add the LED on pin 27 and 28


# Define the tasks ***********************************************************

# simple example of a blinking LED but with pin as parameter


def blinking_led(pin_id):
    pin = Pin(pin_id, Pin.OUT)
    while True:
        pin.on()
        yield 200
        pin.off()
        yield 800


# Add the tasks ****************************************************************
add_task(blinking_led, pin_id=ON_BOARD_LED_PIN)
add_task(blinking_led, pin_id=27)
add_task(blinking_led, pin_id=28)

# start all the tasks **********************************************************
start_tasks()

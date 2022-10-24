from machine import Pin

from async_runner import add_task, start_tasks
from gbl import ON_BOARD_LED_PIN


# ON_BOARD_LED_PIN is automatically set to the internal LED pin.
# that is pin 25 for the Pi Pico or 'LED' when using Pi Pico W)


# This library implements async methods to make development easier
# Scripts will contain three sections
# 1 - define the tasks
# 2 - add the tasks
# 3 - start the tasks

# HARDWARE SETUP:
#  Just your pi pico (w) and nothing else


# Define the tasks ************************************************************

# simple example of a blinking LED

def blinking():
    pin = Pin(ON_BOARD_LED_PIN, Pin.OUT)
    while True:
        pin.on()
        yield 200  # instead of using sleep_ms(200), use yield, this time can now be used by other processes
        # Note : using yield with an integer will wait from the last yield so the time of any
        #        statements being executed is ignored allowing for PERFECT synchonisation

        pin.off()
        yield 800


# Add the tasks *****************************************************************
add_task(blinking)

# start all the tasks ***********************************************************
start_tasks()

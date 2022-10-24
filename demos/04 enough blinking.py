from machine import Pin

from async_runner import add_task, start_tasks
from async_tasks import cpu_load
from gbl import ON_BOARD_LED_PIN


# seeing some code duplication so lets simplify

# HARDWARE SETUP:
#   2 x red LED + 2x 220ohm resistor
#   add the LED on pin 27 and 28

# Define the tasks ***********************************************************

# added additional parameters with default values


def blinking_led(pin_id, on_time_ms=200, off_time_ms=800):
    pin = Pin(pin_id, Pin.OUT)
    while True:
        pin.on()
        yield on_time_ms
        pin.off()
        yield off_time_ms


# Add the tasks ****************************************************************

# 25 for on-board LED  (or 'LED' when using Pi Pico W)
# events the blinking to twice per second
add_task(blinking_led, pin_id=ON_BOARD_LED_PIN, on_time_ms=100, off_time_ms=400)

add_task(blinking_led, pin_id=27)  # use default parameters
add_task(blinking_led, pin_id=28, on_time_ms=400, off_time_ms=1600)  # twice as slow

add_task(cpu_load)  # task that shows how much memory and cpu load is being used

# start all the tasks **********************************************************
start_tasks()

from machine import Pin

from async_runner import add_task, start_tasks


# This library implements async methods to make development easier
# Scripts will contain three sections
# 1 - define the tasks
# 2 - add the tasks
# 3 - start the tasks


# Define the tasks ************************************************************

# simple example of a blinking LED

def blinking():
    pin = Pin(25, Pin.OUT)  # 25 for on-board LED  (or 'LED' when using Pi Pico W)
    while True:
        pin.on()
        yield 200  # instead of saying sleep_ms(200), use yield, this time can now be used by other processes
        # Note : using yield with an integer will wait from the last yield so the time of any
        #        statements being executed is ignored allowing for PERFECT synchonisation

        pin.off()
        yield 800


# Add the tasks *****************************************************************
add_task(blinking)

# start all the tasks ***********************************************************
start_tasks()

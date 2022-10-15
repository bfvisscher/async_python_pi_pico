from machine import Pin

from async_runner import add_task, start_tasks


# now that we added a single task, lets add on more to see how easy it is.

# setup : add an LED on pin 15


# Define the tasks ***********************************************************

# simple example of a blinking LED with

def blinking_on_board():
    pin = Pin(25, Pin.OUT)  # 25 for on-board LED  (or 'LED' when using Pi Pico W)
    while True:
        pin.on()
        yield 200
        pin.off()
        yield 800


def blinking_led():
    pin = Pin(15, Pin.OUT)
    while True:
        pin.on()
        yield 200
        pin.off()
        yield 800


# Add the tasks ****************************************************************
add_task(blinking_on_board)
add_task(blinking_led)

# start all the tasks **********************************************************
start_tasks()

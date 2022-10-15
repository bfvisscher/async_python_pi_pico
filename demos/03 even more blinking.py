from machine import Pin

from async_runner import add_task, start_tasks


# seeing some code duplication so lets simplify

# setup : add an LED on pin 15


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
add_task(blinking_led, pin_id=25)  # 25 for on-board LED  (or 'LED' when using Pi Pico W)
add_task(blinking_led, pin_id=15)

# start all the tasks **********************************************************
start_tasks()

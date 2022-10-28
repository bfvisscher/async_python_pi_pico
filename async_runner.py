# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT


import gc
import time

import rp2
import uasyncio
from machine import Pin, PWM


def as_pins(pin_ids, *nargs, **kwargs):
    pins = []
    for pin_id in pin_ids:
        pin = Pin(pin_id, *nargs, **kwargs)
        pins.append(pin)
    return pins


def as_pwm(pin_ids, freq):
    pwm_pins = []
    for pin in pin_ids:
        pin = PWM(Pin(pin, Pin.OUT))
        pin.freq(freq)
        pwm_pins.append(pin)
    return pwm_pins


async def _run(fcn, *nargs, exception_handler, **kwargs) -> None:
    try:
        last_wait_time = time.ticks_ms()
        for item in fcn(*nargs, **kwargs):
            gc.collect()  # for gc to keep things smooth
            if isinstance(item, int):
                last_wait_time = time.ticks_add(last_wait_time, item)
                wait_for_ms = time.ticks_diff(last_wait_time, time.ticks_ms())
                if wait_for_ms < 0:
                    wait_for_ms = 0
                await uasyncio.sleep_ms(wait_for_ms)
            else:
                await item
                last_wait_time = time.ticks_ms()
    except Exception as e:
        if exception_handler:
            exception_handler(e)
        else:
            raise


def add_task(fcn, *nargs, exception_handler=None, **kwargs):
    return uasyncio.create_task(_run(fcn, *nargs, exception_handler=exception_handler, **kwargs))


def start_tasks():
    print('Starting tasks')

    # not available in rp2 port
    # sys.atexit(cleanup)
    gc.collect()
    gc.disable()
    try:
        uasyncio.get_event_loop().run_forever()
    finally:
        gc.collect()
        gc.enable()
        cleanup()


def cleanup():
    print('Removing all PIO programs')

    # https://github.com/micropython/micropython/issues/9003
    for i in range(2):
        rp2.PIO(i).remove_program()

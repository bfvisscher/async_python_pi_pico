import time

import uasyncio
from machine import Pin, PWM



def as_pins(pin_ids, *nargs, **kwargs):
    pins = []
    for pin_id in pin_ids:
        pin = Pin(pin_id, *nargs, **kwargs)
        pins.append(pin)
    return pins


def as_pwm(pin_ids, freq_pwm):
    pwm_pins = []
    for pin in pin_ids:
        pin = PWM(Pin(pin, Pin.OUT))
        pin.freq(freq_pwm)
        pwm_pins.append(pin)
    return pwm_pins


async def _run(fcn, *nargs, **kwargs) -> None:
    last_wait_time = time.ticks_ms()
    for item in fcn(*nargs, **kwargs):
        if isinstance(item, int):
            last_wait_time = time.ticks_add(last_wait_time, item)
            wait_for_ms = time.ticks_diff(last_wait_time, time.ticks_ms())
            if wait_for_ms < 0:
                wait_for_ms = 0
            await uasyncio.sleep_ms(wait_for_ms)
        else:
            await item
            last_wait_time = time.ticks_ms()
            

def wait_for(fcn, *nargs, **kwargs):
    async def __converted_to_async(fcn, *nargs, **kwargs):
        return await fcn(*nargs, **kwargs)


def add_task(fcn, *nargs, **kwargs):
    return uasyncio.create_task(_run(fcn, *nargs, **kwargs))


def start_tasks():
    print('Starting tasks')
    uasyncio.get_event_loop().run_forever()

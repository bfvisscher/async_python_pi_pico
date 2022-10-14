import time

from machine import Pin

from async_tasks import SignalTimer


class HCSR04(SignalTimer):
    def measurement(self):
        return super().measurement() * 340 / 20000  # sound_velocity = 340m/s


def ranging_HCSR04(trigger_pin, echo_pin, callback, delay_ms=50):
    trigger_pin = Pin(trigger_pin, Pin.OUT, 0)
    HCSR04(echo_pin, callback, SignalTimer.TIME_HIGH, hard=True)
    while True:
        trigger_pin.value(1)
        time.sleep_us(10)
        trigger_pin.value(0)
        yield delay_ms  # delay to avoid echo's

# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT

# Class to use for working with Buttons for pi pico.
# Event detection in irq based to minimise cpu overhead
# Debouncing is done using an async execution model
# Callback execution is done using async processing


import micropython
import uasyncio
from machine import Pin


class Button:
    RELEASE = 2
    PRESS = 1

    def __init__(self, pin, callback, consecutive=4, interval_ms=5):
        """

        :param pin: pin with button connected (assumed 0 is pressed, 1 is released)
        :param callback:  method f(events:int)
        :param consecutive: nr of consecutive identical pin states before changing (used for debouncing)
        :param interval_ms: time between each consecutive pin state (used for debouncing)

        possible events in the callback are:
            Button.PRESS
            Button.RELEASE
        """
        self.button_pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.button_pin.irq(self._button_irq_handler, Pin.IRQ_RISING | Pin.IRQ_FALLING)
        self.irq_event = uasyncio.ThreadSafeFlag()
        self.callback = callback
        self.debounce_interval_ms = interval_ms
        self.debounce_consecutive = consecutive
        self.current_state = self.button_pin()
        self.events = 0
        self.ignore_button_irq = False
        self.task = uasyncio.create_task(self())

    def cancel(self):
        self.task.cancel()

    def clear(self):
        self.events = 0

    @micropython.viper
    def _button_irq_handler(self, pin):
        if not self.ignore_button_irq and self.current_state != pin():
            self.ignore_button_irq = True  # Change detected, debounce using async method
            self.irq_event.set()  # button event is potentially happened (after debounce)

    @micropython.native
    async def __call__(self):
        while True:
            await self.irq_event.wait()
            if self.ignore_button_irq:  # event includes potentially a button event
                new_state = 1 - self.current_state
                measurements = 0  # the irq even is the first measure
                while measurements < self.debounce_consecutive:
                    await uasyncio.sleep_ms(self.debounce_interval_ms)
                    if new_state == self.button_pin():
                        measurements += 1
                    else:
                        measurements = 0
                        new_state = 1 - new_state

                if new_state != self.current_state:  # confirmed event
                    self.current_state = new_state
                    button_event = Button.RELEASE if new_state else Button.PRESS
                    self.events |= button_event
                self.ignore_button_irq = False  # listen for new button events

            if self.events:
                self.callback(self.events)
                self.clear()

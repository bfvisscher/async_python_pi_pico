# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT


# Class to use the KY-040 rotary module for pi pico.
# Event detection in irq based to minimise cpu overhead
# Callback execution is done using async processing

from machine import Pin

from async_button import Button


class KY040(Button):  # Rotary input
    COUNTER_CLOCKWISE = 4
    CLOCKWISE = 8

    def __init__(self, clk_pin, dt_pin, sw_pin, callback, consecutive=3, interval_ms=5):
        """

        :param clk_pin: pin with label clk
        :param dt_pin:  pin with label dt
        :param sw_pin: pin with label sw
        :param callback:  method f(events:int)

        possible events in the callback are:
            KY040.COUNTER_CLOCKWISE
            KY040.CLOCKWISE
            Button.PRESS
            Button.RELEASE
            
        NOTE: Because of the time between event determination and callback execution,
              it is possible to have both KY040.COUNTER_CLOCKWISE and KY040.CLOCKWISE
              at the same time! Don't assume they are mutually exclusive..
        """
        super().__init__(sw_pin, callback, consecutive=consecutive, interval_ms=interval_ms)
        self.clk_pin = Pin(clk_pin, Pin.IN)
        self.dt_pin = Pin(dt_pin, Pin.IN)
        self._rotary_state = 0
        self.clk_pin.irq(self._rotary_irq_handler, Pin.IRQ_RISING | Pin.IRQ_FALLING)
        self.dt_pin.irq(self._rotary_irq_handler, Pin.IRQ_RISING | Pin.IRQ_FALLING)

    @micropython.native
    def _rotary_irq_handler(self, pin):
        new_state = (self.dt_pin() << 1) | self.clk_pin()
        rotary_event = 0  # no event

        if self._rotary_state in [0, 3]:
            self._rotary_state = new_state
        elif new_state == 0:  # self._rotary_state in [1,2]
            rotary_event = KY040.CLOCKWISE if self._rotary_state == 1 else KY040.COUNTER_CLOCKWISE
            self._rotary_state = new_state
        elif new_state == 3:  # self._rotary_state in [1,2]
            rotary_event = KY040.COUNTER_CLOCKWISE if self._rotary_state == 1 else KY040.CLOCKWISE
            self._rotary_state = new_state

        if rotary_event:
            self.events |= rotary_event
            self.irq_event.set()

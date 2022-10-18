# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT


import gc
import random
import time

import uasyncio
from machine import Pin, WDT

from async_runner import as_pwm
from gbl import ON_BOARD_LED_PIN


def reset_if_unresponsive(unresponsive_ms=2000):
    wdt = WDT(timeout=unresponsive_ms)
    unresponsive_ms >>= 1
    while True:
        yield unresponsive_ms
        wdt.feed()


def rgb_led_random(rgb_pins, delay_ms=200, start_delay_ms=0, freq_pwm=10_000):
    # setup all pins as pwm
    pwm_pins = as_pwm(rgb_pins, freq_pwm)

    # run the program
    yield start_delay_ms
    while True:
        for p in pwm_pins:
            p.duty_u16(random.randint(0, 65535))
        yield delay_ms


def random_item_selector(black_board, entry, items, switch_time_ms, repetition=False):
    if len(items) == 1:
        repetition = True

    while True:
        if repetition:
            black_board[entry] = random.choice(items)
        else:
            current = black_board.get(entry, None)
            red_list = items.copy()
            if current in red_list:
                red_list.remove(current)
            black_board[entry] = random.choice(red_list)
        yield switch_time_ms


def cpu_load(time_between_report_ms=1000, mqtt=None):
    # idle_load = 417.7  # 417.0 # compensate for regular overhead of async
    if mqtt is not None:
        from hass_entities import HassSensor
        cpu_sensor = HassSensor(mqtt, "CPU utilization", 0, unit_of_measurement="%", icon="mdi:cpu-64-bit")

    idle_load = None
    gc.disable()
    load = 80
    while True:
        start_time = time.ticks_ms()

        loop = 0
        total_out_time = 0
        total_self_time = 0

        wait_time = time.ticks_add(start_time, time_between_report_ms)

        self_start_time = time.ticks_us()
        while wait_time > time.ticks_ms():
            loop += 1

            pre_tick = time.ticks_us()
            yield 0
            post_tick = time.ticks_us()

            self_time = time.ticks_diff(pre_tick, self_start_time)
            self_start_time = post_tick
            out_time = time.ticks_diff(post_tick, pre_tick)

            total_self_time = time.ticks_add(self_time, total_self_time)

            if idle_load is None or out_time < idle_load:
                idle_load = out_time

            total_out_time = time.ticks_add(out_time, total_out_time)
            if load < 70:
                gc.collect()

        # print("loopsit id  : %i   idle: %i    self : %i    Out : %i" % (
        # loop, self.idle_load, total_self_time, total_out_time))
        load = 100 - 100 * (total_self_time + (loop * idle_load)) / (total_out_time + total_self_time)

        if mqtt is not None:
            cpu_sensor.state = round(load, 0)
            cpu_sensor.publish_state()
        else:
            print('CPU load: %2.1f%%  RAM free %d RAM alloc %d' % (load, gc.mem_free(), gc.mem_alloc()))


def heartbeat(pin=ON_BOARD_LED_PIN):
    pin = Pin(pin, Pin.OUT)
    while True:
        pin.value(1)
        yield 200
        pin.value(0)
        yield 800


class SignalTimer:
    """
    Class that accurately measures the duration at which a signal_pin is high/low (measured in us (=1000*ms)
    When the signal has stopped, the callback function is called with the duration within async loop
    """
    TIME_HIGH = 1
    TIME_LOW = 0

    def __init__(self, signal_pin, callback, measure=1, hard=False):
        """
        :param signal_pin: Pin to monitor for signal
        :param callback:  fn( measurement:int ) -> None     measurement is an integer of time difference (us)
        :param measure (SignalTimer.TIME_HIGH):  measure either  SignalTimer.TIME_HIGH or  SignalTimer.TIME_LOW
        :param hard:(False)  Use hardware interrupt (more accurate but only few available) or software interrupt (false)
        """
        self.signal_pin = Pin(signal_pin, Pin.IN, Pin.PULL_DOWN if measure == SignalTimer.TIME_HIGH else Pin.PULL_UP)

        self.measure = measure
        self.start = 0
        self.stop = 0
        self._cb = callback
        self.event = uasyncio.ThreadSafeFlag()
        self.signal_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.irq_handler, hard=hard)
        uasyncio.create_task(self())

    @micropython.native
    async def __call__(self):
        while True:
            await self.event.wait()
            if self.start < self.stop:
                self._cb(self.measurement())

    @micropython.native
    def measurement(self):  # duration by default
        return time.ticks_diff(self.stop, self.start)

    @micropython.viper
    def irq_handler(self, pin):
        ticks = time.ticks_us()
        if pin() == self.measure:
            self.start = ticks
        else:
            self.stop = ticks
            self.event.set()

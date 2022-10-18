# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT


import rp2
from machine import Pin, bitstream

import dma
from async_runner import as_pins, as_pwm
from pio_state_machines import __WS282B__, __SK6812__
from pixel_buffers import PixelBufferPWM, PixelBufferNeo, PixelBuffer


def pin_driver(pin_ids, pattern_fcn, **kwargs):
    pins = as_pins(pin_ids, Pin.OUT)

    pixel_buffer = PixelBuffer(len(pins))

    for delay_ms in pattern_fcn(pixel_buffer=pixel_buffer, **kwargs):

        # send buffer to pwm pins
        for pin, pixel in zip(pins, pixel_buffer):
            pin.value(pixel)

        yield delay_ms


def pwm_driver(pin_ids, pattern_fcn, freq_pwm=10_000, **kwargs):
    pwm_pins = as_pwm(pin_ids=pin_ids, freq_pwm=freq_pwm)

    pixel_buffer = PixelBufferPWM(len(pwm_pins))

    for delay_ms in pattern_fcn(pixel_buffer=pixel_buffer, **kwargs):

        # send buffer to pwm pins
        for pin, pixel in zip(pwm_pins, pixel_buffer):
            pin.duty_u16(pixel)

        yield delay_ms


def neo_driver_bitstream(pin, pattern_fcn, n, bpp=3, timing=1, **kwargs):
    # Timing arg can either be 1 for 800kHz or 0 for 400kHz,
    # or a user-specified timing ns tuple (high_0, low_0, high_1, low_1).

    pin = Pin(pin, Pin.OUT)
    timing = ((400, 850, 800, 450) if timing else (800, 1700, 1600, 900)) if isinstance(timing, int) else timing
    pixel_buffer = PixelBufferNeo(n, bpp)
    task_id = -1
    for delay_ms in pattern_fcn(pixel_buffer=pixel_buffer, **kwargs):
        # update

        # sent pixels to leds
        # BITSTREAM_TYPE_HIGH_LOW = 0
        bitstream(pin, 0, timing, pixel_buffer.buf)

        yield delay_ms


def neo_driver_pio(pin, pattern_fcn, n, bpp=3, state_machine=0, **kwargs):
    if bpp == 3:
        pio_driver = __WS282B__
    elif bpp == 4:
        pio_driver = __SK6812__
    else:
        print('bbp can not be %i but most be either 3 or 4' % bpp)

    pin = Pin(pin, Pin.OUT)

    sm = rp2.StateMachine(state_machine, pio_driver, freq=8_000_000, sideset_base=pin)
    sm.active(1)

    pixel_buffer = PixelBufferNeo(n, bpp)

    cut = 8
    if bpp == 4:
        cut = 0

    sm_put = lambda x: sm.put(x, cut)

    for delay_ms in pattern_fcn(pixel_buffer=pixel_buffer, **kwargs):

        # sent pixels to leds
        buf = pixel_buffer.buf
        for x in buf:
            sm_put(x)

        yield delay_ms


def neo_driver_dma(pin, pattern_fcn, n, bpp=3, state_machine=0, **kwargs):
    if bpp == 3:
        pio_driver = __WS282B__
    elif bpp == 4:
        pio_driver = __SK6812__
    else:
        print('bbp can not be %i but most be either 3 or 4' % bpp)

    pin = Pin(pin, Pin.OUT)
    sm = rp2.StateMachine(state_machine, pio_driver, freq=8_000_000, sideset_base=pin)
    sm.active(1)

    ch = dma.dma.allocate_channel()
    if ch is None:
        print('Could not allocate a dedicated DMA channel for neo_driver_dma')

    pixel_buffer = PixelBufferNeo(n, bpp, dma=True)
    yield 0
    for delay_ms in pattern_fcn(pixel_buffer=pixel_buffer, **kwargs):
        # sent pixels to leds        

        ch.mem_2_pio(pixel_buffer.buf, state_machine, dma.DMA_SIZE_32)
        yield delay_ms

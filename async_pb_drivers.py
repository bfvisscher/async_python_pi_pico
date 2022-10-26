# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT


import rp2
from machine import Pin, bitstream

import hardware
from async_runner import as_pins, as_pwm
from pio_state_machines import __WS282B__, __SK6812__
from pixel_buffers import PixelBufferPWM, PixelBufferNeo, PixelBufferBit


def pin_driver(pin_ids, pattern, **kwargs):
    pins = as_pins(pin_ids, Pin.OUT)

    pixel_buffer = PixelBufferBit(len(pins))

    for delay_ms in pattern(pixel_buffer=pixel_buffer, **kwargs):

        # send buffer to pwm pins
        for pin, pixel in zip(pins, pixel_buffer):
            pin.value(pixel)

        yield delay_ms


def pwm_driver(pin_ids, pattern, freq_pwm=10_000, **kwargs):
    pwm_pins = as_pwm(pin_ids=pin_ids, freq_pwm=freq_pwm)

    pixel_buffer = PixelBufferPWM(len(pwm_pins))

    for delay_ms in pattern(pixel_buffer=pixel_buffer, **kwargs):

        # send buffer to pwm pins
        for pin, pixel in zip(pwm_pins, pixel_buffer):
            pin.duty_u16(pixel)

        yield delay_ms


def neo_driver_bitstream(pin, pattern, n, bpp=4, timing=1, **kwargs):
    # Timing arg can either be 1 for 800kHz or 0 for 400kHz,
    # or a user-specified timing ns tuple (high_0, low_0, high_1, low_1).
    if bpp != 4:
        raise Exception('neo_driver_bitstream only works with bpp=4')

    pin = Pin(pin, Pin.OUT)
    timing = ((400, 850, 800, 450) if timing else (800, 1700, 1600, 900)) if isinstance(timing, int) else timing
    pixel_buffer = PixelBufferNeo(n, bpp)
    task_id = -1
    for delay_ms in pattern(pixel_buffer=pixel_buffer, **kwargs):
        # update

        # sent pixels to leds
        # BITSTREAM_TYPE_HIGH_LOW = 0
        bitstream(pin, 0, timing, pixel_buffer.buf)

        yield delay_ms


def neo_driver_pio(pin, pattern, n, bpp=3, state_machine=0, **kwargs):
    if bpp == 3:
        pio_driver = __WS282B__
    elif bpp == 4:
        pio_driver = __SK6812__
    else:
        raise Exception('bbp can not be %i but must be either 3 or 4' % bpp)

    pin = Pin(pin, Pin.OUT)

    sm = rp2.StateMachine(state_machine, pio_driver, freq=8_000_000, sideset_base=pin)
    sm.active(1)

    pixel_buffer = PixelBufferNeo(n, bpp)

    sm_put = lambda x: sm.put(x)

    buf = pixel_buffer.buf
    for delay_ms in pattern(pixel_buffer=pixel_buffer, **kwargs):

        # sent pixels to led strip
        for p in buf:
            sm_put(p)

        yield delay_ms


def neo_driver_dma(pin, pattern, n, bpp=3, state_machine=0, **kwargs):
    if bpp == 3:
        pio_driver = __WS282B__
    elif bpp == 4:
        pio_driver = __SK6812__
    else:
        raise Exception('bbp can not be %i but most be either 3 or 4' % bpp)

    pin = Pin(pin, Pin.OUT)
    sm = rp2.StateMachine(state_machine, pio_driver, freq=8_000_000, sideset_base=pin)
    sm.active(1)

    dma_channel = hardware.dma.allocate_channel()

    pixel_buffer = PixelBufferNeo(n, bpp)
    try:
        for delay_ms in pattern(pixel_buffer=pixel_buffer, **kwargs):
            # sent pixels to neo pixels
            dma_channel.mem_2_pio(pixel_buffer.buf, state_machine, hardware.DMA_SIZE_32)

            yield delay_ms

            while dma_channel.is_busy():                
                yield 1 # safety incase DMA didn't manage to complete

    except Exception as e:
        print('Caught in driver')
        print(e)

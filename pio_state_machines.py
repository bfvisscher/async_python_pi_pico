# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT


import rp2


@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def __WS282B__():
    """
    State Machine Assembly for sending the bitstream to LEDs.
    Internal class function, not intended for external calling.
    """
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1).side(0)[T3 - 1]
    jmp(not_x, "do_zero").side(1)[T1 - 1]
    jmp("bitloop").side(1)[T2 - 1]
    label("do_zero")
    nop().side(0)[T2 - 1]
    wrap()

# PIO _rotary_state machine for RGBW. Pulls 32 bits (rgbw -> 4 * 8bit) 
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=32)
def __SK6812__():
    """
    State Machine Assembly for sending the bitstream to LEDs.
    Internal class function, not intended for external calling.
    """
    T1 = 2
    T2 = 5
    T3 = 3

    wrap_target()
    label("bitloop")
    out(x, 1).side(0)[T3 - 2]

    jmp(not_x, "do_zero").side(1)[T1 - 1]
    jmp("bitloop").side(1)[T2 - 1]
    label("do_zero")
    nop().side(0)[T2 - 1]
    wrap()

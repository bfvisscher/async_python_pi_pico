# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT


import os
import time


# slice constructor is by default disabled in micropython
class MakeSlice:
    @micropython.native
    def __getitem__(self, sl: slice) -> slice:
        return sl


make_slice = MakeSlice()


# use make_slice[1:-1] to make a slice object


def timed_function(f, *args, **kwargs):
    myname = str(f)

    def new_func(*args, **kwargs):
        print('start timing')
        t = time.ticks_us()

        for i in range(100):
            result = f(*args, **kwargs)

        delta = time.ticks_diff(time.ticks_us(), t)
        print('Function {} Time = {:6.3f}ns'.format(myname, delta / 10000))

        return result

    return new_func


PICO_W = 'Pico W' in os.uname()[-1]

ON_BOARD_LED_PIN = 'LED' if PICO_W else 25

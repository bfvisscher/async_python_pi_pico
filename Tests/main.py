from async_drivers import *
from async_runner import *
from async_tasks import cpu_load, rgb_led_random
from patterns import *

PICO_W = True
if PICO_W:
    ON_BOARD_PIN = 'LED'
else:
    ON_BOARD_PIN = 25

from machine import Pin



add_task(rgb_led_random, rgb_pins=[13, 12, 11])
add_task(cpu_load)
add_task(pin_driver, [ON_BOARD_PIN], blink, pixel=1)

# add_task(pin_driver, [15, 16, 17, 18, 19, 20, 21, 22, 26, 27], blink, on_pixel=65535, off_pixel=0, )
add_task(pwm_driver, [15, 16, 17, 18, 19, 20, 21, 22, 26, 28], fading_bars, pixel=65535, fade=.8, freq=50)
# add_task(neo_driver_dma, 27, fading_bars, pixel=[0, 255, 255], n=8, bpp=3, fade=.9, freq=50)
# add_task(neo_driver_dma, 27, blink, on_pixel=[0, 255, 255], off_pixel=[255, 0, 0], n=8, bpp=3)

# add_task(neo_driver_dma, 27, morse_code, on_pixel=[0, 255, 255, 0], off_pixel=[255, 0, 0, 255], n=350, bpp=4, message="sos", loop=True, reverse=False, local=False)

#add_task(neo_driver_dma, 27, kit, pixel=[255, 0, 0], n=144, bpp=3)

pl3 = [
    [255, 0, 0],
    [255, 255, 0],
    [0, 255, 0],
    [0, 255, 255],
    [0, 0, 255],
    [255, 0, 255],
]

pl4 = [
    [255, 0, 0, 0],
    [255, 255, 0, 0],
    [0, 255, 0, 0],
    [0, 255, 255, 0],
    [0, 0, 255, 0],
    [255, 0, 255, 0],
    [0, 0, 0, 255],
]

#add_task(neo_driver_dma, 27, breathing, pixel_list=pl, n=144, bpp=3)
add_task(neo_driver_dma, 27, snakes, pixel_list=pl3, n=144, bpp=3, freq=50)

start_tasks()  # keeps running forever

from async_pb_drivers import *
from async_runner import *
from patterns import *


pin_strip_upper = 27
pin_strip_lower = 6

driver = neo_driver_bitstream

add_task(driver, pin_strip_upper, clear, n=144, bpp=3)
add_task(driver, pin_strip_lower, clear, n=300, bpp=4)


start_tasks()  # keeps running forever
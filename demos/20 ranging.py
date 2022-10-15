from async_hcsr04 import ranging_HCSR04
from async_runner import *
from async_tasks import cpu_load, heartbeat

PICO_W = True
if PICO_W:
    ON_BOARD_PIN = 'LED'
else:
    ON_BOARD_PIN = 25


# class to handle the callback when ranging returns a new value
class UpdateDistance:
    def __init__(self):
        self.counter = 0
        self.total = 0

    def update_distance(self, distance):
        self.counter += 1
        self.total += distance
        if self.counter == 20:
            print("Distance : %.2fcm" % (self.total / self.counter))
            self.counter = 0
            self.total = 0


add_task(cpu_load)  # show CPU usage while running
add_task(heartbeat, pin=ON_BOARD_PIN)  # show the on-board LED blinking to indicate activity

add_task(ranging_HCSR04, trigger_pin=19, echo_pin=18, callback=UpdateDistance().update_distance, delay_ms=50)

start_tasks()  # keeps running forever

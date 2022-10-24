from async_hcsr04 import ranging_HCSR04
from async_runner import *
from async_tasks import cpu_load, heartbeat


# HARDWARE SETUP:
# add a HCSR04 module:
#                    echo pin to pin 19
#                    trigger pin to pin 18



def show_distance(distance):        
    print("Distance : %.2fcm" % distance)


add_task(cpu_load)  # show CPU usage while running
add_task(heartbeat)  # show the on-board LED blinking to indicate activity

add_task(ranging_HCSR04, trigger_pin=19, echo_pin=18, callback=show_distance, delay_ms=500)

start_tasks()  # keeps running forever

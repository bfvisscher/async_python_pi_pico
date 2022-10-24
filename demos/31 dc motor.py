from async_runner import *
from async_tasks import cpu_load, heartbeat

from dc_motor import DCMotor


# HARDWARE SETUP:
# Materials:
#            L293D bridge and a DC engine and some wires
# add a L293D Bridge:
#                    connect 1,2 enable to pin 17 (speed control)
#                    connect 1A and 2A to to pin 15 and pin 16 (direction control)
#                    add the dc motor to 1Y and 2Y
#                    add 3.3v power to Vcc1 to power to logic circuits
#                    add 5v power (or more) to Vcc2 to power the dc motor

# class to handle the callback when ranging returns a new value

def motor_demo(power):
    #  stall_zone  is the minimum power that needs to be applied before the engine starts turning,
    #              this can be changed at any time by saying motor.stall_zone = .2  (to change it to 20%)
    motor = DCMotor(enable_pin=17, in_a=15, in_b=16, stall_zone=.3, invert=False)

    # if the motor rotates in the opposite direction, you can change invert=True or swap the in_a, in_b pins
    while True:
        motor.throttle(-power)  # use 50% power in counter clockwise direction
        yield 2500  # let it run for 2000 milliseconds (=2s)

        motor.stop()  # stops the engine
        yield 500  # give it time to stop

        motor.throttle(power)  # use 50% power in clockwise direction
        yield 2500  # let it run for 2000 milliseconds (=2s)

        motor.stop()  # stops the engine
        yield 500  # give it time to stop

        # NOTE: The LED blinking stays synchonised with the engine starting to rotate


add_task(cpu_load)  # show CPU usage while running
add_task(heartbeat)  # show the on-board LED blinking to indicate activity
add_task(motor_demo, power=.5) #  run the motor forward / backward at 50%

start_tasks()  # keeps running forever

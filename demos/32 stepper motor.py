from async_runner import add_task, start_tasks
from async_tasks import cpu_load, heartbeat
from stepper_motor import BYJ46


# HARDWARE SETUP:
# Materials:
#            Stepper motor driver
#            Stepper motor
#
# add the motor driver:
#                    connect to stepper motor
#                    connect to the power
#                    connect IN1-IN4 to pin 6-9

# NOTE: The Stepper motor class uses the PIO statemachine to send the sequence to
#       the motor driver. The CPU requirements are because of this very low..
#
# NOTE: To stop execution, use control-c in the REPL (Shell in Thonny). This will
#       avoid ENOMEM on the Pico W (https://github.com/micropython/micropython/issues/9003)


def engine_run():
    # The speed pin is used by the stepper motor driver to time when to take
    # a step. The smaller the delay, the quicker the RPM. If this is made too
    # small, the engine will not move at all.
    speed_pin = 10

    eng = BYJ46(pins=[6, 7, 8, 9], speed_pin=speed_pin, delay_ns=1000)

    print("Stepping clockwise, slowly")

    yield eng.next_n(1000, delay_ns=2000)  # take 1000 (half)steps clockwise
    eng.stop()  # force the engine to stop
    yield 1000  # wait a bit (1s)

    print("Stepping counter clockwise, very slowly")
    yield eng.previous_n(1000, delay_ns=3000)  # take 1000 (half)steps counter clockwise
    yield 1000  # wait a bit (1s)
    while True:
        yield eng.rotate_angle(-90)  # It returns a wait object
        yield eng.rotate_angle(90)  # It returns a wait object


add_task(cpu_load)
add_task(heartbeat)
add_task(engine_run)

start_tasks()

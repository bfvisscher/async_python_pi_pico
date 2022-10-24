from angular_servo import AngularServo
from async_runner import add_task, start_tasks
from async_tasks import cpu_load, heartbeat


# HARDWARE SETUP:
# Materials:
#            servo motor
#
# connect the servo motor:
#                    connect to the power and GND
#                    connect signal to pin 4


def engine_run():
    # The speed pin is used by the stepper motor driver to time when to take
    # a step. The smaller the delay, the quicker the RPM. If this is made too
    # small, the engine will not move at all.

    servo = AngularServo(control_pin=10)

    while True:
        for angle in [0, 45, 90, 45, 0, -45, -90, -45]:
            servo.angle = angle  # set the servo to the new angle
            yield 1000  # wait 1s nfor the servo to move to the new position


add_task(cpu_load)
add_task(heartbeat)
add_task(engine_run)

start_tasks()

from machine import Pin, PWM

from async_hcsr04 import ranging_HCSR04
from async_runner import start_tasks, add_task
from async_tasks import heartbeat
from angular_servo import AngularServo


from async_ky040 import KY040, Button


class ServoCalibration:
    def __init__(self, servo_pin, angle_mode, small_step=1, large_step=5):
        self.duty = 3000
        self.angle = 0
        self.angle_mode = angle_mode
        self.step = large_step
        self.small_step = small_step
        self.large_step = large_step
        self.servo = AngularServo(servo_pin)

    def callback(self, event):
        if event & Button.PRESS:
            if self.step == self.large_step:
                self.step = self.small_step
            else:
                self.step = self.large_step

        cur_duty = self.duty
        cur_angle = self.angle
        if self.angle_mode:
            if event & KY040.CLOCKWISE:
                self.angle += self.step
            if event & KY040.COUNTER_CLOCKWISE:
                self.angle -= self.step

        else:
            if event & KY040.CLOCKWISE:
                self.duty += self.step
            if event & KY040.COUNTER_CLOCKWISE:
                self.duty -= self.step

        if cur_angle != self.angle:
            print('Angle = %i' % self.angle)
            self.servo.angle = self.angle

        if cur_duty != self.duty:
            print('Duty = %i' % self.duty)
            self.servo.setduty_u16(self.duty)


sc = ServoCalibration(servo_pin=10, angle_mode=True)

k = KY040(clk_pin=20, dt_pin=19, sw_pin=18, callback=sc.callback)


add_task(heartbeat)
start_tasks()

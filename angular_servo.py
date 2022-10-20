from machine import Pin, PWM


class AngularServo:
    def __init__(self, control_pin, initial_angle=0, pwm_freq=50,
                 min_angle=-90, min_angle_duty=1602,
                 max_angle=90, max_angle_duty=7423):
        self.control_pin = PWM(Pin(control_pin))
        self.control_pin.freq(pwm_freq)

        self.min_angle_duty = min_angle_duty
        self.max_angle_duty = max_angle_duty
        self.delta_duty = max_angle_duty - min_angle_duty
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.delta_angle = max_angle - min_angle
        # self._angle = initial_angle
        self.angle = initial_angle

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, angle):
        """

        :param angle: value between min_angle and max_angle
        :return:
        """
        if angle < self.min_angle:
            angle = self.min_angle
        if angle > self.max_angle:
            angle = self.max_angle

        duty = int(self.min_angle_duty + self.delta_duty * (angle - self.min_angle) / self.delta_angle)
        self.control_pin.duty_u16(duty)
        self._angle = angle

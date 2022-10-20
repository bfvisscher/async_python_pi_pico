# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT


from machine import Pin, PWM


class DCMotor:
    def __init__(self, enable_pin, in_a, in_b, pwm_freq=1000, stall_zone=.3, invert=False):
        self.enable_pin = PWM(Pin(enable_pin))
        self.enable_pin.freq(pwm_freq)

        if invert:
            self.drb_pin = Pin(in_a, Pin.OUT)
            self.dra_pin = Pin(in_b, Pin.OUT)
        else:
            self.dra_pin = Pin(in_a, Pin.OUT)
            self.drb_pin = Pin(in_b, Pin.OUT)

        self._stall_zone = stall_zone
        self.power = 0
        self.direction = 0

    def stop(self):
        self.direction = 0
        self.dra_pin.value(0)
        self.drb_pin.value(0)

    def clock_wise(self):
        self.direction = 1
        self.dra_pin.value(0)
        self.drb_pin.value(1)

    def counter_clock_wise(self):
        self.direction = -1
        self.drb_pin.value(0)
        self.dra_pin.value(1)

    @property
    def stall_zone(self):
        return self._stall_zone

    @stall_zone.setter
    def stall_zone(self, stall_zone):
        self._stall_zone = stall_zone
        self.power = self.power  # recalculate duty based on new stall_zone

    @property
    def power(self):
        return self._power

    @power.setter
    def power(self, power: float):
        """

        :param power:  value between 0 and 1
        :return:
        """
        self._power = power
        duty = min(65535, int(65536 * (self._stall_zone + (1 - self._stall_zone) * power)))
        self.enable_pin.duty_u16(duty)

    def throttle(self, power: float):
        """
        Sets both direction and power by using (-1, +1)
        :param power:
        :return:
        """
        if power == 0:
            self.stop()
        elif power < 0:
            self.counter_clock_wise()
            power = -power
        else:
            self.clock_wise()
        self.power = power

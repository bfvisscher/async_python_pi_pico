import machine
import rp2
import uasyncio

from async_runner import as_pins
from cyclers import ByteCycler


@rp2.asm_pio(out_init=[rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW])
def __4BITCYCLER__():
    """
    State Machine Assembly for sending 4 bits in a cycle when receiving 0 in input pin

    """
    CYCLE_LENGTH = 8
    DELAY = 10
    wrap_target()
    pull(block)
    mov(y, osr)  # use y as counter (pattern is repeated y+1 times)
    pull(block)
    mov(isr, osr)  # store the pattern in x

    label('Cycle')
    jmp(not_osre, 'sync')  # if pattern is not completely sent, keep cycling
    mov(osr, isr)  # reload the full pattern
    label('sync')
    wait(1, pin, 0)
    out(pins, 4)

    wait(0, pin, 0)
    jmp(y_dec, 'Cycle')
    wrap()


class CyclicalPinPIOMDriver:
    def __init__(self, pins, speed_pin, sequence, steps, delay_ns, state_machine=0):
        self.pins = as_pins(pins, machine.Pin.OUT)
        self.speed_pin = machine.PWM(machine.Pin(speed_pin, machine.Pin.OUT))
        self.speed_pin.duty_u16(32767)
        self.delay_ns = delay_ns
        self.speed_pin.freq(1_000_000 // delay_ns)
        self.cycler = ByteCycler(sequence)
        self.steps = steps
        self.sm = rp2.StateMachine(state_machine, __4BITCYCLER__, in_base=machine.Pin(speed_pin), out_base=self.pins[0],
                                   freq=10_000_000)
        self.sm.active(1)

    def set_pins(self, value):
        for p in self.pins:
            p.value(value & 1)
            value >>= 1

    def stop(self):
        self.sm.restart()  # interrupt any execution
        # read the current step
        self.cycler.set(self.current_seq())
        self.sm.put(0)  # take one step
        self.sm.put(0)  # pattern

    def current_seq(self):
        value = 0
        for p in reversed(self.pins):
            value = (value << 1) + p.value()
        return  value

    def next(self):
        self.sm.put(0)  # take one step
        self.sm.put(self.cycler.next(), 28)

    def previous(self):
        self.sm.put(0)  # take one step
        self.sm.put(self.cycler.previous(), 28)

    def next_n(self, n, delay_ns=None):
        return self._set_pio(n, delay_ns)

    def previous_n(self, n, delay_ns=None):
        return self._set_pio(-n, delay_ns)

    def rotate_angle(self, angle, delay_ns=None):
        n = angle * self.steps // 360
        return self._set_pio(n, delay_ns)

    def _set_pio(self, n, delay_ns):
        if n < 0:
            steps = -n
            generator_fcn = self.cycler.previous
        else:
            steps = n
            generator_fcn = self.cycler.next
        seq = 0
        for i in range(len(self.cycler)):
            seq = seq << 4 | generator_fcn()
        self.cycler.step(n)

        if delay_ns is None:
            delay_ns = self.delay_ns

        freq = 1_000_000 // delay_ns

        self.speed_pin.freq(freq)
        self.sm.put(steps - 1)
        self.sm.put(seq)
        return uasyncio.sleep_ms(steps * 1000 // freq)


class BYJ46(CyclicalPinPIOMDriver):
    def __init__(self, pins, speed_pin=29, steps=4082, delay_ns=1000, state_machine=0):
        super().__init__(pins=pins, sequence=[1, 3, 2, 6, 4, 12, 8, 9], speed_pin=speed_pin, steps=steps,
                         delay_ns=delay_ns, state_machine=state_machine)

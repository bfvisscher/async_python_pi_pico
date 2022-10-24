import micropython
import array

class ByteCycler:
    def __init__(self, sequence):
        self.sequence = array.array('B', sequence)
        self.current = 0
        self.n = len(self.sequence)

    @micropython.viper
    def next(self) -> int:
        current = int(self.current)
        seq = ptr8(self.sequence)
        n = int(self.n)
        current += 1
        if current == n:
            current = 0
        self.current = current
        return seq[current]

    @micropython.viper
    def previous(self) -> int:
        seq = ptr8(self.sequence)
        current = int(self.current)
        n = int(self.n)
        if current == 0:
            current = n
        current -= 1
        self.current = current
        return seq[current]

    @micropython.native
    def __len__(self):
        return self.n

    @micropython.viper
    def current(self) -> int:
        seq = ptr8(self.sequence)
        current = int(self.current)
        return seq[current]

    @micropython.native
    def step(self, n):  # do n forward- / backward-steps (-) in one go
        self.current = (self.current + n) % self.n

    def set(self, value):
        try:
            self.current = self.sequence.index(value)
        except:
            # don't do anything if value not in the list
            pass

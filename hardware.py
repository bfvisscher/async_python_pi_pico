# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT


#   This file is a work in progress
#   The aim is to have different types of dma transfers readily available
#   to and from all the different options ie
#   mem -> mem, pio -> mem mem -> pio, mem->i2c etc
#


import micropython
from uctypes import BF_POS, BF_LEN, UINT32, BFUINT32, struct, addressof

PIO0_BASE = const(0x50200000)
PIO1_BASE = const(0x50300000)

PIO_REGS = {
    "CTRL": 0x00 | UINT32,
    "FSTAT": 0x04 | UINT32,
    "FDEBUG": 0x08 | UINT32,
    "FLEVEL": 0x00c | UINT32,
    "TXF0": 0x010 | UINT32,
    "TXF1": 0x014 | UINT32,
    "TXF2": 0x018 | UINT32,
    "TXF3": 0x01c | UINT32,
    "RXF0": 0x020 | UINT32,
    "RXF1": 0x024 | UINT32,
    "RXF2": 0x028 | UINT32,
    "RXF3": 0x02c | UINT32,
}

pio = [struct(PIO0_BASE, PIO_REGS), struct(PIO1_BASE, PIO_REGS)]

GPIO_BASE = const(0x40014000)
GPIO_CHAN_WIDTH = const(0x08)
GPIO_PIN_COUNT = const(30)

PAD_BASE = const(0x4001c000)
PAD_PIN_WIDTH = const(0x04)
ADC_BASE = const(0x4004c000)

DMA_BASE = const(0x50000000)
DMA_CHAN_WIDTH = const(0x40)
DMA_CHAN_COUNT = const(12)

DMA_SIZE_8 = const(0)
DMA_SIZE_16 = const(1)
DMA_SIZE_32 = const(3)

# DMA: RP2040 datasheet 2.5.7
DMA_CTRL_FIELDS = {
    "AHB_ERROR": 31 << BF_POS | 1 << BF_LEN | BFUINT32,
    "READ_ERROR": 30 << BF_POS | 1 << BF_LEN | BFUINT32,
    "WRITE_ERROR": 29 << BF_POS | 1 << BF_LEN | BFUINT32,
    "BUSY": 24 << BF_POS | 1 << BF_LEN | BFUINT32,
    "SNIFF_EN": 23 << BF_POS | 1 << BF_LEN | BFUINT32,
    "BSWAP": 22 << BF_POS | 1 << BF_LEN | BFUINT32,
    "IRQ_QUIET": 21 << BF_POS | 1 << BF_LEN | BFUINT32,
    "TREQ_SEL": 15 << BF_POS | 6 << BF_LEN | BFUINT32,
    "CHAIN_TO": 11 << BF_POS | 4 << BF_LEN | BFUINT32,
    "RING_SEL": 10 << BF_POS | 1 << BF_LEN | BFUINT32,
    "RING_SIZE": 6 << BF_POS | 4 << BF_LEN | BFUINT32,
    "INCR_WRITE": 5 << BF_POS | 1 << BF_LEN | BFUINT32,
    "INCR_READ": 4 << BF_POS | 1 << BF_LEN | BFUINT32,
    "DATA_SIZE": 2 << BF_POS | 2 << BF_LEN | BFUINT32,
    "HIGH_PRIORITY": 1 << BF_POS | 1 << BF_LEN | BFUINT32,
    "EN": 0 << BF_POS | 1 << BF_LEN | BFUINT32
}

# Channel-specific DMA registers, have one trigger and one non trigger version of each [2.5.2.1]
DMA_CHAN_REGS = {
    "READ_ADDR_REG": 0x00 | UINT32,
    "READ_ADDR_REG_TRIG": 0x3C | UINT32,

    "WRITE_ADDR_REG": 0x04 | UINT32,
    "WRITE_ADDR_REG_TRIG": 0x2C | UINT32,

    "TRANS_COUNT_REG": 0x08 | UINT32,
    "TRANS_COUNT_REG_TRIG": 0x1C | UINT32,

    "CTRL_REG_TRIG": 0x0C | UINT32,
    "CTRL_TRIG": (0x0C, DMA_CTRL_FIELDS),

    "CTRL_REG": 0x10 | UINT32,
    "CTRL": (0x10, DMA_CTRL_FIELDS),
}

# General DMA registers
DMA_REGS = {
    "INTR": 0x400 | UINT32,
    "INTE0": 0x404 | UINT32,  # enable/disable irq0 for channel
    "INTF0": 0x408 | UINT32,
    "INTS0": 0x40c | UINT32,
    "INTE1": 0x414 | UINT32,  # enable/disable irq1 for channel
    "INTF1": 0x418 | UINT32,
    "INTS1": 0x41c | UINT32,
    "TIMER0": 0x420 | UINT32,
    "TIMER1": 0x424 | UINT32,
    "TIMER2": 0x428 | UINT32,
    "TIMER3": 0x42c | UINT32,
    "MULTI_CHAN_TRIGGER": 0x430 | UINT32,
    "SNIFF_CTRL": 0x434 | UINT32,
    "SNIFF_DATA": 0x438 | UINT32,
    "FIFO_LEVELS": 0x440 | UINT32,
    "CHAN_ABORT": 0x444 | UINT32
}

# GPIO status and control: RP2040 datasheet 2.19.6.1.10
GPIO_STATUS_FIELDS = {
    "IRQTOPROC": 26 << BF_POS | 1 << BF_LEN | BFUINT32,
    "IRQFROMPAD": 24 << BF_POS | 1 << BF_LEN | BFUINT32,
    "INTOPERI": 19 << BF_POS | 1 << BF_LEN | BFUINT32,
    "INFROMPAD": 17 << BF_POS | 1 << BF_LEN | BFUINT32,
    "OETOPAD": 13 << BF_POS | 1 << BF_LEN | BFUINT32,
    "OEFROMPERI": 12 << BF_POS | 1 << BF_LEN | BFUINT32,
    "OUTTOPAD": 9 << BF_POS | 1 << BF_LEN | BFUINT32,
    "OUTFROMPERI": 8 << BF_POS | 1 << BF_LEN | BFUINT32
}
GPIO_CTRL_FIELDS = {
    "IRQOVER": 28 << BF_POS | 2 << BF_LEN | BFUINT32,
    "INOVER": 16 << BF_POS | 2 << BF_LEN | BFUINT32,
    "OEOVER": 12 << BF_POS | 2 << BF_LEN | BFUINT32,
    "OUTOVER": 8 << BF_POS | 2 << BF_LEN | BFUINT32,
    "FUNCSEL": 0 << BF_POS | 5 << BF_LEN | BFUINT32
}
GPIO_REGS = {
    "GPIO_STATUS_REG": 0x00 | UINT32,
    "GPIO_STATUS": (0x00, GPIO_STATUS_FIELDS),
    "GPIO_CTRL_REG": 0x04 | UINT32,
    "GPIO_CTRL": (0x04, GPIO_CTRL_FIELDS)
}

# PAD control: RP2040 datasheet 2.19.6.3
PAD_FIELDS = {
    "OD": 7 << BF_POS | 1 << BF_LEN | BFUINT32,
    "IE": 6 << BF_POS | 1 << BF_LEN | BFUINT32,
    "DRIVE": 4 << BF_POS | 2 << BF_LEN | BFUINT32,
    "PUE": 3 << BF_POS | 1 << BF_LEN | BFUINT32,
    "PDE": 2 << BF_POS | 1 << BF_LEN | BFUINT32,
    "SCHMITT": 1 << BF_POS | 1 << BF_LEN | BFUINT32,
    "SLEWFAST": 0 << BF_POS | 1 << BF_LEN | BFUINT32
}
PAD_REGS = {
    "PAD_REG": 0x00 | UINT32,
    "PAD": (0x00, PAD_FIELDS)
}

# ADC: RP2040 datasheet 4.9.6
ADC_CS_FIELDS = {
    "RROBIN": 16 << BF_POS | 5 << BF_LEN | BFUINT32,
    "AINSEL": 12 << BF_POS | 3 << BF_LEN | BFUINT32,
    "ERR_STICKY": 10 << BF_POS | 1 << BF_LEN | BFUINT32,
    "ERR": 9 << BF_POS | 1 << BF_LEN | BFUINT32,
    "READY": 8 << BF_POS | 1 << BF_LEN | BFUINT32,
    "START_MANY": 3 << BF_POS | 1 << BF_LEN | BFUINT32,
    "START_ONCE": 2 << BF_POS | 1 << BF_LEN | BFUINT32,
    "TS_EN": 1 << BF_POS | 1 << BF_LEN | BFUINT32,
    "EN": 0 << BF_POS | 1 << BF_LEN | BFUINT32
}
ADC_FCS_FIELDS = {
    "THRESH": 24 << BF_POS | 4 << BF_LEN | BFUINT32,
    "LEVEL": 16 << BF_POS | 4 << BF_LEN | BFUINT32,
    "OVER": 11 << BF_POS | 1 << BF_LEN | BFUINT32,
    "UNDER": 10 << BF_POS | 1 << BF_LEN | BFUINT32,
    "FULL": 9 << BF_POS | 1 << BF_LEN | BFUINT32,
    "EMPTY": 8 << BF_POS | 1 << BF_LEN | BFUINT32,
    "DREQ_EN": 3 << BF_POS | 1 << BF_LEN | BFUINT32,
    "ERR": 2 << BF_POS | 1 << BF_LEN | BFUINT32,
    "SHIFT": 1 << BF_POS | 1 << BF_LEN | BFUINT32,
    "EN": 0 << BF_POS | 1 << BF_LEN | BFUINT32,
}
ADC_REGS = {
    "CS_REG": 0x00 | UINT32,
    "CS": (0x00, ADC_CS_FIELDS),
    "RESULT_REG": 0x04 | UINT32,
    "FCS_REG": 0x08 | UINT32,
    "FCS": (0x08, ADC_FCS_FIELDS),
    "FIFO_REG": 0x0c | UINT32,
    "DIV_REG": 0x10 | UINT32,
    "INTR_REG": 0x14 | UINT32,
    "INTE_REG": 0x18 | UINT32,
    "INTF_REG": 0x1c | UINT32,
    "INTS_REG": 0x20 | UINT32
}
DREQ_PIO0_TX0 = 0x00
DREQ_PIO0_TX1 = 0x01
DREQ_PIO0_TX2 = 0x02
DREQ_PIO0_TX3 = 0x03
DREQ_PIO0_RX0 = 0x04
DREQ_PIO0_RX1 = 0x05
DREQ_PIO0_RX2 = 0x06
DREQ_PIO0_RX3 = 0x07
DREQ_PIO1_TX0 = 0x08
DREQ_PIO1_TX1 = 0x09
DREQ_PIO1_TX2 = 0x0a
DREQ_PIO1_TX3 = 0x0b
DREQ_PIO1_RX0 = 0x0c
DREQ_PIO1_RX1 = 0x0d
DREQ_PIO1_RX2 = 0x0e
DREQ_PIO1_RX3 = 0x0f
DREQ_SPI0_TX = 0x10
DREQ_SPI0_RX = 0x11
DREQ_SPI1_TX = 0x12
DREQ_SPI1_RX = 0x13
DREQ_UART0_TX = 0x14
DREQ_UART0_RX = 0x15
DREQ_UART1_TX = 0x16
DREQ_UART1_RX = 0x17
DREQ_PWM_WRAP0 = 0x18
DREQ_PWM_WRAP1 = 0x19
DREQ_PWM_WRAP2 = 0x1a
DREQ_PWM_WRAP3 = 0x1b
DREQ_PWM_WRAP4 = 0x1c
DREQ_PWM_WRAP5 = 0x1d
DREQ_PWM_WRAP6 = 0x1e
DREQ_PWM_WRAP7 = 0x1f
DREQ_I2C0_TX = 0x20
DREQ_I2C0_RX = 0x21
DREQ_I2C1_TX = 0x22
DREQ_I2C1_RX = 0x23
DREQ_ADC = 0x24
DREQ_XIP_STREAM = 0x25
DREQ_XIP_SSITX = 0x26
DREQ_XIP_SSIRX = 0x27
TREQ_TIMER0 = 0x3b
TREQ_TIMER1 = 0x3c
TREQ_TIMER2 = 0x3d
TREQ_TIMER3 = 0x3e
TREQ_UNPACED = 0x3f


# PAD_PINS =  [struct(PAD_BASE + n*PAD_PIN_WIDTH, PAD_REGS) for n in range(0,GPIO_PIN_COUNT)]
# ADC_DEVICE = struct(ADC_BASE, ADC_REGS)
# ADC_FIFO_ADDR = ADC_BASE + 0x0c

# GPIO_FUNC_SPI, GPIO_FUNC_UART, GPIO_FUNC_I2C = 1, 2, 3
# GPIO_FUNC_PWM, GPIO_FUNC_SIO, GPIO_FUNC_PIO0 = 4, 5, 6
# GPIO_FUNC_NULL = 0x1f


class DMAChannel:
    def __init__(self, channel_id, dma):
        self.allocated = False
        self.dma = dma
        self.id = channel_id
        self.mask = 1 << channel_id
        self._internals = struct(DMA_BASE + channel_id * DMA_CHAN_WIDTH, DMA_CHAN_REGS)
        self.reset()

    def status(self):
        print("Control :  0b{0:032b}".format(self._internals.CTRL_REG))
        print("Read    :  0x{0:08x}".format(self._internals.READ_ADDR_REG))
        print("Write   :  0x{0:08x}".format(self._internals.WRITE_ADDR_REG))
        print("Transfer:  0x{0:08x}".format(self._internals.TRANS_COUNT_REG))
        # print("Read    :  {}".format(self._internals.READ_ADDR_REG))
        # print("Write   :  {}".format(self._internals.WRITE_ADDR_REG))
        # print("Transfer:  {}".format(self._internals.TRANS_COUNT_REG))

    def reset(self):
        # set defaults
        self.chain_to = None
        self._internals.CTRL.IRQ_QUIET = 1
        self._internals.CTRL.EN = 1  # enable channel
        self._internals.CTRL.HIGH_PRIORITY = 1
        self._internals.CTRL.BSWAP = 0
        self._internals.CTRL.SNIFF_EN = 0
        self._internals.CTRL.RING_SEL = 0
        self._internals.CTRL.RING_SIZE = 0

    def byteswap(self, enabled=None):
        if enabled is not None:
            self._internals.CTRL.BSWAP = enabled
        return self._internals.CTRL.BSWAP

    def enable(self):
        self._internals.CTRL.EN = 1  # enable channel

    def is_enabled(self):
        return self._internals.CTRL.EN

    def disable(self):
        self._internals.CTRL.EN = 0  # enable channel

    @property
    def chain_to(self):
        value = self._internals.CTRL.CHAIN_TO
        return value if value != self.id else None

    @chain_to.setter
    def chain_to(self, value=None):
        if value is None:
            value = self.id
        self._internals.CTRL.CHAIN_TO = int(value)

    def trans_count_trigger(self, count):
        self._internals.TRANS_COUNT_REG = count

    def trigger(self):
        self._internals.CTRL_TRIG.EN = 1  # enable channel and trigger

    @micropython.native
    def is_busy(self):
        return self._internals.CTRL.BUSY

    @micropython.native
    def mem_2_mem(self, source, target, data_size: int = DMA_SIZE_32, BSWAP=0):
        self._internals.CTRL.BSWAP = BSWAP
        self._internals.CTRL.DATA_SIZE = data_size
        self._internals.CTRL.INCR_WRITE = 1
        self._internals.CTRL.INCR_READ = 1
        self._internals.CTRL.TREQ_SEL = TREQ_UNPACED  # start copying
        self._internals.READ_ADDR_REG = addressof(source)
        self._internals.WRITE_ADDR_REG = addressof(target)
        self._internals.TRANS_COUNT_REG = len(source)
        self.trigger()

    @micropython.native
    def mem_2_pio(self, source, pio_state_machine, data_size: int = DMA_SIZE_32, BSWAP=0):
        if pio_state_machine < 4:
            target = PIO0_BASE
            dreq = pio_state_machine
        else:
            target = PIO1_BASE
            pio_state_machine -= 4
            dreq = pio_state_machine + 8
        target += 0x10 + (pio_state_machine << 2)

        self._internals.CTRL.BSWAP = BSWAP
        self._internals.CTRL.DATA_SIZE = data_size
        self._internals.CTRL.INCR_WRITE = 0
        self._internals.CTRL.INCR_READ = 1
        self._internals.CTRL.TREQ_SEL = dreq  # transfer at pace of pio
        self._internals.READ_ADDR_REG = addressof(source)
        self._internals.WRITE_ADDR_REG = target
        self._internals.TRANS_COUNT_REG = len(source)
        self.trigger()

    @micropython.native
    def abort(self):
        self._internals.CTRL_TRIG.IRQ_QUIET = 1  # avoid completion IRQ being called
        self.dma._internals.CHAN_ABORT &= self.mask
        while self.dma._internals.CHAN_ABORT & self.mask:
            pass

    @micropython.native
    def memcopy8(self, source, target):
        return self.mem_2_mem(source, target, DMA_SIZE_8)

    @micropython.native
    def memcopy16(self, source, target):
        return self.mem_2_mem(source, target, DMA_SIZE_16)

    @micropython.native
    def memcopy32(self, source, target):
        return self.mem_2_mem(source, target, DMA_SIZE_32)


class _DMA:
    __instance = None

    def __new__(cls, *nargs, **kwargs):  # ensures only a single instance is created
        if not cls.__instance:
            cls.__instance = super(cls, _DMA).__new__(cls)
        return cls.__instance

    def __init__(self, channels=10):
        print('Initialising DMA')
        self._internals = struct(DMA_BASE, DMA_REGS)
        self._channels = [DMAChannel(i, self) for i in range(channels)]
        self.abort()

    @micropython.native
    def __getitem__(self, id):
        return self._channels[id]

    @micropython.native
    def __iter__(self):
        return self._channels.__iter__()

    @micropython.native
    def abort(self, channel_mask=0xffff):
        self._internals.CHAN_ABORT = channel_mask

    @micropython.native
    def __len__(self):
        return len(self._channels)

    @micropython.native
    def allocate_channel(self) -> DMAChannel:
        ch = self.unused_channel()
        if ch:
            ch.allocated = True
        else:
            raise Exception('Unable to reserve free DMA channel')
        return ch

    @micropython.native
    def unused_channel(self) -> DMAChannel:
        for ch in reversed(self._channels): # lower dma channels are used so are less reliable
            if not ch.is_busy() and not ch.allocated:
                return ch
        return None

    @micropython.native
    def mem_2_mem(self, source, target, data_size: DMA_SIZE_32):
        return self.unused_channel().mem_2_mem(source, target, data_size=data_size)

    @micropython.native
    def mem_2_pio(self, source, state_machine_id, data_size: DMA_SIZE_32, BSWAP=0):
        return self.unused_channel().mem_2_pio(source, state_machine_id, data_size=data_size, BSWAP=BSWAP)


dma = _DMA(channels=DMA_CHAN_COUNT)

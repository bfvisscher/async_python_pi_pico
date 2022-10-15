import array

import micropython

from gbl import make_slice

FULL_SLICE = make_slice[:]


class PixelBuffer:
    def __init__(self, n, type='B'):
        """
        :param n: number of pixels in the buffer
        """
        self.n = n
        self.buf = array.array(type, [0 for _ in range(n)])
        if type == 'B':
            max_value = 0xff
        elif type == 'H':
            max_value = 0xffff
        else:
            max_value = 0xffffffff
        self.max_value = max_value

    @micropython.native
    def __len__(self):
        return self.n

    @micropython.native
    def rotate_left(self, num_of_pixels: int = 1):
        mem = memoryview(self.buf)
        self.buf = mem[num_of_pixels:] + mem[:num_of_pixels]

    @micropython.native
    def rotate_right(self, num_of_pixels: int = 1):
        num_of_pixels = -num_of_pixels
        mem = memoryview(self.buf)
        self.buf = mem[num_of_pixels:] + mem[:num_of_pixels]

    @micropython.native
    def __setitem__(self, idx, v):
        if isinstance(idx, slice):
            for i in range(*idx.indices(self.n)):
                self.buf[idx] = v
        else:
            self.buf[idx] = v

    @micropython.native
    def __getitem__(self, i):
        return self.buf[i]

    @micropython.native
    def __iter__(self):
        yield from self.buf

    @micropython.native
    def fill(self, v, slc=FULL_SLICE):
        i, n, s = slc.indices(self.n)
        buf = self.buf
        while i < n:
            buf[i] = v
            i += s

    @micropython.native
    def fade(self, f, slc=FULL_SLICE):
        self._fade_nd(int(f * 1000), 1000, slc)

    @micropython.native
    def _fade_nd(self, numerator, denominator, slc: slice):
        i, n, s = slc.indices(self.n)
        buf = self.buf
        while i < n:
            buf[i] = (numerator * buf[i]) // denominator
            i += s

    @micropython.native
    def pixel_merge(self, i, p):
        buf = self.buf
        buf[i] = min(self.max_value, p + buf[i])


class PixelBufferPWM(PixelBuffer):
    def __init__(self, n):
        super().__init__(n, 'H')


class PixelBufferNeo(PixelBuffer):

    @micropython.viper
    def in_convert_grb(self, value):
        tmp = ptr8(self.tmp_buf)
        # tmp[0] = 0  # ignored
        tmp[1] = uint(value[1])
        tmp[2] = uint(value[0])
        tmp[3] = uint(value[2])

    @micropython.viper
    def out_convert_grb(self, index: int):
        tmp = ptr8(self.tmp_buf)
        buf = ptr8(self.buf)
        index <<= 2
        tmp[0] = buf[index + 2]
        tmp[1] = buf[index + 1]
        tmp[2] = buf[index + 3]

    @micropython.viper
    def in_convert_grb_dma(self, value):
        tmp = ptr8(self.tmp_buf)
        # tmp[0] = 0  # ignored
        tmp[1] = uint(value[2])  # blue
        tmp[2] = uint(value[0])
        tmp[3] = uint(value[1])

    @micropython.viper
    def out_convert_grb_dma(self, index: int):
        tmp = ptr8(self.tmp_buf)
        buf = ptr8(self.buf)
        index <<= 2
        tmp[0] = buf[index + 2]
        tmp[1] = buf[index + 3]
        tmp[2] = buf[index + 1]

    @micropython.viper
    def in_convert_grbw(self, value):
        tmp = ptr8(self.tmp_buf)
        tmp[0] = uint(value[1])
        tmp[1] = uint(value[0])
        tmp[2] = uint(value[2])  # blue
        tmp[3] = uint(value[3])

    @micropython.viper
    def out_convert_grbw(self, index: int):
        tmp = ptr8(self.tmp_buf)
        buf = ptr8(self.buf)
        index <<= 2
        tmp[0] = buf[index + 1]
        tmp[1] = buf[index + 0]
        tmp[2] = buf[index + 2]
        tmp[3] = buf[index + 3]

    @micropython.viper
    def in_convert_grbw_dma(self, value):
        tmp = ptr8(self.tmp_buf)
        tmp[3] = uint(value[1])
        tmp[2] = uint(value[0])
        tmp[1] = uint(value[2])
        tmp[0] = uint(value[3])

    @micropython.viper
    def out_convert_grbw_dma(self, index: int):
        tmp = ptr8(self.tmp_buf)
        buf = ptr8(self.buf)
        index <<= 2
        tmp[0] = buf[index + 2]
        tmp[1] = buf[index + 3]
        tmp[2] = buf[index + 1]
        tmp[3] = buf[index + 0]

    def __init__(self, n, bpp, dma=False):
        super().__init__(n, 'I')
        self.tmp_buf = array.array('B', [0, 0, 0, 0])
        self.bpp = bpp
        self.n = n
        if not dma:
            if bpp == 3:  # G R B
                self.in_convert = self.in_convert_grb
                self.out_convert = self.out_convert_grb
            elif bpp == 4:  # G R B W
                self.in_convert = self.in_convert_grbw
                self.out_convert = self.out_convert_grbw
        else:
            if bpp == 3:  # G R B
                self.in_convert = self.in_convert_grb_dma
                self.out_convert = self.out_convert_grb_dma
            elif bpp == 4:  # G R B W
                self.in_convert = self.in_convert_grbw_dma
                self.out_convert = self.out_convert_grbw_dma

    def __len__(self):
        return self.n

    @micropython.viper
    def __setitem__(self, idx, v):

        if isinstance(idx, slice):
            self.fill(v, idx)
        else:
            self.in_convert(v)
            buf = ptr32(self.buf)
            tmp = ptr32(self.tmp_buf)

            i = int(idx)
            buf[i] = tmp[0]

    @micropython.viper
    def __getitem__(self, i):
        self.out_convert(i)
        return self.tmp_buf

    @micropython.native
    def fill(self, v, slc: slice = FULL_SLICE):
        return self._fill(v, slc)

    @micropython.viper
    def _fill(self, v, slc):
        self.in_convert(v)
        i_, n_, s_ = slc.indices(self.n)
        i = int(i_)
        n = int(n_)
        s = int(s_)
        buf = ptr32(self.buf)
        tmp = ptr32(self.tmp_buf)

        while i < n:
            buf[i] = tmp[0]
            i += s

    @micropython.viper
    def _fade_nd(self, numerator: int, denominator: int, slc):
        buf = ptr8(self.buf)
        i_, n_, s_ = slc.indices(self.n)
        i = int(i_) << 2
        n = int(n_) << 2
        s = int(s_) << 2

        while i < n:
            j = 0
            while j < 4:
                buf[i + j] = (numerator * buf[i + j]) // denominator
                j += 1
            i += s

    @micropython.viper
    def pixel_merge(self, i: int, v):
        self.in_convert(v)
        buf = ptr8(self.buf)
        tmp = ptr8(self.tmp_buf)
        o = i << 2
        j = 0
        while j < 4:
            new = buf[o + j] + tmp[j]
            buf[o + j] = new if new < 255 else 255
            j += 1


class PixelBufferSegment(PixelBuffer):
    """
    Split a single pixelbuffer into multiple independent sub segments. Each can display different patterns
    and can be accessed independently from each other.
    """

    def __init__(self, pixel_buffer: PixelBuffer, start: int, end: int):
        self.buf = pixel_buffer
        self.start = max(0, min(start, self.buf.n))
        self.end = max(0, min(end, self.buf.n))
        self.n = 1 + self.end - self.start

    @micropython.native
    def _reslice(self, slc):
        start, end, step = slc.indices(self.n)
        self_start = self.start
        return make_slice[start + self_start:end + self_start: step]

    @micropython.native
    def pixel_merge(self, i: int, v):
        return self.buf.pixel_merge(i + self.start, v)

    @micropython.native
    def fade(self, factor: float, slc: slice = FULL_SLICE):
        return self.buf.fade(factor, self._reslice(slc))

    @micropython.native
    def fill(self, v, slc: slice = FULL_SLICE):
        return self.buf.fill(v, self._reslice(slc))

    @micropython.native
    def __getitem__(self, i):
        if isinstance(i, slice):
            i = self._reslice(i)
        else:
            i += self.start
        return self.buf.__getitem__(i)

    @micropython.native
    def __setitem__(self, i: int, v):
        if isinstance(i, slice):
            i = self._reslice(i)
        else:
            i += self.start
        return self.buf.__setitem__(i, v)

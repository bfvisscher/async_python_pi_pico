import random
import time

from gbl import make_slice
from pixel_buffers import PixelBuffer, PixelBufferSegment


def select_pattern(pixel_buffer, patterns, black_board, entry, freq=30):
    cycle_delay_ms = 1000 // freq
    current_pattern = None

    if black_board.get(entry, None) is None or black_board[entry] not in patterns:
        black_board[entry] = list(patterns.keys())[0]

    cur_time = 0
    pattern_delay = 0
    while True:
        new_pattern = black_board.get(entry, current_pattern)
        if current_pattern != new_pattern and new_pattern in patterns:
            active_pattern = patterns[new_pattern]
            iterator = iter(active_pattern[0](pixel_buffer, **active_pattern[1]))
            current_pattern = new_pattern

        if pattern_delay <= cur_time:
            pattern_delay += next(iterator)

        delay_ms = min([pattern_delay - cur_time, cycle_delay_ms])

        yield delay_ms
        cur_time += delay_ms


def blink(pixel_buffer: PixelBuffer, pixel, on_time_ms=200, off_time_ms=800):
    while True:
        pixel_buffer.fill(pixel)
        yield on_time_ms
        pixel_buffer.fade(0)
        yield off_time_ms


def fading_bars(pixel_buffer: PixelBuffer, pixel, fade=0.9, freq=60):
    # 1s cycle
    cycle_delay_ms = 1000 // freq
    while True:
        for cycle in range(freq):
            if cycle:
                pixel_buffer.fade(fade)  # to add fading
                pixel_buffer[(len(pixel_buffer) * cycle) // freq] = pixel
            else:  # cycle==0
                pixel_buffer.fill(pixel)

            yield cycle_delay_ms  # changes were made to update


def piano(pixel_buffer: PixelBuffer, pixel, fade=0.9, freq=60):
    cycle_delay_ms = 1000 // freq
    # hit key every 1/10s
    while True:
        for cycle in range(5):
            pixel_buffer.fade(fade)  # to add fading

            if cycle == 0:
                pixel_buffer[random.randint(0, len(pixel_buffer) - 1)] = pixel
            yield cycle_delay_ms  # 50 hz


def kit(pixel_buffer: PixelBuffer, pixel, fade=0.9, freq=60, cycle_length=60):
    cycle_delay_ms = 1000 // freq

    cycle_lenght_ac = cycle_length - 1
    l = len(pixel_buffer)
    ml = l - 1
    prev_pos = 0

    while True:
        cycle = 0
        old_pos = 0
        for cycle in range(cycle_length):
            # 0 to l-1
            pixel_buffer.fade(fade)
            new_pos = (ml * cycle) // cycle_lenght_ac

            for pos in range(old_pos, new_pos + 1):
                pixel_buffer[pos] = pixel
            old_pos = new_pos
            yield cycle_delay_ms

        old_pos = ml
        for cycle in range(cycle_length):
            # l-1 to 0
            pixel_buffer.fade(fade)
            new_pos = ml - (ml * cycle) // cycle_lenght_ac
            for pos in range(new_pos, old_pos + 1):
                pixel_buffer[pos] = pixel
            old_pos = new_pos
            yield cycle_delay_ms


def snakes(pixel_buffer: PixelBuffer, pixel_list, max_speed=10, fade=0.9, freq=60, cycle_length_s=2):
    cycle_delay_ms = 1000 // freq
    l = len(pixel_buffer)
    snakes = len(pixel_list)
    direction = [random.randint(-max_speed, max_speed - 1) for _ in range(snakes)]
    direction = [s if s < 0 else s + 1 for s in direction]  # avoid 0

    pos = [random.randint(0, l) for _ in range(snakes)]

    while True:
        # Iterate over each LED in the strip
        pixel_buffer.fade(fade)
        for i in range(snakes):
            p = pos[i]
            d = 1 if direction[i] > 0 else -1
            s = direction[i] * d  # speed
            for k in range(s):
                p += d
                if p < 0 or p >= l:
                    d = -d
                    direction[i] = d * s
                    p += 2 * d
                pixel_buffer.pixel_merge(p, pixel_list[i])
            pos[i] = p
        yield cycle_delay_ms


def cylon(pixel_buffer: PixelBuffer, pixel, fade=0.85, freq=60):
    old_pos = -1
    l = len(pixel_buffer)
    cycle_delay_ms = 1000 // freq
    if isinstance(pixel, int):
        def fade_fcn(x):
            return int(x * fade)
    else:
        def fade_fcn(x_list):
            return [int(x * fade) for x in x_list]

    while True:
        for cycle in range(2 * freq):
            pixel_buffer.fade(fade)  # to add fading

            pos = ((l * 2 - 2) * cycle) // (2 * freq)
            if pos >= l:
                pos = (l - 2) - (pos - l)

            pixel_buffer[pos] = pixel
            intensity = pixel
            if True or old_pos != pos:
                for i in range(1, 5):

                    intensity = fade_fcn(intensity)
                    if pos + i < l:
                        pixel_buffer.pixel_merge(pos + i, intensity)

                    if pos - i >= 0:
                        pixel_buffer.pixel_merge(pos - i, intensity)

                old_pos = pos
            yield cycle_delay_ms  # 50 hz


def morse_code(pixel_buffer: PixelBuffer, message, on_pixel, off_pixel, loop=True, reverse=False, dit=250):
    morse_code_itu = {
        'a': ".-",
        'b': "-...",
        'c': "-.-.",
        'd': "-..",
        'e': ".",
        'f': "..-.",
        'g': "--.",
        'h': "....",
        'i': "..",
        'j': ".---",
        'k': "-.-",
        'l': ".-..",
        'm': "--",
        'n': "-.",
        'o': "---",
        'p': ".--.",
        'q': "--.-",
        'r': ".-.",
        's': "...",
        't': "-",
        'u': "..-",
        'v': "...-",
        'w': ".--",
        'x': "-..-",
        'y': "-.--",
        'z': "--..",

        '1': ".----",
        '2': "..---",
        '3': "...--",
        '4': "....-",
        '5': ".....",
        '6': "-....",
        '7': "--...",
        '8': "---..",
        '9': "----.",
        '0': "-----",

    }
    if reverse:
        def on():
            pixel_buffer.rotate_left(1)
            pixel_buffer[-1] = on_pixel
            return dit

        def off():
            pixel_buffer.rotate_left(1)
            pixel_buffer[-1] = off_pixel
            return dit
    else:
        def on():
            pixel_buffer.rotate_right(1)
            pixel_buffer[0] = on_pixel
            return dit

        def off():
            pixel_buffer.rotate_right(1)
            pixel_buffer[0] = off_pixel
            return dit

    first = True
    while first or loop:
        first = False

        for c in message:
            c = c.lower()  # convert to lower case
            if c == ' ':
                for t in range(4):
                    yield off()
            elif c in morse_code_itu:
                for s in morse_code_itu[c]:
                    if s == '.':  # blink dit
                        yield on()
                    elif s == '-':  # blink dah  (=3x dit)
                        for t in range(3):
                            yield on()
                    yield off()

                for t in range(2):
                    yield off()

        for t in range(4):
            yield off()  # waited 3 dits already (between characters) so this makes it 7 for next message


def breathing(pixel_buffer, pixel_list, turn_on_ms=2000, on_time_ms=1000, turn_off_ms=1900, off_time_ms=100,
              freq=60):
    if isinstance(pixel_list[0], int):
        def fade_fcn(x, fade):
            return int(x * fade)
    else:
        def fade_fcn(x_list, fade):
            return [int(x * fade) for x in x_list]

    cycle_delay_ms = 1000 // freq

    while True:
        for pixel in pixel_list:
            for i in range(0, turn_on_ms, cycle_delay_ms):
                pixel_buffer.fill(fade_fcn(pixel, i / turn_on_ms))
                yield cycle_delay_ms

            pixel_buffer.fill(pixel)
            yield on_time_ms

            for i in range(turn_off_ms, 0, -cycle_delay_ms):
                pixel_buffer.fill(fade_fcn(pixel, i / turn_off_ms))
                yield cycle_delay_ms

            pixel_buffer.fill(fade_fcn(pixel, 0))

            yield off_time_ms


def attention(pixel_buffer, pixel, freq=60, fade=0.8):
    n = len(pixel_buffer)
    half = (n >> 1)
    cycle_delay_ms = 1000 // freq
    fade2 = fade * fade
    centre_slice = make_slice[(half - 1):n - (half - 1)]

    while True:
        # close in cycle                
        for i in range(0, freq, 2):  # .5s
            r = half * i // freq
            pixel_buffer.fill(pixel, make_slice[:r])
            pixel_buffer.fill(pixel, make_slice[n - 1 - r:])
            yield cycle_delay_ms
        pixel_buffer.fill(pixel)
        yield cycle_delay_ms

        # trail fading

        for i in range(0, freq, 2):  # .5s
            r = half * i // (freq - 1)
            us = make_slice[:r]
            ls = make_slice[n - 1 - r:]
            pixel_buffer.fade(fade2, us)
            pixel_buffer.fade(fade2, ls)
            pixel_buffer.fill(pixel, centre_slice)
            yield cycle_delay_ms

        # fade out        
        for i in range(0, freq, 4):  #
            pixel_buffer.fade(fade2)
            if i < freq / 2:
                pixel_buffer.fill(pixel, centre_slice)
            yield cycle_delay_ms
        pixel_buffer.fade(0)  # force all off
        # random blinking
        for i in range(0, 3 * freq, 1):
            if random.randint(0, 3 * freq) < i:
                pixel_buffer.fill(pixel, centre_slice)
            else:
                pixel_buffer.fade(0, centre_slice)
            yield cycle_delay_ms

        pixel_buffer.fill(pixel, centre_slice)
        # close in cycle
        prev = 0
        for i in range(0, freq + 2, 2):  # .5s
            r = half * i // freq
            pixel_buffer.fill(pixel, make_slice[half - r:half - prev])
            pixel_buffer.fill(pixel, make_slice[half + prev:half + r])
            pixel_buffer.fade(fade)
            prev = r
            yield cycle_delay_ms

        for i in range(0, freq, 4):  # .5s
            pixel_buffer.fade(fade)
            yield cycle_delay_ms
        pixel_buffer.fade(0)
        yield 500


def multi_pattern(pixel_buffer, segment_sizes, segment_patterns):
    assert len(segment_sizes) == len(segment_patterns)

    segments = []
    start = 0
    for size in segment_sizes:
        segments.append(PixelBufferSegment(pixel_buffer, start, start + size - 1))
        start += size

    iterators = [iter(pat[0](seg, **pat[1])) for seg, pat in zip(segments, segment_patterns)]
    delays = [0 for _ in iterators]

    cur_time = 0
    while True:
        for i, itr in enumerate(iterators):
            if delays[i] <= cur_time:
                delays[i] += next(itr)

        delay_ms = min([d - cur_time for d in delays])

        yield delay_ms
        cur_time += delay_ms


def clear(pixel_buffer, freq=60, wait_cycles=20):
    pixel_buffer.fade(0)
    yield 0
    cycle_delay_ms = (1000 * wait_cycles) // freq
    while True:
        yield cycle_delay_ms


def left_right_slow(pixel_buffer: PixelBuffer, lr_pixel, rl_pixel, speed=.5, freq=60, fade=.8):
    cycle_delay_ms = 1000 // freq
    space = len(pixel_buffer) // 5

    n = len(pixel_buffer)
    pos = 0.0
    if isinstance(lr_pixel, int):
        def fade_fcn(x, si):
            return int(x * si)
    else:
        def fade_fcn(x_list, si):
            return [int(x * si) for x in x_list]

    while True:
        pixel_buffer.fade(fade)
        i = int(pos)
        si = pos - i
        while i < n:
            pixel_buffer.pixel_merge(i, lr_pixel)
            pixel_buffer.pixel_merge(n - 1 - i, rl_pixel)
            i += space

        if si >= speed:
            corr = (si - speed) * (1 - fade)

            faded_lr_pixel = fade_fcn(lr_pixel, speed + corr)
            faded_rl_pixel = fade_fcn(rl_pixel, speed + corr)

            i = int(pos) + 1

            while i < n:
                pixel_buffer.pixel_merge(i, faded_lr_pixel)
                pixel_buffer.pixel_merge(n - 1 - i, faded_rl_pixel)
                i += space

        yield cycle_delay_ms
        pos += speed
        if pos >= space:
            pos = 0


def strip_clock(pixel_buffer: PixelBuffer):
    n = len(pixel_buffer)
    step_half_hour = n // 48
    step_half_5minute = n // 24
    separator_pixel_3hour = [1, 0, 0]
    separator_pixel_12hour = [127, 0, 127]
    hour_pixel = [0, 127, 0]
    minute_pixel = [32, 32, 0]
    delay_ms = 250
    while True:
        # clear the whole thing
        year, month, day, hour, minute, second, weekday, yearday = time.localtime()
        pixel_buffer.fade(0)

        # colour the minutes
        minute_part = 2 * minute // 5
        if minute_part == 0:
            minute_part = 24
        pixel_buffer[(minute_part - 1) * step_half_5minute:minute_part * step_half_5minute] = minute_pixel
        if minute_part == 24:
            minute_part = 0
        pixel_buffer[minute_part * step_half_5minute:(minute_part + 1) * step_half_5minute] = minute_pixel

        # colour the hour
        hour_part = 2 * hour
        if hour_part == 0:
            hour_part = 48
        pixel_buffer[(hour_part - 1) * step_half_hour:hour_part * step_half_hour] = hour_pixel
        if hour_part == 48:
            hour_part = 0
        pixel_buffer[hour_part * step_half_hour:(hour_part + 1) * step_half_hour] = hour_pixel

        # show hour separators
        pixel_buffer[6 * step_half_hour:n:6 * step_half_hour] = separator_pixel_3hour

        centre_slice = make_slice[24 * step_half_hour:n:24 * step_half_hour]
        if second % 2:
            pixel_buffer[centre_slice] = separator_pixel_12hour  # centre pixel
        else:
            pixel_buffer.fade(0, centre_slice)  # clear centre pixel

        yield delay_ms

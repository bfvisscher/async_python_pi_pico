import async_hass
from async_drivers import *
from async_runner import *
from async_tasks import *
from hass_entities import hass_lightstrip
from patterns import *
import json
PICO_W = True

if PICO_W:
    ON_BOARD_PIN = 'LED'
else:
    ON_BOARD_PIN = 25

pin_strip_upper = 27
pin_strip_lower = 6

blackboard = {}  # used to create a shared variable space

with open('secrets.json', 'rt') as f:
    secrets = json.load(f)

hass = async_hass.HomeAssistantMQTT('192.168.68.11:1883', secrets['mqtt.username'], secrets['mqtt.password'], secrets['wifi.ssid'], secrets['wifi.password'])

networklogins = {secrets['wifi.ssid']: secrets['wifi.password']}
# add_task(connect_wifi, networklogins, blackboard)


add_task(cpu_load)
ledstrip_driver = neo_driver_dma

# add_task(pin_driver, [ON_BOARD_PIN], blink, pixel=1)

# ***********************
# add_task(ledstrip_driver, pin_strip_upper, blink, pixel=[255, 0, 0], n=500, bpp=3)


# add_task(ledstrip_driver, pin_strip_upper, breathing, pixel_list=[[255, 0, 0]], n=500, bpp=3)


#   neo_driver_irq  #50%  (96%)     neo_driver2  - 94.3%  (48%)
pl3 = [
    #    [255, 0, 0],
    [255, 255, 0],
    #    [0, 255, 0],
    [0, 255, 255],
    #    [0, 0, 255],
    [255, 0, 255],
]

pl4 = [
    [255, 0, 0, 0],
    [255, 255, 0, 0],
    [0, 255, 0, 0],
    [0, 255, 255, 0],
    [0, 0, 255, 0],
    [255, 0, 255, 0],
    [0, 0, 0, 255],
]

# add_task(ledstrip_driver, pin_strip_upper, kit, pixel=[255, 0, 0], n=144, bpp=3, freq=60, fade=.85, cycle_length=30, state_machine=0)

# add_task(ledstrip_driver, pin_strip_upper, attention, pixel=[0, 255, 255], n=144, bpp=3, freq=60, state_machine=0)


pattern_attention_bpp3 = (attention, {'pixel': [255, 0, 0]})
pattern_clock = (strip_clock, {})
pattern_attention_multisegment_bpp3 = (multi_pattern, {'segment_sizes': [14, 116, 14],
                                                       'segment_patterns': [pattern_attention_bpp3,
                                                                            pattern_attention_bpp3,
                                                                            pattern_attention_bpp3]})

pattern_snakes_bpp3 = (snakes, {'pixel_list': pl3, 'max_speed': 3, 'fade': 0.7})
pattern_piano_bpp3 = (piano, {'pixel': [255, 255, 255]})


pattern_blink_bpp4 = (blink, {'pixel': [0, 255, 255, 0]})
pattern_breathing_bpp4 = (breathing, {'pixel_list': pl4})
pattern_piano_bpp4 = (piano, {'pixel': [0, 0, 0, 255]})
pattern_snakes_bpp4 = (snakes, {'pixel_list': pl4, 'max_speed': 6, 'fade': 0.7})
pattern_down_bpp4 = (left_right_slow, {'lr_pixel': [0, 0, 0, 0], 'rl_pixel': [0, 255, 255, 0]})
pattern_up_bpp4 = (left_right_slow, {'lr_pixel': [255, 255, 0, 0], 'rl_pixel': [0, 0, 0, 0]})
pattern_updown_bpp4 = (left_right_slow, {'lr_pixel': [255, 255, 0, 0], 'rl_pixel': [0, 255, 255, 0]})

strip1_patterns = {
    'clock': pattern_clock,
    'knocking': pattern_attention_multisegment_bpp3,
    'party': pattern_snakes_bpp3,
    'piano': pattern_piano_bpp3,
}

strip2_patterns = {
    'up': pattern_up_bpp4,
    'down': pattern_down_bpp4,
    'updown': pattern_updown_bpp4,
    'party': pattern_snakes_bpp4,
    'piano': pattern_piano_bpp4,
    'breathing': pattern_breathing_bpp4,    
}

# selection of the pattern

# execution of the patterns
add_task(ledstrip_driver, pin_strip_upper, hass_lightstrip, name='Lightstrip Door', hass=hass,
         patterns=strip1_patterns, n=144, bpp=3, state_machine=0)
add_task(ledstrip_driver, pin_strip_lower, hass_lightstrip, name='Lightstrip Stairs', hass=hass,
         patterns=strip2_patterns, n=300, bpp=4, state_machine=1)

# add_task(ledstrip_driver, pin_strip_lower, kit, pixel=[0, 0, 0, 255], n=300, bpp=4, freq=60, fade=.9, state_machine=1)  # 57%

# add_task(ledstrip_driver, pin_strip_upper, breathing, pixel_list=pl3, n=144, bpp=3, freq=50, state_machine=0)

# add_task(ledstrip_driver, pin_strip_upper, snakes, pixel_list=pl3, n=144, bpp=3, freq=50, max_speed=6, state_machine=0, fade=.7)
# add_task(ledstrip_driver, pin_strip_lower, snakes, pixel_list=pl4, n=300, bpp=4, freq=50, max_speed=4, state_machine=1, fade=.7)


# add_task(ledstrip_driver, pin_strip_lower, multi_pattern, segment_sizes = [75, 75, 75, 75], segment_patterns=demo_patterns_bpp4,  n=300, bpp=4, state_machine=1, freq=60)

# add_task(ledstrip_driver, pin_strip_upper, clear, n=144, bpp=3, freq=50, state_machine=0)
# add_task(ledstrip_driver, pin_strip_lower, clear, n=300, bpp=4, freq=50, state_machine=1)

# add_task(ledstrip_driver, pin_strip_upper, strip_clock, n=144, bpp=3, state_machine=0)

# ******************** Patterns to use ***********************

# add_task(ledstrip_driver, pin_strip_upper, multi_pattern, segment_sizes=[36, 72, 36], segment_patterns=attention_patterns_bpp3, n=144, bpp=3, state_machine=0, freq=60)
# add_task(ledstrip_driver , pin_strip_lower, left_right_slow, lr_pixel=[255, 255, 0, 0], rl_pixel=[0, 255, 255, 0], n=300, bpp=4, state_machine=1, freq=60)

start_tasks()  # keeps running forever

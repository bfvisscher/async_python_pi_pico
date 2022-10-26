import json

import async_hass
from async_pb_drivers import *
from async_runner import *
from async_tasks import *
from patterns import *
import machine

# This is a project that runs on a pi pico W and allows for control
# of two neostripts with different effect patterns via home assistant.
#
#
# TO USE: MOdify line 35 in this file and setup the MQTT ip address. 
#         create a json dictionary file called secrets.json and set
#         your "mqtt.username", "mqtt.password","wifi.ssid" and "wifi.password"
#         keys so they can be used in that same command.
#
#
# Define the length, connected pin and strip type (bpp:3 for rgb, 4 for rgbw)

machine.freq(200_000_000)

upper = {'pin': 27,
         'length': 144,  # 144 
         'bpp': 3,
         'freq': 60
         }

lower = {'pin': 6,
         'length': 300,  # 300
         'bpp': 4,
         'freq': 60 
         }

with open('secrets.json', 'rt') as f:
    secrets = json.load(f)

hass_mqtt = async_hass.HomeAssistantMQTT('192.168.68.11:1883', secrets['mqtt.username'], secrets['mqtt.password'],
                                         secrets['wifi.ssid'], secrets['wifi.password'])

add_task(cpu_load, time_between_report_ms=2000) # mqtt=hass_mqtt
add_task(heartbeat)

ledstrip_driver = neo_driver_dma
#ledstrip_driver = neo_driver_pio
#ledstrip_driver = neo_driver_bitstream (only works for bpp4)
# ***********************

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


def test_pattern(pixel_buffer:PixelBuffer):
    bpp = pixel_buffer.bpp    
    n = len(pixel_buffer)
    print('Testing neopixels. Length: %i,  bpp: %i'%(n,bpp))
    while True:
        print('all black')
        pixel_buffer.fade(0)
        yield 3000
        
        print('full on')
        white_pixel = pixel_buffer.max_pixel_value
        print('white pixel : ', white_pixel)
        pixel_buffer.fill(white_pixel)
        yield 3000
        
        print('red on')
        red_pixel = [ 255 if i==0 else 0 for i in range(bpp)]
        pixel_buffer.fill(red_pixel)
        yield 3000

        print('green on')
        green_pixel = [ 255 if i==1 else 0 for i in range(bpp)]
        pixel_buffer.fill(green_pixel)
        yield 3000

        print('blue on')
        blue_pixel = [ 255 if i==2 else 0 for i in range(bpp)]
        pixel_buffer.fill(blue_pixel)
        yield 3000

        print('first on')
        pixel_buffer.fade(0)
        pixel_buffer[0]=white_pixel
        yield 3000

        print('last on')
        pixel_buffer.fade(0)
        pixel_buffer[n-1]=white_pixel
        yield 3000




pattern_attention_bpp3 = (attention, {'pixel': [255, 0, 0], 'freq': upper['freq']})
pattern_clock = (strip_clock, {})
pattern_attention_multisegment_bpp3 = (multi_pattern, {'segment_sizes': [14, 116, 14],
                                                       'segment_patterns': [pattern_attention_bpp3,
                                                                            pattern_attention_bpp3,
                                                                            pattern_attention_bpp3]})

pattern_snakes_bpp3 = (snakes, {'pixel_list': pl3, 'max_speed': 3, 'fade': 0.7, 'freq': upper['freq']})
pattern_piano_bpp3 = (piano, {'pixel': [255, 255, 255], 'freq': upper['freq']})

pattern_blink_bpp4 = (blink, {'pixel': [0, 255, 255, 0]})
pattern_breathing_bpp4 = (breathing, {'pixel_list': pl4, 'freq': lower['freq']})
pattern_piano_bpp4 = (piano, {'pixel': [0, 0, 0, 255]})
pattern_snakes_bpp4 = (snakes, {'pixel_list': pl4, 'max_speed': 6, 'fade': 0.7, 'freq': lower['freq']})
pattern_down_bpp4 = (left_right_slow, {'lr_pixel': [0, 0, 0, 0], 'rl_pixel': [0, 255, 255, 0], 'freq': lower['freq']})
pattern_up_bpp4 = (left_right_slow, {'lr_pixel': [255, 255, 0, 0], 'rl_pixel': [0, 0, 0, 0], 'freq': lower['freq']})
pattern_updown_bpp4 = (left_right_slow, {'lr_pixel': [255, 255, 0, 0], 'rl_pixel': [0, 255, 255, 0], 'freq': lower['freq']})

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

# execution of test patterns

#add_task(ledstrip_driver, lower['pin'], test_pattern, n=lower['length'], bpp=lower['bpp'], state_machine=0)
#add_task(ledstrip_driver, upper['pin'], test_pattern, n=upper['length'], bpp=upper['bpp'], state_machine=1)


# execution of the patterns via HASS 


add_task(ledstrip_driver, upper['pin'], hass_lightstrip, name='Lightstrip Door', mqtt=hass_mqtt,
          patterns=strip1_patterns, n=upper['length'], bpp=upper['bpp'], state_machine=0)

add_task(ledstrip_driver, lower['pin'], hass_lightstrip, name='Lightstrip Stairs', mqtt=hass_mqtt,
         patterns=strip2_patterns, n=lower['length'], bpp=lower['bpp'], state_machine=1)

#s1_pattern = 'party'
#add_task(ledstrip_driver, upper['pin'], strip1_patterns[s1_pattern][0], n=upper['length'], bpp=upper['bpp'], **strip1_patterns[s1_pattern][1], state_machine=0)

# add_task(ledstrip_driver, upper['pin'], breathing, pixel_list=pl3, n=144, bpp=3, freq=50, state_machine=0)


# ********* Different patterns for testing *****************************

# add_task(ledstrip_driver, lower['pin'], kit, pixel=[255, 0, 0, 0], n=lower['length'], bpp=lower['bpp'], freq=60,
#         fade=.9, state_machine=1)  # 57%

# add_task(ledstrip_driver, upper['pin'], breathing, pixel_list=pl3, n=144, bpp=3, freq=50, state_machine=0)

# add_task(ledstrip_driver, upper['pin'], snakes, pixel_list=pl3, n=144, bpp=3, freq=50, max_speed=6, state_machine=0, fade=.7)
# add_task(ledstrip_driver, lower['pin'], snakes, pixel_list=pl4, n=lower['length'], bpp=lower['bpp'], freq=50, max_speed=4, state_machine=1, fade=.7)


# add_task(ledstrip_driver, lower['pin'], multi_pattern, segment_sizes = [75, 75, 75, 75], segment_patterns=demo_patterns_bpp4,  n=300, bpp=4, state_machine=1, freq=60)

# add_task(ledstrip_driver, upper['pin'], clear, n=144, bpp=3, freq=50, state_machine=0)
# add_task(ledstrip_driver, lower['pin'], clear, n=300, bpp=4, freq=50, state_machine=1)

# add_task(ledstrip_driver, upper['pin'], strip_clock, n=144, bpp=3, state_machine=0)

# ******************** Patterns to use ***********************

# add_task(ledstrip_driver, pin_strip_upper, multi_pattern, segment_sizes=[36, 72, 36], segment_patterns=attention_patterns_bpp3, n=144, bpp=3, state_machine=0, freq=60)
# add_task(ledstrip_driver , pin_strip_lower, left_right_slow, lr_pixel=[255, 255, 0, 0], rl_pixel=[0, 255, 255, 0], n=300, bpp=4, state_machine=1, freq=60)


start_tasks()  # keeps running forever

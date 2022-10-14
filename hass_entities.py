import uasyncio

import async_hass


def hass_lightstrip(pixel_buffer, name, hass: async_hass.HomeAssistantMQTT, patterns=dict()):
    if pixel_buffer.bpp == 3:
        lightmode = "rgb"
    else:
        lightmode = "rgbw"

    effect_list = list(patterns.keys())

    hass_entity_config = {
        "schema": "json",
        "effect_list": effect_list,
        "color_mode": lightmode is not None,
        "brightness": True,
        "effect": len(effect_list) > 0,
        "supported_color_modes": [lightmode],
        "icon": "mdi:led-strip-variant",
        "optimistic": False,
        "qos": 1,
        "retain": True
    }

    def command_callback(entity, command):

        if command.get('effect', False) and command.get('state', 'OFF') == 'ON':
            entity.pattern = True
            #
        if command.get('color', False):
            entity.pattern = False

        # update the following
        for key in ['effect', 'brightness', 'color', 'state']:
            if key in command:
                entity.state[key] = command[key]

        entity.new_command.set()
        if entity.state['state'] == 'OFF':
            entity.state = {'state': 'OFF'}  # clear of all other info
        return entity.state

    initial_state = {"state": "OFF"}

    entity = async_hass.HomeAssistantEntity(name, 'light', hass, hass_entity_config, initial_state, command_callback)
    entity.pattern = False
    entity.new_command = uasyncio.Event()
    current_pattern = None

    if pixel_buffer.bpp == 3:
        lightmode = "rgb"
    else:
        lightmode = "rgbw"

    yield 0
    while True:
        if entity.pattern and entity.state['state'] == 'ON':
            cur_time = 0
            new_pattern = entity.state.get('effect', current_pattern)
            if current_pattern != new_pattern and new_pattern in patterns:
                active_pattern = patterns[new_pattern]
                iterator = iter(active_pattern[0](pixel_buffer, **active_pattern[1]))
                current_pattern = new_pattern
            yield next(iterator)
        else:
            if entity.state['state'] == 'ON':
                # colour has been send
                brightness = entity.state.get('brightness', 255)
                color = entity.state.get('color', {})
                pixel_buffer.fill([brightness * color.get(c, 0) // 255 for c in lightmode])
            else:
                # state is OFF
                pixel_buffer.fade(0)
            entity.new_command.clear()
            yield entity.new_command.wait()

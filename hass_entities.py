# MIT License (MIT)
# Copyright (c) 2022 Bart-Floris Visscher
# https://opensource.org/licenses/MIT


from async_hass import HomeAssistantMQTT, HomeAssistantEntity


def HassSensor(mqtt, name, initial_state=0, unit_of_measurement="", icon="mdi:gauge",
               **kwargs) -> HomeAssistantEntity:
    """

    :param mqtt: hass_mqtt hass_mqtt server
    :param name: name of the entity
    :param initial_state: assume this value
    :param unit_of_measurement: to add %  or m/s etc.
    :param icon: Name of the hass icon to use
    :return:
    """
    hass_entity_config = {
        "icon": icon,
        "force_update": True,
        "unit_of_measurement": unit_of_measurement,
    }
    hass_entity_config.update(**kwargs)
    return HomeAssistantEntity(name, 'sensor', mqtt, hass_entity_config, initial_state, None, qos=0)


def HassButton(mqtt: HomeAssistantMQTT, name, command_callback, icon="mdi:gesture-tap-button",
               **kwargs) -> HomeAssistantEntity:
    """

    :param mqtt: hass_mqtt hass_mqtt server
    :param name: name of the entity
    :param command_callback: method to call upon receiving a events from hass_mqtt  (will ONLY receive 'PRESS')
    :param icon: Name of the hass_mqtt icon to use
    :return:
    """
    hass_entity_config = {
        "icon": icon,
        "optimistic": False,
        "qos": 1,
        "retain": False  # do not retain to avoid historical button presses when starting
    }
    hass_entity_config.update(**kwargs)
    return HomeAssistantEntity(name, 'button', mqtt, hass_entity_config, None, command_callback)


def HassNumber(mqtt: HomeAssistantMQTT, name, command_callback, initial_value=0, min_value=0, max_value=100, step=1,
               unit="", use_box=False, icon="mdi:speedometer", **kwargs) -> HomeAssistantEntity:
    """

    :param mqtt: hass_mqtt hass_mqtt server
    :param name: name of the entity
    :param command_callback: method to call upon receiving a events from hass_mqtt
    :param initial_value: initialise with this value
    :param min_value: lowest value
    :param max_value: highest value
    :param step: minimum events
    :param unit: Unit of the value being used
    :param use_box: True to use numeric input, False to use slider
    :param icon: Name of the hass_mqtt icon to use
    :return:
    """
    hass_entity_config = {
        "icon": icon,
        "optimistic": False,
        "qos": 1,
        "min": min_value,
        "max": max_value,
        "step": step,
        "mode": "box" if use_box else "slider",
        "unit_of_measurement": unit,
        "retain": True
    }
    hass_entity_config.update(**kwargs)
    return HomeAssistantEntity(name, 'number', mqtt, hass_entity_config, initial_value,
                               command_callback)


def HassLight(mqtt: HomeAssistantMQTT, name, command_callback, color_mode=None, effect_list=[],
              initial_state={"state": "OFF"}, icon="mdi:lightbulb-variant-outline", **kwargs) -> HomeAssistantEntity:
    """
    Create an entity representing a light

    :param name: Name of the entity
    :param mqtt: hass_mqtt server connected to home assistant
    :param command_callback: function to be used when receiving commands from hass_mqtt
    :param color_mode: supported colour modes ie 'onoff', 'brightness', 'color_temp', 'hs', 'xy', 'rgb', 'rgbw', 'rgbww', 'white'
    :param effect_list: list of supported effects
    :param initial_state:
    :return:
    """

    hass_entity_config = {
        "schema": "json",
        "effect_list": effect_list,
        "color_mode": color_mode is not None,
        "brightness": 'onoff' != color_mode,  # all other modes support brightness
        "effect": len(effect_list) > 0,
        "icon": icon,
        "optimistic": False,
        "qos": 1,
        "retain": True
    }
    if color_mode is not None:
        hass_entity_config["supported_color_modes"] = color_mode
    hass_entity_config.update(**kwargs)
    return HomeAssistantEntity(name, 'light', mqtt, hass_entity_config, initial_state, command_callback,
                               device=None)  # HASS doesn't recognise more than one light on the same device

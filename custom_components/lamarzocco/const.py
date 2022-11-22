"""Constants for the La Marzocco integration."""

from lmdirect.const import MODEL_NAME
from lmdirect.msgs import *

DOMAIN = "lamarzocco"

"""Set polling interval at 20s."""
POLLING_INTERVAL = 30

"""Configuration parameters"""
CONF_SERIAL_NUMBER = "serial_number"
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_KEY = "key"
CONF_MACHINE_NAME = "machine_name"
CONF_MODEL_NAME = "model_name"

DEFAULT_PORT = 1774

DEFAULT_NAME = "Espresso Machine"

SCHEMA = "schema"
MODELS_SUPPORTED = "supported"
FUNC = "func"

SUPPORTED = "supported"
MODELS = [MODEL_GS3_AV, MODEL_GS3_MP, MODEL_LM]

"""List of attributes for each entity based on model."""
ATTR_MAP_MAIN_GS3_AV = [
    DATE_RECEIVED,
    MACHINE_NAME,
    MODEL_NAME,
    UPDATE_AVAILABLE,
    HEATING_STATE,
    (DOSE, "k1"),
    (DOSE, "k2"),
    (DOSE, "k3"),
    (DOSE, "k4"),
    (DOSE, "k5"),
    DOSE_HOT_WATER,
    FRONT_PANEL_DISPLAY,
]

ATTR_MAP_MAIN_GS3_MP = [
    DATE_RECEIVED,
    MACHINE_NAME,
    MODEL_NAME,
    UPDATE_AVAILABLE,
    HEATING_STATE,
    FRONT_PANEL_DISPLAY,
]

ATTR_MAP_MAIN_LM = [
    DATE_RECEIVED,
    MACHINE_NAME,
    MODEL_NAME,
    UPDATE_AVAILABLE,
    HEATING_STATE,
]

ATTR_MAP_STEAM_BOILER_ENABLE = [
    DATE_RECEIVED,
]

ATTR_MAP_PREBREW_GS3_AV = [
    DATE_RECEIVED,
    (PREBREWING, TON, "k1"),
    (PREBREWING, TON, "k2"),
    (PREBREWING, TON, "k3"),
    (PREBREWING, TON, "k4"),
    (PREBREWING, TOFF, "k1"),
    (PREBREWING, TOFF, "k2"),
    (PREBREWING, TOFF, "k3"),
    (PREBREWING, TOFF, "k4"),
]

ATTR_MAP_PREINFUSION_GS3_AV = [
    DATE_RECEIVED,
    (PREINFUSION, "k1"),
    (PREINFUSION, "k2"),
    (PREINFUSION, "k3"),
    (PREINFUSION, "k4"),
]

ATTR_MAP_PREINFUSION_LM = [
    DATE_RECEIVED,
    (PREINFUSION, "k1"),
]

ATTR_MAP_PREBREW_LM = [
    DATE_RECEIVED,
    (PREBREWING, TON, "k1"),
    (PREBREWING, TOFF, "k1"),
]

ATTR_MAP_COFFEE = [
    DATE_RECEIVED,
    COFFEE_HEATING_ELEMENT_HOURS,
]

ATTR_MAP_STEAM = [
    DATE_RECEIVED,
    STEAM_HEATING_ELEMENT_HOURS,
]

ATTR_MAP_AUTO_ON_OFF = [
    DATE_RECEIVED,
    (SUN, AUTO),
    (SUN, ON, TIME),
    (SUN, OFF, TIME),
    (MON, AUTO),
    (MON, ON, TIME),
    (MON, OFF, TIME),
    (TUE, AUTO),
    (TUE, ON, TIME),
    (TUE, OFF, TIME),
    (WED, AUTO),
    (WED, ON, TIME),
    (WED, OFF, TIME),
    (THU, AUTO),
    (THU, ON, TIME),
    (THU, OFF, TIME),
    (FRI, AUTO),
    (FRI, ON, TIME),
    (FRI, OFF, TIME),
    (SAT, AUTO),
    (SAT, ON, TIME),
    (SAT, OFF, TIME),
]

ATTR_MAP_DRINK_STATS_GS3_AV = [
    DATE_RECEIVED,
    (DRINKS, "k1"),
    (DRINKS, "k2"),
    (DRINKS, "k3"),
    (DRINKS, "k4"),
    CONTINUOUS,
    TOTAL_FLUSHING,
    DRINKS_HOT_WATER,
    HOT_WATER,
    TOTAL_COFFEE,
    TOTAL_COFFEE_ACTIVATIONS,
]

ATTR_MAP_DRINK_STATS_GS3_MP_LM = [
    DATE_RECEIVED,
    (DRINKS, "k1"),
    CONTINUOUS,
    TOTAL_FLUSHING,
    DRINKS_HOT_WATER,
    HOT_WATER,
    TOTAL_COFFEE,
    TOTAL_COFFEE_ACTIVATIONS,
]

ATTR_MAP_WATER_RESERVOIR = [
    WATER_RESERVOIR_CONTACT
]

ENTITY_TAG = "tag"
ENTITY_TEMP_TAG = "temp_tag"
ENTITY_TSET_TAG = "tset_tag"
ENTITY_NAME = "name"
ENTITY_MAP = "map"
ENTITY_TYPE = "type"
ENTITY_ICON = "icon"
ENTITY_FUNC = "func"
ENTITY_CLASS = "class"
ENTITY_UNITS = "units"

PLATFORM = "platform"
PLATFORM_SENSOR = "sensor"
PLATFORM_SWITCH = "switch"

"""Constants for the La Marzocco integration."""

from lmdirect.msgs import *

DOMAIN = "lamarzocco"

"""Set polling interval at 20s."""
POLLING_INTERVAL = 20

"""Configuration parameters"""
CONF_SERIAL_NUMBER = "serial_number"
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_KEY = "key"
CONF_MACHINE_NAME = "machine_name"
CONF_MODEL_NAME = "model_name"

DEFAULT_PORT = 1774

DEFAULT_NAME = "Espresso Machine"

TEMP_KEY = "temp"

SUPPORTED = "supported"
MODELS = [MODEL_GS3_AV, MODEL_GS3_MP, MODEL_LM]

"""List of attributes for each entity based on model."""
ATTR_MAP_MAIN_GS3_AV = [
    DATE_RECEIVED,
    UPDATE_AVAILABLE,
    DOSE_K1,
    DOSE_K2,
    DOSE_K3,
    DOSE_K4,
    DOSE_K5,
    DOSE_TEA,
]

ATTR_MAP_MAIN_GS3_MP_LM = [
    DATE_RECEIVED,
    UPDATE_AVAILABLE,
]

ATTR_MAP_PREBREW_GS3_AV = [
    DATE_RECEIVED,
    PREBREWING_TON_K1,
    PREBREWING_TON_K2,
    PREBREWING_TON_K3,
    PREBREWING_TON_K4,
    PREBREWING_TOFF_K1,
    PREBREWING_TOFF_K2,
    PREBREWING_TOFF_K3,
    PREBREWING_TOFF_K4,
]

ATTR_MAP_PREBREW_LM = [
    DATE_RECEIVED,
    PREBREWING_TON_K1,
    PREBREWING_TOFF_K1,
]

ATTR_MAP_COFFEE_TEMP = [
    DATE_RECEIVED,
    TSET_COFFEE,
]

ATTR_MAP_STEAM_TEMP = {
    DATE_RECEIVED,
    TSET_STEAM,
}

ATTR_MAP_AUTO_ON_OFF = [
    DATE_RECEIVED,
    SUN_AUTO,
    SUN_ON,
    SUN_OFF,
    MON_AUTO,
    MON_ON,
    MON_OFF,
    TUE_AUTO,
    TUE_ON,
    TUE_OFF,
    WED_AUTO,
    WED_ON,
    WED_OFF,
    THU_AUTO,
    THU_ON,
    THU_OFF,
    FRI_AUTO,
    FRI_ON,
    FRI_OFF,
    SAT_AUTO,
    SAT_ON,
    SAT_OFF,
]

ATTR_MAP_DRINK_STATS_GS3_AV = [
    DATE_RECEIVED,
    DRINKS_K1,
    DRINKS_K2,
    DRINKS_K3,
    DRINKS_K4,
    CONTINUOUS,
    HOT_WATER,
    DRINK_MYSTERY,
    TOTAL_COFFEE,
    TOTAL_DRINKS,
    HOT_WATER_2,
    DRINKS_TEA,
]

ATTR_MAP_DRINK_STATS_GS3_MP_LM = [
    DATE_RECEIVED,
    DRINKS_K1,
    CONTINUOUS,
    HOT_WATER,
    DRINK_MYSTERY,
    TOTAL_COFFEE,
    TOTAL_DRINKS,
    HOT_WATER_2,
    DRINKS_TEA,
]

DAYS = [SUN_AUTO, MON_AUTO, TUE_AUTO, WED_AUTO, THU_AUTO, FRI_AUTO, SAT_AUTO]

ENTITY_TAG = "tag"
ENTITY_NAME = "name"
ENTITY_MAP = "map"
ENTITY_TYPE = "type"
ENTITY_ICON = "icon"
ENTITY_FUNC = "func"
ENTITY_CLASS = "class"
ENTITY_UNITS = "units"

FUNC_BASE = "self._lm."

"""Service call names."""
SERVICE_SET_COFFEE_TEMP = "set_coffee_temp"
SERVICE_SET_STEAM_TEMP = "set_steam_temp"
SERVICE_ENABLE_AUTO_ON_OFF = "enable_auto_on_off"
SERVICE_DISABLE_AUTO_ON_OFF = "disable_auto_on_off"
SERVICE_SET_AUTO_ON_OFF_HOURS = "set_auto_on_off_hours"
SERVICE_SET_DOSE = "set_dose"
SERVICE_SET_DOSE_TEA = "set_dose_tea"
SERVICE_SET_PREBREW_TIMES = "set_prebrew_times"

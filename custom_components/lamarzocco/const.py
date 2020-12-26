"""Constants for the La Marzocco integration."""

from lmdirect.msgs import *

DOMAIN = "lamarzocco"

CONF_SERIAL_NUMBER = "serial_number"
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"

DEFAULT_NAME = "Espresso Machine"

ATTRIBUTION = "Data from La Marzocco"

COMMAND_ON = {"status": "ON"}
COMMAND_STANDBY = {"status": "STANDBY"}

TEMP_KEYS = ["TSET", "TEMP"]

ATTR_STATUS_MAP_MAIN = {
    RECEIVED: "date_received",
    DOSE_K1: "dose_k1",
    DOSE_K2: "dose_k2",
    DOSE_K3: "dose_k3",
    DOSE_K4: "dose_k4",
    DOSE_K5: "dose_k5",
    DOSE_TEA: "dose_tea",
}

ATTR_STATUS_MAP_PREBREW = {
    RECEIVED: "date_received",
    TON_PREBREWING_K1: "prebrewing_ton_k1",
    TON_PREBREWING_K2: "prebrewing_ton_k2",
    TON_PREBREWING_K3: "prebrewing_ton_k3",
    TON_PREBREWING_K4: "prebrewing_ton_k4",
    TOFF_PREBREWING_K1: "prebrewing_toff_k1",
    TOFF_PREBREWING_K2: "prebrewing_toff_k2",
    TOFF_PREBREWING_K3: "prebrewing_toff_k3",
    TOFF_PREBREWING_K4: "prebrewing_toff_k4",
}

ATTR_STATUS_MAP_COFFEE_TEMP = {
    RECEIVED: "date_received",
    TSET_COFFEE: "coffee_temp_setting",
}

ATTR_STATUS_MAP_STEAM_TEMP = {
    RECEIVED: "date_received",
    TSET_STEAM: "steam_temp_setting",
}

ATTR_STATUS_MAP_AUTO_ON_OFF = {
    RECEIVED: "date_received",
    SUN_AUTO: "sun",
    SUN_ON: "sun_on",
    SUN_OFF: "sun_off",
    MON_AUTO: "mon",
    MON_ON: "mon_on",
    MON_OFF: "mon_off",
    TUE_AUTO: "tue",
    TUE_ON: "tue_on",
    TUE_OFF: "tue_off",
    WED_AUTO: "wed",
    WED_ON: "wed_on",
    WED_OFF: "wed_off",
    THU_AUTO: "thu",
    THU_ON: "thu_on",
    THU_OFF: "thu_off",
    FRI_AUTO: "fri",
    FRI_ON: "fri_on",
    FRI_OFF: "fri_off",
    SAT_AUTO: "sat",
    SAT_ON: "sat_on",
    SAT_OFF: "sat_off",
}

DAYS = [SUN_AUTO, MON_AUTO, TUE_AUTO, WED_AUTO, THU_AUTO, FRI_AUTO, SAT_AUTO]

ENTITY_TAG = "tag"
ENTITY_NAME = "name"
ENTITY_MAP = "map"
ENTITY_TYPE = "type"
ENTITY_ICON = "icon"
ENTITY_FUNC = "func"

FUNC_BASE = "self._lm."

# Services
SERVICE_SET_COFFEE_TEMP = "set_coffee_temp"
SERVICE_SET_STEAM_TEMP = "set_steam_temp"
SERVICE_ENABLE_AUTO_ON_OFF = "enable_auto_on_off"
SERVICE_DISABLE_AUTO_ON_OFF = "disable_auto_on_off"
SERVICE_SET_AUTO_ON_OFF_HOURS = "set_auto_on_off_hours"
SERVICE_SET_DOSE = "set_dose"
SERVICE_SET_DOSE_TEA = "set_dose_tea"
SERVICE_SET_PREBREW_TIMES = "set_prebrew_times"
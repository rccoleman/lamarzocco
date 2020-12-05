"""Constants for the La Marzocco integration."""

DOMAIN = "lamarzocco"

CONF_SERIAL_NUMBER = "serial_number"
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"

DEFAULT_NAME = "Espresso Machine"

ATTRIBUTION = "Data from La Marzocco"

DATA_TAG = "data"

DATA_ENABLE_PREBREWING = "ENABLE_PREBREWING"
DATA_STBY_TIMER = "STBY_TIMER"
DATA_TON_PREBREWING_K1 = "TON_PREBREWING_K1"
DATA_TON_PREBREWING_K2 = "TON_PREBREWING_K2"
DATA_TON_PREBREWING_K3 = "TON_PREBREWING_K3"
DATA_TON_PREBREWING_K4 = "TON_PREBREWING_K4"
DATA_TOFF_PREBREWING_K1 = "TOFF_PREBREWING_K1"
DATA_TOFF_PREBREWING_K2 = "TOFF_PREBREWING_K2"
DATA_TOFF_PREBREWING_K3 = "TOFF_PREBREWING_K3"
DATA_TOFF_PREBREWING_K4 = "TOFF_PREBREWING_K4"
DATA_TSET_STEAM = "TSET_STEAM"
DATA_TSET_COFFEE = "TSET_COFFEE"
DATA_DOSE_K1 = "DOSE_K1"
DATA_DOSE_K2 = "DOSE_K2"
DATA_DOSE_K3 = "DOSE_K3"
DATA_DOSE_K4 = "DOSE_K4"
DATA_DOSE_K5 = "DOSE_K5"
DATA_DOSE_TEA = "DOSE_TEA"

STATUS_ON = "ON"
STATUS_STANDBY = "STANDBY"

STATUS_MACHINE_STATUS = "MACHINE_STATUS"
STATUS_TEMP_STEAM = "TEMP_STEAM"
STATUS_TEMP_COFFEE = "TEMP_COFFEE"

RECEIVED_DATETIME = "received"

COMMAND_ON = {"status": "ON"}
COMMAND_STANDBY = {"status": "STANDBY"}

TEMP_KEYS = ["TSET", "TEMP"]

GW_URL = "https://gw.lamarzocco.io/v1/home/machines"
TOKEN_URL = "https://cms.lamarzocco.io/oauth/v2/token"

ATTR_DATA_MAP = {
    RECEIVED_DATETIME: "data_last_changed",
    DATA_ENABLE_PREBREWING: "prebrewing_enabled",
    DATA_STBY_TIMER: "standby_timer",
    DATA_TON_PREBREWING_K1: "prebrewing_ton_k1",
    DATA_TON_PREBREWING_K2: "prebrewing_ton_k2",
    DATA_TON_PREBREWING_K3: "prebrewing_ton_k3",
    DATA_TON_PREBREWING_K4: "prebrewing_ton_k4",
    DATA_TOFF_PREBREWING_K1: "prebrewing_toff_k1",
    DATA_TOFF_PREBREWING_K2: "prebrewing_toff_k2",
    DATA_TOFF_PREBREWING_K3: "prebrewing_toff_k3",
    DATA_TOFF_PREBREWING_K4: "prebrewing_toff_k4",
    DATA_TSET_STEAM: "steam_temperature",
    DATA_TSET_COFFEE: "coffee_temperature",
    DATA_DOSE_K1: "dose_k1",
    DATA_DOSE_K2: "dose_k2",
    DATA_DOSE_K3: "dose_k3",
    DATA_DOSE_K4: "dose_k4",
    DATA_DOSE_K5: "dose_k5",
    DATA_DOSE_TEA: "dose_tea",
}

ATTR_STATUS_MAP = {
    RECEIVED_DATETIME: "status_last_changed",
    STATUS_TEMP_STEAM: "steam_temp",
    STATUS_TEMP_COFFEE: "coffee_temp",
}

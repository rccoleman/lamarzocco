"""Constants for the La Marzocco integration."""

DOMAIN = "lamarzocco"

CONF_SERIAL_NUMBER = "serial_number"
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"

DEFAULT_NAME = "lamarzocco"

ATTR_ENABLE_PREBREWING = "ENABLE_PREBREWING"
ATTR_STBY_TIMER = "STBY_TIMER"
ATTR_TON_PREBREWING_K1 = "TON_PREBREWING_K1"
ATTR_TON_PREBREWING_K2 = "TON_PREBREWING_K2"
ATTR_TON_PREBREWING_K3 = "TON_PREBREWING_K3"
ATTR_TON_PREBREWING_K4 = "TON_PREBREWING_K4"
ATTR_TOFF_PREBREWING_K1 = "TOFF_PREBREWING_K1"
ATTR_TOFF_PREBREWING_K2 = "TOFF_PREBREWING_K2"
ATTR_TOFF_PREBREWING_K3 = "TOFF_PREBREWING_K3"
ATTR_TOFF_PREBREWING_K4 = "TOFF_PREBREWING_K4"
ATTR_TSET_STEAM = "TSET_STEAM"
ATTR_TSET_COFFEE = "TSET_COFFEE"
ATTR_DOSE_K1 = "DOSE_K1"
ATTR_DOSE_K2 = "DOSE_K2"
ATTR_DOSE_K3 = "DOSE_K3"
ATTR_DOSE_K4 = "DOSE_K4"
ATTR_DOSE_K5 = "DOSE_K5"
ATTR_DOSE_TEA = "DOSE_TEA"
STATE_STATUS = "status"
DATA_TAG = "data"

ATTR_MAP = {
    STATE_STATUS: "Status",
    ATTR_ENABLE_PREBREWING: "Prebrewing Enabled",
    ATTR_STBY_TIMER: "Standby Timer",
    ATTR_TON_PREBREWING_K1: "Prebrewing Time On (Key 1)",
    ATTR_TON_PREBREWING_K2: "Prebrewing Time On (Key 2)",
    ATTR_TON_PREBREWING_K3: "Prebrewing Time On (Key 3)",
    ATTR_TON_PREBREWING_K4: "Prebrewing Time On (Key 4)",
    ATTR_TOFF_PREBREWING_K1: "Prebrewing Time Off (Key 1)",
    ATTR_TOFF_PREBREWING_K2: "Prebrewing Time Off (Key 2)",
    ATTR_TOFF_PREBREWING_K3: "Prebrewing Time Off (Key 3)",
    ATTR_TOFF_PREBREWING_K4: "Prebrewing Time Off (Key 4)",
    ATTR_TSET_STEAM: "Steam Temperature",
    ATTR_TSET_COFFEE: "Coffee Temperature",
    ATTR_DOSE_K1: "Dose (Key 1)",
    ATTR_DOSE_K2: "Dose (Key 2)",
    ATTR_DOSE_K3: "Dose (Key 3)",
    ATTR_DOSE_K4: "Dose (Key 4)",
    ATTR_DOSE_K5: "Dose (Key 5)",
    ATTR_DOSE_TEA: "Dose (Tea)",
}

test_data = {
    "status": "true",
    "data": {
        "received": "2020-01-01T20:00:00.000Z",
        "ENABLE_PREBREWING": "true",
        "STBY_TIMER": 30,
        "TON_PREBREWING_K1": 1.1,
        "TON_PREBREWING_K2": 0,
        "TON_PREBREWING_K3": 0,
        "TON_PREBREWING_K4": 0,
        "TOFF_PREBREWING_K1": 2.2,
        "TOFF_PREBREWING_K2": 0,
        "TOFF_PREBREWING_K3": 0,
        "TOFF_PREBREWING_K4": 0,
        "TSET_STEAM": 255,
        "TSET_COFFEE": 203,
        "DOSE_K1": 6,
        "DOSE_K2": 12,
        "DOSE_K3": 24,
        "DOSE_K4": 48,
        "DOSE_K5": 96,
        "DOSE_TEA": 128,
    },
}


data = test_data.get("data")

output = {}
for tag in data:
    if tag in ATTR_MAP.keys():
        output[ATTR_MAP[tag]] = data[tag]

print(output)

"""
        enable_prebrewing = self.enable_prebrewing
        if enable_prebrewing is not None:
            data[ATTR_ENABLE_PREBREWING] = enable_prebrewing

        standby_timer = self.standby_timer
        if standby_timer is not None:
            data[ATTR_STBY_TIMER] = standby_timer

        time_on_prebrewing_k1 = self.time_on_prebrewing_k1
        if time_on_prebrewing_k1 is not None:
            data[ATTR_TON_PREBREWING_K1] = time_on_prebrewing_k1

        time_on_prebrewing_k2 = self.time_on_prebrewing_k2
        if time_on_prebrewing_k2 is not None:
            data[ATTR_TON_PREBREWING_K2] = time_on_prebrewing_k2

        time_on_prebrewing_k3 = self.time_on_prebrewing_k3
        if time_on_prebrewing_k3 is not None:
            data[ATTR_TON_PREBREWING_K3] = time_on_prebrewing_k3

        time_on_prebrewing_k4 = self.time_on_prebrewing_k4
        if time_on_prebrewing_k4 is not None:
            data[ATTR_TON_PREBREWING_K4] = time_on_prebrewing_k4

        time_off_prebrewing_k1 = self.time_off_prebrewing_k1
        if time_off_prebrewing_k1 is not None:
            data[ATTR_TOFF_PREBREWING_K1] = time_off_prebrewing_k1

        time_off_prebrewing_k2 = self.time_off_prebrewing_k2
        if time_off_prebrewing_k2 is not None:
            data[ATTR_TOFF_PREBREWING_K2] = time_off_prebrewing_k2

        time_off_prebrewing_k3 = self.time_off_prebrewing_k3
        if time_off_prebrewing_k3 is not None:
            data[ATTR_TOFF_PREBREWING_K3] = time_off_prebrewing_k3

        time_off_prebrewing_k4 = self.time_off_prebrewing_k4
        if time_on_prebrewing_k4 is not None:
            data[ATTR_TOFF_PREBREWING_K4] = time_off_prebrewing_k4

        steam_temp = self.steam_temp
        if steam_temp is not None:
            data[ATTR_TSET_STEAM] = steam_temp

        coffee_temp = self.coffee_temp
        if coffee_temp is not None:
            data[ATTR_TSET_COFFEE] = coffee_temp

        dose_k1 = self.dose_k1
        if dose_k1 is not None:
            data[ATTR_DOSE_K1] = dose_k1

        dose_k2 = self.dose_k2
        if dose_k2 is not None:
            data[ATTR_DOSE_K2] = dose_k2

        dose_k3 = self.dose_k3
        if dose_k3 is not None:
            data[ATTR_DOSE_K3] = dose_k3

        dose_k4 = self.dose_k4
        if dose_k4 is not None:
            data[ATTR_DOSE_K4] = dose_k4

        dose_k5 = self.dose_k5
        if dose_k5 is not None:
            data[ATTR_DOSE_K5] = dose_k5

        dose_tea = self.dose_tea
        if dose_tea is not None:
            data[ATTR_DOSE_TEA] = dose_tea
"""


@property
def enable_prebrewing(self):
    """Return the prebrewing setting."""
    return self.coordinator.data.current_data.get(ATTR_ENABLE_PREBREWING)


@property
def standby_timer(self):
    """Return the standby timer."""
    return self.coordinator.data.current_data.get(ATTR_STBY_TIMER)


@property
def time_on_prebrewing_k1(self):
    """Return the time on for key 1 prebrewing."""
    return self.coordinator.data.current_data.get(ATTR_TON_PREBREWING_K1)


@property
def time_on_prebrewing_k2(self):
    """Return the time on for key 2 prebrewing."""
    return self.coordinator.data.current_data.get(ATTR_TON_PREBREWING_K2)


@property
def time_on_prebrewing_k3(self):
    """Return the time on for key 3 prebrewing."""
    return self.coordinator.data.current_data.get(ATTR_TON_PREBREWING_K3)


@property
def time_on_prebrewing_k4(self):
    """Return the time on for key 4 prebrewing."""
    return self.coordinator.data.current_data.get(ATTR_TON_PREBREWING_K4)


@property
def time_off_prebrewing_k1(self):
    """Return the time off for key 1 prebrewing."""
    return self.coordinator.data.current_data.get(ATTR_TOFF_PREBREWING_K1)


@property
def time_off_prebrewing_k2(self):
    """Return the time off for key 2 prebrewing."""
    return self.coordinator.data.current_data.get(ATTR_TOFF_PREBREWING_K2)


@property
def time_off_prebrewing_k3(self):
    """Return the time off for key 3 prebrewing."""
    return self.coordinator.data.current_data.get(ATTR_TOFF_PREBREWING_K3)


@property
def time_off_prebrewing_k4(self):
    """Return the time off for key 4 prebrewing."""
    return self.coordinator.data.current_data.get(ATTR_TOFF_PREBREWING_K4)


@property
def steam_temp(self):
    """Return the steam temp."""
    return self.coordinator.data.current_data.get(ATTR_TSET_STEAM)


@property
def coffee_temp(self):
    """Return the coffee temp."""
    return self.coordinator.data.current_data.get(ATTR_TSET_COFFEE)


@property
def dose_k1(self):
    """Return the key 1 dose."""
    return self.coordinator.data.current_data.get(ATTR_DOSE_K1)


@property
def dose_k2(self):
    """Return the key 2 dose."""
    return self.coordinator.data.current_data.get(ATTR_DOSE_K2)


@property
def dose_k3(self):
    """Return the key 3 dose."""
    return self.coordinator.data.current_data.get(ATTR_DOSE_K3)


@property
def dose_k4(self):
    """Return the key 4 dose."""
    return self.coordinator.data.current_data.get(ATTR_DOSE_K4)


@property
def dose_k5(self):
    """Return the key 5 dose."""
    return self.coordinator.data.current_data.get(ATTR_DOSE_K5)


@property
def dose_tea(self):
    """Return the tea dose."""
    return self.coordinator.data.current_data.get(ATTR_DOSE_TEA)

from typing import Dict
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.core import DOMAIN, callback
import logging
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.dt import as_local, parse_datetime
from .const import (
    ATTR_DATA_MAP,
    ATTR_STATUS_MAP,
    DOMAIN,
    CONF_SERIAL_NUMBER,
    DEFAULT_NAME,
    RECEIVED_DATETIME,
    STATUS_MACHINE_STATUS,
    STATUS_ON,
    TEMP_KEYS,
    ATTRIBUTION,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add a switch entity from a config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [LaMarzoccoEntity(coordinator, config_entry.data, hass.config.units.is_metric)]
    )


class LaMarzoccoEntity(CoordinatorEntity, SwitchEntity, RestoreEntity):
    """Implementation of a La Marzocco integration"""

    def __init__(self, coordinator, config, is_metric):
        """Initialise the platform with a data instance and site."""
        super().__init__(coordinator)
        self._config = config
        self._temp_state = None
        self._is_on = (
            coordinator.data.current_status[STATUS_MACHINE_STATUS] == STATUS_ON
        )
        self.is_metric = is_metric

    async def async_turn_on(self, **kwargs) -> None:
        """Turn device on."""
        await self.coordinator.data.power(True)
        self._temp_state = True
        self.async_schedule_update_ha_state(force_refresh=False)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn device off."""
        await self.coordinator.data.power(False)
        self._temp_state = False
        self.async_schedule_update_ha_state(force_refresh=False)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Respond to a DataUpdateCoordinator update."""
        self.update_from_latest_data()
        super()._handle_coordinator_update()

    @callback
    def update_from_latest_data(self) -> None:
        """Update the state."""
        status = self.coordinator.data.current_status[STATUS_MACHINE_STATUS]
        self._is_on = status == STATUS_ON
        if self._temp_state == self._is_on:
            self._temp_state = None

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._config[CONF_SERIAL_NUMBER]}"

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        return self._temp_state if self._temp_state is not None else self._is_on

    @property
    def assumed_state(self) -> bool:
        """Return true if unable to access real state of entity."""
        return False

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{DEFAULT_NAME}"

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return True

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def state_attributes(self):
        """Return the state attributes."""
        output = self.generate_attrs(
            self.coordinator.data.current_status, ATTR_STATUS_MAP
        )

        output.update(
            self.generate_attrs(self.coordinator.data.current_data, ATTR_DATA_MAP)
        )

        return output

    def generate_attrs(self, data, map) -> Dict:
        output = {}

        current_data = self.coordinator.data.current_data
        for key in data:
            if key in map.keys():
                value = data[key]

                """Convert boolean values to strings to improve display in Lovelace"""
                if isinstance(value, bool):
                    value = str(value)

                """Convert temps to fahrenheit if needed"""
                if not self.is_metric and any(val in key for val in TEMP_KEYS):
                    value = round((value * 9 / 5) + 32, 1)

                """Convert dates to datetime"""
                if RECEIVED_DATETIME in key:
                    value = parse_datetime(value)

                output[map[key]] = value

        return output

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend, if any."""
        return "mdi:coffee-maker"

    @property
    def device_info(self):
        """Device info."""
        return {
            "identifiers": {(DOMAIN,)},
            "name": "La Marzocco",
            "manufacturer": "La Marzocco",
            "model": "GS/3",
            "default_name": "lamarzocco",
            "entry_type": "None",
        }

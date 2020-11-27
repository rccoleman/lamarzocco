from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA_BASE
from homeassistant.core import DOMAIN
import voluptuous as vol
import logging
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, CONF_SERIAL_NUMBER, DEFAULT_NAME, ATTR_MAP
from homeassistant.const import CONF_CLIENT_ID, CONF_NAME, CONF_USERNAME, CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Data from La Marzocco"

PLATFORM_SCHEMA = PLATFORM_SCHEMA_BASE.extend(
    {
        vol.Required(CONF_SERIAL_NUMBER): cv.string,
        vol.Required(CONF_CLIENT_ID): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add a switch entity from a config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            LaMarzocco(coordinator, config_entry.data),
        ]
    )


class LaMarzocco(CoordinatorEntity, SwitchEntity, RestoreEntity):
    """Implementation of a La Marzocco integration"""

    def __init__(self, coordinator, config):
        """Initialise the platform with a data instance and site."""
        super().__init__(coordinator)
        self._config = config

    def turn_on(self, **kwargs) -> None:
        """Turn device on."""
        self.coordinator.data.new_status = True

        # Update the data
        self.schedule_update_ha_state(True)

    def turn_off(self, **kwargs) -> None:
        """Turn device off."""
        self.coordinator.data.new_status = False

        # Update the data
        self.schedule_update_ha_state(True)

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._config[CONF_SERIAL_NUMBER]}"

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        return self.coordinator.data.new_status

    @property
    def assumed_state(self) -> bool:
        """Return true if unable to access real state of entity."""
        return False

    @property
    def name(self):
        """Return the name of the sensor."""
        name = self._config.get(CONF_NAME)

        if name is not None:
            return name

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
        output = {}

        current_data = self.coordinator.data.current_data
        for tag in current_data:
            if tag in ATTR_MAP.keys():
                output[ATTR_MAP[tag]] = current_data[tag]

        return output

    @property
    def device_info(self):
        """Device info."""
        return {
            "identifiers": {(DOMAIN,)},
            "manufacturer": "La Marzocco",
            "model": "Forecast",
            "default_name": "lamarzocco",
            "entry_type": "service",
        }

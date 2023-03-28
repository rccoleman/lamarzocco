"""Interface with the lmdirect library."""

import asyncio
import logging

from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from lmdirect.connection import AuthFail as LMAuthFail, ConnectionFail as LMConnectionFail
from lmdirect.msgs import FIRMWARE_VER, POWER, UPDATE_AVAILABLE

from .const import DOMAIN, MODEL_GS3_AV, MODELS, POLLING_INTERVAL
from .interface import LMInterface

_LOGGER = logging.getLogger(__name__)


class LaMarzocco(LMInterface):
    """Keep data for La Marzocco entities."""

    def __init__(self):
        """Initialise the LaMarzocco entity data."""
        self._current_status = {}
        self._polling_task = None
        self._device_version = None
        self._poll_reaper_task = None

        """Start with the machine in standby if we haven't received accurate data yet"""
        self._current_status[POWER] = 0

    @classmethod
    async def create(cls, hass, config_entry=None, data=None):
        self = cls()
        self._config_entry = config_entry
        self._hass = hass
        await super().create(config_entry.data if config_entry else data)
        await super().init_data(hass)

    @property
    def model_name(self):
        """Return the model name of the normalized espresso machine."""
        model_name = super().model_name
        if model_name not in MODELS:
            _LOGGER.error(
                f"Unsupported model, falling back to all entities and services: {model_name}"
            )
        return model_name if model_name in MODELS else MODEL_GS3_AV

    @property
    def true_model_name(self):
        """Return the model name from the cloud, even if it's not one we know about.  Used for display only."""
        model_name = super().model_name
        return model_name if model_name in MODELS else model_name + " (Unknown)"

    async def poll_reaper(self):
        _LOGGER.debug("Starting polling reaper")
        try:
            await asyncio.gather(self._polling_task)
        except Exception as err:
            _LOGGER.error(f"Exception in polling task: {err}")

        _LOGGER.debug("Finished reaping polling task")

    async def close(self):
        """Tell the read and polling loops to stop."""
        self._run = False

        if self._polling_task:
            self._polling_task.cancel()

        await super().close()

    @callback
    def update_callback(self, **kwargs):
        """Callback for when new data is available."""
        self._current_status.update(kwargs.get("current_status"))
        self._current_status[UPDATE_AVAILABLE] = self._update_available

        if not self._device_version and FIRMWARE_VER in self._current_status:
            self._hass.loop.create_task(
                self._update_device_info(self._current_status[FIRMWARE_VER])
            )
            self._device_version = self._current_status[FIRMWARE_VER]

    async def _update_device_info(self, firmware_version):
        """Update the device info with the firmware version."""

        device_registry = dr.async_get(self._hass)
        device_entry = device_registry.async_get_device(
            {(DOMAIN, self.serial_number)}, set()
        )
        device_registry.async_update_device(
            device_entry.id, sw_version=firmware_version
        )

    async def connect(self):
        """Connect to the machine."""

        try:
            return await super().connect()
        except LMAuthFail:
            raise AuthFail
        except LMConnectionFail:
            raise ConnectionFail

    async def fetch_data(self):
        """Loop that periodically polls the machine for new data."""
        while self._run:
            _LOGGER.debug("Fetching data")
            try:
                """Request latest status."""
                await self.request_status()
            except Exception as err:
                _LOGGER.error(f"Caught exception: {err}")
            await asyncio.sleep(POLLING_INTERVAL)
        _LOGGER.error(f"Exiting polling task: {self._run}")


class AuthFail(Exception):
    """The server rejected the authentication."""


class ConnectionFail(Exception):
    """Could not connect to the server."""

import asyncio
import errno
import logging
from datetime import datetime
from socket import error as SocketError

from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from lmdirect import LMDirect
from lmdirect.msgs import FIRMWARE_VER, POWER, DATE_RECEIVED, UPDATE_AVAILABLE

from .const import MODEL_GS3_AV, POLLING_INTERVAL, DOMAIN, MODELS

_LOGGER = logging.getLogger(__name__)


class LaMarzocco(LMDirect):
    """Keep data for La Marzocco entities."""

    def __init__(self, hass, config_entry=None, data=None):
        """Initialise the LaMarzocco entity data."""
        self._hass = hass
        self._current_status = {}
        self._polling_task = None
        self._config_entry = config_entry
        self._device_version = None
        self._poll_reaper_task = None

        """Start with the machine in standby if we haven't received accurate data yet"""
        self._current_status[POWER] = 0

        super().__init__(config_entry.data if config_entry else data)

    async def init_data(self, hass):
        """Register the callback to receive updates"""
        self.register_callback(self.update_callback)

        self._run = True

        """Start polling for status"""
        self._polling_task = hass.loop.create_task(self.fetch_data())

        """Reap the results and any any exceptions"""
        self._poll_reaper_task = hass.loop.create_task(
            self.poll_reaper(), name="Poll Reaper"
        )

    @property
    def model_name(self):
        model_name = super().model_name
        if model_name not in MODELS:
            _LOGGER.error(
                f"Unsupported model, falling back to all entities and services: {super().model_name}"
            )
        return model_name if model_name in MODELS else MODEL_GS3_AV

    @property
    def true_model_name(self):
        model_name = super().model_name
        return model_name if model_name in MODELS else model_name + " (Unknown)"

    async def poll_reaper(self):
        _LOGGER.debug("Starting poll reaper")
        try:
            await asyncio.gather(self._polling_task)
        except Exception as err:
            _LOGGER.error(f"Exception in polling task: {err}")

        _LOGGER.debug("Finished reaping polling task")

    async def close(self):
        """Stop the reeive and send loops"""
        self._run = False

        if self._polling_task:
            self._polling_task.cancel()

        await super().close()

    @callback
    def update_callback(self, **kwargs):
        """Callback when new data is available"""
        self._current_status.update(kwargs.get("current_status"))
        self._current_status[DATE_RECEIVED] = datetime.now().replace(microsecond=0)
        self._current_status[UPDATE_AVAILABLE] = self._update_available

        if not self._device_version and FIRMWARE_VER in self._current_status:
            self._hass.loop.create_task(
                self._update_device_info(self._current_status[FIRMWARE_VER])
            )
            self._device_version = self._current_status[FIRMWARE_VER]

    async def _update_device_info(self, firmware_version):
        """Update the device with the firmware version"""

        _LOGGER.debug(f"Updating firmware version to {firmware_version}")
        device_registry = await dr.async_get_registry(self._hass)
        device_entry = device_registry.async_get_device(
            {(DOMAIN, self.serial_number)}, set()
        )
        device_registry.async_update_device(
            device_entry.id, sw_version=firmware_version
        )

    async def fetch_data(self):
        while self._run:
            """Fetch data from API - (current weather and forecast)."""
            _LOGGER.debug("Fetching data")
            try:
                """Request latest status"""
                await self.request_status()
            except SocketError as e:
                if e.errno != errno.ECONNRESET:
                    _LOGGER.error("Connection error: {}".format(e))
            await asyncio.sleep(POLLING_INTERVAL)
        _LOGGER.error(f"Exiting polling task: {self._run}")

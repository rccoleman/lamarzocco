import asyncio
import logging
from datetime import timedelta

from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (DataUpdateCoordinator,
                                                      UpdateFailed)

from lmcloud.exceptions import AuthFail, RequestNotSuccessful

SCAN_INTERVAL = timedelta(seconds=30)
UPDATE_DELAY = 2

_LOGGER = logging.getLogger(__name__)


class LmApiCoordinator(DataUpdateCoordinator):
    """Class to handle fetching data from the La Marzocco API centrally"""

    @property
    def lm(self):
        return self._lm

    def __init__(self, hass, lm):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="La Marzocco API coordinator",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=SCAN_INTERVAL
        )
        self._lm = lm
        self._initialized = False
        # TODO: Get value from options flow
        self._use_websocket = False

    async def _async_update_data(self):
        try:
            _LOGGER.debug("Update coordinator: Updating data")
            if not self._initialized:
                await self._lm.hass_init()
                self._initialized = True
                if self._use_websocket:
                    self.hass.async_create_task(
                        self._lm._lm_local_api.websocket_connect(self._async_update_status)
                    )
            # wait for a bit before getting a new state, to let the machine settle in to any state changes
            await asyncio.sleep(UPDATE_DELAY)
            await self._lm.update_local_machine_status()
        except AuthFail as ex:
            msg = "Authentication failed. \
                            Maybe one of your credential details was invalid or you changed your password."
            _LOGGER.error(msg)
            raise ConfigEntryAuthFailed(msg) from ex
        except (RequestNotSuccessful, Exception) as ex:
            _LOGGER.error(ex)
            raise UpdateFailed("Querying API failed. Error: %s", ex)
        _LOGGER.debug("Current status: %s", str(self._lm.current_status))
        return self._lm

    @callback
    def _async_update_status(self, status: dict):
        """ callback which gets called whenever the websocket receives data """
        # TODO: check if we need to set more data here
        self.async_set_updated_data(status)

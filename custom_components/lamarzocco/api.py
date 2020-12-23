import errno
import logging
from datetime import datetime
from socket import error as SocketError
from datetime import datetime
from homeassistant.core import callback

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from lmdirect import LMDirect
from lmdirect.const import *

from .const import *

_LOGGER = logging.getLogger(__name__)


class LaMarzocco(LMDirect):
    """Keep data for La Marzocco entities."""

    def __init__(self, hass, config):
        """Initialise the weather entity data."""
        self.hass = hass
        self._current_status = {}

        """Start with the machine in standby if we haven't received accurate data yet"""
        self._is_on = False

        self._current_status[STATUS_MACHINE_STATUS] = 0

        super().__init__(
            {
                IP_ADDR: config[CONF_HOST],
                CLIENT_ID: config[CONF_CLIENT_ID],
                CLIENT_SECRET: config[CONF_CLIENT_SECRET],
                USERNAME: config[CONF_USERNAME],
                PASSWORD: config[CONF_PASSWORD],
            }
        )

    async def init_data(self):
        """Register the callback to receive updates"""
        self.register_callback(self.update_callback)

    @callback
    def update_callback(self, status, state):
        _LOGGER.debug("Data updated: {}, state={}".format(status, state))
        self._current_status.update(status)
        self._current_status[STATUS_RECEIVED] = datetime.now()
        self._is_on = True if self._current_status[STATUS_MACHINE_STATUS] else False
        _LOGGER.debug("update_callback for API called")

    async def fetch_data(self):
        """Fetch data from API - (current weather and forecast)."""
        _LOGGER.debug("Fetching data")
        try:
            """Request latest status"""
            await self.request_status()
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise
            else:
                _LOGGER.debug("Connection error: {}".format(e))

        return self

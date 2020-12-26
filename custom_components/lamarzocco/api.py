import asyncio
import errno
import logging
from datetime import datetime
from socket import error as SocketError

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
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
        self._run = True

        """Start with the machine in standby if we haven't received accurate data yet"""
        self._is_on = False

        self._current_status[POWER] = 0

        super().__init__(
            {
                IP_ADDR: config[CONF_HOST],
                CLIENT_ID: config[CONF_CLIENT_ID],
                CLIENT_SECRET: config[CONF_CLIENT_SECRET],
                USERNAME: config[CONF_USERNAME],
                PASSWORD: config[CONF_PASSWORD],
            }
        )

    async def init_data(self, hass):
        """Register the callback to receive updates"""
        self.register_callback(self.update_callback)

        """Connect to populate info"""
        await self.connect()

        """Start listening for status"""
        hass.loop.create_task(self.fetch_data())

    async def close(self):
        self._run = False
        super().close()

    @callback
    def update_callback(self, **kwargs):
        self._current_status.update(kwargs.get("current_status"))
        self._current_status[RECEIVED] = datetime.now().replace(microsecond=0)
        self._is_on = True if self._current_status[POWER] else False

    async def fetch_data(self):
        while self._run:
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
            await asyncio.sleep(20)

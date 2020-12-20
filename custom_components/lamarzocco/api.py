import errno
import logging
from socket import error as SocketError

import lmdirect.cmds as CMD
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from lmdirect import LMDirect
from lmdirect.const import *

from .const import CONF_CLIENT_ID, CONF_CLIENT_SECRET

_LOGGER = logging.getLogger(__name__)


class LaMarzocco:
    """Keep data for La Marzocco entities."""

    def __init__(self, hass, config):
        """Initialise the weather entity data."""
        self.hass = hass
        self._config = config
        self.lmdirect = None
        self._serial_number = None
        self._machine_name = None

    async def init_data(self):
        creds = {
            IP_ADDR: self._config[CONF_HOST],
            CLIENT_ID: self._config[CONF_CLIENT_ID],
            CLIENT_SECRET: self._config[CONF_CLIENT_SECRET],
            USERNAME: self._config[CONF_USERNAME],
            PASSWORD: self._config[CONF_PASSWORD],
        }
        self.lmdirect = LMDirect(creds)

    async def close(self):
        if self.lmdirect is not None:
            await self.lmdirect.close()

    async def fetch_data(self):
        """Fetch data from API - (current weather and forecast)."""
        _LOGGER.debug("Fetching data")
        try:
            """Request latest status"""
            await self.lmdirect.request_status()
            if any(x is None for x in [self._machine_name, self._serial_number]):
                self._machine_name = self.lmdirect.machine_name
                self._serial_number = self.lmdirect.serial_number
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise
            else:
                _LOGGER.debug("Connection error: {}".format(e))

        return self

    @property
    def serial_number(self):
        """Return serial number"""
        return self._serial_number

    @property
    def machine_name(self):
        """Return machine name"""
        return self._machine_name

    async def power(self, power):
        """Send power on or power off commands"""
        cmd = CMD.CMD_ON if power else CMD.CMD_OFF
        await self.lmdirect.send_cmd(cmd)

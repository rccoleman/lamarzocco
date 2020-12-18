import errno
import logging
from socket import error as SocketError

import lmdirect.cmds as CMD
from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.httpx_client import AsyncOAuth2Client
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from lmdirect import LMDirect

from .const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_SERIAL_NUMBER,
    CUSTOMER_URL,
    GW_URL,
    TOKEN_URL,
)

_LOGGER = logging.getLogger(__name__)


class LaMarzocco:
    """Keep data for La Marzocco entities."""

    def __init__(self, hass, config):
        """Initialise the weather entity data."""
        self.hass = hass
        self._config = config
        self.client = None
        serial_number = self._config[CONF_SERIAL_NUMBER]
        self.config_endpoint = f"{GW_URL}/{serial_number}/configuration"
        self.status_endpoint = f"{GW_URL}/{serial_number}/status"
        self.lmdirect = None

    async def init_data(self):
        """Machine data inialization"""
        client_id = self._config[CONF_CLIENT_ID]
        client_secret = self._config[CONF_CLIENT_SECRET]

        self.client = AsyncOAuth2Client(
            client_id=client_id,
            client_secret=client_secret,
            token_endpoint=TOKEN_URL,
        )

        headers = {"client_id": client_id, "client_secret": client_secret}

        try:
            await self.client.fetch_token(
                url=TOKEN_URL,
                username=self._config[CONF_USERNAME],
                password=self._config[CONF_PASSWORD],
                headers=headers,
            )
        except OAuthError:
            await self.close()
            raise AuthFail

        except Exception as err:
            print("Caught: {}, {}".format(type(err), err))
            await self.close()
            raise AuthFail

        cust_info = await self.client.get(CUSTOMER_URL)
        key = None
        if cust_info is not None:
            key = cust_info.json()["data"]["fleet"][0]["communicationKey"]
        self.lmdirect = LMDirect(key, self._config[CONF_HOST])

    async def close(self):
        if self.lmdirect is not None:
            await self.lmdirect.close()
        if self.client is not None:
            await self.client.aclose()

    async def fetch_data(self):
        """Fetch data from API - (current weather and forecast)."""
        _LOGGER.debug("Fetching data")
        try:
            """Request latest status"""
            await self.lmdirect.request_status()
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise
            else:
                _LOGGER.debug("Connection error: {}".format(e))

        return self

    async def power(self, power):
        """Send power on or power off commands"""
        cmd = CMD.CMD_ON if power else CMD.CMD_OFF
        await self.lmdirect.send_cmd(cmd)


class AuthFail(BaseException):
    """Error to indicate there is invalid auth."""

"""Test La Marzocco machine setup."""
import logging
from copy import deepcopy

import lmdirect
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.async_mock import patch
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lamarzocco.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_MACHINE_NAME,
    CONF_MODEL_NAME,
    CONF_SERIAL_NUMBER,
    DOMAIN,
)

ENTRY_ID = 1

_LOGGER = logging.getLogger(__name__)

DATA = {
    CONF_HOST: "1.2.3.4",
    CONF_CLIENT_ID: "aabbcc",
    CONF_CLIENT_SECRET: "bbccdd",
    CONF_USERNAME: "username",
    CONF_PASSWORD: "password",
    CONF_SERIAL_NUMBER: "aabbcc",
    CONF_MODEL_NAME: "GS3 AV",
    CONF_MACHINE_NAME: "bbbbb",
}


async def setup_lm_machine(hass):
    """Set up a test configuration."""

    await async_setup_component(hass, DOMAIN, {})

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=deepcopy(DATA),
        entry_id=ENTRY_ID,
    )

    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.entry_id in hass.data[DOMAIN]

    machine = hass.data[DOMAIN][config_entry.entry_id]
    assert machine is not None

    return machine


@patch.object(lmdirect.LMDirect, "_connect", autospec=True)
@patch.object(lmdirect.LMDirect, "_send_msg", autospec=True)
async def test_setup_lm_machine(
    mock_send_msg,
    mock_connect,
    hass,
):
    """Test set up and tear down."""
    machine = await setup_lm_machine(hass)
    assert machine == hass.data[DOMAIN][ENTRY_ID]

    config_entry = hass.config_entries.async_get_entry(ENTRY_ID)
    assert config_entry.data == DATA

    assert await hass.config_entries.async_unload(ENTRY_ID)
    assert not hass.data[DOMAIN]

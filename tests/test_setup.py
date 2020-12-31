"""Test La Marzocco machine"""
from copy import deepcopy

import pytest

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN

from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.setup import async_setup_component

from pytest_homeassistant_custom_component.async_mock import patch
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lamarzocco.const import (
    DOMAIN,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_SERIAL_NUMBER,
    CONF_MODEL_NAME,
    CONF_MACHINE_NAME,
)

DATA = {
    CONF_HOST: "1.2.3.4",
    CONF_CLIENT_ID: "aabbcc",
    CONF_CLIENT_SECRET: "bbccdd",
    CONF_USERNAME: "username",
    CONF_PASSWORD: "password",
    CONF_SERIAL_NUMBER: "aabbcc",
    CONF_MODEL_NAME: "aaaaa",
    CONF_MACHINE_NAME: "bbbbb",
}


async def setup_lm_machine(hass, config=DATA):
    await async_setup_component(hass, DOMAIN, {})

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=deepcopy(config),
        entry_id=1,
    )

    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.entry_id in hass.data[DOMAIN]

    machine = hass.data[DOMAIN][config_entry.entry_id]
    assert machine is not None

    return machine


@patch("custom_components.lamarzocco.api.LaMarzocco.request_status")
@patch("custom_components.lamarzocco.api.LaMarzocco.connect")
@patch("lmdirect.LMDirect.close")
async def test_setup_lm_machine(
    mock_close,
    mock_connect,
    mock_init_data,
    hass,
    config=DATA,
):
    mock_connect.return_value = DATA
    lm = await setup_lm_machine(hass, config)
    assert lm.machine_name == "bbbbb"


@patch("custom_components.lamarzocco.api.LaMarzocco.request_status")
@patch("custom_components.lamarzocco.api.LaMarzocco.connect")
@patch("lmdirect.LMDirect.close")
async def test_controller_unload(
    mock_close,
    mock_connect,
    mock_init_data,
    hass,
):
    entry_id = 1
    mock_connect.return_value = DATA
    machine = await setup_lm_machine(hass)
    assert machine == hass.data[DOMAIN][entry_id]

    assert await hass.config_entries.async_unload(entry_id)
    assert not hass.data[DOMAIN]

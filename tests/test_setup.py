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

CONTROLLER_DATA = {
    CONF_HOST: "1.2.3.4",
    CONF_CLIENT_ID: "aabbcc",
    CONF_CLIENT_SECRET: "bbccdd",
    CONF_USERNAME: "username",
    CONF_PASSWORD: "password",
    CONF_SERIAL_NUMBER: "aabbcc",
    CONF_MODEL_NAME: "aaaaa",
    CONF_MACHINE_NAME: "bbbbb",
}

ENTRY_CONFIG = {"lamarzocco": CONTROLLER_DATA}
ENTRY_OPTIONS = {}

CONFIGURATION = []


async def setup_lm_machine(hass, config=ENTRY_CONFIG, options=ENTRY_OPTIONS):
    await async_setup_component(hass, DOMAIN, {})

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=deepcopy(config),
        options=deepcopy(options),
        entry_id=1,
    )

    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    if config_entry.entry_id not in hass.data[DOMAIN]:
        return None
    machine = hass.data[DOMAIN][config_entry.entry_id]

    return machine


@patch("custom_components.lamarzocco.api.LaMarzocco.init_data")
@patch("custom_components.lamarzocco.api.LaMarzocco.connect")
@patch("lmdirect.LMDirect.close")
async def test_setup_lm_machine(
    mock_close,
    mock_connect,
    mock_init_data,
    hass,
    config=ENTRY_CONFIG,
    options=ENTRY_OPTIONS,
):
    data = {
        "title": "buzz",
        "machine_name": "test_machine",
        "serial_number": "12345",
        "client_id": "aabbcc",
        "client_secret": "bbccdd",
        "username": "username",
        "password": "password",
    }

    mock_connect.return_value = data
    return await setup_lm_machine(hass, config, options)


@patch("custom_components.lamarzocco.api.LaMarzocco.init_data")
@patch("custom_components.lamarzocco.api.LaMarzocco.connect")
@patch("lmdirect.LMDirect.close")
async def test_controller_unload(
    mock_close,
    mock_connect,
    mock_init_data,
    hass,
    config=ENTRY_CONFIG,
    options=ENTRY_OPTIONS,
):
    data = {
        "title": "buzz",
        "machine_name": "test_machine",
        "serial_number": "12345",
        "client_id": "aabbcc",
        "client_secret": "bbccdd",
        "username": "username",
        "password": "password",
    }
    mock_connect.return_value = data
    machine = await setup_lm_machine(hass)
    assert machine == hass.data[DOMAIN][1]
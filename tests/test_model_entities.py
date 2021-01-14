"""Test La Marzocco model-specific entity creation."""
import logging
from copy import deepcopy

import lmdirect
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_registry import async_entries_for_config_entry
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.async_mock import patch
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lamarzocco.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_KEY,
    CONF_MACHINE_NAME,
    CONF_MODEL_NAME,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    MODEL_GS3_AV,
    MODEL_GS3_MP,
    MODEL_LM,
)

_LOGGER = logging.getLogger(__name__)

ENTRY_ID = 1

ENTITIES = 0
SERVICES = 1

MODEL_UNKNOWN = "New Model"
SERIAL_NUMBER = "aabbcc"


async def setup_lm_machine(hass, model):
    await async_setup_component(hass, DOMAIN, {})

    DATA = {
        CONF_HOST: "1.2.3.4",
        CONF_CLIENT_ID: "aabbcc",
        CONF_CLIENT_SECRET: "bbccdd",
        CONF_USERNAME: "username",
        CONF_PASSWORD: "password",
        CONF_SERIAL_NUMBER: SERIAL_NUMBER,
        CONF_MODEL_NAME: model,
        CONF_MACHINE_NAME: "bbbbb",
        CONF_KEY: "12345678901234567890123456789012",
    }

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


async def unload_lm_machine(hass):
    assert await hass.config_entries.async_unload(ENTRY_ID)
    assert not hass.data[DOMAIN]


DATA = {
    MODEL_GS3_AV: {
        ENTITIES: [
            "sensor.bbbbb_coffee_temp",
            "sensor.bbbbb_steam_temp",
            "sensor.bbbbb_total_drinks",
            "switch.bbbbb_main",
            "switch.bbbbb_auto_on_off",
            "switch.bbbbb_prebrew",
        ],
        SERVICES: [
            "set_temp",
            "enable_auto_on_off",
            "disable_auto_on_off",
            "set_auto_on_off_hours",
            "set_dose",
            "set_dose_hot_water",
            "set_prebrew_times",
        ],
    },
    MODEL_GS3_MP: {
        ENTITIES: [
            "switch.bbbbb_main",
            "switch.bbbbb_auto_on_off",
            "sensor.bbbbb_coffee_temp",
            "sensor.bbbbb_steam_temp",
            "sensor.bbbbb_total_drinks",
        ],
        SERVICES: [
            "set_temp",
            "enable_auto_on_off",
            "disable_auto_on_off",
            "set_auto_on_off_hours",
            "set_dose_hot_water",
        ],
    },
    MODEL_LM: {
        ENTITIES: [
            "switch.bbbbb_main",
            "switch.bbbbb_auto_on_off",
            "switch.bbbbb_prebrew",
            "sensor.bbbbb_coffee_temp",
            "sensor.bbbbb_total_drinks",
        ],
        SERVICES: [
            "set_temp",
            "enable_auto_on_off",
            "disable_auto_on_off",
            "set_auto_on_off_hours",
            "set_prebrew_times",
        ],
    },
}


@patch.object(lmdirect.LMDirect, "_send_msg", autospec=True)
class TestModels:
    """Class containing available tests.  Patches will be applied to all member functions."""

    async def test_gs3_av(self, mock_send_msg, hass):
        await self.setup_model(mock_send_msg, hass, MODEL_GS3_AV)

    async def test_gs3_mp(self, mock_send_msg, hass):
        await self.setup_model(mock_send_msg, hass, MODEL_GS3_MP)

    async def test_gs3_lm(self, mock_send_msg, hass):
        await self.setup_model(mock_send_msg, hass, MODEL_LM)

    async def test_unknown_model(self, mock_send_msg, hass):
        await self.setup_model(mock_send_msg, hass, MODEL_UNKNOWN)

    async def setup_model(self, mock_send_msg, hass, model):
        """Test model configurations"""
        await setup_lm_machine(hass, model)

        entity_registry = await hass.helpers.entity_registry.async_get_registry()

        entities = [
            x.entity_id
            for x in async_entries_for_config_entry(entity_registry, ENTRY_ID)
        ]

        adjusted_model = model if model != MODEL_UNKNOWN else MODEL_GS3_AV

        _LOGGER.debug(
            f"ENTITIES: {entities} Expected: {DATA[adjusted_model][ENTITIES]}"
        )

        assert len(entities) == len(DATA[adjusted_model][ENTITIES])
        assert not any(x not in DATA[adjusted_model][ENTITIES] for x in entities)

        services = hass.services.async_services().get(DOMAIN)
        _LOGGER.debug(
            f"SERVICES: {list(services.keys())} Expected: {DATA[adjusted_model][SERVICES]}"
        )

        assert len(services) == len(DATA[adjusted_model][SERVICES])
        assert not any(x not in DATA[adjusted_model][SERVICES] for x in services)

        device_registry = await dr.async_get_registry(hass)
        device_entry = device_registry.async_get_device(
            {(DOMAIN, SERIAL_NUMBER)}, set()
        )

        assert (
            device_entry.model == MODEL_UNKNOWN + " (Unknown)"
            if model == MODEL_UNKNOWN
            else model
        )

        await unload_lm_machine(hass)

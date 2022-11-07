"""Test La Marzocco integration with different incoming messages."""
import logging
from copy import deepcopy
from unittest.mock import patch

import lmdirect
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.setup import async_setup_component
from lmdirect.msgs import GATEWAY_DRINK_MAP, UPDATE_AVAILABLE
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lamarzocco.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_KEY,
    CONF_MACHINE_NAME,
    CONF_MODEL_NAME,
    CONF_SERIAL_NUMBER,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

ENTRY_ID = 1


async def setup_lm_machine(hass):
    await async_setup_component(hass, DOMAIN, {})

    DATA = {
        CONF_HOST: "1.2.3.4",
        CONF_CLIENT_ID: "aabbcc",
        CONF_CLIENT_SECRET: "bbccdd",
        CONF_USERNAME: "username",
        CONF_PASSWORD: "password",
        CONF_SERIAL_NUMBER: "aabbcc",
        CONF_MODEL_NAME: "aaaaa",
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


STATUS_DATA = "status_data"
CONFIG_DATA = "config_data"
AUTO_ON_OFF_DATA = "auto_on_off_data"
DATETIME_DATA = "datetime_data"
DRINKS_DATA = "drinks_data"
FLOW_DATA = "flow_data"
SERIAL_NUM_DATA = "serial_num_data"
PREBREW_TIME_ON = "prebrew_time_on"
PREBREW_TIME_OFF = "prebrew_time_off"
FACTORY_CONFIG = "factory_config"

"""Structure representing all tests to run."""
DATA = {
    FACTORY_CONFIG: {
        "msg": "R4070000E64006400CA000600000101BD0099000056",
        "resp": {
            "flushing_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
            "pid_offset": 20.2,
            "brew_group_offset": 0.5,
            "water_filter_liters": 6,
            "t_unit": 153,
        },
    },
    STATUS_DATA: {
        "msg": "R40000023018C020000000000000000000000000100000000000000010100005003AA0372000205B6",
        "resp": {
            "flushing_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
            "firmware_ver": "1.40",
            "module_ser_num": "",
            "heating_state": ["heating_on", 'steam_heater_on'],
            "power_mystery": 1,
            "water_reservoir_contact": 1,
            "mystery_1": 0,
            "mystery_2": 2,
            "steam_boiler_enable": False,
            "coffee_temp": 93.3,
            "steam_temp": 88.2,
        },
    },
    CONFIG_DATA: {
        "msg": "R0000001F010000026E313903C204D7000B16212C0B16212C00780076006E008203E808B9",
        "resp": {
            "flushing_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
            "coffee_set_temp": 96.2,
            "steam_set_temp": 123.9,
            "enable_prebrewing": 0,
            "prebrew_flag": 0,
            "power": 1,
            "prebrewing_ton_k1": 1.1,
            "prebrewing_ton_k2": 2.2,
            "prebrewing_ton_k3": 3.3,
            "prebrewing_ton_k4": 4.4,
            "prebrewing_toff_k1": 1.1,
            "prebrewing_toff_k2": 2.2,
            "prebrewing_toff_k3": 3.3,
            "prebrewing_toff_k4": 4.4,
            "dose_k1": 120,
            "dose_k2": 118,
            "dose_k3": 110,
            "dose_k4": 130,
            "dose_k5": 1000,
            "dose_hot_water": 8,
        },
    },
    AUTO_ON_OFF_DATA: {
        "msg": "R0310001DFF061106110611061106110611061100000000000000000000000000002F",
        "resp": {
            "flushing_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
            "global_auto": "Enabled",
            "mon_auto": "Enabled",
            "tue_auto": "Enabled",
            "wed_auto": "Enabled",
            "thu_auto": "Enabled",
            "fri_auto": "Enabled",
            "sat_auto": "Enabled",
            "sun_auto": "Enabled",
            "sun_on_hour": 6,
            "sun_on_min": 0,
            "sun_on_time": "06:00",
            "sun_off_hour": 17,
            "sun_off_min": 0,
            "sun_off_time": "17:00",
            "mon_on_hour": 6,
            "mon_on_min": 0,
            "mon_on_time": "06:00",
            "mon_off_hour": 17,
            "mon_off_min": 0,
            "mon_off_time": "17:00",
            "tue_on_hour": 6,
            "tue_on_min": 0,
            "tue_on_time": "06:00",
            "tue_off_hour": 17,
            "tue_off_min": 0,
            "tue_off_time": "17:00",
            "wed_on_hour": 6,
            "wed_on_min": 0,
            "wed_on_time": "06:00",
            "wed_off_hour": 17,
            "wed_off_min": 0,
            "wed_off_time": "17:00",
            "thu_on_hour": 6,
            "thu_on_min": 0,
            "thu_on_time": "06:00",
            "thu_off_hour": 17,
            "thu_off_min": 0,
            "thu_off_time": "17:00",
            "fri_on_hour": 6,
            "fri_on_min": 0,
            "fri_on_time": "06:00",
            "fri_off_hour": 17,
            "fri_off_min": 0,
            "fri_off_time": "17:00",
            "sat_on_hour": 6,
            "sat_on_min": 0,
            "sat_on_time": "06:00",
            "sat_off_hour": 17,
            "sat_off_min": 0,
            "sat_off_time": "17:00",
            "auto_bitfield": 0xFF,
        },
    },
    DATETIME_DATA: {
        "msg": "R03000007001A0906020115A6",
        "resp": {
            "flushing_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
            "second": 0,
            "minute": 26,
            "hour": 9,
            "dayofweek": 6,
            "day": 2,
            "month": 21,
        },
    },
    DRINKS_DATA: {
        "msg": "R0020002C0000014B00000098000001B1000000250000056A00000923000000180000000A00000AEE000000180000003A48",
        "resp": {
            "flushing_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
            "drinks_k1": 331,
            "drinks_k2": 152,
            "drinks_k3": 433,
            "drinks_k4": 37,
            "continuous": 1386,
            "total_coffee": 2339,
            "total_coffee_activations": 2798,
            "total_flushing": 459,
            "hot_water": 24,
            "drink_mystery": 10,
            "hot_water_2": 24,
            "drinks_hot_water": 58,
        },
    },
    FLOW_DATA: {
        "msg": "Z600000160000000000000000000000000401000A000E03B604D4E604",
        "resp": {
            "flushing_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
            "flow_seconds": 10,
            "flow_pulses": 14,
            "flow_key": 4,
            "flow_rate": 1,
        },
    },
    SERIAL_NUM_DATA: {
        "msg": "R010000115A000000000000000000000000000000004B",
        "resp": {
            "flushing_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
            "machine_ser_num": "",
        },
    },
    PREBREW_TIME_ON: {
        "msg": "W000F0001OK88",
        "resp": {
            "flushing_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
        },
    },
    PREBREW_TIME_OFF: {
        "msg": "W00130001OK76",
        "resp": {
            "flushing_offset": 0,
            "drinks_k1_offset": 0,
            "drinks_k2_offset": 0,
            "drinks_k3_offset": 0,
            "drinks_k4_offset": 0,
            "continuous_offset": 0,
            "update_available": "none",
        },
    },
}


@patch.object(lmdirect.LMDirect, "_send_msg", autospec=True)
class TestMessages:
    """Class containing available tests.  Patches will be applied to all member functions."""

    async def test_status_data(self, mock_send_msg, hass, enable_custom_integrations):
        await self.send_items(mock_send_msg, hass, [STATUS_DATA])

    async def test_config_data(self, mock_send_msg, hass, enable_custom_integrations):
        await self.send_items(mock_send_msg, hass, [CONFIG_DATA])

    async def test_auto_on_off_data(
        self, mock_send_msg, hass, enable_custom_integrations
    ):
        await self.send_items(mock_send_msg, hass, [AUTO_ON_OFF_DATA])

    async def test_datetime_data(self, mock_send_msg, hass, enable_custom_integrations):
        await self.send_items(mock_send_msg, hass, [DATETIME_DATA])

    async def test_drinks_data(self, mock_send_msg, hass, enable_custom_integrations):
        await self.send_items(mock_send_msg, hass, [DRINKS_DATA])

    async def test_flow_data(self, mock_send_msg, hass, enable_custom_integrations):
        await self.send_items(mock_send_msg, hass, [FLOW_DATA])

    async def test_serial_number_data(
        self, mock_send_msg, hass, enable_custom_integrations
    ):
        await self.send_items(mock_send_msg, hass, [SERIAL_NUM_DATA])

    async def test_prebrew_time_on(
        self, mock_send_msg, hass, enable_custom_integrations
    ):
        await self.send_items(mock_send_msg, hass, [PREBREW_TIME_ON])

    async def test_prebrew_time_off(
        self, mock_send_msg, hass, enable_custom_integrations
    ):
        await self.send_items(mock_send_msg, hass, [PREBREW_TIME_OFF])

    async def test_factory_config(
        self, mock_send_msg, hass, enable_custom_integrations
    ):
        await self.send_items(mock_send_msg, hass, [FACTORY_CONFIG])

    async def test_send_all_data(self, mock_send_msg, hass, enable_custom_integrations):
        await self.send_items(mock_send_msg, hass, list(DATA.keys()))

    async def send_items(self, mock_send_msg, hass, items):
        """Inject data and compare results."""

        def _get_key(k):
            """Construct tag name if needed."""
            if isinstance(k, tuple):
                k = "_".join(k)
            return k

        expected = {}
        result = {}

        async def add_data(self, *args, **kwargs):
            async def send_msg(self, *args, **kwargs):
                """Populate data structures with sample data."""
                nonlocal expected
                nonlocal result
                msg = DATA[kwargs["item"]]["msg"]
                resp = DATA[kwargs["item"]]["resp"]
                expected.update(resp)
                print(f"SENDING {msg} expecting {resp}")
                self._current_status.update(
                    {_get_key(GATEWAY_DRINK_MAP[x]): 0 for x in range(-1, 5)}
                )
                self._current_status.update({UPDATE_AVAILABLE: "none"})
                assert await self.process_data(msg)

            await send_msg(self, *args, item=FACTORY_CONFIG, **kwargs)
            [await send_msg(self, *args, item=x, **kwargs) for x in items]
            result.update(self._current_status)
            print(f"Result: {result}")
            print(f"Expected: {expected}")

        """Populate data every time the _send_msg API is called, simulating lots of incoming data."""
        mock_send_msg.side_effect = add_data

        await setup_lm_machine(hass)

        await hass.async_block_till_done()

        assert result == expected

        await unload_lm_machine(hass)

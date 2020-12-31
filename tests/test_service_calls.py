"""Test La Marzocco service calls"""
import logging
from copy import deepcopy

import lmdirect
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
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
    SERVICE_DISABLE_AUTO_ON_OFF,
    SERVICE_ENABLE_AUTO_ON_OFF,
    SERVICE_SET_AUTO_ON_OFF_HOURS,
    SERVICE_SET_COFFEE_TEMP,
    SERVICE_SET_DOSE,
    SERVICE_SET_DOSE_TEA,
    SERVICE_SET_PREBREW_TIMES,
    SERVICE_SET_STEAM_TEMP,
)

_LOGGER = logging.getLogger(__name__)

ENTRY_ID = 1
CALL_DOMAIN = "call_domain"
CALL_DATA = "call_data"
CALL_RESULTS = "call_result"
USE_CALLBACK = "use_callback"

SERVICE = 0
DATA = 1


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


SERVICE_CALLS = [
    # Set coffee temp to 203.1F
    (
        SERVICE_SET_COFFEE_TEMP,
        {
            CALL_DOMAIN: DOMAIN,
            CALL_DATA: {"entity_id": "switch.bbbbb_main", "temperature": "203.1"},
            CALL_RESULTS: [((8,), {"data": "07EF"}), ((4,), {"data": "07EF"})],
            USE_CALLBACK: False,
        },
    ),
    # Set steam temp to 255.1F
    (
        SERVICE_SET_STEAM_TEMP,
        {
            CALL_DOMAIN: DOMAIN,
            CALL_DATA: {"entity_id": "switch.bbbbb_main", "temperature": "255.1"},
            CALL_RESULTS: [((9,), {"data": "09F7"}), ((4,), {"data": "09F7"})],
            USE_CALLBACK: False,
        },
    ),
    # Enable auto on/off for Tuesday
    (
        SERVICE_ENABLE_AUTO_ON_OFF,
        {
            CALL_DOMAIN: DOMAIN,
            CALL_DATA: {"entity_id": "switch.bbbbb_main", "day_of_week": "tue"},
            CALL_RESULTS: [
                ((2,), {}),
                (
                    (11,),
                    {
                        "data": "FF06110611061106110611061106110000000000000000000000000000"
                    },
                ),
                ((2,), {}),
            ],
            USE_CALLBACK: True,
        },
    ),
    # Disable auto on/off for Tuesday
    (
        SERVICE_DISABLE_AUTO_ON_OFF,
        {
            CALL_DOMAIN: DOMAIN,
            CALL_DATA: {"entity_id": "switch.bbbbb_main", "day_of_week": "tue"},
            CALL_RESULTS: [
                ((2,), {}),
                (
                    (11,),
                    {
                        "data": "FB06110611061106110611061106110000000000000000000000000000"
                    },
                ),
                ((2,), {}),
            ],
            USE_CALLBACK: True,
        },
    ),
    # Set auto on/off to 5AM to 12PM on Tuesday
    (
        SERVICE_SET_AUTO_ON_OFF_HOURS,
        {
            CALL_DOMAIN: DOMAIN,
            CALL_DATA: {
                "entity_id": "switch.bbbbb_main",
                "day_of_week": "tue",
                "hour_on": "5",
                "hour_off": "12",
            },
            CALL_RESULTS: [
                ((2,), {}),
                (
                    (11,),
                    {
                        "data": "FF06110611050C06110611061106110000000000000000000000000000"
                    },
                ),
                ((2,), {}),
            ],
            USE_CALLBACK: True,
        },
    ),
    # Set dose for key 2 to 120 pulses
    (
        SERVICE_SET_DOSE,
        {
            CALL_DOMAIN: DOMAIN,
            CALL_DATA: {
                "entity_id": "switch.bbbbb_main",
                "key": "2",
                "pulses": "120",
            },
            CALL_RESULTS: [
                ((12,), {"data": "0078", "key": "16"}),
                ((1,), {}),
            ],
            USE_CALLBACK: False,
        },
    ),
    # Set dose for key 2 to 120 pulses
    (
        SERVICE_SET_DOSE,
        {
            CALL_DOMAIN: DOMAIN,
            CALL_DATA: {
                "entity_id": "switch.bbbbb_main",
                "key": "2",
                "pulses": "120",
            },
            CALL_RESULTS: [
                ((12,), {"data": "0078", "key": "16"}),
                ((1,), {}),
            ],
            USE_CALLBACK: False,
        },
    ),
    # Set prebrew time for key 4 to 3.1 seconds on and 2.5 seconds off
    (
        SERVICE_SET_PREBREW_TIMES,
        {
            CALL_DOMAIN: DOMAIN,
            CALL_DATA: {
                "entity_id": "switch.bbbbb_main",
                "key": "4",
                "time_on": "3.1",
                "time_off": "2.5",
            },
            CALL_RESULTS: [
                ((14,), {"data": "1F", "key": "0F"}),
                ((14,), {"data": "19", "key": "13"}),
                ((1,), {}),
            ],
            USE_CALLBACK: False,
        },
    ),
    # Set tea dose to 16 seconds
    (
        SERVICE_SET_DOSE_TEA,
        {
            CALL_DOMAIN: DOMAIN,
            CALL_DATA: {
                "entity_id": "switch.bbbbb_main",
                "seconds": "16",
            },
            CALL_RESULTS: [
                ((13,), {"data": "10"}),
                ((1,), {}),
            ],
            USE_CALLBACK: False,
        },
    ),
    # Turn on the main switch
    (
        SERVICE_TURN_ON,
        {
            CALL_DOMAIN: SWITCH_DOMAIN,
            CALL_DATA: {
                "entity_id": "switch.bbbbb_main",
            },
            CALL_RESULTS: [
                ((3,), {"data": "01"}),
                ((1,), {}),
            ],
            USE_CALLBACK: False,
        },
    ),
    # Turn off the main switch
    (
        SERVICE_TURN_OFF,
        {
            CALL_DOMAIN: SWITCH_DOMAIN,
            CALL_DATA: {
                "entity_id": "switch.bbbbb_main",
            },
            CALL_RESULTS: [
                ((3,), {"data": "00"}),
                ((1,), {}),
            ],
            USE_CALLBACK: False,
        },
    ),
    # Turn prebew on
    (
        SERVICE_TURN_ON,
        {
            CALL_DOMAIN: SWITCH_DOMAIN,
            CALL_DATA: {
                "entity_id": "switch.bbbbb_prebrew",
            },
            CALL_RESULTS: [
                ((10,), {"data": "01"}),
                ((1,), {}),
            ],
            USE_CALLBACK: False,
        },
    ),
    # Turn prebew off
    (
        SERVICE_TURN_OFF,
        {
            CALL_DOMAIN: SWITCH_DOMAIN,
            CALL_DATA: {
                "entity_id": "switch.bbbbb_prebrew",
            },
            CALL_RESULTS: [
                ((10,), {"data": "00"}),
                ((1,), {}),
            ],
            USE_CALLBACK: False,
        },
    ),
    # Enable auto on/off
    (
        SERVICE_TURN_ON,
        {
            CALL_DOMAIN: SWITCH_DOMAIN,
            CALL_DATA: {
                "entity_id": "switch.bbbbb_auto_on_off",
            },
            CALL_RESULTS: [
                ((2,), {}),
                (
                    (11,),
                    {
                        "data": "FF06110611061106110611061106110000000000000000000000000000"
                    },
                ),
                ((2,), {}),
            ],
            USE_CALLBACK: True,
        },
    ),
    # Disable auto on/off
    (
        SERVICE_TURN_OFF,
        {
            CALL_DOMAIN: SWITCH_DOMAIN,
            CALL_DATA: {
                "entity_id": "switch.bbbbb_auto_on_off",
            },
            CALL_RESULTS: [
                ((2,), {}),
                (
                    (11,),
                    {
                        "data": "FE06110611061106110611061106110000000000000000000000000000"
                    },
                ),
                ((2,), {}),
            ],
            USE_CALLBACK: True,
        },
    ),
]

AUTO_ON_OFF_DATA = (
    "R0310001DFF061106110611061106110611061100000000000000000000000000002F"
)


@patch("custom_components.lamarzocco.api.LaMarzocco.connect")
@patch.object(lmdirect.LMDirect, "_send_msg", autospec=True)
class TestServices:
    async def test_set_coffee_temp(self, mock_send_msg, mock_connect, hass):
        await self.make_service_call(mock_send_msg, hass, 0)

    async def test_set_steam_temp(self, mock_send_msg, mock_connect, hass):
        await self.make_service_call(mock_send_msg, hass, 1)

    async def test_enable_auto_on_off(self, mock_send_msg, mock_connect, hass):
        await self.make_service_call(mock_send_msg, hass, 2)

    async def test_disable_auto_on_off(self, mock_send_msg, mock_connect, hass):
        await self.make_service_call(mock_send_msg, hass, 3)

    async def test_set_auto_on_off_hours(self, mock_send_msg, mock_connect, hass):
        await self.make_service_call(mock_send_msg, hass, 4)

    async def test_set_dose(self, mock_send_msg, mock_connect, hass):
        await self.make_service_call(mock_send_msg, hass, 5)

    async def test_set_prebrew_times(self, mock_send_msg, mock_connect, hass):
        await self.make_service_call(mock_send_msg, hass, 6)

    async def test_set_dose_tea(self, mock_send_msg, mock_connect, hass):
        await self.make_service_call(mock_send_msg, hass, 7)

    async def test_turn_on_main(self, mock_send_msg, mock_connect, hass):
        await self.make_service_call(mock_send_msg, hass, 8)

    async def test_turn_off_main(self, mock_send_msg, mock_connect, hass):
        await self.make_service_call(mock_send_msg, hass, 9)

    async def test_turn_on_prebrew(self, mock_send_msg, mock_connect, hass):
        await self.make_service_call(mock_send_msg, hass, 10)

    async def test_turn_off_prebrew(self, mock_send_msg, mock_connect, hass):
        await self.make_service_call(mock_send_msg, hass, 11)

    async def test_turn_on_auto_on_off(self, mock_send_msg, mock_connect, hass):
        await self.make_service_call(mock_send_msg, hass, 12)

    async def test_turn_off_auto_on_off(self, mock_send_msg, mock_connect, hass):
        await self.make_service_call(mock_send_msg, hass, 13)

    async def make_service_call(self, mock_send_msg, hass, index):
        """Test one service call"""

        def validate_results(arg_list, expected):
            assert len(arg_list) == len(expected)
            expect_iter = iter(expected)
            for call in arg_list:
                args, kwargs = call
                _LOGGER.error(f"arg_list={arg_list}, args={args}, kwargs={kwargs}")
                args = args[1:]
                elem = next(expect_iter)
                _LOGGER.debug(f"ARGS=<{args}><{elem[0]}>, KWARGS=<{kwargs}><{elem[1]}>")
                assert args == elem[0] and kwargs == elem[1]

        async def callback_method(self, param, param2=None):
            mock_send_msg.side_effect = None
            await self._process_data(AUTO_ON_OFF_DATA)

        await setup_lm_machine(hass)

        service = SERVICE_CALLS[index][SERVICE]
        data = SERVICE_CALLS[index][DATA]

        if data[USE_CALLBACK]:
            mock_send_msg.side_effect = callback_method

        mock_send_msg.reset_mock()

        await hass.services.async_call(
            data[CALL_DOMAIN],
            service,
            data[CALL_DATA],
        )
        await hass.async_block_till_done()

        validate_results(mock_send_msg.call_args_list, data[CALL_RESULTS])

        _LOGGER.debug(f"CALLS: {mock_send_msg.mock_calls}")

        await unload_lm_machine(hass)

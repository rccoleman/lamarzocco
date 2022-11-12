"""Test La Marzocco service calls"""
import logging
from copy import deepcopy
from unittest.mock import PropertyMock, patch

import lmdirect
import pytest
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.water_heater import DOMAIN as WATER_HEATER_DOMAIN
from homeassistant.components.water_heater import SERVICE_SET_TEMPERATURE
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.exceptions import ServiceNotFound
from homeassistant.setup import async_setup_component
from lmdirect.msgs import Msg, MODEL_GS3_AV, MODEL_GS3_MP, MODEL_LM
from pytest_homeassistant_custom_component.common import MockConfigEntry
from voluptuous.error import MultipleInvalid

from custom_components.lamarzocco.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_KEY,
    CONF_MACHINE_NAME,
    CONF_MODEL_NAME,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    MODELS,
)
from custom_components.lamarzocco.sensor import LaMarzoccoSensor

_LOGGER = logging.getLogger(__name__)

ENTRY_ID = 1
CALL_SERVICE = "call_service"
CALL_DOMAIN = "call_domain"
CALL_DATA = "call_data"
CALL_RESULTS = "call_result"
USE_CALLBACK = "use_callback"

SERVICE = 0
DATA = 1

"""Services to test."""
TEST_SET_COFFEE_TEMP = 0
TEST_SET_STEAM_TEMP = 1
TEST_ENABLE_AUTO_ON_OFF = 2
TEST_DISABLE_AUTO_ON_OFF = 3
TEST_SET_AUTO_ON_OFF_TIMES = 4
TEST_SET_DOSE = 5
TEST_SET_PREBREW_TIMES = 6
TEST_SET_DOSE_HOT_WATER = 7
TEST_TURN_ON_MAIN = 8
TEST_TURN_OFF_MAIN = 9
TEST_ENABLE_PREBREW = 10
TEST_DISABLE_PREBREW = 11
TEST_ENABLE_GLOBAL_AUTO_ON_OFF = 12
TEST_DISABLE_GLOBAL_AUTO_ON_OFF = 13
TEST_SET_PREINFUSION_TIME = 14

"""Table of tests to run and respones to expect."""
TESTS = {
    # Set coffee temp to 203.1F
    TEST_SET_COFFEE_TEMP: {
        CALL_SERVICE: SERVICE_SET_TEMPERATURE,
        CALL_DOMAIN: WATER_HEATER_DOMAIN,
        CALL_DATA: {"entity_id": "water_heater.bbbbb_coffee", "temperature": "203.1"},
        CALL_RESULTS: [(Msg.SET_COFFEE_TEMP, ["07EF"])],
        USE_CALLBACK: False,
    },
    # Set steam temp to 255.1F
    TEST_SET_STEAM_TEMP: {
        CALL_SERVICE: SERVICE_SET_TEMPERATURE,
        CALL_DOMAIN: WATER_HEATER_DOMAIN,
        CALL_DATA: {"entity_id": "water_heater.bbbbb_steam", "temperature": "255.1"},
        CALL_RESULTS: [(Msg.SET_STEAM_TEMP, ["09F7"])],
        USE_CALLBACK: False,
    },
    # Enable auto on/off for Tuesday
    TEST_ENABLE_AUTO_ON_OFF: {
        CALL_SERVICE: Msg.SET_AUTO_ON_OFF_ENABLE,
        CALL_DOMAIN: DOMAIN,
        CALL_DATA: {
            "day_of_week": "tue",
            "enable": "on",
        },
        CALL_RESULTS: [
            (Msg.SET_AUTO_ON_OFF_ENABLE, ["FF"]),
        ],
        USE_CALLBACK: True,
    },
    # Disable auto on/off for Tuesday
    TEST_DISABLE_AUTO_ON_OFF: {
        CALL_SERVICE: Msg.SET_AUTO_ON_OFF_ENABLE,
        CALL_DOMAIN: DOMAIN,
        CALL_DATA: {
            "day_of_week": "tue",
            "enable": "off",
        },
        CALL_RESULTS: [
            (Msg.SET_AUTO_ON_OFF_ENABLE, ["FB"]),
        ],
        USE_CALLBACK: True,
    },
    # Set auto on/off to 5:05AM to 12:10PM on Tuesday
    TEST_SET_AUTO_ON_OFF_TIMES: {
        CALL_SERVICE: Msg.SET_AUTO_ON_OFF_TIMES,
        CALL_DOMAIN: DOMAIN,
        CALL_DATA: {
            "day_of_week": "tue",
            "hour_on": "5",
            "minute_on": "5",
            "hour_off": "12",
            "minute_off": "10",
        },
        CALL_RESULTS: [(Msg.SET_AUTO_ON_OFF_TIMES, ["13", "050C"]), (Msg.SET_AUTO_ON_OFF_TIMES, ["22", "050A"])],
        USE_CALLBACK: False,
    },
    # Set dose for key 2 to 120 pulses
    TEST_SET_DOSE: {
        CALL_SERVICE: Msg.SET_DOSE,
        CALL_DOMAIN: DOMAIN,
        CALL_DATA: {
            "key": "2",
            "pulses": "120",
        },
        CALL_RESULTS: [
            (Msg.SET_DOSE, ["16", "0078"]),
        ],
        USE_CALLBACK: False,
    },
    # Set prebrew time for key 4 to 3.1 seconds on and 2.5 seconds off
    TEST_SET_PREBREW_TIMES: {
        CALL_SERVICE: Msg.SET_PREBREW_TIMES,
        CALL_DOMAIN: DOMAIN,
        CALL_DATA: {
            "key": "4",
            "seconds_on": "3.1",
            "seconds_off": "2.5",
        },
        CALL_RESULTS: [
            (Msg.SET_PREBREW_TIMES, ["0F", "1F"]),
            (Msg.SET_PREBREW_TIMES, ["13", "19"]),
        ],
        USE_CALLBACK: False,
    },
    # Set hot water dose to 16 seconds
    TEST_SET_DOSE_HOT_WATER: {
        CALL_SERVICE: Msg.SET_DOSE_HOT_WATER,
        CALL_DOMAIN: DOMAIN,
        CALL_DATA: {
            "seconds": "16",
        },
        CALL_RESULTS: [
            (Msg.SET_DOSE_HOT_WATER, ["10"]),
        ],
        USE_CALLBACK: False,
    },
    # Turn on the main switch
    TEST_TURN_ON_MAIN: {
        CALL_SERVICE: SERVICE_TURN_ON,
        CALL_DOMAIN: SWITCH_DOMAIN,
        CALL_DATA: {
            "entity_id": "switch.bbbbb_main",
        },
        CALL_RESULTS: [
            (Msg.SET_POWER, ["01"]),
        ],
        USE_CALLBACK: False,
    },
    # Turn off the main switch
    TEST_TURN_OFF_MAIN: {
        CALL_SERVICE: SERVICE_TURN_OFF,
        CALL_DOMAIN: SWITCH_DOMAIN,
        CALL_DATA: {
            "entity_id": "switch.bbbbb_main",
        },
        CALL_RESULTS: [
            (Msg.SET_POWER, ["00"]),
        ],
        USE_CALLBACK: False,
    },
    # Turn prebew on
    TEST_ENABLE_PREBREW: {
        CALL_SERVICE: SERVICE_TURN_ON,
        CALL_DOMAIN: SWITCH_DOMAIN,
        CALL_DATA: {
            "entity_id": "switch.bbbbb_prebrew",
        },
        CALL_RESULTS: [
            (Msg.SET_PREBREWING_ENABLE, ["01"]),
        ],
        USE_CALLBACK: False,
    },
    # Turn prebew off
    TEST_DISABLE_PREBREW: {
        CALL_SERVICE: SERVICE_TURN_OFF,
        CALL_DOMAIN: SWITCH_DOMAIN,
        CALL_DATA: {
            "entity_id": "switch.bbbbb_prebrew",
        },
        CALL_RESULTS: [
            (Msg.SET_PREBREWING_ENABLE, ["00"]),
        ],
        USE_CALLBACK: False,
    },
    # Enable global auto on/off
    TEST_ENABLE_GLOBAL_AUTO_ON_OFF: {
        CALL_SERVICE: SERVICE_TURN_ON,
        CALL_DOMAIN: SWITCH_DOMAIN,
        CALL_DATA: {
            "entity_id": "switch.bbbbb_auto_on_off",
        },
        CALL_RESULTS: [
            (Msg.SET_AUTO_ON_OFF_ENABLE, ["FF"]),
        ],
        USE_CALLBACK: True,
    },
    # Disable global auto on/off
    TEST_DISABLE_GLOBAL_AUTO_ON_OFF: {
        CALL_SERVICE: SERVICE_TURN_OFF,
        CALL_DOMAIN: SWITCH_DOMAIN,
        CALL_DATA: {
            "entity_id": "switch.bbbbb_auto_on_off",
        },
        CALL_RESULTS: [
            (Msg.SET_AUTO_ON_OFF_ENABLE, ["FE"]),
        ],
        USE_CALLBACK: True,
    },
    # Set prebrew time for key 4 to 3.1 seconds on and 2.5 seconds off
    TEST_SET_PREINFUSION_TIME: {
        CALL_SERVICE: Msg.SET_PREINFUSION_TIME,
        CALL_DOMAIN: DOMAIN,
        CALL_DATA: {
            "key": "4",
            "seconds": "22.2",
        },
        CALL_RESULTS: [
            (Msg.SET_PREINFUSION_TIME, ["E5", "DE"]),
        ],
        USE_CALLBACK: False,
    },
}

"""Data to inject during the auto on/off tests."""
AUTO_ON_OFF_DATA = (
    "R0310001DFF061106110611061106110611061100000000000000000000000000002F"
)


async def setup_lm_machine(hass):
    """Set up a test configuration."""

    await async_setup_component(hass, DOMAIN, {})

    DATA = {
        CONF_HOST: "1.2.3.4",
        CONF_CLIENT_ID: "aabbcc",
        CONF_CLIENT_SECRET: "bbccdd",
        CONF_USERNAME: "username",
        CONF_PASSWORD: "password",
        CONF_SERIAL_NUMBER: "aabbcc",
        CONF_MODEL_NAME: "GS3 AV",
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


async def mock_call_service(func, *args, **kwargs):
    await func(*args, **kwargs)
    return True


@patch.object(lmdirect.LMDirect, "_send_msg", autospec=True)
@patch("lmdirect.LMDirect.model_name", new_callable=PropertyMock, return_value="none")
@patch(
    "custom_components.lamarzocco.services.call_service",
    autospec=True,
    side_effect=mock_call_service,
)
class TestServices:
    """Class containing available tests.  Patches will be applied to all member functions."""

    async def test_set_coffee_temp(
        self,
        mock_call,
        mock_model_name,
        mock_send_msg,
        hass,
        enable_custom_integrations,
    ):
        with patch.object(
            LaMarzoccoSensor, "available", new_callable=PropertyMock, return_value=True
        ):
            for model in MODELS:
                mock_model_name.return_value = model
                await self.make_service_call(mock_send_msg, hass, TEST_SET_COFFEE_TEMP)

    async def test_set_steam_temp(
        self,
        mock_call,
        mock_model_name,
        mock_send_msg,
        hass,
        enable_custom_integrations,
    ):
        with patch.object(
            LaMarzoccoSensor, "available", new_callable=PropertyMock, return_value=True
        ):
            for model in [MODEL_GS3_AV, MODEL_GS3_MP]:
                mock_model_name.return_value = model
                await self.make_service_call(mock_send_msg, hass, TEST_SET_STEAM_TEMP)

    async def test_enable_auto_on_off(
        self,
        mock_call,
        mock_model_name,
        mock_send_msg,
        hass,
        enable_custom_integrations,
    ):
        for model in MODELS:
            mock_model_name.return_value = model
            await self.make_service_call(mock_send_msg, hass, TEST_ENABLE_AUTO_ON_OFF)

    async def test_disable_auto_on_off(
        self,
        mock_call,
        mock_model_name,
        mock_send_msg,
        hass,
        enable_custom_integrations,
    ):
        for model in MODELS:
            mock_model_name.return_value = model
            await self.make_service_call(mock_send_msg, hass, TEST_DISABLE_AUTO_ON_OFF)

    async def test_set_auto_on_off_times(
        self,
        mock_call,
        mock_model_name,
        mock_send_msg,
        hass,
        enable_custom_integrations,
    ):
        for model in MODELS:
            mock_model_name.return_value = model
            await self.make_service_call(mock_send_msg, hass, TEST_SET_AUTO_ON_OFF_TIMES)

    async def test_set_dose(
        self,
        mock_call,
        mock_model_name,
        mock_send_msg,
        hass,
        enable_custom_integrations,
    ):
        for model in MODELS:
            mock_model_name.return_value = model
            if model in [MODEL_GS3_MP, MODEL_LM]:
                with pytest.raises(ServiceNotFound):
                    await self.make_service_call(mock_send_msg, hass, TEST_SET_DOSE)
            else:
                await self.make_service_call(mock_send_msg, hass, TEST_SET_DOSE)

    async def test_set_prebrew_times(
        self,
        mock_call,
        mock_model_name,
        mock_send_msg,
        hass,
        enable_custom_integrations,
    ):
        expected_exceptions = {
            MODEL_GS3_MP: ServiceNotFound,
            MODEL_LM: (lmdirect.InvalidInput, MultipleInvalid),
        }
        for model in MODELS:
            mock_model_name.return_value = model

            _LOGGER.debug(f"Testing {model}")
            if model in [MODEL_GS3_MP, MODEL_LM]:
                with pytest.raises(expected_exceptions[model]):
                    await self.make_service_call(mock_send_msg, hass, TEST_SET_PREBREW_TIMES)
            else:
                await self.make_service_call(mock_send_msg, hass, TEST_SET_PREBREW_TIMES)

    async def test_set_dose_hot_water(
        self,
        mock_call,
        mock_model_name,
        mock_send_msg,
        hass,
        enable_custom_integrations,
    ):
        for model in MODELS:
            mock_model_name.return_value = model
            if model == MODEL_LM:
                with pytest.raises(ServiceNotFound):
                    await self.make_service_call(
                        mock_send_msg, hass, TEST_SET_DOSE_HOT_WATER
                    )
            else:
                await self.make_service_call(mock_send_msg, hass, TEST_SET_DOSE_HOT_WATER)

    async def test_turn_on_main(
        self,
        mock_call,
        mock_model_name,
        mock_send_msg,
        hass,
        enable_custom_integrations,
    ):
        for model in MODELS:
            mock_model_name.return_value = model
            await self.make_service_call(mock_send_msg, hass, TEST_TURN_ON_MAIN)

    async def test_turn_off_main(
        self,
        mock_call,
        mock_model_name,
        mock_send_msg,
        hass,
        enable_custom_integrations,
    ):
        for model in MODELS:
            mock_model_name.return_value = model
            await self.make_service_call(mock_send_msg, hass, TEST_TURN_OFF_MAIN)

    async def test_enable_prebrew(
        self,
        mock_call,
        mock_model_name,
        mock_send_msg,
        hass,
        enable_custom_integrations,
    ):
        for model in [MODEL_GS3_AV, MODEL_LM]:
            mock_model_name.return_value = model
            await self.make_service_call(mock_send_msg, hass, TEST_ENABLE_PREBREW)

    async def test_disable_prebrew(
        self,
        mock_call,
        mock_model_name,
        mock_send_msg,
        hass,
        enable_custom_integrations,
    ):
        for model in [MODEL_GS3_AV, MODEL_LM]:
            mock_model_name.return_value = model
            await self.make_service_call(mock_send_msg, hass, TEST_DISABLE_PREBREW)

    async def test_enable_global_auto_on_off(
        self,
        mock_call,
        mock_model_name,
        mock_send_msg,
        hass,
        enable_custom_integrations,
    ):
        for model in MODELS:
            mock_model_name.return_value = model
            await self.make_service_call(mock_send_msg, hass, TEST_ENABLE_GLOBAL_AUTO_ON_OFF)

    async def test_disable_global_auto_on_off(
        self,
        mock_call,
        mock_model_name,
        mock_send_msg,
        hass,
        enable_custom_integrations,
    ):
        for model in MODELS:
            mock_model_name.return_value = model
            await self.make_service_call(
                mock_send_msg, hass, TEST_DISABLE_GLOBAL_AUTO_ON_OFF
            )

    async def test_set_preinfusion_time(
        self,
        mock_call,
        mock_model_name,
        mock_send_msg,
        hass,
        enable_custom_integrations,
    ):
        expected_exceptions = {
            MODEL_GS3_MP: ServiceNotFound,
            MODEL_LM: (lmdirect.InvalidInput, MultipleInvalid),
        }
        for model in MODELS:
            mock_model_name.return_value = model

            _LOGGER.debug(f"Testing {model}")
            if model in [MODEL_GS3_MP, MODEL_LM]:
                with pytest.raises(expected_exceptions[model]):
                    await self.make_service_call(mock_send_msg, hass, TEST_SET_PREINFUSION_TIME)
            else:
                await self.make_service_call(mock_send_msg, hass, TEST_SET_PREINFUSION_TIME)

    async def make_service_call(self, mock_send_msg, hass, test):
        """Test one service call"""

        def validate_results(arg_list, expected):
            """Compare results to expected values."""
            assert len(arg_list) == len(expected)
            expect_iter = iter(expected)
            for call in arg_list:
                _LOGGER.debug(
                    f"CALL=<{call}>"
                )
                received_args, received_kwargs = call
                (received_args,) = received_args[1:]
                received_kwargs = list(received_kwargs.values())
                expect_args, expect_kwargs = next(expect_iter)
                _LOGGER.debug(
                    f"ARGS=<{received_args}><{expect_args}>, KWARGS=<{received_kwargs}><{expect_kwargs}>"
                )
                assert received_args == expect_args and received_kwargs == expect_kwargs

        async def callback_method(self, msg, **kwargs):
            """Callback is called from LMDirect instance context."""
            mock_send_msg.side_effect = None
            await self.process_data(AUTO_ON_OFF_DATA)
            _LOGGER.debug(f"{self._current_status}")

        """Retrieve the test to run."""
        test_entry = TESTS[test]

        mock_send_msg.side_effect = None

        await setup_lm_machine(hass)

        """If we're running an auto on/off test, we need to send simulate incoming data."""
        if test_entry[USE_CALLBACK]:
            mock_send_msg.side_effect = callback_method

            """We won't have done a query yet, so make a call that we can verify failure and mock."""
            with pytest.raises(lmdirect.NotReady):
                result = await hass.services.async_call(
                    test_entry[CALL_DOMAIN],
                    test_entry[CALL_SERVICE],
                    test_entry[CALL_DATA],
                    blocking=True,
                )
                await hass.async_block_till_done()

        """Make sure that mock calls during setup are zeroed out."""
        mock_send_msg.reset_mock()

        try:
            result = await hass.services.async_call(
                test_entry[CALL_DOMAIN],
                test_entry[CALL_SERVICE],
                test_entry[CALL_DATA],
                blocking=True,
            )
            await hass.async_block_till_done()

            _LOGGER.debug(f"RESULT={result}")
            _LOGGER.debug(f"ARG_LIST={mock_send_msg.call_args_list}")

            validate_results(mock_send_msg.call_args_list, test_entry[CALL_RESULTS])

        except Exception as err:
            _LOGGER.debug(f"Got exception, re-raising: {err}")
            raise
        finally:
            await unload_lm_machine(hass)
            await hass.async_block_till_done()

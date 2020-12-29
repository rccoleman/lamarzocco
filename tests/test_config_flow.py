"""Tests for the config flow."""
from unittest import mock

from homeassistant.const import CONF_ACCESS_TOKEN, CONF_NAME, CONF_PATH
from homeassistant import data_entry_flow
from lmdirect.connection import AuthFail

import pytest
from pytest_homeassistant_custom_component.async_mock import AsyncMock, patch
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lamarzocco import config_flow
from custom_components.lamarzocco.const import DOMAIN
from custom_components.lamarzocco.config_flow import validate_input, InvalidAuth
from lmdirect import LMDirect


@patch("custom_components.lamarzocco.api.LaMarzocco.init_data")
@patch("custom_components.lamarzocco.api.LaMarzocco.connect")
@patch("lmdirect.LMDirect.close")
async def test_function(mock_init_data, mock_connect, mock_close, hass):
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
    result = await validate_input(hass, data)
    assert result == data


async def test_flow_user_init(hass):
    """Test the initialization of the form in the first step of the config flow."""
    data = {
        "title": "buzz",
    }
    with patch(
        "custom_components.lamarzocco.config_flow.validate_input"
    ) as mock_validate_input:
        machine_info = mock_validate_input.return_value = data
        result = await hass.config_entries.flow.async_init(
            config_flow.DOMAIN, context={"source": "user"}
        )
    expected = {
        "data_schema": config_flow.STEP_USER_DATA_SCHEMA,
        "description_placeholders": None,
        "errors": {},
        "flow_id": mock.ANY,
        "handler": "lamarzocco",
        "step_id": "user",
        "type": "form",
    }
    assert expected == result
    assert data == machine_info


@patch("custom_components.lamarzocco.config_flow.LaMarzocco")
@patch("custom_components.lamarzocco.LaMarzocco")
async def test_user_flow_works(mock_async_setup_entry, mock_class, hass):
    """Test config flow."""
    data = {
        "title": "buzz",
        "host": "1.2.3.4",
        "client_id": "aabbcc",
        "client_secret": "bbccdd",
        "username": "username",
        "password": "password",
    }
    instance = AsyncMock()
    instance.connect = AsyncMock(return_value=data)
    instance._current_status = {"POWER": 0}
    instance.current_status = {"POWER": 0}
    instance.serial_number = "12345"
    instance.model_name = "model_name"
    instance.machine_name = "machine_name"
    instance.register_callback = mock.Mock()
    mock_class.return_value = instance
    mock_async_setup_entry.return_value = instance
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            "host": "1.2.3.4",
            "client_id": "aabbcc",
            "client_secret": "bbccdd",
            "username": "username",
            "password": "password",
        },
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["title"] == "buzz"
    assert result["data"] == {
        "title": "buzz",
        "host": "1.2.3.4",
        "client_id": "aabbcc",
        "client_secret": "bbccdd",
        "username": "username",
        "password": "password",
    }
    print("async_setup: {}".format(mock_async_setup_entry.mock_calls))
    print("mock_class: {}".format(mock_class.mock_calls))


@patch("custom_components.lamarzocco.config_flow.LaMarzocco")
@patch("custom_components.lamarzocco.LaMarzocco")
async def test_zeroconf_flow_works(mock_async_setup_entry, mock_class, hass):
    """Test config flow."""
    data = {
        "title": "buzz",
        "host": "1.2.3.4",
        "client_id": "aabbcc",
        "client_secret": "bbccdd",
        "username": "username",
        "password": "password",
    }
    instance = AsyncMock()
    instance.connect = AsyncMock(return_value=data)
    instance._current_status = {"POWER": 0}
    instance.current_status = {"POWER": 0}
    instance.serial_number = "12345"
    instance.model_name = "model_name"
    instance.machine_name = "machine_name"
    instance.register_callback = mock.Mock()
    mock_class.return_value = instance
    mock_async_setup_entry.return_value = instance
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "zeroconf"},
        data={
            "host": bytes("1.2.3.4", "utf-8"),
            "properties": {
                "_raw": {
                    "type": bytes("machine_type", "utf8"),
                    "serial_number": bytes("aabbccdd", "utf8"),
                    "name": bytes("buzz", "utf8"),
                }
            },
        },
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "confirm"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            "client_id": "aabbcc",
            "client_secret": "bbccdd",
            "username": "username",
            "password": "password",
        },
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["title"] == "buzz"
    assert result["data"] == {
        "title": "buzz",
        "host": "1.2.3.4",
        "client_id": "aabbcc",
        "client_secret": "bbccdd",
        "username": "username",
        "password": "password",
    }
    print("async_setup: {}".format(mock_async_setup_entry.mock_calls))
    print("mock_class: {}".format(mock_class.mock_calls))


@patch(
    "custom_components.lamarzocco.config_flow.validate_input",
    side_effect=InvalidAuth,
)
@patch("custom_components.lamarzocco.config_flow.LaMarzocco")
@patch("custom_components.lamarzocco.LaMarzocco")
async def test_user_auth_fail(mock_async_setup_entry, mock_class, mock_func, hass):
    """Test config flow."""
    data = {
        "title": "buzz",
        "host": "1.2.3.4",
        "client_id": "aabbcc",
        "client_secret": "bbccdd",
        "username": "username",
        "password": "password",
    }
    instance = AsyncMock()
    instance.connect = AsyncMock(return_value=data)
    instance._current_status = {"POWER": 0}
    instance.current_status = {"POWER": 0}
    instance.serial_number = "12345"
    instance.model_name = "model_name"
    instance.machine_name = "machine_name"
    instance.register_callback = mock.Mock()
    mock_class.return_value = instance
    mock_async_setup_entry.return_value = instance
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            "host": "1.2.3.4",
            "client_id": "aabbcc",
            "client_secret": "bbccdd",
            "username": "username",
            "password": "password",
        },
    )

    print(result["errors"])
    assert result["errors"]["base"] == "invalid_auth"


@patch(
    "custom_components.lamarzocco.config_flow.validate_input",
    side_effect=InvalidAuth,
)
@patch("custom_components.lamarzocco.config_flow.LaMarzocco")
@patch("custom_components.lamarzocco.LaMarzocco")
async def test_zeroconf_auth_fail(mock_async_setup_entry, mock_class, mock_func, hass):
    """Test config flow."""
    data = {
        "title": "buzz",
        "host": "1.2.3.4",
        "client_id": "aabbcc",
        "client_secret": "bbccdd",
        "username": "username",
        "password": "password",
    }
    instance = AsyncMock()
    instance.connect = AsyncMock(return_value=data)
    instance._current_status = {"POWER": 0}
    instance.current_status = {"POWER": 0}
    instance.serial_number = "12345"
    instance.model_name = "model_name"
    instance.machine_name = "machine_name"
    instance.register_callback = mock.Mock()
    mock_class.return_value = instance
    mock_async_setup_entry.return_value = instance
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "zeroconf"},
        data={
            "host": bytes("1.2.3.4", "utf-8"),
            "properties": {
                "_raw": {
                    "type": bytes("machine_type", "utf8"),
                    "serial_number": bytes("aabbccdd", "utf8"),
                    "name": bytes("buzz", "utf8"),
                }
            },
        },
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "confirm"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            "client_id": "aabbcc",
            "client_secret": "bbccdd",
            "username": "username",
            "password": "password",
        },
    )

    print(result["errors"])
    assert result["errors"]["base"] == "invalid_auth"

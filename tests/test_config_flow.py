"""Tests for the config flow."""
from unittest import mock

from homeassistant import data_entry_flow, core
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
)
from pytest_homeassistant_custom_component.async_mock import patch

from custom_components.lamarzocco import config_flow
from custom_components.lamarzocco.config_flow import InvalidAuth, validate_input
from custom_components.lamarzocco.const import (
    CONF_MACHINE_NAME,
    CONF_SERIAL_NUMBER,
    CONF_MODEL_NAME,
    DOMAIN,
)


@patch("custom_components.lamarzocco.api.LaMarzocco.init_data")
@patch("custom_components.lamarzocco.api.LaMarzocco.connect")
@patch("custom_components.lamarzocco.api.LaMarzocco.close")
async def test_validate_input(mock_close, mock_connect, mock_init_data, hass):
    data = {
        "title": "buzz",
        "host": "1.2.3.4",
        "port": 1774,
        "machine_name": "machine_name",
        "serial_number": "1234567890",
        "client_id": "aabbcc",
        "client_secret": "bbccdd",
        "username": "username",
        "password": "password",
        "model_name": "model_name",
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


async def test_flow_zeroconf_init(hass):
    """Test the initialization of the form in the first step of the config flow."""
    data = {
        "title": "buzz",
    }
    with patch(
        "custom_components.lamarzocco.config_flow.validate_input"
    ) as mock_validate_input:
        machine_info = mock_validate_input.return_value = data
        result = await hass.config_entries.flow.async_init(
            config_flow.DOMAIN,
            context={"source": "zeroconf"},
            data={
                "host": bytes("1.2.3.4", "utf-8"),
                "port": 1774,
                "properties": {
                    "_raw": {
                        "type": bytes("machine_type", "utf8"),
                        "serial_number": bytes("aabbccdd", "utf8"),
                        "name": bytes("buzz", "utf8"),
                    }
                },
            },
        )
    expected = {
        "data_schema": config_flow.STEP_DISCOVERY_DATA_SCHEMA,
        "description_placeholders": None,
        "errors": {},
        "flow_id": mock.ANY,
        "handler": "lamarzocco",
        "step_id": "confirm",
        "type": "form",
    }
    assert expected == result
    assert data == machine_info


async def mock_func_validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect."""
    data = {
        "title": "buzz",
        CONF_HOST: "1.2.3.4",
        CONF_PORT: 1774,
        CONF_CLIENT_ID: "aabbcc",
        CONF_CLIENT_SECRET: "bbccdd",
        CONF_USERNAME: "username",
        CONF_PASSWORD: "password",
        CONF_SERIAL_NUMBER: "1234567890",
        CONF_MACHINE_NAME: "machine_name",
        CONF_MODEL_NAME: "model_name",
    }

    return data


@patch(
    "custom_components.lamarzocco.config_flow.validate_input", mock_func_validate_input
)
@patch("custom_components.lamarzocco.LaMarzocco.request_status")
async def test_user_flow_works(
    mock_request_status,
    hass,
):
    """Test config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_HOST: "1.2.3.4",
            CONF_CLIENT_ID: "aabbcc",
            CONF_CLIENT_SECRET: "bbccdd",
            CONF_USERNAME: "username",
            CONF_PASSWORD: "password",
        },
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["title"] == "buzz"
    assert result["data"] == {
        "title": "buzz",
        CONF_HOST: "1.2.3.4",
        CONF_PORT: 1774,
        CONF_CLIENT_ID: "aabbcc",
        CONF_CLIENT_SECRET: "bbccdd",
        CONF_USERNAME: "username",
        CONF_PASSWORD: "password",
        CONF_SERIAL_NUMBER: "1234567890",
        CONF_MACHINE_NAME: "machine_name",
        CONF_MODEL_NAME: "model_name",
    }


@patch(
    "custom_components.lamarzocco.config_flow.validate_input", mock_func_validate_input
)
@patch("custom_components.lamarzocco.LaMarzocco.request_status")
async def test_zeroconf_flow_works(mock_request_status, hass):
    """Test config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "zeroconf"},
        data={
            "host": bytes("1.2.3.4", "utf-8"),
            "port": 1774,
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
            CONF_CLIENT_ID: "aabbcc",
            CONF_CLIENT_SECRET: "bbccdd",
            CONF_USERNAME: "username",
            CONF_PASSWORD: "password",
        },
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["title"] == "buzz"
    assert result["data"] == {
        "title": "buzz",
        CONF_HOST: "1.2.3.4",
        CONF_PORT: 1774,
        CONF_CLIENT_ID: "aabbcc",
        CONF_CLIENT_SECRET: "bbccdd",
        CONF_USERNAME: "username",
        CONF_PASSWORD: "password",
        CONF_SERIAL_NUMBER: "1234567890",
        CONF_MACHINE_NAME: "machine_name",
        CONF_MODEL_NAME: "model_name",
    }


@patch(
    "custom_components.lamarzocco.config_flow.validate_input",
    side_effect=InvalidAuth,
)
@patch("custom_components.lamarzocco.LaMarzocco.request_status")
async def test_user_auth_fail(mock_request_status, mock_validate_input, hass):
    """Test config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_HOST: "1.2.3.4",
            CONF_CLIENT_ID: "aabbcc",
            CONF_CLIENT_SECRET: "bbccdd",
            CONF_USERNAME: "username",
            CONF_PASSWORD: "password",
        },
    )

    print(result["errors"])
    assert result["errors"]["base"] == "invalid_auth"


@patch(
    "custom_components.lamarzocco.config_flow.validate_input",
    side_effect=InvalidAuth,
)
@patch("custom_components.lamarzocco.LaMarzocco.request_status")
async def test_zeroconf_auth_fail(mock_request_status, mock_validate_input, hass):
    """Test config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "zeroconf"},
        data={
            "host": bytes("1.2.3.4", "utf-8"),
            "port": bytes("1774", "utf-8"),
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

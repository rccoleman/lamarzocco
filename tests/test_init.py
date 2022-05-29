"""Test La Marzocco component setup."""
from homeassistant.setup import async_setup_component

from custom_components.lamarzocco.const import DOMAIN


async def test_async_setup(hass, enable_custom_integrations):
    """Test the component gets setup."""
    assert await async_setup_component(hass, DOMAIN, {}) is True

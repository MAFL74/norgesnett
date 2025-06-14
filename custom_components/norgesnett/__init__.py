import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.debug("Setting up Norgesnett entry")

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.debug("Unloading Norgesnett entry")

    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.info("Successfully unloaded Norgesnett integration")
    
    return unload_ok

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.info("Options updated for Norgesnett integration")

    new_api_key = entry.options.get(CONF_API_KEY)
    if new_api_key:
        hass.data[DOMAIN][entry.entry_id][CONF_API_KEY] = new_api_key

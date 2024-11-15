import logging
import aiohttp
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity, UpdateFailed
from .const import DOMAIN, CONF_API_KEY, CONF_METERING_POINT_ID, CONF_UPDATE_INTERVAL, CONF_API_URL, DEFAULT_API_URL, DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the sensor using the configuration entry."""
    api_key = entry.data[CONF_API_KEY]
    metering_point_id = entry.data[CONF_METERING_POINT_ID]
    update_interval = entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
    api_url = entry.data.get(CONF_API_URL, DEFAULT_API_URL)

    coordinator = NorgesnettDataCoordinator(
        hass, api_key, metering_point_id, api_url, update_interval
    )

    await coordinator.async_config_entry_first_refresh()
    async_add_entities([NorgesnettTariffSensor(coordinator)], True)


class NorgesnettDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Norgesnett API."""

    def __init__(self, hass, api_key, metering_point_id, api_url, update_interval):
        self.api_key = api_key
        self.metering_point_id = metering_point_id
        self.api_url = api_url
        self.headers = {"X-API-Key": self.api_key}
        self.payload = {"meteringPointIds": [self.metering_point_id]}

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=update_interval)
        )

    async def _async_update_data(self):
        """Fetch data from the API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=self.headers, json=self.payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    _LOGGER.debug("Fetched data: %s", data)
                    return data
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")


class NorgesnettTariffSensor(CoordinatorEntity, SensorEntity):
    """Sensor to represent the Norgesnett tariff data."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._name = "Norgesnett Tariff"
        self._unique_id = f"norgesnett_{coordinator.metering_point_id}"

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def state(self):
        """Return the current energy price for private customers."""
        if not self.coordinator.data:
            return None

        # Hent energipriser for PRIVATE kunder
        energy_prices = self.coordinator.data.get("gridTariffCollections", [{}])[0] \
            .get("gridTariff", {}).get("tariffPrice", {}).get("priceInfo", {}).get("energyPrices", [])
        private_price = next(
            (price for price in energy_prices if price.get("customerType") == "PRIVATE" and price.get("level") == "CHEAP"),
            None
        )
        return private_price.get("total") if private_price else "Unknown"

    @property
    def extra_state_attributes(self):
        """Return additional attributes from the API response."""
        if not self.coordinator.data:
            return {}

        tariff_data = self.coordinator.data.get("gridTariffCollections", [{}])[0].get("gridTariff", {})
        price_info = tariff_data.get("tariffPrice", {}).get("priceInfo", {})
        energy_prices = price_info.get("energyPrices", [])
        fixed_prices = price_info.get("fixedPrices", [{}])[0].get("priceLevels", [{}])

        # Filtrer ut priser for PRIVATE kunder
        private_price = next(
            (price for price in energy_prices if price.get("customerType") == "PRIVATE" and price.get("level") == "CHEAP"),
            {}
        )

        # Hent kapasitetsledd detaljer
        kapasitetsledd_price = fixed_prices[0] if fixed_prices else {}

        # Bruk 'monthlyTotal' inkludert moms hvis tilgjengelig
        kapasitetsledd_total = kapasitetsledd_price.get("monthlyTotal")
        kapasitetsledd_total_with_tax = kapasitetsledd_price.get("monthlyTotal") + kapasitetsledd_price.get("monthlyTaxes", 0)

        attributes = {
            # Tariff detaljer
            "tariff_id": tariff_data.get("id"),
            "tariff_key": tariff_data.get("tariffType", {}).get("tariffKey"),
            "product": tariff_data.get("tariffType", {}).get("product"),
            "company_name": tariff_data.get("tariffType", {}).get("companyName"),
            "company_org_no": tariff_data.get("tariffType", {}).get("companyOrgNo"),
            "title": tariff_data.get("tariffType", {}).get("title"),
            "last_updated": tariff_data.get("tariffType", {}).get("lastUpdated"),
            "resolution": tariff_data.get("tariffType", {}).get("resolution"),
            "description": tariff_data.get("tariffType", {}).get("description"),

            # Energy price details for private customers
            "energy_id": private_price.get("id"),
            "total": private_price.get("total"),
            "total_ex_vat": private_price.get("totalExVat"),
            "taxes": private_price.get("taxes"),
            "currency": private_price.get("currency"),
            "monetary_unit": private_price.get("monetaryUnitOfMeasure"),

            # Kapasitetsledd detaljer
            "kapasitetsledd_id": kapasitetsledd_price.get("id"),
            "kapasitetsledd_value_min": kapasitetsledd_price.get("valueMin"),
            "kapasitetsledd_value_max": kapasitetsledd_price.get("valueMax"),
            "kapasitetsledd_monthly_total": kapasitetsledd_total,
            "kapasitetsledd_monthly_with_tax": kapasitetsledd_total_with_tax,
            "kapasitetsledd_currency": kapasitetsledd_price.get("currency"),
            "kapasitetsledd_unit": kapasitetsledd_price.get("monthlyUnitOfMeasure")
        }

        _LOGGER.debug("Sensor attributes: %s", attributes)
        return attributes

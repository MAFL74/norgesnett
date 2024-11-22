
import logging
import aiohttp
import datetime
import re
from datetime import datetime, timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity, UpdateFailed
from .const import DOMAIN, CONF_API_KEY, CONF_METERING_POINT_ID, CONF_UPDATE_INTERVAL, CONF_API_URL, DEFAULT_API_URL, DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)
last_api_update_time = None

# Kapasitetstrinn-tabell basert på valueMin
TRINN_TABELL = {
    "0": 1,
    "2": 2,
    "5": 3,
    "10": 4,
    "15": 5,
    "20": 6,
    "25": 7,
    "50": 8,
    "75": 9,
    "100": 10
}

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
        self.last_api_update_time = None

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
                    self.last_api_update_time = datetime.now()
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
        """Return the current energy price based on time."""
        if not self.coordinator.data:
            return None

        energy_prices = self.coordinator.data.get("gridTariffCollections", [{}])[0] \
            .get("gridTariff", {}).get("tariffPrice", {}).get("priceInfo", {}).get("energyPrices", [])

        cheap_price = next(
            (price for price in energy_prices if price.get("customerType") == "PRIVATE" and price.get("level") == "CHEAP"),
            None
        )
        normal_price = next(
            (price for price in energy_prices if price.get("customerType") == "PRIVATE" and price.get("level") == "NORMAL"),
            None
        )

        current_time = datetime.now().time()
        cheap_start = datetime.strptime("22:00", "%H:%M").time()
        cheap_end = datetime.strptime("06:00", "%H:%M").time()

        if (current_time >= cheap_start) or (current_time < cheap_end):
            return cheap_price.get("total") if cheap_price else "Unknown"
        else:
            return normal_price.get("total") if normal_price else "Unknown"

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}

        attributes = {}
        tariff_data = self.coordinator.data.get("gridTariffCollections", [{}])[0].get("gridTariff", {})
        price_info = tariff_data.get("tariffPrice", {}).get("priceInfo", {})
        energy_prices = price_info.get("energyPrices", [])
        fixed_prices = price_info.get("fixedPrices", [])
        metering_points = self.coordinator.data.get("meteringPointsAndPriceLevels", [])

        # Filtrer ut CHEAP_PRIVATE og NORMAL_PRIVATE priser
        cheap_price = next(
            (price for price in energy_prices if price.get("customerType") == "PRIVATE" and price.get("level") == "CHEAP"),
            {}
        )
        normal_price = next(
            (price for price in energy_prices if price.get("customerType") == "PRIVATE" and price.get("level") == "NORMAL"),
            {}
        )

        if len(fixed_prices) > 1:  # Sjekker at dataset nr. 2 finnes
            second_fixed_price = fixed_prices[1]  # Hent dataset nr. 2
            price_levels = second_fixed_price.get("priceLevels", [])
            _LOGGER.debug("Price levels (second dataset): %s", price_levels)

            if price_levels:
                # Hent det første priceLevel i dataset nr. 2
                capacity_details = price_levels[0]
                _LOGGER.debug("Capacity details (from second dataset): %s", capacity_details)

                # Prøv å hente valueMin og matche det med TRINN_TABELL
                value_min = capacity_details.get("valueMin")
                if value_min is not None:
                    value_min_str = str(int(value_min))
                    capacity_level_id = TRINN_TABELL.get(value_min_str)
        else:
            _LOGGER.warning("Fixed prices do not contain a second dataset.")

        # Legg til kapasitetsledd og attributter
        attributes.update({
            "tariff_id": tariff_data.get("id"),
            "tariff_key": tariff_data.get("tariffType", {}).get("tariffKey"),
            "product": tariff_data.get("tariffType", {}).get("product"),
            "company_name": tariff_data.get("tariffType", {}).get("companyName"),
            "company_org_no": tariff_data.get("tariffType", {}).get("companyOrgNo"),
            "title": tariff_data.get("tariffType", {}).get("title"),
            "last_updated": tariff_data.get("tariffType", {}).get("lastUpdated"),
            "resolution": tariff_data.get("tariffType", {}).get("resolution"),
            "cheap_energy_id": cheap_price.get("id"),
            "cheap_total": cheap_price.get("total"),
            "cheap_total_ex_vat": cheap_price.get("totalExVat"),
            "cheap_taxes": cheap_price.get("taxes"),
            "normal_energy_id": normal_price.get("id"),
            "normal_total": normal_price.get("total"),
            "normal_total_ex_vat": normal_price.get("totalExVat"),
            "normal_taxes": normal_price.get("taxes"),
            "kapasitetsledd_value_min": capacity_details.get("valueMin"),
            "kapasitetsledd_value_max": capacity_details.get("valueMax"),
            "kapasitetsledd_next_down": capacity_details.get("nextIdDown"),
            "kapasitetsledd_next_up": capacity_details.get("nextIdUp"),
            "kapasitetsledd_unit": capacity_details.get("valueUnitOfMeasure"),
            "kapasitetsledd_monthly_total": capacity_details.get("monthlyTotal"),
            "kapasitetsledd_monthly_ex_vat": capacity_details.get("monthlyTotalExVat"),
            "kapasitetsledd_monthly_taxes": capacity_details.get("monthlyTaxes"),
            "kapasitetsledd_currency": capacity_details.get("currency"),
            "kapasitetsledd_unit_measure": capacity_details.get("monthlyUnitOfMeasure"),
            "kapasitetsledd_trinn": capacity_level_id,
            "last_api_update": self.coordinator.last_api_update_time.strftime('%Y-%m-%d %H:%M:%S') if self.coordinator.last_api_update_time else "Unknown"
        })

        _LOGGER.debug("Final attributes: %s", attributes)

        return attributes

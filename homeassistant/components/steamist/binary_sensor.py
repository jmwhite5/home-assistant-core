"""Support for Steamist binary sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from aiosteamist import SteamistStatus
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SteamistDataUpdateCoordinator
from .entity import SteamistEntity

_KEY_IN_USE = "in_use"


@dataclass
class SteamistBinarySensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[SteamistStatus], bool | None]


@dataclass
class SteamistBinarySensorEntityDescription(
    BinarySensorEntityDescription, SteamistBinarySensorEntityDescriptionMixin
):
    """Describes a Steamist binary sensor entity."""


BINARY_SENSOR = (
    SteamistBinarySensorEntityDescription(
        key=_KEY_IN_USE,
        name="In Use",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda status: status.active,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors."""
    coordinator: SteamistDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    entities = [
        SteamistBinarySensorEntity(coordinator, config_entry, description)
        for description in BINARY_SENSOR
    ]
    async_add_entities(entities)


class SteamistBinarySensorEntity(SteamistEntity, BinarySensorEntity):
    """Representation of a Steamist binary sensor entity."""

    entity_description: SteamistBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: SteamistDataUpdateCoordinator,
        entry: ConfigEntry,
        description: SteamistBinarySensorEntityDescription,
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator, entry, description)

    @property
    def is_on(self) -> bool | None:
        """Calculate the binary sensor value from the entity description."""
        return self.entity_description.value_fn(self._status)

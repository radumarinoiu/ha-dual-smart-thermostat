from abc import ABC, abstractmethod
import logging

from homeassistant.components.climate import HVACAction, HVACMode
from homeassistant.core import CALLBACK_TYPE, Context, HomeAssistant, callback

from custom_components.dual_smart_thermostat.hvac_action_reason.hvac_action_reason import (
    HVACActionReason,
)

_LOGGER = logging.getLogger(__name__)


class ControlableHVACDevice(ABC):

    hsss: HomeAssistant
    entity_id: str
    hvac_modes: list[HVACMode]

    # Hold list for functions to call on remove.
    _on_remove: list[CALLBACK_TYPE] | None = None

    _context = Context | None
    _hvac_mode: HVACMode
    _HVACActionReason: HVACActionReason

    @abstractmethod
    async def async_control_hvac(self, time=None, force=False):
        pass

    @abstractmethod
    def get_device_ids(self) -> list[str]:
        pass

    @property
    def hvac_mode(self) -> HVACMode:
        return self._hvac_mode

    @property
    def hvac_action(self) -> HVACAction:
        """concrete implementations should return the current hvac action of the device."""
        pass

    @hvac_mode.setter
    def hvac_mode(self, hvac_mode: HVACMode):
        self._hvac_mode = hvac_mode

    async def async_set_hvac_mode(self, hvac_mode: HVACMode):
        _LOGGER.info("Setting hvac mode to %s of %s", hvac_mode, self.hvac_modes)
        if hvac_mode in self.hvac_modes:
            self._hvac_mode = hvac_mode
        else:
            self._hvac_mode = HVACMode.OFF

        if self._hvac_mode == HVACMode.OFF:
            await self.async_turn_off()
            self._HVACActionReason = HVACActionReason.NONE
        else:
            await self.async_control_hvac(self, force=True)

        _LOGGER.info("Hvac mode set to %s", self._hvac_mode)

    def async_on_remove(self, func: CALLBACK_TYPE) -> None:
        """Add a function to call when entity is removed or not added."""
        if self._on_remove is None:
            self._on_remove = []
        self._on_remove.append(func)

    @callback
    def call_on_remove_callbacks(self) -> None:
        """Call callbacks registered by async_on_remove."""
        if self._on_remove is None:
            return
        while self._on_remove:
            self._on_remove.pop()()

    @abstractmethod
    def set_context(self, context: Context):
        pass

    @abstractmethod
    def on_startup(self):
        pass

    @abstractmethod
    async def _async_check_device_initial_state(self) -> None:
        pass

    @abstractmethod
    async def async_turn_on(self):
        """Concrete implementations should turn the device on."""
        pass

    @abstractmethod
    async def async_turn_off(self):
        pass

    @abstractmethod
    def is_active(self) -> bool:
        pass

    @property
    def HVACActionReason(self) -> HVACActionReason:
        return self._HVACActionReason

    @HVACActionReason.setter
    def HVACActionReason(self, HVACActionReason: HVACActionReason):
        self._HVACActionReason = HVACActionReason

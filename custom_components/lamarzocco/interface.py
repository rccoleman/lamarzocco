
import logging

from lmdirect import LMDirect
from lmcloud import LMCloud

from .const import *
from lmdirect.const import HOST, SERIAL_NUMBER
from homeassistant.components import bluetooth

_LOGGER = logging.getLogger(__name__)


class LMInterface:
    '''
    Class to interface between lmdirect and lmcloud
    '''

    @property
    def model_name(self):
        """Return model name."""
        return self._model_name
  
    @property
    def machine_info(self):
        return self._machine_info
  
    @property
    def machine_name(self):
        """Return the name of the machine."""
        return self.machine_info[MACHINE_NAME]

    @property
    def serial_number(self):
        """Return serial number."""
        return self.machine_info[SERIAL_NUMBER]
    
    @property
    def firmware_version(self):
        if self.model_name in LM_CLOUD_MODELS:
            return self._lm_cloud.firmware_version
        else:
            return self._lm_direct.firmware_version
        
    @property
    def current_status(self):
        if self.model_name in LM_CLOUD_MODELS:
            return self._lm_cloud.current_status
        else:
            return self._lm_direct.current_status
        
    '''
    Initialization
    '''
    def __init__(self):
        self._lm_direct = None
        self._lm_cloud = None
        self._model_name = None
        self._machine_info = None
        self._callback_list = []
        self.hass = None

    @classmethod
    async def create(cls, config):
        self = cls()
        await self.init_lm_client(config)
        return self

    async def init_lm_client(self, hass, config):
        self.hass = hass
        self._lm_cloud = await LMCloud.create(config)
        self._model_name = self._lm_cloud.model_name
        self._machine_info = self._lm_cloud.machine_info

        _LOGGER.debug(f"Model name: {self._model_name}")

        if self._model_name in LM_CLOUD_MODELS:
            _LOGGER.debug("Initializing lmcloud...")

            init_bt = False
            bt_scanner = None
            # check if there are any bluetooth adapters to use
            count = bluetooth.async_scanner_count(hass, connectable=True)
            if count > 0:
                _LOGGER.debug("Found bluetooth adapters, initializing with bluetooth.")
                init_bt = True
                bt_scanner = bluetooth.async_get_scanner(hass)

            self._lm_cloud = await LMCloud.create_with_local_api(
                config,
                config[HOST],
                port=DEFAULT_PORT_CLOUD,
                use_bluetooth=init_bt,
                bluetooth_scanner=bt_scanner)
        else:
            _LOGGER.debug("Initializing lmdirect...")
            self._lm_direct = LMDirect.__init__(config)

    async def init_data(self, hass):
        """Register the callback to receive updates."""
        self.register_callback(self.update_callback)

        self._run = True

        """Start polling for status."""
        self._polling_task = hass.loop.create_task(
            self.fetch_data(), name="Polling Loop"
        )

        """Reap the results and any any exceptions."""
        self._poll_reaper_task = hass.loop.create_task(
            self.poll_reaper(), name="Poll Reaper"
        )

    '''
    interface methods
    '''
    async def connect(self):
        if self.model_name in LM_CLOUD_MODELS:
            pass
        else:
            self._machine_info = await self._lm_direct.connect()

        return self.machine_info

    async def close(self):
        if self.model_name in LM_CLOUD_MODELS:
            pass
        else:
            await self._lm_direct.close()

    def register_callback(self, callback):
        """Register callback for updates."""
        if callable(callback):
            self._callback_list.append(callback)

    async def request_status(self):
        if self.model_name in LM_CLOUD_MODELS:
            await self._lm_cloud.update_local_machine_status()
        else:
            await self._lm_direct.request_status()

    async def set_power(self, power_on):
        if self.model_name in LM_CLOUD_MODELS:
            await self.get_hass_bt_client()
            await self._lm_cloud.set_power(power_on)
        else:
            await self._lm_direct.set_power(power_on)

    async def set_steam_boiler_enable(self, enable):
        if self.model_name in LM_CLOUD_MODELS:
            await self.get_hass_bt_client()
            await self._lm_cloud.set_steam(enable)
        else:
            await self._lm_direct.set_power(enable)

    async def set_preinfusion_enable(self, enable):
        if self.model_name in LM_CLOUD_MODELS:
            await self._lm_cloud.set_preinfusion(enable)
        else:
            await self._lm_direct.set_preinfusion_enable(enable)

    async def set_prebrewing_enable(self, enable):
        if self.model_name in LM_CLOUD_MODELS:
            await self._lm_cloud.set_prebrew(enable)
        else:
            await self._lm_direct.set_prebrewing_enable(enable)

    async def set_auto_on_off_global(self, enable):
        if self.model_name in LM_CLOUD_MODELS:
            await self._lm_cloud.configure_schedule(enable, await self._lm_cloud.get_schedule())
        else:
            await self._lm_direct.set_auto_on_off_global(enable)

    async def set_auto_on_off_enable(self, day_of_week, enable):
        if self.model_name in LM_CLOUD_MODELS:
            await self._lm_cloud.set_auto_on_off_enable(day_of_week, enable)
        else:
            await self._lm_direct.set_auto_on_off_enable(day_of_week, enable)

    async def set_auto_on_off_times(self, day_of_week, hour_on, minute_on, hour_off, minute_off):
        if self.model_name in LM_CLOUD_MODELS:
            await self._lm_cloud.set_auto_on_off(day_of_week, hour_on, minute_on, hour_off, minute_off)
        else:
            await self._lm_direct.set_auto_on_off_times(day_of_week, hour_on, minute_on, hour_off, minute_off)

    async def set_dose(self, key, pulses):
        if self.model_name in LM_CLOUD_MODELS:
            pass
        else:
            await self._lm_direct.set_dose(key, pulses)

    async def set_dose_hot_water(self, seconds):
        if self.model_name in LM_CLOUD_MODELS:
            pass
        else:
            await self._lm_direct.set_dose_hot_water(seconds)

    async def set_prebrew_times(self, key, seconds_on, seconds_off):
        if self.model_name in LM_CLOUD_MODELS:
            await self._lm_cloud.configure_prebrew(prebrewOnTime=seconds_on * 1000, prebrewOffTime=seconds_off * 1000)
        else:
            await self._lm_direct.set_prebrew_times(key, seconds_on, seconds_off)

    async def set_preinfusion_time(self, key, seconds):
        if self.model_name in LM_CLOUD_MODELS:
            await self._lm_cloud.configure_prebrew(prebrewOnTime=0, prebrewOffTime=seconds * 1000)
        else:
            await self._lm_direct.set_preinfusion_time(key, seconds)

    async def set_start_backflush(self):
        if self.model_name in LM_CLOUD_MODELS:
            await self._lm_cloud.start_backflush()
        else:
            await self._lm_direct.set_start_backflush()

    async def set_coffee_temp(self, temp):
        if self.model_name in LM_CLOUD_MODELS:
            await self.get_hass_bt_client()
            await self._lm_cloud.set_coffee_temp(temp)
        else:
            await self._lm_direct.set_coffee_temp(temp)

    async def set_steam_temp(self, temp):
        if self.model_name in LM_CLOUD_MODELS:
            possible_temps = [126, 128, 131]
            temp = min(possible_temps, key=lambda x: abs(x - temp))
            await self.get_hass_bt_client()
            await self._lm_cloud.set_steam_temp(temp)
        else:
            await self._lm_direct.set_steam_temp(temp)

    async def get_hass_bt_client(self):
        # according to HA best practices, we should not reuse the same client
        # get a new BLE device from hass and init a new Bleak Client with it
        if self._lm_cloud._lm_bluetooth:
            ble_device = bluetooth.async_ble_device_from_address(self.hass,
                                                                 self._lm_cloud._lm_bluetooth._address,
                                                                 connectable=True)
            await self._lm_cloud._lm_bluetooth.new_bleak_client_from_ble_device(ble_device)


import logging

from lmdirect import LMDirect
from lmcloud import LMCloud

from .const import *
from lmdirect.const import HOST, SERIAL_NUMBER

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
            return self.machine_info
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

    @classmethod
    async def create(cls, config):
        self = cls()
        await self.init_lm_client(config)
        return self

    async def init_lm_client(self, config):
        self._lm_cloud = await LMCloud.create(config)
        self._model_name = self._lm_cloud.model_name
        self._machine_info = self._lm_cloud.machine_info

        _LOGGER.info(f"Model name: {self._model_name}")

        if self._model_name in LM_CLOUD_MODELS:
            _LOGGER.info("Initializing lmcloud...")
            self._lm_cloud = await LMCloud.create_with_local_api(config, config[HOST], port=DEFAULT_PORT_CLOUD)
        else:
            _LOGGER.info("Initializing lmdirect...")
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
            await self._lm_cloud.get_status()
        else:
            await self._lm_direct.request_status()

    async def set_power(self, power_on):
        if self.model_name in LM_CLOUD_MODELS:
            await self._lm_cloud.set_power(power_on)
        else:
            await self._lm_direct.set_power(power_on)

    async def set_steam_boiler_enable(self, enable):
        if self.model_name in LM_CLOUD_MODELS:
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
            await self._lm_cloud.configure_schedule(enable, self._lm_cloud.get_schedule())
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
            await self._lm_cloud.configure_prebrew(prebrewOnTime=seconds_on, prebrewOffTime=seconds_off)
        else:
            await self._lm_direct.set_prebrew_times(key, seconds_on, seconds_off)

    async def set_preinfusion_time(self, key, seconds):
        if self.model_name in LM_CLOUD_MODELS:
            # TODO
            pass
        else:
            await self._lm_direct.set_preinfusion_time(key, seconds)

    async def set_start_backflush(self):
        if self.model_name in LM_CLOUD_MODELS:
            await self._lm_cloud.start_backflush()
        else:
            await self._lm_direct.set_start_backflush()

    async def set_coffee_temp(self, temp):
        if self.model_name in LM_CLOUD_MODELS:
            possible_temps = [126, 128, 131]
            temp = min(possible_temps, key=lambda x: abs(x - temp))
            await self._lm_cloud.set_coffee_temp(temp)
        else:
            await self._lm_direct.set_coffee_temp(temp)

    async def set_steam_temp(self, temp):
        if self.model_name in LM_CLOUD_MODELS:

            await self._lm_cloud.set_steam_temp(temp)
        else:
            await self._lm_direct.set_steam_temp(temp)

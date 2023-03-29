
import logging

from lmdirect import LMDirect
from lmcloud import LMCloud

from .const import *
from lmdirect.const import HOST, SERIAL_NUMBER

_LOGGER = logging.getLogger(__name__)

'''
Class to interface between lmdirect and lmcloud
'''


class LMInterface:

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

    def __init__(self):
        self._lm_direct = None
        self._lm_cloud = None
        self._model_name = None
        self._machine_info = None
        self._callback_list = []

    @classmethod
    async def create(cls, hass, config):
        self = cls()
        await self.init_lm_client(hass, config)
        return self

    async def init_lm_client(self, hass, config):
        self._lm_cloud = await LMCloud.create(config)
        self._model_name = self._lm_cloud.model_name
        self._machine_info = self._lm_cloud.machine_info

        _LOGGER.info(f"Model name: {self._model_name}")

        if self._model_name in LM_CLOUD_MODELS:
            _LOGGER.info("Initializing lmcloud...")
            self._lm_cloud = await LMCloud.create_with_local_api(config, config[HOST], port=DEFAULT_PORT_CLOUD)
            hass.async_add_executor_job(self._lm_cloud.get_status)
        else:
            _LOGGER.info("Initializing lmdirect...")
            self._lm_direct = LMDirect.__init__(config)

    async def init_data(self, hass):
        """Register the callback to receive updates."""
        self.register_callback(self.update_callback)

        self._run = True

        """Start polling for status."""
        self._polling_task = hass.loop.create_task(
            self.fetch_data(hass), name="Polling Loop"
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

    async def request_status(self, hass):
        if self.model_name in LM_CLOUD_MODELS:
            await hass.async_add_executor_job(self._lm_cloud.get_status)
        else:
            await self._lm_direct.request_status()

    async def set_power(self, power_on):
        if self.model_name in LM_CLOUD_MODELS:
            mode = "ON" if power_on else "STANDBY"
            await self._lm_cloud.set_power(mode)
        else:
            await self._lm_direct.set_power(power_on)

    async def set_auto_on_off_enable(self, day_of_week, enable):
        if self.model_name in LM_CLOUD_MODELS:
            schedule = self._lm_cloud.get_schedule()
            idx = [index for (index, d) in enumerate(schedule) if d["day"] == day_of_week.upper()][0]
            schedule[idx]["enable"] = True
            await self._lm_cloud.configure_schedule(True, schedule)
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
            pass
        else:
            await self._lm_direct.set_preinfusion_time(key, seconds)

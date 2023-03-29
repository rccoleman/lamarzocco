
import logging

from lmdirect import LMDirect
from lmcloud import LMCloud

from .const import *
from lmdirect.const import HOST

_LOGGER = logging.getLogger(__name__)

'''
Class to interface between lmdirect and lmcloud
'''


class LMInterface:

    @property
    def model_name(self):
        return self._model_name

    def __init__(self):
        self._lm_direct = None
        self._lm_cloud = None
        self._model_name = None

    @classmethod
    async def create(cls, config):
        self = cls()
        self._lm_cloud = await LMCloud.create(config)
        self._model_name = self._lm_cloud.model_name

        _LOGGER.debug(f"Model name: {self._model_name}")

        if self._model_name in LM_CLOUD_MODELS:
            _LOGGER.debug("Initializing lmcloud...")
            self._lm_cloud = await LMCloud.create_with_local_api(config, config[HOST], port=DEFAULT_PORT_CLOUD)
        else:
            _LOGGER.debug("Initializing lmdirect...")
            self._lm_direct = LMDirect.__init__(config)

    async def init_data(self, hass):
        if self.model_name in LM_CLOUD_MODELS:
            pass
        else:
            """Initialize the underlying lmdirect package."""

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
            return self._lm_cloud.machine_info
        else:
            return await self._lm_direct.connect()

    async def close(self):
        if self.model_name in LM_CLOUD_MODELS:
            pass
        else:
            await self._lm_direct.close()

    async def request_status(self):
        if self.model_name in LM_CLOUD_MODELS:
            await self._lm_cloud.get_status()
        else:
            await self._lm_direct.request_status()

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
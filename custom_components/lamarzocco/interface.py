
from LMDirect import LMDirect
from LMCloud import LMCloud

'''
Class to interface between lmdirect and lmcloud
'''
class LMInterface:

@property
def model_name(self):
    return self._model_name

lm_direct = None
lm_cloud = None

'''
Get model name during initialization
'''
def __init__(self, creds):
    pass

async def connect():
    if self.model_name == MODEL_LMU:
        pass
    else:
        lm_direct.connect()

async def request_status():
    if self.model_name == MODEL_LMU:
        lm_cloud.get_status()
    else:
        lm_direct.request_status()

async def set_auto_on_off_times(self, day_of_week, hour_on, minute_on, hour_off, minute_off):
    if self.model_name == MODEL_LMU:
        lm_cloud.set_auto_on_off(day_of_week, hour_on, minute_on, hour_off, minute_off)
    else:
        lm_direct.set_auto_on_off_times(day_of_week, hour_on, minute_on, hour_off, minute_off)




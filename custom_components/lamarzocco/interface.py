
import lmdirect
import lmcloud

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
        pass
    else:
        lm_direct.request_status()



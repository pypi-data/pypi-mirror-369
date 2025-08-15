from typing import Dict
from .redisClient import RedisClient
from .baseObj import BaseObj
from .singleton import Singleton

class EventsStream(metaclass=Singleton):
    def __init__(self):
        self.db = RedisClient()

    def publishObject(self, channelId: str, dataObj : BaseObj):
        self.db.pubObjToChannel(dataObj=dataObj, channelId=channelId)

    def getObjsFromChannel(self, channelId : str, cls: BaseObj, timeout = 5000) -> Dict[str,BaseObj]:
        return self.db.subGetObjFromChannel(cls=cls, channelId=channelId, timeout=timeout)

    def removeFromChannel(self, channelId : str, objId: str):
        return self.db.removeFromChannel(channelId=channelId, messageId=objId)
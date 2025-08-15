from typing import List
from dynamicObjInfra.redisClient import RedisClient
from dynamicObjInfra.baseObj import BaseObj
from dynamicObjInfra.utils.env import EnvConfig, initialize
from pydantic import create_model, Field

def configureEnv():

    dbhost = "127.0.0.1"
    dbport = 27017
    chatDbName = "claro_kp"
    redisHost = "127.0.0.1"
    redisPort = 6379

    dynObjConf = EnvConfig(db_host=dbhost, db_port=dbport, db_name=chatDbName, redis_host=redisHost, redis_port=redisPort, db_useRedisCache=True)
    initialize(dynObjConf)

def createChatTags():
    return create_model(
        "ChatTags",
         userInsights=(List[str], Field(..., description="some user insights description")),
         title=(str, Field(..., description="some title description")))

class A(BaseObj):
    dbCollectionName = "test"
    id :str
    name: str
    userInsights : List[str] = []
    title : str = ""



ChatTags =createChatTags()
ctIns = ChatTags(userInsights=["1", "2"], title="test")

aIns = A(id="1", name="test")
aIns.updateFromBaseModel(ctIns)

print(aIns.toReadableText())
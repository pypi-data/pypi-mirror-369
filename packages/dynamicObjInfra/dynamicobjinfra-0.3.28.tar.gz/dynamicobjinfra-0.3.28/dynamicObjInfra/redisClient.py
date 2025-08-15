import traceback
from typing import Dict, List
from .utils.env import get_config, get_ttl_by_type
from .doi_logProvider import logger
import redis
from redis.commands.json.path import Path
from redis.commands.search.field import TagField
from redis.commands.search.query import Query
from .baseObj import BaseObj
from .singleton import Singleton
from .enums import TTL_Type
from .validators import validate_base_obj_cls, validate_base_obj_instance

class RedisClient(metaclass=Singleton):
    def __init__(self,  host: str = None, port: int = None):
        self.redisInstance = None
        self.channelLastMessage = {}

    def getDatabase(self):
        if (self.redisInstance is None):
            host = get_config().redis_host
            port = get_config().redis_port

            self.redisInstance = redis.Redis(host=host, port=port, db=0, decode_responses=True)

        return self.redisInstance

    def createIndexForClass(self, cls):
        """
        Create a RediSearch JSON index for the given class based on its indexed fields.
        Expects the class to have a dbCollectionName and to be marked with @redis_indexed.
        """
        from redis.commands.search.field import TextField, NumericField
        from redis.commands.search.indexDefinition import IndexDefinition, IndexType

        index_name = f"idx:{cls.dbCollectionName}"
        prefix = f"{cls.dbCollectionName}:"

        index_fields = cls.get_redis_index_fields()  # uses the helper defined in BaseObj
        fields = []
        for field_name, field_type in index_fields.items():
            json_path = f"$.{field_name}"
            if field_type == "tag":
                fields.append(TagField(f"$.{field_name}", as_name=field_name))
            elif field_type == "numeric":
                fields.append(NumericField(json_path, as_name=field_name))
            else:
                fields.append(TextField(json_path, as_name=field_name))
        
        definition = IndexDefinition(prefix=[prefix], index_type=IndexType.JSON)
        try:
            self.getDatabase().ft(index_name).create_index(fields=fields, definition=definition)
            print(f"Index '{index_name}' created with prefix '{prefix}' and fields: {index_fields}")
        except Exception as e:
            print(f"Index '{index_name}' creation might have already been done: {e}")

    @validate_base_obj_instance
    def saveToDB (self, dataObj : BaseObj,objId: str):
        db = self.getDatabase()

        try: 
            db.json().set(f"{dataObj.dbCollectionName}:{objId}", '.', dataObj.toJSON())
        except Exception as e:
            logger().error(f'RedisClient.saveToDB raised an unhandled Exception {str(e)}\n trace is {traceback.format_exc()}')
            return

    @validate_base_obj_instance
    def saveTempToDB (self, dataObj : BaseObj, objId: str, ttlType: TTL_Type = TTL_Type.LONG):
        if (dataObj.dbCollectionName == ""):
            logger().error(f'RedisClient.saveTempToDB called for Class {dataObj.__name__} but does not have dbCollectionName defined.')
            raise Exception(f'RedisClient.saveTempToDB called for Class {dataObj.__name__} but does not have dbCollectionName defined.')

        try: 
            self.saveToDB(objId=objId,dataObj=dataObj)

            objTTL = get_ttl_by_type(ttlType=ttlType)

            self.getDatabase().expire(f"{dataObj.dbCollectionName}:{objId}", objTTL)
        except Exception as e:
            logger().error(f'RedisClient.saveTempToDB raised an unhandled Exception {str(e)}\n trace is {traceback.format_exc()}')
            return


    # get all ids for this cls
    @validate_base_obj_cls
    def loadIdsFromDB(self, cls, filter= '*'):
        try:
            foundAllObjsIds = self.getDatabase().scan_iter(f"{cls.dbCollectionName}:{filter}")

            allObjsIds : list[str]= []
            for currFoundObjId in foundAllObjsIds:
                currObjId : str = currFoundObjId.replace(f'{cls.dbCollectionName}:',"")
                allObjsIds.append(currObjId)

            # all objsIds is Iterator - convert to list
            return list(allObjsIds)
        except Exception as e:
            logger().error(f'RedisClient.loadIdsFromDB raised an unhandled Exception {str(e)}\n trace is {traceback.format_exc()}')
            return []

    @validate_base_obj_cls
    def loadFromDB(self, cls, objId):
        db = self.getDatabase()

        try:
            result = db.json().get(f"{cls.dbCollectionName}:{objId}")

            if result:
                return cls.fromJSON(result)
            else:
                return None
        except Exception as e:
            logger().error(f'RedisClient.loadFromDB raised an unhandled Exception {str(e)}\n trace is {traceback.format_exc()}')
            return None

    @validate_base_obj_cls
    def loadManyFromDB (self, cls, filter) -> List[BaseObj]:
        db = self.getDatabase()
        objectsList : List[BaseObj] = []

        try:
            for objId in db.scan_iter(f"{cls.dbCollectionName}:{filter}"):
                # Get the JSON data for each matched key
                
                jsonData = db.json().get(f'{objId}', Path.root_path())
                currUserObjRef = cls.fromJSON(jsonData)

                if (currUserObjRef is not None):
                    objectsList.append(currUserObjRef)

            return objectsList
        except Exception as e:
            logger().error(f'RedisClient.loadManyFromDB raised an unhandled Exception {str(e)}\n trace is {traceback.format_exc()}')
            return []

    @validate_base_obj_cls
    def searchByField(self, cls, fieldName: str, fieldValue) -> List[BaseObj]:
        """
        Searches via RediSearch index for documents where `field_name == field_value`.
        Returns deserialized objects.
        """
        try:
            indexName = f"idx:{cls.dbCollectionName}"
            # Quote the value in case it has special characters/spaces
            queryString = f'@{fieldName}:{fieldValue}'
            logger().debug(f"searchByField: Searching in index '{indexName}' with query: {queryString}")
            result = self.getDatabase().ft(indexName).search(Query(queryString))

            objectsList = []
            for doc in result.docs:
                # doc.id is like 'CollectionName:<id>'
                json_data = self.getDatabase().json().get(doc.id)
                if json_data:
                    obj = cls.fromJSON(json_data)
                    objectsList.append(obj)

            return objectsList
        except Exception as e:
            logger().error(f'RedisClient.searchByField raised an unhandled Exception {str(e)}\n trace is {traceback.format_exc()}')
            return []


    @validate_base_obj_cls
    def removeFromDB(self, cls, objId : str):
        try:
            db = self.getDatabase()        
            db.delete(f"{cls.dbCollectionName}:{objId}")
        except Exception as e:
            logger().error(f'RedisClient.removeFromDB raised an unhandled Exception {str(e)}\n trace is {traceback.format_exc()}')
            return

    @validate_base_obj_instance
    def pubObjToChannel(self, dataObj: BaseObj, channelId: str):
        try:
            self.getDatabase().xadd(channelId, {'data': dataObj.toJSON()})
        except Exception as e:
            logger().error(f'RedisClient.pushObjToChannel raised an unhandled Exception {str(e)}\n trace is {traceback.format_exc()}')
            return


    @validate_base_obj_cls
    def subGetObjFromChannel(self, cls, channelId : str, timeout=5000) -> Dict[str,BaseObj]:
        if (channelId not in self.channelLastMessage):
            self.channelLastMessage [channelId] = '0-0'

        lastMessageId = self.channelLastMessage[channelId]

        try:
            rawMessages = self.getDatabase().xread({channelId: lastMessageId}, block=timeout)

            if rawMessages is None:
                return {}
            
            objsDict = {}
            # Process and delete the messages
            for stream, message_list in rawMessages:
                for messageId, message_data in message_list:
                    # jsonData = message_data[b'data'].decode('utf-8')  # Convert bytes to string
                    jsonData = message_data['data']
                    # jsonData = json.loads(json_string)  # Parse JSON

                    currObj = cls.fromJSON(jsonData)
                    objsDict[messageId]= currObj

                    self.channelLastMessage[channelId] = messageId

            return objsDict
        except Exception as e:
            logger().error(f'RedisClient.subGetObjFromChannel raised an unhandled Exception {str(e)}\n trace is {traceback.format_exc()}')
            return

    def removeFromChannel(self, channelId: str, messageId: str):
        # Delete the processed message from the stream
        try:
            self.getDatabase().xdel(channelId, messageId)
        except Exception as e:
            logger().error(f'RedisClient.removeFromChannel raised an unhandled Exception {str(e)}\n trace is {traceback.format_exc()}')
            return


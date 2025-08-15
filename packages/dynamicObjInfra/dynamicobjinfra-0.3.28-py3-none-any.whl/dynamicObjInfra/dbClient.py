from typing import List

from dynamicObjInfra.translations import TranslationEntry
from .redisClient import RedisClient
from .doi_logProvider import logger
from .baseObj import BaseObj
from singleton import Singleton
from pymongo import MongoClient
from .validators import validate_base_obj_cls, validate_base_obj_instance
from .utils.env import get_config 

#TBD: add support for redis configutation
GENDERED_LANG_PREFIXES = {"he-IL"}

class DBClient(metaclass=Singleton):
    dbInstance = None
    useRedisCache : bool = False
    redisCache : RedisClient

    def __init__(self):
        #empty __init__ to allow external configuration
        pass

    def getDatabase(self):                
        if self.dbInstance is None:
            # initialize dbInstance
            if (get_config().db_Client is not None):
                self.dbInstance = get_config().db_Client
                logger().debug(f"DBClient: using existing dbClient")
            else:
                host = get_config().db_host
                port = get_config().db_port
                dbName = get_config().db_name   
    
                logger().debug(f"DBClient: host: {host}, port: {port}, dbName: {dbName}, useRedisCache: {self.useRedisCache}")

                if (dbName is None or dbName == "" or host is None or host=="" or port is None):
                    logger().critical(f'DBClient was created without dbName')
                    raise RuntimeError('DBClient was created without dbName')

                connectionString = f"mongodb://{host}:{port}/"
                client = MongoClient(connectionString, tz_aware=True)

                self.dbInstance = client[dbName]

            self.useRedisCache = get_config().db_useRedisCache           
            if (self.useRedisCache):
                self.redisCache = RedisClient()

        return self.dbInstance
    
    @validate_base_obj_instance
    def saveToDB (self, dataObj : BaseObj, filter = {}):
        db = self.getDatabase()
        collection = db[dataObj.dbCollectionName]

        if (filter == {}):
            filter = {'id': dataObj.id}
            
        collection.replace_one(filter, dataObj.serialize(), upsert=True)

        if (self.useRedisCache and dataObj.isCached):
            #update cache
            self.redisCache.saveTempToDB(dataObj=dataObj, objId=dataObj.id)

    @validate_base_obj_instance
    def saveToDB_NoFilter (self, dataObj : BaseObj):
        db = self.getDatabase()
        collection = db[dataObj.dbCollectionName]
           
        collection.insert_one(dataObj.serialize())

        if (self.useRedisCache and dataObj.isCached):
            logger().warning(f'saveToDB_NoFilter called for Class {dataObj.__name__} but isCached is True. This is not supported.')


    @validate_base_obj_instance
    def saveWithTranslations(
        self,
        dataObj: BaseObj,
        translations: List[TranslationEntry]
    ) -> None:
        """
        1) Save (or upsert) the main dataObj into its collection.
        2) For each provided TranslationEntry, upsert it into "translations".
        """
        # (a) Save the main object as before
        self.saveToDB(dataObj)

        # (b) Now save each translation entry
        for tr in translations:
            # Ensure the translation’s object_id matches dataObj.id
            if tr.object_id != dataObj.id:
                raise ValueError(
                    f"TranslationEntry.object_id ({tr.object_id}) must match dataObj.id ({dataObj.id})"
                )

            # Upsert by a composite filter: (object_id, locale, field_id, gender_variant)
            filter = tr.createFilter()

            # saveToDB uses replace_one(upsert=True) on that filter—so it becomes an upsert.
            self.saveToDB(tr, filter=filter)    

    @validate_base_obj_cls
    def deleteFromDB(self, cls, field_value = None, field_name: str = 'id', filter = {}):
        db = self.getDatabase()
        collection = db[cls.dbCollectionName]

        if (filter == {}):
            query = {field_name: field_value}
        else:
            query = filter

        collection.delete_one(query)

        if (self.useRedisCache and cls.isCached):
            #update cache
            self.redisCache.removeFromDB(cls=cls, objId=field_value)

    @validate_base_obj_cls
    def loadFromDB(self, cls, field_value = None, field_name: str = 'id', filter = {}, locale: str = None, gender: int | None = None):

        if (field_value is None and filter == {}):
            raise ValueError("either field_value or filter must be provided")
        
        if (self.useRedisCache and cls.isCached):
            # see if the data is in the cache
            obj = self.redisCache.loadFromDB(cls=cls, objId=field_value)
            if (obj is not None):
                # Apply translations if locale is provided
                if (locale is not None):
                    obj = self._applyTranslations(obj, locale, gender)
                return obj

        db = self.getDatabase()
        collection = db[cls.dbCollectionName]

        if (filter == {}):
            query = {field_name: field_value}
        else:
            query = filter

        result = collection.find_one(query)

        if result:
            # Remove '_id' 
            result.pop('_id', None)
            obj : BaseObj = cls.deserialize(result)
           
            if (obj is None):
                logger().error(f'loadFromDB failed to desiralize objId {field_value}, result is {result}')
                return None

            if (self.useRedisCache and cls.isCached):
                # update cache - before localization
                self.redisCache.saveTempToDB(objId=obj.id, dataObj=obj)

            # Apply translations if locale is provided
            if (locale is not None):
                obj = self._applyTranslations(obj, locale, gender)

            return obj
        else:
            return None
        
    @validate_base_obj_cls
    def loadFromDBByFilter (self, cls, filter, locale: str = None, gender: int | None = None):
        if filter is None:
            return None

        db = self.getDatabase()
        collection = db[cls.dbCollectionName]

        result = collection.find_one(filter)

        if result:
            # Remove '_id' 
            result.pop('_id', None)
            obj : BaseObj = cls.deserialize(result)
           
            if (obj is None):
                logger().error(f'loadFromDB failed to desiralize filter {filter}, result is {result}')
                return None

            # Apply translations if locale is provided
            if (locale is not None):
                obj = self._applyTranslations(obj, locale, gender)

            return obj
        else:
            return None
        

    @validate_base_obj_cls
    def loadManyFromDB(self, cls, field_name: str, field_value):
        
        logger().debug(f"loadManyFromDB: {cls.dbCollectionName} where {field_name} = {field_value}, userRedisCache: {self.useRedisCache}, cls.isCached: {cls.isCached}")
        # 1) Try to retrieve cached docs from Redis.
        cached_ids = set()
        cached_docs = {}
        if self.useRedisCache and cls.isCached:
            redis_results : List[BaseObj]= self.redisCache.searchByField(cls, field_name, field_value)
            for doc in redis_results:
                cached_ids.add(doc.id)
                cached_docs[doc.id] = doc

        # 2) Fetch missing documents from the DB using $nin.
        db = self.getDatabase()
        collection = db[cls.dbCollectionName]
        query = { field_name: field_value }
        if cached_ids:
            query["id"] = {"$nin": list(cached_ids)}

        missing_docs = []
        for result in collection.find(query):
            result.pop('_id', None)
            obj = cls.deserialize(result)
            missing_docs.append(obj)
            # Update cache.
            if self.useRedisCache and cls.isCached:
                self.redisCache.saveTempToDB(objId=obj.id, dataObj=obj)

        # 3) Return merged results: cached docs + missing docs.
        all_docs = list(cached_docs.values()) + missing_docs
        return all_docs


    @validate_base_obj_cls
    def loadManyFromDBByFilter(self, cls, filter = {}):
        db = self.getDatabase()
        collection = db[cls.dbCollectionName]

        results = collection.find(filter)

        objects = []
        for result in results:
            result.pop('_id', None)  # Remove '_id'
            obj = cls.deserialize(result)
            objects.append(obj)

            if (self.useRedisCache and cls.isCached):
                # update cache
                self.redisCache.saveTempToDB(objId=obj.id, dataObj=obj)            

        return objects
    
    def _fetchRawTranslations(self, obj, locale, gender):
        base = {
            "object_id":  obj.id,
            "locale":     locale,
        }

        # 1) Try gendered entries
        if gender is not None:
            base["gender_variant"] = gender
        else:
            base["gender_variant"] = None

        return self.loadManyFromDBByFilter(TranslationEntry, base)

    
    def _applyTranslations(self, obj: BaseObj, locale: str, gender: int | None) -> BaseObj:
        if (gender is not None and locale not in get_config().gendered_languages):
            # gender is not supported for this locale, ignore it
            gender = None
        
        entries = self._fetchRawTranslations(obj, locale, gender)
        for t in entries:
            name = obj.__class__.get_field_name_by_id(t.field_id)
            if name:
                setattr(obj, name, t.text)
        
        # recursively localize nested objects
        for field_name, field_info in obj.model_fields.items():
            val = getattr(obj, field_name, None)
            if isinstance(val, BaseObj):
                # nested object → localize it
                self._applyTranslations(val, locale, gender)

            elif isinstance(val, list):
                # list of things: localize any BaseObj inside
                for item in val:
                    if isinstance(item, BaseObj):
                        self._applyTranslations(item, locale, gender)

            elif isinstance(val, dict):
                # dict of things: localize any BaseObj values
                for item in val.values():
                    if isinstance(item, BaseObj):
                        self._applyTranslations(item, locale, gender)
        
        return obj
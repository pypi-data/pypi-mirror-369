from dataclasses import dataclass, field
from dynamicObjInfra.enums import TTL_Type
import pymongo
from ..doi_logProvider import logger

@dataclass
class EnvConfig:
    db_Client: pymongo.MongoClient | None = None
    db_host: str | None = None
    db_port: int | None = None
    db_name: str | None = None
    db_useRedisCache: bool = False
    redis_host: str | None = None
    redis_port: int = 6379
    cache_short_ttl: int = 300
    cache_long_ttl: int = 1800
    cache_extra_long_ttl: int = 86400
    gendered_languages: set[str] = field(default_factory=set)

_GLOBAL_CONFIG: EnvConfig | None = None

def initialize(config: EnvConfig) -> None:
    """
    Store a global config object for use elsewhere in the package.
    Must be called once by the application.
    """
    global _GLOBAL_CONFIG
    _GLOBAL_CONFIG = config

    if (_GLOBAL_CONFIG.db_Client is None and (_GLOBAL_CONFIG.db_host is None or _GLOBAL_CONFIG.db_port is None or _GLOBAL_CONFIG.db_name is None)):
        logger().critical("DBClient was not given a client or a combination of db_host, db_port, or db_name")
        raise RuntimeError("DBClient was not given a client or a combination of db_host, db_port, or db_name")

def get_config() -> EnvConfig:
    """
    Return the global config, or raise an error if not initialized yet.
    """
    if _GLOBAL_CONFIG is None:
        raise RuntimeError("InfraConfig is not initialized. Call initialize(...) first.")
    return _GLOBAL_CONFIG

def get_ttl_by_type(ttlType : TTL_Type):
    if (ttlType == TTL_Type.SHORT):
        return get_config().cache_short_ttl
    elif (ttlType == TTL_Type.LONG):
        return get_config().cache_long_ttl
    elif (ttlType == TTL_Type.EXTRA_LONG):
        return get_config().cache_extra_long_ttl        
    
    return None

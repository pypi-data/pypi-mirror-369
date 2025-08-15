# dynamicObjInfra

**dynamicObjInfra** is a reusable infrastructure package for data handling. It provides a set of tools for building data models, managing data persistence with MongoDB and Redis caching, and handling event streams using Redis. The package leverages Pydantic for data validation and serialization, and it includes support for Redis indexing of model fields.

## Features

- **Base Object Model:** Extend the provided `BaseObj` to create data models with automatic JSON serialization/deserialization.
- **Database Integration:** Use `DBClient` for MongoDB persistence.
- **Redis Caching & Indexing:**
  - **Caching:** Enable Redis caching for rapid retrieval of frequently used data.
    - Each data model may define an `isCached` property. When set to `True`, objects of that model will be cached in Redis.
    - The `DBClient` class reads the global configuration parameter `db_useRedisCache` to determine whether to use Redis for caching. This flag is stored as `useRedisCache` within the client.
    - With both `isCached` and `useRedisCache` enabled, database operations such as saving and loading objects will interact with Redis using the `RedisClient`.
  - **Indexing:** Automatically create RediSearch indexes for your models via helpers like `IndexedField` and the `@redis_indexed` decorator.
- **Event Streams:** Publish and subscribe to model events using Redis streams, with support provided by the `EventsStream` module.
- **Configurable Environment:** Set up global configurations with `EnvConfig` and `initialize`.
- **Custom Logging:** Use the included log provider to integrate your own logging framework.

## Installation

Install using pip:
bash
pip install dynamicObjInfra


> **Note:** The package has runtime dependencies on [pydantic](https://pydantic-docs.helpmanual.io/), [redis](https://github.com/redis/redis-py), and [pymongo](https://pymongo.readthedocs.io/).

## Quickstart

### 1. Initialize the Environment

Before using any of the package functionalities, initialize the global configuration:


python:dynamicObjInfra/utils/env_usage.py
from dynamicObjInfra.utils.env import EnvConfig, initialize
config = EnvConfig(
db_host="localhost",
db_port=27017,
db_name="your_database",
db_useRedisCache=True, # Enable Redis caching globally
redis_host="localhost",
redis_port=6379,
cache_short_ttl=300,
cache_long_ttl=1800
)
initialize(config)

### 2. Create a Data Model

Extend the `BaseObj` to create your schema. For example, a simple `User` model with caching enabled:
```python:dynamicObjInfra/models/user.py
from pydantic import Field
from dynamicObjInfra.baseObj import BaseObj

class User(BaseObj):
    # Collection name for MongoDB and Redis
    dbCollectionName: str = "users"
    
    # Enable Redis caching for this model
    isCached: bool = True
    
    # Define the fields for the model
    id: str
    name: str = Field(default="unknown")
    age: int = Field(default=0)
```

### 3. Database Operations with Caching

Use `DBClient` to save and load objects. The client first checks if caching is enabled both globally (`useRedisCache`) and for the object (`isCached`). If so, it leverages Redis to speed up operations.

python:dynamicObjInfra/dbClient_usage.py
from dynamicObjInfra.dbClient import DBClient
from dynamicObjInfra.models.user import User

Create a DBClient instance
db_client = DBClient()
Create a new User object
user = User(id="user_001", name="Alice", age=30)
Save the object to MongoDB; if caching is enabled, the object is also updated in Redis.
db_client.saveToDB(user)
Load the User object; the load operation first tries Redis (if enabled)
loaded_user = db_client.loadFromDB(User, field_value="user_001")
print(loaded_user)
```

### 4. Using the Redis Cache Directly

You can interact with the Redis cache directly using `RedisClient`. This is useful for cases where you might want to update or retrieve cached objects without going through `DBClient`.
```python:dynamicObjInfra/redis_usage.py
from dynamicObjInfra.redisClient import RedisClient
from dynamicObjInfra.models.user import User

redis_client = RedisClient()

# Save a User object directly in Redis
redis_client.saveTempToDB(dataObj=user, objId=user.id)

# Retrieve the User object directly from Redis
cached_user = redis_client.loadFromDB(User, objId="user_001")
print(cached_user)
```

### 5. Publish and Subscribe to Events

Publish events (e.g., when a user is updated) and subscribe to them using `EventsStream`:

```python:dynamicObjInfra/events_example.py
from dynamicObjInfra.eventsStream import EventsStream
from dynamicObjInfra.models.user import User
import time

# Initialize the events stream
events = EventsStream()
channel = "user_updates"

# Publish an event with the User object (automatically sends its JSON representation)
events.publishObject(channel, user)

# Wait for incoming messages
time.sleep(1)

# Subscribe to the channel and process the incoming events
incoming_events = events.getObjsFromChannel(channel, User)
for message_id, user_event in incoming_events.items():
    print(f"Message ID: {message_id} - User Data: {user_event}")
```

### 6. Logging

Configure a custom logger if needed. The package uses a simple log provider that can be replaced at runtime:

```python:dynamicObjInfra/logging_setup.py
import logging
from dynamicObjInfra.logProvider import setAppLogger, logger

# Configure your logger
my_logger = logging.getLogger("my_app_logger")
my_logger.setLevel(logging.DEBUG)
logging.basicConfig()

# Set the application's logger for dynamicObjInfra
setAppLogger(my_logger)

# Log a message to verify setup
logger().info("dynamicObjInfra is configured and ready to use!")
```

## Redis Caching Details

### How Caching Works

- **`isCached` Property in BaseObj:**  
  When creating your models (extending `BaseObj`), you can add a class-level property `isCached`. Setting `isCached = True` indicates that objects of this model should be cached in Redis. For example:
  ```python
  class User(BaseObj):
      dbCollectionName: str = "users"
      isCached: bool = True  # Enable caching for User objects
      
      id: str
      name: str
      # ... additional fields
  ```

- **`useRedisCache` Flag in DBClient:**  
  The `DBClient` reads the global configuration parameter `db_useRedisCache` and stores it as `useRedisCache`. When this flag is enabled:
  - **On Save:** After saving an object in MongoDB using the `saveToDB` method, if the object's model has `isCached = True`, the same object is also stored (or updated) in Redis.
  - **On Load:** When calling the `loadFromDB` or `loadManyFromDB` methods, `DBClient` first attempts to retrieve the object from Redis if both `useRedisCache` and the model's `isCached` flag are enabled. If the object is not found in the cache, it falls back to MongoDB and then updates the cache.

This two-level caching mechanism helps improve performance by reducing the load on MongoDB for frequently accessed data.

## Contributing

Contributions are welcome! If you wish to improve the package or fix issues, please open a pull request or report an issue on the [GitHub repository](https://github.com/Shaulbm/dynamicObjInfra/issues).

## License

This project is licensed under the MIT License.
```

Feel free to adjust the examples and configurations as needed for your use case.
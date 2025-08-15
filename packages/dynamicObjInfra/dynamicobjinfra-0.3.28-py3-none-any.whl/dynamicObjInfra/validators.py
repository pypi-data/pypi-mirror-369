import functools
from .doi_logProvider import logger
from .baseObj import BaseObj

def validate_base_obj_cls(func):
    """Decorator to ensure 'cls' is a subclass of BaseObj and has a valid dbCollectionName."""
    @functools.wraps(func)
    def wrapper(self, cls, *args, **kwargs):
        if not issubclass(cls, BaseObj):
            logger().error(f"{func.__name__} - {cls.__name__} does not inherit from BaseObj")
            raise TypeError(f"{cls.__name__} must inherit from BaseObj")
        
        if not getattr(cls, "dbCollectionName", ""):
            logger().error(f"{func.__name__} - {cls.__name__} has an empty dbCollectionName")
            raise ValueError(f"{cls.__name__} must define dbCollectionName")
        
        return func(self, cls, *args, **kwargs)
    return wrapper

def validate_base_obj_instance(func):
    """Decorator to ensure the second argument `dataObj` is a BaseObj and has a non-empty dbCollectionName."""
    @functools.wraps(func)
    def wrapper(self, dataObj, *args, **kwargs):
        # Optional: verify that dataObj is an instance of BaseObj
        if not isinstance(dataObj, BaseObj):
            logger().error(f"{func.__name__} - dataObj is not a BaseObj instance.")
            raise TypeError(f"Argument 'dataObj' must be a BaseObj subclass, got {type(dataObj)}")

        # Check dbCollectionName
        if not getattr(dataObj, "dbCollectionName", ""):
            logger().error(
                f"{func.__name__} called for {type(dataObj).__name__} without a dbCollectionName defined."
            )
            raise ValueError(f"{type(dataObj).__name__} must define dbCollectionName.")

        return func(self, dataObj, *args, **kwargs)
    return wrapper
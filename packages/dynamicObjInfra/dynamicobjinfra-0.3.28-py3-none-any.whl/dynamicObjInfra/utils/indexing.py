from pydantic import Field

def IndexedField(default, *, index_type="text", **kwargs):
    """
    Returns a Pydantic Field with extra metadata for indexing stored in json_schema_extra.
    """
    # Merge any existing json_schema_extra with our index metadata.
    extra = kwargs.pop("json_schema_extra", {})
    extra["index_type"] = index_type
    return Field(default, json_schema_extra=extra, **kwargs)

def redis_indexed(cls):
    """
    Class decorator that marks the model as redis-indexed.
    (We do not scan __fields__ here, because they aren’t ready yet.)
    """
    cls.__redis_indexed__ = True
    return cls


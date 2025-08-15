from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, List, Type
from pydantic import BaseModel
from .doi_logProvider import logger
from .utils.parser import convertToUTC

class BaseObj(BaseModel):
    state_fields: ClassVar[List[str]] = []  # Fields considered as "state" and will be ignored when updating data from other objs
    readable_fields : ClassVar[list[str]] = []
    dbCollectionName : ClassVar[str] = ""
    isCached: ClassVar[bool] = False

    def serialize(self):
        serialized_data = {}
        for key, value in self.model_dump().items():
            serialized_data[key] = self._serialize_value(value)
        
        return serialized_data

    @staticmethod
    def _serialize_value(value):
        if isinstance(value, Enum):
            return value.value  # Convert Enum to its value
        elif isinstance(value, list):  # Handle lists of Enums
            return [BaseObj._serialize_value(v) for v in value]
        elif isinstance(value, dict):  # Handle dicts with Enums
            return {k: BaseObj._serialize_value(v) for k, v in value.items()}
        return value  # Return value as is if not Enum

    @classmethod
    def deserialize(cls, data):
        if (data is None):
            return None
        try:
            return cls.model_validate(data)
        except Exception as e:
            logger().error (f'BaseObj.deserialize failed to load data error is {e}')
            raise e

    def toJSON(self):
        return self.model_dump_json()
    
    @classmethod
    def fromJSON(cls, data):
        if (data is None):
            return None
        
        try:
            return cls.model_validate_json(data)
        except Exception as e:
            logger().error (f'BaseObj.fromJson failed to load data error is {e}')
            raise e

    def toReadableText(self, indent=0) -> str:
        indent_str = '  ' * indent

        # Get the list of fields to include - if none defined, include all fields
        if (self.__class__.readable_fields.__len__() > 0):
            fields_to_include = self.__class__.readable_fields
        else:
            fields_to_include = self.model_fields.keys()

        readable_lines = []
        for field_name in fields_to_include:
            if field_name in self.model_fields:
                value = getattr(self, field_name)
                field_info = self.model_fields[field_name]
                field_description = field_info.description
                readable_value = self._value_to_text(field_name, value, indent + 1)
                if field_description:
                    readable_lines.append(f"{indent_str}{field_name} ({field_description}): {readable_value}")
                else:
                    readable_lines.append(f"{indent_str}{field_name}: {readable_value}")
        readable_text = "\n".join(readable_lines)
        return readable_text
    
    # subclasses provide their .field_ids mapping
    @classmethod
    def get_field_name_by_id(cls, field_id: str) -> str | None:
        for name, fid in getattr(cls, "field_ids", {}).items():
            if fid == field_id:
                return name
        return None
    
    def _value_to_text(self, field_name, value, indent=0):
        indent_str = '  ' * indent
        if isinstance(value, BaseObj):
            return f"\n{value.toReadableText(indent)}"
        
        elif isinstance(value, list):
            if not value:  # Handle empty lists
                return "[]"
            
            def process_list_item(item):
                if isinstance(item, BaseObj):
                    return item.toReadableText(indent + 1)
                return self._value_to_text(field_name, item, indent + 1)
            
            list_items_text = [f"{indent_str}- {process_list_item(item)}" for item in value]
            return "\n" + "\n".join(list_items_text)
        
        elif isinstance(value, dict):
            if not value:  # Handle empty dictionaries
                return "{}"

            def process_dict_item(key, val):
                processed_key = str(key)  # Ensure the key is stringified
                processed_val = self._value_to_text(field_name, val, indent + 1)
                return f"{indent_str}{processed_key}: {processed_val}"

            dict_items_text = [process_dict_item(k, v) for k, v in value.items()]
            return "\n" + "\n".join(dict_items_text)
        
        elif isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return str(value)
        
    @classmethod
    def fromSharedData(cls: Type[Any], data: BaseObj) -> Any:
        """Create an instance of the cls from an original data object, copy all shared fields including shared fields and nested BaseObj objects."""
        if not isinstance(data, BaseObj):
            raise TypeError(f"Expected BaseObj, got {type(data).__name__}")

        # Prepare a dictionary to hold transformed data
        transformed_data = {}

        for field_name, field_info in cls.model_fields.items():
            if field_name not in data.model_fields:
                # Skip fields that don't exist in the source data
                continue

            if field_name in cls.state_fields:
                # skip fields that are in the state_fields
                continue

            # Get the source value
            value = getattr(data, field_name)

            # Handle nested BaseObj instances
            if isinstance(value, BaseObj):
                transformed_data[field_name] = field_info.annotation.fromSharedData(value)

            # Handle lists of BaseObj instances
            elif isinstance(value, list):
                list_type = field_info.annotation.__args__[0]  # Extract the list element type
                if issubclass(list_type, BaseObj):
                    transformed_data[field_name] = [
                        list_type.fromSharedData(item) for item in value
                    ]
                else:
                    transformed_data[field_name] = value  # Leave lists of primitives as is

            # Handle primitive types directly
            else:
                transformed_data[field_name] = value

        # Return an instance of the subclass
        return cls(**transformed_data)

    def updateFrom(self, other: "BaseObj") -> None:
        """
        Update the shared properties of this object from another BaseObj instance.

        - Skips fields in `state_fields`.
        - Recursively updates nested BaseObj fields.
        - If the new value is a list, the entire old list is replaced with the new one.
        - If the new value is a dict, merges by key, keeping only keys present in the new dict.
        - If both old and new values for a key are BaseObj, calls updateFrom on them.
        - If only the new value is BaseObj, creates a new instance.
        - Otherwise, replaces with the new value.
        - Everything else (primitives, etc.) is replaced directly with the new value.
        """
        if not isinstance(other, BaseObj):
            raise TypeError(f"Expected BaseObj, got {type(other).__name__}")

        for field_name, field_info in self.model_fields.items():
            # Skip fields that don't exist in the source object
            if field_name not in other.model_fields:
                continue

            # Skip state fields
            if field_name in self.state_fields:
                continue

            new_value = getattr(other, field_name)
            current_value = getattr(self, field_name, None)

            # 1) Nested BaseObj => recurse
            if isinstance(new_value, BaseObj) and isinstance(current_value, BaseObj):
                current_value.updateFrom(new_value)
                continue

            # 2) Lists => replace
            if isinstance(new_value, list):
                setattr(self, field_name, new_value)
                continue

            # 3) Dictionaries => merge by key
            if isinstance(new_value, dict):
                if not isinstance(current_value, dict):
                    # Old value not a dict => just replace
                    setattr(self, field_name, new_value)
                    continue

                merged_dict = {}
                for key, val in new_value.items():
                    old_val = current_value.get(key)
                    if isinstance(val, BaseObj) and isinstance(old_val, BaseObj):
                        old_val.updateFrom(val)
                        merged_dict[key] = old_val
                    elif isinstance(val, BaseObj):
                        merged_dict[key] = val.__class__.fromSharedData(val)
                    else:
                        merged_dict[key] = val

                # We discard any old keys that aren't in new_value
                setattr(self, field_name, merged_dict)
                continue

            # 4) Everything else => replace
            setattr(self, field_name, new_value)

    @classmethod
    def fromBaseModel(cls: Type[Any], data: BaseModel) -> Any:
        """
        Create an instance of the current class from a Pydantic BaseModel.
        Supports nested objects and lists of BaseObj-compatible objects.
        """
        if not isinstance(data, BaseModel):
            raise TypeError(f"Expected BaseModel, got {type(data).__name__}")

        transformed_data = {}

        for field_name, field_info in cls.model_fields.items():
            # Skip fields that don't exist in the source model
            if not hasattr(data, field_name):
                continue

            value = getattr(data, field_name)

            # Handle nested BaseObj instances
            if isinstance(value, BaseModel) and issubclass(field_info.annotation, BaseObj):
                transformed_data[field_name] = field_info.annotation.fromBaseModel(value)

            # Handle lists of BaseModel instances
            elif isinstance(value, list):
                list_type = field_info.annotation.__args__[0]  # Extract the list element type
                if issubclass(list_type, BaseObj) and all(isinstance(v, BaseModel) for v in value):
                    transformed_data[field_name] = [
                        list_type.fromBaseModel(item) for item in value
                    ]
                else:
                    transformed_data[field_name] = value  # Leave lists of primitives as is

            # Handle primitive types directly
            else:
                transformed_data[field_name] = value

        # Return an instance of the target class
        return cls(**transformed_data)
    
    def updateFromBaseModel(self, data: BaseModel) -> None:
        """
        Update the current instance from a Pydantic BaseModel.
        Supports nested objects and lists of BaseObj-compatible objects.
        """
        if not isinstance(data, BaseModel):
            raise TypeError(f"Expected BaseModel, got {type(data).__name__}")

        for field_name, field_info in self.model_fields.items():
            # Skip fields that don't exist in the source model
            if not hasattr(data, field_name):
                continue

            value = getattr(data, field_name)

            # Handle nested BaseObj instances
            if isinstance(value, BaseModel) and issubclass(field_info.annotation, BaseObj):
                setattr(self, field_name, field_info.annotation.updateFromBaseModel(value))

            # Handle lists of BaseModel instances
            elif isinstance(value, list):
                list_type = field_info.annotation.__args__[0]  # Extract the list element type
                if issubclass(list_type, BaseObj) and all(isinstance(v, BaseModel) for v in value):
                    setattr(self, field_name, [
                        list_type.updateFromBaseModel(item) for item in value
                    ])
                else:
                    setattr(self, field_name, value)  # Leave lists of primitives as is
            
            # Handle primitive types directly
            else:
                setattr(self, field_name, value)

       
    def verifyUTC(self):
        """
        Ensures all `datetime` fields of the object, including nested BaseObj instances, 
        are UTC-aware.
        """
        for attr, value in self.__dict__.items():
            if isinstance(value, datetime):  # If it's a datetime
                setattr(self, attr, convertToUTC(value))
            elif isinstance(value, BaseObj):  # If it's a nested BaseObj
                value.verifyUTC()
            elif isinstance(value, list):  # If it's a list, check each item
                setattr(self, attr, [
                    convertToUTC(v) if isinstance(v, datetime) 
                    else (v.verifyUTC() or v if isinstance(v, BaseObj) else v)
                    for v in value
                ])
            elif isinstance(value, dict):  # If it's a dict, check each value
                setattr(self, attr, {
                    k: convertToUTC(v) if isinstance(v, datetime) 
                    else (v.verifyUTC() or v if isinstance(v, BaseObj) else v)
                    for k, v in value.items()
                })

    @classmethod
    def get_redis_index_fields(cls):
        """
        Returns a dict mapping field names to their declared index type,
        based on the Pydantic field metadata stored in json_schema_extra.
        """
        index_fields = {}
        if getattr(cls, "__redis_indexed__", False):
            for field_name, model_field in cls.model_fields.items():
                # if the field has extra data, check for an index_type
                if (model_field.json_schema_extra is not None):
                    index_type = model_field.json_schema_extra.get("index_type")

                    if index_type:
                        index_fields[field_name] = index_type
        return index_fields
    
    def createFilter(self) -> dict[str, Any]:
        if ('id' not in self.model_fields):
            raise ValueError("id field is required, did you forget to override createFilter?")

        return {'id': self.id}

from typing import List, Union, get_type_hints, TypedDict, Type
from datetime import date, datetime
from pydantic import BaseModel, Field, create_model


class AvroTypeRequiredFields(TypedDict):
    type: str

class AvroTypeNotRequiredFields(TypedDict, total=False):
    logicalType: str

class AvroTypeField(AvroTypeRequiredFields,AvroTypeNotRequiredFields):
    ...

class AvroFieldDescription:
    name: str
    type: AvroTypeField

class AvroScheme():
    type: str
    name: str
    namespace: str
    fields: List[AvroFieldDescription]

def int_to_avro() -> AvroTypeField:
    return {"type": "int"}

def float_to_avro() -> AvroTypeField:
    return {"type": "float"}

def str_to_avro() -> AvroTypeField:
    return {"type": "string"}

def bool_to_avro() -> AvroTypeField:
    return {"type": "boolen"}

def date_to_avro() -> AvroTypeField:
    return {"type": "int", "logicalType": "date"}

def datetime_to_avro() -> AvroTypeField:
    return {"type": "long", "logicalType": "timestamp-millis"}

def python_type_to_avro_converter(python_type: Type) -> AvroTypeField:
    if issubclass(python_type, int):
        return int_to_avro()
    elif issubclass(python_type, bool):
        return bool_to_avro()
    elif issubclass(python_type, float):
        return float_to_avro()
    elif issubclass(python_type, str):
        return str_to_avro()
    elif issubclass(python_type, date) and not issubclass(python_type, datetime):
        return date_to_avro()
    elif issubclass(python_type, datetime):
        return datetime_to_avro()
    else:
        raise TypeError(f"No Avro conversion available for type {python_type}")

def generate_avro_schema_from_pydantic(pydantic_class: BaseModel) -> AvroScheme:
    type_hints = get_type_hints(pydantic_class)
    fields = []
    
    for field_name, field_type in type_hints.items():
        avro_field = {
            "name": field_name,
            "type": python_type_to_avro_converter(field_type)
        }
        fields.append(avro_field)
    
    schema = {
        "type": "record",
        "name": pydantic_class.__name__,
        "namespace": "com.example",
        "fields": fields
    }
    return schema


def avro_type_to_pydantic_type(avro_type: AvroTypeField) -> Union[date, datetime, int, float, str]:
    if isinstance(avro_type, dict) and 'logicalType' in avro_type:
        if avro_type['logicalType'] == 'date':
            return date
        elif avro_type['logicalType'] == 'timestamp-millis':
            return datetime
    
    if isinstance(avro_type, dict):
        simple_avro_type = avro_type['type']
    else:
        simple_avro_type = avro_type
    
    if simple_avro_type == 'int':
        return int
    elif simple_avro_type == 'float':
        return float
    elif simple_avro_type == 'string':
        return str
    else:
        raise ValueError(f"Unsupported Avro type: {simple_avro_type}")

def _get_fields_from_schema(avro_schema: AvroScheme):
    fields_definition = {}
    
    for field in avro_schema['fields']:
        field_name = field['name']
        field_type = avro_type_to_pydantic_type(field['type'])
        
        fields_definition[field_name] = (field_type, Field(...))

    return fields_definition

def is_prev_schema_compatible_with_next(prev_version: AvroScheme, next_version: AvroScheme) -> bool:
    # prev items should be in next
    prev_version_fields = _get_fields_from_schema(prev_version)
    next_version_fields = _get_fields_from_schema(next_version)

    for field, value in prev_version_fields.items():
        if not str(value) == str(next_version_fields.get(field,"")):
            return False

    return True

def are_schemas_compatible(ordered_avro_schemas: List[AvroScheme]) -> bool:
    if len(ordered_avro_schemas) == 1:
        return True
    
    if len(ordered_avro_schemas) == 2:
        prev_schema, next_schema = ordered_avro_schemas
        return is_prev_schema_compatible_with_next(prev_version=prev_schema, next_version=next_schema)
    
    for i in range(0, len(ordered_avro_schemas) - 1):
        if not is_prev_schema_compatible_with_next(prev_version=ordered_avro_schemas[i], next_version=ordered_avro_schemas[i+1]):
            return False

    return True

def create_pydantic_model_from_avro_schema(avro_schema: AvroScheme) -> Type[BaseModel]:
    
    fields_definition = _get_fields_from_schema(avro_schema)
    
    dynamic_model = create_model(avro_schema["name"], **fields_definition)
    return dynamic_model

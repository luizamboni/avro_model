import io
import fastavro
from io import BytesIO
from typing import Any, Dict, Type
from pydantic import BaseModel
from avro_model.src.avro_scheme import generate_avro_schema_from_pydantic
from avro_model.src.python_to_avro_values import python_type_to_avro


def convert_pydantic_to_avro(model_instance: BaseModel) -> Dict[str, Any]:
    model_class = type(model_instance)
    schema = generate_avro_schema_from_pydantic(model_class)
    data = {}

    for field in schema["fields"]:
        field_name = field["name"]
        field_value = getattr(model_instance, field_name, None)
        converter = python_type_to_avro(type(field_value))
        if field_value is not None:
            data[field_name] = converter(field_value)

    return data

def convert_pydantic_to_avro_binary(model_instance: BaseModel) -> bytes:
    schema_dict = generate_avro_schema_from_pydantic(type(model_instance))
    avro_schema = fastavro.parse_schema(schema_dict)

    data = convert_pydantic_to_avro(model_instance)

    buffer = BytesIO()
    fastavro.schemaless_writer(buffer, avro_schema, data)
    return buffer.getvalue()

def convert_avro_binary_to_pydantic_instance(avro_bin: bytes, cls: Type) -> Dict:
    schema_dict = generate_avro_schema_from_pydantic(cls)
    avro_schema = fastavro.parse_schema(schema_dict)
    avro_record = fastavro.schemaless_reader(io.BytesIO(avro_bin), avro_schema)
    return cls(**avro_record)

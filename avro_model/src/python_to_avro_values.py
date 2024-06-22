from datetime import date, datetime, timezone
from typing import Type, Union

def int_to_avro(value: int) -> int:
    return value

def float_to_avro(value: float) -> float:
    return value

def str_to_avro(value: str) -> str:
    return value

def date_to_avro(value: date) -> int:
    epoch = date(1970, 1, 1)
    return (value - epoch).days

def datetime_to_avro_timestamp_millis(value: datetime) -> int:
    epoch = datetime(1970, 1, 1,tzinfo=timezone.utc)
    delta = value - epoch
    return int(delta.total_seconds() * 1000)

def python_type_to_avro(python_type: Type) -> Union[int, float, str]:
    if issubclass(python_type, int):
        return int_to_avro
    elif issubclass(python_type, float):
        return float_to_avro
    elif issubclass(python_type, str):
        return str_to_avro
    elif issubclass(python_type, date) and not issubclass(python_type, datetime) :
        return date_to_avro
    elif issubclass(python_type, datetime):
        return datetime_to_avro_timestamp_millis
    else:
        raise TypeError(f"No conversion available for type {python_type}")

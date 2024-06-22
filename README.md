# Avro Model

`avro_model` is a Python module that dynamically generates Pydantic models from Avro schemas. 
This module is designed to facilitate the use of Avro data in Python applications, providing strong type checks at runtime and easing data validation and serialization tasks.

## Covered types in python to Avro

| Python Type | Avro Type                           |
|-------------|-------------------------------------|
| int         | int                                 |
| float       | float                               |
| str         | string                              |
| date        | int (logicalType: `date`)           |
| datetime    | long (logicalType: `timestamp-millis`) |


## Installment
`avro_model` is in its early days. So to install
```shell
$ pip install
```

## With `avro_model` is possible:

Extract a pydantic model correspondent avro schema

```python
from avro_model import convert_pydantic_to_avro_binary
from pydantic import BaseModel
from datetime import date, datetime, timezone

class User(BaseModel):
    name: str
    age: int
    is_student: bool 
    gender: str
    birth_date: date
    last_login: datetime


instance = User(**{
    "name": "Joåhn Doe",
    "age": 30,
    "is_student": False,
    "gender": "MALE",
    "birth_date": date(1990, 5, 20),
    "last_login": datetime(2022, 1, 1, 12, 0,0,0, tzinfo=timezone.utc),
})
print(instance)
#> User(name='Joåhn Doe', age=30, is_student=False, gender='MALE', birth_date=datetime.date(1990, 5, 20), last_login=datetime.datetime(2022, 1, 1, 12, 0, tzinfo=datetime.timezone.utc))

avro_bytes = convert_pydantic_to_avro_binary(instance)
print(avro_bytes)
#> b'\x14Jo\xc3\xa5hn Doe<\x00\x08MALE\xa8t\x80\xa8\x96\xd8\xc2_'
```

And also convert avro binary to the correspondent pydantic Model
```python
from avro_model import convert_avro_binary_to_pydantic_instance

rebuilt_instance = convert_avro_binary_to_pydantic_instance(avro_bytes, User)
print(rebuilt_instance)
#> User(name='Joåhn Doe', age=30, is_student=False, gender='MALE', birth_date=datetime.date(1990, 5, 20), last_login=datetime.datetime(2022, 1, 1, 12, 0, tzinfo=datetime.timezone.utc))
```


Create a pydantic_model by a Avro Scheme
```python
from avro_model import create_pydantic_model_from_avro_schema

avro_scheme = {
    'type': 'record', 
    'name': 'com.example.User', 
    'fields': [
        {'name': 'name', 'type': 'string'}, # simple description
        {'name': 'age', 'type': {'type': 'int'}}, 
        {'name': 'is_student', 'type': {'type': 'int'}}, 
        {'name': 'gender', 'type': {'type': 'string'}}, 
        {'name': 'birth_date', 'type': {'logicalType': 'date', 'type': 'int'}}, 
        {'name': 'last_login', 'type': {'type': 'long', 'logicalType': 'timestamp-millis'}}
    ]
}

ModelClass = create_pydantic_model_from_avro_schema(avro_scheme)
print(ModelClass)
#> <class 'pydantic.main.com.example.User'>

model_instance = ModelClass(**{
    "name": "Joåhn Doe",
    "age": 30,
    "is_student": False,
    "gender": "MALE",
    "birth_date": date(1990, 5, 20),
    "last_login": datetime(2022, 1, 1, 12, 0,0,0, tzinfo=timezone.utc),
})
print(model_instance)
#> com.example.User(name='Joåhn Doe', age=30, is_student=0, gender='MALE', birth_date=datetime.date(1990, 5, 20), last_login=datetime.datetime(2022, 1, 1, 12, 0, tzinfo=datetime.timezone.utc))
```

Ensure Avro Schema compatibility
```python
from avro_model import is_prev_schema_compatible_with_next

v1_avro_scheme = {
    'type': 'record', 
    'name': 'com.example.User', 
    'fields': [
        {'name': 'name', 'type': 'string'},
    ]
}

v2_avro_scheme = {
    'type': 'record', 
    'name': 'com.example.User', 
    'fields': [
        {'name': 'name', 'type': 'string'},
        {'name': 'age', 'type': {'type': 'int'}}, 
    ]
}

v3_invalid_avro_scheme = {
    'type': 'record', 
    'name': 'com.example.User', 
    'fields': [
        {'name': 'name', 'type': 'string'},
    ]
}

assert is_prev_schema_compatible_with_next(prev_version=v1_avro_scheme, next_version=v2_avro_scheme) == True
assert is_prev_schema_compatible_with_next(prev_version=v2_avro_scheme, next_version=v3_invalid_avro_scheme) == False
```

Or check a chain of schemas.
```python
from avro_model import is_schemas_compatibles

v1_avro_scheme = {
    'type': 'record', 
    'name': 'com.example.User', 
    'fields': [
        {'name': 'name', 'type': 'string'},
    ]
}

v2_avro_scheme = {
    'type': 'record', 
    'name': 'com.example.User', 
    'fields': [
        {'name': 'name', 'type': 'string'},
        {'name': 'age', 'type': {'type': 'int'}}, 
    ]
}


v3_avro_scheme = {
    'type': 'record', 
    'name': 'com.example.User', 
    'fields': [
        {'name': 'name', 'type': 'string'},
        {'name': 'age', 'type': {'type': 'int'}}, 
        {'name': 'birth_date', 'type': {'logicalType': 'date', 'type': 'int'}}, 
    ]
}

v3_invalid_avro_scheme = {
    'type': 'record', 
    'name': 'com.example.User', 
    'fields': [
        {'name': 'name', 'type': 'string'},
    ]
}

assert are_schemas_compatible(ordered_avro_schemas=[v1_avro_scheme, v2_avro_scheme, v3_avro_scheme]) == True
assert are_schemas_compatible(ordered_avro_schemas=[v1_avro_scheme, v2_avro_scheme, v3_invalid_avro_scheme]) == False
```

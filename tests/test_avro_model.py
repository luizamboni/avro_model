import unittest
from datetime import date, datetime, timezone

from pydantic import BaseModel
from avro_model import (
    convert_pydantic_to_avro_binary, convert_pydantic_to_avro, convert_avro_binary_to_pydantic_instance,
    create_pydantic_model_from_avro_schema, is_prev_schema_compatible_with_next, are_schemas_compatible
)

class User(BaseModel):
    name: str
    age: int
    is_student: bool 
    gender: str
    birth_date: date
    last_login: datetime

valid_model_input = {
    "name": "Joåhn Doe",
    "age": 30,
    "is_student": False,
    "gender": "MALE",
    "birth_date": date(1990, 5, 20),
    "last_login": datetime(2022, 1, 1, 12, 0,0,0, tzinfo=timezone.utc),
}

class TestAvroModel(unittest.TestCase):

    def setUp(self):
        """Setup reusable model instance for tests."""
        self.model = User(**valid_model_input)

    def test_convert_pydantic_to_avro_values(self):
        avro_dict = convert_pydantic_to_avro(self.model)
       
        assert avro_dict["name"] == self.model.name
        assert avro_dict["age"] == self.model.age
        assert avro_dict["is_student"] == self.model.is_student
        assert avro_dict["gender"] == self.model.gender

        assert avro_dict["birth_date"] == 7444
        assert avro_dict["last_login"] == 1641038400000
    
    def test_convert_pydantic_to_avro_binary(self):
        avro_bin = convert_pydantic_to_avro_binary(self.model)
        model_instance = convert_avro_binary_to_pydantic_instance(avro_bin, User)
       
        assert model_instance.name == self.model.name
        assert model_instance.age == self.model.age
        assert model_instance.is_student == self.model.is_student
        assert model_instance.gender == self.model.gender

        assert model_instance.birth_date == self.model.birth_date
        assert model_instance.last_login == self.model.last_login

    def test_create_pydantic_model_by_avro_scheme(self):

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

        model_instance = ModelClass(**valid_model_input)

        assert model_instance.name == self.model.name
        assert model_instance.age == self.model.age
        assert model_instance.is_student == self.model.is_student
        assert model_instance.gender == self.model.gender

        assert model_instance.birth_date == self.model.birth_date
        assert model_instance.last_login == self.model.last_login

        with self.assertRaises(Exception):
            invalid_model_input = {**valid_model_input, "name": None}
            model_instance = ModelClass(**invalid_model_input)


    def test_is_prev_schema_compatible_with_next(self):
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

    def test_is_schemas_compatibles(self):
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

import pytest
import json
import os
print("PYTHONPATH: ", os.getenv('PYTHONPATH'))



from codable.formats.json import JSONCodec
from codable.serialization import (
    Encodable,
    Decodable,
    KeyedEncodingContainer,
    KeyedDecodingContainer,
    AutoEncodable,
    AutoDecodable
)

class EncodableClassForTesting(Encodable, Decodable):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def encode(self, container: KeyedEncodingContainer):
        container.encode("name", self.name)
        container.encode("value", self.value)

    @classmethod
    def decode(cls, container: KeyedDecodingContainer):
        name = container.decode("name")
        value = container.decode("value")
        return cls(name, value)


    def __repr__(self):
        return f"EncodableClassForTesting ({self.name}: {self.value})"

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

    def __hash__(self):
        return hash((self.name, self.value))


class AutoEncodableClassForTesting(AutoEncodable, AutoDecodable):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return f"AutoEncodableClassForTesting ({self.name}: {self.value})"

    def __repr__(self):
        return f"AutoEncodableClassForTesting ({self.name}: {self.value})"
    
    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

    def __hash__(self):
        return hash((self.name, self.value))

class AnotherTestEncodableClass(Encodable, Decodable):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def encode(self, container: KeyedEncodingContainer):
        container.encode("name", self.name)
        container.encode("value", self.value)

    @classmethod
    def decode(cls, container: KeyedDecodingContainer):
        name = container.decode("name")
        value = container.decode("value")
        return cls(name, value)

    def __repr__(self):
        return f"AnotherTestEncodableClass ({self.name}: {self.value})"

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

    def __hash__(self):
        return hash((self.name, self.value))


def test_encodable_serialization():
    obj = EncodableClassForTesting(name="test", value=123)
    encoded_obj = JSONCodec.encode(obj)
    expected_json = '{"name": "test", "value": 123, "__type__": "EncodableClassForTesting"}'
    assert encoded_obj == expected_json

def test_encodable_deserialization():
    json_data = '{"name": "test", "value": 123, "__type__": "EncodableClassForTesting"}'
    decoded_obj = JSONCodec.decode(json_data)
    assert decoded_obj == EncodableClassForTesting(name="test", value=123)

def test_autoencodable_serialization():
    obj = AutoEncodableClassForTesting(name="test", value=123)
    encoded_obj = JSONCodec.encode(obj)
    expected_json = '{"name": "test", "value": 123, "__type__": "AutoEncodableClassForTesting"}'
    assert encoded_obj == expected_json

def test_autoencodable_deserialization():
    json_data = '{"name": "test", "value": 123, "__type__": "AutoEncodableClassForTesting"}'
    decoded_obj = JSONCodec.decode(json_data)
    assert decoded_obj == AutoEncodableClassForTesting(name="test", value=123)

def test_registering_multiple_types():
    obj = AnotherTestEncodableClass(name="test2", value=456)
    encoded_obj = JSONCodec.encode(obj)
    expected_json = '{"name": "test2", "value": 456, "__type__": "AnotherTestEncodableClass"}'
    assert encoded_obj == expected_json

    json_data = '{"name": "test2", "value": 456, "__type__": "AnotherTestEncodableClass"}'
    decoded_obj = JSONCodec.decode(json_data)
    assert decoded_obj == AnotherTestEncodableClass(name="test2", value=456)


def test_same_class_name():
    obj = EncodableClassForTesting(name="test3", value=789)
    encoded_obj = JSONCodec.encode(obj)
    expected_json = '{"name": "test3", "value": 789, "__type__": "EncodableClassForTesting"}'
    assert encoded_obj == expected_json

    json_data = '{"name": "test3", "value": 789, "__type__": "EncodableClassForTesting"}'
    decoded_obj = JSONCodec.decode(json_data)
    assert decoded_obj == EncodableClassForTesting(name="test3", value=789)

def test_edge_cases():
    # Test empty object
    obj = EncodableClassForTesting(name="", value=0)
    encoded_obj = JSONCodec.encode(obj)
    expected_json = '{"name": "", "value": 0, "__type__": "EncodableClassForTesting"}'
    assert encoded_obj == expected_json

    json_data = '{"name": "", "value": 0, "__type__": "EncodableClassForTesting"}'
    decoded_obj = JSONCodec.decode(json_data)
    assert decoded_obj == EncodableClassForTesting(name="", value=0)

    # Test None values
    obj = EncodableClassForTesting(name=None, value=None)
    encoded_obj = JSONCodec.encode(obj)
    expected_json = '{"name": null, "value": null, "__type__": "EncodableClassForTesting"}'
    assert encoded_obj == expected_json

    json_data = '{"name": null, "value": null, "__type__": "EncodableClassForTesting"}'
    decoded_obj = JSONCodec.decode(json_data)
    assert decoded_obj == EncodableClassForTesting(name=None, value=None)


if __name__ == '__main__':
    pytest.main(["-s"])
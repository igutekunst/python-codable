import pytest
from codable.serialization import KeyedEncodingContainer, KeyedDecodingContainer, UnkeyedEncodingContainer, UnkeyedDecodingContainer, Encodable, Decodable, AutoEncodable, AutoDecodable
from codable.formats.json import JSONCodec
from tests.test_coding_containers import EncodableClassForTesting, AutoEncodableClassForTesting
import json

class NestedEncodableClass(Encodable, Decodable):
    def __init__(self, name, nested):
        self.name = name
        self.nested = nested

    def encode(self, container: KeyedEncodingContainer):
        container.encode("name", self.name)
        container.encode("nested", self.nested)

    @classmethod
    def decode(cls, container: KeyedDecodingContainer):
        name = container.decode("name")
        nested = container.decode("nested")
        return cls(name, nested)

    def __repr__(self):
        return f"NestedEncodableClass ({self.name}: {self.nested})"

    def __eq__(self, other):
        return self.name == other.name and self.nested == other.nested

    def __hash__(self):
        return hash((self.name, self.nested))

class AutoNestedEncodableClass(AutoEncodable, AutoDecodable):
    def __init__(self, name, nested):
        self.name = name
        self.nested = nested

    def __repr__(self):
        return f"AutoNestedEncodableClass ({self.name}: {self.nested})"

    def __eq__(self, other):
        return self.name == other.name and self.nested == other.nested

    def __hash__(self):
        return hash((self.name, self.nested))

def test_nested_encodable_serialization():
    nested_obj = EncodableClassForTesting(name="nested", value=456)
    obj = NestedEncodableClass(name="test", nested=nested_obj)
    encoded_obj = JSONCodec.encode(obj)
    expected_json = '{"name": "test", "nested": {"name": "nested", "value": 456, "__type__": "EncodableClassForTesting"}, "__type__": "NestedEncodableClass"}'
    assert encoded_obj == expected_json

def test_nested_encodable_deserialization():
    json_data = '{"name": "test", "nested": {"name": "nested", "value": 456, "__type__": "EncodableClassForTesting"}, "__type__": "NestedEncodableClass"}'
    decoded_obj = JSONCodec.decode(json_data)
    nested_obj = EncodableClassForTesting(name="nested", value=456)
    assert decoded_obj == NestedEncodableClass(name="test", nested=nested_obj)

class AutoDictEncodableClass(AutoEncodable, AutoDecodable):
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def __repr__(self):
        return f"AutoDictEncodableClass ({self.name}: {self.data})"

    def __eq__(self, other):
        return self.name == other.name and self.data == other.data

    def __hash__(self):
        return hash((self.name, tuple(self.data.items())))

def test_dict_serialization():
    obj = AutoDictEncodableClass(name="test", data={"key1": "value1", "key2": 123, "key3": {"nestedKey": "nestedValue"}})
    encoded_obj = JSONCodec.encode(obj)
    expected_json = '{"name": "test", "data": {"key1": "value1", "key2": 123, "key3": {"nestedKey": "nestedValue"}}, "__type__": "AutoDictEncodableClass"}'
    assert encoded_obj == expected_json

def test_dict_deserialization():
    json_data = '{"name": "test", "data": {"key1": "value1", "key2": 123, "key3": {"nestedKey": "nestedValue"}}, "__type__": "AutoDictEncodableClass"}'
    decoded_obj = JSONCodec.decode(json_data)
    expected_obj = AutoDictEncodableClass(name="test", data={"key1": "value1", "key2": 123, "key3": {"nestedKey": "nestedValue"}})
    assert decoded_obj == expected_obj

def test_array_serialization():
    obj = AutoDictEncodableClass(name="test", data=["value1", 123, {"nestedKey": "nestedValue"}])
    encoded_obj = JSONCodec.encode(obj)
    expected_json = '{"name": "test", "data": ["value1", 123, {"nestedKey": "nestedValue"}], "__type__": "AutoDictEncodableClass"}'
    assert encoded_obj == expected_json

def test_array_deserialization():
    json_data = '{"name": "test", "data": ["value1", 123, {"nestedKey": "nestedValue"}], "__type__": "AutoDictEncodableClass"}'
    decoded_obj = JSONCodec.decode(json_data)
    expected_obj = AutoDictEncodableClass(name="test", data=["value1", 123, {"nestedKey": "nestedValue"}])
    assert decoded_obj == expected_obj


if __name__ == "__main__":
    pytest.main(["-s"])
import pytest
from codable.serialization import EncodingContainer, DecodingContainer, Encodable, Decodable, AutoEncodable, AutoDecodable
from codable.formats.json import JSONCodec
from tests.test_coding_containers import EncodableClassForTesting, AutoEncodableClassForTesting

class NestedEncodableClass(Encodable, Decodable):
    def __init__(self, name, nested):
        self.name = name
        self.nested = nested

    def encode(self, container: EncodingContainer):
        container.encode("name", self.name)
        container.encode("nested", self.nested)

    @classmethod
    def decode(cls, container: DecodingContainer):
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
    expected_json = '{"name": "test", "nested": {"name": "nested", "value": 456, "__type__": "EncodableClassForTesting"}, "__type__": "EncodableClassForTesting"}'
    assert encoded_obj == expected_json

def test_nested_encodable_deserialization():
    json_data = '{"name": "test", "nested": {"name": "nested", "value": 456, "__type__": "EncodableClassForTesting"}, "__type__": "NestedEncodableClass"}'
    decoded_obj = JSONCodec.decode(json_data)
    nested_obj = EncodableClassForTesting(name="nested", value=456)
    assert decoded_obj == NestedEncodableClass(name="test", nested=nested_obj)


if __name__ == "__main__":
    pytest.main(["-s"])
import pytest
from codable.formats.sample_json import JSONFooCodec
from codable.serialization import AutoDecodable, AutoEncodable


class AutoEncodableClassForTesting(AutoEncodable, AutoDecodable):
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.l = ['one', 'two', 'three']

    def __str__(self):
        return f"AutoEncodableClassForTesting ({self.name}: {self.value})"

    def __repr__(self):
        return f"AutoEncodableClassForTesting ({self.name}: {self.value})"
    
    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

    def __hash__(self):
        return hash((self.name, self.value))

def test_encodable_serialization():
    obj = AutoEncodableClassForTesting(name="test", value=123)
    encoded_obj = JSONFooCodec.encode(obj)
    expected_json = '{"name": "test", "value": 123, "l": ["one", "two", "three"], "__type__": "AutoEncodableClassForTesting"}'
    assert encoded_obj == expected_json


if __name__ == '__main__':
    pytest.main(["-s"])
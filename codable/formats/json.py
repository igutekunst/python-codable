import json

from codable.serialization import CustomTypeRegistry, Decodable, custom_type_registry, Encodable
from codable.serialization import (
    SingleValueEncodingContainer,
    SingleValueDecodingContainer,
    KeyedEncodingContainer,
    KeyedDecodingContainer,
    UnkeyedEncodingContainer,
    UnkeyedDecodingContainer
)


class JSONKeyedEncodingContainer(KeyedEncodingContainer):
    def __init__(self, keypath=None):
        self.data = {}

        if keypath is None:
            keypath = []
        self.keypath = keypath

    def encode(self, key, value):
        new_keypath = self.keypath + [key]
        if isinstance(value, Encodable):
            container = JSONKeyedEncodingContainer(keypath=new_keypath)
            value.encode(container)
            container.encode("__type__", value.__class__.__name__)
        elif isinstance(value, dict):
            container = JSONKeyedEncodingContainer(keypath=new_keypath)
            for k, v in value.items():
                container.encode(k, v)
        elif isinstance(value, list):
            container = JSONUnkeyedEncodingContainer(keypath=new_keypath)
            for v in value:
                container.encode(v)

        else:
            container = JSONSingleValueEncodingContainer(value)
        self.data[key] = container

class JSONKeyedDecodingContainer(KeyedDecodingContainer):
    def __init__(self, data, keypath=None):
        self.data = data

        if keypath is None:
            keypath = []
        self.keypath = keypath

    def decode(self, key, default=None):
        value = self.data.get(key, default)
        if isinstance(value, dict):
            cls_name = value.get('__type__')
            if cls_name:
                cls = custom_type_registry.get_class(cls_name)
                if cls:
                    container = JSONKeyedDecodingContainer(value)
                    return cls.decode(container) # decode_from
            else:
                container = JSONKeyedDecodingContainer(value)
                return {k: container.decode(k) for k in value}
        return value

class JSONUnkeyedEncodingContainer(UnkeyedEncodingContainer):
    def __init__(self, keypath=None):
        self.data = []

        if keypath is None:
            keypath = []
        self.keypath = keypath

    def encode(self, value):
        new_keypath = self.keypath + [len(self.data)]
        if isinstance(value, Encodable):
            container = JSONKeyedEncodingContainer(keypath=new_keypath)
            value.encode(container)
        elif isinstance(value, list):
            container = JSONUnkeyedEncodingContainer(keypath=new_keypath)
            for item in value:
                container.encode(item)
        else:
            container = JSONSingleValueEncodingContainer(value, keypath=new_keypath)
        self.data.append(container)

class JSONUnkeyedDecodingContainer(UnkeyedDecodingContainer):
    def __init__(self, data, keypath=None):
        self.data = data

        if keypath is None:
            keypath = []
        self.keypath = keypath


    def decode(self, index, default=None):
        value = self.data[index] if index < len(self.data) else default
        if isinstance(value, dict):
            cls_name = value.get('__type__')
            if cls_name:
                cls = custom_type_registry.get_class(cls_name)
                if cls:
                    container = JSONKeyedDecodingContainer(value)
                    value.pop('__type__')
                    return cls.decode(container)
            else:
                container = JSONKeyedDecodingContainer(value)
                for k, v in value.items():
                    container.decode(k, v)
                return container
        elif isinstance(value, list):
            container = JSONUnkeyedDecodingContainer(value)
            return [container.decode(i) for i in range(len(value))]
        return value

class JSONSingleValueEncodingContainer(SingleValueEncodingContainer):
    def __init__(self, value, keypath=None):
        self.value= value

        if keypath is None:
            keypath = []
        self.keypath = keypath

class JSONSingleValueDecodingContainer(SingleValueDecodingContainer):
    def __init__(self, value, keypath=None):
        self.value = value

        if keypath is None:
            keypath = []
        self.keypath = keypath

class JSONCodec:
    @staticmethod
    def encode(obj: Encodable) -> str:
        if isinstance(obj, Encodable):
            container = JSONKeyedEncodingContainer()
            obj.encode(container)
            container.encode("__type__", obj.__class__.__name__)
            def get_dict(container):
                result = {}
                for key, value in container.data.items():
                    if isinstance(value, JSONKeyedEncodingContainer):
                            result[key] = get_dict(value)
                    elif isinstance(value, JSONUnkeyedEncodingContainer):
                        result[key] = get_list(value)
                    elif isinstance(value, JSONSingleValueEncodingContainer):
                        result[key] = value.value
                    else:
                        raise Exception(f"type {type(value)} should not get here.")
                return result

            def get_list(container):
                result = []
                for value in container.data:
                    if isinstance(value, JSONKeyedEncodingContainer):
                        result.append(get_dict(value))
                    elif isinstance(value, JSONUnkeyedEncodingContainer):
                        result.append(get_list(value))
                    elif isinstance(value, JSONSingleValueEncodingContainer):
                        result.append(value.value)
                    else:
                        raise Exception(f"type {type(value)} should not get here.")
                return result

            encoded_data = get_dict(container)
            return json.dumps(encoded_data)
        raise TypeError(f"Object of type {obj.__class__.__name__} is not Encodable")

    @staticmethod
    def decode(json_str: str) -> Decodable:
        data = json.loads(json_str)

        def decode_dict(data):
            if "__type__" in data:  # Check if the dictionary has a __type__ field
                cls_name = data["__type__"]  # Get the class name from the __type__ field
                cls = custom_type_registry.get_class(cls_name)  # Retrieve the class from the registry
                if cls and issubclass(cls, Decodable):  # Check if the class is a subclass of Decodable
                    container = JSONKeyedDecodingContainer(data)  # Create a decoding container
                    return cls.decode(container)  # Decode the object using the class's decode method
                else:
                    raise TypeError("JSON string does not contain a valid Decodable type")  # Raise error if not decodable
            else:
                return data  # Return the dictionary as is if no __type__ field

        def decode_list(data):
            result = []
            for item in data:
                if isinstance(item, dict):
                    result.append(decode_dict(item))
                elif isinstance(item, list):
                    result.append(decode_list(item))
                else:
                    result.append(item)
            return result

        if isinstance(data, dict):
            return decode_dict(data)
        elif isinstance(data, list):
            return decode_list(data)
        else:
            raise TypeError("JSON string does not contain a valid Decodable type")


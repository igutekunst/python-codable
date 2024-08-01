import json
from codable.serialization import SingleValueEncodingContainer, custom_type_registry, Encodable, Decodable, KeyedDecodingContainer, KeyedEncodingContainer, UnkeyedEncodingContainer, UnkeyedDecodingContainer


class JSONCodec:
    @staticmethod
    def encode(obj: Encodable) -> str:
        if isinstance(obj, Encodable):
            container = KeyedEncodingContainer()
            obj.encode(container)
            container.encode("__type__", obj.__class__.__name__)
            def get_dict(container):
                result = {}
                for key, value in container.data.items():
                    if isinstance(value, KeyedEncodingContainer):
                            result[key] = get_dict(value)
                    elif isinstance(value, UnkeyedEncodingContainer):
                        result[key] = get_list(value)
                    elif isinstance(value, SingleValueEncodingContainer):
                        result[key] = value.value
                    else:
                        raise Exception(f"type {type(value)} should not get here.")
                return result

            def get_list(container):
                result = []
                for value in container.data:
                    if isinstance(value, KeyedEncodingContainer):
                        result.append(get_dict(value))
                    elif isinstance(value, UnkeyedEncodingContainer):
                        result.append(get_list(value))
                    elif isinstance(value, SingleValueEncodingContainer):
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
                    container = KeyedDecodingContainer(data)  # Create a decoding container
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


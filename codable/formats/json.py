import json
from codable.serialization import custom_type_registry, Encodable, Decodable, KeyedDecodingContainer, KeyedEncodingContainer


class JSONCodec:
    @staticmethod
    def encode(obj: Encodable) -> str:
        if isinstance(obj, Encodable):
            container = KeyedEncodingContainer(obj.__class__.__name__)
            obj.encode(container)
            def get_dict(container):
                result = {}
                for key, value in container.data.items():
                    if isinstance(value, KeyedEncodingContainer):
                        if value.type_name == "dict":
                            result[key] = get_dict(value)
                        else:
                            result[key] = get_dict(value)
                            result[key]["__type__"] = value.type_name
                    else:
                        result[key] = value
                if container.type_name != "dict":
                    result["__type__"] = container.type_name
                return result

            encoded_data = get_dict(container)
            return json.dumps(encoded_data)
        raise TypeError(f"Object of type {obj.__class__.__name__} is not Encodable")

    @staticmethod
    def decode(json_str: str) -> Decodable:
        data = json.loads(json_str)
        if "__type__" in data:
            cls_name = data["__type__"]
            cls = custom_type_registry.get_class(cls_name)
            if cls and issubclass(cls, Decodable):
                container = KeyedDecodingContainer(data)
                return cls.decode(container)
        raise TypeError("JSON string does not contain a valid Decodable type")
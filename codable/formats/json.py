import json
from codable.serialization import custom_type_registry, Encodable, Decodable, DecodingContainer, EncodingContainer


class JSONCodec:
    @staticmethod
    def encode(obj: Encodable) -> str:
        if isinstance(obj, Encodable):
            container = EncodingContainer(obj.__class__.__name__)
            obj.encode(container)
            def get_dict(container):
                result = {}
                for key, value in container.data.items():
                    if isinstance(value, EncodingContainer):
                        result[key] = get_dict(value)
                    else:
                        result[key] = value
                result["__type__"] = container.type_name
                return result

            container.data = get_dict(container)
            return json.dumps(container.data)
        raise TypeError(f"Object of type {obj.__class__.__name__} is not Encodable")

    @staticmethod
    def decode(json_str: str) -> Decodable:
        data = json.loads(json_str)
        if "__type__" in data:
            cls_name = data["__type__"]
            cls = custom_type_registry.get_class(cls_name)
            if cls and issubclass(cls, Decodable):
                container = DecodingContainer(data)
                return cls.decode(container)
        raise TypeError("JSON string does not contain a valid Decodable type")
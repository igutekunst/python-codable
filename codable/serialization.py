import json
from django.http import JsonResponse as DjangoJsonResponse
from typing import Union, NamedTuple
from abc import ABC, ABCMeta, abstractmethod

class RegistryEntry(NamedTuple):
    cls: type
    encoder: json.JSONEncoder
    decoder: json.JSONDecoder

class CustomTypeRegistry:
    def __init__(self):
        self._registry: dict[str, RegistryEntry] = {}

    def register(self, cls, encoder, decoder):
        self._registry[cls.__name__] = RegistryEntry(cls, encoder, decoder)

    def get_encoder(self, cls) -> Union[json.JSONEncoder, None]:
        entry = self._registry.get(cls.__name__)
        return entry.encoder if entry else None

    def get_decoder(self, cls_name) -> Union[json.JSONDecoder, type, None]:
        entry = self._registry.get(cls_name)
        return entry.decoder if entry else None

    def get_class(self, cls_name) -> Union[type, None]:
        entry = self._registry.get(cls_name)
        return entry.cls if entry else None

# Create a global registry instance
custom_type_registry = CustomTypeRegistry()

class EncodingContainer:
    def __init__(self):
        self.data = {}

    def encode(self, key, value):
        self.data[key] = value

class DecodingContainer:
    def __init__(self, data):
        self.data = data

    def decode(self, key, default=None):
        return self.data.get(key, default)

@classmethod
def from_container(cls, container: DecodingContainer):
    instance = cls.__new__(cls)
    for key, value in container.data.items():
        if not key.startswith('_'):
            setattr(instance, key, value)
    return instance

def to_container(self) -> EncodingContainer:
    container = EncodingContainer()
    for k, v in self.__dict__.items():
        if not k.startswith('_'):
            container.encode(k, v)
    return container

class CodeableMeta(ABCMeta):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        if issubclass(cls, (globals().get('Encodable', object), globals().get('Decodable', object))) and cls not in (globals().get('Encodable', object), globals().get('Decodable', object)):
            custom_type_registry.register(cls, globals().get('ToDictJSONEncoder'), globals().get('FromDictJSONDecoder'))
        if issubclass(cls, globals().get('AutoEncodable', object)) and cls is not globals().get('AutoEncodable', object):
            cls.to_container = to_container
        if issubclass(cls, globals().get('AutoDecodable', object)) and cls is not globals().get('AutoDecodable', object):
            cls.from_container = from_container

class Encodable(ABC, metaclass=CodeableMeta):
    @abstractmethod
    def encode(self, container: EncodingContainer):
        pass

class Decodable(ABC, metaclass=CodeableMeta):
    @abstractmethod
    def decode(cls, container: DecodingContainer):
        pass

class AutoEncodable(Encodable, metaclass=CodeableMeta):
    def encode(self, container: EncodingContainer):
        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                container.encode(k, v)

    def __hash__(self):
        return hash(tuple((k, v) for k, v in self.__dict__.items() if not k.startswith('_')))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return all(
            getattr(self, k) == getattr(other, k)
            for k in self.__dict__.keys()
            if not k.startswith('_')
        )
    

class AutoDecodable(Decodable, metaclass=CodeableMeta):
    @classmethod
    def decode(cls, container: DecodingContainer):
        instance = cls.__new__(cls)
        for key, value in container.data.items():
            if not key.startswith('_'):
                setattr(instance, key, value)
        return instance

    def __hash__(self):
        return hash(tuple((k, v) for k, v in self.__dict__.items() if not k.startswith('_')))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return all(
            getattr(self, k) == getattr(other, k)
            for k in self.__dict__.keys()
            if not k.startswith('_')
        )

class ToDictJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Encodable):
            container = obj.to_container()
            container.data["__type__"] = obj.__class__.__name__
            return container.data
        return super().default(obj)

class FromDictJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if "__type__" in dct:
            Class = custom_type_registry.get_class(dct["__type__"])
            if Class:
                container = DecodingContainer(dct)
                return Class.from_container(container)
        return dct

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Encodable):
            encoder = ToDictJSONEncoder
        else:
            encoder = custom_type_registry.get_encoder(type(obj))
        if encoder:
            return encoder().default(obj)  # Use the default method of the encoder instance
        return super().default(obj)

class CustomJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if "__type__" in dct:
            decoder = custom_type_registry.get_decoder(dct["__type__"])
            if not decoder:
                return dct
            return decoder().object_hook(dct)
        return dct

class JsonResponse(DjangoJsonResponse):
    def __init__(self, data, encoder=CustomJSONEncoder, safe=True, json_dumps_params=None, **kwargs):
        if json_dumps_params is None:
            json_dumps_params = {}
        json_dumps_params['cls'] = encoder
        super().__init__(data, safe=safe, json_dumps_params=json_dumps_params, **kwargs)

# Example

class TestEncodableClass(Encodable, Decodable):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def encode(self, container: EncodingContainer):
        container.encode("name", self.name)
        container.encode("value", self.value)

    @classmethod
    def decode(cls, container: DecodingContainer):
        name = container.decode("name")
        value = container.decode("value")
        return cls(name, value)


class TestAutoEncodableClass(AutoEncodable, AutoDecodable):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return f"TestAutoEncodableClass ({self.name}: {self.value})"


def loads(data, decoder=CustomJSONDecoder):
    return json.loads(data, cls=decoder)

def dumps(data, encoder=CustomJSONEncoder):
    return json.dumps(data, cls=encoder)
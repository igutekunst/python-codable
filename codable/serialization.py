import json
from typing import NamedTuple, Union, Any
from abc import ABC, ABCMeta, abstractmethod

class RegistryEntry(NamedTuple):
    cls: type
    encoder: Any
    decoder: Any

class CustomTypeRegistry:
    def __init__(self):
        self._registry: dict[str, RegistryEntry] = {}

    def register(self, cls, encoder=None, decoder=None):
        if cls.__name__ in self._registry:
            existing_entry = self._registry[cls.__name__]
            new_encoder = encoder if encoder is not None else existing_entry.encoder
            new_decoder = decoder if decoder is not None else existing_entry.decoder
            self._registry[cls.__name__] = RegistryEntry(cls, new_encoder, new_decoder)
        else:
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
        base_classes = {'Encodable', 'Decodable', 'AutoEncodable', 'AutoDecodable'}
        if name in base_classes:
            return
        auto_encodable = globals().get('AutoEncodable', object)
        auto_decodable = globals().get('AutoDecodable', object)
        encodable = globals().get('Encodable', object)
        decodable = globals().get('Decodable', object)
        if issubclass(cls, encodable) and cls is not encodable:
            custom_type_registry.register(cls, cls.encode)
        if issubclass(cls, decodable) and cls is not decodable:
            custom_type_registry.register(cls, cls.decode)

        if issubclass(cls, auto_encodable) and cls is not auto_encodable:
            cls.to_container = to_container
        if issubclass(cls, auto_decodable) and cls is not auto_decodable:
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

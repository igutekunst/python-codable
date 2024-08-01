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


class KeyedEncodingContainer(ABC):
    pass

class KeyedDecodingContainer(ABC):
    pass

class UnkeyedEncodingContainer(ABC):
    pass

class UnkeyedDecodingContainer(ABC):
    pass

class SingleValueEncodingContainer(ABC):
    pass

class SingleValueDecodingContainer(ABC):
    pass

class CodeableMeta(ABCMeta):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        base_classes = {'Encodable', 'Decodable', 'AutoEncodable', 'AutoDecodable'}
        if name in base_classes:
            return
        encodable = globals().get('Encodable', object)
        decodable = globals().get('Decodable', object)
        if issubclass(cls, encodable) and cls is not encodable:
            custom_type_registry.register(cls, cls.encode)
        if issubclass(cls, decodable) and cls is not decodable:
            custom_type_registry.register(cls, cls.decode)


class Encodable(ABC, metaclass=CodeableMeta):
    @abstractmethod
    def encode(self, container: KeyedEncodingContainer):
        pass

class Decodable(ABC, metaclass=CodeableMeta):
    @abstractmethod
    def decode(cls, container: KeyedDecodingContainer):
        pass

class Codable(Encodable, Decodable):
    pass

class AutoEncodable(Encodable, metaclass=CodeableMeta):
    def encode(self, container: KeyedEncodingContainer):
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
    def decode(cls, container: KeyedDecodingContainer):
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

class AutoCodable(Codable, AutoEncodable, AutoDecodable):
    pass
""" Notes

Top Level Encoder:
    1. It is passed a Encodable type
    2. It creates a KeyedEncodingContainer.
    3. It asks the Encodable to encode itself into the container
        container.encode("__type__", typename)
        Encodable.encode_into(container)

        4: Inside of Encodable:
            1) Loops over all properties:
                for key, value in properties:
                    container.encode(key, value)

        5) Inside of KeyedCodingContainer.encode(key, value)
            path=keypath + [key]
            switch (type(value)) {
                case Terminal:
                    container = SingleValueEncodingContainer(value)
                case Encodable:
                    container = KeyEncodingContainer()
                    container.encode("__type__", typename(value))
                    value.encode_into(container)
                case dict:
                    container = KeyEncodingContainer()
                    # container.encode("__type__", "__dict__) ?
                    for nested_key, nested_value in value.items():
                        container.encode(key, value)
                case list:
                    container = UnKeyEncodingContainer()
                    for index, value in iter(value):
                        container.encode(value)

                encoded_value = container
                self.data[key] = encoded_value
            }

Some unresolved questions:
    Should the __type__ be added inside Encodable.encode_to() ?
        Pros: 
            - no logic is needed inside of the KeyedEncodingContainer
            - Object can decide how to tag its type
        Cons: 
            - Since decoding requires looking at the type before selecting the
                appropriate calss to call .decode_from(), then it's not symmetric
            - Object can decide how to tag its type, which could be a problem


"""
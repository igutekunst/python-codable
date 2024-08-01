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

class KeyedEncodingContainer:
    def __init__(self, keypath=None):
        self.data = {}

        if keypath is None:
            keypath = []
        self.keypath = keypath

    def encode(self, key, value):
        new_keypath = self.keypath + [key]
        if isinstance(value, Encodable):
            container = KeyedEncodingContainer(keypath=new_keypath)
            value.encode(container)
            container.encode("__type__", value.__class__.__name__)
        elif isinstance(value, dict):
            container = KeyedEncodingContainer(keypath=new_keypath)
            for k, v in value.items():
                container.encode(k, v)
        elif isinstance(value, list):
            container = UnkeyedEncodingContainer(keypath=new_keypath)
            for v in value:
                container.encode(v)

        else:
            container = SingleValueEncodingContainer(value)
        self.data[key] = container

class KeyedDecodingContainer:
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
                    container = KeyedDecodingContainer(value)
                    return cls.decode(container) # decode_from
            else:
                container = KeyedDecodingContainer(value)
                return {k: container.decode(k) for k in value}
        return value

class UnkeyedEncodingContainer:
    def __init__(self, keypath=None):
        self.data = []

        if keypath is None:
            keypath = []
        self.keypath = keypath

    def encode(self, value):
        new_keypath = self.keypath + [len(self.data)]
        if isinstance(value, Encodable):
            container = KeyedEncodingContainer(keypath=new_keypath)
            value.encode(container)
        elif isinstance(value, list):
            container = UnkeyedEncodingContainer(keypath=new_keypath)
            for item in value:
                container.encode(item)
        else:
            container = SingleValueEncodingContainer(value, keypath=new_keypath)
        self.data.append(container)

class UnkeyedDecodingContainer:
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
                    container = KeyedDecodingContainer(value)
                    value.pop('__type__')
                    return cls.decode(container)
            else:
                container = KeyedDecodingContainer(value)
                for k, v in value.items():
                    container.decode(k, v)
                return container
        elif isinstance(value, list):
            container = UnkeyedDecodingContainer(value)
            return [container.decode(i) for i in range(len(value))]
        return value

class SingleValueEncodingContainer:
    def __init__(self, value, keypath=None):
        self.value= value

        if keypath is None:
            keypath = []
        self.keypath = keypath

class SingleValueDecodingContainer:
    def __init__(self, value, keypath=None):
        self.value = value

        if keypath is None:
            keypath = []
        self.keypath = keypath

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
from codable.serialization import Codable, Encodable, Decodable, AutoEncodable, AutoDecodable, AutoCodable

def encodable(cls):
    class NewClass(cls, Encodable):
        pass
    NewClass.__name__ = cls.__name__
    NewClass.__module__ = cls.__module__
    return NewClass

def decodable(cls):
    class NewClass(cls, Decodable):
        pass
    NewClass.__name__ = cls.__name__
    NewClass.__module__ = cls.__module__
    return NewClass

def codable(cls):
    class NewClass(cls, Codable):
        pass
    NewClass.__name__ = cls.__name__
    NewClass.__module__ = cls.__module__
    return NewClass

def auto_encodable(cls):
    class NewClass(cls, AutoEncodable):
        pass
    NewClass.__name__ = cls.__name__
    NewClass.__module__ = cls.__module__
    return NewClass

def auto_decodable(cls):
    class NewClass(cls, AutoDecodable):
        pass
    NewClass.__name__ = cls.__name__
    NewClass.__module__ = cls.__module__
    return NewClass

def auto_codable(cls):
    class NewClass(cls, AutoCodable):
        pass
    NewClass.__name__ = cls.__name__
    NewClass.__module__ = cls.__module__
    return NewClass
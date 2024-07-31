# Codable

Codable is a Python module for encoding and decoding objects using customizable serialization. It allows you to easily convert your Python objects to and from JSON, with support for custom encoders and decoders. This module is designed to be flexible and extensible, making it easy to work with complex data structures and custom object types.

## Features

- **Customizable Serialization**: Define your own encoders and decoders to handle specific object types.
- **Automatic Encoding/Decoding**: Use the built-in `AutoEncodable` and `AutoDecodable` classes to automatically handle common serialization tasks.
- **Helpful Decorators**: Use decorators to quickly make classes Codable.
- **Integration with Django**: Includes a custom `JsonResponse` class that integrates with Django's HTTP response system.

## Installation

To install Codable, use pip:
```bash
    pip install codeble
```

## Examples

### Example: Using `@auto_codable` for a Simple Class Describing a Person

Here's an example of how to use the `@auto_codable` decorator to make a simple class describing a person automatically encodable and decodable.

```Python
from codable.decorators import auto_codable
from codable.formats.json import JSONCodec

@auto_codable
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

# Create an instance of the Person class
person = Person(name="John Doe", age=30)

# Encode the person object to JSON
encoded_person = JSONCodec.encode(person)
print(f"Encoded JSON: {encoded_person}")

# Decode the JSON back to a Person object
decoded_person = JSONCodec.decode(encoded_person)
print(f"Decoded Person: {decoded_person}")

```

### Example: Making an AutoCodable subclass

```Python
from codable.auto import AutoCodable
from codable.formats.json import JSONCodec

class Employee(AutoCodable):
    def __init__(self, employee_id, name, position):
        self.employee_id = employee_id
        self.name = name
        self.position = position

# Create an instance of the Employee class
employee = Employee(employee_id=123, name="Jane Smith", position="Developer")

# Encode the employee object to JSON
encoded_employee = JSONCodec.encode(employee)
print(f"Encoded JSON: {encoded_employee}")

# Decode the JSON back to an Employee object
decoded_employee = JSONCodec.decode(encoded_employee)
print(f"Decoded Employee: {decoded_employee}")

```





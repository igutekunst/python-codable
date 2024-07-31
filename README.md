# Codable

Codable is a Python module for encoding and decoding objects using customizable serialization. It allows you to easily convert your Python objects to and from JSON, with support for custom encoders and decoders. This module is designed to be flexible and extensible, making it easy to work with complex data structures and custom object types.

## Features

- **Customizable Serialization**: Define your own encoders and decoders to handle specific object types.
- **Automatic Encoding/Decoding**: Use the built-in `AutoEncodable` and `AutoDecodable` classes to automatically handle common serialization tasks.
- **Registry-Based System**: Register your custom types with a global registry for easy access and management.
- **Integration with Django**: Includes a custom `JsonResponse` class that integrates with Django's HTTP response system.

## Installation

To install Codable, use pip:
```bash
    pip install codeable
```

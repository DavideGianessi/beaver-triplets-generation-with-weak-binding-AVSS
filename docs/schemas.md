# Schemas

Schemas are used to ensure that a message has the correct structure when it arrives, so we can assume when writing the handlers that the messages may have wrong values due to malicious adversaries, but at least have the correct structure, or it woould have been discarded by the dispatcher. This makes the handlers code much cleaner, as they now only have to worry about the actual protocol definition

## Example


```python
SCHEMA = {
    "type": "dict",
    "keys": {
        "username": {"type": "str", "regex": r"^[a-zA-Z0-9_]{3,16}$"},
        "age": {"type": "int", "min": 0, "max": 120},
        "data": {"type": "bytes", "len": 16},
        "tags": {
            "type": "list",
            "len": 3,
            "items": {"type": "str", "regex": r"^\w+$"},
        },
    },
}

data = {
    "username": "user_123",
    "age": 25,
    "data": b"1234567890abcdef",
    "tags": ["one", "two", "three"],
}

print(validate(data, SCHEMA))  # True

bad_data = {
    "username": "user_123!",
    "age": -1,
    "data": b"xx",
    "tags": ["one", "two"],
}

print(validate(bad_data, SCHEMA))  # False
```


## Dicts

All the keys have predefined string names, then define for each key the schema of the value

## Lists

len is the lenght that the list must have, provide the schema that all items of that list must satisfay

## Bytes

must have the specified len

## Integers

min and max inclusive can be specified

## Strings

a regex may be specified

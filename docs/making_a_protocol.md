# Making a Protocol

A new protocol must extend the abstract class `BaseProtocol`.

## Requirements

- The protocol must define **at compile time**:
  - The list of messages it involves → `get_messages()`
  - The subprotocols it starts → `get_subprotocols()`

- The protocol’s constructor must accept the following arguments:

```python
def __init__(self, manager, path, params):
    super().__init__(manager, path)
    # params may contain input data for the protocol
```

- The protocol must define a **message handler** with this signature:

```python
def handle_message(self, message, by, data):
    """
    message: str   # message name
    by: int        # PARTY_ID of the sender
    data: bytes    # message payload
    """
```

- The protocol must define a **subprotocol handler** with this signature:

```python
def handle_subprotocol(self, subprotocol, index, result):
    """
    subprotocol: str   # subprotocol name
    index: int         # instance number (the number after "_" in the ID)
    result: any        # returned value from the subprotocol
    """
```

## Allowed Interactions

Within these handlers, the protocol may only interact with the rest of the program through the following methods:

- `self.start_subprotocol(protocol_name_with_index, params={})`  
  Starts a new subprotocol.

- `self.stop()`  
  Ensures the protocol is no longer useful to anyone else before calling this (e.g., it has already sent all messages it could).  
  Follow with `return` to terminate execution of the handler.

- `self.return_result(result_dict)`  
  Sends the result to the parent protocol’s handler.  
  This should only be called once.  
  **Note:** It does not stop the protocol; you must call `self.stop()` explicitly.

- `self.send_message(to, message_name, data)`  
  Sends a message to another party.

- `log(string)`  
  Writes the given string to a file in the `outputs/` directory.

# Structure

```
├── LICENSE
├── README.md
├── docs
│   └── documentation
├── outputs
│   ├── output*.txt
│   └── router.txt
├── party
│   ├── Dockerfile
│   ├── config.py
│   ├── party.py
│   ├── protocol_finder.py
│   ├── protocol_manager.py
│   ├── protocols
│   │   ├── __init__.py
│   │   ├── baseProtocol.py
│   │   └── Protocol1
│   │       ├── __init__.py
│   │       └── protocol1.py
│   ├── requirements.txt
│   ├── type_defs
│   │   ├── type1.py
│   │   └── __init__.py
│   └── util
│       ├── __init__.py
│       ├── logging.py
│       ├── networking.py
│       └── paths.py
│       └── schemas.py
├── router
│   ├── Dockerfile
│   ├── requirements.txt
│   └── router.py
└── start.sh
```

## File/Module Descriptions

- **config.py**: Defines the parameters for the protocol (e.g., number of parties involved). Values are taken from environment variables.  
- **party.py**: Entrypoint for the party process.  
- **protocol_manager.py**: Controls the flow of protocol execution.  
- **protocol_finder.py**: Maps protocol names to their corresponding classes.  
- **baseProtocol.py**: Abstract class that all protocols must extend. It abstracts the need to handle the path ID.

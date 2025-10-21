import re

def validate(value, schema):
    t = schema.get("type")

    # --- ints ---
    if t == "int":
        if not isinstance(value, int):
            return False
        if "min" in schema and value < schema["min"]:
            return False
        if "max" in schema and value > schema["max"]:
            return False
        return True

    # --- strings ---
    elif t == "str":
        if not isinstance(value, str):
            return False
        if "regex" in schema:
            if not re.fullmatch(schema["regex"], value):
                return False
        return True

    # --- bytes ---
    elif t == "bytes":
        if not isinstance(value, bytes):
            return False
        if "len" in schema and len(value) != schema["len"]:
            return False
        return True

    # --- lists ---
    elif t == "list":
        if not isinstance(value, list):
            return False
        if "len" in schema and len(value) != schema["len"]:
            return False
        item_schema = schema.get("items")
        if item_schema:
            for v in value:
                if not validate(v, item_schema):
                    return False
        return True

    # --- dicts ---
    elif t == "dict":
        if not isinstance(value, dict):
            return False
        expected_keys = schema.get("keys", {})
        for k, sub_schema in expected_keys.items():
            if k not in value:
                return False
            if not validate(value[k], sub_schema):
                return False
        return True

    else:
        # unknown type
        return False

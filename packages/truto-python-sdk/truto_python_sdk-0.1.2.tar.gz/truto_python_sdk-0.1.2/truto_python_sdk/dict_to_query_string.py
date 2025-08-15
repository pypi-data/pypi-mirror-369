from urllib.parse import urlencode, quote_plus
import datetime


def _convert_to_query_params(prefix, data):
    """
    Recursively convert a Python dictionary, list, or primitive into a valid
    HTTP query parameter string.
    """
    params = []

    if isinstance(data, dict):
        # Recursively handle dictionaries (objects)
        for key, value in data.items():
            new_prefix = f"{prefix}[{key}]" if prefix else key
            params.extend(_convert_to_query_params(new_prefix, value))
    elif isinstance(data, list):
        # Handle lists (arrays)
        for item in data:
            new_prefix = f"{prefix}[]"
            params.extend(_convert_to_query_params(new_prefix, item))
    else:
        # Base case for strings, numbers, booleans, and date/time
        if isinstance(data, (datetime.date, datetime.datetime)):
            # Convert date/time to ISO 8601 format
            data = data.isoformat()
        elif isinstance(data, bool):
            # Convert booleans to lowercase string "true" or "false"
            data = str(data).lower()

        params.append((prefix, data))

    return params


def dict_to_query_string(data):
    """
    Convert a Python dictionary into a valid HTTP query string with proper encoding.
    """
    query_params = []
    for key, value in data.items():
        query_params.extend(_convert_to_query_params(key, value))

    return urlencode(query_params, doseq=True, quote_via=quote_plus)
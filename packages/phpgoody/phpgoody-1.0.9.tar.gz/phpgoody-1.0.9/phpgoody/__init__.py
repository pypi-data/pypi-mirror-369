"""
Implement php functions in python
"""
from urllib.parse import ParseResult


def time():
    """
    Return current unix timestamp
    """
    import datetime

    return int(datetime.datetime.now().timestamp())


def date(format_: str, timestamp: int = None):
    """
    Format a local time/date
    """
    import datetime

    if timestamp is None:
        return datetime.datetime.now().strftime(format_)

    return datetime.datetime.fromtimestamp(timestamp).strftime(format_)


def date_default_timezone_set(timezone: str):
    """
    Sets the default timezone used by all date/time functions in a script
    """
    import os
    import time

    os.environ["TZ"] = timezone
    time.tzset()


def is_file(filename: str) -> bool:
    """
    Checks whether a file or directory exists
    """
    import os

    return os.path.isfile(filename)


def file_exists(filename: str) -> bool:
    """
    Checks whether a file or directory exists.
    """
    import os

    return os.path.exists(filename)


def each(array: list | dict):
    """
    Return the current key and value pair from an array and advance the array cursor
    """
    for key, value in enumerate(array) if isinstance(array, list) else array.items():
        yield key, value


def json_decode(json_string: str):
    """
    Decodes a JSON string
    """
    import json

    return json.loads(json_string)


def json_encode(data) -> str:
    """
    Returns the JSON representation of a value
    """
    import json
    from collections.abc import Mapping, Iterable
    from decimal import Decimal

    class DecimalEncoder(json.JSONEncoder):
        def encode(self, obj):
            if isinstance(obj, Mapping):
                return "{" + ", ".join(f"{self.encode(k)}: {self.encode(v)}" for (k, v) in obj.items()) + "}"
            if isinstance(obj, Iterable) and (not isinstance(obj, str)):
                return "[" + ", ".join(map(self.encode, obj)) + "]"
            if isinstance(obj, Decimal):
                # using normalize() gets rid of trailing 0s, using ':f' prevents scientific notation
                return f"{obj.normalize():f}"
            return super().encode(obj)

    return json.dumps(data, cls=DecimalEncoder, default=str)


def file_put_contents(filename: str, data: str):
    """
    Write data to a file
    """
    with open(filename, "w", encoding="utf-8") as file:
        file.write(data)

    return len(data)


def array_map(callback, array: list):
    """
    Applies the callback to the elements of the given arrays
    """
    return [callback(value) for value in array]


def file_get_contents(filename: str):
    """
    Reads entire file into a string
    """
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()


def preg_match(pattern: str, subject: str):
    """
    Perform a regular expression match
    """
    import re

    match = re.search(pattern, subject)

    return match.groups() if match else None


def strtotime(datetime_: str, base_timestamp: int = None) -> int:
    """
    Parse about any English textual datetime description into a Unix timestamp
    """
    import datetime
    import dateutil.relativedelta

    if base_timestamp is None:
        base_timestamp = time()

    base = datetime.datetime.fromtimestamp(base_timestamp)

    if datetime_ == "now":
        return base_timestamp

    if datetime_ == "tomorrow":
        return int((base + datetime.timedelta(days=1)).timestamp())

    if datetime_ == "yesterday":
        return int((base - datetime.timedelta(days=1)).timestamp())

    matches = preg_match(r"^(-?\d+)\s(days|day|year|years)?$", datetime_)
    if matches:
        matches = list(matches)
        if matches[1] == "year":
            matches[1] = "years"
        if matches[1] == "day":
            matches[1] = "days"

        return int((
                           base + dateutil.relativedelta.relativedelta(**{matches[1]: int(matches[0])})
                   ).timestamp())

    return -1


def str_ends_with(haystack: str, needle: str) -> bool:
    """
    Check if a string ends with a specific string
    """
    return haystack.endswith(needle)


def str_starts_with(haystack: str, needle: str) -> bool:
    """
    Check if a string starts with a specific string
    """
    return haystack.startswith(needle)


def array_merge(*arrays: list | dict) -> list | dict:
    """
    Merge one or more arrays
    """
    if isinstance(arrays[0], dict):
        result = {}
        for array in arrays:
            result = {**result, **array}

        return result

    result = []
    for array in arrays:
        result.extend(array)

    return result


def array_values(array: dict) -> list:
    """
    Return all the values of an array
    """
    return list(array.values())


def array_keys(array: dict) -> list:
    """
    Return all the keys of an array
    """
    return list(array.keys())


def array_column(array: list, column: str) -> list:
    """
    Return the values from a single column in the input array
    """
    return [row[column] for row in array]


def ksort(array: dict) -> dict:
    """
    Sort an array by key
    """
    return dict(sorted(array.items()))


def date_diff(date1: str, date2: str):
    """
    Returns the difference between two DateTime objects
    """
    import datetime

    date1 = datetime.datetime.strptime(date1, "%Y-%m-%d")
    date2 = datetime.datetime.strptime(date2, "%Y-%m-%d")

    return date2 - date1


def sleep(seconds: int):
    """
    Delay execution
    """
    import time

    time.sleep(seconds)


def array_sum(array: list) -> int:
    """
    Calculate the sum of values in an array
    """
    return sum(array)


def array_slice(array: list | dict, offset: int, length: int = None) -> dict | list:
    """
    Extract a slice of the array
    """
    if isinstance(array, dict):
        array = list(array.items())
        if length is None:
            return dict(array[offset:])
        return dict(array[offset: offset + length])

    if length is None:
        return array[offset:]
    return array[offset: offset + length]


def array_reverse(array: list) -> list:
    """
    Return an array with elements in reverse order
    """
    return array[::-1]


def arsort(array: dict) -> dict:
    """
    Sort an array in reverse order and maintain index association
    """
    return dict(sorted(array.items(), key=lambda x: x[1], reverse=True))


def preg_replace(pattern: str, replacement: str, subject: str) -> str:
    """
    Perform a regular expression search and replace
    """
    import re

    return re.sub(pattern, replacement, subject)


def md5(string: str) -> str:
    """
    Calculate the md5 hash of a string
    """
    import hashlib

    return hashlib.md5(string.encode()).hexdigest()


def parse_str(query_string: str, array: dict):
    """
    Parses the string into variables
    """
    import urllib.parse

    for key, value in urllib.parse.parse_qsl(query_string):
        array[key] = value


def str_replace(search: str | list, replace: str | list, subject: str) -> str:
    """
    Replace all occurrences of the search string with the replacement string
    """
    if isinstance(search, list):
        for s, r in zip(search, replace):
            subject = subject.replace(s, r)
    else:
        subject = subject.replace(search, replace)

    return subject


def implode(glue: str, pieces: list) -> str:
    """
    Join array elements with a string
    """
    return glue.join(pieces)


def count(array: list | dict) -> int:
    """
    Count all elements in an array, or something in an object
    """
    return len(array)


def dirname(path: str) -> str:
    """
    Returns a parent directory's path
    """
    import os

    return os.path.dirname(path)


def substr(string: str, start: int, length: int = None) -> str:
    """
    Return part of a string
    """
    if length is None:
        return string[start:]
    return string[start: start + length]


def strpos(haystack: str, needle: str) -> int:
    """
    Find the position of the first occurrence of a substring in a string
    """
    return haystack.find(needle)


def in_array(needle, haystack: list | dict) -> bool:
    """
    Checks if a value exists in an array
    """
    return needle in haystack


def explode(delimiter: str, string: str) -> list:
    """
    Split a string by a string
    """
    return string.split(delimiter)


def strlen(string: str) -> int:
    """
    Get string length
    """
    return len(string)


def is_array(var) -> bool:
    """
    Finds whether a variable is an array
    """
    return isinstance(var, list) or isinstance(var, dict)


def array_key_exists(key, array: dict) -> bool:
    """
    Checks if the given key or index exists in the array
    """
    return key in array


def trim(string: str, characters: str = None) -> str:
    """
    Strip whitespace (or other characters) from the beginning and end of a string
    """
    return string.strip(characters)


def method_exists(object_, method: str) -> bool:
    """
    Checks if the class method exists
    """
    return hasattr(object_, method)


def defined(name: str) -> bool:
    """
    Checks whether a given named constant exists
    """
    return name in globals()


def is_string(var) -> bool:
    """
    Find whether the type of variable is string
    """
    return isinstance(var, str)


def function_exists(function_name: str) -> bool:
    """
    Return true if the given function has been defined
    """
    return function_name in globals()


def strtolower(string: str) -> str:
    """
    Make a string lowercase
    """
    return string.lower()


def is_dir(filename: str) -> bool:
    """
    Tells whether the filename is a directory
    """
    import os

    return os.path.isdir(filename)


def strtr(string: str, from_: str, to: str) -> str:
    """
    Translate characters or replace substrings
    """
    return string.translate(str.maketrans(from_, to))


def call_user_func_array(callback, parameters: list):
    """
    Call a user function given with an array of parameters
    """
    return callback(*parameters)


def array_flip(array: dict) -> dict:
    """
    Exchanges all keys with their associated values in an array
    """
    return {value: key for key, value in array.items()}


def array_filter(array: list, callback=None) -> list:
    """
    Filters elements of an array using a callback function
    """
    return list(filter(callback, array))


def array_walk_recursive(array: list | dict, callback):
    """
    Apply a user function recursively to every member of an array
    """
    for key, value in each(array):
        if is_array(value):
            array_walk_recursive(value, callback)
        else:
            callback(value, key)


def htmlspecialchars(string: str) -> str:
    """
    Convert special characters to HTML entities
    """
    import html

    return html.escape(string)


def array_reduce(array: list, callback, initial=None):
    """
    Iteratively reduce the array to a single value using a callback function
    """
    from functools import reduce

    return reduce(callback, array, initial)


def mkdir(path: str, mode=0o777, recursive=False):
    """
    Makes directory
    """
    import os

    os.makedirs(path, mode, exist_ok=recursive)


def realpath(path: str) -> str:
    """
    Returns canonicalized absolute pathname
    """
    import os

    return os.path.realpath(path)


def unlink(filename: str):
    """
    Deletes a file
    """
    import os

    os.unlink(filename)


def array_shift(array: list) -> any:
    """
    Shift an element off the beginning of array
    """
    return array.pop(0)


def array_unshift(array: list, value: any):
    """
    Prepend one or more elements to the beginning of an array
    """
    array.insert(0, value)


def array_pop(array: list) -> any:
    """
    Pop the element off the end of array
    """
    return array.pop()


def is_int(var) -> bool:
    """
    Find whether the type of variable is integer
    """
    return isinstance(var, int)


def is_numeric(var) -> bool:
    """
    Finds whether a variable is a number or a numeric string
    """
    return isinstance(var, int) or isinstance(var, float) or (is_string(var) and var.isnumeric())


def array_unique(array: list) -> list:
    """
    Removes duplicate values from an array
    """
    return list(set(array))


def basename(path: str) -> str:
    """
    Returns trailing name component of path
    """
    import os

    return os.path.basename(path)


def preg_match_all(pattern: str, subject: str):
    """
    Perform a global regular expression match
    """
    import re

    return re.findall(pattern, subject)


def array_diff(array1: list, array2: list) -> list:
    """
    Computes the difference of arrays
    """
    return list(set(array1) - set(array2))


def parse_url(url: str) -> ParseResult:
    """
    Parse a URL and return its components
    """
    import urllib.parse

    return urllib.parse.urlparse(url)


def base64_encode(string: str) -> str:
    """
    Encodes data with MIME base64
    """
    import base64

    return base64.b64encode(string.encode()).decode()


def base64_decode(string: str) -> str:
    """
    Decodes data encoded with MIME base64
    """
    import base64

    return base64.b64decode(string).decode()


def strtoupper(string: str) -> str:
    """
    Make a string uppercase
    """
    return string.upper()


def array_push(array: list, value: any):
    """
    Push one or more elements onto the end of array
    """
    array.append(value)


def fopen(filename: str, mode: str):
    """
    Opens file or URL
    """
    return open(filename, mode)


def fclose(handle):
    """
    Closes an open file pointer
    """
    handle.close()


def fread(handle, length: int):
    """
    Binary-safe file read
    """
    return handle.read(length)


def fwrite(handle, data: str):
    """
    Binary-safe file write
    """
    return handle.write(data)


def rmdir(dirname_: str):
    """
    Removes directory
    """
    import os

    os.rmdir(dirname_)


def scandir(dirname_: str) -> list:
    """
    List files and directories inside the specified path
    """
    import os

    return os.listdir(dirname_)

def array_chunk(array: list | dict, size: int, preserve_keys: bool = False) -> list:
    """
    Chunks an array into arrays with size elements.
    The last chunk may contain less than size elements.
    """
    if size < 1:
        raise ValueError("array_chunk(): size must be greater than 0")

    if not preserve_keys:
        arr = list(array.values()) if isinstance(array, dict) else array
        return [arr[i:i + size] for i in range(0, len(arr), size)]

    # preserve_keys is True
    items = list(array.items()) if isinstance(array, dict) else list(enumerate(array))
    chunks = [items[i:i + size] for i in range(0, len(items), size)]
    return [dict(chunk) for chunk in chunks]


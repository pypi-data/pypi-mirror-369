# strarr

`strarr` is a Python library designed to convert any iterable of objects or dictionaries
into a formatted table string with minimum effort.

It is intended to be used to quickly print data in a tabular format,
for better understanding or debugging purpose.

## Features

- **Iterables support**: Works with lists, tuples, and any other iterables.
- **Object and Dictionary Support**: Works with both objects and dictionaries.
  - Use attributes for objects and keys for dictionaries.
  - Automatically infer type of data (either dict or object) 
    based on the first element in the iterable.
  - Assumes same type for all elements in the iterable.
- **Automatic Field Detection**: Automatically detects fields from objects or dictionaries.
- **Customizable Field Inclusion/Exclusion**: Easily include or exclude specific fields.
- **Index Column**: Optionally add an index column to the table.
- **Customizable output**:
  - Add optional indentation at the start of rows.
  - Control spaces between columns.

## Installation

Install the library using pip:

```bash
pip install strarr
```

## Usage

Basic example:

```python
from strarr import strarr


class Example:
    def __init__(self, an_id, name):
        self.id = an_id
        self.name = name


data = [Example(1, "Alice"), Example(2, "Bob")]

print(strarr(data))
"""Output:
#  [id]  [name]
1     1   Alice
2     2     Bob
"""
```

For more examples, see `tests` directory in the GitHub repository.


## Documentation

```python
from collections.abc import Iterable, Collection
from typing import Any

def strarr(
    iterable: Iterable[Any],
    /,
    include: Collection[str] = (),
    *,
    exclude: Collection[str] = (),
    index: int | None = 1,
    indent: str = "",
    space: int = 2,
    align_left: bool = False,
) -> str:
    """
    Convert an iterable of objects or dictionaries into a formatted table
    rendered in a string.

    :param iterable: Iterable of objects or dictionaries.
    :param include: List of fields to include in the table.
        If not specified or empty, all fields will be included.
        Mutually exclusive with `exclude`.
    :param exclude: List of fields to exclude from the table.
        Mutually exclusive with `include`.
    :param index: If not None, adds an index column starting from this value.
    :param indent: String to prepend to each line of the table (default "").
    :param space: Number of spaces to add between columns (default 2).
    :param align_left: If True, aligns columns to the left,
        otherwise to the right (default False).
    :return: Formatted string table.
    :raises IncludeExcludeError: If both include and exclude are specified.
    :raises NoFieldError:
        If `include` is not specified and no fields
        can be inferred from the first element.
    :raises NoFieldAfterExcludingError:
        If `exclude` is specified and no fields are left after excluding.
    """
```

## License

This project is licensed under the terms of the [MIT License](LICENSE).
```

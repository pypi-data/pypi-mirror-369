# mojangson

A small Python library for parsing, stringifying, simplifying, and normalizing [Mojangson](https://minecraft.fandom.com/wiki/NBT_format#Mojangson) - the textual representation of Minecraft's NBT (Named Binary Tag) data.

## Installation

```bash
pip install mojangson
```

## API
`parse` - Parse Mojangson text into a typed dict representation.

`stringify` - Convert a typed Mojangson dict back to a Mojangson string.

`simplify` - Simplify a typed Mojangson dict into a regular Python dict/list/primitive values, stripping Minecraft-specific type suffixes.

`normalize` - Normalize Mojangson text by parsing and then stringifying it - ensures consistent formatting and ordering.

## Usage example
```py
from mojangson import parse, stringify, simplify, normalize

mojangson_string = '{key:value}'

mojangson_parsed = parse(mojangson_string)
print(mojangson_parsed)
# {'type': 'compound', 'value': {'key': {'type': 'string', 'value': 'value'}}}

print(simplify(mojangson_parsed))
# {'key': 'value'}

mojangson_stringified = stringify(mojangson_parsed)
print(mojangson_stringified)
# {key:value}

print(normalize(mojangson_string) == mojangson_stringified)
# True
```
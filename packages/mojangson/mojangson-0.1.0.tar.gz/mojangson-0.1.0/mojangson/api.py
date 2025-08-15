from lark import Lark
from typing import Any
from .transformer import MojangsonTransformer


__all__ = (
    "parse",
    "simplify",
    "stringify",
    "normalize"
)


GRAMMAR = r"""
?main: jvalue

?jvalue: jobject
       | "'" jobject "'"   -> jvalue_quoted_obj
       | jarray
       | string
       | "null"             -> jnull

jobject: "{" "}"          -> empty_obj
       | "{" pair ("," pair)* ","? "}" -> object

jarray: "[" "]"            -> empty_list
      | "[" array_type ";" jvalue ("," jvalue)* ","? "]" -> typed_array
      | "[" (jvalue | bare_letter) ("," (jvalue | bare_letter))* ","? "]" -> array
      | "[" pair ("," pair)* ","? "]"             -> array_pair

pair: string COLON jvalue   -> kv

string: ESCAPED_STRING        -> quoted_string
      | UNQUOTED              -> bare_string

array_type: "B" -> byte_array
          | "I" -> int_array
          | "L" -> long_array

bare_letter: "B" -> bare_b
           | "I" -> bare_i
           | "L" -> bare_l

COLON: ":"

ESCAPED_STRING: "\"" ( "\\\"" | /[^"]/ )* "\""

UNQUOTED: /[^"'{}\[\]:;, \t\r\n][^{}\[\]:;, \t\r\n]*/

%import common.WS
%ignore WS
"""


_parser = Lark(GRAMMAR, start="main", parser="lalr", transformer=MojangsonTransformer())


def simplify(node: dict[str, Any]) -> Any:
    """Simplify a typed Mojangson dict into regular Python dict/list/values."""

    def transform(value: Any, typ: str) -> Any:
        if typ == 'compound':
            return {k: simplify(v) for k, v in value.items()}
        if typ == 'list':
            arr = value.get('value')
            if not isinstance(arr, list):
                return []
            t = value.get('type')
            return [transform(v, t) for v in arr]
        return value

    return transform(node['value'], node['type'])


def _normalize_string(s: str) -> str:
    """Normalize a string with quotes if needed."""
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1]
    needs_quotes = (
        not s or
        any(c in s for c in "'{}[]:;,()§=") or
        not all(c.isalnum() or c in ('_', ' ') for c in s)
    )
    if needs_quotes:
        s = s.replace('"', '\\"')
        return f'"{s}"'
    return s


def _has_missing(arr: list[Any]) -> bool:
    """Check if list contains any None values."""
    return any(el is None for el in arr)


def _get_suffix(val: Any, typ: str) -> str:
    """Get Mojangson numeric suffix for a value."""
    if typ == 'double':
        try:
            iv = int(val)
            return 'd' if float(iv) == float(val) else ''
        except Exception:
            return ''
    return {'int': '', 'byte': 'b', 'short': 's', 'float': 'f', 'long': 'l', 'string': ''}.get(typ, '')


def _get_array_prefix(typ: str) -> str:
    """Get prefix for typed arrays (B/I/L)."""
    return typ[0].upper() + ';'


def _stringify_array_values(payload: dict[str, Any]) -> str:
    """Stringify values of a Mojangson array."""
    arr = payload['value']
    typ = payload['type']
    missing = _has_missing(arr)
    parts: list[str] = []
    for i, v in enumerate(arr):
        if v is None:
            continue
        curr = stringify({"value": v, "type": typ})
        parts.append(f"{i}:{curr}" if missing else curr)
    return ",".join(parts)


def stringify(node: dict[str, Any]) -> str:
    """Convert a typed Mojangson dict back to Mojangson string."""
    typ = node['type']
    val = node['value']
    if typ == 'compound':
        parts: list[str] = []
        for key, child in val.items():
            s = stringify(child)
            if child['type'] == 'string':
                if isinstance(child['value'], str):
                    s = _normalize_string(child['value'])
                else:
                    s = str(child['value'])
            parts.append(f"{key}:{s}")
        return '{' + ','.join(parts) + '}'
    elif typ == 'list':
        if not isinstance(val.get('value'), list):
            return '[]'
        inner = _stringify_array_values(val)
        return '[' + inner + ']'
    elif typ in ('byteArray', 'intArray', 'longArray'):
        prefix = _get_array_prefix(typ)
        inner = _stringify_array_values(val)
        return '[' + prefix + inner + ']'
    else:
        s = f"{val}{_get_suffix(val, typ)}"
        if typ == 'string':
            s = _normalize_string(s)
        return s


def parse(text: str) -> dict[str, Any]:
    """Parse Mojangson text into typed dict representation."""
    try:
        return _parser.parse(text)
    except Exception as e:
        raise ValueError(f"Error parsing text '{text}'") from e


def normalize(text: str) -> str:
    """Normalize Mojangson text (parse and stringify)."""
    return stringify(parse(text))

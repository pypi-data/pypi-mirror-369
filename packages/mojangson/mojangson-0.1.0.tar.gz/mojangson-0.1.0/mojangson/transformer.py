import json

from lark import (
    v_args,
    Transformer
)

from typing import (
    Any,
    Optional
)


__all__ = (
    "MojangsonTransformer",
)


SUFFIX_TO_TYPE = {'b': 'byte', 's': 'short', 'l': 'long', 'f': 'float', 'd': 'double', 'i': 'int'}
NUMERIC_SUFFIXES = set(SUFFIX_TO_TYPE.keys())
INT32_MIN = -(2**31)
INT32_MAX = 2**31 - 1


def _parse_value(s: str) -> dict[str, Any]:
    """Parse a raw Mojangson string token into a typed dict with 'type' and 'value'."""
    if s == 'true':
        return {"type": "boolean", "value": True}
    if s == 'false':
        return {"type": "boolean", "value": False}
    if not s:
        return {"type": "string", "value": s}

    last = s[-1].lower()
    if last in NUMERIC_SUFFIXES:
        try:
            v = float(s[:-1])
        except ValueError:
            return {"type": "string", "value": s}
        if v.is_integer():
            v = int(v)
        return {"type": SUFFIX_TO_TYPE[last], "value": v}

    try:
        v = float(s)
    except ValueError:
        return {"type": "string", "value": s}

    decimal = '.' in s
    if decimal:
        if v.is_integer():
            v = int(v)
        return {"type": "double", "value": v}

    try:
        iv = int(v)
    except (ValueError, OverflowError):
        return {"type": "string", "value": s}

    if INT32_MIN <= iv <= INT32_MAX:
        return {"type": "int", "value": iv}

    return {"type": "string", "value": s}


@v_args(inline=True)
class MojangsonTransformer(Transformer):
    """Transformer to convert parse tree nodes into Mojangson typed dicts."""

    def byte_array(self) -> str:
        return 'B'

    def int_array(self) -> str:
        return 'I'

    def long_array(self) -> str:
        return 'L'

    def bare_b(self) -> dict[str, str]:
        return {"type": "string", "value": "B"}

    def bare_i(self) -> dict[str, str]:
        return {"type": "string", "value": "I"}

    def bare_l(self) -> dict[str, str]:
        return {"type": "string", "value": "L"}

    def jvalue_quoted_obj(self, obj: dict) -> dict:
        return obj

    def jnull(self) -> dict[str, str]:
        return {"type": "string", "value": "null"}

    def empty_obj(self) -> dict[str, Any]:
        return {"type": "compound", "value": {}}

    def object(self, first_kv: tuple[str, dict], *rest: tuple[str, dict]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        k, v = first_kv
        if k is not None:
            out[k] = v
        for k2, v2 in rest:
            if k2 is not None:
                out[k2] = v2
        return {"type": "compound", "value": out}

    def empty_list(self) -> dict[str, Any]:
        return {"type": "list", "value": {"type": "string", "value": []}}

    def typed_array(self, bil: str, first: dict, *rest: dict) -> dict[str, Any]:
        items = [first] + list(rest)
        arr_vals = [it for it in items]
        tmap = {'B': 'byteArray', 'I': 'intArray', 'L': 'longArray'}
        arr_type = tmap[bil]
        return {
            "type": arr_type,
            "value": {
                "type": arr_vals[0]["type"],
                "value": [x["value"] for x in arr_vals],
            },
        }

    def array(self, first: dict, *rest: dict) -> dict[str, Any]:
        items = [first] + list(rest)
        return {"type": "list", "value": {"type": items[0]["type"], "value": [x["value"] for x in items]}}

    def array_pair(self, first_kv: tuple[str, dict], *rest: tuple[str, dict]) -> dict[str, Any]:
        tmp: dict[int, dict] = {}
        def put(kv: tuple[str, dict]) -> None:
            k, v = kv
            if k is None:
                return
            try:
                idx = int(k)
            except ValueError:
                return
            tmp[idx] = v
        put(first_kv)
        for kv in rest:
            put(kv)
        if not tmp:
            return {"type": "list", "value": {"type": "string", "value": []}}
        max_i = max(tmp)
        arr: list[Optional[Any]] = [None] * (max_i + 1)
        for i, node in tmp.items():
            arr[i] = node
        first_el = next(x for x in arr if x is not None)
        return {"type": "list", "value": {"type": first_el["type"], "value": [x["value"] if x is not None else None for x in arr]}}

    def kv(self, k: dict, _colon: str, v: dict) -> tuple[str, dict]:
        return k["value"], v

    def quoted_string(self, tok: str) -> dict:
        text = json.loads(str(tok))
        return _parse_value(text)

    def bare_string(self, tok: str) -> dict:
        return _parse_value(str(tok))

    def jobject(self, x: dict) -> dict:
        return x

    def jarray(self, x: dict) -> dict:
        return x

    def string(self, x: dict) -> dict:
        return x

    def BIL(self, tok: str) -> str:
        return str(tok)

from typing import Any


def not_none(x: Any) -> bool:
    return x is not None


def escape(text: str) -> str:
    return repr(text)


def mix_dicts(*dicts: dict) -> dict:
    result = dict()
    for d in dicts:
        result.update(d)
    return result

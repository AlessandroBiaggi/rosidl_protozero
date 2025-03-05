from typing import Iterable
from typing import List


def filter_tuples(
        *required: str,
        allowed: List[str],
        tuples: Iterable[str],
        separator: str = ':',
) -> List[str]:
    return [
        filter_tuple(
            *required,
            allowed=allowed,
            tuple=tuple,
            separator=separator,
        )
        for tuple in tuples
    ]

def filter_tuple(
        *required: str,
        allowed: List[str],
        tuple: str,
        separator: str = ':',
) -> str:
    min_tuple_len = len(required)
    parts = tuple.split(separator, min_tuple_len)

    if len(parts) < min_tuple_len:
        raise ValueError(f"Invalid tuple '{tuple}'")

    # TODO wtf is this
    for i in range(min_tuple_len - 1):
        if parts[i] != required[i]:
            continue

    if parts[min_tuple_len] not in allowed:
        raise ValueError(f"Invalid value '{parts[min_tuple_len]}'")

    return separator.join(parts[min_tuple_len:])

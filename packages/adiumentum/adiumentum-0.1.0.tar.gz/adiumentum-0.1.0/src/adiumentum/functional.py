from collections.abc import Callable, Iterable
from functools import reduce
from typing import TypeVar

T = TypeVar("T")
TPost = TypeVar("TPost")
TPre = TypeVar("TPre")
K = TypeVar("K")
V = TypeVar("V")


def lmap(callable_: Callable[[TPre], TPost], iterable: Iterable[TPre]) -> list[TPost]:
    return list(map(callable_, iterable))


def smap(callable_: Callable[[TPre], TPost], iterable: Iterable[TPre]) -> set[TPost]:
    return set(map(callable_, iterable))


def tmap(callable_: Callable[[TPre], TPost], iterable: Iterable[TPre]) -> tuple[TPost, ...]:
    return tuple(map(callable_, iterable))


def vmap(callable_: Callable[[TPre], TPost], dictionary: dict[K, TPre]) -> dict[K, TPost]:
    return {k: callable_(v) for k, v in dictionary.items()}


def kmap(callable_: Callable[[TPre], TPost], dictionary: dict[TPre, V]) -> dict[TPost, V]:
    return {callable_(k): v for k, v in dictionary.items()}


def dmap(callable_: Callable[[TPre], TPost], dictionary: dict[TPre, TPre]) -> dict[TPost, TPost]:
    return {callable_(k): callable_(v) for k, v in dictionary.items()}


def identity(x: T) -> T:
    return x


def fold_dictionaries(dicts: Iterable[dict[K, T]]) -> dict[K, T]:
    def _or(dict1: dict[K, T], dict2: dict[K, T]) -> dict[K, T]:
        return dict1 | dict2

    return reduce(_or, dicts)

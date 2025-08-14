from collections.abc import Callable, Iterable
from types import UnionType
from typing import TypeVar

T = TypeVar("T")

ClassInfo = type | UnionType | tuple["ClassInfo"]


def areinstances(iterable_instance: Iterable, class_or_tuple: ClassInfo) -> bool:
    return all(map(lambda inst: isinstance(inst, class_or_tuple), iterable_instance))


def fallback_if_none(orig: T | None, alt: T) -> T:
    return alt if (orig is None) else orig


def call_fallback_if_none(orig: T | None, alt: Callable[[], T]) -> T:
    return alt() if (orig is None) else orig

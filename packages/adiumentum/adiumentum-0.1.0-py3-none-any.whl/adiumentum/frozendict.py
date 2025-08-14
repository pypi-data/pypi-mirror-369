from collections import defaultdict
from collections.abc import Callable
from typing import Generic, TypeVar, cast

T = TypeVar("T")
K = TypeVar("K")


class FrozenDefaultDict(defaultdict[K, T], Generic[K, T]):
    def __init__(self, default_factory: Callable[[], T], dictionary: dict[K, T]):
        super().__init__(default_factory, dictionary)

    def __repr__(self) -> str:
        default = self.default_factory
        result = default.__name__ if callable(default) else repr(default)
        return f"{self.__class__.__name__}({dict(self)}, default={result})"

    def __getitem__(self, key: K) -> T:
        if key in self:
            return super().__getitem__(key)
        return cast(Callable, self.default_factory)()

    def __setitem__(self, key: K, value: T) -> None:
        raise TypeError(f"{self.__class__.__name__} is immutable")

    def __delitem__(self, key) -> None:
        raise TypeError(f"{self.__class__.__name__} is immutable")

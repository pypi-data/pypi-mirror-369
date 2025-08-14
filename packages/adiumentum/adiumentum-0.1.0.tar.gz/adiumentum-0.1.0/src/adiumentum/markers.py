from collections.abc import Callable
from functools import wraps

from .functional import identity


def impure(callable_or_none: Callable | None = None, **kwargs) -> Callable:
    if callable_or_none is None:
        return identity
    else:
        return callable_or_none


def pure(callable_or_none: Callable | None = None, **kwargs) -> Callable:
    if callable_or_none is None:
        return identity
    else:
        return callable_or_none


def helper(callable_or_none: Callable | None = None, **kwargs) -> Callable:
    if callable_or_none is None:
        return identity
    else:
        return callable_or_none


def step_data(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*fargs, **fkwargs):
        return func(*fargs, **fkwargs)

    return wrapper


def step_transition(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*fargs, **fkwargs):
        return func(*fargs, **fkwargs)

    return wrapper


def validator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*fargs, **fkwargs):
        return func(*fargs, **fkwargs)

    return wrapper


def mutates_instance(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*fargs, **fkwargs):
        # print(
        #     (
        #         f"\u001b[31mMutating in place\u001b[0m:         "
        #         f"\u001b[32m{type(fargs[0]).__name__:<25}\u001b[0m"
        #         f" via \u001b[33m{func.__name__:<25}\u001b[0m"
        #         f" in \u001b[34m{func.__module__}\u001b[0m"
        #     )
        # )
        return func(*fargs, **fkwargs)

    return wrapper


def mutates_and_returns_instance(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*fargs, **fkwargs):
        # print(
        #     (
        #         f"\u001b[31mMutating and returning\u001b[0m:    "
        #         f"\u001b[32m{type(fargs[0]).__name__:<25}\u001b[0m"
        #         f" via \u001b[33m{func.__name__:<25}\u001b[0m"
        #         f" in \u001b[34m{func.__module__}\u001b[0m"
        #     )
        # )
        return func(*fargs, **fkwargs)

    return wrapper


def mutates(*args, **kwargs) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*fargs, **fkwargs):
            print(
                f"Mutating attributes \u001b[36m{', '.join(args):<50}\u001b[0m"
                f" of \u001b[32m{type(fargs[0]).__name__:<25}\u001b[0m"
                f" via \u001b[33m{func.__name__:<25}\u001b[0m"
                f" in \u001b[34m{func.__module__.replace('consilium.', '.'):<40}\u001b[0m"
            )

            return func(*fargs, **fkwargs)

        return wrapper

    return decorator


def refactor(*args) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*fargs, **fkwargs):
            print(
                f"\u001b[36mREFACTOR\u001b[0m"
                f" \u001b[33m{func.__name__}\u001b[0m"
                f" in \u001b[34m{func.__module__.replace('consilium.', '.')}\u001b[0m."
                f" Notes: \u001b[32m{', '.join(args)}\u001b[0m"
            )

            return func(*fargs, **fkwargs)

        return wrapper

    return decorator

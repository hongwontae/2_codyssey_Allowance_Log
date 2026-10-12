
from functools import wraps
from time import perf_counter
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def measure_time(func: Callable[P, R]) -> Callable[P, R]:
    """함수의 실행 시간을 측정하는 데코레이터."""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = perf_counter()

        try:
            return func(*args, **kwargs)
        finally:
            elapsed = perf_counter() - start
            print(
                f"[실행 시간] {func.__name__}: "
                f"{elapsed:.4f}초"
            )

    return wrapper

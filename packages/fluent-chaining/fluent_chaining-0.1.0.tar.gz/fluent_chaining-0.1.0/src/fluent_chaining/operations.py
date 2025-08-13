"""
Additional operations and utilities for fluent chaining.

This module provides extra operations that can be used with the Chain class
to extend functionality beyond the core operations.
"""

from typing import Any, Callable, Dict, List, Optional, TypeVar

from .core import Chain

T = TypeVar("T")
U = TypeVar("U")
K = TypeVar("K")


def compose(*functions: Callable[..., Any]) -> Callable[..., Any]:
    """
    Compose multiple functions from right to left.

    Args:
        *functions: Functions to compose

    Returns:
        A composed function

    Example:
        f = compose(lambda x: x + 1, lambda x: x * 2)
        result = f(5)  # 11
    """
    if not functions:
        return lambda x: x

    def composed(*args: Any, **kwargs: Any) -> Any:
        result = functions[-1](*args, **kwargs)
        for func in reversed(functions[:-1]):
            result = func(result)
        return result

    return composed


def pipe(*functions: Callable[..., Any]) -> Callable[..., Any]:
    """
    Pipe multiple functions from left to right.

    Args:
        *functions: Functions to pipe

    Returns:
        A piped function

    Example:
        f = pipe(lambda x: x * 2, lambda x: x + 1)
        result = f(5)  # 11
    """
    if not functions:
        return lambda x: x

    def piped(*args: Any, **kwargs: Any) -> Any:
        result = functions[0](*args, **kwargs)
        for func in functions[1:]:
            result = func(result)
        return result

    return piped


def curry(func: Callable[..., T]) -> Callable[..., Any]:
    """
    Curry a function to allow partial application.

    Args:
        func: Function to curry

    Returns:
        A curried version of the function

    Example:
        def add(x, y):
            return x + y

        curried_add = curry(add)
        add_five = curried_add(5)
        result = add_five(3)  # 8
    """

    def curried(*args: Any) -> Any:
        if len(args) >= func.__code__.co_argcount:
            return func(*args)
        return lambda *more_args: curried(*(args + more_args))

    return curried


def partial(func: Callable[..., T], *args: Any, **kwargs: Any) -> Callable[..., T]:
    """
    Create a partial function with some arguments pre-filled.

    Args:
        func: Function to partially apply
        *args: Positional arguments to pre-fill
        **kwargs: Keyword arguments to pre-fill

    Returns:
        A partial function

    Example:
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        greet_john = partial(greet, "John")
        result = greet_john()  # "Hello, John!"
    """

    def partial_func(*more_args: Any, **more_kwargs: Any) -> T:
        all_args = args + more_args
        all_kwargs = {**kwargs, **more_kwargs}
        return func(*all_args, **all_kwargs)

    return partial_func


def flip(func: Callable[[T, U], Any]) -> Callable[[U, T], Any]:
    """
    Flip the order of the first two arguments of a function.

    Args:
        func: Function to flip

    Returns:
        A function with flipped arguments

    Example:
        def divide(x, y):
            return x / y

        flipped_divide = flip(divide)
        result = flipped_divide(2, 10)  # 5.0
    """

    def flipped(a: U, b: T) -> Any:
        return func(b, a)

    return flipped


def apply(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Apply a function to arguments.

    Args:
        func: Function to apply
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Result of applying the function
    """
    return func(*args, **kwargs)


def always(predicate: Callable[[T], bool]) -> Callable[[List[T]], bool]:
    """
    Check if a predicate is true for all elements.

    Args:
        predicate: Function to test each element

    Returns:
        Function that returns True if predicate is true for all elements

    Example:
        is_positive = lambda x: x > 0
        all_positive = always(is_positive)
        result = all_positive([1, 2, 3])  # True
    """
    return lambda iterable: all(predicate(item) for item in iterable)


def exists(predicate: Callable[[T], bool]) -> Callable[[List[T]], bool]:
    """
    Check if a predicate is true for at least one element (existential quantification).

    Args:
        predicate: Function to test each element

    Returns:
        Function that returns True if predicate is true for any element

    Example:
        is_even = lambda x: x % 2 == 0
        any_even = exists(is_even)
        result = any_even([1, 3, 4, 5])  # True
    """
    return lambda iterable: any(predicate(item) for item in iterable)


def tap(func: Callable[[T], None]) -> Callable[[T], T]:
    """
    Create a function that calls a side-effect function but returns the original value.

    Useful for debugging or logging in function chains.

    Args:
        func: Side-effect function to call

    Returns:
        Function that calls the side-effect but returns the original value

    Example:
        debug_print = tap(print)
        result = take([1, 2, 3]).transform(debug_print).sum().value()
    """

    def tapped(value: T) -> T:
        func(value)
        return value

    return tapped


# Additional Chain methods
def distinct(chain: Chain[T]) -> Chain[T]:
    """Remove duplicate elements while preserving order."""
    if hasattr(chain._data, "__iter__") and not isinstance(chain._data, (str, bytes)):
        seen = set()
        result = []
        for item in chain._data:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return Chain(result)  # type: ignore
    return Chain(chain._data)


def unique(chain: Chain[T]) -> Chain[T]:
    """Alias for distinct - remove duplicate elements."""
    return distinct(chain)


def reverse(chain: Chain[T]) -> Chain[T]:
    """Reverse the order of elements."""
    if hasattr(chain._data, "__iter__") and not isinstance(chain._data, (str, bytes)):
        return Chain(list(reversed(list(chain._data))))  # type: ignore
    return Chain(chain._data)


def sort(
    chain: Chain[T], key: Optional[Callable[[T], Any]] = None, reverse: bool = False
) -> Chain[T]:
    """Sort elements."""
    if hasattr(chain._data, "__iter__") and not isinstance(chain._data, (str, bytes)):
        return Chain(sorted(chain._data, key=key, reverse=reverse))  # type: ignore
    return Chain(chain._data)


def group_by(chain: Chain[T], key_func: Callable[[T], K]) -> Chain[Dict[K, List[T]]]:
    """Group elements by a key function."""
    if hasattr(chain._data, "__iter__") and not isinstance(chain._data, (str, bytes)):
        from itertools import groupby

        sorted_data = sorted(chain._data, key=key_func)  # type: ignore
        groups = {k: list(g) for k, g in groupby(sorted_data, key_func)}
        return Chain(groups)
    raise TypeError(f"Cannot group non-iterable type: {type(chain._data)}")


def flatten(chain: Chain[T]) -> Chain[T]:
    """Flatten nested iterables."""
    if hasattr(chain._data, "__iter__") and not isinstance(chain._data, (str, bytes)):
        result = []
        for item in chain._data:
            if hasattr(item, "__iter__") and not isinstance(item, (str, bytes)):
                result.extend(item)
            else:
                result.append(item)
        return Chain(result)  # type: ignore
    return Chain(chain._data)


# Add methods to Chain class
Chain.distinct = distinct  # type: ignore
Chain.unique = unique  # type: ignore
Chain.reverse = reverse  # type: ignore
Chain.sort = sort  # type: ignore
Chain.group_by = group_by  # type: ignore
Chain.flatten = flatten  # type: ignore


def memoize(func: Callable[..., T]) -> Callable[..., T]:
    """
    Memoize a function to cache its results.

    Args:
        func: Function to memoize

    Returns:
        A memoized version of the function

    Example:
        @memoize
        def fibonacci(n):
            if n < 2:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
    """
    cache: Dict[str, T] = {}

    def memoized(*args: Any, **kwargs: Any) -> T:
        # Create a key from args and kwargs
        key = str(args) + str(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    memoized.__name__ = getattr(func, "__name__", "memoized")
    memoized.__doc__ = getattr(func, "__doc__", None)
    return memoized


def identity(x: T) -> T:
    """
    Identity function - returns its argument unchanged.

    Useful as a default function or in function composition.

    Args:
        x: Value to return

    Returns:
        The same value
    """
    return x


def constant(value: T) -> Callable[..., T]:
    """
    Create a function that always returns the same value.

    Args:
        value: Value to always return

    Returns:
        A function that always returns the value

    Example:
        always_five = constant(5)
        result = always_five()  # 5
        result = always_five("anything")  # 5
    """
    return lambda *args, **kwargs: value


# Advanced Chain methods
def tap_chain(chain: Chain[T], func: Callable[[T], None]) -> Chain[T]:
    """Apply a function for its side effect and return the chain."""
    func(chain._data)
    return chain


def apply_if(
    chain: Chain[T], condition: bool, func: Callable[[Chain[T]], Chain[T]]
) -> Chain[T]:
    """Apply a function to the chain only if a condition is true."""
    if condition:
        return func(chain)
    return chain


def apply_when(
    chain: Chain[T],
    predicate: Callable[[T], bool],
    func: Callable[[Chain[T]], Chain[T]],
) -> Chain[T]:
    """Apply a function to the chain only when a predicate is true."""
    if predicate(chain._data):
        return func(chain)
    return chain


def branch(
    chain: Chain[T],
    condition: bool,
    if_true: Callable[[Chain[T]], Chain[T]],
    if_false: Optional[Callable[[Chain[T]], Chain[T]]] = None,
) -> Chain[T]:
    """Branch the chain based on a condition."""
    if condition:
        return if_true(chain)
    elif if_false:
        return if_false(chain)
    return chain


def side_effect(chain: Chain[T], func: Callable[[T], None]) -> Chain[T]:
    """Apply a side effect function and return the chain unchanged."""
    func(chain._data)
    return chain


def debug(chain: Chain[T], label: str = "Debug") -> Chain[T]:
    """Print the current value for debugging."""
    print(f"{label}: {chain._data}")
    return Chain(chain._data)


def assert_that(
    chain: Chain[T], predicate: Callable[[T], bool], message: str = "Assertion failed"
) -> Chain[T]:
    """Assert that the chain data satisfies a predicate."""
    if not predicate(chain._data):
        raise AssertionError(message)
    return chain


def or_else(chain: Chain[T], default_value: Any) -> Chain[T]:
    """Return default value if current value is None or empty."""
    if chain._data is None or (
        hasattr(chain._data, "__len__") and len(chain._data) == 0
    ):
        return Chain(default_value)
    return Chain(chain._data)


# Add advanced methods to Chain class
Chain.tap_chain = tap_chain  # type: ignore
Chain.apply_if = apply_if  # type: ignore
Chain.apply_when = apply_when  # type: ignore
Chain.branch = branch  # type: ignore
Chain.side_effect = side_effect  # type: ignore
Chain.debug = debug  # type: ignore
Chain.assert_that = assert_that  # type: ignore
Chain.or_else = or_else  # type: ignore

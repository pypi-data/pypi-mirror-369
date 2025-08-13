"""
Result<T> type for functional error handling.

Inspired by Rust's Result type and .NET's functional programming patterns.
"""

from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")  # Remove the Exception bound to allow more flexibility
U = TypeVar("U")


class Result(Generic[T, E]):
    """Result type for handling success and error cases."""

    def is_ok(self) -> bool:
        """Check if this is an Ok variant."""
        raise NotImplementedError

    def is_err(self) -> bool:
        """Check if this is an Err variant."""
        raise NotImplementedError

    def map(self, func: Callable[[T], U]) -> "Result[U, E]":
        """Apply a function to the contained value if Ok."""
        raise NotImplementedError

    def map_err(self, func: Callable[[E], U]) -> "Result[T, U]":
        """Apply a function to the contained error if Err."""
        raise NotImplementedError

    def then(self, func: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        """Chain operations that return Results."""
        raise NotImplementedError

    def unwrap(self) -> T:
        """Extract the value from Ok, or raise an error."""
        raise NotImplementedError

    def unwrap_or(self, default: T) -> T:
        """Extract the value from Ok, or return default."""
        raise NotImplementedError

    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        """Extract the value from Ok, or compute from error."""
        raise NotImplementedError

    def unwrap_err(self) -> E:
        """Extract the error from Err, or raise an error."""
        raise NotImplementedError

    def match(self, ok_func: Callable[[T], U], err_func: Callable[[E], U]) -> U:
        """Pattern match on the Result."""
        raise NotImplementedError

    def and_then(self, func: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        """Alias for then() - chain operations that may fail."""
        return self.then(func)

    def or_else(self, func: Callable[[E], "Result[T, U]"]) -> "Result[T, U]":
        """Chain operations on the error case."""
        if self.is_err():
            return func(self.unwrap_err())
        return Ok(self.unwrap())

    def filter(self, predicate: Callable[[T], bool], error: E) -> "Result[T, E]":
        """Filter the success value, converting to error if predicate fails."""
        if self.is_ok():
            value = self.unwrap()
            if predicate(value):
                return Ok(value)
            else:
                return Err(error)
        return self

    def flatten(self) -> "Result[T, E]":
        """Flatten nested Results."""
        if self.is_ok():
            inner = self.unwrap()
            if isinstance(inner, Result):
                return inner
        return self


class Ok(Result[T, E]):
    """Success variant of Result."""

    def __init__(self, value: T) -> None:
        self._value = value

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def map(self, func: Callable[[T], U]) -> "Result[U, E]":
        try:
            return Ok(func(self._value))
        except Exception as e:
            return Err(e)  # type: ignore

    def map_err(self, func: Callable[[E], U]) -> "Result[T, U]":
        return Ok(self._value)

    def then(self, func: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        try:
            return func(self._value)
        except Exception as e:
            return Err(e)  # type: ignore

    def unwrap(self) -> T:
        return self._value

    def unwrap_or(self, default: T) -> T:
        return self._value

    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        return self._value

    def unwrap_err(self) -> E:
        raise ValueError(f"Called unwrap_err() on Ok value: {self._value}")

    def match(self, ok_func: Callable[[T], U], err_func: Callable[[E], U]) -> U:
        return ok_func(self._value)

    def and_then(self, func: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        return self.then(func)

    def or_else(self, func: Callable[[E], "Result[T, U]"]) -> "Result[T, U]":
        return Ok(self._value)

    def filter(self, predicate: Callable[[T], bool], error: E) -> "Result[T, E]":
        if predicate(self._value):
            return Ok(self._value)
        else:
            return Err(error)

    def flatten(self) -> "Result[T, E]":
        if isinstance(self._value, Result):
            return self._value
        return self

    def __repr__(self) -> str:
        return f"Ok({self._value!r})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Ok) and self._value == other._value


class Err(Result[T, E]):
    """Error variant of Result."""

    def __init__(self, error: E) -> None:
        self._error = error

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def map(self, func: Callable[[T], U]) -> "Result[U, E]":
        return Err(self._error)

    def map_err(self, func: Callable[[E], U]) -> "Result[T, U]":
        try:
            return Err(func(self._error))
        except Exception as e:
            return Err(e)  # type: ignore

    def then(self, func: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        return Err(self._error)

    def unwrap(self) -> T:
        raise ValueError(f"Called unwrap() on Err value: {self._error}")

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        return func(self._error)

    def unwrap_err(self) -> E:
        return self._error

    def match(self, ok_func: Callable[[T], U], err_func: Callable[[E], U]) -> U:
        return err_func(self._error)

    def and_then(self, func: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        return Err(self._error)

    def or_else(self, func: Callable[[E], "Result[T, U]"]) -> "Result[T, U]":
        return func(self._error)

    def filter(self, predicate: Callable[[T], bool], error: E) -> "Result[T, E]":
        return Err(self._error)

    def flatten(self) -> "Result[T, E]":
        return self

    def __repr__(self) -> str:
        return f"Err({self._error!r})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Err) and self._error == other._error


# Convenience functions
def ok(value: T) -> Result[T, E]:
    """Create a successful Result."""
    return Ok(value)


def err(error: E) -> Result[T, E]:
    """Create an error Result."""
    return Err(error)


def safe(func: Callable[..., T]) -> Callable[..., Result[T, Exception]]:
    """
    Decorator to convert a function that might raise exceptions into one that returns
    Result.

    Example:
        @safe
        def divide(x, y):
            return x / y

        result = divide(10, 2)  # Ok(5.0)
        result = divide(10, 0)  # Err(ZeroDivisionError)
    """
    from functools import wraps

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Result[T, Exception]:
        try:
            return Ok(func(*args, **kwargs))
        except Exception as e:
            return Err(e)

    return wrapper


def try_parse_int(value: str) -> Result[int, str]:
    """Try to parse a string as an integer."""
    try:
        return Ok(int(value))
    except ValueError:
        return Err(f"Cannot parse '{value}' as integer")


def try_parse_float(value: str) -> Result[float, str]:
    """Try to parse a string as a float."""
    try:
        return Ok(float(value))
    except ValueError:
        return Err(f"Cannot parse '{value}' as float")


def collect_results(results: list[Result[T, E]]) -> Result[list[T], E]:
    """Collect a list of Results into a single Result."""
    values = []
    for result in results:
        if result.is_err():
            return result  # type: ignore
        values.append(result.unwrap())
    return Ok(values)


def from_result(result: Result[T, E]) -> T:
    """Extract value from Result, raising an error if Err."""
    if result.is_err():
        raise ValueError(f"Attempted to extract value from Err: {result.unwrap_err()}")
    return result.unwrap()

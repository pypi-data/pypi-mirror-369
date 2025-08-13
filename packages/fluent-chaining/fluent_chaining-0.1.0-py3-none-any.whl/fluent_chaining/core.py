"""
Core fluent chaining functionality.

This module provides the foundational Chain class that enables fluent method
chaining for functional programming operations.
"""

from typing import TYPE_CHECKING, Any, Callable, Generic, List, Optional, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E", bound=Exception)
Numeric = TypeVar("Numeric", bound=Union[int, float])

if TYPE_CHECKING:
    from .option import Option
    from .result import Result


class Chain(Generic[T]):
    """
    A fluent interface for chaining operations on data.

    This class provides a natural, prose-like API for data transformation,
    filtering, and aggregation operations.
    """

    def __init__(self, data: T) -> None:
        self._data = data

    def apply_func(self, func: Callable[[T], U]) -> "Chain[U]":
        """Apply a function to the current value."""
        return Chain(func(self._data))

    def chain(self, func: Callable[[T], U]) -> "Chain[U]":
        """Alias for apply_func() - apply a function to the current value."""
        return self.apply_func(func)

    # Filtering methods

    def where(self, predicate: Callable[[T], bool]) -> "Chain[T]":
        """Filter elements based on a predicate."""
        if hasattr(self._data, "__iter__") and not isinstance(self._data, (str, bytes)):
            filtered_data = list(filter(predicate, self._data))
            return Chain(filtered_data)  # type: ignore
        raise TypeError(f"Cannot filter non-iterable type: {type(self._data)}")

    def filter(self, predicate: Callable[[T], bool]) -> "Chain[T]":
        """Alias for where() - filter elements based on a predicate."""
        return self.where(predicate)

    # Transformation methods

    def transform(self, func: Callable[[T], U]) -> "Chain[U]":
        """Transform each element using a function."""
        if hasattr(self._data, "__iter__") and not isinstance(self._data, (str, bytes)):
            transformed_data = list(map(func, self._data))
            return Chain(transformed_data)  # type: ignore
        raise TypeError(f"Cannot map over non-iterable type: {type(self._data)}")

    def map(self, func: Callable[[T], U]) -> "Chain[U]":
        """Alias for transform() - transform each element using a function."""
        return self.transform(func)

    # Prose-like convenience methods

    def that_are(self, predicate: Callable[[T], bool]) -> "Chain[T]":
        """Filter elements using a more natural language approach."""
        return self.where(predicate)

    def that_are_greater_than(self, value: Numeric) -> "Chain[T]":
        """Filter elements that are greater than the specified value."""
        return self.where(lambda x: x > value)  # type: ignore

    def that_are_less_than(self, value: Numeric) -> "Chain[T]":
        """Filter elements that are less than the specified value."""
        return self.where(lambda x: x < value)  # type: ignore

    def that_equal(self, value: Any) -> "Chain[T]":
        """Filter elements that equal the specified value."""
        return self.where(lambda x: x == value)

    def multiplied_by(self, factor: Numeric) -> "Chain[T]":
        """Multiply each numeric element by the specified factor."""
        return self.transform(lambda x: x * factor)  # type: ignore

    def divided_by(self, divisor: Numeric) -> "Chain[T]":
        """Divide each numeric element by the specified divisor."""
        return self.transform(lambda x: x / divisor)  # type: ignore

    def plus(self, addend: Numeric) -> "Chain[T]":
        """Add the specified value to each numeric element."""
        return self.transform(lambda x: x + addend)  # type: ignore

    def minus(self, subtrahend: Numeric) -> "Chain[T]":
        """Subtract the specified value from each numeric element."""
        return self.transform(lambda x: x - subtrahend)  # type: ignore

    # Aggregation methods

    def sum(self) -> "Chain[T]":
        """Calculate the sum of all elements."""
        if hasattr(self._data, "__iter__") and not isinstance(self._data, (str, bytes)):
            return Chain(sum(self._data))  # type: ignore
        raise TypeError(f"Cannot sum non-iterable type: {type(self._data)}")

    def count(self) -> "Chain[int]":
        """Count the number of elements."""
        if hasattr(self._data, "__iter__") and not isinstance(self._data, (str, bytes)):
            return Chain(len(list(self._data)))
        return Chain(1)  # Single item counts as 1

    def length(self) -> "Chain[int]":
        """Get the length/count of elements (alias for count)."""
        return self.count()

    def max(self) -> "Chain[T]":
        """Find the maximum element."""
        if hasattr(self._data, "__iter__") and not isinstance(self._data, (str, bytes)):
            return Chain(max(self._data))
        return Chain(self._data)

    def min(self) -> "Chain[T]":
        """Find the minimum element."""
        if hasattr(self._data, "__iter__") and not isinstance(self._data, (str, bytes)):
            return Chain(min(self._data))
        return Chain(self._data)

    def first(self) -> "Chain[T]":
        """Get the first element."""
        if hasattr(self._data, "__iter__") and not isinstance(self._data, (str, bytes)):
            data_list = list(self._data)
            if data_list:
                return Chain(data_list[0])
            raise IndexError("Cannot get first element of empty sequence")
        return Chain(self._data)

    def last(self) -> "Chain[T]":
        """Get the last element."""
        if hasattr(self._data, "__iter__") and not isinstance(self._data, (str, bytes)):
            data_list = list(self._data)
            if data_list:
                return Chain(data_list[-1])
            raise IndexError("Cannot get last element of empty sequence")
        return Chain(self._data)

    def take_elements(self, n: int) -> "Chain[T]":
        """Take the first n elements."""
        if hasattr(self._data, "__iter__") and not isinstance(self._data, (str, bytes)):
            return Chain(list(self._data)[:n])  # type: ignore
        raise TypeError(f"Cannot take from non-iterable type: {type(self._data)}")

    def skip(self, n: int) -> "Chain[T]":
        """Skip the first n elements."""
        if hasattr(self._data, "__iter__") and not isinstance(self._data, (str, bytes)):
            return Chain(list(self._data)[n:])  # type: ignore
        raise TypeError(f"Cannot skip from non-iterable type: {type(self._data)}")

    def skip_elements(self, n: int) -> "Chain[T]":
        """Skip the first n elements (alias for skip)."""
        return self.skip(n)

    # Utility methods

    def to_list(self) -> List[T]:
        """Convert the current value to a list."""
        if hasattr(self._data, "__iter__") and not isinstance(self._data, (str, bytes)):
            return list(self._data)
        return [self._data]

    def to_list_single(self) -> List[T]:
        """Convert single value to a list (alias for to_list)."""
        return self.to_list()

    def value(self) -> T:
        """Return the current value of the chain (alias for direct access)."""
        return self._data

    def to_option(self) -> "Option[T]":
        """Convert the chain to an Option type."""
        if (
            hasattr(self._data, "__len__") and len(self._data) == 0
        ) or self._data is None:
            from .option import Nothing

            return Nothing()
        from .option import Some

        return Some(self._data)

    def to_result(self, error_on_empty: Any = "Empty chain") -> "Result[T, Any]":
        """Convert the chain to a Result type."""
        if (
            hasattr(self._data, "__len__") and len(self._data) == 0
        ) or self._data is None:
            from .result import Err

            return Err(error_on_empty)
        from .result import Ok

        return Ok(self._data)

    # Reduction methods

    def reduce(
        self, func: Callable[[U, T], U], initial: Optional[U] = None
    ) -> "Chain[U]":
        """Reduce elements using a function."""
        if hasattr(self._data, "__iter__") and not isinstance(self._data, (str, bytes)):
            if initial is not None:
                result = initial
                for item in self._data:
                    result = func(result, item)
                return Chain(result)
            else:
                data_list = list(self._data)
                if not data_list:
                    raise ValueError(
                        "Cannot reduce empty sequence without initial value"
                    )
                result = data_list[0]
                for item in data_list[1:]:
                    result = func(result, item)
                return Chain(result)
        # For non-iterable data, apply the function with initial value or
        # return the data as-is
        if initial is not None:
            return Chain(func(initial, self._data))
        return Chain(self._data)  # type: ignore

    def fold(
        self, func: Callable[[U, T], U], initial: Optional[U] = None
    ) -> "Chain[U]":
        """Alias for reduce() - reduce elements using a function."""
        return self.reduce(func, initial)

    def __repr__(self) -> str:
        return f"Chain({self._data!r})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Chain) and self._data == other._data


# Convenience functions


def chain(data: T) -> Chain[T]:
    """Create a new Chain with the given data."""
    return Chain(data)


def take(data: T) -> Chain[T]:
    """Create a new Chain with the given data (alias for chain)."""
    return Chain(data)


def from_result(result: "Result[T, E]") -> Chain[T]:
    """Create a Chain from a Result."""
    if result.is_err():
        raise ValueError(f"Attempted to create Chain from Err: {result.unwrap_err()}")
    return Chain(result.unwrap())


def from_option(option: "Option[T]", default: Any = None) -> Chain[T]:
    """Create a Chain from an Option."""
    if option.is_none():
        return Chain(default)
    return Chain(option.unwrap())

"""
Option<T> type for functional null handling.

Inspired by Rust's Option type and .NET's functional programming patterns.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")


class Option(Generic[T], ABC):
    """
    An Option type that represents either some value (Some) or no value (None).

    This enables functional null handling, making null checks explicit and composable.
    """

    @abstractmethod
    def is_some(self) -> bool:
        """Check if this Option contains a value."""
        pass

    @abstractmethod
    def is_none(self) -> bool:
        """Check if this Option contains no value."""
        pass

    @abstractmethod
    def map(self, func: Callable[[T], U]) -> "Option[U]":
        """Transform the contained value if Some, otherwise return None."""
        pass

    @abstractmethod
    def then(self, func: Callable[[T], "Option[U]"]) -> "Option[U]":
        """Chain operations that may return None (monadic bind)."""
        pass

    @abstractmethod
    def filter(self, predicate: Callable[[T], bool]) -> "Option[T]":
        """Filter the value, returning None if predicate fails."""
        pass

    @abstractmethod
    def unwrap(self) -> T:
        """Extract the value, raising an exception if None."""
        pass

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """Extract the value, or return default if None."""
        pass

    @abstractmethod
    def unwrap_or_else(self, func: Callable[[], T]) -> T:
        """Extract the value, or compute default if None."""
        pass

    def match(self, some_func: Callable[[T], U], none_func: Callable[[], U]) -> U:
        """
        Pattern match on the Option, applying appropriate function.

        This is the key method you mentioned - similar to .NET's match pattern.

        Args:
            some_func: Function to call with the value if Some
            none_func: Function to call if None

        Returns:
            Result of the appropriate function

        Example:
            result = option.match(
                some=lambda x: f"Found: {x}",
                none=lambda: "Nothing found"
            )
        """
        if self.is_some():
            return some_func(self.unwrap())
        else:
            return none_func()

    def and_then(self, func: Callable[[T], "Option[U]"]) -> "Option[U]":
        """Alias for then() - chain operations that may return None."""
        return self.then(func)

    def or_else(self, func: Callable[[], "Option[T]"]) -> "Option[T]":
        """Return this Option if Some, otherwise call func to get alternative."""
        if self.is_some():
            return self
        return func()

    def flatten(self) -> "Option[T]":
        """Flatten nested Options."""
        if self.is_some():
            inner = self.unwrap()
            if isinstance(inner, Option):
                return inner
        return self

    def zip(self, other: "Option[U]") -> "Option[tuple[T, U]]":
        """Combine two Options into an Option of tuple."""
        if self.is_some() and other.is_some():
            return Some((self.unwrap(), other.unwrap()))
        return Nothing()

    def to_list(self) -> list[T]:
        """Convert to list - empty if None, single item if Some."""
        if self.is_some():
            return [self.unwrap()]
        return []


class Some(Option[T]):
    """Some variant of Option - contains a value."""

    def __init__(self, value: T) -> None:
        if value is None:
            raise ValueError("Some cannot contain None - use Nothing() instead")
        self._value = value

    def is_some(self) -> bool:
        return True

    def is_none(self) -> bool:
        return False

    def map(self, func: Callable[[T], U]) -> "Option[U]":
        try:
            result = func(self._value)
            if result is None:
                return Nothing()
            return Some(result)
        except Exception:
            return Nothing()

    def then(self, func: Callable[[T], "Option[U]"]) -> "Option[U]":
        try:
            return func(self._value)
        except Exception:
            return Nothing()

    def filter(self, predicate: Callable[[T], bool]) -> "Option[T]":
        try:
            if predicate(self._value):
                return self
            return Nothing()
        except Exception:
            return Nothing()

    def unwrap(self) -> T:
        return self._value

    def unwrap_or(self, default: T) -> T:
        return self._value

    def unwrap_or_else(self, func: Callable[[], T]) -> T:
        return self._value

    def __repr__(self) -> str:
        return f"Some({self._value!r})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Some) and self._value == other._value


class Nothing(Option[T]):
    """Nothing variant of Option - contains no value."""

    def is_some(self) -> bool:
        return False

    def is_none(self) -> bool:
        return True

    def map(self, func: Callable[[T], U]) -> "Option[U]":
        return Nothing()

    def then(self, func: Callable[[T], "Option[U]"]) -> "Option[U]":
        return Nothing()

    def filter(self, predicate: Callable[[T], bool]) -> "Option[T]":
        return Nothing()

    def unwrap(self) -> T:
        raise ValueError("Called unwrap() on Nothing")

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, func: Callable[[], T]) -> T:
        return func()

    def __repr__(self) -> str:
        return "Nothing()"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Nothing)


# Convenience functions
def some(value: T) -> Option[T]:
    """Create a Some Option."""
    return Some(value)


def nothing() -> Option[T]:
    """Create a Nothing Option."""
    return Nothing()


def from_nullable(value: Union[T, None]) -> Option[T]:
    """
    Convert a nullable value to an Option.

    Args:
        value: Value that might be None

    Returns:
        Some(value) if value is not None, Nothing() if value is None
    """
    if value is None:
        return Nothing()
    return Some(value)


def from_list(lst: list[T]) -> Option[T]:
    """
    Get the first element of a list as an Option.

    Args:
        lst: List to get first element from

    Returns:
        Some(first_element) if list is not empty, Nothing() if empty
    """
    if lst:
        return Some(lst[0])
    return Nothing()


def from_dict(d: dict[Any, T], key: Any) -> Option[T]:
    """
    Get a value from a dictionary as an Option.

    Args:
        d: Dictionary to get value from
        key: Key to look up

    Returns:
        Some(value) if key exists, Nothing() if key not found
    """
    if key in d:
        return Some(d[key])
    return Nothing()


def safe_get(obj: Any, attr: str) -> Option[Any]:
    """
    Safely get an attribute from an object.

    Args:
        obj: Object to get attribute from
        attr: Attribute name

    Returns:
        Some(value) if attribute exists, Nothing() if not found
    """
    try:
        return Some(getattr(obj, attr))
    except AttributeError:
        return Nothing()


def safe_index(lst: list[T], index: int) -> Option[T]:
    """
    Safely get an element from a list by index.

    Args:
        lst: List to index into
        index: Index to access

    Returns:
        Some(element) if index is valid, Nothing() if out of bounds
    """
    try:
        return Some(lst[index])
    except (IndexError, TypeError):
        return Nothing()


def collect_options(options: list[Option[T]]) -> Option[list[T]]:
    """
    Collect a list of Options into a single Option.

    If all Options are Some, returns Some with list of values.
    If any Option is Nothing, returns Nothing.

    Args:
        options: List of Options to collect

    Returns:
        Some(list[T]) if all Some, Nothing if any Nothing
    """
    values = []
    for option in options:
        if option.is_none():
            return Nothing()
        values.append(option.unwrap())
    return Some(values)


def traverse_options(items: list[T], func: Callable[[T], Option[U]]) -> Option[list[U]]:
    """
    Apply a function to each item and collect the results.

    If all applications succeed (return Some), returns Some with list of results.
    If any application fails (returns Nothing), returns Nothing.

    Args:
        items: List of items to process
        func: Function that may return Nothing

    Returns:
        Some(list[U]) if all succeed, Nothing if any fails
    """
    results = [func(item) for item in items]
    return collect_options(results)

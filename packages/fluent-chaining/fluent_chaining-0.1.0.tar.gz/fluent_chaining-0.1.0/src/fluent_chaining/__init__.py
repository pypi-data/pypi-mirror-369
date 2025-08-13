"""
Fluent Chaining - Pure functional programming with prose-like syntax.

A Python package that enables functional programming with fluent method chaining
that reads like natural language, making code more expressive and readable.

Example:
    from fluent_chaining import take

    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    result = (take(numbers)
        .where(lambda x: x % 2 == 0)
        .transform(lambda x: x ** 2)
        .that_are_greater_than(10)
        .sum()
        .to_list())
"""

from .core import Chain, chain, from_option, from_result, take
from .operations import (
    always,
    apply,
    compose,
    constant,
    curry,
    exists,
    flip,
    identity,
    memoize,
    partial,
    pipe,
    tap,
)
from .option import (
    Nothing,
    Option,
    Some,
    collect_options,
    from_dict,
    from_list,
    from_nullable,
    nothing,
    safe_get,
    safe_index,
    some,
    traverse_options,
)
from .result import (
    Err,
    Ok,
    Result,
    collect_results,
    err,
    ok,
    safe,
    try_parse_float,
    try_parse_int,
)

__version__ = "0.1.0"
__all__ = [
    # Core functionality
    "Chain",
    "take",
    "chain",
    "from_result",
    "from_option",
    # Advanced functional programming utilities
    "compose",
    "pipe",
    "curry",
    "partial",
    "memoize",
    "identity",
    "constant",
    "flip",
    "apply",
    "always",
    "exists",
    "tap",
    # Monadic types for error and null handling
    "Result",
    "Ok",
    "Err",
    "ok",
    "err",
    "safe",
    "try_parse_int",
    "try_parse_float",
    "collect_results",
    "Option",
    "Some",
    "Nothing",
    "some",
    "nothing",
    "from_nullable",
    "from_list",
    "from_dict",
    "safe_get",
    "safe_index",
    "collect_options",
    "traverse_options",
]

"""
Tests for Result<T> type and related functionality.
"""

import pytest

from fluent_chaining import (
    Err,
    Ok,
    collect_results,
    err,
    from_result,
    ok,
    safe,
    take,
    try_parse_float,
    try_parse_int,
)


class TestResultBasics:
    """Test basic Result functionality."""

    def test_ok_creation(self):
        """Test creating Ok results."""
        result = Ok(42)
        assert result.is_ok()
        assert not result.is_err()
        assert result.unwrap() == 42

    def test_err_creation(self):
        """Test creating Err results."""
        result = Err("error message")
        assert result.is_err()
        assert not result.is_ok()
        assert result.unwrap_err() == "error message"

    def test_convenience_functions(self):
        """Test ok() and err() convenience functions."""
        ok_result = ok(100)
        assert ok_result.is_ok()
        assert ok_result.unwrap() == 100

        err_result = err("failed")
        assert err_result.is_err()
        assert err_result.unwrap_err() == "failed"

    def test_unwrap_errors(self):
        """Test unwrap methods raise appropriate errors."""
        ok_result = Ok(42)
        err_result = Err("error")

        # Can't unwrap error from Ok
        with pytest.raises(ValueError, match="Called unwrap_err"):
            ok_result.unwrap_err()

        # Can't unwrap value from Err
        with pytest.raises(ValueError, match="Called unwrap"):
            err_result.unwrap()

    def test_equality(self):
        """Test Result equality."""
        assert Ok(42) == Ok(42)
        assert Err("error") == Err("error")
        assert Ok(42) != Ok(43)
        assert Err("error") != Err("different")
        assert Ok(42) != Err("error")

    def test_repr(self):
        """Test string representation."""
        assert repr(Ok(42)) == "Ok(42)"
        assert repr(Err("error")) == "Err('error')"


class TestResultOperations:
    """Test Result functional operations."""

    def test_map_ok(self):
        """Test mapping over Ok values."""
        result = Ok(5).map(lambda x: x * 2)
        assert result == Ok(10)

    def test_map_err(self):
        """Test mapping over Err values passes through."""
        result = Err("error").map(lambda x: x * 2)
        assert result == Err("error")

    def test_map_err_transformation(self):
        """Test transforming error values."""
        result = Err("error").map_err(lambda e: f"Failed: {e}")
        assert result == Err("Failed: error")

    def test_map_err_on_ok(self):
        """Test map_err on Ok values passes through."""
        result = Ok(42).map_err(lambda e: f"Failed: {e}")
        assert result == Ok(42)

    def test_then_ok(self):
        """Test chaining operations on Ok values."""

        def divide_by_two(x):
            if x % 2 == 0:
                return Ok(x // 2)
            return Err("Not divisible by 2")

        result = Ok(10).then(divide_by_two)
        assert result == Ok(5)

        result = Ok(5).then(divide_by_two)
        assert result == Err("Not divisible by 2")

    def test_then_err(self):
        """Test chaining operations on Err values."""

        def divide_by_two(x):
            return Ok(x // 2)

        result = Err("initial error").then(divide_by_two)
        assert result == Err("initial error")

    def test_unwrap_or(self):
        """Test unwrap_or with default values."""
        assert Ok(42).unwrap_or(0) == 42
        assert Err("error").unwrap_or(0) == 0

    def test_unwrap_or_else(self):
        """Test unwrap_or_else with function."""
        assert Ok(42).unwrap_or_else(lambda e: 0) == 42
        assert Err("error").unwrap_or_else(lambda e: len(e)) == 5

    def test_match(self):
        """Test pattern matching."""
        ok_result = Ok(42)
        err_result = Err("error")

        ok_matched = ok_result.match(
            ok_func=lambda x: f"Success: {x}", err_func=lambda e: f"Error: {e}"
        )
        assert ok_matched == "Success: 42"

        err_matched = err_result.match(
            ok_func=lambda x: f"Success: {x}", err_func=lambda e: f"Error: {e}"
        )
        assert err_matched == "Error: error"

    def test_and_then_alias(self):
        """Test that and_then is an alias for then."""

        def double(x):
            return Ok(x * 2)

        result1 = Ok(5).then(double)
        result2 = Ok(5).and_then(double)
        assert result1 == result2

    def test_or_else(self):
        """Test or_else for error recovery."""

        def recovery(error):
            return Ok(f"Recovered from: {error}")

        ok_result = Ok(42).or_else(recovery)
        assert ok_result == Ok(42)

        err_result = Err("error").or_else(recovery)
        assert err_result == Ok("Recovered from: error")

    def test_filter(self):
        """Test filtering Results."""
        # Ok value that passes filter
        result = Ok(10).filter(lambda x: x > 5, "Too small")
        assert result == Ok(10)

        # Ok value that fails filter
        result = Ok(3).filter(lambda x: x > 5, "Too small")
        assert result == Err("Too small")

        # Err value passes through
        result = Err("original error").filter(lambda x: x > 5, "Too small")
        assert result == Err("original error")

    def test_flatten(self):
        """Test flattening nested Results."""
        nested_ok = Ok(Ok(42))
        flattened = nested_ok.flatten()
        assert flattened == Ok(42)

        nested_err = Ok(Err("inner error"))
        flattened = nested_err.flatten()
        assert flattened == Err("inner error")

        regular_ok = Ok(42)
        flattened = regular_ok.flatten()
        assert flattened == Ok(42)


class TestSafeDecorator:
    """Test the @safe decorator."""

    def test_safe_success(self):
        """Test @safe with successful function."""

        @safe
        def divide(x, y):
            return x / y

        result = divide(10, 2)
        assert result == Ok(5.0)

    def test_safe_exception(self):
        """Test @safe with function that raises exception."""

        @safe
        def divide(x, y):
            return x / y

        result = divide(10, 0)
        assert result.is_err()
        assert isinstance(result.unwrap_err(), ZeroDivisionError)

    def test_safe_with_args_kwargs(self):
        """Test @safe with various argument patterns."""

        @safe
        def complex_function(a, b, c=1, d=2):
            return a + b + c + d

        result = complex_function(1, 2, c=3, d=4)
        assert result == Ok(10)


class TestParsingFunctions:
    """Test parsing utility functions."""

    def test_try_parse_int_success(self):
        """Test successful integer parsing."""
        result = try_parse_int("42")
        assert result == Ok(42)

        result = try_parse_int("-123")
        assert result == Ok(-123)

    def test_try_parse_int_failure(self):
        """Test failed integer parsing."""
        result = try_parse_int("not a number")
        assert result.is_err()
        assert "Cannot parse" in result.unwrap_err()

        result = try_parse_int("3.14")
        assert result.is_err()

    def test_try_parse_float_success(self):
        """Test successful float parsing."""
        result = try_parse_float("3.14")
        assert result == Ok(3.14)

        result = try_parse_float("-2.5")
        assert result == Ok(-2.5)

        result = try_parse_float("42")
        assert result == Ok(42.0)

    def test_try_parse_float_failure(self):
        """Test failed float parsing."""
        result = try_parse_float("not a number")
        assert result.is_err()
        assert "Cannot parse" in result.unwrap_err()


class TestCollectResults:
    """Test collecting multiple Results."""

    def test_collect_all_ok(self):
        """Test collecting when all Results are Ok."""
        results = [Ok(1), Ok(2), Ok(3)]
        collected = collect_results(results)
        assert collected == Ok([1, 2, 3])

    def test_collect_with_err(self):
        """Test collecting when some Results are Err."""
        results = [Ok(1), Err("error"), Ok(3)]
        collected = collect_results(results)
        assert collected == Err("error")

    def test_collect_empty(self):
        """Test collecting empty list."""
        results = []
        collected = collect_results(results)
        assert collected == Ok([])


class TestResultWithChain:
    """Test integration between Result and Chain."""

    def test_chain_to_result(self):
        """Test converting Chain to Result."""
        # Non-empty chain
        result = take([1, 2, 3]).to_result()
        assert result.is_ok()
        assert result.unwrap() == [1, 2, 3]

        # Empty chain
        result = take([]).to_result("Empty list")
        assert result.is_err()
        assert result.unwrap_err() == "Empty list"

        # None chain
        result = take(None).to_result("Was None")
        assert result.is_err()
        assert result.unwrap_err() == "Was None"

    def test_from_result(self):
        """Test creating Chain from Result."""
        # From Ok
        chain = from_result(Ok([1, 2, 3]))
        assert chain.value() == [1, 2, 3]

        # From Err should raise
        with pytest.raises(ValueError):
            from_result(Err("error"))


class TestComplexResultChains:
    """Test complex chains using Results."""

    def test_parsing_pipeline(self):
        """Test a complex parsing and processing pipeline."""
        input_strings = ["1", "2", "invalid", "4"]

        # Parse all strings, collect successful parses
        parsed_results = [try_parse_int(s) for s in input_strings]
        successful_parses = [r.unwrap() for r in parsed_results if r.is_ok()]

        # Process with chain
        result = take(successful_parses).transform(lambda x: x * 2).sum().value()

        assert result == 14  # (1 + 2 + 4) * 2 = 14

    def test_safe_division_chain(self):
        """Test safe division operations."""

        @safe
        def safe_divide(x, y):
            return x / y

        # Successful operations
        results = [safe_divide(10, 2), safe_divide(15, 3), safe_divide(20, 4)]

        successful_values = [r.unwrap() for r in results if r.is_ok()]
        total = take(successful_values).sum().value()
        assert total == 15.0  # 5.0 + 5.0 + 5.0

        # With some failures
        results_with_errors = [
            safe_divide(10, 2),
            safe_divide(10, 0),  # Division by zero
            safe_divide(15, 3),
        ]

        successful_values = [r.unwrap() for r in results_with_errors if r.is_ok()]
        total = take(successful_values).sum().value()
        assert total == 10.0  # 5.0 + 5.0

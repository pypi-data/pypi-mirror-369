"""
Tests for Option<T> type and related functionality.
"""

import pytest

from fluent_chaining import (
    Nothing,
    Some,
    collect_options,
    from_dict,
    from_list,
    from_nullable,
    from_option,
    nothing,
    safe_get,
    safe_index,
    some,
    take,
    traverse_options,
)


class TestOptionBasics:
    """Test basic Option functionality."""

    def test_some_creation(self):
        """Test creating Some options."""
        option = Some(42)
        assert option.is_some()
        assert not option.is_none()
        assert option.unwrap() == 42

    def test_nothing_creation(self):
        """Test creating Nothing options."""
        option = Nothing()
        assert option.is_none()
        assert not option.is_some()

    def test_some_cannot_contain_none(self):
        """Test that Some cannot contain None."""
        with pytest.raises(ValueError, match="Some cannot contain None"):
            Some(None)

    def test_convenience_functions(self):
        """Test some() and nothing() convenience functions."""
        some_option = some(100)
        assert some_option.is_some()
        assert some_option.unwrap() == 100

        nothing_option = nothing()
        assert nothing_option.is_none()

    def test_unwrap_errors(self):
        """Test unwrap methods raise appropriate errors."""
        some_option = Some(42)
        nothing_option = Nothing()

        # Can unwrap Some
        assert some_option.unwrap() == 42

        # Can't unwrap Nothing
        with pytest.raises(ValueError, match="Called unwrap"):
            nothing_option.unwrap()

    def test_equality(self):
        """Test Option equality."""
        assert Some(42) == Some(42)
        assert Nothing() == Nothing()
        assert Some(42) != Some(43)
        assert Some(42) != Nothing()
        assert Nothing() != Some(42)

    def test_repr(self):
        """Test string representation."""
        assert repr(Some(42)) == "Some(42)"
        assert repr(Nothing()) == "Nothing()"


class TestOptionOperations:
    """Test Option functional operations."""

    def test_map_some(self):
        """Test mapping over Some values."""
        result = Some(5).map(lambda x: x * 2)
        assert result == Some(10)

    def test_map_nothing(self):
        """Test mapping over Nothing values."""
        result = Nothing().map(lambda x: x * 2)
        assert result == Nothing()

    def test_map_returns_nothing_for_none_result(self):
        """Test that map returns Nothing if function returns None."""
        result = Some(5).map(lambda x: None)
        assert result == Nothing()

    def test_map_exception_handling(self):
        """Test that map returns Nothing if function raises exception."""
        result = Some(5).map(lambda x: 1 / 0)  # Division by zero
        assert result == Nothing()

    def test_then_some(self):
        """Test chaining operations on Some values."""

        def safe_divide_by_two(x):
            if x % 2 == 0:
                return Some(x // 2)
            return Nothing()

        result = Some(10).then(safe_divide_by_two)
        assert result == Some(5)

        result = Some(5).then(safe_divide_by_two)
        assert result == Nothing()

    def test_then_nothing(self):
        """Test chaining operations on Nothing values."""

        def safe_divide_by_two(x):
            return Some(x // 2)

        result = Nothing().then(safe_divide_by_two)
        assert result == Nothing()

    def test_filter_some(self):
        """Test filtering Some values."""
        # Value passes filter
        result = Some(10).filter(lambda x: x > 5)
        assert result == Some(10)

        # Value fails filter
        result = Some(3).filter(lambda x: x > 5)
        assert result == Nothing()

    def test_filter_nothing(self):
        """Test filtering Nothing values."""
        result = Nothing().filter(lambda x: x > 5)
        assert result == Nothing()

    def test_filter_exception_handling(self):
        """Test that filter returns Nothing if predicate raises exception."""
        result = Some(5).filter(lambda x: 1 / 0 > x)  # Division by zero
        assert result == Nothing()

    def test_unwrap_or(self):
        """Test unwrap_or with default values."""
        assert Some(42).unwrap_or(0) == 42
        assert Nothing().unwrap_or(0) == 0

    def test_unwrap_or_else(self):
        """Test unwrap_or_else with function."""
        assert Some(42).unwrap_or_else(lambda: 0) == 42
        assert Nothing().unwrap_or_else(lambda: 999) == 999

    def test_match(self):
        """Test pattern matching - the key feature you requested!"""
        some_option = Some(42)
        nothing_option = Nothing()

        # Match Some
        some_matched = some_option.match(
            some_func=lambda x: f"Found: {x}", none_func=lambda: "Nothing found"
        )
        assert some_matched == "Found: 42"

        # Match Nothing
        nothing_matched = nothing_option.match(
            some_func=lambda x: f"Found: {x}", none_func=lambda: "Nothing found"
        )
        assert nothing_matched == "Nothing found"

    def test_and_then_alias(self):
        """Test that and_then is an alias for then."""

        def double(x):
            return Some(x * 2)

        result1 = Some(5).then(double)
        result2 = Some(5).and_then(double)
        assert result1 == result2

    def test_or_else(self):
        """Test or_else for providing alternatives."""

        def alternative():
            return Some("alternative value")

        some_result = Some(42).or_else(alternative)
        assert some_result == Some(42)

        nothing_result = Nothing().or_else(alternative)
        assert nothing_result == Some("alternative value")

    def test_flatten(self):
        """Test flattening nested Options."""
        nested_some = Some(Some(42))
        flattened = nested_some.flatten()
        assert flattened == Some(42)

        nested_nothing = Some(Nothing())
        flattened = nested_nothing.flatten()
        assert flattened == Nothing()

        regular_some = Some(42)
        flattened = regular_some.flatten()
        assert flattened == Some(42)

    def test_zip(self):
        """Test zipping two Options."""
        some1 = Some(1)
        some2 = Some(2)
        nothing_opt = Nothing()

        # Both Some
        result = some1.zip(some2)
        assert result == Some((1, 2))

        # First Nothing
        result = nothing_opt.zip(some2)
        assert result == Nothing()

        # Second Nothing
        result = some1.zip(nothing_opt)
        assert result == Nothing()

        # Both Nothing
        result = nothing_opt.zip(Nothing())
        assert result == Nothing()

    def test_to_list(self):
        """Test converting to list."""
        assert Some(42).to_list() == [42]
        assert Nothing().to_list() == []


class TestUtilityFunctions:
    """Test utility functions for creating Options."""

    def test_from_nullable(self):
        """Test creating Option from nullable value."""
        assert from_nullable(42) == Some(42)
        assert from_nullable(None) == Nothing()
        assert from_nullable("hello") == Some("hello")

    def test_from_list(self):
        """Test creating Option from list."""
        assert from_list([1, 2, 3]) == Some(1)
        assert from_list([]) == Nothing()
        assert from_list(["hello", "world"]) == Some("hello")

    def test_from_dict(self):
        """Test creating Option from dictionary lookup."""
        d = {"a": 1, "b": 2}

        assert from_dict(d, "a") == Some(1)
        assert from_dict(d, "c") == Nothing()
        assert from_dict({}, "key") == Nothing()

    def test_safe_get(self):
        """Test safely getting attributes."""

        class TestObj:
            def __init__(self):
                self.existing_attr = "value"

        obj = TestObj()

        assert safe_get(obj, "existing_attr") == Some("value")
        assert safe_get(obj, "nonexistent_attr") == Nothing()

    def test_safe_index(self):
        """Test safely indexing into lists."""
        lst = [1, 2, 3]

        assert safe_index(lst, 0) == Some(1)
        assert safe_index(lst, 2) == Some(3)
        assert safe_index(lst, 5) == Nothing()
        assert safe_index(lst, -1) == Some(3)  # Negative indexing works
        assert safe_index(lst, -10) == Nothing()  # Out of bounds negative


class TestCollectingOptions:
    """Test collecting multiple Options."""

    def test_collect_all_some(self):
        """Test collecting when all Options are Some."""
        options = [Some(1), Some(2), Some(3)]
        collected = collect_options(options)
        assert collected == Some([1, 2, 3])

    def test_collect_with_nothing(self):
        """Test collecting when some Options are Nothing."""
        options = [Some(1), Nothing(), Some(3)]
        collected = collect_options(options)
        assert collected == Nothing()

    def test_collect_empty(self):
        """Test collecting empty list."""
        options = []
        collected = collect_options(options)
        assert collected == Some([])

    def test_traverse_options(self):
        """Test traversing with function that returns Options."""

        def safe_sqrt(x):
            if x >= 0:
                return Some(x**0.5)
            return Nothing()

        # All positive numbers
        result = traverse_options([1, 4, 9], safe_sqrt)
        assert result == Some([1.0, 2.0, 3.0])

        # Contains negative number
        result = traverse_options([1, -4, 9], safe_sqrt)
        assert result == Nothing()

        # Empty list
        result = traverse_options([], safe_sqrt)
        assert result == Some([])


class TestOptionWithChain:
    """Test integration between Option and Chain."""

    def test_chain_to_option(self):
        """Test converting Chain to Option."""
        # Non-empty chain
        option = take([1, 2, 3]).to_option()
        assert option.is_some()
        assert option.unwrap() == [1, 2, 3]

        # Empty chain
        option = take([]).to_option()
        assert option.is_none()

        # None chain
        option = take(None).to_option()
        assert option.is_none()

    def test_from_option(self):
        """Test creating Chain from Option."""
        # From Some
        chain = from_option(Some([1, 2, 3]))
        assert chain.value() == [1, 2, 3]

        # From Nothing with default
        chain = from_option(Nothing(), [0])
        assert chain.value() == [0]

        # From Nothing without default
        chain = from_option(Nothing())
        assert chain.value() is None


class TestComplexOptionChains:
    """Test complex usage patterns with Options."""

    def test_safe_parsing_pipeline(self):
        """Test a safe parsing pipeline using Options."""

        def safe_parse_positive_int(s):
            try:
                value = int(s)
                if value > 0:
                    return Some(value)
                return Nothing()
            except ValueError:
                return Nothing()

        inputs = ["1", "2", "invalid", "-5", "10"]

        # Parse and collect successful positive integers
        options = [safe_parse_positive_int(s) for s in inputs]
        successful_values = [opt.unwrap() for opt in options if opt.is_some()]

        result = take(successful_values).sum().value()
        assert result == 13  # 1 + 2 + 10

    def test_nested_data_access(self):
        """Test safe nested data access."""
        data = {
            "users": [
                {"name": "Alice", "profile": {"age": 25}},
                {"name": "Bob"},  # Missing profile
                {"name": "Charlie", "profile": {"age": 30}},
            ]
        }

        # Safely extract ages
        def get_user_age(user):
            return from_dict(user, "profile").then(
                lambda profile: from_dict(profile, "age")
            )

        users = data["users"]
        ages = [get_user_age(user) for user in users]
        valid_ages = [age.unwrap() for age in ages if age.is_some()]

        assert valid_ages == [25, 30]
        average_age = take(valid_ages).sum().value() / len(valid_ages)
        assert average_age == 27.5

    def test_option_match_patterns(self):
        """Test various match patterns - showcasing the key feature."""

        def process_optional_value(opt):
            return opt.match(
                some_func=lambda x: f"Processing: {x * 2}",
                none_func=lambda: "No value to process",
            )

        assert process_optional_value(Some(5)) == "Processing: 10"
        assert process_optional_value(Nothing()) == "No value to process"

        # More complex match with side effects
        processed_count = 0

        def process_some(value):
            nonlocal processed_count
            processed_count += 1
            return value * 2

        def process_none():
            return 0

        def process_with_side_effect(opt):
            return opt.match(some_func=process_some, none_func=process_none)

        values = [Some(1), Nothing(), Some(3), Nothing(), Some(5)]
        results = [process_with_side_effect(val) for val in values]

        assert results == [2, 0, 6, 0, 10]
        assert processed_count == 3  # Only Some values were processed

    def test_chaining_options_with_fluent_api(self):
        """Test combining Options with fluent chaining."""

        # Create a pipeline that safely processes data
        def safe_process_user_data(user_data):
            return (
                from_dict(user_data, "scores")
                .filter(lambda scores: len(scores) > 0)
                .map(lambda scores: take(scores).where(lambda x: x >= 0).sum().value())
            )

        user1 = {"name": "Alice", "scores": [85, 92, 78]}
        user2 = {"name": "Bob", "scores": []}
        user3 = {"name": "Charlie"}  # No scores key
        user4 = {"name": "Diana", "scores": [95, -10, 88]}  # Contains negative

        results = [
            safe_process_user_data(user) for user in [user1, user2, user3, user4]
        ]

        # Extract successful results
        successful_scores = [r.unwrap() for r in results if r.is_some()]
        assert successful_scores == [
            255,
            183,
        ]  # Alice: 85+92+78, Diana: 95+88 (negative filtered)

        # Use match to provide user-friendly messages
        messages = []
        for i, result in enumerate(results):
            user_name = [user1, user2, user3, user4][i]["name"]
            message = result.match(
                some_func=lambda score: f"{user_name}: Total score {score}",
                none_func=lambda: f"{user_name}: No valid scores",
            )
            messages.append(message)

        expected_messages = [
            "Alice: Total score 255",
            "Bob: No valid scores",
            "Charlie: No valid scores",
            "Diana: Total score 183",
        ]
        assert messages == expected_messages

"""
Tests for advanced features and utilities.
"""

import pytest

from fluent_chaining import (
    always,
    apply,
    constant,
    exists,
    flip,
    identity,
    memoize,
    take,
    tap,
)


class TestAdvancedFunctions:
    """Test advanced functional programming utilities."""

    def test_memoize(self):
        """Test memoization functionality."""
        call_count = 0

        @memoize
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * x

        # First call
        result1 = expensive_function(5)
        assert result1 == 25
        assert call_count == 1

        # Second call with same argument (should use cache)
        result2 = expensive_function(5)
        assert result2 == 25
        assert call_count == 1  # Should not increment

        # Call with different argument
        result3 = expensive_function(6)
        assert result3 == 36
        assert call_count == 2

    def test_identity(self):
        """Test identity function."""
        assert identity(42) == 42
        assert identity("hello") == "hello"
        assert identity([1, 2, 3]) == [1, 2, 3]

    def test_constant(self):
        """Test constant function generator."""
        always_true = constant(True)
        assert always_true() is True
        assert always_true(1, 2, 3) is True
        assert always_true(foo="bar") is True

        always_42 = constant(42)
        assert always_42("anything") == 42

    def test_flip(self):
        """Test argument order flipping."""

        def subtract(x, y):
            return x - y

        flipped_subtract = flip(subtract)
        assert subtract(10, 5) == 5
        assert flipped_subtract(5, 10) == 5  # Arguments flipped: 10 - 5

    def test_apply(self):
        """Test function application."""

        def add(x, y):
            return x + y

        result = apply(add, 3, 5)
        assert result == 8

        result = apply(add, x=3, y=5)
        assert result == 8

    def test_always(self):
        """Test universal quantification."""

        def is_positive(x):
            return x > 0

        all_positive = always(is_positive)

        assert all_positive([1, 2, 3, 4]) is True
        assert all_positive([1, 2, -3, 4]) is False
        assert all_positive([]) is True  # Vacuously true

    def test_exists(self):
        """Test existential quantification."""

        def is_even(x):
            return x % 2 == 0

        any_even = exists(is_even)

        assert any_even([1, 3, 4, 5]) is True
        assert any_even([1, 3, 5]) is False
        assert any_even([]) is False

    def test_tap(self):
        """Test tap function for side effects."""
        side_effects = []

        def record_side_effect(x):
            side_effects.append(x)

        tap_record = tap(record_side_effect)

        # Test that tap returns the original value
        result = tap_record(42)
        assert result == 42
        assert side_effects == [42]

        # Test in a chain
        result = take([1, 2, 3]).transform(tap_record).sum().value()

        assert result == 6
        assert side_effects == [42, 1, 2, 3]


class TestAdvancedChainMethods:
    """Test advanced methods added to Chain class."""

    def test_tap_chain(self):
        """Test tap_chain method for side effects."""
        side_effects = []

        def record(data):
            side_effects.append(data)

        result = take([1, 2, 3]).tap_chain(record).sum().value()

        assert result == 6
        assert side_effects == [[1, 2, 3]]

    def test_side_effect_alias(self):
        """Test that side_effect is an alias for tap_chain."""
        side_effects = []

        def record(data):
            side_effects.append(data)

        result = take([1, 2, 3]).side_effect(record).sum().value()

        assert result == 6
        assert side_effects == [[1, 2, 3]]

    def test_debug(self):
        """Test debug method (captured output not tested, just functionality)."""
        result = take([1, 2, 3]).debug("Numbers").sum().value()

        assert result == 6

    def test_apply_if(self):
        """Test conditional application."""

        def double_transform(chain):
            return chain.transform(lambda x: x * 2)

        # True condition
        result = take([1, 2, 3]).apply_if(True, double_transform).value()
        assert result == [2, 4, 6]

        # False condition
        result = take([1, 2, 3]).apply_if(False, double_transform).value()
        assert result == [1, 2, 3]

    def test_apply_when(self):
        """Test predicate-based application."""

        def double_transform(chain):
            return chain.transform(lambda x: x * 2)

        # Predicate true (sum > 5)
        result = (
            take([1, 2, 3])
            .apply_when(lambda data: sum(data) > 5, double_transform)
            .value()
        )
        assert result == [2, 4, 6]

        # Predicate false (sum > 10)
        result = (
            take([1, 2, 3])
            .apply_when(lambda data: sum(data) > 10, double_transform)
            .value()
        )
        assert result == [1, 2, 3]

    def test_branch(self):
        """Test branching logic."""

        def double_transform(chain):
            return chain.transform(lambda x: x * 2)

        def add_ten_transform(chain):
            return chain.transform(lambda x: x + 10)

        # True branch
        result = (
            take([1, 2, 3]).branch(True, double_transform, add_ten_transform).value()
        )
        assert result == [2, 4, 6]

        # False branch
        result = (
            take([1, 2, 3]).branch(False, double_transform, add_ten_transform).value()
        )
        assert result == [11, 12, 13]

        # False branch with no else
        result = take([1, 2, 3]).branch(False, double_transform).value()
        assert result == [1, 2, 3]

    def test_assert_that(self):
        """Test assertion functionality."""
        # Successful assertion
        result = (
            take([1, 2, 3])
            .assert_that(lambda data: len(data) == 3, "Should have 3 elements")
            .sum()
            .value()
        )
        assert result == 6

        # Failed assertion
        with pytest.raises(AssertionError, match="Should be positive"):
            take([-1, -2, -3]).assert_that(
                lambda data: all(x > 0 for x in data), "Should be positive"
            )

    def test_or_else(self):
        """Test default value functionality."""
        # Non-empty list
        result = take([1, 2, 3]).or_else([0]).value()
        assert result == [1, 2, 3]

        # Empty list
        result = take([]).or_else([0]).value()
        assert result == [0]

        # None value
        result = take(None).or_else("default").value()
        assert result == "default"


class TestComplexAdvancedChains:
    """Test complex chains using advanced features."""

    def test_fibonacci_with_memoization(self):
        """Test fibonacci calculation with memoization."""

        @memoize
        def fibonacci(n):
            if n < 2:
                return n
            return fibonacci(n - 1) + fibonacci(n - 2)

        # Calculate fibonacci numbers using chaining
        result = take(range(10)).transform(fibonacci).value()

        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        assert result == expected

    def test_complex_functional_pipeline(self):
        """Test complex pipeline with multiple advanced features."""
        from fluent_chaining import compose

        # Create composed transformation
        double_and_add_one = compose(lambda x: x + 1, lambda x: x * 2)

        # Track side effects
        processed_values = []

        def track_processing(value):
            processed_values.append(value)

        result = (
            take([1, 2, 3, 4, 5])
            .where(lambda x: x % 2 == 1)  # [1, 3, 5]
            .transform(double_and_add_one)  # [3, 7, 11]
            .tap_chain(track_processing)
            .apply_if(
                True, lambda chain: chain.transform(lambda x: x * 10)
            )  # [30, 70, 110]
            .assert_that(lambda data: all(x >= 30 for x in data), "All should be >= 30")
            .sum()
            .value()
        )

        assert result == 210  # 30 + 70 + 110
        assert processed_values == [[3, 7, 11]]

    def test_data_processing_with_branching(self):
        """Test data processing with conditional branching."""

        def process_small_dataset(chain):
            return chain.transform(lambda x: x * 2)

        def process_large_dataset(chain):
            return chain.transform(lambda x: x * 3).take_elements(5)

        # Small dataset
        small_data = [1, 2, 3]
        result = (
            take(small_data)
            .branch(len(small_data) < 5, process_small_dataset, process_large_dataset)
            .sum()
            .value()
        )
        assert result == 12  # (1*2 + 2*2 + 3*2) = 12

        # Large dataset
        large_data = list(range(1, 11))  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = (
            take(large_data)
            .branch(len(large_data) < 5, process_small_dataset, process_large_dataset)
            .sum()
            .value()
        )
        assert result == 45  # (1*3 + 2*3 + 3*3 + 4*3 + 5*3) = 45

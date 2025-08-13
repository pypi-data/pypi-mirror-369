"""
Tests for the core fluent chaining functionality.
"""

import pytest

from fluent_chaining import Chain, chain, take


class TestChainBasics:
    """Test basic Chain functionality."""

    def test_chain_initialization(self):
        """Test that Chain can be initialized with data."""
        data = [1, 2, 3]
        c = Chain(data)
        assert c.value() == data

    def test_take_function(self):
        """Test the take() entry point function."""
        data = [1, 2, 3]
        result = take(data)
        assert isinstance(result, Chain)
        assert result.value() == data

    def test_chain_function(self):
        """Test the chain() entry point function."""
        data = [1, 2, 3]
        result = chain(data)
        assert isinstance(result, Chain)
        assert result.value() == data


class TestFilteringOperations:
    """Test filtering operations."""

    def test_where_basic(self):
        """Test basic where filtering."""
        numbers = [1, 2, 3, 4, 5]
        result = take(numbers).where(lambda x: x > 3).value()
        assert result == [4, 5]

    def test_where_even_numbers(self):
        """Test filtering even numbers."""
        numbers = [1, 2, 3, 4, 5, 6]
        result = take(numbers).where(lambda x: x % 2 == 0).value()
        assert result == [2, 4, 6]

    def test_filter_alias(self):
        """Test that filter() is an alias for where()."""
        numbers = [1, 2, 3, 4, 5]
        where_result = take(numbers).where(lambda x: x > 3).value()
        filter_result = take(numbers).filter(lambda x: x > 3).value()
        assert where_result == filter_result

    def test_that_are_greater_than(self):
        """Test the prose-like that_are_greater_than method."""
        numbers = [1, 2, 3, 4, 5]
        result = take(numbers).that_are_greater_than(3).value()
        assert result == [4, 5]

    def test_that_are_less_than(self):
        """Test the prose-like that_are_less_than method."""
        numbers = [1, 2, 3, 4, 5]
        result = take(numbers).that_are_less_than(3).value()
        assert result == [1, 2]

    def test_that_equal(self):
        """Test the prose-like that_equal method."""
        numbers = [1, 2, 3, 2, 4]
        result = take(numbers).that_equal(2).value()
        assert result == [2, 2]

    def test_that_are_alias(self):
        """Test that that_are() is an alias for where()."""
        numbers = [1, 2, 3, 4, 5]
        where_result = take(numbers).where(lambda x: x % 2 == 0).value()
        that_are_result = take(numbers).that_are(lambda x: x % 2 == 0).value()
        assert where_result == that_are_result


class TestTransformationOperations:
    """Test transformation operations."""

    def test_transform_basic(self):
        """Test basic transform operation."""
        numbers = [1, 2, 3]
        result = take(numbers).transform(lambda x: x * 2).value()
        assert result == [2, 4, 6]

    def test_map_alias(self):
        """Test that map() is an alias for transform()."""
        numbers = [1, 2, 3]
        transform_result = take(numbers).transform(lambda x: x * 2).value()
        map_result = take(numbers).map(lambda x: x * 2).value()
        assert transform_result == map_result

    def test_multiplied_by(self):
        """Test the prose-like multiplied_by method."""
        numbers = [1, 2, 3]
        result = take(numbers).multiplied_by(3).value()
        assert result == [3, 6, 9]

    def test_divided_by(self):
        """Test the prose-like divided_by method."""
        numbers = [2, 4, 6]
        result = take(numbers).divided_by(2).value()
        assert result == [1.0, 2.0, 3.0]

    def test_plus(self):
        """Test the prose-like plus method."""
        numbers = [1, 2, 3]
        result = take(numbers).plus(5).value()
        assert result == [6, 7, 8]

    def test_minus(self):
        """Test the prose-like minus method."""
        numbers = [5, 6, 7]
        result = take(numbers).minus(2).value()
        assert result == [3, 4, 5]


class TestAggregationOperations:
    """Test aggregation operations."""

    def test_sum(self):
        """Test sum aggregation."""
        numbers = [1, 2, 3, 4, 5]
        result = take(numbers).sum().value()
        assert result == 15

    def test_count(self):
        """Test count aggregation."""
        numbers = [1, 2, 3, 4, 5]
        result = take(numbers).count().value()
        assert result == 5

    def test_length_alias(self):
        """Test that length() is an alias for count()."""
        numbers = [1, 2, 3, 4, 5]
        count_result = take(numbers).count().value()
        length_result = take(numbers).length().value()
        assert count_result == length_result

    def test_max(self):
        """Test max aggregation."""
        numbers = [3, 1, 4, 1, 5, 9]
        result = take(numbers).max().value()
        assert result == 9

    def test_min(self):
        """Test min aggregation."""
        numbers = [3, 1, 4, 1, 5, 9]
        result = take(numbers).min().value()
        assert result == 1

    def test_first(self):
        """Test first element extraction."""
        numbers = [1, 2, 3, 4, 5]
        result = take(numbers).first().value()
        assert result == 1

    def test_last(self):
        """Test last element extraction."""
        numbers = [1, 2, 3, 4, 5]
        result = take(numbers).last().value()
        assert result == 5

    def test_first_empty_list(self):
        """Test first() with empty list raises IndexError."""
        with pytest.raises(IndexError):
            take([]).first().value()

    def test_last_empty_list(self):
        """Test last() with empty list raises IndexError."""
        with pytest.raises(IndexError):
            take([]).last().value()


class TestCollectionOperations:
    """Test collection manipulation operations."""

    def test_take_elements(self):
        """Test taking first n elements."""
        numbers = [1, 2, 3, 4, 5]
        result = take(numbers).take_elements(3).value()
        assert result == [1, 2, 3]

        # Test with fewer elements than requested
        result = take([1, 2]).take_elements(5).value()
        assert result == [1, 2]

        # Test with empty list
        result = take([]).take_elements(3).value()
        assert result == []

    def test_skip_elements(self):
        """Test skipping first n elements."""
        numbers = [1, 2, 3, 4, 5]
        result = take(numbers).skip(2).value()
        assert result == [3, 4, 5]

    def test_to_list(self):
        """Test converting to list."""
        numbers = [1, 2, 3]
        result = take(numbers).to_list()
        assert result == [1, 2, 3]
        assert isinstance(result, list)

    def test_to_list_single_value(self):
        """Test converting single value to list."""
        result = take(42).to_list()
        assert result == [42]


class TestReductionOperations:
    """Test reduction operations."""

    def test_reduce_with_initial(self):
        """Test reduce with initial value."""
        numbers = [1, 2, 3, 4]
        result = take(numbers).reduce(lambda acc, x: acc + x, 0).value()
        assert result == 10

    def test_reduce_without_initial(self):
        """Test reduce without initial value."""
        numbers = [1, 2, 3, 4]
        result = take(numbers).reduce(lambda acc, x: acc + x).value()
        assert result == 10

    def test_fold_alias(self):
        """Test that fold() works like reduce with initial."""
        numbers = [1, 2, 3, 4]
        reduce_result = take(numbers).reduce(lambda acc, x: acc + x, 0).value()
        fold_result = take(numbers).fold(lambda acc, x: acc + x, 0).value()
        assert reduce_result == fold_result


class TestChainedOperations:
    """Test complex chained operations."""

    def test_filter_and_transform(self):
        """Test chaining filter and transform operations."""
        numbers = [1, 2, 3, 4, 5, 6]
        result = (
            take(numbers).where(lambda x: x % 2 == 0).transform(lambda x: x**2).value()
        )
        assert result == [4, 16, 36]

    def test_complex_chain(self):
        """Test a complex chain of operations."""
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = (
            take(numbers)
            .where(lambda x: x % 2 == 0)
            .transform(lambda x: x**2)
            .that_are_greater_than(10)
            .sum()
            .value()
        )
        assert result == 216  # 16 + 36 + 64 + 100

    def test_prose_like_chain(self):
        """Test a prose-like chain of operations."""
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = (
            take(numbers)
            .that_are_greater_than(5)
            .multiplied_by(2)
            .minus(1)
            .sum()
            .value()
        )
        # (6,7,8,9,10) -> (12,14,16,18,20) -> (11,13,15,17,19) -> 75
        assert result == 75


class TestErrorHandling:
    """Test error handling for invalid operations."""

    def test_filter_non_iterable(self):
        """Test filtering non-iterable raises TypeError."""
        with pytest.raises(TypeError):
            take(42).where(lambda x: x > 0).value()

    def test_transform_non_iterable(self):
        """Test transforming non-iterable raises TypeError."""
        with pytest.raises(TypeError):
            take(42).transform(lambda x: x * 2).value()

    def test_sum_non_iterable(self):
        """Test sum of non-iterable raises TypeError."""
        with pytest.raises(TypeError):
            take(42).sum().value()

    def test_take_non_iterable(self):
        """Test take from non-iterable raises TypeError."""
        with pytest.raises(TypeError):
            take(42).take_elements(2).value()

    def test_skip_non_iterable(self):
        """Test skip from non-iterable raises TypeError."""
        with pytest.raises(TypeError):
            take(42).skip(2).value()


class TestStringRepresentation:
    """Test string representation of Chain objects."""

    def test_repr(self):
        """Test Chain string representation."""
        data = [1, 2, 3]
        c = Chain(data)
        assert repr(c) == "Chain([1, 2, 3])"

"""
Tests for additional operations and utilities.
"""

from fluent_chaining import take
from fluent_chaining.operations import compose, curry, partial, pipe


class TestAdditionalChainMethods:
    """Test additional methods added to Chain class."""

    def test_distinct(self):
        """Test removing duplicates while preserving order."""
        numbers = [1, 2, 2, 3, 3, 3, 4]
        result = take(numbers).distinct().value()
        assert result == [1, 2, 3, 4]

    def test_unique_alias(self):
        """Test that unique() is an alias for distinct()."""
        numbers = [1, 2, 2, 3, 3, 3, 4]
        distinct_result = take(numbers).distinct().value()
        unique_result = take(numbers).unique().value()
        assert distinct_result == unique_result

    def test_reverse(self):
        """Test reversing element order."""
        numbers = [1, 2, 3, 4, 5]
        result = take(numbers).reverse().value()
        assert result == [5, 4, 3, 2, 1]

    def test_sort_default(self):
        """Test sorting with default parameters."""
        numbers = [3, 1, 4, 1, 5, 9]
        result = take(numbers).sort().value()
        assert result == [1, 1, 3, 4, 5, 9]

    def test_sort_reverse(self):
        """Test sorting in reverse order."""
        numbers = [3, 1, 4, 1, 5, 9]
        result = take(numbers).sort(reverse=True).value()
        assert result == [9, 5, 4, 3, 1, 1]

    def test_sort_with_key(self):
        """Test sorting with a key function."""
        words = ["apple", "pie", "a", "longer"]
        result = take(words).sort(key=len).value()
        assert result == ["a", "pie", "apple", "longer"]

    def test_flatten(self):
        """Test flattening nested iterables."""
        nested = [[1, 2], [3, 4], [5, 6]]
        result = take(nested).flatten().value()
        assert result == [1, 2, 3, 4, 5, 6]

    def test_flatten_mixed(self):
        """Test flattening with mixed nested/non-nested items."""
        mixed = [1, [2, 3], 4, [5, 6]]
        result = take(mixed).flatten().value()
        assert result == [1, 2, 3, 4, 5, 6]

    def test_group_by(self):
        """Test grouping elements by key function."""
        numbers = [1, 2, 2, 3, 3, 3]
        result = take(numbers).group_by(lambda x: x).value()
        expected = {1: [1], 2: [2, 2], 3: [3, 3, 3]}
        assert result == expected

    def test_group_by_custom_key(self):
        """Test grouping with custom key function."""
        words = ["apple", "banana", "cherry", "apricot"]
        result = take(words).group_by(lambda word: word[0]).value()
        expected = {"a": ["apple", "apricot"], "b": ["banana"], "c": ["cherry"]}
        assert result == expected


class TestComposeFunction:
    """Test function composition utility."""

    def test_compose_two_functions(self):
        """Test composing two functions."""

        def add_one(x):
            return x + 1

        def multiply_by_two(x):
            return x * 2

        composed = compose(multiply_by_two, add_one)

        result = composed(3)
        assert result == 8  # (3 + 1) * 2

    def test_compose_three_functions(self):
        """Test composing three functions."""

        def add_one(x):
            return x + 1

        def multiply_by_two(x):
            return x * 2

        def subtract_three(x):
            return x - 3

        composed = compose(subtract_three, multiply_by_two, add_one)

        result = composed(5)
        assert result == 9  # ((5 + 1) * 2) - 3 = 12 - 3 = 9

    def test_compose_with_chain(self):
        """Test using composed functions with Chain."""

        def add_one(x):
            return x + 1

        def multiply_by_two(x):
            return x * 2

        composed = compose(multiply_by_two, add_one)

        numbers = [1, 2, 3]
        result = take(numbers).transform(composed).value()
        assert result == [4, 6, 8]  # [(1+1)*2, (2+1)*2, (3+1)*2]


class TestPipeFunction:
    """Test function piping utility."""

    def test_pipe_two_functions(self):
        """Test piping two functions."""

        def add_one(x):
            return x + 1

        def multiply_by_two(x):
            return x * 2

        piped = pipe(add_one, multiply_by_two)

        result = piped(3)
        assert result == 8  # (3 + 1) * 2

    def test_pipe_three_functions(self):
        """Test piping three functions."""

        def add_one(x):
            return x + 1

        def multiply_by_two(x):
            return x * 2

        def subtract_three(x):
            return x - 3

        piped = pipe(add_one, multiply_by_two, subtract_three)

        result = piped(5)
        assert result == 9  # ((5 + 1) * 2) - 3 = 12 - 3 = 9

    def test_pipe_vs_compose(self):
        """Test that pipe and compose give same results."""

        def add_one(x):
            return x + 1

        def multiply_by_two(x):
            return x * 2

        piped = pipe(add_one, multiply_by_two)
        composed = compose(multiply_by_two, add_one)

        for x in range(10):
            assert piped(x) == composed(x)


class TestCurryFunction:
    """Test currying utility."""

    def test_curry_two_args(self):
        """Test currying function with two arguments."""

        @curry
        def add(x, y):
            return x + y

        add_five = add(5)
        result = add_five(3)
        assert result == 8

    def test_curry_three_args(self):
        """Test currying function with three arguments."""

        @curry
        def add_three(x, y, z):
            return x + y + z

        # Partial application
        add_five = add_three(2)(3)
        result = add_five(1)
        assert result == 6

        # Full application
        result = add_three(1)(2)(3)
        assert result == 6

    def test_curry_immediate_call(self):
        """Test curried function with immediate full application."""

        @curry
        def multiply(x, y):
            return x * y

        result = multiply(4, 5)
        assert result == 20


class TestPartialFunction:
    """Test partial application utility."""

    def test_partial_basic(self):
        """Test basic partial application."""

        def add_three(x, y, z):
            return x + y + z

        add_to_ten = partial(add_three, 5, 5)
        result = add_to_ten(2)
        assert result == 12

    def test_partial_with_kwargs(self):
        """Test partial application with keyword arguments."""

        def greet(greeting, name, punctuation="!"):
            return f"{greeting}, {name}{punctuation}"

        say_hello = partial(greet, "Hello", punctuation=".")
        result = say_hello("World")
        assert result == "Hello, World."

    def test_partial_mixed_args(self):
        """Test partial application with mixed args and kwargs."""

        def format_number(number, prefix="", suffix="", decimals=2):
            return f"{prefix}{number:.{decimals}f}{suffix}"

        format_currency = partial(format_number, prefix="$", decimals=2)
        result = format_currency(123.456)
        assert result == "$123.46"


class TestComplexChains:
    """Test complex chains using additional operations."""

    def test_complex_data_processing(self):
        """Test complex data processing pipeline."""
        data = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]

        result = (
            take(data)
            .distinct()
            .transform(lambda x: x**2)
            .sort(reverse=True)
            .take_elements(3)
            .sum()
            .value()
        )

        # distinct: [1, 2, 3, 4]
        # squared: [1, 4, 9, 16]
        # sorted desc: [16, 9, 4, 1]
        # take 3: [16, 9, 4]
        # sum: 29
        assert result == 29

    def test_text_processing_chain(self):
        """Test text processing with chained operations."""
        words = ["hello", "world", "hello", "python", "world"]

        result = take(words).distinct().sort(key=len).transform(str.upper).value()

        # distinct: ["hello", "world", "python"]
        # sort by length: ["hello", "world", "python"]
        # to upper: ["HELLO", "WORLD", "PYTHON"]
        assert result == ["HELLO", "WORLD", "PYTHON"]

    def test_nested_flattening_chain(self):
        """Test nested data flattening and processing."""
        nested_data = [[1, 2], [3, 4], [5, 6, 7]]

        result = (
            take(nested_data)
            .flatten()
            .where(lambda x: x % 2 == 1)
            .multiplied_by(2)
            .sum()
            .value()
        )

        # flatten: [1, 2, 3, 4, 5, 6, 7]
        # odd numbers: [1, 3, 5, 7]
        # multiply by 2: [2, 6, 10, 14]
        # sum: 32
        assert result == 32

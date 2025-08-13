"""
Tests for README examples to ensure they work as documented.
"""

from fluent_chaining import take


class TestReadmeExamples:
    """Test examples from the README to ensure documentation accuracy."""

    def test_basic_example(self):
        """Test the basic example from README."""
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = (
            take(numbers)
            .where(lambda x: x % 2 == 0)
            .transform(lambda x: x**2)
            .sum()
            .value()
        )

        # Even numbers: [2, 4, 6, 8, 10]
        # Squared: [4, 16, 36, 64, 100]
        # Sum: 220
        assert result == 220

    def test_natural_language_filtering(self):
        """Test natural language filtering examples."""
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        # Even numbers
        even_result = take(numbers).where(lambda x: x % 2 == 0).value()
        assert even_result == [2, 4, 6, 8, 10]

        # Large numbers
        large_result = take(numbers).that_are_greater_than(5).value()
        assert large_result == [6, 7, 8, 9, 10]

        # Chained conditions
        chained_result = (
            take(numbers).where(lambda x: x % 2 == 0).that_are_greater_than(4).value()
        )
        assert chained_result == [6, 8, 10]

    def test_mathematical_operations(self):
        """Test mathematical operations example."""
        numbers = [1, 2, 3, 4, 5]

        # Transform and add
        result1 = take(numbers).transform(lambda x: x * 2).plus(1).value()
        assert result1 == [3, 5, 7, 9, 11]

        # Multiple transformations
        result2 = take(numbers).multiplied_by(3).minus(1).divided_by(2).value()
        assert result2 == [1.0, 2.5, 4.0, 5.5, 7.0]

    def test_aggregations_example(self):
        """Test aggregation examples."""
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        # Simple aggregations
        total = take(numbers).sum().value()
        assert total == 55

        count = take(numbers).count().value()
        assert count == 10

        maximum = take(numbers).max().value()
        assert maximum == 10

        minimum = take(numbers).min().value()
        assert minimum == 1

    def test_data_processing_pipeline(self):
        """Test data processing pipeline example."""
        users = [
            {"name": "Alice", "age": 25, "city": "New York", "salary": 50000},
            {"name": "Bob", "age": 30, "city": "San Francisco", "salary": 75000},
            {"name": "Charlie", "age": 35, "city": "New York", "salary": 60000},
            {"name": "Diana", "age": 28, "city": "Boston", "salary": 55000},
        ]

        # Find users over 25 in New York
        ny_users_over_25 = (
            take(users)
            .where(lambda user: user["age"] > 25)
            .where(lambda user: user["city"] == "New York")
            .value()
        )

        assert len(ny_users_over_25) == 1
        assert ny_users_over_25[0]["name"] == "Charlie"

        # Get their salaries
        salaries = (
            take(users)
            .where(lambda user: user["age"] > 25)
            .where(lambda user: user["city"] == "New York")
            .transform(lambda user: user["salary"])
            .value()
        )

        assert salaries == [60000]

    def test_text_processing_example(self):
        """Test text processing example."""
        text = ["hello", "world", "this", "is", "a", "test"]

        result = (
            take(text)
            .where(lambda word: len(word) > 3)
            .transform(str.upper)
            .transform(lambda word: f"[{word}]")
            .value()
        )

        assert result == ["[HELLO]", "[WORLD]", "[THIS]", "[TEST]"]

    def test_factorial_example(self):
        """Test factorial calculation example."""

        def factorial(n):
            return take(range(1, n + 1)).reduce(lambda acc, x: acc * x, 1).value()

        assert factorial(5) == 120
        assert factorial(0) == 1  # 0! = 1
        assert factorial(1) == 1  # 1! = 1

    def test_nested_data_example(self):
        """Test nested data processing example."""
        nested_data = [[1, 2], [3, 4], [5, 6]]

        # Flatten and process
        result = take(nested_data).flatten().where(lambda x: x % 2 == 0).value()

        assert result == [2, 4, 6]

    def test_remove_duplicates_example(self):
        """Test removing duplicates example."""
        data_with_dupes = [1, 2, 2, 3, 3, 3, 4]
        unique_values = take(data_with_dupes).distinct().value()

        assert unique_values == [1, 2, 3, 4]

    def test_sorting_example(self):
        """Test sorting examples."""
        people = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
            {"name": "Charlie", "age": 20},
        ]

        # Sort by age
        sorted_people = take(people).sort(key=lambda person: person["age"]).value()

        ages = [person["age"] for person in sorted_people]
        assert ages == [20, 25, 30]

        # Reverse order
        reversed_ages = (
            take(people)
            .transform(lambda person: person["age"])
            .sort(reverse=True)
            .value()
        )

        assert reversed_ages == [30, 25, 20]

    def test_grouping_example(self):
        """Test grouping operations example."""
        students = [
            {"name": "Alice", "grade": "A"},
            {"name": "Bob", "grade": "B"},
            {"name": "Charlie", "grade": "A"},
            {"name": "Diana", "grade": "B"},
        ]

        # Group students by grade
        groups = take(students).group_by(lambda student: student["grade"]).value()

        assert "A" in groups
        assert "B" in groups
        assert len(groups["A"]) == 2
        assert len(groups["B"]) == 2

    def test_complex_prose_chain(self):
        """Test complex prose-like chain from README."""
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = (
            take(numbers)
            .that_are_greater_than(5)
            .multiplied_by(2)
            .minus(1)
            .sum()
            .value()
        )

        # Numbers > 5: [6, 7, 8, 9, 10]
        # Multiplied by 2: [12, 14, 16, 18, 20]
        # Minus 1: [11, 13, 15, 17, 19]
        # Sum: 75
        assert result == 75


class TestPerformanceExamples:
    """Test performance and edge cases."""

    def test_large_dataset(self):
        """Test with a larger dataset."""
        large_numbers = list(range(1000))

        result = (
            take(large_numbers)
            .where(lambda x: x % 2 == 0)
            .transform(lambda x: x // 2)
            .that_are_greater_than(100)
            .count()
            .value()
        )

        # Even numbers: 0, 2, 4, ..., 998 (500 numbers)
        # Divided by 2: 0, 1, 2, ..., 499
        # Greater than 100: 101, 102, ..., 499 (399 numbers)
        assert result == 399

    def test_empty_collections(self):
        """Test behavior with empty collections."""
        empty_result = take([]).count().value()
        assert empty_result == 0

        # Chain operations on empty collection
        result = (
            take([]).where(lambda x: x > 0).transform(lambda x: x * 2).count().value()
        )
        assert result == 0

    def test_single_element(self):
        """Test behavior with single element."""
        result = (
            take([42]).where(lambda x: x > 40).transform(lambda x: x * 2).sum().value()
        )
        assert result == 84

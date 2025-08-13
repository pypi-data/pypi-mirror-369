# Fluent Chaining

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> Pure functional programming with fluent chaining that reads like prose.

Fluent Chaining is a Python package that enables functional programming with method chaining that reads like natural language, making your code more expressive, readable, and maintainable.

## ✨ Why Fluent Chaining?

Traditional functional programming in Python can be verbose and hard to read:

```python
# Traditional approach - hard to read
from functools import reduce

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
result = reduce(
    lambda acc, x: acc + x,
    map(lambda x: x ** 2,
        filter(lambda x: x % 2 == 0, numbers)),
    0
)
```

With Fluent Chaining, the same operation reads like prose:

```python
# Fluent Chaining - reads like natural language
from fluent_chaining import take

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
result = (take(numbers)
    .where(lambda x: x % 2 == 0)
    .transform(lambda x: x ** 2)
    .sum()
    .value())
```

## 🚀 Installation (Project-Saturday Members Only)

### Quick Setup (Recommended)
```bash
# 1. Set up your credentials (one-time)
cp docs/setup/team-secrets.template team-secrets.env
# Edit team-secrets.env with your GitHub PAT token

# 2. Run automated setup
python scripts/setup-team-environment.py

# 3. Install the package
pip install fluent-chaining
```

### Alternative Installation Methods

**GitHub Packages (manual setup):**
```bash
# Configure pip for GitHub Packages
pip config set global.extra-index-url https://pypi.pkg.github.com/Project-Saturday/simple/
pip config set global.trusted-host pypi.pkg.github.com

# Install with your .pypirc configured
pip install fluent-chaining
```

**Direct Git Installation:**
```bash
# Install latest from git
pip install git+https://github.com/Project-Saturday/fluent-chaining.git

# Install specific version
pip install git+https://github.com/Project-Saturday/fluent-chaining.git@v0.1.0
```

> **Note:** This is a private Project-Saturday library. You'll need a GitHub Personal Access Token with `packages:read` permission. See [`docs/setup/setup-github-packages.md`](docs/setup/setup-github-packages.md) for detailed setup instructions.

## 📖 Basic Usage

### Getting Started

```python
from fluent_chaining import take

# Start with data using take()
data = [1, 2, 3, 4, 5]
result = take(data).transform(lambda x: x * 2).value()
# Result: [2, 4, 6, 8, 10]
```

### Core Operations

#### Filtering with Natural Language

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Using prose-like methods
even_numbers = (take(numbers)
    .where(lambda x: x % 2 == 0)
    .value())

# Even more natural
large_numbers = (take(numbers)
    .that_are_greater_than(5)
    .value())

# Chaining conditions
result = (take(numbers)
    .where(lambda x: x % 2 == 0)
    .that_are_greater_than(4)
    .value())
# Result: [6, 8, 10]
```

#### Transformations

```python
numbers = [1, 2, 3, 4, 5]

# Mathematical operations with readable syntax
result = (take(numbers)
    .transform(lambda x: x * 2)
    .plus(1)
    .value())
# Result: [3, 5, 7, 9, 11]

# Multiple transformations
result = (take(numbers)
    .multiplied_by(3)
    .minus(1)
    .divided_by(2)
    .value())
# Result: [1.0, 2.5, 4.0, 5.5, 7.0]
```

#### Aggregations

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Simple aggregations
total = take(numbers).sum().value()
count = take(numbers).count().value()
maximum = take(numbers).max().value()
minimum = take(numbers).min().value()

# Complex chained operations
average_of_squares = (take(numbers)
    .where(lambda x: x % 2 == 0)
    .transform(lambda x: x ** 2)
    .sum()
    .divided_by(take(numbers).where(lambda x: x % 2 == 0).count().value())
    .value())
```

## 🎯 Real-World Examples

### Data Processing Pipeline

```python
from fluent_chaining import take

# Process a list of user records
users = [
    {"name": "Alice", "age": 25, "city": "New York", "salary": 50000},
    {"name": "Bob", "age": 30, "city": "San Francisco", "salary": 75000},
    {"name": "Charlie", "age": 35, "city": "New York", "salary": 60000},
    {"name": "Diana", "age": 28, "city": "Boston", "salary": 55000},
]

# Find the average salary of users over 25 in New York
average_salary = (take(users)
    .where(lambda user: user["age"] > 25)
    .where(lambda user: user["city"] == "New York")
    .transform(lambda user: user["salary"])
    .sum()
    .divided_by(
        take(users)
        .where(lambda user: user["age"] > 25)
        .where(lambda user: user["city"] == "New York")
        .count()
        .value()
    )
    .value())
```

### Text Processing

```python
text = ["hello", "world", "this", "is", "a", "test"]

# Process text with readable operations
result = (take(text)
    .where(lambda word: len(word) > 3)
    .transform(str.upper)
    .transform(lambda word: f"[{word}]")
    .value())
# Result: ['[HELLO]', '[WORLD]', '[THIS]', '[TEST]']
```

### Mathematical Computations

```python
# Calculate factorial using fluent chaining
def factorial(n):
    return (take(range(1, n + 1))
        .reduce(lambda acc, x: acc * x, 1)
        .value())

# Find prime numbers with descriptive operations
def is_prime(n):
    if n < 2:
        return False
    return (take(range(2, int(n ** 0.5) + 1))
        .where(lambda x: n % x == 0)
        .count()
        .value()) == 0

primes = (take(range(2, 20))
    .where(is_prime)
    .value())
```

## 🔧 Advanced Features

### Working with Collections

```python
nested_data = [[1, 2], [3, 4], [5, 6]]

# Flatten and process
result = (take(nested_data)
    .flatten()
    .where(lambda x: x % 2 == 0)
    .value())
# Result: [2, 4, 6]

# Remove duplicates
data_with_dupes = [1, 2, 2, 3, 3, 3, 4]
unique_values = (take(data_with_dupes)
    .distinct()
    .value())
# Result: [1, 2, 3, 4]
```

### Sorting and Ordering

```python
people = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 30},
    {"name": "Charlie", "age": 20},
]

# Sort by age
sorted_people = (take(people)
    .sort(key=lambda person: person["age"])
    .value())

# Reverse order
reversed_ages = (take(people)
    .transform(lambda person: person["age"])
    .sort(reverse=True)
    .value())
```

### Grouping Operations

```python
students = [
    {"name": "Alice", "grade": "A"},
    {"name": "Bob", "grade": "B"},
    {"name": "Charlie", "grade": "A"},
    {"name": "Diana", "grade": "B"},
]

# Group students by grade
groups = (take(students)
    .group_by(lambda student: student["grade"])
    .value())
```

## 🛠️ Method Reference

### Entry Points
- `take(data)` - Start a fluent chain with data
- `chain(data)` - Alias for `take()`

### Filtering Methods
- `.where(predicate)` - Filter elements that satisfy the predicate
- `.filter(predicate)` - Alias for `where()`
- `.that_are(predicate)` - Natural language filtering
- `.that_are_greater_than(value)` - Filter elements > value
- `.that_are_less_than(value)` - Filter elements < value
- `.that_equal(value)` - Filter elements == value

### Transformation Methods
- `.transform(func)` - Transform each element
- `.map(func)` - Alias for `transform()`
- `.multiplied_by(factor)` - Multiply by factor
- `.divided_by(divisor)` - Divide by divisor
- `.plus(addend)` - Add value
- `.minus(subtrahend)` - Subtract value

### Aggregation Methods
- `.sum()` - Sum all elements
- `.count()` - Count elements
- `.length()` - Alias for `count()`
- `.max()` - Maximum element
- `.min()` - Minimum element
- `.first()` - First element
- `.last()` - Last element

### Collection Methods
- `.take(n)` - Take first n elements
- `.skip(n)` - Skip first n elements
- `.distinct()` - Remove duplicates
- `.unique()` - Alias for `distinct()`
- `.reverse()` - Reverse order
- `.sort(key=None, reverse=False)` - Sort elements
- `.flatten()` - Flatten nested collections
- `.group_by(key_func)` - Group by key function

### Reduction Methods
- `.reduce(func, initial=None)` - Reduce to single value
- `.fold(func, initial)` - Fold with initial value

### Output Methods
- `.value()` - Get the final result
- `.to_list()` - Convert to list

## 🧪 Advanced Functional Programming

The package includes comprehensive utilities for advanced functional programming:

### Function Composition and Utilities

```python
from fluent_chaining import compose, pipe, curry, partial, memoize

# Function composition
add_one = lambda x: x + 1
multiply_by_two = lambda x: x * 2
composed = compose(multiply_by_two, add_one)

result = take([1, 2, 3]).transform(composed).value()
# Result: [4, 6, 8]

# Function piping (left to right)
piped = pipe(add_one, multiply_by_two)
result = take([1, 2, 3]).transform(piped).value()
# Result: [4, 6, 8]

# Currying
@curry
def add_three_numbers(x, y, z):
    return x + y + z

add_five = add_three_numbers(2)(3)
result = take([1, 2, 3]).transform(add_five).value()
# Result: [6, 7, 8]

# Memoization for expensive computations
@memoize
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

fib_sequence = take(range(10)).transform(fibonacci).value()
# Result: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### Advanced Chain Methods

```python
# Debugging and side effects
result = (take([1, 2, 3, 4, 5])
    .where(lambda x: x % 2 == 0)
    .debug("Even numbers")  # Prints: Debug: [2, 4]
    .transform(lambda x: x ** 2)
    .side_effect(lambda data: print(f"Squared: {data}"))
    .sum()
    .value())

# Conditional processing
def double_if_small(chain):
    return chain.transform(lambda x: x * 2)

result = (take([1, 2, 3])
    .apply_if(True, double_if_small)  # Apply transformation conditionally
    .apply_when(lambda data: sum(data) > 10, lambda c: c.plus(5))  # Apply when condition met
    .value())

# Branching logic
result = (take([1, 2, 3, 4, 5])
    .branch(
        len([1, 2, 3, 4, 5]) > 3,
        lambda c: c.take(3),  # If true: take first 3
        lambda c: c.reverse()  # If false: reverse
    )
    .sum()
    .value())

# Error handling and defaults
result = (take([])
    .or_else([1, 2, 3])  # Use default if empty
    .assert_that(lambda data: len(data) > 0, "Must not be empty")
    .sum()
    .value())
```

### Quantification and Higher-Order Functions

```python
from fluent_chaining import always, exists, identity, constant

# Universal and existential quantification
is_positive = lambda x: x > 0
all_positive = always(is_positive)
any_positive = exists(is_positive)

result1 = all_positive([1, 2, 3])  # True
result2 = any_positive([-1, 0, 1])  # True

# Utility functions
numbers = [1, 2, 3, 4, 5]
result = (take(numbers)
    .transform(identity)  # No-op transformation
    .where(constant(True))  # Always true predicate
    .value())
```

## 🚀 Monadic Types (.NET-Style Functional Programming)

Inspired by .NET's functional programming patterns, we provide `Result<T>` and `Option<T>` types for robust error and null handling.

### Result<T> - Functional Error Handling

No more exception handling - make errors explicit and composable:

```python
from fluent_chaining import Result, Ok, Err, safe, try_parse_int

# Safe operations that return Result<T>
def safe_divide(x, y):
    if y == 0:
        return Err("Division by zero")
    return Ok(x / y)

# Chain operations with .then() - like .NET's Result.Then()
result = (safe_divide(10, 2)
    .then(lambda x: safe_divide(x, 2))
    .then(lambda x: Ok(x + 1))
    .match(
        ok_func=lambda value: f"Success: {value}",
        err_func=lambda error: f"Error: {error}"
    ))
# Result: "Success: 3.5"

# Convert exception-throwing functions with @safe decorator
@safe
def risky_operation(value):
    if value < 0:
        raise ValueError("Negative value not allowed")
    return value * 2

results = [risky_operation(x) for x in [1, -2, 3]]
successful_values = [r.unwrap() for r in results if r.is_ok()]
# successful_values: [2, 6]

# Parse and process data safely
input_data = ["10", "20", "invalid", "30"]
parsed_results = [try_parse_int(s) for s in input_data]

total = (take([r.unwrap() for r in parsed_results if r.is_ok()])
    .sum()
    .value())
# total: 60 (10 + 20 + 30, "invalid" safely ignored)
```

### Option<T> - Functional Null Handling

Handle null/missing values functionally with pattern matching:

```python
from fluent_chaining import Some, Nothing, from_nullable, from_dict

# Create Options
user_name = Some("Alice")
missing_data = Nothing()

# Pattern matching - like .NET's Option.Match()
def process_user(name_option):
    return name_option.match(
        some_func=lambda name: f"Processing user: {name}",
        none_func=lambda: "No user to process"
    )

print(process_user(user_name))    # "Processing user: Alice"
print(process_user(missing_data)) # "No user to process"

# Safe data access
user_data = {"name": "Bob", "profile": {"age": 30}}

age_message = (from_dict(user_data, "profile")
    .then(lambda profile: from_dict(profile, "age"))
    .match(
        some_func=lambda age: f"User is {age} years old",
        none_func=lambda: "Age not available"
    ))
# Result: "User is 30 years old"

# Chain multiple optional operations
def get_user_email_domain(user):
    return (from_dict(user, "email")
        .map(lambda email: email.split("@"))
        .filter(lambda parts: len(parts) == 2)
        .map(lambda parts: parts[1])
        .unwrap_or("unknown"))

users = [
    {"email": "alice@example.com"},
    {"email": "invalid-email"},
    {"name": "Bob"}  # No email
]

domains = [get_user_email_domain(user) for user in users]
# domains: ["example.com", "unknown", "unknown"]
```

### Integration with Fluent Chains

Convert between chains and monadic types seamlessly:

```python
# Chain to Result/Option
numbers = [1, 2, 3, 4, 5]
result = (take(numbers)
    .where(lambda x: x > 10)
    .to_result("No large numbers found"))

result.match(
    ok_func=lambda values: f"Found: {values}",
    err_func=lambda error: f"Error: {error}"
)
# Result: "Error: No large numbers found"

# Option to Chain
optional_data = Some([1, 2, 3])
total = (from_option(optional_data, [])
    .sum()
    .value())
# total: 6

# Complex pipeline with error handling
def safe_process_scores(scores_text):
    return (try_parse_int(scores_text)
        .filter(lambda score: 0 <= score <= 100, "Score out of range")
        .map(lambda score: score * 1.1)  # Apply 10% bonus
        .map(lambda score: min(score, 100)))  # Cap at 100

test_scores = ["85", "95", "invalid", "105", "-5"]
processed = [safe_process_scores(s) for s in test_scores]

# Extract successful scores
final_scores = [r.unwrap() for r in processed if r.is_ok()]
average = take(final_scores).sum().value() / len(final_scores) if final_scores else 0
# average: ~96.5 (from 85*1.1=93.5 and 95*1.1=100 capped)
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Project Saturday

This package is part of the [Project Saturday](https://github.com/Project-Saturday) organization, dedicated to creating tools that make programming more expressive and enjoyable.

---

*Made with ❤️ by the Project Saturday team*

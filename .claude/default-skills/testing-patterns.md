# Testing Patterns

When creating or updating tests, follow these patterns for Python projects
using pytest.

## TDD Workflow

1. **Red** — Write a failing test that describes the desired behavior.
2. **Green** — Write the minimum code to make the test pass.
3. **Refactor** — Clean up the code while keeping tests green.

Always run `pytest` after each step to verify the cycle.

## Test Structure

Use `describe`-style grouping with classes or nested functions:

```python
class TestUserRegistration:
    """Tests for user registration flow."""

    def test_creates_user_with_valid_email(self):
        ...

    def test_rejects_duplicate_email(self):
        ...

    def test_hashes_password_before_storing(self):
        ...
```

Follow the **Arrange-Act-Assert** (AAA) pattern in every test:

```python
def test_calculates_total_with_discount():
    # Arrange
    cart = make_cart(items=[make_item(price=100)], discount_pct=10)

    # Act
    total = cart.calculate_total()

    # Assert
    assert total == 90.0
```

## Factory Functions

Create reusable factory functions for test data instead of repeating
fixture setup. Name them `make_<entity>()` with optional keyword
overrides:

```python
def make_user(**overrides) -> User:
    defaults = {
        "name": "Test User",
        "email": "test@example.com",
        "is_active": True,
    }
    return User(**(defaults | overrides))
```

## Fixtures

Use `@pytest.fixture` for shared setup. Prefer function-scoped fixtures
(the default) unless the setup is expensive:

```python
@pytest.fixture
def db_session():
    session = create_test_session()
    yield session
    session.rollback()
    session.close()
```

Use `conftest.py` for fixtures shared across multiple test files.

## Mocking

Mock **external boundaries**, not internal code:

- **Mock**: HTTP APIs, databases, file systems, clocks, third-party
  services.
- **Do NOT mock**: Internal functions, classes, or methods under test.

```python
from unittest.mock import patch, MagicMock

@patch("myapp.services.requests.get")
def test_fetches_user_profile(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {"name": "Alice"},
    )

    profile = fetch_profile("alice")
    assert profile["name"] == "Alice"
    mock_get.assert_called_once()
```

## Parametrize

Use `@pytest.mark.parametrize` for testing multiple inputs:

```python
@pytest.mark.parametrize("input_val,expected", [
    ("hello", "HELLO"),
    ("", ""),
    ("123", "123"),
])
def test_uppercase(input_val, expected):
    assert to_upper(input_val) == expected
```

## Assertions

- **One logical assertion per test** — test one behavior, not everything.
- **Use descriptive assertion messages** when the failure is not obvious.
- **Prefer `assert x == y`** over `assertTrue(x == y)`.
- **Use `pytest.raises`** for expected exceptions:

```python
with pytest.raises(ValueError, match="must be positive"):
    create_order(quantity=-1)
```

## Test File Organization

- Place tests in a `tests/` directory mirroring `src/` structure.
- Name test files `test_<module>.py`.
- Name test functions `test_<behavior_description>`.
- One `conftest.py` per test directory for shared fixtures.

## What NOT to Test

- Third-party library internals (trust their tests).
- Simple property access or trivial getters.
- Python language features (e.g., dict lookup works).
- Private implementation details that may change.

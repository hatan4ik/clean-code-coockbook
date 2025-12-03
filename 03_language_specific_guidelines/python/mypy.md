# Using mypy for Robust, Type-Safe Python

`mypy` is a static type checker for Python. It allows you to add type hints to your code and then check them for correctness before you run the code. This can help you catch a wide variety of errors before they make it into production.

## 1. Problem: The Perils of Dynamic Typing

Python's dynamic typing is one of its greatest strengths. It allows for rapid prototyping and a flexible, expressive syntax. However, in large, complex codebases, dynamic typing can become a liability.

- **`None`-related errors:** The infamous `AttributeError: 'NoneType' object has no attribute '...` is a common bug that can be difficult to track down.
- **Incorrect types passed to functions:** Passing a `str` to a function that expects an `int` can lead to subtle bugs that are only discovered at runtime.
- **Refactoring nightmares:** Without type information, it can be difficult to refactor code with confidence. It's hard to know what the expected inputs and outputs of a function are, and what the impact of a change will be.
- **Poor autocompletion and IDE support:** IDEs and other development tools have a hard time providing accurate autocompletion and analysis for dynamically typed code.

## 2. Solution: Static Typing with `mypy`

`mypy` brings the benefits of static typing to Python, without sacrificing the language's flexibility. By adding type hints to your code, you can:

- **Catch errors early:** `mypy` will flag type errors before you even run your code, saving you from debugging runtime errors.
- **Improve code quality and readability:** Type hints serve as a form of documentation, making your code easier to read and understand.
- **Refactor with confidence:** With type information, you can refactor your code with confidence, knowing that `mypy` will catch any type-related errors you introduce.
- **Better IDE support:** IDEs can use type hints to provide better autocompletion, code navigation, and error highlighting.

## 3. Zero-to-Hero with `mypy`

### Step 1: Basic Type Hinting

You can start by adding basic type hints to your functions.

```python
def greet(name: str) -> str:
    return f"Hello, {name}"

# mypy will flag this as an error
greet(123)
```

### Step 2: Complex Types

The `typing` module provides a rich set of types for more complex scenarios.

- **`List`, `Tuple`, `Dict`, `Set`**: For generic containers.
- **`Optional[T]`**: For values that can be `None`. `Optional[str]` is equivalent to `Union[str, None]`.
- **`Union[T, U]`**: For values that can be one of several types.
- **`Any`**: A dynamic type that can be anything. Use it as a last resort.

```python
from typing import List, Optional

def find_user(users: List[dict], user_id: int) -> Optional[dict]:
    for user in users:
        if user["id"] == user_id:
            return user
    return None
```

### Step 3: Advanced Types (`TypeVar`, `Protocol`, `TypedDict`)

- **`TypeVar`**: For creating generic functions and classes.
- **`Protocol`**: For defining structural subtypes (duck typing).
- **`TypedDict`**: For providing type information for dictionaries with a fixed set of keys.

```python
from typing import TypedDict

class User(TypedDict):
    id: int
    name: str
    email: str

def get_user_name(user: User) -> str:
    return user["name"]
```

## 4. Real-World Example: Catching a Bug

Consider this code:

```python
def send_email(email: str, message: str):
    # ...
    pass

def notify_user(user):
    # What if user is None?
    send_email(user["email"], "Your order has shipped!")
```

Without `mypy`, this code will raise an `AttributeError` at runtime if `user` is `None`. With `mypy`, you can catch this bug before it ever happens.

```python
from typing import Optional

def notify_user(user: Optional[dict]):
    if user:
        send_email(user["email"], "Your order has shipped!")
```

By adding the `Optional[dict]` type hint and a `None` check, `mypy` can verify that the code is safe.

## 5. Configuration and CI/CD

You can configure `mypy` in your `pyproject.toml` or `mypy.ini` file. A strict configuration is recommended for most projects.

```ini
[mypy]
# Universal strictness
disallow_any_unimported = true
disallow_any_expr = false
disallow_any_decorated = false
disallow_any_explicit = true
disallow_any_generics = false
disallow_subclassing_any = true
disallow_untyped_calls = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_return_any = true
implicit_reexport = false
strict_equality = true

# Per-module overrides can go here
# e.g. mypy-requests.*

# We're not ready for this yet
#disallow_implicit_reexport = true
```

You should integrate `mypy` into your CI/CD pipeline to ensure that all new code is type-checked.

```yaml
# .github/workflows/ci.yml
- name: Run mypy
  run: mypy .
```

By embracing static typing with `mypy`, you can write more robust, maintainable, and error-free Python code.

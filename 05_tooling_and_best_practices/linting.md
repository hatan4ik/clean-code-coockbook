# Linting and Formatting

A consistent code style is crucial for readability and maintainability. Linters and formatters are tools that automatically enforce a consistent style, and they can also catch potential bugs before they make it into production.

## 1. Why Lint and Format?

-   **Consistency:** A consistent code style makes it easier for developers to read and understand code, regardless of who wrote it.
-   **Readability:** Linters and formatters can help you write code that is more readable and easier to follow.
-   **Early Bug Detection:** Linters can catch a wide variety of potential bugs, from simple syntax errors to more complex issues like unused variables and race conditions.
-   **Fewer Arguments:** By automating the process of formatting and linting, you can avoid time-wasting arguments about code style.

## 2. Python

### Ruff

`Ruff` is an extremely fast Python linter and formatter, written in Rust. It can replace dozens of other tools (`flake8`, `isort`, `pycodestyle`, etc.) with a single binary.

**Sample Configuration (`pyproject.toml`):**

```toml
[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "C",  # flake8-comprehensions
    "B",  # flake8-bugbear
]
ignore = ["E501"] # ignore line length errors (handled by the formatter)
```

### MyPy

`MyPy` is a static type checker for Python. It's an essential tool for writing robust, maintainable Python code. See the [MyPy documentation](./../python/mypy.md) for more details.

## 3. Go

### `gofmt` and `goimports`

`gofmt` is the official Go code formatter. It's not optional; it's a standard part of the Go toolchain. `goimports` is a tool that automatically adds and removes imports as needed, and also formats your code in the same style as `gofmt`.

Your editor should be configured to run `goimports` on save.

### `golangci-lint`

`golangci-lint` is a fast, comprehensive linter aggregator for Go. It runs dozens of linters in parallel and caches the results for speed.

**Sample Configuration (`.golangci.yml`):**

```yaml
run:
  timeout: 5m

linters:
  enable:
    - govet
    - errcheck
    - staticcheck
    - unused
    - goimports
    - revive
    - ineffassign
    - typecheck
    - unconvert
```

## 4. CI Integration

You should integrate your linters and formatters into your CI pipeline to ensure that all code is checked before it's merged.

### Ruff in GitHub Actions

```yaml
- name: Lint with Ruff
  run: |
    pip install ruff
    ruff check .
    ruff format --check .
```

### `golangci-lint` in GitHub Actions

```yaml
- name: Run golangci-lint
  uses: golangci/golangci-lint-action@v3
  with:
    version: v1.55
```

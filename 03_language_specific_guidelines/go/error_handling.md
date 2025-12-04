# Error Handling in Go

Go's approach to error handling is a core part of the language's design. It's built on a simple but powerful idea: **errors are values**. This is in stark contrast to exceptions, which are used in many other languages.

## 1. "Errors are values"

In Go, an error is any type that implements the built-in `error` interface:

```go
type error interface {
    Error() string
}
```

Because errors are just values, you handle them using the same control flow statements you use for any other value: `if`, `switch`, etc. This makes the error handling logic explicit and easy to follow.

## 2. Creating Errors

The two most common ways to create an error are with the `errors.New` and `fmt.Errorf` functions.

```go
import (
    "errors"
    "fmt"
)

// Create a simple error with a static message
err1 := errors.New("something went wrong")

// Create an error with a formatted message
err2 := fmt.Errorf("user with id %d not found", 123)
```

## 3. Error Wrapping

When an error is returned from a function, it's often useful to add context to it. This is called "wrapping" the error. You can wrap an error using the `%w` verb in `fmt.Errorf`.

```go
import (
    "fmt"
    "os"
)

func readFile() error {
    f, err := os.Open("my-file.txt")
    if err != nil {
        // Add context to the original error
        return fmt.Errorf("failed to open file: %w", err)
    }
    defer f.Close()
    // ...
    return nil
}
```

Wrapping errors creates a chain of errors, which can be inspected to get more information about what went wrong.

## 4. Inspecting Errors

The `errors` package provides two functions for inspecting errors: `errors.Is` and `errors.As`.

### `errors.Is`

Use `errors.Is` to check if an error in the chain is equal to a specific error value. This is useful for checking for sentinel errors like `sql.ErrNoRows` or `io.EOF`.

```go
import (
    "database/sql"
    "errors"
)

func getUser(id int) (*User, error) {
    // ... query database ...
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, fmt.Errorf("user not found")
        }
        return nil, fmt.Errorf("failed to get user: %w", err)
    }
    // ...
}
```

### `errors.As`

Use `errors.As` to check if an error in the chain is of a specific type. This is useful when you want to extract information from a custom error type.

```go
import "errors"

type MyError struct {
    msg  string
    code int
}

func (e *MyError) Error() string {
    return e.msg
}

func doSomething() error {
    return &MyError{msg: "something went wrong", code: 500}
}

func main() {
    err := doSomething()
    var myErr *MyError
    if errors.As(err, &myErr) {
        fmt.Println("Error code:", myErr.code)
    }
}
```

## 5. Custom Error Types

You can create your own custom error types to hold more information about what went wrong. This is useful for passing structured error information back to the caller.

```go
type NetworkError struct {
    URL    string
    Method string
    Err    error
}

func (e *NetworkError) Error() string {
    return fmt.Sprintf("failed to make %s request to %s: %v", e.Method, e.URL, e.Err)
}
```

## 6. Panic vs. Error

- **Errors** are for expected problems that can be handled by the caller (e.g., file not found, network connection failed).
- **Panics** are for unrecoverable errors, i.e., programmer mistakes (e.g., index out of bounds, nil pointer dereference).

In general, you should use errors for most problems and only use panics for truly exceptional situations. Don't use panics for normal error handling.

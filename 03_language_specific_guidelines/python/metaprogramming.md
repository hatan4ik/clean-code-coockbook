*   **Metaprogramming for Developer Experience (DX):** We will explore how to use decorators and metaclasses to reduce boilerplate and create more expressive APIs.
    *   **Use Case:** Creating a simple decorator to automatically add logging to a function or a metaclass to register plugins.
    *   **Example (Decorator for timing):**
        ```python
        import time
        from functools import wraps

        def timing_decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                result = func(*args, **kwargs)
                end = time.perf_counter()
                print(f"{func.__name__} took {end - start:.4f} seconds")
                return result
            return wrapper
        ```
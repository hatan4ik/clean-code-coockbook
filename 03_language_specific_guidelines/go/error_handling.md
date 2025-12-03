*   **Error Handling as a First-Class Citizen:** We will demonstrate robust error handling strategies.
    *   **Guideline:** Errors are values. They should be handled explicitly and gracefully.
    *   **Technique:** We will use `errors.As` and `errors.Is` for checking specific error types, and wrap errors to provide context.
        ```go
        if err != nil {
            return fmt.Errorf("failed to process user %s: %w", userID, err)
        }
        ```
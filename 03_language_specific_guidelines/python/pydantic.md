*   **Declarative Data with Pydantic:** We will move beyond basic dataclasses and embrace `Pydantic` for creating self-documenting, type-hinted, and validated data models.
    *   **Problem:** Standard Python dataclasses don't enforce type correctness at runtime, leading to subtle bugs.
    *   **Solution:** Use Pydantic models to get runtime data validation, serialization, and even JSON Schema generation for free.
    *   **Example:**
        ```python
        from pydantic import BaseModel, EmailStr, PositiveInt

        class UserProfile(BaseModel):
            username: str
            email: EmailStr
            age: PositiveInt
        ```
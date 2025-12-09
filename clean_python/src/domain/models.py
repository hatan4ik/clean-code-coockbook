import re
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class User(BaseModel):
    """
    Rich Domain Model.
    Contains both data AND business rules validation.
    """
    id: UUID = Field(default_factory=uuid4)
    username: str
    email: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username with comprehensive rules."""
        if len(v) < 3 or len(v) > 30:
            raise ValueError("Username must be 3-30 characters")
        if not re.match("^[a-zA-Z][a-zA-Z0-9_]*$", v):
            raise ValueError("Username must start with letter, contain only alphanumeric and underscore")
        if v.endswith("_"):
            raise ValueError("Username cannot end with underscore")
        return v.lower()  # Normalize to lowercase
    
    def can_receive_email(self) -> bool:
        """Pure business logic method."""
        return self.is_active

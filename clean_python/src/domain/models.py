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
        if not re.match("^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must be alphanumeric")
        return v
    
    def can_receive_email(self) -> bool:
        """Pure business logic method."""
        return self.is_active

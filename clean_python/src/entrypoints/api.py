import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, ValidationError
from src.service_layer import handlers
from src.service_layer.unit_of_work import AbstractUnitOfWork
from src.entrypoints.deps import get_uow
from src.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version
)

# DTOs
class RegisterRequest(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    is_active: bool

class ErrorResponse(BaseModel):
    error: str
    code: str
    details: Optional[dict] = None

@app.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    responses={
        409: {"model": ErrorResponse, "description": "User already exists"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def create_user_endpoint(
    data: RegisterRequest,
    uow: AbstractUnitOfWork = Depends(get_uow)
) -> UserResponse:
    """Register a new user."""
    try:
        user = await handlers.register_user_service(
            username=data.username,
            email=data.email,
            uow=uow
        )
        return UserResponse(
            user_id=str(user.id),
            username=user.username,
            email=user.email,
            is_active=user.is_active
        )
    except ValueError as e:
        logger.warning(f"User registration conflict: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "User already exists", "code": "USER_EXISTS"}
        )
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "Invalid input", "code": "VALIDATION_ERROR"}
        )
    except Exception as e:
        logger.error(f"Unexpected error in user registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "code": "INTERNAL_ERROR"}
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

import logging
from src.domain.models import User
from src.service_layer.unit_of_work import AbstractUnitOfWork

logger = logging.getLogger(__name__)


async def register_user_service(
    username: str, 
    email: str, 
    uow: AbstractUnitOfWork
) -> User:
    """
    High-Level Use Case: Register a new user.
    
    1. Check constraints (async)
    2. Create Model (sync)
    3. Persist (sync add, async commit)
    """
    async with uow:
        # 1. Check if user already exists
        existing = await uow.users.get_by_email(email)
        if existing:
            logger.info("Registration attempt for existing user", extra={"email_hash": hash(email)})
            raise ValueError("User already exists")  # Don't expose email in error
        
        # 2. Invoke Domain Logic
        user = User(username=username, email=email)
        
        # 3. Save and Commit (add is now synchronous)
        uow.users.add(user)
        await uow.commit()
        
        logger.info("User registered successfully", extra={"user_id": str(user.id)})
        return user

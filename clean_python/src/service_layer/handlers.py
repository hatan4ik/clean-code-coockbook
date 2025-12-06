from src.domain.models import User
from src.service_layer.unit_of_work import AbstractUnitOfWork

async def register_user_service(
    username: str, 
    email: str, 
    uow: AbstractUnitOfWork
) -> User:
    """
    High-Level Use Case.
    1. Check constraints (async)
    2. Create Model (sync)
    3. Persist (async)
    """
    async with uow:
        # 1. Check if user already exists
        existing = await uow.users.get_by_email(email)
        if existing:
            raise ValueError(f"User {email} already exists")
        
        # 2. Invoke Domain Logic
        user = User(username=username, email=email)
        
        # 3. Save and Commit
        await uow.users.add(user)
        await uow.commit()
        
        return user

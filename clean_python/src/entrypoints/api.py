from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from src.service_layer import handlers
from src.service_layer.unit_of_work import AbstractUnitOfWork
from src.entrypoints.deps import get_uow

app = FastAPI()

# Data Transfer Object (DTO)
class RegisterRequest(BaseModel):
    username: str
    email: str

@app.post("/users", status_code=201)
async def create_user_endpoint(
    data: RegisterRequest,
    uow: AbstractUnitOfWork = Depends(get_uow)
):
    try:
        user = await handlers.register_user_service(
            username=data.username,
            email=data.email,
            uow=uow
        )
        return {"user_id": user.id, "status": "active"}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

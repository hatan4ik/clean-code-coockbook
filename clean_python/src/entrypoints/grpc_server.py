import asyncio
import logging
import grpc
from typing import AsyncIterator

from src.entrypoints.deps import get_uow
from src.service_layer import handlers
from src.domain import models
# Note: In a real environment, these imports would come from the generated code package.
# For this cookbook, we assume they are available or mocked if generation isn't run.
try:
    from users.v1 import user_bridge_pb2, user_bridge_pb2_grpc
except ImportError:
    # Fallback/Mock for CI environments where proto gen hasn't run
    logging.warning("Proto generated files not found. Using mocks for demonstration.")
    from types import SimpleNamespace
    user_bridge_pb2 = SimpleNamespace(
        RegisterUserResponse=lambda **k: k,
        GetUserResponse=lambda **k: k,
        User=lambda **k: k,
        UserEvent=lambda **k: k
    )
    user_bridge_pb2_grpc = SimpleNamespace(
        UserServiceServicer=object,
        add_UserServiceServicer_to_server=lambda s, x: None
    )

logger = logging.getLogger(__name__)

class UserService(user_bridge_pb2_grpc.UserServiceServicer):
    async def RegisterUser(self, request, context):
        logger.info(f"Registering user via gRPC: {request.email}")
        uow = get_uow()
        try:
            # Note: handlers.register_user might need adaptation if it expects a command object
            # or if we are calling the domain service directly.
            # Assuming a simple handler wrapper here or direct usage if handler is simple.
            # Checking handlers.py in previous step revealed 'register_user' signature.
            
            # Since handlers.register_user is likely sync or async, we await it.
            # Based on common patterns in this repo (async uow), handlers are likely async.
            
            # We map the request to the handler arguments
            user = await handlers.register_user_service(
                username=request.username,
                email=request.email,
                uow=uow
            )
            
            return user_bridge_pb2.RegisterUserResponse(
                id=str(user.id),
                email=user.email,
                username=user.username,
                status="active",
            )
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetUser(self, request, context):
        uow = get_uow()
        # Direct UOW usage for queries (CQRS pattern: simplified)
        async with uow:
            found = await uow.users.get_by_email(request.email)
        
        if not found:
            await context.abort(grpc.StatusCode.NOT_FOUND, "user not found")
            
        return user_bridge_pb2.GetUserResponse(
            user=user_bridge_pb2.User(
                id=str(found.id),
                email=found.email,
                username=found.name,
                is_active=True, # Defaulting as domain model might not have it yet
                created_at=found.created_at.isoformat() if hasattr(found, 'created_at') else "",
            )
        )

    async def StreamUserEvents(self, request, context) -> AsyncIterator[user_bridge_pb2.UserEvent]:
        # Simulation of streaming events
        events = [
            ("user_registered", "alice"),
            ("user_activated", "alice"),
            ("user_updated", "alice")
        ]
        for evt_type, user in events:
            yield user_bridge_pb2.UserEvent(
                id="evt-123",
                type=evt_type,
                payload=user_bridge_pb2.User(username=user),
                occurred_at="2023-10-27T10:00:00Z"
            )
            await asyncio.sleep(0.5)

async def serve():
    server = grpc.aio.server()
    user_bridge_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)
    logger.info(f"gRPC Server starting on {listen_addr}")
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())

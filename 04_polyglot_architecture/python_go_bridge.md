# Part 3: Python ↔ Go Bridge (gRPC)

Design for connecting the Python “brains” service to the Go “edge” using gRPC/HTTP2 + protobuf.

## Contract
- Single source of truth: `proto/user_bridge.proto`
- Service: `users.v1.UserService`
  - `RegisterUser` (unary)
  - `GetUser` (unary)
  - `StreamUserEvents` (server-streaming)

## Code generation
From repo root:
```bash
# Go
protoc -I proto \
  --go_out=proto/gen/go --go_opt=paths=source_relative \
  --go-grpc_out=proto/gen/go --go-grpc_opt=paths=source_relative \
  proto/user_bridge.proto

# Python (async stubs)
python -m grpc_tools.protoc -I proto \
  --python_out=clean_python/src \
  --grpc_python_out=clean_python/src \
  proto/user_bridge.proto
```
Tip: add `proto/gen/go` and `clean_python/src` to `.gitignore` if you only want generated code in build artifacts.

## Python service (gRPC server, brains)
Sketch using existing domain + unit of work (async SQLAlchemy):
```python
# clean_python/src/entrypoints/grpc_server.py
import asyncio
import grpc
from src.entrypoints.deps import get_uow
from src.service_layer import handlers
from users.v1 import user_bridge_pb2, user_bridge_pb2_grpc

class UserService(user_bridge_pb2_grpc.UserServiceServicer):
    async def RegisterUser(self, request, context):
        uow = get_uow()
        user = await handlers.register_user_service(
            username=request.username,
            email=request.email,
            uow=uow,
        )
        return user_bridge_pb2.RegisterUserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            status="active",
        )

    async def GetUser(self, request, context):
        uow = get_uow()
        async with uow:
            found = await uow.users.get_by_email(request.email)
        if not found:
            await context.abort(grpc.StatusCode.NOT_FOUND, "user not found")
        return user_bridge_pb2.GetUserResponse(
            user=user_bridge_pb2.User(
                id=str(found.id),
                email=found.email,
                username=found.username,
                is_active=found.is_active,
                created_at=found.created_at.isoformat(),
            )
        )

async def serve():
    server = grpc.aio.server()  # deadline-aware
    user_bridge_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port("[::]:50051")  # swap to mTLS in prod
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve())
```
Notes: honor deadlines from `context`; map domain errors to gRPC status; prefer mTLS; surface health via gRPC health service.

## Go edge (client) sketch
```go
// pkg/bridge/user_client.go (example)
conn, err := grpc.DialContext(
    ctx,
    pythonAddr,
    grpc.WithTransportCredentials(creds), // mTLS
    grpc.WithBlock(),
)
client := usersv1.NewUserServiceClient(conn)
resp, err := client.RegisterUser(ctx, &usersv1.RegisterUserRequest{
    Email: "a@example.com", Username: "alice",
})
```
For streaming events:
```go
stream, _ := client.StreamUserEvents(ctx, &usersv1.UserEventsRequest{})
for {
    evt, err := stream.Recv()
    if errors.Is(err, io.EOF) { break }
    // fan-out to caches/queues
}
```

## Resilience & performance guardrails
- Deadlines: set per-call timeouts (`context.WithTimeout` in Go; `context.set_deadline` in Python).
- Retries: idempotent GETs only; no retries on Register unless you use idempotency keys.
- Backpressure: limit concurrent RPCs; pool connections; bound streaming consumers.
- Security: mTLS between services; authz via JWT/SPKI pinned certs; audit log gRPC metadata.
- Observability: propagate trace headers (b3/traceparent) via gRPC metadata; export metrics (latency, RPS, error codes) and structured logs.

## Deployment path
- Generate stubs in CI.
- Build/publish Python image exposing gRPC on 50051 (behind mTLS).
- Go edge uses service discovery (DNS/Consul/K8s) to reach Python.
- Manage DB schema via Alembic (Python) and align proto contract changes with versioned releases.

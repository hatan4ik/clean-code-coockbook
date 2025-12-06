# Go Systems Track: Standard Layout

```
clean_go_system/
├── go.mod                  # Dependencies
├── cmd/                    # Entry points (main applications)
│   └── server/
│       └── main.go         # The wiring / composition root
├── internal/               # 🔒 Private application code
│   ├── domain/             # Pure logic (structs & interfaces)
│   │   ├── user.go
│   │   └── errors.go
│   ├── adapter/            # Infrastructure (SQL, HTTP clients)
│   │   ├── postgres/
│   │   │   └── repo.go
│   │   └── http/
│   │       └── handler.go
│   └── core/               # Service layer
│       └── user_service.go
└── pkg/                    # 🔓 Public libraries (utils shared with others)
    └── logger/
```

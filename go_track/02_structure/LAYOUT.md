clean_go_system/
├── go.mod                  # Dependencies
├── cmd/                    # Entry points (Main applications)
│   └── server/
│       └── main.go         # The Wiring
├── internal/               # 🔒 Private Application Code
│   ├── domain/             # Pure Logic (Structs & Interfaces)
│   │   ├── user.go
│   │   └── errors.go
│   ├── adapter/            # Infrastructure (SQL, HTTP Clients)
│   │   ├── postgres/
│   │   │   └── repo.go
│   │   └── http/
│   │       └── handler.go
│   └── core/               # Service Layer
│       └── user_service.go
└── pkg/                    # 🔓 Public Libraries (Utils shared with others)
    └── logger/
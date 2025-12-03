# Module 2: The Hexagonal Blueprint
## "The Anatomy of a Scalable Python System"

### 1. The Directory Tree
We do not dump files in the root. We categorize them by **responsibility**, not by file type.

```text
clean_code_cookbook/
├── pyproject.toml              # The Build System (Poetry/Hatch)
├── src/
│   └── core_system/            # The Application Name
│       ├── __init__.py
│       ├── main.py             # Entry point (The Wiring)
│       ├── config.py           # 12-Factor App Settings
│       ├── domain/             # 🧠 PURE LOGIC (No Frameworks!)
│       │   ├── models.py       # Dataclasses / Business Rules
│       │   └── events.py       # Domain Events
│       ├── adapters/           # 🔌 THE OUTSIDE WORLD (I/O)
│       │   ├── orm.py          # Database Connectors (SQLAlchemy)
│       │   ├── redis.py        # Cache Connectors
│       │   └── notifications.py# Email/Slack implementations
│       └── service_layer/      # ⚙️ THE ORCHESTRATOR
│           └── unit_of_work.py # Transaction Management
├── tests/
│   ├── unit/                   # Fast, mocks only (tests Domain)
│   ├── integration/            # Slower, real DB (tests Adapters)
│   └── e2e/                    # Slowest, full system (tests Main)
└── docker-compose.yml
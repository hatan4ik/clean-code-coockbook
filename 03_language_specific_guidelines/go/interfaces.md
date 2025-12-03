*   **Interface-Driven Design:** Interfaces are at the heart of Go's flexibility.
    *   **Principle:** "Accept interfaces, return structs." This allows for easy mocking in tests and decoupling of components.
    *   **Example:** Instead of depending on a concrete `*sql.DB`, a service should depend on an interface that defines the methods it needs. This allows you to provide a real database in production and a mock database in tests.
        ```go
        // In the domain layer
        type UserStore interface {
            GetUser(ctx context.Context, id string) (*User, error)
        }

        // In the service layer
        type UserService struct {
            store UserStore
        }

        func (s *UserService) GetUser(ctx context.Context, id string) (*User, error) {
            return s.store.GetUser(ctx, id)
        }
        ```
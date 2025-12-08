package domain

import (
	"context"
	"time"

	"github.com/google/uuid"
)

// User is our clean entity
type User struct {
	ID        uuid.UUID
	Email     string
	Username  string
	CreatedAt time.Time
}

// UserRepository defines the contract for storage.
// Note: It uses context.Context for timeout/cancellation propagation.
type UserRepository interface {
	Save(ctx context.Context, u User) error
	GetByEmail(ctx context.Context, email string) (*User, error)
}
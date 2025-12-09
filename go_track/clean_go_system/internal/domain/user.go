package domain

import (
	"context"
	"errors"
	"time"

	"github.com/google/uuid"
)

// Common Domain Errors
var (
	ErrUserNotFound = errors.New("user not found")
	ErrInvalidEmail = errors.New("invalid email format")
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
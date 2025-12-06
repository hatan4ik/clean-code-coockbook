package domain

import (
	"context"
	"net/mail"
	"time"

	"github.com/google/uuid"
)

// User is our clean entity.
type User struct {
	ID        uuid.UUID
	Email     string
	Username  string
	CreatedAt time.Time
}

// ValidateEmail ensures basic format validity without tying to any adapter.
func ValidateEmail(email string) error {
	if _, err := mail.ParseAddress(email); err != nil {
		return ErrInvalidEmail
	}
	return nil
}

// UserRepository defines the contract for storage.
// Note: It uses context.Context for timeout/cancellation propagation.
type UserRepository interface {
	Save(ctx context.Context, u User) error
	GetByEmail(ctx context.Context, email string) (*User, error)
}

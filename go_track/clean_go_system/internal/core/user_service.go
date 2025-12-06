package core

import (
	"context"
	"fmt"
	"time"

	"github.com/google/uuid"

	"clean_go_system/internal/domain"
)

// UserService contains the business logic.
type UserService struct {
	repo domain.UserRepository
}

// NewUserService is a constructor (factory).
func NewUserService(repo domain.UserRepository) *UserService {
	return &UserService{repo: repo}
}

// Register handles the user creation flow.
func (s *UserService) Register(ctx context.Context, email, username string) (*domain.User, error) {
	if err := domain.ValidateEmail(email); err != nil {
		return nil, fmt.Errorf("validate email: %w", err)
	}

	existing, err := s.repo.GetByEmail(ctx, email)
	if err != nil && err != domain.ErrUserNotFound {
		return nil, fmt.Errorf("check user: %w", err)
	}
	if existing != nil {
		return nil, fmt.Errorf("check user: %w", domain.ErrUserExists)
	}

	newUser := domain.User{
		ID:        uuid.New(),
		Email:     email,
		Username:  username,
		CreatedAt: time.Now().UTC(),
	}

	if err := s.repo.Save(ctx, newUser); err != nil {
		return nil, fmt.Errorf("save user: %w", err)
	}

	return &newUser, nil
}

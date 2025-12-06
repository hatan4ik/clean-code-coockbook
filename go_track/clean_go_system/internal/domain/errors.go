package domain

import "errors"

var (
	ErrUserNotFound = errors.New("user not found")
	ErrInvalidEmail = errors.New("invalid email format")
	ErrUserExists   = errors.New("user already exists")
)

package postgres

import (
	"context"
	"database/sql"
	"clean_go_system/internal/domain"
)

type PostgresRepository struct {
	db *sql.DB
}

func NewPostgresRepository(db *sql.DB) *PostgresRepository {
	return &PostgresRepository{db: db}
}

func (r *PostgresRepository) Save(ctx context.Context, u domain.User) error {
	query := `INSERT INTO users (id, email, username, created_at) VALUES ($1, $2, $3, $4)`
	
	// ExecContext is crucial for handling timeouts/cancellations
	_, err := r.db.ExecContext(ctx, query, u.ID, u.Email, u.Username, u.CreatedAt)
	return err
}

func (r *PostgresRepository) GetByEmail(ctx context.Context, email string) (*domain.User, error) {
	query := `SELECT id, email, username, created_at FROM users WHERE email = $1`
	
	row := r.db.QueryRowContext(ctx, query, email)
	
	var u domain.User
	err := row.Scan(&u.ID, &u.Email, &u.Username, &u.CreatedAt)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, domain.ErrUserNotFound
		}
		return nil, err
	}
	return &u, nil
}
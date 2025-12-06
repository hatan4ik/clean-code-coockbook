package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"
	"time"

	_ "github.com/lib/pq" // Postgres driver

	httpadapter "clean_go_system/internal/adapter/http"
	"clean_go_system/internal/adapter/postgres"
	"clean_go_system/internal/core"
)

func main() {
	connStr := envOrDefault("DATABASE_URL", "postgres://user:pass@localhost:5432/db?sslmode=disable")
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
	db.SetConnMaxLifetime(30 * time.Minute)
	db.SetMaxOpenConns(20)
	db.SetMaxIdleConns(5)
	defer db.Close()

	repo := postgres.NewPostgresRepository(db)
	userService := core.NewUserService(repo)

	emailPool := core.NewWorkerPool(5, 100)
	emailPool.Start()
	defer emailPool.Stop()

	handler := httpadapter.NewHandler(userService, emailPool)

	http.HandleFunc("/register", handler.Register)

	log.Println("server starting on :8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}
}

func envOrDefault(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

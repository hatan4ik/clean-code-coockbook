package main

import (
	"database/sql"
	"log"
	"net/http"

	"clean_go_system/internal/adapter/postgres"
	"clean_go_system/internal/core"
	_ "github.com/lib/pq" // Postgres Driver
)

func main() {
	// 1. Infrastructure
	connStr := "user=postgres dbname=mydb sslmode=disable"
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// 2. Wiring Layers (The "Composition Root")
	repo := postgres.NewPostgresRepository(db)
	svc := core.NewUserService(repo)

	// 3. Background Workers
	emailPool := core.NewWorkerPool(5, 100) // 5 Workers, Buffer of 100
	emailPool.Start()
	defer emailPool.Stop()

	// 4. HTTP Handlers (Using Standard Lib or Chi/Gin)
	http.HandleFunc("/register", func(w http.ResponseWriter, r *http.Request) {
		// Parse JSON...
		// Call svc.Register()...
		// Send Email Job to Pool: emailPool.JobQueue <- job
		w.WriteHeader(http.StatusCreated)
	})

	// 5. Start Server
	log.Println("Server starting on :8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}
}
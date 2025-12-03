package main

import (
	"context"
	"log"
	"net/http"
	"time"

	"github.com/clean-code-coockbook/catalog/internal/app"
	"github.com/clean-code-coockbook/catalog/internal/domain"
)

type noopInventory struct{}
type noopPricing struct{}
type noopReviews struct{}

func (noopInventory) Get(_ context.Context, _ string) (domain.Inventory, error) {
	return domain.Inventory{Available: 3}, nil
}
func (noopPricing) Get(_ context.Context, _ string) (domain.Price, error) {
	return domain.Price{Currency: "USD", Amount: 9.99}, nil
}
func (noopReviews) Get(_ context.Context, _ string) ([]string, error) {
	return []string{"ok"}, nil
}

func main() {
	svc := app.Service{
		Inventory: noopInventory{},
		Pricing:   noopPricing{},
		Reviews:   noopReviews{},
		Timeout:   200 * time.Millisecond,
	}

	http.HandleFunc("/products/", func(w http.ResponseWriter, r *http.Request) {
		id := r.URL.Path[len("/products/"):]
		product, err := svc.FetchProduct(r.Context(), id)
		if err != nil {
			http.Error(w, err.Error(), http.StatusGatewayTimeout)
			return
		}
		_, _ = w.Write([]byte(product.ID))
	})

	log.Println("catalog listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

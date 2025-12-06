package tests

import (
	"context"
	"errors"
	"testing"
	"clean-code-cookbook/go/services/catalog/internal/app"
	"clean-code-cookbook/go/services/catalog/internal/domain"
)

// mockProductFetcher is a mock implementation of the ProductFetcher port.
// It allows us to simulate the behavior of an external service.
type mockProductFetcher struct {
	mockedProduct *domain.Product
	mockedError   error
}

// FetchProductByID is the mock's implementation of the interface method.
func (m *mockProductFetcher) FetchProductByID(ctx context.Context, id string) (*domain.Product, error) {
	if m.mockedError != nil {
		return nil, m.mockedError
	}
	// Simulate finding a product.
	if m.mockedProduct != nil && m.mockedProduct.ID == id {
		return m.mockedProduct, nil
	}
	return nil, errors.New("product not found")
}

func TestFetchProductQuery_Execute_Success(t *testing.T) {
	// Arrange
	mockFetcher := &mockProductFetcher{
		mockedProduct: &domain.Product{ID: "123", Name: "Test Product", Price: 99.99},
	}
	query := app.FetchProductQuery{ProductFetcher: mockFetcher}
	ctx := context.Background()

	// Act
	product, err := query.Execute(ctx, "123")

	// Assert
	if err != nil {
		t.Fatalf("Expected no error, but got: %v", err)
	}
	if product == nil {
		t.Fatal("Expected a product, but got nil")
	}
	if product.Name != "Test Product" {
		t.Errorf("Expected product name 'Test Product', but got '%s'", product.Name)
	}
}

func TestFetchProductQuery_Execute_FetcherError(t *testing.T) {
	// Arrange
	expectedError := errors.New("network error")
	mockFetcher := &mockProductFetcher{
		mockedError: expectedError,
	}
	query := app.FetchProductQuery{ProductFetcher: mockFetcher}
	ctx := context.Background()

	// Act
	_, err := query.Execute(ctx, "123")

	// Assert
	if err == nil {
		t.Fatal("Expected an error, but got nil")
	}
	if !errors.Is(err, expectedError) {
		t.Fatalf("Expected error '%v', but got '%v'", expectedError, err)
	}
}
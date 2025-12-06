package domain

// Product is the core domain model. It represents a product in our catalog.
// Note that it contains no tags for JSON or database serialization.
// This is a pure, business-logic-oriented struct.
type Product struct {
	ID    string
	Name  string
	Price float64 // Use float64 for currency in this example, but consider a dedicated type in production.
}
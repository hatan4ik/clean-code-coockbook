package httpadapter

import (
	"encoding/json"
	"net/http"

	"clean_go_system/internal/core"
	"clean_go_system/internal/domain"
)

type Handler struct {
	userService *core.UserService
	emailPool   *core.WorkerPool
}

func NewHandler(userService *core.UserService, emailPool *core.WorkerPool) *Handler {
	return &Handler{
		userService: userService,
		emailPool:   emailPool,
	}
}

type registerRequest struct {
	Email    string `json:"email"`
	Username string `json:"username"`
}

type registerResponse struct {
	ID       string `json:"id"`
	Email    string `json:"email"`
	Username string `json:"username"`
}

func (h *Handler) Register(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var payload registerRequest
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		http.Error(w, "invalid payload", http.StatusBadRequest)
		return
	}

	user, err := h.userService.Register(r.Context(), payload.Email, payload.Username)
	if err != nil {
		status := http.StatusInternalServerError
		if err == domain.ErrInvalidEmail {
			status = http.StatusBadRequest
		} else if err == domain.ErrUserExists {
			status = http.StatusConflict
		}
		http.Error(w, err.Error(), status)
		return
	}

	// Kick off a background email send.
	select {
	case h.emailPool.JobQueue <- core.EmailJob{Email: user.Email, Body: "welcome aboard"}:
	default:
		// If the queue is full, we drop the job to protect latency.
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	_ = json.NewEncoder(w).Encode(registerResponse{
		ID:       user.ID.String(),
		Email:    user.Email,
		Username: user.Username,
	})
}

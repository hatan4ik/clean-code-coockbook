package logger

import (
	"log"
	"os"
)

// New returns a stdlib logger with sane defaults.
func New() *log.Logger {
	return log.New(os.Stdout, "[clean-go] ", log.LstdFlags|log.Lshortfile)
}

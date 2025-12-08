package core

import (
	"fmt"
	"sync"
)

// Job represents the work to be done
type EmailJob struct {
	Email string
	Body  string
}

// WorkerPool manages concurrency
type WorkerPool struct {
	JobQueue chan EmailJob
	Workers  int
	wg       sync.WaitGroup
}

func NewWorkerPool(workers int, bufferSize int) *WorkerPool {
	return &WorkerPool{
		JobQueue: make(chan EmailJob, bufferSize), // Buffered Channel
		Workers:  workers,
	}
}

func (wp *WorkerPool) Start() {
	for i := 0; i < wp.Workers; i++ {
		wp.wg.Add(1)
		go func(workerID int) {
			defer wp.wg.Done()
			fmt.Printf("Worker %d started\n", workerID)
			
			// Range over channel: This loop blocks until a job comes in
			// It exits when the channel is closed.
			for job := range wp.JobQueue {
				fmt.Printf("Worker %d processing email to %s\n", workerID, job.Email)
				// Simulate sending email
				// time.Sleep(100 * time.Millisecond) 
			}
			fmt.Printf("Worker %d stopped\n", workerID)
		}(i)
	}
}

func (wp *WorkerPool) Stop() {
	close(wp.JobQueue) // This signals all workers to finish current loop and exit
	wp.wg.Wait()       // Wait for all goroutines to finish
}
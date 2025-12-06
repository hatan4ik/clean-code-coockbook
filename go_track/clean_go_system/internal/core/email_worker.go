package core

import (
	"fmt"
	"sync"
)

// EmailJob represents the work to be done.
type EmailJob struct {
	Email string
	Body  string
}

// WorkerPool manages concurrency.
type WorkerPool struct {
	JobQueue chan EmailJob
	Workers  int
	wg       sync.WaitGroup
}

func NewWorkerPool(workers int, bufferSize int) *WorkerPool {
	return &WorkerPool{
		JobQueue: make(chan EmailJob, bufferSize), // Buffered channel
		Workers:  workers,
	}
}

func (wp *WorkerPool) Start() {
	for i := 0; i < wp.Workers; i++ {
		wp.wg.Add(1)
		go func(workerID int) {
			defer wp.wg.Done()
			fmt.Printf("worker %d started\n", workerID)

			for job := range wp.JobQueue {
				fmt.Printf("worker %d processing email to %s\n", workerID, job.Email)
				// simulate send: time.Sleep(...)
				_ = job
			}

			fmt.Printf("worker %d stopped\n", workerID)
		}(i + 1)
	}
}

func (wp *WorkerPool) Stop() {
	close(wp.JobQueue) // signals workers to exit
	wp.wg.Wait()
}

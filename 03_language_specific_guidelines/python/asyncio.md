### Advanced `asyncio` Patterns

This section goes beyond basic `await` calls and explores the patterns needed for building resilient, high-concurrency systems.

#### Structured Concurrency with `TaskGroup`

`asyncio.TaskGroup` (introduced in Python 3.11) is a powerful tool for managing the lifecycle of multiple related tasks. It provides a much safer and more robust way to manage concurrent tasks than `asyncio.gather`.

```python
import asyncio

async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(some_coroutine())
        task2 = tg.create_task(another_coroutine())
    print(f"Both tasks have completed. Results: {task1.result()}, {task2.result()}")
```

If any task in the `TaskGroup` raises an exception, all other tasks in the group are cancelled. This makes it much easier to reason about the state of your application when errors occur.

#### Resource Management

When building concurrent applications, it's important to manage your resources carefully. `asyncio` provides several tools to help with this.

##### `asyncio.Semaphore`

A semaphore is a synchronization primitive that can be used to limit access to a resource. For example, you can use a semaphore to limit the number of concurrent connections to a database.

```python
import asyncio

async def do_work(semaphore, work_id):
    async with semaphore:
        print(f"Starting work {work_id}")
        await asyncio.sleep(1)
        print(f"Finished work {work_id}")

async def main():
    semaphore = asyncio.Semaphore(5)  # Allow up to 5 concurrent tasks
    tasks = [do_work(semaphore, i) for i in range(10)]
    await asyncio.gather(*tasks)
```

##### `asyncio.Queue`

A queue is a data structure that can be used to pass data between concurrent tasks. Queues are often used in producer-consumer patterns.

```python
import asyncio

async def producer(queue):
    for i in range(10):
        await queue.put(i)
        await asyncio.sleep(0.1)
    await queue.put(None)  # Sentinel to signal the end

async def consumer(queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"Consumed {item}")
        queue.task_done()

async def main():
    queue = asyncio.Queue()
    producers = [asyncio.create_task(producer(queue))]
    consumers = [asyncio.create_task(consumer(queue))]
    await asyncio.gather(*producers)
    await queue.join()  # Wait until all items are processed
    for c in consumers:
        c.cancel()
```

#### Cancellation and Timeouts

`asyncio` provides a robust way to handle task cancellation and timeouts. You can use `asyncio.wait_for` to set a timeout on a coroutine.

```python
import asyncio

async def slow_operation():
    await asyncio.sleep(10)

async def main():
    try:
        await asyncio.wait_for(slow_operation(), timeout=1.0)
    except asyncio.TimeoutError:
        print("The operation timed out!")
```

#### Testing Async Code

Testing asynchronous code can be tricky, but there are several libraries that can help. `pytest-asyncio` is a popular choice for testing async code with `pytest`.

```python
import asyncio
import pytest

@pytest.mark.asyncio
async def test_my_async_function():
    result = await my_async_function()
    assert result == "expected_result"
```
